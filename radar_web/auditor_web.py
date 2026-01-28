import os

# ================= CONFIGURACIÓN =================
RUTA_WEB = "/root/radar_web"  # Tu ruta confirmada
SALIDA = "resumen_web.txt"

# Archivos que nos interesa leer para entender tu web
EXT_INTERES = {'.py', '.html', '.css', '.js', '.txt', '.yml', '.yaml'}
ARCHIVOS_EXACTOS = {'Dockerfile'}

# Carpetas y archivos a IGNORAR (Basura, binarios, DBs)
DIRS_IGNORAR = {'.git', '__pycache__', 'imagenes_multas', 'venv', 'env', '.idea', 'vscode'}
EXT_IGNORAR = {'.db', '.sqlite', '.rpm', '.pyc', '.png', '.jpg', '.mp4'}

def debe_leerse(nombre_archivo):
    if nombre_archivo in ARCHIVOS_EXACTOS: return True
    _, ext = os.path.splitext(nombre_archivo)
    return ext in EXT_INTERES and ext not in EXT_IGNORAR

def procesar_directorio():
    with open(SALIDA, 'w', encoding='utf-8') as f_out:
        f_out.write(f"REPORTE DE CÓDIGO WEB - {RUTA_WEB}\n")
        f_out.write("========================================\n")

        if not os.path.exists(RUTA_WEB):
            print(f"❌ Error: La ruta {RUTA_WEB} no existe.")
            return

        for raiz, dirs, archivos in os.walk(RUTA_WEB):
            # Filtrar carpetas ignoradas
            dirs[:] = [d for d in dirs if d not in DIRS_IGNORAR]

            for archivo in archivos:
                if debe_leerse(archivo):
                    ruta_completa = os.path.join(raiz, archivo)
                    try:
                        with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f_in:
                            contenido = f_in.read()
                            
                        f_out.write(f"\n\n--- ARCHIVO: {archivo} ({raiz}) ---\n")
                        f_out.write(contenido)
                        f_out.write(f"\n--- FIN: {archivo} ---\n")
                        print(f"✅ Leído: {archivo}")
                    except Exception as e:
                        print(f"⚠️ No se pudo leer {archivo}: {e}")

if __name__ == "__main__":
    procesar_directorio()
    print(f"\n✨ ¡Listo! Archivo creado: {SALIDA}")
    print("👉 Ejecuta: cat resumen_web.txt")
