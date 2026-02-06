import streamlit as st
import sqlite3
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# ==========================================
# 🛑 CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="Infracciones Graves", page_icon="🚨", layout="wide")

# RUTAS
DB_PATH = '/app/data_folder/cola_mensajes.db'
FOTOS_DIR = "/app/imagenes_multas/"
if not os.path.exists(DB_PATH): DB_PATH = 'cola_mensajes.db'

# ==========================================
# ✨ CSS MAESTRO: SIDEBAR PRO + EVIDENCIA
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
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            margin-bottom: 20px;
        }

        /* --- 4. TEXTOS Y GRADIENTES --- */
        .gradient-text-alert {
            background: linear-gradient(90deg, #ff9a9e, #fecfef, #f5576c);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;
        }
        
        /* --- 5. TARJETAS DE EVIDENCIA --- */
        .evidence-card {
            background-color: #1a1e29;
            border: 1px solid rgba(245, 87, 108, 0.3);
            border-radius: 16px;
            overflow: hidden;
            margin-bottom: 20px;
        }
        .evidence-header {
            background: rgba(245, 87, 108, 0.1);
            padding: 10px 15px;
            border-bottom: 1px solid rgba(245, 87, 108, 0.2);
            display: flex; justify-content: space-between; align-items: center;
        }
        .pill-tag {
            padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; display: inline-block;
        }
        
        /* --- 6. INPUTS --- */
        .stSelectbox > div > div, .stDateInput > div > div, .stTextInput > div > div > input {
            background-color: #1e2330 !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #e8eaed !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 LÓGICA
# ==========================================
@st.cache_data(ttl=15)
def cargar_graves(fecha_inicio, fecha_fin):
    if not os.path.exists(DB_PATH): return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        query = "SELECT * FROM historial WHERE velocidad >= 60 AND fecha BETWEEN ? AND ? ORDER BY fecha DESC, hora DESC"
        df = pd.read_sql_query(query, conn, params=(str(fecha_inicio), str(fecha_fin)))
        conn.close()
        if df.empty: return df
        if 'tipo' not in df.columns: df['tipo'] = "N/A"
        if 'placa' not in df.columns: df['placa'] = "---"
        return df
    except: return pd.DataFrame()

# ==========================================
# 🖥️ UI
# ==========================================
st.markdown("""
    <div style="font-size: 26px; font-weight: 600; color: white; margin-bottom: 20px;">
        <span style="font-size: 32px;">🚨</span> Monitor de <span class="gradient-text-alert">Infracciones Graves</span>
    </div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="gemini-card" style="padding: 15px;">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    hoy = datetime.now().date()
    f_inicio = c1.date_input("Desde", hoy - timedelta(days=7)) 
    f_fin = c2.date_input("Hasta", hoy)
    df = cargar_graves(f_inicio, f_fin)
    radares_list = ["Todos"] + sorted(list(df['radar'].unique())) if not df.empty else ["Todos"]
    tipos_list = ["Todos"] + sorted(list(df['tipo'].unique())) if not df.empty else ["Todos"]
    filtro_radar = c3.selectbox("Radar", radares_list)
    filtro_tipo = c4.selectbox("Vehículo", tipos_list)
    st.markdown('</div>', unsafe_allow_html=True)

df_show = df.copy()
if not df_show.empty:
    if filtro_radar != "Todos": df_show = df_show[df_show['radar'] == filtro_radar]
    if filtro_tipo != "Todos": df_show = df_show[df_show['tipo'] == filtro_tipo]

# KPIs
if not df_show.empty:
    k1, k2, k3, k4 = st.columns(4)
    grad_red = "background: linear-gradient(45deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 32px; font-weight: 800;"
    
    def alert_kpi(col, title, val, sub):
        col.markdown(f"""
            <div class="gemini-card" style="padding: 15px; border: 1px solid rgba(245, 87, 108, 0.2); text-align: center;">
                <div style="font-size: 11px; color: #ffb4ab; font-weight: bold; text-transform: uppercase;">{title}</div>
                <div style="{grad_red}">{val}</div>
                <div style="font-size: 11px; color: #aaa;">{sub}</div>
            </div>
        """, unsafe_allow_html=True)

    alert_kpi(k1, "TOTAL GRAVES", len(df_show), "Infracciones > 60km/h")
    alert_kpi(k2, "VELOCIDAD MAX", f"{df_show['velocidad'].max()} km/h", "Récord del periodo")
    radar_critico = df_show['radar'].mode()[0] if not df_show.empty else "N/A"
    alert_kpi(k3, "PUNTO CRÍTICO", radar_critico, "Mayor incidencia")
    with k4:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        csv = df_show.to_csv(index=False).encode('utf-8')
        st.download_button("📥 DESCARGAR REPORTE", csv, f"reporte_{hoy}.csv", "text/csv", width="stretch")

# Galería
st.markdown("<br>", unsafe_allow_html=True)
if df_show.empty:
    st.info("✅ No se encontraron infracciones.")
else:
    cols = st.columns(3)
    for idx, row in df_show.reset_index().iterrows():
        with cols[idx % 3]:
            placa = row.get('placa', '---')
            placa_html = f'<span class="pill-tag" style="background:rgba(129, 201, 149, 0.2); color:#81c995;">🆔 {placa}</span>'
            st.markdown(f"""
                <div class="evidence-card">
                    <div class="evidence-header">
                        <span style="color:#ffb4ab; font-weight:bold; font-size:18px;">⚡ {row['velocidad']} km/h</span>
                        <span style="color:#aaa; font-size:12px;">{row['hora']}</span>
                    </div>
                    <div style="padding:15px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                            <span style="color:#e8eaed; font-weight:500;">📍 {row['radar']}</span>
                            {placa_html}
                        </div>
                        <div style="color:#9aa0a6; font-size:12px; margin-bottom:10px;">📦 Tipo: {row['tipo']}</div>
                    </div>
            """, unsafe_allow_html=True)
            foto = row.get('foto')
            if foto and os.path.exists(os.path.join(FOTOS_DIR, foto)):
                st.image(os.path.join(FOTOS_DIR, foto), width="stretch")
            else:
                st.markdown("<div style='height:150px; background:#111;'></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

time.sleep(30)
st.rerun()