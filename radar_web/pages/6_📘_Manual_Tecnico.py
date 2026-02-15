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
st.set_page_config(page_title="Manual Técnico - LCC AI Radar", page_icon="📘", layout="wide")

with st.sidebar:
    st.markdown(f"👤 **{auth.get_username()}** ({auth.get_role()})")
    if st.button("🚪 Cerrar Sesión"):
        auth.logout()
        st.rerun()

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
            font-size: 42px;
            filter: drop-shadow(0 0 8px rgba(233, 30, 99, 0.4));
            margin: 0;
            display: inline;
        }
        
        .gradient-icon {
            font-size: 48px;
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

        /* --- 5. CONTENIDO DEL MANUAL --- */
        .manual-content {
            background-color: #131722;
            border-radius: 16px;
            border: 1px solid rgba(100, 149, 237, 0.08);
            padding: 24px;
            color: #9aa0a6;
            line-height: 1.8;
        }
        
        .manual-content h1 {
            color: #fff;
            font-size: 32px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(66, 133, 244, 0.3);
        }
        
        .manual-content h2 {
            color: #4285F4;
            font-size: 24px;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        
        .manual-content h3 {
            color: #00BCD4;
            font-size: 20px;
            margin-top: 25px;
            margin-bottom: 12px;
        }
        
        .manual-content p {
            margin-bottom: 15px;
        }
        
        .manual-content ul, .manual-content ol {
            margin-left: 20px;
            margin-bottom: 15px;
        }
        
        .manual-content li {
            margin-bottom: 8px;
        }
        
        .manual-content code {
            background-color: #0d1117;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'Monaco', 'Consolas', monospace;
            color: #c9d1d9;
        }
        
        .manual-content pre {
            background-color: #0d1117;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 15px 0;
        }
        
        .manual-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        .manual-content th, .manual-content td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(100, 149, 237, 0.1);
        }
        
        .manual-content th {
            background-color: rgba(66, 133, 244, 0.1);
            color: #4285F4;
            font-weight: 600;
        }
        
        .manual-content blockquote {
            border-left: 4px solid #4285F4;
            padding-left: 16px;
            margin: 15px 0;
            color: #9aa0a6;
            font-style: italic;
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
# 📖 CONTENIDO DEL MANUAL TÉCNICO INTEGRADO
# ==========================================

st.markdown('''
<div style="text-align: center; display: flex; align-items: center; justify-content: center;">
    <span class="gradient-icon">📘</span>
    <span class="gradient-title">Manual Técnico</span>
</div>
''' , unsafe_allow_html=True)

st.write("")

# Contenido integrado directamente del MANUAL_TECNICO.md
manual_content = """
<h1>🌌 Sistema de Radar LCC AI</h1>

<h2>📋 Descripción del Proyecto</h2>

<p>Sistema integral de monitoreo y análisis de tráfico que combina tecnologías de detección de velocidad, visualización de datos en tiempo real y análisis inteligente. El sistema utiliza radares TCP para capturar datos de vehículos, procesarlos y presentarlos en una interfaz web moderna basada en Streamlit con un diseño visual inspirado en el estilo "Gemini Dark".</p>

<hr style="border-color: rgba(100, 149, 237, 0.2); margin: 30px 0;">

<h2>🎯 Funcionalidades Principales</h2>

<h3>1. Monitoreo en Tiempo Real</h3>
<ul>
<li>Captura continua de datos de velocidad de vehículos</li>
<li>Detección automática de infracciones (>60 km/h)</li>
<li>Estado operativo de sensores/radares</li>
<li>Feed de capturas fotográficas de eventos</li>
</ul>

<h3>2. Análisis de Datos</h3>
<ul>
<li>Estadísticas descriptivas (promedio, máximo, mínimo)</li>
<li>Mapa de calor de intensidad de tráfico por hora</li>
<li>Distribución de velocidad por radar</li>
<li>Tendencias temporales (diarias, semanales, horarias)</li>
</ul>

<h3>3. Sistema de Alertas</h3>
<ul>
<li>Alertas automáticas por excesos de velocidad</li>
<li>Clasificación de infracciones graves</li>
<li>Notificaciones visuales diferenciadas</li>
</ul>

<h3>4. Gestión Multimedia</h3>
<ul>
<li>Búsqueda de videos por fecha y ubicación</li>
<li>Descarga de evidencia en formato MP4</li>
<li>Visualización de capturas fotográficas</li>
</ul>

<h3>5. Exportación de Datos</h3>
<ul>
<li>Descarga de reportes en CSV</li>
<li>Datos crudos para auditoría externa</li>
</ul>

<hr style="border-color: rgba(100, 149, 237, 0.2); margin: 30px 0;">

<h2>🖥️ Manual de Comportamiento</h2>

<h3>Flujo de Usuario</h3>

<pre><code class="text">
 ┌─────────────────────────────────────────────────────────────┐
 │                    PÁGINA PRINCIPAL                         │
 │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
 │  │  Inicio     │  │  Alertas    │  │  Estadísticas       │  │
 │  │  (Dashboard)│  │  (>55km/h)  │  │  (Análisis profundo)│  │
 │  └─────────────┘  └─────────────┘  └─────────────────────┘  │
 │                                                             │
 │  ┌─────────────────────────────────────────────────────┐    │
 │  │  Búsqueda Videos | Infracciones Graves (>60km/h)    │    │
 │  └─────────────────────────────────────────────────────┘    │
 └─────────────────────────────────────────────────────────────┘
</code></pre>

<h3>Uso de Cada Módulo</h3>

<h4>Página Principal (app.py)</h4>
<ol>
<li>Seleccionar ubicación del radar en el filtro</li>
<li>Filtrar por tipo de vehículo</li>
<li>Ajustar rango de fechas</li>
<li>Visualizar KPIs: Tráfico Total, Vel. Promedio, Infracciones, Récord</li>
<li>Explorar gráficos de dispersión y distribución</li>
<li>Revisar capturas recientes</li>
<li>Consultar estado de sensores</li>
</ol>

<h4>Alertas (2_alertas.py)</h4>
<ol>
<li>Visualizar alertas activas (>55 km/h)</li>
<li>Filtrar por radar y período</li>
<li>Ver galería de imágenes con evidencia</li>
<li>Revisar evolución mensual de alertas</li>
</ol>

<h4>Infracciones Graves (1_🚨_Infracciones_Graves.py)</h4>
<ol>
<li>Definir rango de fechas (desde/hasta)</li>
<li>Filtrar por radar y tipo de vehículo</li>
<li>Visualizar estadísticas: Total graves, Velocidad máxima, Punto crítico</li>
<li>Explorar galería de evidencias fotográficas</li>
</ol>

<h4>Búsqueda de Videos (3_Busqueda_Videos.py)</h4>
<ol>
<li>Seleccionar fecha del evento</li>
<li>Elegir ubicación del radar</li>
<li>Ajustar filtro de velocidad mínima</li>
<li>Visualizar timeline de eventos</li>
<li>Reproducir y descargar videos disponibles</li>
</ol>

<h4>Estadísticas (4_📊_Estadisticas.py)</h4>
<ol>
<li>Ver tabla de vehículos detectados</li>
<li>Analizar tendencias temporales</li>
<li>Comparar radares</li>
<li>Identificar patrones por día y hora</li>
<li>Explorar detalle por radar individual</li>
</ol>

<hr style="border-color: rgba(100, 149, 237, 0.2); margin: 30px 0;">

<h2>📁 Estructura del Código</h2>

<h3>Archivo: radar_web/app.py</h3>
<p><strong>Propósito</strong>: Página principal del dashboard</p>

<table>
<tr><th>Sección</th><th>Descripción</th><th>Líneas</th></tr>
<tr><td>Configuración</td><td>Page config de Streamlit</td><td>12-17</td></tr>
<tr><td>Rutas</td><td>Definición de paths para DB y archivos</td><td>21-25</td></tr>
<tr><td>CSS Maestro</td><td>Estilos Gemini Dark UI + Sidebar Pro</td><td>30-145</td></tr>
<tr><td>Motor de Datos</td><td>Función get_data() con cache</td><td>150-170</td></tr>
<tr><td>Header & Filtros</td><td>Título y controles de filtro</td><td>175-199</td></tr>
<tr><td>KPIs</td><td>Tarjetas con métricas principales</td><td>221-225</td></tr>
<tr><td>Panel Pro</td><td>Gráfico de dispersión Plotly</td><td>227-247</td></tr>
<tr><td>Resumen</td><td>Resumen inteligente lateral</td><td>249-263</td></tr>
<tr><td>Feed</td><td>Capturas recientes con imágenes</td><td>271-286</td></tr>
<tr><td>Sensores</td><td>Estado de sensores online/offline</td><td>300-324</td></tr>
<tr><td>Analytics</td><td>Mapa de calor y box plots</td><td>331-361</td></tr>
<tr><td>Auditoría</td><td>Tabla de estadísticas por radar</td><td>363-381</td></tr>
<tr><td>Neural Summary</td><td>Terminal con insights IA</td><td>389-408</td></tr>
<tr><td>Export</td><td>Descarga de datos CSV</td><td>411-424</td></tr>
</table>

<h3>Archivo: radar_web/pages/1_🚨_Infracciones_Graves.py</h3>
<p><strong>Propósito</strong>: Monitoreo de infracciones (>60 km/h)</p>

<table>
<tr><th>Sección</th><th>Descripción</th><th>Líneas</th></tr>
<tr><td>Configuración</td><td>Page config especializado</td><td>11</td></tr>
<tr><td>CSS</td><td>Estilos con gradientes de alerta</td><td>21-104</td></tr>
<tr><td>Lógica</td><td>Función cargar_graves()</td><td>110-122</td></tr>
<tr><td>UI</td><td>Header con gradiente de alerta</td><td>127-131</td></tr>
<tr><td>Filtros</td><td>Contenedor con selects y date inputs</td><td>133-144</td></tr>
<tr><td>KPIs</td><td>Métricas de infracciones graves</td><td>152-172</td></tr>
<tr><td>Galería</td><td>Grid de evidencias fotográficas</td><td>174-203</td></tr>
</table>

<h3>Archivo: radar_web/pages/2_alertas.py</h3>
<p><strong>Propósito</strong>: Monitor de alertas (>55 km/h)</p>

<table>
<tr><th>Sección</th><th>Descripción</th><th>Líneas</th></tr>
<tr><td>Configuración</td><td>Page config expandido</td><td>12-17</td></tr>
<tr><td>CSS</td><td>Estilos Gemini Dark</td><td>29-68</td></tr>
<tr><td>Motor</td><td>get_alert_data() filtrado</td><td>73-87</td></tr>
<tr><td>Header</td><td>Título con gradiente</td><td>94</td></tr>
<tr><td>Filtros</td><td>Selectores de radar y fecha</td><td>101-107</td></tr>
<tr><td>KPIs</td><td>Métricas de alertas</td><td>110-115</td></tr>
<tr><td>Galería</td><td>Grid de imágenes con evidencia</td><td>122-152</td></tr>
<tr><td>Evolución</td><td>Gráfico mensual</td><td>156-166</td></tr>
</table>

<h3>Archivo: radar_web/pages/3_Busqueda_Videos.py</h3>
<p><strong>Propósito</strong>: Sistema de video forense</p>

<table>
<tr><th>Sección</th><th>Descripción</th><th>Líneas</th></tr>
<tr><td>Configuración</td><td>Page config wide</td><td>11</td></tr>
<tr><td>CSS</td><td>Estilos con reproductor</td><td>21-103</td></tr>
<tr><td>Lógica DB</td><td>cargar_infracciones()</td><td>108-121</td></tr>
<tr><td>Lógica Videos</td><td>obtener_videos_disponibles()</td><td>123-130</td></tr>
<tr><td>UI Header</td><td>Título con gradiente</td><td>135-139</td></tr>
<tr><td>Parámetros</td><td>Filtros de búsqueda</td><td>141-156</td></tr>
<tr><td>Timeline</td><td>Dataframe de eventos</td><td>169-173</td></tr>
<tr><td>Visor</td><td>Reproductor y descarga</td><td>182-191</td></tr>
</table>

<h3>Archivo: radar_web/pages/4_📊_Estadisticas.py</h3>
<p><strong>Propósito</strong>: Panel de análisis estadístico</p>

<table>
<tr><th>Sección</th><th>Descripción</th><th>Líneas</th></tr>
<tr><td>Configuración</td><td>Page config wide</td><td>14-19</td></tr>
<tr><td>CSS</td><td>Estilos con tabla personalizada</td><td>33-119</td></tr>
<tr><td>DB</td><td>conectar_db()</td><td>121-127</td></tr>
<tr><td>Datos</td><td>obtener_datos_historial()</td><td>129-152</td></tr>
<tr><td>Tabla</td><td>render_custom_table()</td><td>154-216</td></tr>
<tr><td>Header</td><td>Título con gradiente</td><td>221-225</td></tr>
<tr><td>Filtros</td><td>Sidebar con radares</td><td>239-242</td></tr>
<tr><td>KPIs</td><td>Métricas con comparación</td><td>257-265</td></tr>
<tr><td>Tendencias</td><td>Evolución diaria y heatmap</td><td>268-299</td></tr>
<tr><td>Análisis Radar</td><td>Comparativa y box plots</td><td>304-328</td></tr>
<tr><td>Patrones</td><td>Día y hora</td><td>331-360</td></tr>
<tr><td>Detalle</td><td>Expander por radar</td><td>365-377</td></tr>
</table>

<h3>Archivo: radar_web/campo_estrellas.html</h3>
<p><strong>Propósito</strong>: Visualización de campo de estrellas interactivo</p>

<table>
<tr><th>Componente</th><th>Descripción</th></tr>
<tr><td>Canvas</td><td>Elemento principal de renderizado</td></tr>
<tr><td>Clase Estrella</td><td>Estrellas individuales con parallax y parpadeo</td></tr>
<tr><td>Clase EstrellaFugaz</td><td>Estrellas fugaces con cola de gradiente</td></tr>
<tr><td>drawNebula()</td><td>Nebulosa de fondo con gradiente radial</td></tr>
<tr><td>animate()</td><td>Loop principal de animación</td></tr>
</table>

<hr style="border-color: rgba(100, 149, 237, 0.2); margin: 30px 0;">

<h2>🎨 Estilo Visual Gemini Dark</h2>

<h3>Colores Principales</h3>

<table>
<tr><th>Color</th><th>Valor</th><th>Uso</th></tr>
<tr><td>Fondo Principal</td><td>#0b0f19</td><td>Base de la aplicación</td></tr>
<tr><td>Fondo Tarjeta</td><td>#131722</td><td>Cards y contenedores</td></tr>
<tr><td>Acento Azul</td><td>#4285F4</td><td>Primario Gemini</td></tr>
<tr><td>Acento Rosa</td><td>#E91E63</td><td>Alertas y énfasis</td></tr>
<tr><td>Acento Violeta</td><td>#9C27B0</td><td>Gradientes</td></tr>
<tr><td>Texto Blanco</td><td>#ffffff</td><td>Títulos principales</td></tr>
<tr><td>Texto Gris</td><td>#9aa0a6</td><td>Subtítulos</td></tr>
</table>

<h3>Elementos CSS Destacados</h3>

<pre><code class="css">/* Gradiente de texto */
.gradient-text {
    background: linear-gradient(90deg, #4285F4, #9C27B0, #E91E63);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Tarjeta Gemini */
.gemini-card {
    background-color: #131722;
    border-radius: 24px;
    border: 1px solid rgba(100, 149, 237, 0.08);
    padding: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0b0f19;
    border-right: 1px solid rgba(100, 149, 237, 0.05);
}
</code></pre>

<hr style="border-color: rgba(100, 149, 237, 0.2); margin: 30px 0;">

<h2>🗄️ Base de Datos</h2>

<h3>Estructura de la Tabla historial</h3>

<table>
<tr><th>Campo</th><th>Tipo</th><th>Descripción</th></tr>
<tr><td>id</td><td>INTEGER</td><td>Identificador único</td></tr>
<tr><td>fecha</td><td>DATE</td><td>Fecha del registro</td></tr>
<tr><td>hora</td><td>TIME</td><td>Hora del registro</td></tr>
<tr><td>radar</td><td>TEXT</td><td>Identificador del radar</td></tr>
<tr><td>velocidad</td><td>REAL</td><td>Velocidad detectada (km/h)</td></tr>
<tr><td>tipo</td><td>TEXT</td><td>Tipo de vehículo</td></tr>
<tr><td>placa</td><td>TEXT</td><td>Placa del vehículo</td></tr>
<tr><td>foto</td><td>TEXT</td><td>Ruta de imagen</td></tr>
</table>

<hr style="border-color: rgba(100, 149, 237, 0.2); margin: 30px 0;">

<h2>🚀 Tecnologías Utilizadas</h2>

<ul>
<li><strong>Frontend</strong>: Streamlit, Plotly, HTML/CSS/JS</li>
<li><strong>Backend</strong>: Python, SQLite</li>
<li><strong>Visualización</strong>: Plotly Express, Plotly Graph Objects</li>
<li><strong>Estilos</strong>: CSS Personalizado (Gemini Dark)</li>
<li><strong>Animaciones</strong>: Canvas API (campo_estrellas.html)</li>
</ul>

<hr style="border-color: rgba(100, 149, 237, 0.2); margin: 30px 0;">

<h2>📦 Dependencias</h2>

<pre><code class="text">
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.18.0
sqlite3 (estándar)
</code></pre>

<hr style="border-color: rgba(100, 149, 237, 0.2); margin: 30px 0;">

<h2>📄 Licencia</h2>

<p>© 2024 LCC Analytics - Sistema v2.5</p>
""" 
# 🛑 FIN DE LA VARIABLE manual_content.
# Las tres comillas de arriba (linea anterior) cierran el bloque de texto HTML.

# ==========================================
# 🎨 RENDERIZADO DEL CONTENIDO
# ==========================================
# Inyectamos el HTML dentro del contenedor con la clase CSS 'manual-content'
# Nota: Usamos unsafe_allow_html=True para permitir el renderizado del HTML complejo.
st.markdown(f'''
    <div class="manual-content">
        {manual_content}
    </div>
''', unsafe_allow_html=True)

# ==========================================
# ⚡ ACCESOS RÁPIDOS
# ==========================================
st.markdown("""
    <div class="gemini-card" style="margin-top: 30px;">
        <p class="gradient-subtitle">⚡ Accesos Rápidos</p>
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <a href="/" target="_blank" style="padding: 10px; background: rgba(66, 133, 244, 0.1); border-radius: 8px; color: #4285F4;">
                🏠 Inicio
            </a>
            <a href="https://github.com" target="_blank" style="padding: 10px; background: rgba(66, 133, 244, 0.1); border-radius: 8px; color: #4285F4;">
                📂 Repositorio GitHub
            </a>
            <a href="https://docs.docker.com/get-started/" target="_blank" style="padding: 10px; background: rgba(0, 188, 212, 0.1); border-radius: 8px; color: #00BCD4;">
                🐳 Documentación Docker
            </a>
        </div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 📝 FOOTER (Pie de página)
# ==========================================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #5f6368; font-size: 12px; margin-top: 20px;">
        <p>📘 Manual Técnico | LCC AI Radar Monitor</p>
        <p>© 2024-2026 | Todos los derechos reservados</p>
    </div>
""", unsafe_allow_html=True)
