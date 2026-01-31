import socket, time, requests, os, subprocess, threading, sqlite3, json, cv2, re
import easyocr
import logging
from requests.auth import HTTPDigestAuth
from datetime import datetime
from config import *
# --- NUEVO: CEREBRO YOLO ---
from ultralytics import YOLO

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
os.environ['TZ'] = 'America/Mexico_City'
try: time.tzset()
except: pass

# Suprimir logs de YOLO para mantener la consola limpia
logging.getLogger("ultralytics").setLevel(logging.ERROR)

# Carga de Modelos
print("🧠 Cargando OCR...")
reader = easyocr.Reader(['es'], gpu=False)
print("👁️ Cargando YOLO AI...")
model_ai = YOLO('yolov8n.pt') # Modelo Nano (Rápido y Ligero)

BUFFER_DIR = "/dev/shm/radar_buffer"
BASE_DIR = "/mnt/darat"
DB_FILE = f"{BASE_DIR}/data/cola_mensajes.db"
FOTOS_PATH = "/mnt/darat/multas_fotos/"
VIDEO_PATH = "/mnt/darat/clips/"
LOG_FILE = f"{VIDEO_PATH}velocidades.log"

LAST_SEEN = {name: time.time() for name in RADARES} 
RADAR_STATUS = {name: True for name in RADARES} 

for ruta in [FOTOS_PATH, VIDEO_PATH, f"{BASE_DIR}/data", BUFFER_DIR]:
    os.makedirs(ruta, exist_ok=True)

# ==========================================
# 2. CEREBRO CLAWDBOT (FILTRO PLACAS)
# ==========================================
def validar_placa(texto_sucio):
    limpio = "".join(e for e in texto_sucio if e.isalnum()).upper()
    if re.search(r'\d{8,}', limpio): return None 
    if 5 <= len(limpio) <= 8: return limpio
    return None

