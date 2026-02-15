"""
Módulo de autenticación para Radar Web
Permite acceso público a ciertas páginas sin login
"""
import streamlit as st
import hashlib
import os

# ==========================================
# CONFIGURACIÓN DE USUARIOS (Archivo JSON)
# ==========================================
USERS_FILE = "/app/data_folder/users.json"
if not os.path.exists(USERS_FILE):
    USERS_FILE = "users.json"

# Usuarios por defecto (puede擴充)
DEFAULT_USERS = {
    "admin": {
        "password": "admin123",  # En producción, usar hash
        "role": "admin"
    },
    "operador": {
        "password": "operador123",
        "role": "user"
    }
}

# ==========================================
# FUNCIONES DE AUTENTICACIÓN
# ==========================================

def load_users():
    """Carga usuarios desde archivo JSON"""
    if os.path.exists(USERS_FILE):
        try:
            import json
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_USERS.copy()

def save_users(users):
    """Guarda usuarios en archivo JSON"""
    try:
        import json
        os.makedirs(os.path.dirname(USERS_FILE) if os.path.dirname(USERS_FILE) else ".", exist_ok=True)
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        return True
    except:
        return False

def hash_password(password):
    """Hashea password"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verifica password"""
    return hash_password(password) == hashed

def init_session():
    """Inicializa sesión de usuario"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None

def login(username, password):
    """Intenta login"""
    users = load_users()
    
    if username in users:
        user = users[username]
        # Verificar password (soporta hash o texto plano para compatibilidad)
        stored_pass = user.get('password', '')
        if verify_password(password, stored_pass) or password == stored_pass:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.role = user.get('role', 'user')
            return True
    return False

def logout():
    """Cierra sesión"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None

def is_authenticated():
    """Retorna si usuario está autenticado"""
    return st.session_state.get('authenticated', False)

def get_username():
    """Retorna nombre de usuario"""
    return st.session_state.get('username')

def get_role():
    """Retorna rol de usuario"""
    return st.session_state.get('role')

# ==========================================
# PÁGINAS PÚBLICAS (sin login requerido)
# ==========================================
PUBLIC_PAGES = [
    "app.py",  # Página principal
    "1_🚨_Infracciones_Graves.py",
    "2_🎯_alertas.py",
    "3_🎥_Busqueda_Videos.py",
    "4_📊_Estadisticas.py"
]

def is_public_page():
    """Determina si la página actual es pública"""
    try:
        import streamlit as st
        # Obtener página actual
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        if ctx is None:
            return False
        current_page = ctx.script_path
        if current_page:
            page_name = os.path.basename(current_page)
            return page_name in PUBLIC_PAGES
    except:
        pass
    return False

def require_login():
    """Requiere login si la página no es pública"""
    init_session()
    
    if is_public_page():
        # Página pública, permitir acceso
        return True
    
    if not is_authenticated():
        # Mostrar login
        show_login_page()
        return False
    
    return True

def show_login_page():
    """Muestra página de login"""
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 50px auto;
            padding: 30px;
            background: #131722;
            border-radius: 20px;
            border: 1px solid rgba(100, 149, 237, 0.2);
        }
        .login-title {
            text-align: center;
            color: #fff;
            font-size: 24px;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 Iniciar Sesión</div>', unsafe_allow_html=True)
    
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar", type="primary"):
        if login(username, password):
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

def show_login_button():
    """Muestra botón de login en sidebar"""
    init_session()
    
    if is_authenticated():
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"👤 **Usuario:** {get_username()}")
        st.sidebar.markdown(f"🔖 **Rol:** {get_role()}")
        if st.sidebar.button("Cerrar Sesión"):
            logout()
            st.rerun()
    else:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔐 Acceso Restringido")
        st.sidebar.info("Algunas funciones requieren inicio de sesión.")

# ==========================================
# UI DE LOGIN EMBEBIDO
# ==========================================
def show_login_form():
    """Muestra formulario de login en la página"""
    init_session()
    
    if is_authenticated():
        return True
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h2>🔐 Iniciar Sesión</h2>
            <p style="color: #888;">Acceso solo para personal autorizado</p>
        </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("Usuario", key="login_user")
        password = st.text_input("Contraseña", type="password", key="login_pass")
        
        if st.button("Ingresar", type="primary", use_container_width=True):
            if login(username, password):
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 12px;">
            Contacta al administrador si no tienes credenciales
        </div>
        """, unsafe_allow_html=True)
    
    return False
