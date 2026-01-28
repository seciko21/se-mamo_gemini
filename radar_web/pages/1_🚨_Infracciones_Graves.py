import streamlit as st
import sqlite3
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="Infracciones Graves", page_icon="🚨", layout="wide")

# ==========================================
# 1. DETECCIÓN DE RUTAS (INTELIGENTE)
# ==========================================
RUTAS_DB = [
    '/app/data_folder/cola_mensajes.db',  # Docker
    'db_radar.sqlite',                    # Local Symlink
    'cola_mensajes.db'                    # Local Directo
]
DB_PATH = next((r for r in RUTAS_DB if os.path.exists(r)), None)
FOTOS_DIR = "imagenes_multas"

# ==========================================
# 2. CARGA DE DATOS OPTIMIZADA (CACHE)
# ==========================================
@st.cache_data(ttl=15)  # Se actualiza cada 15 segundos automáticamente si hay cambios
def cargar_graves(fecha_inicio, fecha_fin):
    if not DB_PATH: return pd.DataFrame()

    try:
        conn = sqlite3.connect(DB_PATH)
        # Verificamos columnas para evitar errores
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(historial)")
        cols = [i[1] for i in cursor.fetchall()]
        
        # --- DETECCIÓN DINÁMICA DE COLUMNAS NUEVAS ---
        has_foto = 'foto' in cols
        has_placa = 'placa' in cols
        
        col_foto = ", foto" if has_foto else ""
        col_placa = ", placa" if has_placa else ""
        
        # Consulta actualizada para traer la PLACA también
        query = f"""
            SELECT id, radar, velocidad, fecha, hora {col_foto} {col_placa}
            FROM historial 
            WHERE velocidad >= 60 
            AND fecha BETWEEN ? AND ?
            ORDER BY fecha DESC, hora DESC
        """
        
        df = pd.read_sql_query(query, conn, params=(fecha_inicio, fecha_fin))
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error DB: {e}")
        return pd.DataFrame()

# ==========================================
# 3. INTERFAZ Y FILTROS LATERALES
# ==========================================
st.title("🚨 Monitor de Infracciones Graves")
st.markdown("---")

# Sidebar para filtros
with st.sidebar:
    st.header("🔍 Filtros de Búsqueda")
    
    # Filtro de Fechas
    hoy = datetime.now().date()
    col1, col2 = st.columns(2)
    f_inicio = col1.date_input("Desde", hoy - timedelta(days=7)) 
    f_fin = col2.date_input("Hasta", hoy)
    
    # Carga de datos inicial con el rango seleccionado
    df = cargar_graves(f_inicio, f_fin)
    
    # Filtro de Radar (dinámico)
    radares_disponibles = ["Todos"] + sorted(list(df['radar'].unique())) if not df.empty else ["Todos"]
    filtro_radar = st.selectbox("Seleccionar Radar:", radares_disponibles)
    
    # --- NUEVO: FILTRO POR PLACA ---
    filtro_placa = st.text_input("Buscar por Placa:", "").upper()
    
    st.divider()
    st.caption(f"📅 Mostrando datos del {f_inicio} al {f_fin}")
    
    if st.button("🔄 Actualizar Ahora", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Aplicar filtros en memoria
df_show = df.copy()
if filtro_radar != "Todos":
    df_show = df_show[df_show['radar'] == filtro_radar]

if filtro_placa:
    # Filtramos si la columna placa existe y el texto coincide
    if 'placa' in df_show.columns:
        df_show = df_show[df_show['placa'].str.contains(filtro_placa, na=False)]

# ==========================================
# 4. MÉTRICAS SUPERIORES (KPIs)
# ==========================================
if not df_show.empty:
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    kpi1.metric("Total Graves", len(df_show), delta="En rango seleccionado")
    
    max_vel = df_show['velocidad'].max()
    radar_max = df_show.loc[df_show['velocidad'].idxmax()]['radar']
    kpi2.metric("Récord de Velocidad", f"{max_vel} km/h", radar_max, delta_color="inverse")
    
    radar_freq = df_show['radar'].mode()[0]
    count_freq = len(df_show[df_show['radar'] == radar_freq])
    kpi3.metric("Radar + Conflictivo", radar_freq, f"{count_freq} multas")

    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(df_show)
    kpi4.download_button(
        label="📥 Descargar Reporte CSV",
        data=csv,
        file_name='infracciones_graves.csv',
        mime='text/csv',
    )
    
    st.markdown("---")

# ==========================================
# 5. GALERÍA DE TARJETAS (CON SOPORTE IA)
# ==========================================
if df_show.empty:
    st.info("✅ No se encontraron infracciones graves con los filtros seleccionados.")
else:
    cols = st.columns(3)
    
    for index, row in df_show.reset_index().iterrows():
        with cols[index % 3]:
            with st.container(border=True):
                # Encabezado
                c_head1, c_head2 = st.columns([2, 1])
                c_head1.subheader(f"⚡ {row['velocidad']} km/h")
                c_head2.caption(f"{row['fecha']}")
                
                st.text(f"📍 {row['radar']} | 🕒 {row['hora']}")
                
                # --- MOSTRAR PLACA (CORRECCIÓN IA) ---
                if 'placa' in row and row['placa'] not in [None, "NO_APLICA", "NO_DETECTADA", "ERROR_IA"]:
                    st.success(f"🆔 **PLACA: {row['placa']}**")
                else:
                    st.warning("🆔 Placa: No identificada")
                
                # Imagen
                nombre_foto = row.get('foto')
                img_mostrada = False
                
                if nombre_foto:
                    ruta_completa = os.path.join(FOTOS_DIR, nombre_foto)
                    if os.path.exists(ruta_completa):
                        st.image(ruta_completa, use_container_width=True)
                        img_mostrada = True
                
                if not img_mostrada:
                    st.markdown("""
                        <div style="
                            height: 150px; 
                            background-color: #262730; 
                            border-radius: 8px; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center; 
                            color: #888;
                            border: 1px dashed #444;">
                            📷 Sin Evidencia Visual
                        </div>
                    """, unsafe_allow_html=True)