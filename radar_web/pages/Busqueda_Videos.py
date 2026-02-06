import streamlit as st
import pandas as pd
import sqlite3
import os
import glob
from datetime import datetime, timedelta, date

# ==========================================
# 🛑 CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="Video Evidence Search", layout="wide", page_icon="🎥")

# RUTAS
DB_PATH = '/app/data_folder/cola_mensajes.db'
if not os.path.exists(DB_PATH): DB_PATH = 'cola_mensajes.db'
CLIPS_DIR = "/app/clips/"

# ==========================================
# ✨ CSS MAESTRO: SIDEBAR PRO + SMART HEADERS
# ==========================================
st.markdown("""
    <style>
        /* --- 1. FONDO --- */
        .stApp {
            background-color: #0b0f19;
            background-image: radial-gradient(circle at 50% -20%, #1c2235 0%, #0b0f19 60%);
        }
        .block-container { padding-top: 2rem; max-width: 96%; }

        /* --- 2. SIDEBAR (MENÚ LATERAL) --- */
        [data-testid="stSidebar"] {
            background-color: #0b0f19;
            border-right: 1px solid rgba(100, 149, 237, 0.05);
        }
        div[data-testid="stSidebarNav"]::before {
            content: "PANEL DE CONTROL";
            margin-left: 20px; margin-top: 20px; margin-bottom: 10px;
            font-size: 10px; font-weight: 700; color: #5f6368; letter-spacing: 1px;
            display: block;
        }
        div[data-testid="stSidebarNav"] a {
            background-color: transparent;
            color: #9aa0a6;
            border-radius: 12px;
            margin: 5px 10px; padding: 10px 15px;
            transition: all 0.3s ease;
            border: 1px solid transparent;
        }
        div[data-testid="stSidebarNav"] a:hover {
            background-color: rgba(255, 255, 255, 0.03);
            color: #e8eaed;
            transform: translateX(3px);
        }
        div[data-testid="stSidebarNav"] a[aria-current="page"] {
            background: linear-gradient(90deg, rgba(66, 133, 244, 0.15), rgba(233, 30, 99, 0.15));
            border: 1px solid rgba(138, 180, 248, 0.2);
            color: #fff;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        /* --- 3. TARJETAS GEMINI --- */
        .gemini-card {
            background-color: #131722;
            border-radius: 24px;
            border: 1px solid rgba(100, 149, 237, 0.08);
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            margin-bottom: 20px;
        }

        /* --- 4. SMART HEADERS --- */
        .smart-header {
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 12px; margin-bottom: 15px;
        }
        .header-title { color: #e8eaed; font-size: 16px; font-weight: 600; }
        .header-badge {
            background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
            color: #9aa0a6; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 500;
        }
        .badge-highlight { background: rgba(66, 133, 244, 0.1); border-color: rgba(66, 133, 244, 0.3); color: #8ab4f8; }

        /* --- 5. REPRODUCTOR --- */
        .video-wrapper {
            background: #000; border-radius: 16px; border: 1px solid #333; padding: 5px; overflow: hidden;
        }
        
        /* --- 6. INPUTS --- */
        .stSelectbox > div > div, .stDateInput > div > div, .stTextInput > div > div > input {
            background-color: #1e2330 !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #e8eaed !important;
        }
        
        .gradient-text-logo {
            background: linear-gradient(90deg, #8ab4f8, #f5a5c0, #e8eaed);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 LÓGICA
# ==========================================
@st.cache_data(ttl=30)
def cargar_infracciones(min_vel, fecha_in, fecha_out, radar_filter):
    try:
        if not os.path.exists(DB_PATH): return pd.DataFrame()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        query = f"SELECT * FROM historial WHERE velocidad >= {min_vel} AND fecha BETWEEN '{fecha_in}' AND '{fecha_out}' ORDER BY fecha DESC, hora DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        if df.empty: return df
        if radar_filter != "TODOS": df = df[df['radar'] == radar_filter]
        if 'tipo' not in df.columns: df['tipo'] = "N/A"
        if 'placa' not in df.columns: df['placa'] = "---"
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def obtener_videos_disponibles(fecha_seleccionada):
    if not os.path.exists(CLIPS_DIR): return []
    fecha_str = fecha_seleccionada.strftime('%Y-%m-%d')
    files = glob.glob(os.path.join(CLIPS_DIR, f"*{fecha_str}*.mp4"))
    if files: return sorted([os.path.basename(v) for v in files], reverse=True)
    all_files = glob.glob(os.path.join(CLIPS_DIR, "*.mp4"))
    return sorted([os.path.basename(v) for v in all_files if date.fromtimestamp(os.path.getmtime(v)) == fecha_seleccionada], reverse=True)

# ==========================================
# 🖥️ UI
# ==========================================
st.markdown("""
    <div style="font-size: 26px; font-weight: 600; color: white; margin-bottom: 20px;">
        <span style="font-size: 32px;">🎥</span> Video <span class="gradient-text-logo">Forensics AI</span>
    </div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="gemini-card">', unsafe_allow_html=True)
    # Header plano
    st.markdown('<div class="smart-header"><div class="header-title">🔍 Parámetros de Búsqueda</div><div class="header-badge badge-highlight"><span>⚡ Sistema Sincronizado</span></div></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1: fecha_sel = st.date_input("Fecha del Evento", datetime.now())
    with c2:
        try:
            conn = sqlite3.connect(DB_PATH)
            df_rad = pd.read_sql("SELECT DISTINCT radar FROM historial", conn)
            radares = ["TODOS"] + sorted(df_rad['radar'].tolist())
            conn.close()
        except: radares = ["TODOS"]
        radar_sel = st.selectbox("Ubicación", radares)
    with c3: velocidad_min = st.slider("Filtro Velocidad Mínima", 0, 150, 40)
    st.markdown('</div>', unsafe_allow_html=True)

df_events = cargar_infracciones(velocidad_min, fecha_sel, fecha_sel, radar_sel)
videos = obtener_videos_disponibles(fecha_sel)

col_db, col_vid = st.columns([4, 3])

with col_db:
    st.markdown('<div class="gemini-card" style="height: 100%;">', unsafe_allow_html=True)
    if not df_events.empty:
        badges = f'<div style="display:flex; gap:10px;"><div class="header-badge">📂 {len(df_events)} Eventos</div><div class="header-badge badge-highlight">🔥 Max: {df_events["velocidad"].max()} km/h</div></div>'
    else: badges = '<div class="header-badge">⚠️ Sin Datos</div>'
    
    st.markdown(f'<div class="smart-header"><div class="header-title">⚡ Timeline de Eventos</div>{badges}</div>', unsafe_allow_html=True)
    if not df_events.empty:
        st.dataframe(df_events[['hora', 'velocidad', 'radar', 'tipo', 'placa']], width="stretch", height=450,
                     column_config={"velocidad": st.column_config.NumberColumn("Velocidad", format="%d km/h")})
    else: st.info(f"No hay registros superiores a {velocidad_min} km/h.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_vid:
    st.markdown('<div class="gemini-card" style="height: 100%;">', unsafe_allow_html=True)
    video_sel = st.selectbox("Seleccionar Archivo", videos) if videos else None
    status = '<div class="header-badge badge-highlight">Online</div>' if video_sel else '<div class="header-badge">Offline</div>'
    st.markdown(f'<div class="smart-header" style="margin-top:10px;"><div class="header-title">🎥 Visor</div>{status}</div>', unsafe_allow_html=True)
    
    if video_sel:
        ruta = os.path.join(CLIPS_DIR, video_sel)
        if os.path.exists(ruta):
            st.markdown('<div class="video-wrapper">', unsafe_allow_html=True)
            st.video(ruta)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            with open(ruta, "rb") as f:
                st.download_button("💾 DESCARGAR EVIDENCIA", f, video_sel, "video/mp4", width="stretch")
        else: st.error("Archivo no encontrado en disco.")
    else: st.warning("No hay videos disponibles.")
    st.markdown('</div>', unsafe_allow_html=True)