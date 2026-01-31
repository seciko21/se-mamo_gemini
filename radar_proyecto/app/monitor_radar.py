import socket, time, requests, os, subprocess, threading, sqlite3, json, cv2
import easyocr
import numpy as np
from requests.auth import HTTPDigestAuth
from datetime import datetime
from config import *

# ==========================================
# 1. CONFIGURACIÓN DE ENTORNO Y BUFFER RAM
# ==========================================
os.environ['TZ'] = 'America/Mexico_City'
try:
    time.tzset()
except:
    pass

# Inicializar lector IA (Carga única en memoria)
reader = easyocr.Reader(['es'], gpu=False)

# Rutas de memoria (Buffer circular) y Disco (900GB)
BUFFER_DIR = "/dev/shm/radar_buffer"
BASE_DIR = "/mnt/darat"
DB_FILE = f"{BASE_DIR}/data/cola_mensajes.db"
FOTOS_PATH = "/mnt/darat/multas_fotos/"
VIDEO_PATH = "/mnt/darat/clips/"
LOG_FILE = f"{VIDEO_PATH}velocidades.log"

LAST_SEEN = {name: time.time() for name in RADARES} 
RADAR_STATUS = {name: True for name in RADARES} 

# Asegurar persistencia de directorios
for ruta in [FOTOS_PATH, VIDEO_PATH, f"{BASE_DIR}/data", BUFFER_DIR]:
    os.makedirs(ruta, exist_ok=True)

