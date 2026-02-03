import requests, time, os, urllib3, threading, subprocess, socket, sqlite3, json, cv2
import numpy as np
from requests.auth import HTTPDigestAuth
from datetime import datetime
from config import *

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
os.environ['TZ'] = 'America/Mexico_City'
try: time.tzset()
except: pass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DB_PATH_REAL = "/mnt/darat/data/cola_mensajes.db"
VIDEO_PATH = "/mnt/darat/clips/"
FOTOS_PATH = "/mnt/darat/multas_fotos/"
URL_DASHBOARD = os.getenv("URL_PUBLICO", "http://localhost:8501")

# --- ZONA DE PERSONALIZACIÓN ---
# PASO 1: Envía tu sticker favorito al bot por Telegram.
# PASO 2: El bot te responderá con el ID. Copialo y pegalo aquí abajo.
STICKER_ROCKET = "CAACAgIAAxkBAAEQaN5pgUyrg7oYGh4H2oAEarPqApF9kgAC9QAD9wLID0dGmGHRUMixOAQ" 

try:
    from monitor_radar import reader, model_ai, validar_placa
    IA_ACTIVA = True
except:
    IA_ACTIVA = False

# ==========================================
# 2. MENÚS
# ==========================================

MENU_HOME = {
    "inline_keyboard": [
        [{"text": "📊 REPORTES E HISTORIAL", "callback_data": "menu_reportes"}],
        [{"text": "📡 CONTROL DE RADARES (IA)", "callback_data": "menu_radares"}],
        [{"text": "📂 CLIPS", "callback_data": "menu_clips"}, {"text": "⚙️ SISTEMA", "callback_data": "menu_sistema"}],
        [{"text": "🔄 REFRESCAR PANEL", "callback_data": "menu_main"}]
    ]
}

MENU_REPORTES = {
    "inline_keyboard": [
        [{"text": "📅 Resumen de Hoy", "callback_data": "cmd_reporte"}],
        [{"text": "📜 Log en Vivo (10 ult)", "callback_data": "cmd_log"}],
        [{"text": "🔙 VOLVER", "callback_data": "menu_main"}]
    ]
}

MENU_SISTEMA = {
    "inline_keyboard": [
        [{"text": "💾 DISCO", "callback_data": "cmd_disco"}, {"text": "🌐 RED", "callback_data": "cmd_salud"}],
        [{"text": "🧹 LIMPIAR CACHÉ", "callback_data": "cmd_depurar"}, {"text": "📖 AYUDA", "callback_data": "cmd_manual"}],
        [{"text": "🔙 VOLVER", "callback_data": "menu_main"}]
    ]
}

MENU_CLIPS = {
    "inline_keyboard": [
        [{"text": "📂 Ver últimos 5 clips", "callback_data": "cmd_ver_clips"}],
        [{"text": "🔙 VOLVER", "callback_data": "menu_main"}]
    ]
}

def get_menu_radares():
    botones = []
    for n in RADARES.keys():
        botones.append([{"text": f"📍 {n}", "callback_data": "none"}])
        botones.append([
            {"text": "📸 FOTO IA", "callback_data": f"iafoto_{n}"},
            {"text": "🎥 REC 15s", "callback_data": f"vid_{n}"}
        ])
    botones.append([{"text": "🔙 VOLVER", "callback_data": "menu_main"}])
    return {"inline_keyboard": botones}

# ==========================================
# 3. FUNCIONES LÓGICAS
# ==========================================

