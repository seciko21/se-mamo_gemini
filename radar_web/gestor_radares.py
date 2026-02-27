"""
MÓDULO DE GESTIÓN DE RADARES PARA LA APLICACIÓN WEB
====================================================
Este módulo permite a la aplicación web acceder a los radares configurados
leyéndolos desde la base de datos SQLite.

La base de datos es actualizada por el bot cuando se agregan/editan/eliminan radares.
"""

import sqlite3
import os
import json

# Rutas configurables con fallback a rutas relativas
BASE_DATA_PATH = os.environ.get('RADAR_DATA_PATH', '/mnt/darat/data')
DB_PATH = os.environ.get('RADAR_DB_PATH', '/app/data_folder/cola_mensajes.db')
RADARES_FILE = os.path.join(BASE_DATA_PATH, 'radares.json')

# Fallback a rutas locales si no existen
if not os.path.exists(DB_PATH):
    DB_PATH = 'cola_mensajes.db'

def obtener_radares():
    """
    Obtiene la lista de radares desde la base de datos.
    Returns: dict - Diccionario de radares {nombre: {ip, puerto, activo}}
    """
    radares = {}
    
    # Primero intentar desde la base de datos
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT nombre, ip, puerto, activo FROM radares_config WHERE activo = 1")
        for row in c.fetchall():
            radares[row[0]] = {"ip": row[1], "puerto": row[2], "activo": row[3]}
        conn.close()
        
        if radares:
            return radares
    except Exception as e:
        print(f"Error leyendo radares de DB: {e}")
    
    # Fallback: intentar leer desde el archivo JSON (montaje directo)
    try:
        if os.path.exists(RADARES_FILE):
            with open(RADARES_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error leyendo radares de JSON: {e}")
    
    # Último fallback: valores por defecto
    return {
        "RC50": {"ip": "192.168.4.152", "puerto": 3000},
        "FINESTRE": {"ip": "192.168.4.36", "puerto": 3000},
        "ROMANZA": {"ip": "192.168.4.99", "puerto": 3000}
    }

def obtener_lista_radares():
    """
    Obtiene una lista simple de nombres de radares.
    Returns: list - Lista de nombres de radares
    """
    radares = obtener_radares()
    return list(radares.keys())

# Alias para compatibilidad
get_radares = obtener_radares
RADARES = obtener_radares()
