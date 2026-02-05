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
    page_title="Radar LCC AI", 
    layout="wide", 
    page_icon="✨", 
    initial_sidebar_state="expanded"
)

OFFSET_HORAS = -0

# RUTAS (Prioridad Docker)
DB_PATH = '/app/data_folder/cola_mensajes.db'
if not os.path.exists(DB_PATH): DB_PATH = 'cola_mensajes.db'
CLIPS_DIR = "/app/clips/"
FOTOS_PATH = "/app/imagenes_multas/" 

# ==========================================
# ✨ CSS MAESTRO: GEMINI DARK UI + SIDEBAR PRO
# ==========================================
st.markdown("""
    <style>
        /* --- 1. FONDO "DEEP SPACE" --- */
        .stApp {
            background-color: #0b0f19;
            background-image: radial-gradient(circle at 50% -20%, #1c2235 0%, #0b0f19 60%);
        }
        
        .block-container { padding-top: 2rem; max-width: 96%; }

        /* --- 2. SIDEBAR (MENÚ LATERAL) ESTILO GEMINI --- */
        [data-testid="stSidebar"] {
            background-color: #0b0f19;
            border-right: 1px solid rgba(100, 149, 237, 0.05);
        }
        
        /* Título de Navegación */
        div[data-testid="stSidebarNav"]::before {
            content: "PANEL DE CONTROL";
            margin-left: 20px; margin-top: 20px; margin-bottom: 10px;
            font-size: 10px; font-weight: 700; color: #5f6368; letter-spacing: 1px;
            display: block;
        }
        
        /* Enlaces del Menú */
        div[data-testid="stSidebarNav"] a {
            background-color: transparent;
            color: #9aa0a6;
            border-radius: 12px;
            margin: 5px 10px; padding: 10px 15px;
            transition: all 0.3s ease;
            border: 1px solid transparent;
        }

        /* Hover */
        div[data-testid="stSidebarNav"] a:hover {
            background-color: rgba(255, 255, 255, 0.03);
            color: #e8eaed;
            transform: translateX(3px);
        }

        /* ACTIVO (Página Actual - Efecto Gradiente) */
        div[data-testid="stSidebarNav"] a[aria-current="page"] {
            background: linear-gradient(90deg, rgba(66, 133, 244, 0.15), rgba(233, 30, 99, 0.15));
            border: 1px solid rgba(138, 180, 248, 0.2);
            color: #fff;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        /* --- 3. TARJETAS GEMINI (GLASS/ROUNDED) --- */
        .gemini-card {
            background-color: #131722;
            border-radius: 24px;
            border: 1px solid rgba(100, 149, 237, 0.08);
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        .gemini-card:hover {
            border-color: rgba(138, 180, 248, 0.2);
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
        }

        /* --- 4. TYPOGRAPHY & GRADIENTS --- */
        .gradient-text-logo {
            background: linear-gradient(90deg, #8ab4f8, #f5a5c0, #e8eaed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
        
        .card-header {
            color: #e8eaed; font-size: 18px; font-weight: 600; margin-bottom: 20px;
            display: flex; align-items: center; gap: 10px;
        }

        /* --- 5. KPIs --- */
        .kpi-val { font-size: 38px; font-weight: 700; color: #fff; letter-spacing: -1px; line-height: 1.1; }
        .kpi-sub { font-size: 12px; color: #9aa0a6; margin-top: 6px; font-weight: 500; }
        
        /* --- 6. INPUTS REDONDEADOS --- */
        .stSelectbox > div > div, .stDateInput > div > div, .stTextInput > div > div > input {
            background-color: #1e2330 !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #e8eaed !important;
        }
        
        /* --- 7. SCROLLBAR FINO --- */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #0b0f19; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #555; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 MOTOR DE DATOS
# ==========================================
@st.cache_data(ttl=10)
def get_data():
    try:
        if not os.path.exists(DB_PATH): return pd.DataFrame()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        df = pd.read_sql_query("SELECT * FROM historial ORDER BY id DESC LIMIT 3000", conn)
        conn.close()
        
        if df.empty: return df
        
        df['fecha_completa'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora'].astype(str))
        df['fecha_completa'] = df['fecha_completa'] + timedelta(hours=OFFSET_HORAS)
        
        if 'tipo' not in df.columns: df['tipo'] = "N/A"
        if 'placa' not in df.columns: df['placa'] = "---"
        df['tipo'] = df['tipo'].fillna("N/A")
        df['placa'] = df['placa'].fillna("---")
        return df
    except: return pd.DataFrame()

df_raw = get_data()

# ==========================================
# 🖥️ HEADER & FILTROS
# ==========================================
c_head, c_filt = st.columns([1, 1])

with c_head:
    # --- CAMBIO REALIZADO AQUÍ: LCC AI ---
    st.markdown("""
        <div style="font-size: 26px; font-weight: 600; color: white; margin-bottom: 10px;">
            <span style="font-size: 32px;">✨</span> Radar <span class="gradient-text-logo">LCC AI</span>
        </div>
    """, unsafe_allow_html=True)

if not df_raw.empty:
    df = df_raw.copy()
    
    with c_filt:
        c1, c2, c3 = st.columns(3)
        radar_sel = c1.selectbox("📍 Ubicación", ["TODOS"] + sorted(df['radar'].unique().tolist()), label_visibility="collapsed")
        tipo_sel = c2.selectbox("🚗 Clase", ["TODOS"] + sorted(df['tipo'].astype(str).unique().tolist()), label_visibility="collapsed")
        f_min, f_max = df['fecha_completa'].dt.date.min(), df['fecha_completa'].dt.date.max()
        rango = c3.date_input("Periodo", (max(f_min, f_max - timedelta(days=2)), f_max), label_visibility="collapsed")

    if radar_sel != "TODOS": df = df[df['radar'] == radar_sel]
    if tipo_sel != "TODOS": df = df[df['tipo'] == tipo_sel]
    if len(rango) == 2: df = df[(df['fecha_completa'].dt.date >= rango[0]) & (df['fecha_completa'].dt.date <= rango[1])]

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 📊 NIVEL 1: TARJETAS KPI
    # ==========================================
    k1, k2, k3, k4 = st.columns(4)
    
    def draw_kpi(col, title, val, sub, icon="📊", alert=False):
        border = "1px solid rgba(255, 85, 70, 0.4)" if alert else "1px solid rgba(100, 149, 237, 0.1)"
        bg = "rgba(255, 85, 70, 0.05)" if alert else "#131722"
        text_col = "#ffb4ab" if alert else "#fff"
        col.markdown(f"""
            <div class="gemini-card" style="padding: 20px; border:{border}; background:{bg}; margin-bottom: 15px;">
                <div style="color: #a8c7fa; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">
                    {icon} {title}
                </div>
                <div class="kpi-val" style="color:{text_col};">{val}</div>
                <div class="kpi-sub">{sub}</div>
            </div>
        """, unsafe_allow_html=True)

    draw_kpi(k1, "Tráfico Total", f"{len(df):,}", "Vehículos procesados")
    draw_kpi(k2, "Vel. Promedio", f"{round(df['velocidad'].mean(), 1)}", "Km/h Global", "⚡")
    graves = len(df[df['velocidad'] >= 60])
    draw_kpi(k3, "Infracciones", f"{graves}", "Alertas de Prioridad", "🚨", alert=True)
    draw_kpi(k4, "Récord Vel.", f"{df['velocidad'].max()}", "Km/h Máximo registrado", "🏆")

    # ==========================================
    # 📈 NIVEL 2: PANEL PRO (GRADIENTES GEMINI)
    # ==========================================
    st.markdown('<div class="gemini-card">', unsafe_allow_html=True)
    c_chart, c_summary = st.columns([3, 1], gap="medium")
    
    with c_chart:
        st.markdown('<div class="card-header">✨ Dispersión de Velocidad (IA Analysis)</div>', unsafe_allow_html=True)
        gemini_gradient = ["#4285F4", "#9C27B0", "#E91E63"] 
        fig_scatter = px.scatter(
            df.head(600), x="fecha_completa", y="velocidad", color="velocidad", size="velocidad",
            color_continuous_scale=gemini_gradient, hover_data=["radar", "placa"], template="plotly_dark"
        )
        fig_scatter.update_layout(
            height=380, margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title=None),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title="Km/h"),
            font=dict(color="#9aa0a6")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with c_summary:
        st.markdown("##### ⚡ Resumen Inteligente")
        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
        v_max = df['velocidad'].max()
        v_mean = df['velocidad'].mean()
        high_events = len(df[df['velocidad'] > 50])
        
        grad_cyan = "background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 28px; font-weight: 800;"
        grad_pink = "background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 36px; font-weight: 800;"

        st.markdown(f"<div style='margin-bottom:15px;'><div style='font-size:11px; color:#a8c7fa; font-weight:bold;'>VELOCIDAD PICO</div><div style='{grad_cyan}'>{v_max} <span style='font-size:14px; -webkit-text-fill-color:#888;'>km/h</span></div></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"<div style='margin-bottom:15px;'><div style='font-size:11px; color:#a8c7fa; font-weight:bold;'>PROMEDIO</div><div style='{grad_cyan}'>{v_mean:.1f} <span style='font-size:14px; -webkit-text-fill-color:#888;'>km/h</span></div></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"<div style='background:linear-gradient(135deg,rgba(245,87,108,0.05),rgba(0,0,0,0)); border:1px solid rgba(245,87,108,0.3); border-radius:16px; padding:15px; text-align:center;'><span style='color:#ffb4ab; font-weight:bold; font-size:11px;'>🔴 ALERTAS ACTIVAS</span><div style='{grad_pink}; margin-top:5px;'>{high_events}</div></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 📸 NIVEL 3: FEED Y SENSORES (SOLUCIONADO)
    # ==========================================
    c_feed, c_side = st.columns([2, 1])
    
    with c_feed:
        st.markdown('<div class="gemini-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📸 Capturas Recientes</div>', unsafe_allow_html=True)
        cols_img = st.columns(3)
        for i, (_, row) in enumerate(df.head(3).iterrows()):
            with cols_img[i]:
                color = "#f5a5c0" if row['velocidad'] >= 60 else "#333"
                st.markdown(f"<div style='border-radius:16px; overflow:hidden; border:1px solid {color}; margin-bottom:10px;'>", unsafe_allow_html=True)
                foto = row.get('foto')
                if foto and os.path.exists(os.path.join(FOTOS_PATH, foto)):
                    st.image(os.path.join(FOTOS_PATH, foto), use_container_width=True)
                else:
                    st.markdown("<div style='height:100px; background:#1e2330;'></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background:rgba(19,23,34,0.9); padding:8px; text-align:center;'><span style='color:#fff; font-weight:bold;'>{row['velocidad']} km/h</span></div></div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_side:
        # Pestañas
        tab1, tab2 = st.tabs(["📊 Distribución", "📡 Sensores"])
        
        with tab1:
            st.markdown('<div class="gemini-card" style="padding:15px;">', unsafe_allow_html=True)
            colors = ["#8ab4f8", "#f5a5c0", "#81c995", "#fdd663"]
            fig_pie = px.pie(df, names='radar', hole=0.6, color_discrete_sequence=colors)
            fig_pie.update_layout(height=220, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=True, legend=dict(orientation="h", y=-0.1))
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with tab2:
            # === SENSORES HTML (VARIABLE PLANA PARA EVITAR ERRORES) ===
            sensors_html_block = ""
            sensors_html_block += '<div class="gemini-card" style="padding:15px; height:350px; overflow-y:auto;">'
            sensors_html_block += '<div style="color:#e8eaed; font-size:16px; font-weight:600; margin-bottom:15px;">📡 Estado de Sensores</div>'
            
            df_hoy = df_raw[df_raw['fecha_completa'].dt.date == datetime.now().date()]
            radares = sorted(df['radar'].unique())
            
            for r in radares:
                d_r = df_hoy[df_hoy['radar'] == r]
                cnt = len(d_r)
                is_online = cnt > 0
                
                # Variables
                color = "#81c995" if is_online else "#5f6368"
                txt = "ONLINE" if is_online else "OFFLINE"
                bg = "rgba(129, 201, 149, 0.2)" if is_online else "rgba(255, 255, 255, 0.05)"
                
                # Construcción plana
                item = f'<div style="display:flex; justify-content:space-between; align-items:center; padding:12px; margin-bottom:8px; background:rgba(255,255,255,0.03); border-radius:12px; border-left:3px solid {color};">'
                item += f'<div style="display:flex; flex-direction:column;"><span style="color:#e8eaed; font-weight:600; font-size:13px;">{r}</span>'
                item += f'<span style="color:{color}; font-size:10px; letter-spacing:1px; margin-top:2px;">● {txt}</span></div>'
                item += f'<span style="background:{bg}; color:{color}; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:bold;">{cnt}</span></div>'
                
                sensors_html_block += item
            
            sensors_html_block += '</div>'
            st.markdown(sensors_html_block, unsafe_allow_html=True)

    # ==========================================
    # 📝 NIVEL 4: LOGS
    # ==========================================
    with st.expander("📝 Ver Registro Completo", expanded=True):
        st.dataframe(
            df[['fecha', 'hora', 'radar', 'velocidad', 'tipo', 'placa']].head(100),
            use_container_width=True,
            height=300,
            column_config={"velocidad": st.column_config.NumberColumn("Velocidad", format="%d km/h")}
        )

else:
    st.info("Esperando datos... Sistema en línea.")

time.sleep(30)
st.rerun()