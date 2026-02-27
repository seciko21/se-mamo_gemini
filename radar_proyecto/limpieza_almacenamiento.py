#!/usr/bin/env python3
"""
🔧 Script de Limpieza de Almacenamiento para Sistema Radar
============================================================
Este script limpia:
- Registros de historial mayores a X días
- Fotos huérfanas (sin referencia en BD)
- Videos antiguos
- Compacta la base de datos SQLite (VACUUM)

Uso: python limpieza_almacenamiento.py [--dias 30] [--dry-run]
"""

import sqlite3
import os
import sys
import argparse
from datetime import datetime, timedelta

# ==========================================
# CONFIGURACIÓN
# ==========================================
BASE_DIR = os.environ.get('RADAR_BASE_DIR', '/mnt/darat')
DB_FILE = f"{BASE_DIR}/data/cola_mensajes.db"
FOTOS_PATH = f"{BASE_DIR}/multas_fotos/"
VIDEOS_PATH = f"{BASE_DIR}/clips/"

# Días de retención (por defecto 30)
DIAS_RETENCION = 30

# Validar que las rutas existan al inicio
def validar_rutas():
    """Valida que las rutas requeridas existan"""
    rutas_ok = True
    if not os.path.exists(BASE_DIR):
        print_status(f"Directorio base no encontrado: {BASE_DIR}", "ERROR")
        rutas_ok = False
    if not os.path.exists(DB_FILE):
        print_status(f"Base de datos no encontrada: {DB_FILE}", "ERROR")
        rutas_ok = False
    return rutas_ok

def print_status(msg, tipo="INFO"):
    """Imprime mensaje con formato"""
    icons = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERROR": "❌"}
    print(f"{icons.get(tipo, 'ℹ️')} [{tipo}] {msg}")

def obtener_conexion_db():
    """Obtiene conexión a la base de datos"""
    if not os.path.exists(DB_FILE):
        print_status(f"Base de datos no encontrada: {DB_FILE}", "ERROR")
        return None
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def limpiar_historial(conn, dias, dry_run=False):
    """Elimina registros de historial mayores a X días"""
    fecha_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
    
    # Contar registros a eliminar
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM historial WHERE fecha < ?", (fecha_limite,))
    count = c.fetchone()[0]
    
    if count == 0:
        print_status(f"Historial: No hay registros mayores a {dias} días", "INFO")
        return 0
    
    print_status(f"Historial: {count} registros a eliminar (antes de {fecha_limite})", "WARN")
    
    if dry_run:
        print_status("Modo dry-run: no se realizará ninguna eliminación", "INFO")
        return count
    
    # Eliminar registros
    c.execute("DELETE FROM historial WHERE fecha < ?", (fecha_limite,))
    conn.commit()
    print_status(f"Historial: {count} registros eliminados", "OK")
    return count

def limpiar_cola_antigua(conn, dias, dry_run=False):
    """
    Elimina mensajes en cola mayores a X días.
    
    ¿Qué es la COLA?
    ---------------
    La cola es un sistema de resiliencia del sistema radar. Cuando el radar
    detecta una infracción y intenta enviar la alerta a Telegram, si falla 
    (por ejemplo, sin internet, Telegram caído, etc.), el mensaje se GUARDA
    en esta tabla 'cola' para reintentarlo más tarde.
    
    El sistema tiene un proceso (procesar_cola_reintentos) que intenta
    enviar estos mensajes pendientes cada 60 segundos.
    
    Si hay 140,097 mensajes pendientes, significa que hay un problema
    continuo de conectividad - los mensajes no se están enviando y se acumulan.
    """
    fecha_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d %H:%M:%S')
    
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM cola WHERE fecha < ?", (fecha_limite,))
    count = c.fetchone()[0]
    
    if count == 0:
        print_status("Cola: No hay mensajes pendientes antiguos", "INFO")
        return 0
    
    print_status(f"Cola: {count} mensajes antiguos a eliminar", "WARN")
    
    if dry_run:
        return count
    
    c.execute("DELETE FROM cola WHERE fecha < ?", (fecha_limite,))
    conn.commit()
    print_status(f"Cola: {count} mensajes eliminados", "OK")
    return count

