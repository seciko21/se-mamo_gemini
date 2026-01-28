import socket, time, requests, os, subprocess, threading, sqlite3, json, cv2
import easyocr
import numpy as np
from requests.auth import HTTPDigestAuth
from datetime import datetime
from config import *

# ==========================================
# CORRECCIÓN DE HORA Y CONFIGURACIÓN IA
# ==========================================
os.environ['TZ'] = 'America/Mexico_City'
try:
    time.tzset()
    print(f"✅ [RELOJ] Hora local sincronizada: {datetime.now()}")
except:
    pass

# Inicializar lector IA (Se carga una vez en memoria)
reader = easyocr.Reader(['es'], gpu=False)

# ==========================================
# 1. ESTADO Y VARIABLES GLOBALES (RUTAS CORREGIDAS)
# ==========================================
BASE_DIR = "/mnt/darat"
DB_FILE = f"{BASE_DIR}/data/cola_mensajes.db"
FOTOS_PATH = "/mnt/darat/multas_fotos/"
VIDEO_PATH = "/mnt/darat/clips/"
LOG_FILE = f"{VIDEO_PATH}velocidades.log"

LAST_SEEN = {name: time.time() for name in RADARES} 
RADAR_STATUS = {name: True for name in RADARES}     

# Asegurar que las carpetas existan en el nuevo disco
for ruta in [FOTOS_PATH, VIDEO_PATH, f"{BASE_DIR}/data"]:
    if not os.path.exists(ruta):
        os.makedirs(ruta, exist_ok=True)

