 # 📘 Manual Técnico: Sistema Clawdbot v5.1

## 📜 Descripción General
Clawdbot es un sistema de vigilancia híbrido que combina la detección de velocidad por radar con inteligencia artificial para la clasificación de vehículos (YOLOv8) y reconocimiento de caracteres (EasyOCR).

---

## 🏗️ Arquitectura del Sistema (Áreas Maestras)

### 1. Cerebro de Inteligencia Artificial (YOLO + OCR)
Esta sección transforma la imagen capturada en datos estructurados.

* **Lógica de Clasificación:** Utiliza `yolov8n.pt` para identificar si el infractor es un **Automóvil, Motocicleta, Camión o Autobús**. Esto permite aplicar reglas de negocio diferentes según el tipo de vehículo.
* **Filtro Anti-Fechas (Regex):** El sistema utiliza expresiones regulares para limpiar el texto detectado. Si el OCR confunde la estampa de tiempo de la cámara (ej. 20260130) con una placa, el código detecta la cadena larga de números e ignora ese resultado.



### 2. Motor de Evidencia Visual (Modo CSI)
Encargado de procesar la fotografía para que sea una prueba válida y legible.

* **Pintado de Bounding Boxes:** Dibuja rectángulos verdes sobre la placa detectada.
* **Timestamping Dinámico:** Estampa la velocidad y la fecha en la **esquina inferior izquierda**. Se utiliza el cálculo `alto - offset` para asegurar que el texto sea visible independientemente de la resolución de la cámara.
* **Contraste Legible:** El texto se genera con una sombra negra de fondo para garantizar la lectura sobre cualquier color de vehículo.



### 3. Gestión de Memoria y Video (FFmpeg Buffer)
Controla la grabación y optimización de clips de video.

* **Buffer Circular en RAM:** El sistema graba constantemente clips de 15 segundos en `/dev/shm/` (memoria compartida). Esto evita el desgaste del disco duro y permite un acceso ultra rápido.
* **Concatenación Robusta:** Al detectar una infracción, une el clip de 15s (pasado) con 5s nuevos (presente) usando el comando `concat` de FFmpeg sin recodificar, manteniendo la eficiencia del procesador.

### 4. Controlador de Optimización de CPU
Es el filtro de entrada que decide el nivel de procesamiento necesario.

* **Umbral de Disparo (55 km/h):** * **Menor a 55:** Envía una alerta preventiva simple. No activa la IA ni guarda fotos, manteniendo el servidor ligero.
    * **Mayor o igual a 55:** Despierta a Clawdbot para realizar el análisis completo de IA y evidencia CSI.



---

## 🛠️ Mantenimiento y Solución de Problemas

| Problema | Causa Probable | Solución |
| :--- | :--- | :--- |
| **Error: Module ultralytics** | Caché de Docker vieja | Ejecutar `docker-compose build --no-cache` |
| **Placas con fechas** | Fallo en Regex | Verificar que el archivo `monitor_radar.py` tenga el `import re` |
| **Contenedor reiniciando** | Error de sintaxis | Revisar logs con `docker logs radar_monitor` |
| **Disco Lleno** | Fallo en motor_mantenimiento | El script limpia al llegar al 90%, verificar permisos en `/mnt/darat` |

---

## 📡 Protocolos de Comunicación
* **RTSP:** Para el flujo de video en tiempo real.
* **HTTP Digest Auth:** Para interactuar con las APIs internas de las cámaras Axis (Overlays y Capturas).
* **Telegram API:** Notificación asíncrona mediante hilos (`threading`) para no bloquear el radar.

---
Manual generado para el Proyecto Se-Mamo_Gemini - 2026 