# ==========================================
# 3. BASE DE DATOS Y UTILIDADES
# ==========================================
def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS cola (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, endpoint TEXT, payload TEXT, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS historial (id INTEGER PRIMARY KEY AUTOINCREMENT, radar TEXT, velocidad INTEGER, fecha DATE DEFAULT (CURRENT_DATE), hora TIME DEFAULT (CURRENT_TIME), foto TEXT, placa TEXT)''')
        conn.commit()
        conn.close()
    except: pass

def registrar_historial(radar, speed, foto=None, placa=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        fecha, hora = datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M:%S')
        conn.execute("INSERT INTO historial (radar, velocidad, fecha, hora, foto, placa) VALUES (?, ?, ?, ?, ?, ?)", (radar, speed, fecha, hora, foto, placa))
        conn.commit()
        conn.close()
    except: pass

def enviar_seguro(metodo, params, files=None):
    url = f"https://api.telegram.org/bot{TOKEN}/{metodo}"
    try:
        if files: return requests.post(url, data=params, files=files, timeout=25).json()
        return requests.post(url, json=params, timeout=10).json()
    except:
        if metodo not in ["sendPhoto", "sendVideo"]: 
            try:
                conn = sqlite3.connect(DB_FILE)
                conn.execute("INSERT INTO cola (tipo, endpoint, payload) VALUES (?, ?, ?)", (metodo, url, json.dumps(params)))
                conn.commit()
                conn.close()
            except: pass
        return None

def procesar_cola_reintentos():
    while True:
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT * FROM cola ORDER BY id ASC LIMIT 5")
            for fila in c.fetchall():
                bid, tipo, endpoint, p_str, fecha = fila
                try:
                    if requests.post(endpoint, json=json.loads(p_str), timeout=10).status_code == 200:
                        c.execute("DELETE FROM cola WHERE id=?", (bid,))
                        conn.commit()
                except: pass
            conn.close()
        except: pass
        time.sleep(60)

def motor_mantenimiento():
    while True:
        ahora = time.time()
        for nombre, last_time in LAST_SEEN.items():
            diff = ahora - last_time
            if diff > 3600 and RADAR_STATUS[nombre]:
                RADAR_STATUS[nombre] = False
                enviar_seguro("sendMessage", {"chat_id": CHAT_ID, "text": f"🚨 <b>OFFLINE:</b> {nombre}", "parse_mode": "HTML"})
            elif diff < 60 and not RADAR_STATUS[nombre]:
                RADAR_STATUS[nombre] = True
                enviar_seguro("sendMessage", {"chat_id": CHAT_ID, "text": f"✅ <b>ONLINE:</b> {nombre}", "parse_mode": "HTML"})
        try:
            st = os.statvfs(BASE_DIR)
            if ((st.f_blocks - st.f_bavail) / st.f_blocks) * 100 > 90:
                archivos = sorted([os.path.join(VIDEO_PATH, f) for f in os.listdir(VIDEO_PATH)], key=os.path.getmtime)
                for i in range(min(20, len(archivos))): os.remove(archivos[i])
        except: pass
        time.sleep(300)

# ==========================================
# 4. BUFFER DE VIDEO (15s + 5s)
# ==========================================
def worker_buffer_continuo(nombre_radar, ip):
    radar_path = os.path.join(BUFFER_DIR, nombre_radar)
    os.makedirs(radar_path, exist_ok=True)
    while True:
        tmp = os.path.join(radar_path, "buffer_raw.mp4")
        subprocess.run(["ffmpeg", "-rtsp_transport", "tcp", "-i", f"rtsp://{USER}:{PASS}@{ip}/axis-media/media.amp", "-t", "15", "-c", "copy", "-y", tmp], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.rename(tmp, os.path.join(radar_path, "ready_15s.mp4"))

def grabar_y_enviar_video_robusto(radar_name, ip, speed, caption):
    ahora_s = datetime.now().strftime('%H%M%S')
    final_p = os.path.join(VIDEO_PATH, f"{radar_name}_{speed}_{ahora_s}.mp4")
    buffer_p = os.path.join(BUFFER_DIR, radar_name, "ready_15s.mp4")
    multa_post = f"/dev/shm/{radar_name}_post.mp4"
    list_f = f"/dev/shm/{radar_name}_list.txt"
    try:
        subprocess.run(["ffmpeg", "-rtsp_transport", "tcp", "-i", f"rtsp://{USER}:{PASS}@{ip}/axis-media/media.amp", "-t", "5", "-c", "copy", "-y", multa_post], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(buffer_p):
            with open(list_f, "w") as f: f.write(f"file '{buffer_p}'\nfile '{multa_post}'\n")
            subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_f, "-c", "copy", "-y", final_p], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else: os.rename(multa_post, final_p)
        if os.path.exists(final_p):
            with open(final_p, 'rb') as v: enviar_seguro("sendVideo", {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}, files={'video': v})
    except: pass

# ==========================================
# 5. MODO CSI + CLASIFICACIÓN IA (YOLO)
# ==========================================
def clasificar_vehiculo(img):
    """
    Usa YOLO para detectar qué tipo de vehículo es.
    Retorna: Icono y Nombre (Ej: '🚛 Camión')
    """
    try:
        # Clases COCO: 2=car, 3=motorcycle, 5=bus, 7=truck
        results = model_ai(img)
        
        # Buscamos la detección con mayor confianza
        mejor_conf = 0
        tipo = "🚗 Vehículo" # Default
        
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                
                if conf > mejor_conf and conf > 0.4: # Umbral confianza 40%
                    mejor_conf = conf
                    if cls_id == 2: tipo = "🚗 Automóvil"
                    elif cls_id == 3: tipo = "🏍️ Motocicleta"
                    elif cls_id == 5: tipo = "🚌 Autobús"
                    elif cls_id == 7: tipo = "🚛 Camión"
                    
        return tipo
    except:
        return "🚗 Vehículo (AI Error)"

def procesar_imagen_csi(ruta_foto, speed):
    try:
        img = cv2.imread(ruta_foto)
        if img is None: return "ERROR_IMG", "🚗 Indefinido"
        
        # A) CLASIFICACIÓN DE VEHÍCULO (YOLO)
        tipo_vehiculo = clasificar_vehiculo(img)
        
        # B) LECTURA DE PLACA (OCR)
        alto, ancho = img.shape[:2]
        recorte = img[0:alto, 0:ancho // 2]
        resultados = reader.readtext(recorte)
        placa_final = "NO_DETECTADA"
        bbox_placa = None
        for (bbox, text, prob) in resultados:
            candidato = validar_placa(text)
            if candidato:
                placa_final = candidato; bbox_placa = bbox; break
        
        # C) DIBUJAR EVIDENCIA
        if bbox_placa:
            (tl, tr, br, bl) = bbox_placa
            top_left = (int(tl[0]), int(tl[1]))
            bottom_right = (int(br[0]), int(br[1]))
            cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 3)
            cv2.putText(img, placa_final, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Texto Inferior
        info = f"VEL: {speed} km/h"
        cv2.putText(img, info, (30, alto - 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 5) 
        cv2.putText(img, info, (30, alto - 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3) 
        
        fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cv2.putText(img, fecha_str, (30, alto - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3) 
        cv2.putText(img, fecha_str, (30, alto - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2) 

        cv2.imwrite(ruta_foto, img)
        return placa_final, tipo_vehiculo
        
    except Exception as e:
        print(f"Error CSI: {e}")
        return "ERROR_PROC", "🚗 Indefinido"

# ==========================================
# 6. LÓGICA DE DETECCIÓN
# ==========================================
def clasificar_infraccion(v):
    if v <= 54: return "PREVENTIVO", "✅"
    elif 55 <= v <= 59: return "ALERTA", "🟡"
    else: return "GRAVE", "🔴"

def axis_overlay(ip, speed, clear=False):
    txt = " " if clear else f"INFRACCION: {speed} km/h"
    try:
        requests.get(f"http://{ip}/axis-cgi/overlaymanager.cgi?action=settext&text={txt.replace(' ', '+')}", auth=HTTPDigestAuth(USER, PASS), timeout=5)
        if not clear: threading.Timer(8, axis_overlay, [ip, 0, True]).start()
    except: pass

def procesar_deteccion(radar_name, ip, speed):
    cat, emo = clasificar_infraccion(speed)
    ahora_dt = datetime.now()
    hora_s = ahora_dt.strftime('%H:%M:%S')
    archivo_foto = None
    placa = "Procesando..."
    vehiculo = "🚗 Analizando..." # Placeholder

    if speed >= 55:
        threading.Thread(target=axis_overlay, args=(ip, speed)).start()
        try:
            r = requests.get(f"http://{ip}/axis-cgi/jpg/image.cgi", auth=HTTPDigestAuth(USER, PASS), timeout=10)
            if r.status_code == 200:
                archivo_foto = f"{radar_name}_{speed}_{ahora_dt.strftime('%H%M%S')}.jpg"
                ruta_f = os.path.join(FOTOS_PATH, archivo_foto)
                with open(ruta_f, "wb") as f: f.write(r.content)
                # LLAMAMOS A LA NUEVA FUNCIÓN QUE DEVUELVE 2 VALORES
                placa, vehiculo = procesar_imagen_csi(ruta_f, speed)
        except: pass

    registrar_historial(radar_name, speed, archivo_foto, placa)
    
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{ahora_dt}] {radar_name} - {speed} km/h - {cat} - {vehiculo}\n")
    except: pass

    # ESTRUCTURA DEL MENSAJE ACTUALIZADA CON TIPO DE VEHÍCULO
    cap = f"{emo} <b>{cat}</b>\n📍 Radar: <b>{radar_name}</b>\n🚘 Tipo: <b>{vehiculo}</b>\n⚡ Velocidad: <b>{speed} km/h</b>\n📄 Placa: <b>{placa}</b>\n⏰ {hora_s}"
    
    if speed >= 55 and archivo_foto:
        with open(os.path.join(FOTOS_PATH, archivo_foto), 'rb') as f:
            enviar_seguro("sendPhoto", {'chat_id': CHAT_ID, 'caption': cap, 'parse_mode': 'HTML'}, files={'photo': f})
        
        if speed >= 60:
            threading.Thread(target=grabar_y_enviar_video_robusto, args=(radar_name, ip, speed, cap)).start()
        
        if speed >= 60 and 'STICKER_KIRBY' in globals():
            enviar_seguro("sendSticker", {"chat_id": CHAT_ID, "sticker": STICKER_KIRBY})
    else:
        enviar_seguro("sendMessage", {"chat_id": CHAT_ID, "text": cap, "parse_mode": "HTML"})

def escuchar_radar(nombre, ip, puerto):
    print(f"👂 Monitor activo: {nombre} ({ip}:{puerto})")
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(15); s.connect((ip, puerto))
            while True:
                data = s.recv(1024)
                if not data: break
                LAST_SEEN[nombre] = time.time()
                speed = 0
                if b'\xfc\xfa' in data: speed = data[data.find(b'\xfc\xfa') + 2]
                elif b'\xfb\xfd' in data: speed = data[data.find(b'\xfb\xfd') + 2]
                if speed >= 1: threading.Thread(target=procesar_deteccion, args=(nombre, ip, speed)).start()
        except: time.sleep(10)

if __name__ == "__main__":
    init_db()
    threading.Thread(target=procesar_cola_reintentos, daemon=True).start()
    threading.Thread(target=motor_mantenimiento, daemon=True).start()
    for n, d in RADARES.items():
        threading.Thread(target=worker_buffer_continuo, args=(n, d['ip']), daemon=True).start()
        threading.Thread(target=escuchar_radar, args=(n, d['ip'], d['puerto']), daemon=True).start()
    while True: time.sleep(1)