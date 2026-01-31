import requests, time, os, urllib3, threading, subprocess, socket, sqlite3, json
from requests.auth import HTTPDigestAuth
from datetime import datetime
from config import *

# ==========================================
# CORRECCIÓN DE ZONA HORARIA (CRÍTICO PARA REPORTES)
# ==========================================
os.environ['TZ'] = 'America/Mexico_City'
try:
    time.tzset()
    print(f"✅ [RELOJ] Bot sincronizado: {datetime.now()}")
except:
    pass
# ==========================================

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURACIÓN DE ENLACE ACTUALIZADA (TAILSCALE + PUERTO 8085) ---
URL_DASHBOARD = os.getenv("URL_PUBLICO", "http://localhost:8501")
# Ruta de la DB basada en tu configuración de 900GB (/mnt/darat)
DB_PATH_REAL = "/mnt/darat/data/cola_mensajes.db"
# Aseguramos que VIDEO_PATH y FOTOS_PATH apunten al disco de 900GB
VIDEO_PATH = "/mnt/darat/clips/"
FOTOS_PATH = "/mnt/darat/multas_fotos/"

# --- FUNCIÓN PARA CONSTRUIR EL ESTADO LLAMATIVO ---

def obtener_mensaje_estado(ip_servidor):
    """Construye la tarjeta visual con barra de progreso y estadísticas del disco corregido a 900GB."""
    try:
        st = os.statvfs('/mnt/darat/')
        libre = (st.f_bavail * st.f_frsize) / (1024**3)
        total_disk = (st.f_blocks * st.f_frsize) / (1024**3)
        porcentaje_usado = ((total_disk - libre) / total_disk) * 100
        
        # Conteo de archivos en el disco de 900GB
        clips = [f for f in os.listdir(VIDEO_PATH) if f.endswith('.mp4')]
        fotos = [f for f in os.listdir(FOTOS_PATH) if f.endswith('.jpg')]
        
        bloques = 10
        llenos = int(porcentaje_usado / bloques)
        barra = "▰" * llenos + "▱" * (bloques - llenos)

        return (
            "💓 <b>ESTADO DEL RADAR (HEARTBEAT)</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🖥 <b>SERVIDOR:</b> <code>{ip_servidor}</code>\n"
            f"💾 <b>DISCO ALMACENAMIENTO (900GB):</b>\n"
            f"<code>{barra}</code> {porcentaje_usado:.1f}%\n"
            f"├ Disponible: <b>{libre:.2f} GB</b>\n"
            f"├ Clips en memoria: <b>{len(clips)}</b>\n"
            f"└ Fotos capturadas: <b>{len(fotos)}</b>\n\n"
            "✅ <b>ESTADO:</b> Sincronizado v5.0 (Tailscale)\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🕒 <b>ACTUALIZADO:</b> {datetime.now().strftime('%H:%M:%S')}"
        )
    except Exception as e:
        return f"❌ Error al obtener estado: {e}"

# --- PANEL DE SALUD ACTUALIZADO ---

def verificar_salud_red():
    reporte = "🌐 <b>PANEL DE SALUD DE RADARES</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    for nombre, datos in RADARES.items():
        ip = datos['ip']
        puerto = datos['puerto']
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex((ip, puerto))
            s.close()
            estado = "🟢 <b>ONLINE</b>" if result == 0 else "🔴 <b>OFFLINE</b>"
        except:
            estado = "🔴 <b>ERROR</b>"
        
        reporte += f"📡 <b>{nombre}:</b> {estado}\n  <code>{ip}:{puerto}</code>\n\n"
    
    reporte += f"🕒 <i>Check: {datetime.now().strftime('%H:%M:%S')}</i>"
    return reporte

# --- MOTORES DE SEGUIMIENTO ---

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

# --- FUNCIONES DE APOYO CORREGIDAS PARA SQLITE ---

