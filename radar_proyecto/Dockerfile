FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TZ=America/Mexico_City

# 1. Dependencias mínimas de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl sqlite3 libgl1 libglib2.0-0 tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. INSTALACIÓN POR PASOS (Para no saturar el disco)
RUN pip install --no-cache-dir --upgrade pip

# PASO CRÍTICO: Instalar TORCH CPU primero solo. 
# Esto evita que easyocr intente bajar la versión de 5GB de NVIDIA.
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# PASO 2: Instalar el resto de librerías
RUN pip install --no-cache-dir \
    requests urllib3 pandas opencv-python-headless easyocr

# 3. PRE-DESCARGA DEL MODELO (Solo si el disco lo permite)
RUN python3 -c "import easyocr; reader = easyocr.Reader(['es'], gpu=False)"

COPY . .

CMD ["python3"]