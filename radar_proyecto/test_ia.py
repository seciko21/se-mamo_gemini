import easyocr
import cv2
import os

# Ruta INTERNA del contenedor (donde Docker ve las fotos)
FOTOS_PATH = "/mnt/md0/radar/multas_fotos/"

print("🔍 Buscando imágenes en:", FOTOS_PATH)

if not os.path.exists(FOTOS_PATH):
    print(f"❌ ERROR: La carpeta {FOTOS_PATH} no existe dentro del contenedor.")
    exit()

archivos = [f for f in os.listdir(FOTOS_PATH) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

if not archivos:
    print("❌ ERROR: No hay fotos en la carpeta para probar.")
    exit()

foto_test = 'prueba_ia.jpg'
ruta_completa = os.path.join(FOTOS_PATH, foto_test)

print(f"📸 Probando con: {foto_test}")

# Inicializar IA
reader = easyocr.Reader(['es'], gpu=False)

# Leer imagen usando la ruta directamente (más seguro para EasyOCR)
try:
    results = reader.readtext(ruta_completa)
    print("-" * 30)
    if not results:
        print("Empty: No se detectó texto (esto es normal si la foto es oscura o borrosa).")
    else:
        for (bbox, text, prob) in results:
            print(f"✅ DETECTADO: {text.upper()} (Confianza: {prob:.2f})")
    print("-" * 30)
except Exception as e:
    print(f"❌ ERROR CRÍTICO: {e}")