# ==========================================
# 2. CAPA DE DATOS (SQLite / IA / Cola)
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
                        radar TEXT, 
                        velocidad INTEGER, 
                        fecha DATE DEFAULT (CURRENT_DATE),
                        hora TIME DEFAULT (CURRENT_TIME),
                        foto TEXT,
                        placa TEXT)''')
        
        conn.commit()
        conn.close()
        print(f"✅ [DB] Estructura lista en: {DB_FILE}")
    except Exception as e:
        print(f"❌ [DB] Error: {e}")

def registrar_historial(radar, speed, foto=None, placa=None):
    """Guarda detección incluyendo evidencia visual y lectura de IA."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        fecha_local = datetime.now().strftime('%Y-%m-%d')
        hora_local = datetime.now().strftime('%H:%M:%S')
        
        c.execute("INSERT INTO historial (radar, velocidad, fecha, hora, foto, placa) VALUES (?, ?, ?, ?, ?, ?)", 
                  (radar, speed, fecha_local, hora_local, foto, placa))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ [DB] Error al registrar historial: {e}")

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
# 3. MOTOR DE INTELIGENCIA ARTIFICIAL (LPR)
# ==========================================
def procesar_lpr(ruta_foto):
    """Analiza únicamente la MITAD IZQUIERDA de la imagen para extraer la placa."""
    try:
        img = cv2.imread(ruta_foto)
        if img is None: return "ERROR_IMAGEN"
        
        alto, ancho = img.shape[:2]
        recorte = img[0:alto, 0:ancho // 2]
        
        resultados = reader.readtext(recorte)
        
        for (bbox, text, prob) in resultados:
            limpio = "".join(e for e in text if e.isalnum()).upper()
            if len(limpio) >= 4:
                print(f"🔎 [IA] Placa detectada (IZQ): {limpio} ({int(prob*100)}% conf)")
                return limpio
        return "NO_DETECTADA"
    except Exception as e:
        print(f"⚠️ [IA] Error en OCR: {e}")
        return "ERROR_IA"

# ==========================================
# 4. COMUNICACIÓN Y MANTENIMIENTO
# ==========================================
def enviar_seguro(metodo, params, files=None):
    url = f"https://api.telegram.org/bot{TOKEN}/{metodo}"
    try:
        if files:
            r = requests.post(url, data=params, files=files, timeout=25)
        else:
            r = requests.post(url, json=params, timeout=10)
        r.raise_for_status()
    except:
        if metodo not in ["sendPhoto", "sendVideo"]:
            guardar_en_cola(metodo, params)

def motor_mantenimiento():
    print("🕵️ [SISTEMA] Watchdog y Auto-limpieza activos.")
    while True:
        ahora = time.time()
        for nombre, last_time in LAST_SEEN.items():
            diff = ahora - last_time
            if diff > 3600 and RADAR_STATUS[nombre]:
                RADAR_STATUS[nombre] = False
                enviar_seguro("sendMessage", {"chat_id": CHAT_ID, "text": f"🚨 <b>SISTEMA:</b> {nombre} OFFLINE.", "parse_mode": "HTML"})
            elif diff < 60 and not RADAR_STATUS[nombre]:
                RADAR_STATUS[nombre] = True
                enviar_seguro("sendMessage", {"chat_id": CHAT_ID, "text": f"✅ <b>SISTEMA:</b> {nombre} ONLINE.", "parse_mode": "HTML"})
        
        try:
            st = os.statvfs(BASE_DIR)
            uso = ((st.f_blocks - st.f_bavail) / st.f_blocks) * 100
            if uso > 90:
                archivos = sorted([os.path.join(VIDEO_PATH, f) for f in os.listdir(VIDEO_PATH)], key=os.path.getmtime)
                for i in range(min(20, len(archivos))): os.remove(archivos[i])
        except: pass
        time.sleep(300)

# ==========================================
# 5. LÓGICA DE DETECCIÓN Y MULTIMEDIA
# ==========================================
def clasificar_infraccion(velocidad):
    if velocidad <= 54: return "🚗 PREVENTIVO", "✅"
    elif 55 <= velocidad <= 59: return "⚠️ ALERTA", "🟡"
    else: return "🚀 GRAVE", "🔴"

def axis_overlay(ip, speed, clear=False):
    txt = " " if clear else f"INFRACCION: {speed} km/h"
    try:
        requests.get(f"http://{ip}/axis-cgi/overlaymanager.cgi?action=settext&text={txt.replace(' ', '+')}", 
                      auth=HTTPDigestAuth(USER, PASS), timeout=5)
        if not clear: threading.Timer(8, axis_overlay, [ip, 0, True]).start()
    except: pass

def grabar_y_enviar_video(ip, speed, caption):
    ahora_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    fname = f"{VIDEO_PATH}inf_{speed}_{ahora_str}.mp4"
    comando = ["ffmpeg", "-rtsp_transport", "tcp", "-i", f"rtsp://{USER}:{PASS}@{ip}/axis-media/media.amp", "-t", "15", "-c", "copy", "-y", fname]
    try:
        subprocess.run(comando, check=True, timeout=30, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(fname) and os.path.getsize(fname) > 100000:
            with open(fname, 'rb') as v:
                enviar_seguro("sendVideo", {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}, files={'video': v})
    except: pass

def procesar_deteccion(radar_name, ip, speed):
    categoria, emoji = clasificar_infraccion(speed)
    ahora_dt = datetime.now()
    ahora_str = ahora_dt.strftime('%H:%M:%S')
    
    archivo_foto = None
    texto_placa = "NO_APLICA"

    if speed >= 55:
        axis_overlay(ip, speed)
        try:
            r = requests.get(f"http://{ip}/axis-cgi/jpg/image.cgi", auth=HTTPDigestAuth(USER, PASS), timeout=15)
            if r.status_code == 200:
                archivo_foto = f"{radar_name}_{speed}_{ahora_dt.strftime('%Y%m%d_%H%M%S')}.jpg"
                ruta_completa = os.path.join(FOTOS_PATH, archivo_foto)
                with open(ruta_completa, "wb") as f:
                    f.write(r.content)
                
                # IA procesando solo la mitad izquierda del archivo guardado
                texto_placa = procesar_lpr(ruta_completa)
        except Exception as e:
            print(f"⚠️ Error capturando foto/IA: {e}")

    # Registrar siempre en historial (IA + DB)
    registrar_historial(radar_name, speed, archivo_foto, texto_placa)

    # --- DOBLE ESCRITURA: LOG DE TEXTO PARA TAIL -F ---
    try:
        log_line = f"[{ahora_dt}] {radar_name} - {speed} km/h - {categoria}\n"
        with open(LOG_FILE, "a") as f:
            f.write(log_line)
    except:
        pass
    
    placa_txt = f"\n📄 Placa: <b>{texto_placa}</b>" if texto_placa not in ["NO_APLICA", "NO_DETECTADA"] else ""
    caption = f"{emoji} <b>{categoria}</b>\n📍 Radar: <b>{radar_name}</b>\n⚡ Velocidad: <b>{speed} km/h</b>\n⏰ Hora: {ahora_str}{placa_txt}"
    
    if speed >= 55:
        # Video solo para Graves (>=60)
        if speed >= 60: threading.Thread(target=grabar_y_enviar_video, args=(ip, speed, caption)).start()
        
        # Enviar foto capturada
        if archivo_foto:
            ruta_completa = os.path.join(FOTOS_PATH, archivo_foto)
            with open(ruta_completa, 'rb') as p:
                enviar_seguro("sendPhoto", {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}, files={'photo': p})
        
        # Sticker Kirby solo para Graves
        if speed >= 60 and 'STICKER_KIRBY' in globals():
            enviar_seguro("sendSticker", {"chat_id": CHAT_ID, "sticker": STICKER_KIRBY})
    else:
        # Preventivos: Solo texto
        enviar_seguro("sendMessage", {"chat_id": CHAT_ID, "text": caption, "parse_mode": "HTML"})

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
                if speed >= 1: 
                    threading.Thread(target=procesar_deteccion, args=(nombre, ip, speed)).start()
        except: time.sleep(10)

if __name__ == "__main__":
    init_db()
    threading.Thread(target=procesar_cola_reintentos, daemon=True).start()
    threading.Thread(target=motor_mantenimiento, daemon=True).start()
    for n, d in RADARES.items():
        threading.Thread(target=escuchar_radar, args=(n, d['ip'], d['puerto']), daemon=True).start()
    while True: time.sleep(1)