def limpiar_fotos_orphaned(conn, dry_run=False):
    """Elimina fotos que no tienen referencia en la base de datos"""
    if not os.path.exists(FOTOS_PATH):
        print_status(f"Directorio de fotos no encontrado: {FOTOS_PATH}", "WARN")
        return 0
    
    # Obtener todas las fotos referenciadas en historial
    c = conn.cursor()
    c.execute("SELECT DISTINCT foto FROM historial WHERE foto IS NOT NULL AND foto != ''")
    fotos_db = set(row[0] for row in c.fetchall())
    
    # Obtener todas las fotos en el directorio
    fotos_disco = set(f for f in os.listdir(FOTOS_PATH) if f.endswith(('.jpg', '.jpeg', '.png')))
    
    # Fotos huérfanas (en disco pero no en BD)
    orphan_photos = fotos_disco - fotos_db
    
    if not orphan_photos:
        print_status("Fotos: No hay fotos huérfanas", "INFO")
        return 0
    
    # Calcular tamaño
    total_size = sum(os.path.getsize(os.path.join(FOTOS_PATH, f)) for f in orphan_photos)
    total_size_mb = total_size / (1024 * 1024)
    
    print_status(f"Fotos: {len(orphan_photos)} fotos huérfanas ({total_size_mb:.1f} MB)", "WARN")
    
    if dry_run:
        print_status("Modo dry-run: no se realizará ninguna eliminación", "INFO")
        return len(orphan_photos)
    
    # Eliminar fotos huérfanas
    for foto in orphan_photos:
        try:
            os.remove(os.path.join(FOTOS_PATH, foto))
        except Exception as e:
            print_status(f"Error al eliminar {foto}: {e}", "ERROR")
    
    print_status(f"Fotos: {len(orphan_photos)} fotos huérfanas eliminadas", "OK")
    return len(orphan_photos)

def limpiar_videos_antiguos(dias, dry_run=False):
    """Elimina videos mayores a X días"""
    if not os.path.exists(VIDEOS_PATH):
        print_status(f"Directorio de videos no encontrado: {VIDEOS_PATH}", "WARN")
        return 0
    
    # Filtrar solo archivos de video (no logs)
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    cutoff_time = datetime.now().timestamp() - (dias * 86400)
    
    videos_antiguos = []
    for f in os.listdir(VIDEOS_PATH):
        if f.endswith(video_extensions):
            filepath = os.path.join(VIDEOS_PATH, f)
            if os.path.getmtime(filepath) < cutoff_time:
                videos_antiguos.append(filepath)
    
    if not videos_antiguos:
        print_status(f"Videos: No hay videos mayores a {dias} días", "INFO")
        return 0
    
    # Calcular tamaño
    total_size = sum(os.path.getsize(f) for f in videos_antiguos)
    total_size_mb = total_size / (1024 * 1024)
    
    print_status(f"Videos: {len(videos_antiguos)} videos antiguos ({total_size_mb:.1f} MB)", "WARN")
    
    if dry_run:
        return len(videos_antiguos)
    
    for video in videos_antiguos:
        try:
            os.remove(video)
        except Exception as e:
            print_status(f"Error al eliminar {os.path.basename(video)}: {e}", "ERROR")
    
    print_status(f"Videos: {len(videos_antiguos)} videos eliminados", "OK")
    return len(videos_antiguos)

def vacuum_db(conn, dry_run=False):
    """Compacta la base de datos SQLite"""
    if dry_run:
        print_status("Vacuum: Simulación (no se ejecutará)", "INFO")
        return
    
    print_status("Vacuum: Compactando base de datos...", "INFO")
    try:
        conn.execute("VACUUM")
        print_status("Vacuum: Base de datos compactada", "OK")
    except Exception as e:
        print_status(f"Vacuum error: {e}", "ERROR")