def procesar_captura_con_ia(img_bytes, radar_name):
    if not IA_ACTIVA: return img_bytes, "IA Desactivada"
    try:
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        results = model_ai(img)
        tipo = "🚗 Vehículo"
        for r in results:
            for box in r.boxes:
                if float(box.conf[0]) > 0.4:
                    cls_id = int(box.cls[0])
                    if cls_id == 2: tipo = "🚗 Automóvil"
                    elif cls_id == 3: tipo = "🏍️ Motocicleta"
                    elif cls_id == 5: tipo = "🚌 Autobús"
                    elif cls_id == 7: tipo = "🚛 Camión"
        
        alto, ancho = img.shape[:2]
        resultados_ocr = reader.readtext(img[0:alto, 0:ancho // 2])
        placa = "No detectada"
        for (bbox, text, prob) in resultados_ocr:
            cand = validar_placa(text)
            if cand: 
                placa = cand
                p1 = (int(bbox[0][0]), int(bbox[0][1])); p2 = (int(bbox[2][0]), int(bbox[2][1]))
                cv2.rectangle(img, p1, p2, (0, 255, 0), 2); break

        cv2.putText(img, f"MANUAL: {radar_name}", (30, alto-50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)
        _, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes(), f"🚘 Tipo: {tipo}\n📄 Placa: {placa}"
    except: return img_bytes, "⚠️ Error IA"

def validar_placa(texto_sucio):
    import re
    limpio = "".join(e for e in texto_sucio if e.isalnum()).upper()
    if re.search(r'\d{8,}', limpio): return None 
    if 5 <= len(limpio) <= 8: return limpio
    return None

def obtener_mensaje_estado(ip_servidor):
    try:
        st = os.statvfs('/mnt/darat/')
        libre = (st.f_bavail * st.f_frsize) / (1024**3)
        total_disk = (st.f_blocks * st.f_frsize) / (1024**3)
        porcentaje_usado = ((total_disk - libre) / total_disk) * 100
        clips = 0
        with os.scandir(VIDEO_PATH) as it:
            for entry in it:
                if entry.is_file() and entry.name.endswith('.mp4'): clips += 1
        
        barra = "▰" * int(porcentaje_usado / 10) + "▱" * (10 - int(porcentaje_usado / 10))
        return f"💾 <b>DISCO:</b> {porcentaje_usado:.1f}% Usado\n<code>{barra}</code>\n└ {libre:.2f} GB Libres | {clips} Clips"
    except: return "❌ Error disco"

def verificar_salud_red():
    rep = "🌐 <b>SALUD RED</b>\n━━━━━━━━━━━━\n"
    for n, d in RADARES.items():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(0.5)
            r = s.connect_ex((d['ip'], d['puerto'])); s.close()
            rep += f"{'🟢' if r == 0 else '🔴'} {n}\n"
        except: rep += f"❓ {n}\n"
    return rep

def depurar_disco_viejo():
    try:
        archivos = []
        with os.scandir(VIDEO_PATH) as it:
            for entry in it:
                if entry.is_file() and entry.name.endswith('.mp4'):
                    archivos.append(entry.path)
        
        if not archivos: return "📁 Nada que limpiar."
        archivos.sort(key=os.path.getmtime)
        lim = max(1, len(archivos)//3)
        for i in range(lim): os.remove(archivos[i])
        return f"✅ Depuración: {lim} videos borrados."
    except: return "❌ Error."

def generar_reporte_diario():
    try:
        conn = sqlite3.connect(DB_PATH_REAL); c = conn.cursor()
        hoy = datetime.now().strftime('%Y-%m-%d')
        c.execute("""SELECT COUNT(*), SUM(CASE WHEN velocidad < 55 THEN 1 ELSE 0 END), 
                            SUM(CASE WHEN velocidad >= 55 AND velocidad < 60 THEN 1 ELSE 0 END), 
                            SUM(CASE WHEN velocidad >= 60 THEN 1 ELSE 0 END), AVG(velocidad) 
                     FROM historial WHERE fecha = ?""", (hoy,))
        f = c.fetchone(); conn.close()
        t, p, a, g, av = f[0] or 0, f[1] or 0, f[2] or 0, f[3] or 0, f[4] or 0
        if t == 0: return f"📅 <b>{hoy}:</b> Sin actividad."
        return (f"📊 <b>REPORTE ({hoy})</b>\n\n✅ Tot: <b>{t}</b>\n🚗 Prev: <b>{p}</b>\n⚠️ Alert: <b>{a}</b>\n🚀 Grav: <b>{g}</b>\n📈 Prom: <b>{av:.1f} km/h</b>")
    except: return "❌ Error DB."

def leer_log_db():
    try:
        conn = sqlite3.connect(DB_PATH_REAL); c = conn.cursor()
        c.execute("SELECT hora, radar, velocidad FROM historial ORDER BY id DESC LIMIT 10")
        rows = c.fetchall(); conn.close()
        msg = ""
        for r in reversed(rows):
            e = "🔴" if r[2]>=60 else "🟡" if r[2]>=55 else "✅"
            msg += f"{e} [{r[0]}] {r[1]}: {r[2]}\n"
        return f"📜 <b>LOG:</b>\n<code>{msg}</code>"
    except: return "❌ Error Log"

def axis_snapshot(ip):
    try:
        r = requests.get(f"http://{ip}/axis-cgi/jpg/image.cgi", auth=HTTPDigestAuth(USER, PASS), timeout=5)
        return r.content if r.status_code == 200 else None
    except: return None

def grabar_video_manual(ip):
    ahora = datetime.now().strftime('%Y%m%d_%H%M%S'); fname = f"{VIDEO_PATH}manual_{ahora}.mp4"
    subprocess.Popen(["ffmpeg", "-rtsp_transport", "tcp", "-i", f"rtsp://{USER}:{PASS}@{ip}/axis-media/media.amp", "-t", "15", "-c", "copy", "-y", fname])
    def env():
        time.sleep(17)
        if os.path.exists(fname): 
            with open(fname, 'rb') as v: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo", data={'chat_id': CHAT_ID, 'caption': '🎬 Manual'}, files={'video': v})
    threading.Thread(target=env).start()

def obtener_ultimos_clips():
    try:
        lista_archivos = []
        with os.scandir(VIDEO_PATH) as it:
            for entry in it:
                if entry.is_file() and entry.name.endswith('.mp4'):
                    lista_archivos.append((entry.name, entry.stat().st_mtime))
        lista_archivos.sort(key=lambda x: x[1], reverse=True)
        msg = "📂 <b>CLIPS RECIENTES:</b>\n"
        for nombre, _ in lista_archivos[:5]:
            msg += f"• <code>{nombre}</code>\n"
        if not lista_archivos: return "📂 Carpeta vacía."
        return msg
    except Exception as e: 
        print(f"Error Clips: {e}")
        return "❌ Error al leer disco."

# ==========================================
# 4. MOTOR UI (CON GESTOR DE STICKERS)
# ==========================================

def enviar_o_editar(chat_id, msg_id, texto, teclado=None, foto=None):
    url = f"https://api.telegram.org/bot{TOKEN}/"
    if foto:
        requests.post(url+"sendPhoto", data={'chat_id': chat_id, 'caption': texto, 'parse_mode': 'HTML'}, files={'photo': foto})
        return
    payload = {"chat_id": chat_id, "text": texto, "parse_mode": "HTML"}
    if teclado: payload["reply_markup"] = json.dumps(teclado)
    if msg_id:
        payload["message_id"] = msg_id
        try: requests.post(url+"editMessageText", json=payload)
        except: pass
    else:
        requests.post(url+"sendMessage", json=payload)

def enviar_sticker(chat_id, sticker_id):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendSticker", data={'chat_id': chat_id, 'sticker': sticker_id})
    except: pass

def ack(cb_id, text, alert=False):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": text, "show_alert": alert})
    except: pass

# --- SERVICIOS ---
def servicio_heartbeat():
    print("💓 Heartbeat iniciado.")
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]; s.close()
            msg = f"💓 <b>CLAWDBOT ACTIVO</b>\nIP: {ip}\n{obtener_mensaje_estado(ip)}"
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
            time.sleep(43200)
        except: time.sleep(60)

def reporte_automatico_cierre():
    print("⏰ Reporte Nocturno iniciado.")
    enviado = False
    while True:
        try:
            ahora = datetime.now()
            if ahora.hour == 23 and ahora.minute == 59 and not enviado:
                rep = generar_reporte_diario()
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": f"🌙 <b>CIERRE</b>\n{rep}", "parse_mode": "HTML"})
                enviado = True; time.sleep(120)
            if ahora.hour == 0: enviado = False
            time.sleep(30)
        except: time.sleep(30)

# --- BUCLE PRINCIPAL ---
def listen_bot():
    last_id = 0
    print("💎 Clawdbot v5.9.8 (Final Stable) Activa.")
    
    TECLADO_PERSISTENTE = {
        "keyboard": [[{"text": "🎛 ABRIR PANEL"}]],
        "resize_keyboard": True,
        "is_persistent": True
    }

    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            res = requests.get(url, params={"offset": last_id+1, "timeout": 20}).json()
            for up in res.get("result", []):
                last_id = up["update_id"]
                chat_id = CHAT_ID

                if "callback_query" in up:
                    cb = up["callback_query"]; data = cb["data"]; mid = cb["message"]["message_id"]
                    cid = cb["id"]

                    if data == "menu_main":
                        head = obtener_mensaje_estado("Local")
                        enviar_o_editar(chat_id, mid, f"🎛 <b>CENTRAL DE MANDO</b>\n━━━━━━━━━━\n{head}", MENU_HOME)
                    elif data == "menu_reportes":
                        enviar_o_editar(chat_id, mid, "📊 <b>REPORTES</b>", MENU_REPORTES)
                    elif data == "menu_sistema":
                        enviar_o_editar(chat_id, mid, "⚙️ <b>SISTEMA</b>", MENU_SISTEMA)
                    elif data == "menu_clips":
                        ack(cid, "Abriendo menú...")
                        enviar_o_editar(chat_id, mid, "📂 <b>CLIPS</b>", MENU_CLIPS)
                    elif data == "menu_radares":
                        enviar_o_editar(chat_id, mid, "📡 <b>RADARES</b>", get_menu_radares())

                    elif data == "cmd_reporte":
                        ack(cid, "Generando...")
                        threading.Thread(target=lambda: enviar_o_editar(chat_id, mid, generar_reporte_diario(), MENU_REPORTES)).start()
                    elif data == "cmd_log":
                        ack(cid, "Leyendo Log...")
                        threading.Thread(target=lambda: enviar_o_editar(chat_id, mid, leer_log_db(), MENU_REPORTES)).start()
                    elif data == "cmd_salud":
                        ack(cid, "Escaneando...")
                        threading.Thread(target=lambda: enviar_o_editar(chat_id, mid, verificar_salud_red(), MENU_SISTEMA)).start()
                    elif data == "cmd_disco":
                        ack(cid, "Verificando disco...")
                        threading.Thread(target=lambda: enviar_o_editar(chat_id, mid, obtener_mensaje_estado("Local"), MENU_SISTEMA)).start()
                    elif data == "cmd_depurar":
                        ack(cid, "Limpiando...", alert=True)
                        threading.Thread(target=lambda: enviar_o_editar(chat_id, mid, depurar_disco_viejo(), MENU_SISTEMA)).start()
                    elif data == "cmd_ver_clips":
                        ack(cid, "Buscando en disco...")
                        def tarea_clips(cid_t, mid_t):
                            res = obtener_ultimos_clips()
                            enviar_o_editar(cid_t, mid_t, res, MENU_CLIPS)
                        threading.Thread(target=tarea_clips, args=(chat_id, mid)).start()
                    
                    elif data == "cmd_manual":
                        ack(cid, "Ayuda...")
                        # Intenta enviar el sticker del cohete
                        enviar_sticker(chat_id, STICKER_ROCKET)
                        ayuda = f"🛠 <b>MANUAL RÁPIDO</b>\n\n• Use el botón de abajo 'ABRIR PANEL'.\n• Escriba nombre del video para bajarlo.\n\n🔗 <a href='{URL_DASHBOARD}'>ACCESO WEB (GRAFANA)</a>"
                        enviar_o_editar(chat_id, mid, ayuda, MENU_SISTEMA)

                    elif data.startswith("iafoto_"):
                        ack(cid, "Procesando IA...")
                        def tarea_foto(rk):
                            raw = axis_snapshot(RADARES[rk]["ip"])
                            if raw:
                                proc, cap = procesar_captura_con_ia(raw, rk)
                                enviar_o_editar(chat_id, None, cap, None, proc)
                                enviar_o_editar(chat_id, None, "📡 ¿Otra acción?", get_menu_radares())
                        threading.Thread(target=tarea_foto, args=(data.split("_")[1],)).start()
                    elif data.startswith("vid_"):
                        ack(cid, "Grabando 15s...")
                        grabar_video_manual(RADARES[data.split("_")[1]]["ip"])
                    continue

                # --- 2. ZONA DE TEXTO Y COMANDOS ---
                msg = up.get("message", {}); txt = msg.get("text", "")

                # DETECCIÓN DE TU STICKER (¡NUEVO!)
                if "sticker" in msg:
                    sid = msg["sticker"]["file_id"]
                    # Te envía el ID al chat para que lo copies
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                  json={"chat_id": chat_id, "text": f"🆔 TU ID DE STICKER:\n<code>{sid}</code>", "parse_mode": "HTML"})

                if "/start" in txt or "ABRIR PANEL" in txt:
                    # Intenta enviar el sticker del cohete
                    enviar_sticker(chat_id, STICKER_ROCKET)
                    
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                  json={"chat_id": chat_id, "text": "🚀 Sistema Listo", "reply_markup": json.dumps(TECLADO_PERSISTENTE)})
                    head = obtener_mensaje_estado("Local")
                    enviar_o_editar(chat_id, None, f"🎛 <b>CENTRAL DE MANDO</b>\n━━━━━━━━━━\n{head}", MENU_HOME)

                elif ".mp4" in txt:
                    def subir_video(ruta_nombre, cid_t):
                        ruta = os.path.join(VIDEO_PATH, ruta_nombre)
                        if os.path.exists(ruta):
                            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": cid_t, "text": "📤 Subiendo..."})
                            with open(ruta, 'rb') as v: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendVideo", data={'chat_id': cid_t}, files={'video': v})
                    threading.Thread(target=subir_video, args=(txt.strip(), chat_id)).start()

        except Exception as e: 
            print(f"Error Loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=servicio_heartbeat, daemon=True).start()
    threading.Thread(target=reporte_automatico_cierre, daemon=True).start()
    listen_bot()