def depurar_disco_viejo():
    try:
        archivos = [os.path.join(VIDEO_PATH, f) for f in os.listdir(VIDEO_PATH) if f.endswith('.mp4')]
        if not archivos: return "📁 Nada que limpiar."
        archivos.sort(key=os.path.getmtime)
        limite = max(1, len(archivos) // 3)
        for i in range(limite): os.remove(archivos[i])
        return f"✅ Depuración completa: {limite} videos eliminados en /mnt/darat/."
    except Exception as e: return f"❌ Error: {e}"

def generar_reporte_diario():
    """Genera reporte consultando la DB SQLite para datos actualizados."""
    try:
        if not os.path.exists(DB_PATH_REAL): return "❌ No hay base de datos en /mnt/darat/."
        hoy = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(DB_PATH_REAL)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*), 
                SUM(CASE WHEN velocidad >= 60 THEN 1 ELSE 0 END),
                SUM(CASE WHEN velocidad >= 55 AND velocidad <= 59 THEN 1 ELSE 0 END),
                SUM(CASE WHEN velocidad < 55 THEN 1 ELSE 0 END),
                AVG(velocidad)
            FROM historial WHERE fecha = ?
        """, (hoy,))
        
        total, graves, alertas, preventivos, promedio = cursor.fetchone()
        conn.close()

        if not total or total == 0: 
            return f"📅 Sin detecciones hoy ({hoy})."

        return (f"📊 <b>RESUMEN ({hoy})</b>\n\n"
                f"✅ Total: {total}\n"
                f"🚗 Prev: {preventivos or 0}\n"
                f"⚠️ Alert: {alertas or 0}\n"
                f"🚀 Grave: {graves or 0}\n"
                f"📈 Prom: {(promedio or 0):.1f} km/h")
    except Exception as e: return f"❌ Error Reporte DB: {e}"

def leer_log_telegram():
    """Obtiene los últimos 15 registros de la DB para evitar el lag de archivos de texto."""
    try:
        if not os.path.exists(DB_PATH_REAL): return "📝 <b>Sin registros en DB.</b>"
        
        conn = sqlite3.connect(DB_PATH_REAL)
        cursor = conn.cursor()
        cursor.execute("SELECT fecha, hora, radar, velocidad FROM historial ORDER BY id DESC LIMIT 15")
        rows = cursor.fetchall()
        conn.close()

        if not rows: return "📝 <b>No hay registros hoy.</b>"

        mensaje = ""
        for r in reversed(rows):
            emoji = "🔴" if r[3] >= 60 else "🟡" if r[3] >= 55 else "✅"
            mensaje += f"{emoji} [{r[1]}] {r[2]}: {r[3]}km/h\n"
        
        return f"📜 <b>ÚLTIMOS REGISTROS (DB):</b>\n\n<code>{mensaje}</code>"
    except Exception as e: return f"❌ Error al leer DB: {e}"

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
    ahora = datetime.now().strftime('%d/%m/%Y')
    return (
        "🚀 <b>SISTEMA DE MONITOREO RADAR PRO v5.0</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🛰 <b>ESTADO DEL SISTEMA:</b> <code>OPERATIVO</code>\n"
        "📅 <b>ÚLTIMA ACTUALIZACIÓN:</b> <code>" + ahora + "</code>\n\n"
        "⚡ <b>CLASIFICACIÓN DE INFRACCIONES:</b>\n"
        "• 🚗 <b>PREVENTIVO (≤ 54 km/h):</b> Registro y notificación.\n"
        "• ⚠️ <b>ALERTA (55 - 59 km/h):</b> Foto instantánea.\n"
        "• 🚀 <b>GRAVE (≥ 60 km/h):</b> Foto + 🎥 Video (15s).\n\n"
        "🛠 <b>CAPACIDADES TÉCNICAS:</b>\n"
        "• <b>Almacenamiento:</b> 900GB en /mnt/darat/.\n"
        "• <b>Acceso Remoto:</b> Tailscale Activa.\n"
        "• <b>Puerto Dashboard:</b> 8085.\n\n"
        "👉 <a href='" + URL_DASHBOARD + "'>PANEL DE CONTROL RADAR</a>"
    )

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

# --- INTERFAZ ---

TECLADO = {
    "keyboard": [
        [{"text": "📊 Reporte de Hoy"}, {"text": "📜 Ver Log de Velocidad"}],
        [{"text": "📸 Forzar Captura de Prueba"}],
        [{"text": "🎥 Forzar Video de Prueba (15s)"}],
        [{"text": "💾 Estado del Disco"}, {"text": "📂 Ver últimos clips"}],
        [{"text": "🧹 Depurar Disco (Borrar viejos)"}, {"text": "🌐 Salud de la Red"}],
        [{"text": "📖 Manual y Proyecto"}]
    ], "resize_keyboard": True
}

MENU_FOTOS = {"inline_keyboard": [[{"text": f"📍 {n}", "callback_data": f"foto_{n}"}] for n in RADARES.keys()]}

def listen_bot():
    last_id = 0
    print("🤖 Bot de Comandos Activo.")
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            res = requests.get(url, params={"offset": last_id + 1, "timeout": 20}).json()
            for up in res.get("result", []):
                last_id = up["update_id"]
                
                if "callback_query" in up:
                    data = up["callback_query"]["data"]
                    if data.startswith("foto_"):
                        rk = data.split("_")[1]
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": f"📸 Capturando {rk}..."})
                        foto = axis_snapshot(RADARES[rk]["ip"])
                        if foto:
                            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", 
                                          data={'chat_id': CHAT_ID, 'caption': f"✅ Prueba: {rk}"}, files={'photo': foto})
                    continue

                msg = up.get("message", {}); txt = msg.get("text", "")
                if not txt: continue

                if "/start" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": "🎮 <b>RADAR PRO v5.0</b>", "reply_markup": TECLADO, "parse_mode": "HTML"})

                elif "Reporte" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": generar_reporte_diario(), "parse_mode": "HTML"})

                elif "Log" in txt or "📜" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": leer_log_telegram(), "parse_mode": "HTML"})

                elif "Captura" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": "📸 Elija radar para captura:", "reply_markup": MENU_FOTOS})

                elif "Video" in txt:
                    rk = list(RADARES.keys())[0] 
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": f"🎬 Grabando video en {rk}..."})
                    grabar_video_manual(RADARES[rk]["ip"])

                elif "clips" in txt.lower():
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": obtener_ultimos_clips(), "parse_mode": "HTML"})

                elif "Manual" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": obtener_manual_proyecto(), "parse_mode": "HTML"})

                elif "Disco" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": obtener_mensaje_estado("LocalHost"), "parse_mode": "HTML"})

                elif "Salud" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": verificar_salud_red(), "parse_mode": "HTML"})

                elif "Depurar" in txt:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": depurar_disco_viejo()})

                elif ".mp4" in txt.lower():
                    ruta = os.path.join(VIDEO_PATH, txt.strip())
                    if os.path.exists(ruta):
                        with open(ruta, 'rb') as v: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo", data={'chat_id': CHAT_ID}, files={'video': v})
        except: time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=servicio_heartbeat, daemon=True).start()
    threading.Thread(target=reporte_automatico_cierre, daemon=True).start()
    listen_bot()