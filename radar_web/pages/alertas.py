import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
from datetime import datetime, date, timedelta
import time

# ==========================================
# 🛑 CONFIGURACIÓN DEL SISTEMA
# ==========================================
st.set_page_config(
    page_title="Monitor de Alertas - LCC AI", 
    layout="wide", 
    page_icon="🚨", 
    initial_sidebar_state="expanded"
)

OFFSET_HORAS = 0

# RUTAS
DB_PATH = '/app/data_folder/cola_mensajes.db'
if not os.path.exists(DB_PATH): DB_PATH = 'cola_mensajes.db'
FOTOS_PATH = "/app/imagenes_multas/" 

# ==========================================
# ✨ CSS MAESTRO (Duplicado de Infracciones Graves)
# ==========================================
st.markdown("""
    <style>
        .stApp {
            background-color: #0b0f19;
            background-image: radial-gradient(circle at 50% -20%, #1c2235 0%, #0b0f19 60%);
        }
        .block-container { padding-top: 2rem; max-width: 96%; }
        [data-testid="stSidebar"] { background-color: #0b0f19; border-right: 1px solid rgba(100, 149, 237, 0.05); }
        
        .gemini-card {
            background-color: #131722;
            border-radius: 24px;
            border: 1px solid rgba(100, 149, 237, 0.08);
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }

        .alert-header {
            background: linear-gradient(90deg, #ff5252, #f5a5c0, #e8eaed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 32px;
        }

        .kpi-val { font-size: 38px; font-weight: 700; color: #fff; letter-spacing: -1px; }
        .kpi-sub { font-size: 12px; color: #9aa0a6; margin-top: 6px; }

        /* Estilo para las tarjetas de imagen */
        .infraction-card {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 15px;
            border: 1px solid rgba(255, 82, 82, 0.2);
            padding: 10px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 MOTOR DE DATOS (Filtrado Alertas > 55 km/h)
# ==========================================
@st.cache_data(ttl=10)
def get_alert_data():
    try:
        if not os.path.exists(DB_PATH): return pd.DataFrame()
        conn = sqlite3.connect(DB_PATH)
        # Filtramos solo alertas mayores a 55 km/h
        df = pd.read_sql_query("SELECT * FROM historial WHERE velocidad > 55 ORDER BY id DESC LIMIT 500", conn)
        conn.close()
        
        if df.empty: return df
        
        df['fecha_completa'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora'].astype(str))
        df['fecha_completa'] = df['fecha_completa'] + timedelta(hours=OFFSET_HORAS)
        return df
    except: return pd.DataFrame()

df_raw = get_alert_data()

# ==========================================
# 🖥️ HEADER Y FILTROS
# ==========================================
st.markdown('<div class="alert-header">🚨 Monitor de Alertas Activas</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if not df_raw.empty:
    df = df_raw.copy()
    
    # Filtros rápidos
    c1, c2, c3 = st.columns(3)
    radar_sel = c1.selectbox("📍 Ubicación", ["TODOS"] + sorted(df['radar'].unique().tolist()))
    f_min, f_max = df['fecha_completa'].dt.date.min(), df['fecha_completa'].dt.date.max()
    rango = c3.date_input("Periodo", (max(f_min, f_max - timedelta(days=2)), f_max))

    if radar_sel != "TODOS": df = df[df['radar'] == radar_sel]
    if len(rango) == 2: df = df[(df['fecha_completa'].dt.date >= rango[0]) & (df['fecha_completa'].dt.date <= rango[1])]

    # KPIs de Alertas
    k1, k2, k3 = st.columns(3)
    k1.metric("Alertas Totales", len(df))
    k1.markdown('<div class="kpi-sub">Eventos > 50 km/h</div>', unsafe_allow_html=True)
    
    k2.metric("Velocidad Máxima", f"{df['velocidad'].max()} km/h")
    k3.metric("Radar Crítico", df['radar'].mode()[0] if not df.empty else "N/A")

    st.markdown("---")

    # ==========================================
    # 📸 GALERÍA DE IMÁGENES (ESTILO INFRACCIONES)
    # ==========================================
    # Generamos la cuadrícula de 3 columnas
    cols = st.columns(3)
    for idx, row in df.head(48).iterrows():
        with cols[idx % 3]:
            st.markdown(f'''
                <div class="infraction-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255, 82, 82, 0.15); padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                        <span style="color: #ff8a80; font-weight: bold; font-size: 20px;">⚡ {row['velocidad']} km/h</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

            # --- CORRECCIÓN DEL ERROR DE RUTA (JOIN) ---
            foto_nombre = row.get('foto')
            if foto_nombre and isinstance(foto_nombre, str):
                foto_full_path = os.path.join(FOTOS_PATH, foto_nombre)
                if os.path.exists(foto_full_path):
                    st.image(foto_full_path, use_container_width='stretch')
                else:
                    st.warning("Imagen no encontrada en disco")
            else:
                st.info("No hay evidencia fotográfica")

            st.markdown(f'''
                <div style="padding: 10px; background: rgba(0,0,0,0.2); border-radius: 10px;">
                    <div style="color: #ff8a80; font-size: 13px; font-weight: bold;">📍 {row['radar']}</div>
                    <div style="color: white; font-size: 14px; margin: 5px 0;"><b>Placa:</b> {row.get('placa', '---')}</div>
                    <div style="color: #9aa0a6; font-size: 11px;">📅 {row['fecha']} | 🕒 {row['hora']}</div>
                </div>
                <div style="margin-bottom: 30px;"></div>
            ''', unsafe_allow_html=True)

    # ==========================================
    # 📊 ESTADÍSTICA MENSUAL (Agregado al final)
    # ==========================================
    st.markdown('<div class="gemini-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">📅 Evolución de Alertas por Mes</div>', unsafe_allow_html=True)
    
    df['Mes'] = df['fecha_completa'].dt.strftime('%Y-%m')
    df_mes = df.groupby('Mes').agg(Total=('id', 'count'), Max_Vel=('velocidad', 'max')).reset_index()
    
    fig_mes = px.bar(df_mes, x='Mes', y='Total', color='Total', color_continuous_scale='Reds', template='plotly_dark')
    fig_mes.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_mes, use_container_width='stretch')
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Esperando alertas... No se registran excesos de velocidad en el periodo seleccionado.")

time.sleep(30)
st.rerun()