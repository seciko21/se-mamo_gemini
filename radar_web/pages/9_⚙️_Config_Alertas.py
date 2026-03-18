import streamlit as st
import sqlite3
import os
import sys

# ==========================================
# 🔐 AUTENTICACIÓN
# ==========================================
sys.path.append('..')
import auth
auth.init_session()

# ==========================================
# 🛑 CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Configuración de Alertas - LCC AI",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🔐 BOTÓN DE LOGIN
# ==========================================
auth.show_top_right_login()

# ==========================================
# 📋 SIDEBAR DE NAVEGACIÓN
# ==========================================
auth.show_sidebar_navigation()

# ==========================================
# 🎨 CSS MAESTRO
# ==========================================
st.markdown("""
    <style>
        .stApp {
            background-color: #0b0f19;
            background-image: radial-gradient(circle at 50% -20%, #1c2235 0%, #0b0f19 60%);
        }
        .block-container { padding-top: 2rem; max-width: 96%; }
        [data-testid="stSidebar"] { background-color: #0b0f19; border-right: 1px solid rgba(100, 149, 237, 0.05); }
        
        .config-card {
            background-color: #131722;
            border-radius: 16px;
            border: 1px solid rgba(100, 149, 237, 0.15);
            padding: 24px;
            margin-bottom: 20px;
        }
        
        .config-title {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 20px;
            color: #fff;
        }
        
        .config-subtitle {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #8ab4f8;
        }
        
        .radar-config {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            border: 1px solid rgba(100, 149, 237, 0.1);
            padding: 16px;
            margin-bottom: 12px;
        }
        
        .radar-name {
            font-size: 16px;
            font-weight: 600;
            color: #e8eaed;
            margin-bottom: 10px;
        }
        
        .stSlider > div[data-baseweb = "slider"] {
            margin-top: 8px;
        }
        
        .save-btn button {
            background: linear-gradient(135deg, #4285F4 0%, #9C27B0 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
        }
        
        .save-btn button:hover {
            background: linear-gradient(135deg, #5c9aff 0%, #b844d4 100%);
        }
        
        .success-msg {
            background: rgba(76, 175, 80, 0.15);
            border: 1px solid rgba(76, 175, 80, 0.3);
            border-radius: 8px;
            padding: 12px;
            color: #81c784;
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📁 RUTAS
# ==========================================
DB_PATH = '/app/data_folder/cola_mensajes.db'
if not os.path.exists(DB_PATH):
    DB_PATH = 'cola_mensajes.db'

# ==========================================
# 🧠 FUNCIONES DE BASE DE DATOS
# ==========================================
@st.cache_data(ttl=5)
def get_radares():
    """Obtiene la lista de radares disponibles"""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT nombre, ip, puerto, activo FROM radares_config ORDER BY nombre", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error al cargar radares: {e}")
        return pd.DataFrame()

def get_alertas_config():
    """Obtiene la configuración de alertas por radar"""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM alertas_config ORDER BY radar_nombre", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error al cargar configuración: {e}")
        return pd.DataFrame()

def save_alerta_config(radar_nombre, umbral_velocidad, umbral_exceso):
    """Guarda la configuración de alertas para un radar"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE alertas_config 
            SET umbral_velocidad = ?, umbral_exceso = ?, 
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE radar_nombre = ?
        """, (umbral_velocidad, umbral_exceso, radar_nombre))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# Importar pandas
import pandas as pd

# ==========================================
# 🎯 TÍTULO PRINCIPAL
# ==========================================
st.markdown("""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 30px;">
        <span style="font-size: 42px;">⚙️</span>
        <span style="background: linear-gradient(90deg, #4285F4, #E91E63, #9C27B0); 
              -webkit-background-clip: text; -webkit-text-fill-color: transparent;
              font-size: 36px; font-weight: 800;">Configuración de Alertas</span>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <p style="color: #9aa0a6; margin-bottom: 30px; font-size: 16px;">
        Configura los umbrales de velocidad para activar alertas por exceso de velocidad en cada radar.
        <br>Por ejemplo: Si estableces <strong>40 km/h</strong> para ROMANZA, cualquier vehículo que supere esa velocidad generará una alerta.
    </p>
""", unsafe_allow_html=True)

# ==========================================
# 📊 CARGAR DATOS
# ==========================================
radares_df = get_radares()
alertas_df = get_alertas_config()

if alertas_df.empty:
    st.error("No se encontró la tabla de configuración de alertas.")
    st.stop()

# ==========================================
# 🔧 FORMULARIO DE CONFIGURACIÓN
# ==========================================
st.markdown('<div class="config-card">', unsafe_allow_html=True)
st.markdown('<div class="config-title">🎚️ Umbrales por Radar</div>', unsafe_allow_html=True)

# Mensaje de éxito
if 'config_saved' in st.session_state and st.session_state.config_saved:
    st.markdown('<div class="success-msg">✅ Configuración guardada correctamente</div>', unsafe_allow_html=True)
    st.session_state.config_saved = False

# Crear formulario para cada radar
form_data = {}

col1, col2 = st.columns([2, 1])

with col1:
    # Selector de radar
    radar_seleccionado = st.selectbox(
        "Seleccionar Radar",
        options=alertas_df['radar_nombre'].tolist(),
        index=0
    )
    
    # Obtener configuración actual del radar seleccionado
    config_actual = alertas_df[alertas_df['radar_nombre'] == radar_seleccionado].iloc[0]
    
    st.markdown(f"""
        <div class="radar-config">
            <div class="radar-name">📍 {radar_seleccionado}</div>
    """, unsafe_allow_html=True)
    
    # Slider para umbral de velocidad
    umbral_vel = st.slider(
        "Velocidad mínima para alerta (km/h)",
        min_value=10,
        max_value=150,
        value=int(config_actual['umbral_velocidad']),
        step=5,
        key="umbral_vel"
    )
    
    # Slider para exceso permitido
    umbral_exc = st.slider(
        "Margen de exceso permitido (km/h)",
        min_value=0,
        max_value=30,
        value=int(config_actual['umbral_exceso']),
        step=5,
        key="umbral_exc"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="config-subtitle">📋 Valores Actuales</div>', unsafe_allow_html=True)
    
    # Mostrar valores actuales
    st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 20px; margin-bottom: 15px;">
            <div style="color: #9aa0a6; font-size: 14px;">Velocidad mínima</div>
            <div style="color: #ff8a80; font-size: 32px; font-weight: 700;">{config_actual['umbral_velocidad']} km/h</div>
        </div>
        
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 20px;">
            <div style="color: #9aa0a6; font-size: 14px;">Margen de exceso</div>
            <div style="color: #ffd54f; font-size: 32px; font-weight: 700;">+{config_actual['umbral_exceso']} km/h</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 💾 BOTÓN DE GUARDAR
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)

col_save1, col_save2, col_save3 = st.columns([1, 1, 2])

with col_save1:
    if st.button("💾 Guardar Configuración", use_container_width=True):
        if save_alerta_config(radar_seleccionado, umbral_vel, umbral_exc):
            st.session_state.config_saved = True
            st.rerun()

with col_save2:
    if st.button("🔄 Restablecer Valores", use_container_width=True):
        # Restaurar valores por defecto
        defaults = {
            'ROMANZA': 40,
            'RC50': 30,
            'RC21': 30,
            'FINESTRE': 50,
            'BAHIAS': 40,
            'NUEVO_RADAR': 50,
            'SIMULACION_TEST': 50
        }
        if radar_seleccionado in defaults:
            if save_alerta_config(radar_seleccionado, defaults[radar_seleccionado], 10):
                st.session_state.config_saved = True
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 📊 TABLA DE CONFIGURACIÓN ACTUAL
# ==========================================
st.markdown('<div class="config-card">', unsafe_allow_html=True)
st.markdown('<div class="config-title">📋 Configuración Actual de Todos los Radares</div>', unsafe_allow_html=True)

# Mostrar tabla de configuración
if not alertas_df.empty:
    st.dataframe(
        alertas_df[['radar_nombre', 'umbral_velocidad', 'umbral_exceso', 'fecha_actualizacion']].rename(columns={
            'radar_nombre': 'Radar',
            'umbral_velocidad': 'Umbral (km/h)',
            'umbral_exceso': 'Margen (km/h)',
            'fecha_actualizacion': 'Última Actualización'
        }),
        use_container_width=True,
        hide_index=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# ℹ️ INFORMACIÓN ADICIONAL
# ==========================================
st.markdown("""
    <div style="background: rgba(66, 133, 244, 0.1); border-radius: 12px; padding: 20px; margin-top: 20px;">
        <div style="color: #8ab4f8; font-size: 18px; font-weight: 600; margin-bottom: 10px;">💡 Cómo funciona:</div>
        <ul style="color: #9aa0a6; line-height: 1.8;">
            <li>El <strong>umbral de velocidad</strong> es la velocidad mínima que debe superar un vehículo para generar una alerta.</li>
            <li>El <strong>margen de exceso</strong> es un buffer adicional que se suma al umbral para considerar una infracción como "grave".</li>
            <li>Ejemplo: Si el umbral es 40 km/h y el margen es 10 km/h, una alerta se muestra a partir de 40 km/h, pero se marca como infracción grave a partir de 50 km/h.</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
