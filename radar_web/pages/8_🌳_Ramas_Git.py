import streamlit as st
import sys

# ==========================================
# 🔐 AUTENTICACIÓN (Página privada - requiere login)
# ==========================================
sys.path.append('..')
import auth
auth.init_session()

if not auth.is_authenticated():
    auth.show_login_form()
    st.stop()

# ==========================================
# 🛑 CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="Ramas Git - LCC AI Radar", page_icon="🌳", layout="wide")

# ==========================================
# 🔐 BOTÓN DE LOGIN - ESQUINA SUPERIOR DERECHA
# ==========================================
auth.show_top_right_login()

# ==========================================
# 📋 SIDEBAR DE NAVEGACIÓN
# ==========================================
auth.show_sidebar_navigation()

# ==========================================
# ✨ CSS MAESTRO: ESTILO GEMINI DARK
# ==========================================
st.markdown("""
    <style>
        /* --- 1. FONDO GEMINI DARK --- */
        .stApp {
            background-color: #0b0f19;
            background-image: radial-gradient(circle at 50% -20%, #1c2235 0%, #0b0f19 60%);
        }
        .block-container { padding-top: 2rem; max-width: 96%; }

        /* --- TÍTULOS --- */
        h1 {
            background: linear-gradient(90deg, #4285F4, #9C27B0, #E91E63);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        h2 { color: #8ab4f8; }
        h3 { color: #8ab4f8; }

        /* --- TARJETAS DE RAMAS --- */
        .branch-card {
            background: linear-gradient(145deg, #1e2330, #161b25);
            padding: 20px;
            border-radius: 16px;
            border-left: 4px solid;
            margin-bottom: 15px;
            transition: transform 0.2s;
        }

        .branch-card:hover {
            transform: translateY(-3px);
        }

        .branch-card.main { border-color: #4285F4; }
        .branch-card.production { border-color: #4ade80; }
        .branch-card.feature { border-color: #9C27B0; }
        .branch-card.dev { border-color: #f59e0b; }
        .branch-card.pruebas { border-color: #ef4444; }

        .branch-name {
            font-weight: bold;
            font-size: 1.1em;
            color: #fff;
            margin-bottom: 5px;
        }

        .branch-type {
            font-size: 0.8em;
            color: #9aa0a6;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* --- TIMELINE --- */
        .timeline {
            position: relative;
            padding-left: 30px;
            border-left: 2px solid #4285F4;
            margin-left: 10px;
        }

        .commit {
            position: relative;
            padding: 15px;
            margin-bottom: 15px;
            background: #1e2330;
            border-radius: 12px;
            border: 1px solid rgba(100, 149, 237, 0.1);
            margin-left: 10px;
        }

        .commit::before {
            content: '';
            position: absolute;
            left: -24px;
            top: 20px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4285F4;
            border: 2px solid #0b0f19;
        }

        .commit:first-child::before {
            background: #4ade80;
            box-shadow: 0 0 10px #4ade80;
        }

        .commit-hash {
            font-family: 'Courier New', monospace;
            color: #8ab4f8;
            font-size: 0.85em;
        }

        .commit-message { color: #e8eaed; margin: 8px 0; }
        .commit-date { color: #9aa0a6; font-size: 0.85em; }

        /* --- STATS --- */
        .stat-box {
            background: linear-gradient(145deg, #1e2330, #161b25);
            padding: 25px;
            border-radius: 16px;
            text-align: center;
            border: 1px solid rgba(100, 149, 237, 0.1);
        }

        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(90deg, #4285F4, #9C27B0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stat-label { color: #9aa0a6; font-size: 0.9em; margin-top: 5px; }

        /* --- TABLA --- */
        .components-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        .components-table th,
        .components-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(100, 149, 237, 0.1);
        }

        .components-table th { color: #8ab4f8; font-weight: 600; }
        .components-table tr:hover { background: rgba(100, 149, 237, 0.05); }

        .tag {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 10px;
            font-size: 0.75em;
            font-weight: bold;
        }

        .tag-main { background: #4285F4; color: white; }
        .tag-prod { background: #4ade80; color: #0b0f19; }
        .tag-feature { background: #9C27B0; color: white; }
        .tag-dev { background: #f59e0b; color: #0b0f19; }
        .tag-test { background: #ef4444; color: white; }

        /* --- STATUS --- */
        .status-badge {
            display: inline-block;
            background: linear-gradient(135deg, #1a472a, #2d5a3d);
            color: #4ade80;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            border: 1px solid #4ade80;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📌 TÍTULO PRINCIPAL
# ==========================================
st.markdown("""
    <div style="text-align: center; padding: 30px 0;">
        <h1 style="font-size: 2.5em;">🌳 Ramas Git y Estado del Proyecto</h1>
        <p style="color: #9aa0a6; font-size: 1.2em;">SE-MAMO-GEMINI - Sistema de Radar LCC AI</p>
        <div class="status-badge">✓ Repositorio Activo</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 📊 ESTADÍSTICAS
# ==========================================
st.markdown("### 📊 Estadísticas del Repositorio")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
        <div class="stat-box">
            <div class="stat-number">12</div>
            <div class="stat-label">Ramas Totales</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div class="stat-box">
            <div class="stat-number">3</div>
            <div class="stat-label">Ramas Remotas</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
        <div class="stat-box">
            <div class="stat-number">9</div>
            <div class="stat-label">Ramas Locales</div>
        </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("""
        <div class="stat-box">
            <div class="stat-number">20</div>
            <div class="stat-label">Últimos Commits</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 🌳 RAMAS DEL REPOSITORIO
# ==========================================
st.markdown("### 📂 Ramas del Repositorio")

# Rama Production
st.markdown("""
    <div class="branch-card production">
        <div class="branch-name">🌟 production</div>
        <div class="branch-type">Rama Principal de Producción (HEAD)</div>
    </div>
""", unsafe_allow_html=True)

# Rama Main
st.markdown("""
    <div class="branch-card main">
        <div class="branch-name">📋 main</div>
        <div class="branch-type">Rama Principal</div>
    </div>
""", unsafe_allow_html=True)

# Ramas de desarrollo
col_dev1, col_dev2 = st.columns(2)
with col_dev1:
    st.markdown("""
        <div class="branch-card dev">
            <div class="branch-name">🛠 dev-claudbot-v5.7</div>
            <div class="branch-type">Desarrollo</div>
        </div>
    """, unsafe_allow_html=True)
with col_dev2:
    st.markdown("""
        <div class="branch-card feature">
            <div class="branch-name">✨ feature-clawdbot</div>
            <div class="branch-type">Feature</div>
        </div>
    """, unsafe_allow_html=True)

# Features
st.markdown("""
    <div class="branch-card feature">
        <div class="branch-name">✨ feature/galeria-visual</div>
        <div class="branch-type">Feature - Galería Visual</div>
    </div>
    <div class="branch-card feature">
        <div class="branch-name">✨ feature/reorder-pages</div>
        <div class="branch-type">Feature - Reordenar Páginas</div>
    </div>
""", unsafe_allow_html=True)

# Ramas de producción
col_prod1, col_prod2 = st.columns(2)
with col_prod1:
    st.markdown("""
        <div class="branch-card production">
            <div class="branch-name">🚀 produccion_v6.2</div>
            <div class="branch-type">Producción</div>
        </div>
    """, unsafe_allow_html=True)
with col_prod2:
    st.markdown("""
        <div class="branch-card production">
            <div class="branch-name">🚀 produccion_060226_1840</div>
            <div class="branch-type">Producción</div>
        </div>
    """, unsafe_allow_html=True)

# Ramas de pruebas
st.markdown("""
    <div class="branch-card pruebas">
        <div class="branch-name">🧪 pruebas</div>
        <div class="branch-type">Pruebas</div>
    </div>
    <div class="branch-card pruebas">
        <div class="branch-name">🧪 pruebas-nuevas</div>
        <div class="branch-type">Pruebas</div>
    </div>
""", unsafe_allow_html=True)

# Ramas remotas
st.markdown("""
    <div style="margin-top: 20px; padding: 15px; background: rgba(100, 149, 237, 0.1); border-radius: 12px;">
        <p style="color: #9aa0a6; margin-bottom: 10px;"><strong>☁️ Ramas Remotas (origin/*):</strong></p>
        <p style="color: #8ab4f8;">origin/feature/galeria-visual • origin/feature/reorder-pages • origin/main • origin/produccion_060226_1840 • origin/pruebas-nuevas</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 📊 ESTADO DEL PROYECTO
# ==========================================
st.markdown("### 📊 Estado Actual del Proyecto")

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    st.markdown("""
        <div class="stat-box">
            <div style="font-size: 2em; margin-bottom: 10px;">🎯</div>
            <div style="color: #8ab4f8; font-size: 0.9em;">Rama Actual</div>
            <div style="color: #4ade80; font-weight: bold; font-size: 1.2em;">production</div>
        </div>
    """, unsafe_allow_html=True)
with col_s2:
    st.markdown("""
        <div class="stat-box">
            <div style="font-size: 2em; margin-bottom: 10px;">☁️</div>
            <div style="color: #8ab4f8; font-size: 0.9em;">Remoto</div>
            <div style="color: #fff; font-weight: bold; font-size: 1.2em;">origin</div>
        </div>
    """, unsafe_allow_html=True)
with col_s3:
    st.markdown("""
        <div class="stat-box">
            <div style="font-size: 2em; margin-bottom: 10px;">📦</div>
            <div style="color: #8ab4f8; font-size: 0.9em;">Versión</div>
            <div style="color: #fff; font-weight: bold; font-size: 1.2em;">v6.2</div>
        </div>
    """, unsafe_allow_html=True)
with col_s4:
    st.markdown("""
        <div class="stat-box">
            <div style="font-size: 2em; margin-bottom: 10px;">🐳</div>
            <div style="color: #8ab4f8; font-size: 0.9em;">Contenedores</div>
            <div style="color: #fff; font-weight: bold; font-size: 1.2em;">4</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 📜 HISTORIAL DE COMMITS
# ==========================================
st.markdown("### 📜 Historial de Commits Recientes")

commits = [
    ("b64544b", "Actualización de archivos radar_web", "HEAD • production"),
    ("d0f937e", "feat: Agregar sistema de autenticación a web", "Autenticación segura"),
    ("e382f74", "feat: Agregar gestion de radares en bot Telegram + optimizacion rendimiento", "Gestión de radares"),
    ("03dfc86", "fix(radar): Corrige parsing TCP para radar Bahías", "Corrección de bugs"),
    ("cbb65af", "feat: aplicar estilo de título con gradiente del README a todas las páginas", "UI/UX"),
    ("00bdfc8", "feat: reorder pages - change page order", "Reordenar páginas"),
    ("6840b32", "Produccion 06/02/26 18:40 hrs - Sincronizacion con radar_tcp_reader.py", "Release Production"),
    ("a8e4e96", "STABLE v6.0: Dashboard Visual + Docker Fixes + Warnings Removed", "Release estable"),
    ("4d41be4", "RELEASE v5.7.2: Video Instantáneo 30s, IA en Bot y Reportes SQL Corregidos", "Release mayor"),
]

for i, (hash_msg, message, date) in enumerate(commits):
    is_first = i == 0
    st.markdown(f"""
        <div class="commit" style="{'border-left: 3px solid #4ade80;' if is_first else ''}">
            <div class="commit-hash">{hash_msg}</div>
            <div class="commit-message">{message}</div>
            <div class="commit-date">{date}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 🧩 COMPONENTES DEL SISTEMA
# ==========================================
st.markdown("### 🧩 Componentes del Sistema")

st.markdown("""
<table class="components-table">
    <thead>
        <tr>
            <th>Componente</th>
            <th>Ubicación</th>
            <th>Descripción</th>
            <th>Tipo</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>radar_proyecto</strong></td>
            <td>/root/se-mamo_gemini/radar_proyecto/</td>
            <td>Monitor + Bot Telegram</td>
            <td><span class="tag tag-prod">Backend</span></td>
        </tr>
        <tr>
            <td><strong>radar_web</strong></td>
            <td>/root/se-mamo_gemini/radar_web/</td>
            <td>Dashboard Streamlit</td>
            <td><span class="tag tag-main">Frontend</span></td>
        </tr>
        <tr>
            <td><strong>docker-compose.yml</strong></td>
            <td>/root/se-mamo_gemini/</td>
            <td>Orquestación de servicios</td>
            <td><span class="tag tag-dev">Infra</span></td>
        </tr>
        <tr>
            <td><strong>MONITOR</strong></td>
            <td>Docker: radar_monitor</td>
            <td>Captura TCP radares + OCR</td>
            <td><span class="tag tag-prod">Servicio</span></td>
        </tr>
        <tr>
            <td><strong>BOT</strong></td>
            <td>Docker: radar_bot</td>
            <td>Comandos Telegram</td>
            <td><span class="tag tag-prod">Servicio</span></td>
        </tr>
        <tr>
            <td><strong>TÚNEL</strong></td>
            <td>Docker: radar_tunel_fijo</td>
            <td>Cloudflare Zero Trust</td>
            <td><span class="tag tag-dev">Infra</span></td>
        </tr>
        <tr>
            <td><strong>DASHBOARD</strong></td>
            <td>Docker: radar_dashboard</td>
            <td>Web Streamlit</td>
            <td><span class="tag tag-prod">Servicio</span></td>
        </tr>
    </tbody>
</table>
""", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 📡 RADARES CONFIGURADOS
# ==========================================
st.markdown("### 📡 Radares Configurados")

st.markdown("""
<table class="components-table">
    <thead>
        <tr>
            <th>Nombre</th>
            <th>IP</th>
            <th>Puerto</th>
            <th>Ubicación</th>
            <th>Estado</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>BAHIAS</strong></td>
            <td>192.168.4.152</td>
            <td>3000</td>
            <td>Bahías</td>
            <td><span class="tag tag-prod">Activo</span></td>
        </tr>
        <tr>
            <td><strong>FINESTRE</strong></td>
            <td>192.168.4.36</td>
            <td>3000</td>
            <td>Finestre</td>
            <td><span class="tag tag-prod">Activo</span></td>
        </tr>
        <tr>
            <td><strong>ROMANZA</strong></td>
            <td>192.168.4.99</td>
            <td>3000</td>
            <td>Romaza</td>
            <td><span class="tag tag-dev">Pendiente</span></td>
        </tr>
    </tbody>
</table>
""", unsafe_allow_html=True)

# ==========================================
# 📝 FOOTER
# ==========================================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 30px; color: #9aa0a6;">
        <p>🌌 SE-MAMO-GEMINI v6.2 | Sistema de Radar LCC AI</p>
        <p style="font-size: 0.9em; margin-top: 10px;">Última actualización: 16/02/2026</p>
    </div>
""", unsafe_allow_html=True)
 