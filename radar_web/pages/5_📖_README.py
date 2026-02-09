import streamlit as st
from datetime import datetime

# ==========================================
# 🛑 CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="README - LCC AI Radar", page_icon="📖", layout="wide")

# ==========================================
# ✨ CSS MAESTRO: ESTILO GEMINI DARK + SIDEBAR
# ==========================================
st.markdown("""
    <style>
        /* --- 1. FONDO GEMINI DARK --- */
        .stApp {
            background-color: #0b0f19;
            background-image: radial-gradient(circle at 50% -20%, #1c2235 0%, #0b0f19 60%);
        }
        .block-container { padding-top: 2rem; max-width: 96%; }

        /* --- 2. SIDEBAR PRO --- */
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

        /* --- 4. TÍTULOS CON GRADIENTE --- */
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
        
        .gradient-subtitle {
            background: linear-gradient(90deg, #4285F4, #00BCD4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 600;
            font-size: 24px;
        }

        /* --- 5. CÓDIGO --- */
        .code-block {
            background-color: #0d1117;
            border-radius: 12px;
            border: 1px solid rgba(100, 149, 237, 0.15);
            padding: 16px;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 14px;
            color: #c9d1d9;
            overflow-x: auto;
        }

        /* --- 6. LINKS --- */
        a {
            color: #4285F4;
            text-decoration: none;
        }
        a:hover {
            color: #E91E63;
            text-decoration: underline;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📖 CONTENIDO DEL README
# ==========================================

st.markdown('''
<div style="text-align: center; display: flex; align-items: center; justify-content: center;">
    <span class="gradient-icon">📖</span>
    <span class="gradient-title">LCC AI Radar Monitor</span>
</div>
''' , unsafe_allow_html=True)

st.write("")

# Columnas para contenido
col1, col2 = st.columns([2, 1])

with col1:
    # TARJETA: ACERCA DEL PROYECTO
    st.markdown("""
        <div class="gemini-card">
            <p class="gradient-subtitle">🤖 Acerca del Proyecto</p>
            <p style="color: #9aa0a6; line-height: 1.8;">
                <strong>LCC AI Radar Monitor</strong> es un sistema de monitoreo de radares de tráfico 
                con detección de infracciones Graves mediante inteligencia artificial. El sistema 
                captura vehículos excediendo límites de velocidad y genera evidencia visual automática.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # TARJETA: CARACTERÍSTICAS
    st.markdown("""
        <div class="gemini-card">
            <p class="gradient-subtitle">✨ Características Principales</p>
            <ul style="color: #9aa0a6; line-height: 2;">
                <li>📡 <strong>Monitoreo en tiempo real</strong> de múltiples radares TCP</li>
                <li>🚨 <strong>Detección automática</strong> de infracciones graves (>55 km/h)</li>
                <li>📸 <strong>Captura de evidencia</strong> con marcas de tiempo GPS</li>
                <li>📊 <strong>Estadísticas avanzadas</strong> con gráficos interactivos</li>
                <li>🔔 <strong>Sistema de alertas</strong> instantáneas</li>
                <li>🌙 <strong>Interfaz oscura</strong> estilo Gemini Pro</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # TARJETA: NAVEGACIÓN
    st.markdown("""
        <div class="gemini-card">
            <p class="gradient-subtitle">🧭 Navegación del Sistema</p>
            <table style="width: 100%; color: #9aa0a6; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid rgba(100, 149, 237, 0.1);">
                    <td style="padding: 12px;">🚨</td>
                    <td style="padding: 12px;"><strong>Infracciones Graves</strong></td>
                    <td style="padding: 12px;">Visualización de todas las infracciones detectadas</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(100, 149, 237, 0.1);">
                    <td style="padding: 12px;">🔔</td>
                    <td style="padding: 12px;"><strong>Alertas</strong></td>
                    <td style="padding: 12px;">Sistema de notificaciones en tiempo real</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(100, 149, 237, 0.1);">
                    <td style="padding: 12px;">🔍</td>
                    <td style="padding: 12px;"><strong>Búsqueda de Videos</strong></td>
                    <td style="padding: 12px;">Exploración y análisis de grabaciones</td>
                </tr>
                <tr>
                    <td style="padding: 12px;">📊</td>
                    <td style="padding: 12px;"><strong>Estadísticas</strong></td>
                    <td style="padding: 12px;">Dashboard con métricas y análisis</td>
                </tr>
            </table>
        </div>
    """, unsafe_allow_html=True)

with col2:
    # TARJETA: ESTADO DEL SISTEMA
    st.markdown("""
        <div class="gemini-card">
            <p class="gradient-subtitle">🟢 Estado del Sistema</p>
            <div style="display: flex; flex-direction: column; gap: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #9aa0a6;">Base de Datos</span>
                    <span style="color: #34a853; font-weight: 600;">● Conectado</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #9aa0a6;">Radar TCP</span>
                    <span style="color: #34a853; font-weight: 600;">● Activo</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #9aa0a6;">Monitor AI</span>
                    <span style="color: #34a853; font-weight: 600;">● Corriendo</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # TARJETA: VERSIÓN
    st.markdown(f"""
        <div class="gemini-card">
            <p class="gradient-subtitle">ℹ️ Información</p>
            <p style="color: #9aa0a6; font-size: 13px;">
                <strong>Versión:</strong> 2.1.0<br>
                <strong>Framework:</strong> Streamlit<br>
                <strong>Tema:</strong> Gemini Dark Pro<br>
                <strong>Actualizado:</strong> {datetime.now().strftime('%Y-%m-%d')}
            </p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 📝 FOOTER
# ==========================================
st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; color: #5f6368; font-size: 12px;">
        <p>🚀 LCC AI Radar Monitor | Desarrollado con ❤️ usando Streamlit</p>
        <p>© 2024-2025 | Todos los derechos reservados</p>
    </div>
""", unsafe_allow_html=True)
