"""
MÓDULO CENTRALIZADO DE GESTIÓN DE RADARES
==========================================
Este módulo proporciona una fuente única de verdad para la configuración de radares.
Todos los componentes (bot, monitor, web) deben importar RADARES desde aquí.

Funcionalidades:
- Carga radares desde archivo JSON (/mnt/darat/data/radares.json)
- Si no existe, usa los valores por defecto de config.py
- Proporciona función para recargar radares después de cambios
"""

import os
import json
import sqlite3
import time
import threading

# Lock para sincronización de acceso a RADARES
_radares_lock = threading.Lock()

# Rutas configurables con fallback a rutas relativas
BASE_DATA_PATH = os.environ.get('RADAR_DATA_PATH', '/mnt/darat/data')
RADARES_FILE = os.path.join(BASE_DATA_PATH, 'radares.json')

# Valores por defecto (fallback si no existe el JSON)
RADARES_DEFAULT = {
    "RC50": {"ip": "192.168.4.152", "puerto": 3000},
    "FINESTRE": {"ip": "192.168.4.36", "puerto": 3000},
    "ROMANZA": {"ip": "192.168.4.99", "puerto": 3000}
}

# Base de datos - configurable con fallback
DB_FILE = os.environ.get('RADAR_DB_PATH', os.path.join(BASE_DATA_PATH, 'cola_mensajes.db'))

def cargar_radares():
    """
    Carga radares desde JSON. Si no existe, crea con valores por defecto.
    Returns: dict - Diccionario de radares {nombre: {ip, puerto}}
    """
    if os.path.exists(RADARES_FILE):
        try:
            with open(RADARES_FILE, 'r') as f:
                datos = json.load(f)
                if datos:  # Si el archivo no está vacío
                    return datos
        except Exception as e:
            print(f"Error cargando radares desde JSON: {e}")
    
    # Si no existe o está vacío, crear con defaults
    guardar_radares(RADARES_DEFAULT)
    return RADARES_DEFAULT.copy()

def guardar_radares(radares):
    """
    Guarda radares en archivo JSON y actualiza la base de datos.
    Returns: bool - True si exitoso
    """
    try:
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(RADARES_FILE), exist_ok=True)
        
        # Guardar en JSON
        with open(RADARES_FILE, 'w') as f:
            json.dump(radares, f, indent=2)
        
        # Actualizar tabla de radares en DB
        actualizar_tabla_radares_db(radares)
        
        return True
    except Exception as e:
        print(f"Error guardando radares: {e}")
        return False

def actualizar_tabla_radares_db(radares):
    """
    Actualiza la tabla de radares en la base de datos SQLite.
    Crea la tabla si no existe.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # Crear tabla si no existe
        c.execute('''CREATE TABLE IF NOT EXISTS radares_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            ip TEXT NOT NULL,
            puerto INTEGER NOT NULL,
            activo INTEGER DEFAULT 1,
            fecha_alta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Obtener radares actuales en DB
        c.execute("SELECT nombre FROM radares_config")
        db_radares = set(row[0] for row in c.fetchall())
        
        # Radares del JSON
        json_radares = set(radares.keys())
        
        # Insertar o actualizar radares del JSON
        for nombre, datos in radares.items():
            c.execute('''INSERT OR REPLACE INTO radares_config (nombre, ip, puerto, activo)
                          VALUES (?, ?, ?, 1)''',
                      (nombre, datos['ip'], datos['puerto']))
        
        # Desactivar radares que ya no están en JSON
        for nombre in db_radares - json_radares:
            c.execute("UPDATE radares_config SET activo = 0 WHERE nombre = ?", (nombre,))
        
        conn.commit()
        conn.close()
        print(f"✅ Tabla radares_config actualizada en DB")
    except Exception as e:
        print(f"Error actualizando tabla radares en DB: {e}")

def recargar_radares():
    """
    Fuerza la recarga de radares desde el archivo JSON.
    Útil cuando otro proceso ha modificado el archivo.
    Thread-safe: usa lock para evitar condiciones de carrera.
    """
    global RADARES
    with _radares_lock:
        RADARES = cargar_radares()
    return RADARES

def obtener_radares_thread_safe():
    """
    Obtiene una copia thread-safe del diccionario de radares.
    Útil para funciones que se ejecutan en threads separados.
    Returns: dict - Copia del diccionario de radares
    """
    with _radares_lock:
        return RADARES.copy()

def obtener_radares_db():
    """
    Obtiene la lista de radares desde la base de datos.
    Útil para la aplicación web.
    Returns: list - Lista de diccionarios con datos de radares
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT nombre, ip, puerto, activo FROM radares_config WHERE activo = 1")
        radares = [{"nombre": row[0], "ip": row[1], "puerto": row[2], "activo": row[3]} 
                   for row in c.fetchall()]
        conn.close()
        return radares
    except Exception as e:
        print(f"Error obteniendo radares de DB: {e}")
        return []

# ==========================================
# INICIALIZACIÓN: Cargar radares al importar
# ==========================================
with _radares_lock:
    RADARES = cargar_radares()

# Asegurar que la tabla de radares exista en DB
try:
    actualizar_tabla_radares_db(RADARES)
except Exception as e:
    print(f"Nota: No se pudo inicializar tabla radares_config: {e}")

# Iniciar observador de cambios (opcional, se puede activar manualmente)
# inicializar_observador_radares()  # Descomentar para auto-detectar cambios

# Alias para compatibilidad
get_radares = cargar_radares

def inicializar_observador_radares(callback=None):
    """
    Inicia un observador de archivos para detectar cambios en radares.json.
    Cuando el archivo cambia, llama a la función callback (si se proporciona)
    y actualiza la variable global RADARES.
    
    Args:
        callback: Función opcional a llamar cuando cambie el archivo
    """
    import threading
    import hashlib
    
    def observar():
        last_hash = ""
        while True:
            try:
                if os.path.exists(RADARES_FILE):
                    with open(RADARES_FILE, 'rb') as f:
                        current_hash = hashlib.md5(f.read()).hexdigest()
                    
                    if current_hash != last_hash and last_hash != "":
                        print(f"🔄 Cambio detectado en {RADARES_FILE}, recargando radares...")
                        recargar_radares()
                        if callback:
                            callback()
                    
                    last_hash = current_hash
            except Exception as e:
                print(f"Error observando radares.json: {e}")
            
            time.sleep(5)  # Verificar cada 5 segundos
    
    # Iniciar hilo de observación
    hilo = threading.Thread(target=observar, daemon=True)
    hilo.start()
    print("👁 Observador de radares.json iniciado")
    return hilo