# ==========================================
# 2. CAPA DE DATOS, COLA Y REINTENTOS
# ==========================================
def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS cola (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tipo TEXT, endpoint TEXT, payload TEXT,
                        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS historial (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        radar TEXT, velocidad INTEGER, 
                        fecha DATE DEFAULT (CURRENT_DATE),
                        hora TIME DEFAULT (CURRENT_TIME),
                        foto TEXT, placa TEXT)''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ [DB] Error: {e}")

def registrar_historial(radar, speed, foto=None, placa=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        f_l = datetime.now().strftime('%Y-%m-%d')
        h_l = datetime.now().strftime('%H:%M:%S')
        c.execute("INSERT INTO historial (radar, velocidad, fecha, hora, foto, placa) VALUES (?, ?, ?, ?, ?, ?)", 
                  (radar, speed, f_l, h_l, foto, placa))
        conn.commit()
        conn.close()
    except: pass

def actualizar_placa_db(archivo_foto, placa):
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("UPDATE historial SET placa = ? WHERE foto = ?", (placa, archivo_foto))
        conn.commit()
        conn.close()
    except: pass

def guardar_en_cola(metodo, params):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO cola (tipo, endpoint, payload) VALUES (?, ?, ?)",
                  (metodo, f"https://api.telegram.org/bot{TOKEN}/{metodo}", json.dumps(params)))
        conn.commit()
        conn.close()
    except: pass

def procesar_cola_reintentos():
    """Hilo dedicado a reenviar mensajes fallidos (Líneas restauradas)."""
    while True:
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT * FROM cola ORDER BY id ASC LIMIT 5")
            for fila in c.fetchall():
                bid, tipo, endpoint, p_str, fecha = fila
                try:
                    r = requests.post(endpoint, json=json.loads(p_str), timeout=10)
                    if r.status_code == 200:
                        c.execute("DELETE FROM cola WHERE id=?", (bid,))
                        conn.commit()
                except: pass
            conn.close()
        except: pass
        time.sleep(60)

# ==========================================
# 3. MANTENIMIENTO Y WATCHDOG
# ==========================================


def enviar_seguro(metodo, params, files=None):
    url = f"https://api.telegram.org/bot{TOKEN}/{metodo}"
    try:
        if files:
            r = requests.post(url, data=params, files=files, timeout=25)
        else:
            r = requests.post(url, json=params, timeout=10)
        return r.json()
    except:
        if metodo not in ["sendPhoto", "sendVideo"]:
            guardar_en_cola(metodo, params)
        return None

def motor_mantenimiento():
    """Monitorea estado de antenas y salud del disco duro."""
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
# 4. TRABAJO DE BUFFER CIRCULAR (RAM)
# ==========================================


def worker_buffer_continuo(nombre_radar, ip):
    """Mantiene clips de 15 segundos frescos en RAM."""
    radar_path = os.path.join(BUFFER_DIR, nombre_radar)
    os.makedirs(radar_path, exist_ok=True)
    while True:
        tmp = os.path.join(radar_path, "buffer_raw.mp4")
        cmd = ["ffmpeg", "-rtsp_transport", "tcp", "-i", f"rtsp://{USER}:{PASS}@{ip}/axis-media/media.amp",
               "-t", "15", "-c", "copy", "-y", tmp]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.rename(tmp, os.path.join(radar_path, "ready_15s.mp4"))

# ==========================================
# 5. IA ASÍNCRONA Y ROBUSTEZ DE VIDEO
# ==========================================
def hilo_ia_lpr(ruta_foto, msg_id, radar_name, speed, hora):
    """Procesamiento de placa y edición de mensaje Telegram."""
    try:
        img = cv2.imread(ruta_foto)
        if img is None: return
        alto, ancho = img.shape[:2]
        recorte = img[0:alto, 0:ancho // 2]
        resultados = reader.readtext(recorte)
        placa = "NO_DETECTADA"
        for (bbox, text, prob) in resultados:
            limpio = "".join(e for e in text if e.isalnum()).upper()
            if len(limpio) >= 4:
                placa = limpio
                break
        
        actualizar_placa_db(os.path.basename(ruta_foto), placa)
        cat, emo = ("🚀 GRAVE", "🔴") if speed >= 60 else ("⚠️ ALERTA", "🟡")
        nuevo_cap = f"{emo} <b>{cat}</b>\n📍 Radar: <b>{radar_name}</b>\n⚡ Velocidad: <b>{speed} km/h</b>\n📄 Placa: <b>{placa}</b>\n⏰ {hora}"
        requests.post(f"https://api.telegram.org/bot{TOKEN}/editMessageCaption",
                      json={"chat_id": CHAT_ID, "message_id": msg_id, "caption": nuevo_cap, "parse_mode": "HTML"}, timeout=10)
    except: pass

def grabar_y_enviar_video_robusto(radar_name, ip, speed, caption):
    """Concatena 15s (PASADO) + 5s (PRESENTE)."""
    ahora_s = datetime.now().strftime('%H%M%S')
    final_p = os.path.join(VIDEO_PATH, f"{radar_name}_{speed}_{ahora_s}.mp4")
    buffer_p = os.path.join(BUFFER_DIR, radar_name, "ready_15s.mp4")
    multa_post = f"/dev/shm/{radar_name}_post.mp4"
    list_f = f"/dev/shm/{radar_name}_list.txt"

    try:
        cmd_post = ["ffmpeg", "-rtsp_transport", "tcp", "-i", f"rtsp://{USER}:{PASS}@{ip}/axis-media/media.amp", "-t", "5", "-c", "copy", "-y", multa_post]
        subprocess.run(cmd_post, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(buffer_p):
            with open(list_f, "w") as f: f.write(f"file '{buffer_p}'\nfile '{multa_post}'\n")
            cmd_j = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_f, "-c", "copy", "-y", final_p]
            subprocess.run(cmd_j, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            os.rename(multa_post, final_p)

        if os.path.exists(final_p):
            with open(final_p, 'rb') as v:
                enviar_seguro("sendVideo", {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}, files={'video': v})
    except: pass

# ==========================================
# 6. LÓGICA DE DETECCIÓN Y ESCUCHA
# ==========================================
def clasificar_infraccion(v):
    if v <= 54: return "🚗 PREVENTIVO", "✅"
    elif 55 <= v <= 59: return "⚠️ ALERTA", "🟡"
    else: return "🚀 GRAVE", "🔴"

def axis_overlay(ip, speed, clear=False):
    """Muestra la velocidad en el stream de la cámara (Línea restaurada)."""
    txt = " " if clear else f"INFRACCION: {speed} km/h"
    try:
        requests.get(f"http://{ip}/axis-cgi/overlaymanager.cgi?action=settext&text={txt.replace(' ', '+')}", 
                     auth=HTTPDigestAuth(USER, PASS), timeout=5)
        if not clear: threading.Timer(8, axis_overlay, [ip, 0, True]).start()
    except: pass

def procesar_deteccion(radar_name, ip, speed):
    cat, emo = clasificar_infraccion(speed)
    ahora_dt = datetime.now()
    hora_s = ahora_dt.strftime('%H:%M:%S')
    archivo_foto = None

    if speed >= 55:
        threading.Thread(target=axis_overlay, args=(ip, speed)).start()
        try:
            r = requests.get(f"http://{ip}/axis-cgi/jpg/image.cgi", auth=HTTPDigestAuth(USER, PASS), timeout=10)
            if r.status_code == 200:
                archivo_foto = f"{radar_name}_{speed}_{ahora_dt.strftime('%H%M%S')}.jpg"
                ruta_f = os.path.join(FOTOS_PATH, archivo_foto)
                with open(ruta_f, "wb") as f: f.write(r.content)
        except: pass

    # Registro en DB e IA
    registrar_historial(radar_name, speed, archivo_foto, "PROCESANDO...")
    
    # Escritura en log de texto (Línea restaurada)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{ahora_dt}] {radar_name} - {speed} km/h - {cat}\n")
    except: pass

    cap = f"{emo} <b>{cat}</b>\n📍 Radar: <b>{radar_name}</b>\n⚡ Velocidad: <b>{speed} km/h</b>\n📄 Placa: ⏳ <i>Procesando...</i>\n⏰ {hora_s}"
    
    if speed >= 55 and archivo_foto:
        with open(os.path.join(FOTOS_PATH, archivo_foto), 'rb') as f:
            res = enviar_seguro("sendPhoto", {'chat_id': CHAT_ID, 'caption': cap, 'parse_mode': 'HTML'}, files={'photo': f})
            if res and res.get('ok'):
                threading.Thread(target=hilo_ia_lpr, args=(os.path.join(FOTOS_PATH, archivo_foto), res['result']['message_id'], radar_name, speed, hora_s)).start()
        
        if speed >= 60:
            threading.Thread(target=grabar_y_enviar_video_robusto, args=(radar_name, ip, speed, cap)).start()
        
        # Sticker Kirby para Graves (Línea restaurada)
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