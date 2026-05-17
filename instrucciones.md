# Instrucciones del Proyecto SE-MAMO-GEMINI

## Resumen del Proyecto
SE-MAMO-GEMINI es un sistema de monitoreo de tráfico impulsado por IA diseñado para la detección en tiempo real de velocidad de vehículos, clasificación de infracciones, captura de evidencia (fotos/vídeos) y visualización de datos. Integra hardware de radar, alertas automatizadas, un bot de Telegram para gestión remota y un panel web inspirado en la interfaz oscura de Google Gemini. El sistema se enfoca en el cumplimiento de leyes de tránsito con reconocimiento de placas mediante modelos YOLO y EasyOCR.

**Tecnologías utilizadas:**
- **Backend:** Python, SQLite, OpenCV, Ultralytics YOLO, EasyOCR.
- **Frontend:** Streamlit, Plotly, HTML/CSS/JS.
- **Infraestructura:** Docker Compose, Cloudflare Tunnel, Cámaras Axis.
- **Comunicación:** Sockets TCP (datos de radar), HTTP (capturas de cámara), API de Telegram.

**Características clave:**
- Monitoreo de velocidad en tiempo real desde antenas de radar.
- Clasificación de infracciones: Preventiva (<55 km/h), Alerta (55-59 km/h), Grave (≥60 km/h).
- Captura automática de fotos/vídeos para infracciones.
- Notificaciones de Telegram y comandos de bot para control.
- Panel web para análisis, reportes y reproducción de vídeos.

## Estructura de Directorios y Archivos

### Directorio Raíz (`/root/se-mamo_gemini`)
- **`.git/`**: Repositorio Git para control de versiones.
- **`.gitignore`**: Excluye archivos sensibles/grandes (ej. binarios, archivos env).
- **`.kilo/`**: Configuración para Kilo (entorno de desarrollo).
- **`.python-version`**: Especifica la versión de Python (probablemente 3.14).
- **`borrador.md`**: Borrador de resumen de arquitectura, servicios y despliegue.
- **`docker-compose.yml`**: Orquesta 4 servicios: radar-monitor, radar-bot, radar-tunnel, radar-dashboard.
- **`MANUAL_TECNICO.md`**: Manual técnico detallado con flujos de UI, secciones de código y estilos.
- **`radar_proyecto/`**: Backend para monitoreo de radar y bot.
- **`radar_web/`**: Frontend del panel web.
- **`restaurar_proyecto.sh`**: Script Bash para restaurar el proyecto desde un respaldo tar.gz.
- **`sshpass-1.09/`**: Utilidad para manejo de contraseñas SSH (probablemente una dependencia).
- **`stres_radar.py`**: Script Python para pruebas de estrés de detecciones de radar vía Docker exec.

### `radar_proyecto/` (Backend de Monitoreo y Bot)
Maneja la ingestión de datos de radar, procesamiento con IA y integración con Telegram.
- **`app/`**: Código de aplicación central.
  - **`bot_comando.py`**: Bot de Telegram para comandos (ej. verificaciones de salud, capturas forzadas, descargas de vídeo). Usa hilos y caché para rendimiento.
  - **`config.py`**: Constantes de configuración (ej. claves de API de Telegram, credenciales de cámara).
  - **`gestor_radares.py`**: Gestiona configuración dinámica de radares (carga/guarda JSON, actualizaciones seguras para hilos).
  - **`monitor_radar.py`**: Monitor principal: Escucha sockets TCP de radares, procesa detecciones, captura evidencia, envía alertas. Incluye YOLO/EasyOCR para reconocimiento de placas.
  - **`radar_tcp_reader.py`**: Utilidad para leer/parsear paquetes TCP de radar (formato de 4 bytes con cabeceras).
- **`Dockerfile`**: Construye la imagen del contenedor para servicios de monitor/bot.
- **`requirements.txt`**: Dependencias Python (ej. requests, ultralytics, easyocr).
- **`test_ia.py`**: Pruebas de modelos de IA (YOLO, OCR).
- **`test_radar_conexion.py`**: Pruebas de conexiones TCP de radar.
- **`yolov8n.pt`**: Modelo YOLO pre-entrenado para detección de objetos (ej. placas de matrícula).
- **`limpieza_almacenamiento.py`**: Script para limpieza de almacenamiento (ej. archivos antiguos).
- **`README.md`, `MANUAL.md`**: Documentación para configuración del backend.

