import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, timedelta
import random

# ==========================================
# 🛑 CONFIGURACIÓN DEL SISTEMA
# ==========================================
st.set_page_config(
    page_title="Estadísticas - LCC AI", 
    layout="wide", 
    page_icon="📊", 
    initial_sidebar_state="expanded"
)

# RUTAS
DB_PATH = '/app/data_folder/cola_mensajes.db'
if not os.path.exists(DB_PATH):
    DB_PATH = 'cola_mensajes.db'
if not os.path.exists(DB_PATH):
    DB_PATH = '/mnt/darat/data/cola_mensajes.db'
if not os.path.exists(DB_PATH):
    DB_PATH = '../cola_mensajes.db'

# ==========================================
# ✨ CSS MAESTRO - ESTILO GEMINI + TABLA
# ==========================================
st.markdown("""
    <style>
        /* --- FONDO --- */
        .stApp {
            background-color: #0b0f19;
            background-image: radial-gradient(circle at 50% -20%, #1c2235 0%, #0b0f19 60%);
        }
        .block-container { padding-top: 2rem; max-width: 96%; }
        [data-testid="stSidebar"] { background-color: #0b0f19; border-right: 1px solid rgba(100, 149, 237, 0.05); }
        
        /* --- TARJETAS GEMINI --- */
        .gemini-card {
            background-color: #131722;
            border-radius: 24px;
            border: 1px solid rgba(100, 149, 237, 0.08);
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }

        /* --- HEADER --- */
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

        /* --- KPI --- */
        .kpi-val { font-size: 38px; font-weight: 700; color: #fff; letter-spacing: -1px; }
        .kpi-sub { font-size: 12px; color: #9aa0a6; margin-top: 6px; }
        .metric-diff {
            font-size: 12px; padding: 2px 8px; border-radius: 8px; margin-left: 8px;
        }
        .diff-pos { background: rgba(16, 185, 129, 0.2); color: #10b981; }
        .diff-neg { background: rgba(245, 87, 87, 0.2); color: #f5575c; }

        /* --- TABLA PERSONALIZADA --- */
        .custom-table-container {
            background-color: #0F131F;
            border-radius: 12px;
            padding: 20px;
            font-family: 'Segoe UI', sans-serif;
            border: 1px solid #1e2538;
        }
        .table-header-title {
            color: #E2E8F0;
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .styled-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        .styled-table th {
            text-align: left;
            padding: 12px 8px;
            color: #94A3B8;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 11px;
            border-bottom: 1px solid #1E293B;
        }
        .styled-table td {
            padding: 12px 8px;
            color: #E2E8F0;
            border-bottom: 1px solid #1E293B;
        }
        .styled-table tr:last-child td { border-bottom: none; }
        .styled-table tr:hover { background-color: #171C2C; }
        
        /* Badges */
        .badge-dir { background-color: #0EA5E9; color: white; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }
        .badge-ok { background-color: rgba(34, 197, 94, 0.15); color: #4ade80; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; border: 1px solid rgba(34, 197, 94, 0.3); }
        .badge-inf { background-color: rgba(239, 68, 68, 0.2); color: #f87171; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; border: 1px solid rgba(239, 68, 68, 0.4); }
        .text-blue { color: #60A5FA; }
        
        .section-header {
            color: #e8eaed; font-size: 20px; font-weight: 600; margin: 30px 0 15px 0;
            border-bottom: 1px solid rgba(100, 149, 237, 0.2); padding-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

def conectar_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except Exception as e:
        st.error(f"Error conectando a DB: {e}")
        return None

@st.cache_data(ttl=30)
def obtener_datos_historial():
    conn = conectar_db()
    if conn is None:
        return pd.DataFrame()
    
    try:
        df = pd.read_sql_query("SELECT * FROM historial ORDER BY id DESC LIMIT 5000", conn)
        conn.close()
        
        if df.empty:
            return df
        
        # Procesamiento de fechas
        df['timestamp'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora'].astype(str), errors='coerce')
        df['fecha_dia'] = df['timestamp'].dt.date
        df['hora_num'] = df['timestamp'].dt.hour
        df['dia_semana'] = df['timestamp'].dt.day_name()
        df['semana'] = df['timestamp'].dt.isocalendar().week
        
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

def render_custom_table(df):
    """Renderiza tabla estilo con vehículos detectados - usa st.dataframe nativo"""
    if df.empty:
        st.info("📭 No hay datos para mostrar en la tabla de vehículos detectados.")
        return

    df_view = df.copy()
    
    # Verificar que las columnas necesarias existan
    required_cols = ['timestamp', 'velocidad', 'radar']
    missing_cols = [col for col in required_cols if col not in df_view.columns]
    if missing_cols:
        st.warning(f"⚠️ Faltan columnas en los datos: {', '.join(missing_cols)}")
        return
    
    # Formatear Hora
    df_view['hora_fmt'] = df_view['timestamp'].dt.strftime('%I:%M:%S %p').str.lower().str.replace('am', 'a.m.').str.replace('pm', 'p.m.')
    
    # Simular columnas faltantes
    if 'lecturas' not in df_view.columns:
        df_view['lecturas'] = [random.randint(1, 15) for _ in range(len(df_view))]
    
    df_view['direccion'] = 'IN'
    
    # Estado OK vs INFRACCIÓN (límite 55 km/h)
    df_view['estado'] = df_view['velocidad'].apply(
        lambda x: 'INFRACCIÓN' if x > 55 else 'OK'
    )
    
    # Preparar dataframe para mostrar (últimas 18 filas)
    df_display = df_view.head(18)[['hora_fmt', 'radar', 'direccion', 'velocidad', 'lecturas', 'estado']].copy()
    df_display.columns = ['HORA', 'UBICACIÓN', 'DIR', 'VEL. MAX', 'LECTURAS', 'ESTADO']
    
    # Aplicar estilo con pandas Styler
    def style_estado(val):
        if val == 'INFRACCIÓN':
            return 'color: #f87171; background-color: rgba(239, 68, 68, 0.2); padding: 4px 10px; border-radius: 12px;'
        return 'color: #4ade80; background-color: rgba(34, 197, 94, 0.15); padding: 4px 10px; border-radius: 12px;'
    
    def style_dir(val):
        return 'background-color: #0EA5E9; color: white; padding: 3px 8px; border-radius: 4px;'
    
    def style_ubi(val):
        return 'color: #60A5FA;'
    
    # Aplicar estilos
    styled_df = df_display.style.applymap(style_estado, subset=['ESTADO'])\
                              .applymap(style_dir, subset=['DIR'])\
                              .applymap(style_ubi, subset=['UBICACIÓN'])\
                              .set_properties(**{
                                  'text-align': 'left',
                                  'padding': '12px 8px',
                                  'border-bottom': '1px solid #1E293B'
                              })\
                              .set_table_styles([
                                  {'selector': 'th', 'props': [('text-align', 'left'), ('color', '#94A3B8'), ('font-weight', '600'), ('text-transform', 'uppercase'), ('font-size', '11px'), ('border-bottom', '1px solid #1E293B'), ('padding', '12px 8px')]},
                                  {'selector': 'td', 'props': [('color', '#E2E8F0'), ('font-size', '13px')]},
                              ])
    
    st.markdown('<div class="custom-table-container">', unsafe_allow_html=True)
    st.markdown('<div class="table-header-title"><span>🚚</span> Últimos Vehículos Detectados</div>', unsafe_allow_html=True)
    st.dataframe(styled_df, use_container_width=True, height=500)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🖥️ HEADER
# ==========================================
st.markdown('''
    <div style="text-align: center; display: flex; align-items: center; justify-content: center;">
        <span class="gradient-icon">📊</span>
        <span class="gradient-title">Estadísticas</span>
    </div>
    ''' , unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

df = obtener_datos_historial()

if df.empty:
    st.markdown("""
        <div class="gemini-card" style="text-align: center; padding: 60px;">
            <p style="color: #9aa0a6; font-size: 20px;">📭 Sin datos disponibles</p>
            <p style="color: #5f6368; font-size: 14px;">Base de datos: /mnt/darat/data/cola_mensajes.db</p>
        </div>
    """, unsafe_allow_html=True)
else:
    # ===== FILTROS =====
    st.sidebar.header("🎛️ Filtros")
    radares = ["Todos"] + sorted(df['radar'].dropna().unique().tolist())
    radar_sel = st.sidebar.selectbox("📡 Radar", radares)
    df_filt = df if radar_sel == "Todos" else df[df['radar'] == radar_sel]
    
    # ===== SECCIÓN 1: TABLA PRINCIPAL =====
    st.markdown('<div class="gemini-card">', unsafe_allow_html=True)
    render_custom_table(df_filt)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== SECCIÓN 2: KPIs =====
    st.markdown("---")
    
    # Comparación con período anterior
    total_comp = len(df[df['fecha_dia'] < df_filt['fecha_dia'].min()]) if not df_filt.empty else 0
    total = len(df_filt)
    diff_pct = ((total - total_comp) / total_comp * 100) if total_comp > 0 else 0
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total", f"{total:,}")
    k1.markdown('<div class="kpi-sub">Registros</div>', unsafe_allow_html=True)
    diff_class = "diff-pos" if diff_pct >= 0 else "diff-neg"
    k1.markdown(f'<span class="metric-diff {diff_class}">{diff_pct:+.1f}% vs anterior</span>', unsafe_allow_html=True)
    
    k2.metric("Radares Activos", df_filt['radar'].nunique())
    k3.metric("Velocidad Máxima", f"{df_filt['velocidad'].max()} km/h")
    k4.metric("Velocidad Promedio", f"{df_filt['velocidad'].mean():.1f} km/h")
    
    # ===== SECCIÓN 3: TENDENCIAS =====
    st.markdown('<div class="section-header">📈 Tendencias Temporales</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="gemini-card">', unsafe_allow_html=True)
        st.markdown("### Evolución Diaria")
        
        diario = df_filt.groupby('fecha_dia').agg({
            'velocidad': ['count', 'mean', 'max']
        }).reset_index()
        diario.columns = ['fecha_dia', 'count', 'vel_prom', 'vel_max']
        
        fig_evo = make_subplots(specs=[[{"secondary_y": True}]])
        fig_evo.add_trace(go.Bar(x=diario['fecha_dia'], y=diario['count'], name="Infracciones", marker_color='rgba(99, 102, 241, 0.7)'), secondary_y=False)
        fig_evo.add_trace(go.Scatter(x=diario['fecha_dia'], y=diario['vel_prom'], name="Vel. Promedio", line=dict(color='#10b981', width=3)), secondary_y=True)
        fig_evo.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', legend=dict(orientation="h", y=1.1))
        fig_evo.update_yaxes(title_text="Cantidad", color='white', secondary_y=False)
        fig_evo.update_yaxes(title_text="km/h", color='white', secondary_y=True)
        st.plotly_chart(fig_evo, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="gemini-card">', unsafe_allow_html=True)
        st.markdown("### Heatmap Horario")
        
        hora_dia = df_filt.groupby(['hora_num', 'fecha_dia']).size().reset_index(name='count')
        hora_pivot = hora_dia.pivot_table(index='hora_num', columns='fecha_dia', values='count', fill_value=0)
        fig_heat = px.imshow(hora_pivot, labels=dict(x="Fecha", y="Hora", color="Infracciones"), color_continuous_scale='Viridis')
        fig_heat.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== SECCIÓN 4: ANÁLISIS POR RADAR =====
    st.markdown('<div class="section-header">📡 Análisis por Radar</div>', unsafe_allow_html=True)
    
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        st.markdown('<div class="gemini-card">', unsafe_allow_html=True)
        st.markdown("### Comparativa de Radares")
        
        radar_stats = df_filt.groupby('radar').agg({'velocidad': ['count', 'mean', 'max']}).reset_index()
        radar_stats.columns = ['radar', 'count', 'vel_prom', 'vel_max']
        radar_stats = radar_stats.sort_values('count', ascending=True)
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Bar(y=radar_stats['radar'], x=radar_stats['count'], name='Infracciones', orientation='h', marker_color='rgba(139, 92, 246, 0.7)'))
        fig_radar.add_trace(go.Scatter(y=radar_stats['radar'], x=radar_stats['vel_prom'], name='Vel. Promedio', mode='markers', marker=dict(color='#f59e0b', size=12, line=dict(width=2, color='white'))))
        fig_radar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_radar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_r2:
        st.markdown('<div class="gemini-card">', unsafe_allow_html=True)
        st.markdown("### Distribución de Velocidad")
        
        fig_box = px.box(df_filt, x='radar', y='velocidad', color='radar', color_discrete_sequence=px.colors.qualitative.Bold)
        fig_box.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== SECCIÓN 5: PATRONES TEMPORALES =====
    st.markdown('<div class="section-header">🕐 Patrones Temporales</div>', unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown('<div class="gemini-card">', unsafe_allow_html=True)
        st.markdown("### Día de la Semana")
        
        dia_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        df_filt['dia_semana'] = pd.Categorical(df_filt['dia_semana'], categories=dia_orden, ordered=True)
        dia_stats = df_filt.groupby('dia_semana').size().reset_index(name='count')
        
        fig_dia = px.bar(dia_stats, x='dia_semana', y='count', labels={'dia_semana': 'Día'}, color='count', color_continuous_scale='Blues')
        fig_dia.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_dia, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_t2:
        st.markdown('<div class="gemini-card">', unsafe_allow_html=True)
        st.markdown("### Tendencia Horaria")
        
        hora_stats = df_filt.groupby('hora_num').agg({'velocidad': ['count', 'mean']}).reset_index()
        hora_stats.columns = ['hora_num', 'count', 'vel_prom']
        
        fig_hora = go.Figure()
        fig_hora.add_trace(go.Bar(x=hora_stats['hora_num'], y=hora_stats['count'], name='Infracciones', marker_color='rgba(16, 185, 129, 0.7)'))
        fig_hora.add_trace(go.Scatter(x=hora_stats['hora_num'], y=hora_stats['vel_prom'], name='Vel. Promedio', yaxis='y2', line=dict(color='#f59e0b', width=3)))
        fig_hora.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', xaxis=dict(tickmode='linear', dtick=1), yaxis=dict(title='Cantidad'), yaxis2=dict(title='km/h', overlaying='y', side='right'))
        st.plotly_chart(fig_hora, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== SECCIÓN 6: DETALLE POR RADAR =====
    st.markdown('<div class="section-header">📊 Detalle por Radar</div>', unsafe_allow_html=True)
    
    for radar in sorted(df_filt['radar'].dropna().unique()):
        df_radar = df_filt[df_filt['radar'] == radar]
        with st.expander(f"📡 {radar}", expanded=False):
            c_r1, c_r2, c_r3, c_r4 = st.columns(4)
            c_r1.metric("Total", len(df_radar))
            c_r2.metric("Vel. Promedio", f"{df_radar['velocidad'].mean():.1f} km/h")
            c_r3.metric("Vel. Máxima", f"{df_radar['velocidad'].max()} km/h")
            c_r4.metric("Día Más Activo", str(df_radar['fecha_dia'].mode()[0]))
            
            diario_radar = df_radar.groupby('fecha_dia').size().reset_index(name='count')
            fig_dr = px.bar(diario_radar, x='fecha_dia', y='count', labels={'fecha_dia': 'Fecha'}, color_discrete_sequence=['#8b5cf6'])
            fig_dr.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_dr, use_container_width=True)
    
    # ===== DATOS CRUDOS =====
    with st.expander("📋 Datos crudos"):
        st.dataframe(df_filt[['timestamp', 'radar', 'velocidad', 'placa', 'foto']], use_container_width=True)

# Auto-refresh cada 30 segundos
st.markdown("""
<script>
setTimeout(function(){
    window.location.reload(1);
}, 30000);
</script>
""", unsafe_allow_html=True)
