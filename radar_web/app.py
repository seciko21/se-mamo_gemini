import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
from datetime import datetime, date, timedelta
import io
import time
import glob

# ==========================================
# CONFIGURACIÓN DE TIEMPO
# ==========================================
OFFSET_HORAS = -0

# RUTAS DE DATOS (Ajustadas al entorno Docker)
DB_PATH = '/app/data_folder/cola_mensajes.db'
CLIPS_DIR = "/app/clips/"
FOTOS_PATH = "/app/imagenes_multas/" 

USER_BOT_TELEGRAM = "Rocket_lcc_bot" 
LINK_GRUPO_ALERTAS = "https://t.me/+K3LKAHY-EF40ZGJh"

pd.set_option("styler.render.max_elements", 1000000)
st.set_page_config(page_title="Radar Dashboard Pro", layout="wide", page_icon="🏎️")

# --- LÓGICA DE BIENVENIDA ---
if "welcome_shown" not in st.session_state:
    st.toast("🚀 Sistema Radar: ONLINE", icon="🤖")
    st.balloons()
    st.session_state.welcome_shown = True

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

st.markdown("""
    <style> 
        .main { background-color: #0e1117; }
        .stMetric { 
            background-color: #161b22; 
            border-radius: 10px; padding: 15px; 
            border: 1px solid #30363d; border-left: 5px solid #00ff00; 
        }
        .time-box {
            text-align: right; color: #00ff00; font-family: 'Courier New', monospace;
            padding: 10px; border: 1px solid #333; border-radius: 5px; background: #1a1a1a;
        }
        .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #0088cc; color: white; font-weight: bold; }
        .css-16idsys p { font-size: 12px; text-align: center; color: #ccc; }
        img { border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- BANNER DE ESTADO ---
st.success(f"🛠️ **PROYECTO: RADAR v6.1** | Almacenamiento: **900GB** | Analítica: **Heatmap Activo**")

hora_local = datetime.now() + timedelta(hours=OFFSET_HORAS)

# --- HEADER ---
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.title("📊 Panel de Control - Radar Infracciones")
    st.caption(f"📡 radar.radar-lcc.site | Sincronización CST: {hora_local.strftime('%H:%M:%S')}")
with col_t2:
    st.markdown(f"""
        <div class="time-box">
            <small>SINCRO LOCAL (CST)</small><br>
            📅 {hora_local.strftime('%d/%m/%Y')}<br>
            🕒 {hora_local.strftime('%H:%M:%S')}
        </div>
    """, unsafe_allow_html=True)

# --- DATOS ---
@st.cache_data(ttl=15)
def get_data():
    try:
        if not os.path.exists(DB_PATH):
            return pd.DataFrame()
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT id, radar, velocidad, fecha, hora FROM historial ORDER BY id DESC", conn)
        conn.close()
        
        if df.empty:
            return df

        df['fecha_completa'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora'].astype(str))
        df['fecha_completa'] = df['fecha_completa'] + timedelta(hours=OFFSET_HORAS)
        
        return df
    except Exception as e:
        st.error(f"Error DB: {e}")
        return pd.DataFrame()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2343/2343277.png", width=100)
    st.header("🛠️ Estado del Sistema")
    
    if os.path.exists(CLIPS_DIR):
        st.success("📁 Disco 900GB: CONECTADO")
    else:
        st.error("📁 Disco 900GB: DESCONECTADO")

    st.divider()
    
    st.markdown("### 📡 Actividad en Vivo (15 min)")
    df_raw = get_data()
    
    if not df_raw.empty:
        tiempo_corte = hora_local - timedelta(minutes=15)
        df_logs = df_raw[df_raw['fecha_completa'] >= tiempo_corte].copy()
        
        if not df_logs.empty:
            for _, row in df_logs.head(8).iterrows():
                color = "#ff4b4b" if row['velocidad'] >= 60 else "#ffaa00" if row['velocidad'] >= 41 else "#00ff00"
                st.markdown(f"<div style='font-size:11px; color:{color}; font-family:monospace;'>● {row['fecha_completa'].strftime('%H:%M')} | {row['radar']} | {row['velocidad']} km/h</div>", unsafe_allow_html=True)
        else:
            st.info("Sin actividad reciente.")
    
    st.divider()
    st.markdown("### ✈️ Accesos Directos")
    st.link_button("🤖 Abrir Bot @Rocket_lcc_bot", f"https://t.me/{USER_BOT_TELEGRAM}", use_container_width=True)
    st.link_button("🚨 Grupo LCC-RADAR", LINK_GRUPO_ALERTAS, use_container_width=True)

# --- CUERPO PRINCIPAL ---
if not df_raw.empty:
    df = df_raw.copy()
    
    st.sidebar.header("🔎 Filtros")
    lista_radares = ["TODOS"] + sorted(df['radar'].unique().tolist())
    radar_sel = st.sidebar.selectbox("Seleccionar Radar", lista_radares)
    if radar_sel != "TODOS":
        df = df[df['radar'] == radar_sel]

    f_min, f_max = df['fecha_completa'].dt.date.min(), df['fecha_completa'].dt.date.max()
    rango = st.sidebar.date_input("Rango de Fechas", value=(max(f_min, f_max - timedelta(days=7)), f_max))
    
    if len(rango) == 2:
        df = df[(df['fecha_completa'].dt.date >= rango[0]) & (df['fecha_completa'].dt.date <= rango[1])]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Infracciones", f"{len(df):,}")
    m2.metric("Promedio Velocidad", f"{round(df['velocidad'].mean(), 1)} km/h")
    m3.metric("Récord Registrado", f"{df['velocidad'].max()} km/h")
    m4.metric("Infracciones Graves", len(df[df['velocidad'] >= 60]))

    # ==========================================
    # SECCIÓN: GALERÍA VISUAL
    # ==========================================
    st.divider()
    st.subheader("📸 Última Evidencia Capturada (Tiempo Real)")
    
    if os.path.exists(FOTOS_PATH):
        archivos_fotos = glob.glob(os.path.join(FOTOS_PATH, "*.jpg"))
        
        if archivos_fotos:
            ultimos_archivos = sorted(archivos_fotos, key=os.path.getmtime, reverse=True)[:4]
            cols_galeria = st.columns(4)
            
            for idx, archivo in enumerate(ultimos_archivos):
                with cols_galeria[idx]:
                    try:
                        nombre_archivo = os.path.basename(archivo)
                        base_limpia = nombre_archivo.lower().replace('.jpg', '').replace('.jpeg', '')
                        partes = base_limpia.split('_')
                        
                        if len(partes) >= 2:
                            radar_name = partes[0].upper()
                            velocidad_val = partes[1]
                            caption_txt = f"📍 {radar_name} | ⚡ {velocidad_val} km/h"
                        else:
                            caption_txt = nombre_archivo

                        st.image(archivo, caption=caption_txt, use_container_width=True)
                    except Exception as e:
                        st.error("Error img")
        else:
            st.info("☁️ Esperando primeras capturas en la carpeta...")
    else:
        st.warning(f"⚠️ Ruta no accesible: {FOTOS_PATH}")

    st.divider()

    col_chart1, col_chart2 = st.columns([1, 2])
    with col_chart1:
        st.subheader("🎯 Reparto por Radar")
        fig_pie = px.pie(df, names='radar', hole=0.4, template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.5))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        # ==========================================
        # NUEVO: MAPA DE CALOR SEMANAL (HEATMAP)
        # ==========================================
        st.subheader("🔥 Mapa de Calor (Día vs Hora)")
        
        try:
            # 1. Preparamos los datos
            df_heat = df.copy()
            dias_traduccion = {
                0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 
                4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
            }
            # Extraemos día numérico y nombre
            df_heat['dia_num'] = df_heat['fecha_completa'].dt.dayofweek
            df_heat['dia_nombre'] = df_heat['dia_num'].map(dias_traduccion)
            df_heat['hora_dia'] = df_heat['fecha_completa'].dt.hour
            
            # 2. Agrupamos para contar infracciones
            heatmap_data = df_heat.groupby(['dia_nombre', 'dia_num', 'hora_dia']).size().reset_index(name='conteo')
            
            # 3. Creamos el Heatmap con Plotly
            fig_heat = px.density_heatmap(
                heatmap_data, 
                x='hora_dia', 
                y='dia_nombre', 
                z='conteo', 
                nbinsx=24, # 24 horas
                color_continuous_scale='Inferno', # Colores estilo "fuego"
                template="plotly_dark"
            )
            
            # 4. Ajustes Visuales Finos
            fig_heat.update_layout(
                xaxis_title="Hora del Día (00:00 - 23:00)",
                yaxis_title=None,
                coloraxis_colorbar_title="Infracciones"
            )
            # Forzamos el orden correcto de Lunes a Domingo
            fig_heat.update_yaxes(categoryorder='array', categoryarray=['Domingo', 'Sábado', 'Viernes', 'Jueves', 'Miércoles', 'Martes', 'Lunes'])
            
            st.plotly_chart(fig_heat, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error generando heatmap: {e}")
        # ==========================================

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📋 Últimos Registros")
        df_display = df[['radar', 'velocidad', 'fecha_completa']].copy()
        df_display['fecha_completa'] = df_display['fecha_completa'].dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(df_display.head(100), use_container_width=True)
        
        output = io.BytesIO()
        df.to_excel(output, index=False)
        st.download_button("📥 Exportar Reporte Excel", output.getvalue(), "reporte_radar.xlsx")

    with c2:
        st.subheader("🎥 Evidencias de Video (900GB)")
        fecha_v = st.date_input("Día de grabación", value=hora_local.date())
        if os.path.exists(CLIPS_DIR):
            files = [f for f in os.listdir(CLIPS_DIR) if f.endswith(".mp4")]
            files_f = [f for f in files if date.fromtimestamp(os.path.getmtime(os.path.join(CLIPS_DIR, f))) == fecha_v]
            if files_f:
                sel = st.selectbox(f"Videos ({len(files_f)})", sorted(files_f, reverse=True))
                st.video(os.path.join(CLIPS_DIR, sel))
            else: st.warning("No hay videos para hoy.")
        else: st.error("Disco no accesible.")

else:
    st.warning("⚠️ Sin datos disponibles.")

time.sleep(30)
st.rerun()