### `radar_web/` (Frontend del Panel)
Aplicación web basada en Streamlit para visualización y gestión de datos.
- **`app.py`**: Página principal del panel (KPIs en tiempo real, gráficos, estado de sensores).
- **`pages/`**: Sub-páginas para características específicas.
  - **`1_🚨_Infracciones_Graves.py`**: Muestra infracciones graves (≥60 km/h) con filtros, KPIs y galería de fotos.
  - **`2_🎯_alertas.py`**: Muestra alertas (55-59 km/h) con gráficos de evolución.
  - **`3_🎥_Busqueda_Videos.py`**: Búsqueda y reproducción de vídeos por fecha/radar/velocidad.
  - **`4_📊_Estadisticas.py`**: Análisis estadístico (tendencias, mapas de calor, comparaciones de radar).
  - **`5_📖_README.py`**, **`6_📘_Manual_Tecnico.py`**: Páginas de documentación embebidas.
  - **`7_🌌_Pagina_Estrellas.py`**: Página de visualización de campo de estrellas.
  - **`8_🌳_Ramas_Git.py`**: Visualización de ramas Git.
  - **`9_⚙️_Config_Alertas.py`**: Configuraciones de alertas.
- **`auditor_web.py`**: Utilidades de auditoría/registro web.
- **`auth.py`**: Manejo de autenticación.
- **`campo_estrellas.html`**: HTML/JS para fondo animado de campo de estrellas.
- **`db_radar.sqlite`**: DB SQLite local (espejo de la DB principal para acceso web).
- **`Dockerfile`**: Construye el contenedor web.
- **`gestor_radares.py`**: Gestión de radares (similar al backend).
- **`imagenes_multas/`**: Directorio para imágenes de multas almacenadas.
- **`requirements.txt`**: Dependencias (ej. streamlit, pandas, plotly).
- **`static/`, **`templates/`**: Activos estáticos y plantillas.
- **`README.md`**: Documentación específica de la web.

## Componentes Principales e Interacciones
El sistema es modular, con componentes que se comunican vía TCP, HTTP, DB y APIs. El flujo de datos va desde el hardware hasta el almacenamiento/visualización.

1. **Hardware de Radar (Antenas Externas)**: Dispositivos físicos de detección de velocidad (ej. BAHÍAS en 192.168.4.152:3000, FINESTRE en 192.168.4.36:3000). Envían paquetes TCP de 4 bytes.

2. **Servicio de Monitor (`radar_proyecto/app/monitor_radar.py`)**: Motor de procesamiento central. Recibe datos, clasifica infracciones, captura evidencia.

3. **Base de Datos (SQLite)**: Almacena detecciones históricas y configuraciones en `/mnt/darat/data/cola_mensajes.db`.

4. **Bot de Telegram (`radar_proyecto/app/bot_comando.py`)**: Interfaz remota para monitoreo/control.

5. **Panel Web (`radar_web/app.py` + páginas)**: Visualización y reportes.

6. **Túnel de Cloudflare**: Acceso seguro remoto al panel.

## Mapa Conceptual del Proceso
El flujo de trabajo es lineal desde la detección hasta la visualización, con alertas y almacenamiento en paralelo.

```
[Antenas de Radar] --> Paquetes TCP --> [Servicio de Monitor]
                                      |
                                      v
[Captura de Cámara (HTTP)] --> [Procesamiento IA (YOLO/OCR)] --> [Clasificación]
                                      |
                                      v
[Almacenamiento DB] <--> [Alertas Telegram]    [Almacenamiento Archivos (Fotos/Vídeos)]
                                      |
                                      v
[Consultas/Comandos del Bot] --> [Panel Web] --> [Visualización del Usuario]
                                      ^
                                      |
[Túnel Cloudflare] --> [Acceso Seguro]
```

1. **Detección:** Radar detecta velocidad, envía paquete TCP.
2. **Ingestión:** Monitor parsea paquete, verifica umbral.
3. **Procesamiento:** Si infracción, captura foto, OCR de placa, clasifica severidad.
4. **Alertas:** Envía notificación/foto/vídeo a Telegram.
5. **Almacenamiento:** Guarda datos/archivos en DB/disco.
6. **Gestión:** Bot permite consultas/comandos remotos.
7. **Visualización:** Web lee DB, muestra análisis/vídeos.
8. **Acceso:** Túnel asegura acceso web.

Esta estructura asegura cumplimiento en tiempo real con precisión de IA, control remoto y visualización escalable. El proyecto enfatiza rendimiento (caché, hilos) y seguridad (túneles, auth).