def obtener_estadisticas(conn):
    """Muestra estadísticas actuales del almacenamiento"""
    print("\n" + "="*50)
    print("📊 ESTADÍSTICAS DE ALMACENAMIENTO ACTUAL")
    print("="*50)
    
    # Tamaño de archivos
    if os.path.exists(DB_FILE):
        db_size = os.path.getsize(DB_FILE) / (1024 * 1024)
        print(f"📦 Base de datos: {db_size:.1f} MB")
    
    if os.path.exists(FOTOS_PATH):
        fotos_count = len([f for f in os.listdir(FOTOS_PATH) if f.endswith(('.jpg', '.jpeg', '.png'))])
        fotos_size = sum(os.path.getsize(os.path.join(FOTOS_PATH, f)) 
                        for f in os.listdir(FOTOS_PATH) if f.endswith(('.jpg', '.jpeg', '.png'))) / (1024 * 1024)
        print(f"📷 Fotos: {fotos_count} archivos ({fotos_size:.1f} MB)")
    
    if os.path.exists(VIDEOS_PATH):
        video_ext = ('.mp4', '.avi', '.mov', '.mkv')
        videos_count = len([f for f in os.listdir(VIDEOS_PATH) if f.endswith(video_ext)])
        videos_size = sum(os.path.getsize(os.path.join(VIDEOS_PATH, f)) 
                         for f in os.listdir(VIDEOS_PATH) if f.endswith(video_ext)) / (1024 * 1024)
        print(f"🎥 Videos: {videos_count} archivos ({videos_size:.1f} MB)")
    
    # Registros en BD
    if conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM historial")
        historial_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM cola")
        cola_count = c.fetchone()[0]
        
        # Rango de fechas
        c.execute("SELECT MIN(fecha), MAX(fecha) FROM historial")
        rango = c.fetchone()
        
        print(f"📋 Historial: {historial_count} registros")
        if rango[0] and rango[1]:
            print(f"   Rango de fechas: {rango[0]} a {rango[1]}")
        print(f"📋 Cola de mensajes: {cola_count} pendientes")
    
    # Espacio en disco
    try:
        st = os.statvfs(BASE_DIR)
        usado_pct = ((st.f_blocks - st.f_bavail) / st.f_blocks) * 100
        libre_gb = (st.f_bavail * st.f_frsize) / (1024**3)
        print(f"💾 Disco: {usado_pct:.1f}% usado, {libre_gb:.1f} GB libre")
    except:
        pass
    
    print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Limpieza de almacenamiento del sistema radar")
    parser.add_argument("--dias", type=int, default=30, help="Días de retención (default: 30)")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin hacer cambios")
    parser.add_argument("--stats", action="store_true", help="Solo mostrar estadísticas")
    args = parser.parse_args()
    
    print("\n" + "🔧 "*20)
    print("🧹 LIMPIEZA DE ALMACENAMIENTO - SISTEMA RADAR")
    print("🔧 "*20 + "\n")
    
    if args.dry_run:
        print_status("MODO DRY-RUN: Solo simulación, no se eliminarán archivos\n", "WARN")
    
    dias = args.dias
    
    # Obtener conexión a BD
    if not validar_rutas():
        print_status("No se puede continuar sin las rutas válidas", "ERROR")
        sys.exit(1)
    
    conn = obtener_conexion_db()
    if not conn:
        print_status("No se puede continuar sin base de datos", "ERROR")
        sys.exit(1)
    
    # Mostrar estadísticas
    obtener_estadisticas(conn)
    
    if args.stats:
        conn.close()
        return
    
    # Ejecutar limpieza
    print(f"🗑️ INICIANDO LIMPIEZA (retención: {dias} días)\n")
    
    # 1. Limpiar historial
    limpiar_historial(conn, dias, args.dry_run)
    
    # 2. Limpiar cola antigua
    limpiar_cola_antigua(conn, dias, args.dry_run)
    
    # 3. Limpiar fotos huérfanas
    limpiar_fotos_orphaned(conn, args.dry_run)
    
    # 4. Limpiar videos antiguos
    limpiar_videos_antiguos(dias, args.dry_run)
    
    # 5. Vacuum (solo si no es dry-run)
    if not args.dry_run:
        vacuum_db(conn)
    
    conn.close()
    
    # Mostrar estadísticas finales
    print("\n📊 ESTADÍSTICAS DESPUÉS DE LIMPIEZA:")
    conn2 = obtener_conexion_db()
    if conn2:
        obtener_estadisticas(conn2)
        conn2.close()
    
    print("\n✅ Limpieza completada!\n")

if __name__ == "__main__":
    main()
