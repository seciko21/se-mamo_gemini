import streamlit as st
import os

# ==========================================
# 🛑 CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Campo de Estrellas | RADAR-WEB", 
    layout="wide", 
    page_icon="🌌", 
    initial_sidebar_state="collapsed"
)

# ==========================================
# ✨ CSS MAESTRO: GEMINI DARK + ESTRELLAS
# ==========================================
st.markdown("""
    <style>
        /* --- 1. FONDO --- */
        .stApp {
            background-color: #0b0f19;
            background-image: radial-gradient(circle at 50% -20%, #1c2235 0%, #0b0f19 60%);
        }
        .block-container { padding-top: 2rem; max-width: 96%; }

        /* --- 2. SIDEBAR --- */
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
        .gradient-title {
            background: linear-gradient(90deg, #4285F4, #E91E63, #9C27B0, #00BCD4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 48px;
            filter: drop-shadow(0 0 8px rgba(233, 30, 99, 0.4));
            margin: 0;
            display: inline;
        }
        
        .gradient-icon {
            font-size: 56px;
            filter: drop-shadow(0 0 12px rgba(66, 133, 244, 0.6));
            margin-right: 15px;
            vertical-align: middle;
        }
        
        .card-header {
            background: linear-gradient(90deg, #8ab4f8, #c084fc, #f5a5c0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 18px; font-weight: 700; margin-bottom: 20px;
        }

        /* --- 5. SCROLLBAR --- */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #0b0f19; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🖥️ HEADER
# ==========================================
st.markdown('''
    <div style="text-align: center; display: flex; align-items: center; justify-content: center;">
        <span class="gradient-icon">🌌</span>
        <span class="gradient-title">Campo de Estrellas</span>
    </div>
    ''' , unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 📖 DESCRIPCIÓN DEL SISTEMA
# ==========================================
with st.container():
    st.markdown('<div class="gemini-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">✨ Sistema de Radar LCC AI</div>', unsafe_allow_html=True)
    st.markdown("""
        <p style="color: #9aa0a6; font-size: 14px; line-height: 1.7;">
            Bienvenido al sistema de monitoreo inteligente de tráfico más avanzado. 
            Nuestra plataforma combina tecnología de punta con inteligencia artificial 
            para proporcionar una solución integral de detección y gestión de infracciones.
        </p>
        <p style="color: #9aa0a6; font-size: 14px; line-height: 1.7;">
            Con capacidades de análisis en tiempo real, visualización de datos avanzada 
            y gestión eficiente de evidencias, revolucionamos la forma en que se monitorea 
            el tráfico vial.
        </p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🎯 CARACTERÍSTICAS
# ==========================================
with st.container():
    st.markdown('<div class="gemini-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">🎯 Características Principales</div>', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown("""
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 36px; margin-bottom: 15px;">🎯</div>
                <div style="color: #fff; font-weight: 600; font-size: 16px; margin-bottom: 10px;">Detección Precisa</div>
                <div style="color: #9aa0a6; font-size: 13px;">Sistema de identificación de vehículos con alta precisión usando algoritmos de IA avanzados.</div>
            </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown("""
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 36px; margin-bottom: 15px;">⚡</div>
                <div style="color: #fff; font-weight: 600; font-size: 16px; margin-bottom: 10px;">Tiempo Real</div>
                <div style="color: #9aa0a6; font-size: 13px;">Procesamiento instantáneo de datos para monitoreo continuo sin retrasos.</div>
            </div>
        """, unsafe_allow_html=True)
    
    with c3:
        st.markdown("""
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 36px; margin-bottom: 15px;">📊</div>
                <div style="color: #fff; font-weight: 600; font-size: 16px; margin-bottom: 10px;">Análisis de Datos</div>
                <div style="color: #9aa0a6; font-size: 13px;">Estadísticas detalladas y reportes automatizados para toma de decisiones.</div>
            </div>
        """, unsafe_allow_html=True)
    
    with c4:
        st.markdown("""
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 36px; margin-bottom: 15px;">🎥</div>
                <div style="color: #fff; font-weight: 600; font-size: 16px; margin-bottom: 10px;">Gestión de Evidencias</div>
                <div style="color: #9aa0a6; font-size: 13px;">Almacenamiento seguro de videos e imágenes con soporte de búsqueda.</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 📈 ESTADÍSTICAS DEL SISTEMA
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

grad_blue = "background: linear-gradient(45deg, #4285F4, #00BCD4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"
grad_purple = "background: linear-gradient(45deg, #9C27B0, #E91E63); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"
grad_pink = "background: linear-gradient(45deg, #E91E63, #FF5722); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"

k1.markdown(f"""
    <div class="gemini-card" style="padding: 20px; text-align: center;">
        <div style="font-size: 11px; color: #8ab4f8; font-weight: bold; text-transform: uppercase;">🚗 Vehículos</div>
        <div style="{grad_blue}; font-size: 32px; font-weight: 800;">1,247</div>
        <div style="font-size: 11px; color: #5f6368;">Monitoreados</div>
    </div>
""", unsafe_allow_html=True)

k2.markdown(f"""
    <div class="gemini-card" style="padding: 20px; text-align: center;">
        <div style="font-size: 11px; color: #c084fc; font-weight: bold; text-transform: uppercase;">🚨 Infracciones</div>
        <div style="{grad_purple}; font-size: 32px; font-weight: 800;">89</div>
        <div style="font-size: 11px; color: #5f6368;">Detectadas</div>
    </div>
""", unsafe_allow_html=True)

k3.markdown(f"""
    <div class="gemini-card" style="padding: 20px; text-align: center;">
        <div style="font-size: 11px; color: #f5a5c0; font-weight: bold; text-transform: uppercase;">📡 Radares</div>
        <div style="{grad_pink}; font-size: 32px; font-weight: 800;">5</div>
        <div style="font-size: 11px; color: #5f6368;">Activos</div>
    </div>
""", unsafe_allow_html=True)

k4.markdown(f"""
    <div class="gemini-card" style="padding: 20px; text-align: center;">
        <div style="font-size: 11px; color: #81c995; font-weight: bold; text-transform: uppercase;">🔔 Alertas</div>
        <div style="{grad_blue}; font-size: 32px; font-weight: 800;">156</div>
        <div style="font-size: 11px; color: #5f6368;">Generadas</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 🌌 CAMPO DE ESTRELLAS (AL FINAL)
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)

# Obtener la ruta del archivo HTML
html_path = os.path.join(os.path.dirname(__file__), 'pagina_estrellas.html')

try:
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extraer solo la sección de estrellas del HTML
    import re
    estrellas_match = re.search(r'<!-- =========================================.*?estrellas-container -->', html_content, re.DOTALL)
    if estrellas_match:
        estrellas_html = estrellas_match.group(0)
        st.markdown(estrellas_html, unsafe_allow_html=True)
    else:
        # Si no se puede extraer, mostrar iframe
        st.components.v1.html(html_content, height=800, scrolling=True)
        
except FileNotFoundError:
    st.error("No se encontró el archivo pagina_estrellas.html")

# ==========================================
# ⚙️ FOOTER
# ==========================================
st.markdown("""
    <div class="footer-text">
        RADAR-WEB v2.5 | © 2026 LCC Analytics | Sistema de Monitoreo Inteligente
    </div>
""", unsafe_allow_html=True)
