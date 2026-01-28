# Manteniendo tu línea base
FROM python:3.10-slim

# Manteniendo tu bloque de configuración de zona horaria
RUN apt-get update && apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/America/Mexico_City /etc/localtime && \
    echo "America/Mexico_City" > /etc/timezone

# --- BLOQUE DE INSTALACIÓN DE DEPENDENCIAS ---
# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo de requerimientos
COPY requirements.txt .

# Instalamos las librerías necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código de la aplicación (app.py y otros archivos)
COPY . .

# Exponemos el puerto que usa Streamlit
EXPOSE 8501

# Comando para ejecutar la aplicación al iniciar el contenedor
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]