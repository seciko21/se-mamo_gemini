import requests, time, os, urllib3, threading, subprocess, socket, sqlite3, json, cv2
import numpy as np
from requests.auth import HTTPDigestAuth
from datetime import datetime
from config import *

# ==========================================
# 1. CONFIGURACIÓN Y ENTORNO
# ==========================================
os.environ['TZ'] = 'America/Mexico_City'
try:
    time.tzset()
    print(f"✅ [RELOJ] Bot sincronizado: {datetime.now()}")
except:
    pass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Rutas críticas del disco de 900GB
DB_PATH_REAL = "/mnt/darat/data/cola_mensajes.db"
VIDEO_PATH = "/mnt/darat/clips/"
FOTOS_PATH = "/mnt/darat/multas_fotos/"
URL_DASHBOARD = os.getenv("URL_PUBLICO", "http://localhost:8501")

# Intentar importar el motor de IA de Clawdbot (Integración)
try:
    from monitor_radar import reader, model_ai, validar_placa
    IA_ACTIVA = True
    print("🤖 Clawdbot Engine: Integrado con éxito al Bot.")
except Exception as e:
    IA_ACTIVA = False
    print(f"⚠️ Clawdbot Engine: No disponible (usando modo estándar). Error: {e}")

# ==========================================
# 2. MOTOR DE IA PARA CAPTURAS MANUALES
# ==========================================
def procesar_captura_con_ia(img_bytes, radar_name):
    """Analiza una foto manual usando el cerebro de Clawdbot."""
    if not IA_ACTIVA: return img_bytes, "IA Desactivada"
    
    try:
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Clasificación YOLO
        results = model_ai(img)
        tipo = "🚗 Vehículo"
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                if float(box.conf[0]) > 0.4:
                    if cls_id == 2: tipo = "🚗 Automóvil"
                    elif cls_id == 3: tipo = "🏍️ Motocicleta"
                    elif cls_id == 5: tipo = "🚌 Autobús"
                    elif cls_id == 7: tipo = "🚛 Camión"
        
        # Lectura de Placa OCR
        alto, ancho = img.shape[:2]
        resultados_ocr = reader.readtext(img[0:alto, 0:ancho // 2])
        placa = "No detectada"
        for (bbox, text, prob) in resultados_ocr:
            cand = validar_placa(text)
            if cand: 
                placa = cand
                p1 = (int(bbox[0][0]), int(bbox[0][1]))
                p2 = (int(bbox[2][0]), int(bbox[2][1]))
                cv2.rectangle(img, p1, p2, (0, 255, 0), 2)
                break

        # Estampado CSI Manual
        cv2.putText(img, f"CAPTURA MANUAL: {radar_name}", (30, alto - 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4)
        cv2.putText(img, f"CAPTURA MANUAL: {radar_name}", (30, alto - 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        _, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes(), f"🚘 Tipo: {tipo}\n📄 Placa: {placa}"
    except:
        return img_bytes, "⚠️ Error en procesado IA"

# ==========================================
# 3. FUNCIONES DE ESTADO Y DISCO
# ==========================================
def obtener_mensaje_estado(ip_servidor):
    try:
        st = os.statvfs('/mnt/darat/')
        libre = (st.f_bavail * st.f_frsize) / (1024**3)
        total_disk = (st.f_blocks * st.f_frsize) / (1024**3)
        porcentaje_usado = ((total_disk - libre) / total_disk) * 100
        
        clips = [f for f in os.listdir(VIDEO_PATH) if f.endswith('.mp4')]
        barra = "▰" * int(porcentaje_usado / 10) + "▱" * (10 - int(porcentaje_usado / 10))

        return (
            "💓 <b>HEARTBEAT CLAWDBOT</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🖥 <b>IP:</b> <code>{ip_servidor}</code>\n"
            f"💾 <b>DISCO (900GB):</b>\n"
            f"<code>{barra}</code> {porcentaje_usado:.1f}%\n"
            f"├ Disponible: <b>{libre:.2f} GB</b>\n"
            f"└ Clips en disco: <b>{len(clips)}</b>\n\n"
            f"🕒 <b>SINC:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    except: return "❌ Error de disco."

def verificar_salud_red():
    reporte = "🌐 <b>SALUD DE RADARES</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    for nombre, datos in RADARES.items():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex((datos['ip'], datos['puerto']))
            s.close()
            estado = "🟢 ONLINE" if result == 0 else "🔴 OFFLINE"
            reporte += f"📡 <b>{nombre}:</b> {estado}\n"
        except: reporte += f"📡 <b>{nombre}:</b> 🔴 ERROR\n"
    return reporte

def depurar_disco_viejo():
    try:
        archivos = [os.path.join(VIDEO_PATH, f) for f in os.listdir(VIDEO_PATH) if f.endswith('.mp4')]
        if not archivos: return "📁 Nada que limpiar."
        archivos.sort(key=os.path.getmtime)
        limite = max(1, len(archivos) // 3)
        for i in range(limite): os.remove(archivos[i])
        return f"✅ Depuración completa: {limite} videos eliminados."
    except Exception as e: return f"❌ Error: {e}"

def obtener_ultimos_clips():
    try:
        archivos = [f for f in os.listdir(VIDEO_PATH) if f.endswith('.mp4')]
        archivos.sort(key=lambda x: os.path.getmtime(os.path.join(VIDEO_PATH, x)), reverse=True)
        top = archivos[:5]
        lista = "📂 <b>ÚLTIMOS CLIPS (900GB):</b>\n\n"
        for arc in top: lista += f"• <code>{arc}</code>\n"
        return lista + "\n<i>💡 Escribe el nombre para descargar.</i>"
    except: return "❌ Error clips."

def obtener_manual_proyecto():
    """Muestra ayuda y link al dashboard (RESTAURADO)."""
    return (
        "🚀 <b>CLAWDBOT v5.7 (IA EDITION)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🛠 <b>COMANDOS DISPONIBLES:</b>\n"
        "• 📸 <b>Captura:</b> Foto manual con análisis IA.\n"
        "• 🎥 <b>Video:</b> Graba 15s manualmente.\n"
        "• 💾 <b>Disco:</b> Estado del servidor.\n"
        "• 📜 <b>Log:</b> Últimas 10 detecciones.\n"
        "• 🧹 <b>Depurar:</b> Limpia videos viejos.\n\n"
        "👉 Escribe el nombre de un archivo .mp4 para descargarlo.\n\n"
        f"🔗 <a href='{URL_DASHBOARD}'>ACCEDER AL DASHBOARD WEB</a>"
    )

# ==========================================
# 4. REPORTES Y LOGS (SQLITE OPTIMIZADO)
# ==========================================
def generar_reporte_diario():
    try:
        conn = sqlite3.connect(DB_PATH_REAL)
        cursor = conn.cursor()
        hoy = datetime.now().strftime('%Y-%m-%d')
        
        # Consulta corregida para el desglose exacto
        cursor.execute("""
            SELECT 
                COUNT(*), 
                SUM(CASE WHEN velocidad < 55 THEN 1 ELSE 0 END),
                SUM(CASE WHEN velocidad >= 55 AND velocidad < 60 THEN 1 ELSE 0 END),
                SUM(CASE WHEN velocidad >= 60 THEN 1 ELSE 0 END),
                AVG(velocidad) 
            FROM historial WHERE fecha = ?
        """, (hoy,))
        
        fila = cursor.fetchone()
        conn.close()
        
        total = fila[0] or 0
        prev = fila[1] or 0
        alert = fila[2] or 0
        grave = fila[3] or 0
        prom = fila[4] or 0

        if total == 0: return f"📅 Sin actividad hoy ({hoy})."

        return (f"📊 <b>RESUMEN ({hoy})</b>\n\n"
                f"✅ Total: <b>{total}</b>\n"
                f"🚗 Prev: <b>{prev}</b>\n"
                f"⚠️ Alert: <b>{alert}</b>\n"
                f"🚀 Grave: <b>{grave}</b>\n"
                f"📈 Prom: <b>{prom:.1f} km/h</b>")
    except Exception as e: return f"❌ Error DB: {e}"

def leer_log_db():
    try:
        conn = sqlite3.connect(DB_PATH_REAL)
        cursor = conn.cursor()
        cursor.execute("SELECT hora, radar, velocidad FROM historial ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()
        conn.close()
        
        mensaje = ""
        for r in reversed(rows):
            emoji = "🔴" if r[2] >= 60 else "🟡" if r[2] >= 55 else "✅"
            mensaje += f"{emoji} [{r[0]}] {r[1]}: {r[2]}km/h\n"
        return f"📜 <b>ÚLTIMOS 10 REGISTROS:</b>\n\n<code>{mensaje}</code>"
    except: return "❌ Error lectura Log."

# ==========================================
# 5. FUNCIONES DE ACCIÓN (HARDWARE)
# ==========================================
def axis_snapshot(ip):
    try:
        r = requests.get(f"http://{ip}/axis-cgi/jpg/image.cgi", auth=HTTPDigestAuth(USER, PASS), timeout=10)
        return r.content if r.status_code == 200 else None
    except: return None

def grabar_video_manual(ip):
    ahora = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{VIDEO_PATH}manual_{ahora}.mp4"
    cmd = ["ffmpeg", "-rtsp_transport", "tcp", "-i", f"rtsp://{USER}:{PASS}@{ip}/axis-media/media.amp",
           "-t", "15", "-c", "copy", "-y", filename]
    subprocess.Popen(cmd)
    
    def enviar():
        time.sleep(17) 
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, 'rb') as v:
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo",
                              data={'chat_id': CHAT_ID, 'caption': f'🎥 Video Manual {ahora}'}, files={'video': v})
    threading.Thread(target=enviar).start()

# ==========================================
# 6. HILOS AUTOMÁTICOS (HEARTBEAT Y REPORTE)
# ==========================================
def servicio_heartbeat():
    print("💓 Motor Heartbeat iniciado.")
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_servidor = s.getsockname()[0]
            s.close()
            
            msg_latido = obtener_mensaje_estado(ip_servidor)
            markup = {"inline_keyboard": [[{"text": "🌐 IR AL PANEL WEB", "url": URL_DASHBOARD}]]}
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": msg_latido, "parse_mode": "HTML", "reply_markup": markup})
            time.sleep(43200) # Cada 12 horas
        except: time.sleep(60)

def reporte_automatico_cierre():
    print("⏰ Motor de Reporte Automático iniciado.")
    enviado = False
    while True:
        try:
            ahora = datetime.now()
            if ahora.hour == 23 and ahora.minute == 59 and not enviado:
                reporte = generar_reporte_diario()
                msg = f"🤖 <b>CIERRE AUTOMÁTICO DEL DÍA</b>\n\n{reporte}"
                markup = {"inline_keyboard": [[{"text": "📊 VER DASHBOARD", "url": URL_DASHBOARD}]]}
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                              json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML", "reply_markup": markup})
                enviado = True
                time.sleep(120)
            if ahora.hour == 0: enviado = False
            time.sleep(30)
        except: time.sleep(30)

# ==========================================
# 7. INTERFAZ Y BUCLE PRINCIPAL
# ==========================================
TECLADO = {
    "keyboard": [
        [{"text": "📊 Reporte de Hoy"}, {"text": "📜 Ver Log"}],
        [{"text": "📸 Captura Manual IA"}],
        [{"text": "🎥 Forzar Video (15s)"}, {"text": "📂 Ver últimos clips"}],
        [{"text": "💾 Estado del Disco"}, {"text": "🌐 Salud de la Red"}],
        [{"text": "🧹 Depurar Disco"}, {"text": "📖 Manual y Proyecto"}]
    ], "resize_keyboard": True
}

MENU_FOTOS_IA = {"inline_keyboard": [[{"text": f"📍 {n}", "callback_data": f"iafoto_{n}"}] for n in RADARES.keys()]}
MENU_VIDEOS = {"inline_keyboard": [[{"text": f"🎥 {n}", "callback_data": f"vid_{n}"}] for n in RADARES.keys()]}

def listen_bot():
    last_id = 0
    print("🤖 Bot de Comandos (IA + Funciones Completas) Activo.")
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            res = requests.get(url, params={"offset": last_id + 1, "timeout": 20}).json()
            for up in res.get("result", []):
                last_id = up["update_id"]
                
                # --- MANEJO DE BOTONES (CALLBACKS) ---
                if "callback_query" in up:
                    data = up["callback_query"]["data"]
                    
                    # FOTO CON IA
                    if data.startswith("iafoto_"):
                        rk = data.split("_")[1]
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": f"🧠 Analizando {rk}..."})
                        raw_img = axis_snapshot(RADARES[rk]["ip"])
                        if raw_img:
                            procesada, caption_ia = procesar_captura_con_ia(raw_img, rk)
                            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", 
                                          data={'chat_id': CHAT_ID, 'caption': f"📸 <b>{rk}</b>\n{caption_ia}", 'parse_mode': 'HTML'}, 
                                          files={'photo': procesada})
                    
                    # VIDEO MANUAL
                    elif data.startswith("vid_"):
                        rk = data.split("_")[1]
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": f"🎬 Grabando 15s en {rk}..."})
                        grabar_video_manual(RADARES[rk]["ip"])
                    continue

                # --- MANEJO DE TEXTO ---
                msg = up.get("message", {}); txt = msg.get("text", "")
                if not txt: continue

                if "/start" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                  json={"chat_id": CHAT_ID, "text": "🎮 <b>CENTRAL CLAWDBOT v5.7</b>", "reply_markup": TECLADO, "parse_mode": "HTML"})
                
                elif "Reporte" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": generar_reporte_diario(), "parse_mode": "HTML"})
                
                elif "Log" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": leer_log_db(), "parse_mode": "HTML"})
                
                elif "Captura" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": "📸 Seleccione radar para análisis IA:", "reply_markup": MENU_FOTOS_IA})
                
                elif "Forzar Video" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": "🎥 Seleccione radar para grabar:", "reply_markup": MENU_VIDEOS})

                elif "clips" in txt.lower():
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": obtener_ultimos_clips(), "parse_mode": "HTML"})
                
                elif "Disco" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": obtener_mensaje_estado("localhost"), "parse_mode": "HTML"})
                
                elif "Salud" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": verificar_salud_red(), "parse_mode": "HTML"})
                
                elif "Depurar" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": depurar_disco_viejo()})
                
                elif "Manual" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": obtener_manual_proyecto(), "parse_mode": "HTML"})

                # DESCARGA DE ARCHIVOS MP4
                elif ".mp4" in txt.lower():
                    ruta = os.path.join(VIDEO_PATH, txt.strip())
                    if os.path.exists(ruta):
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": "📤 Subiendo video..."})
                        with open(ruta, 'rb') as v: 
                            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo", data={'chat_id': CHAT_ID}, files={'video': v})
                    else:
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": "❌ Archivo no encontrado."})

        except: time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=servicio_heartbeat, daemon=True).start()
    threading.Thread(target=reporte_automatico_cierre, daemon=True).start()
    listen_bot()