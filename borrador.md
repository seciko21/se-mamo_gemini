🚀 Borrador Maestro: se-mamo_gemini v3.8
📂 1. Mapa de Rutas (Estructura de Datos)
Toda la persistencia de datos reside en el disco de 900GB montado en el servidor.

Disco Físico: /mnt/darat/

Base de Datos: /mnt/darat/data/cola_mensajes.db

Almacenamiento de Video: /mnt/darat/clips/

Almacenamiento de Fotos: /mnt/darat/multas_fotos/

🛠️ 2. Repositorio Unificado (Monorepo)
Ubicación del código fuente: /root/se-mamo_gemini/

Plaintext
se-mamo_gemini/
├── docker-compose.yml       # Orquestador Maestro
├── .gitignore               # Exclusión de datos pesados
├── radar_proyecto/          # Código del Monitor y Bot
│   ├── Dockerfile
│   └── app/
└── radar_web/               # Código del Dashboard
    ├── Dockerfile
    └── app.py
🐳 3. Configuración de Servicios (docker-compose.yml)
Este archivo controla los 4 pilares del sistema con un solo mando.

YAML
version: '3.8'
services:
  # MOTOR: Captura y procesamiento de radares
  radar-monitor:
    build: ./radar_proyecto
    container_name: radar_monitor
    network_mode: "host"
    restart: always
    volumes:
      - /mnt/darat:/mnt/darat
    command: python3 app/monitor_radar.py

  # BOT: Interfaz de comandos en Telegram
  radar-bot:
    build: ./radar_proyecto
    container_name: radar_bot
    network_mode: "host"
    restart: always
    environment:
      - URL_PUBLICO=https://radar.radar-lcc.site
    volumes:
      - /mnt/darat:/mnt/darat
    command: python3 app/bot_comando.py

  # TÚNEL: Acceso seguro vía Cloudflare
  radar-tunel:
    image: cloudflare/cloudflared:latest
    container_name: radar_tunel_fijo
    network_mode: "host"
    restart: always
    environment:
      - TUNNEL_TOKEN=eyJhIjoiMDk0YmJhYzIzMTBjNTRhMWJhNjcwN2ZlYjNkNjM2MzAiLCJ0IjoiNTk4NDcxMGEtOGUxYS00ZWE4LTg4MjAtNDk5NTIwMGQ3ZjFlIiwicyI6Ik56TTJaV1F5TmpVdE5Ea3pNaTAwTWpRd0xXRm1ORGN0TkdGaE5USTJOelU0Tm1ZMCJ9
    command: tunnel --no-autoupdate run --url http://127.0.0.1:8085

  # DASHBOARD: Visualización de datos y videos
  radar-dashboard:
    build: ./radar_web
    container_name: radar_dashboard
    restart: always
    ports:
      - "8085:8501"
    volumes:
      - /mnt/darat/data:/app/data_folder
      - /mnt/darat/clips:/app/clips:ro
      - /mnt/darat/multas_fotos:/app/imagenes_multas
📝 4. Resumen de Funciones Clave
Monitor: Escucha sockets de radar, clasifica infracciones (Preventivo, Alerta, Grave), ejecuta OCR para placas y guarda evidencia en el disco de 900GB.

Bot: Responde comandos en tiempo real, permite forzar capturas de prueba, descargar clips .mp4 por nombre y muestra el estado de salud de la red.

Dashboard: Interfaz web en radar.radar-lcc.site con reporte de hoy, gráficas de tendencia, exportación a Excel y visor de video integrado.

Git: Repositorio inicializado con rama main y protección contra archivos binarios pesados en el historial.

📡 5. Comandos de Administración Rápida
Iniciar todo: docker-compose up -d

Ver actividad: docker-compose logs -f

Estado de Salud: git status y docker ps

Este borrador deja tu configuración lista para ser replicada o escalada en cualquier momento.


🏎️ se-mamo_gemini v3.8 - Borrador Maestro Final📂 1. Infraestructura de Almacenamiento (900GB)El sistema opera sobre un volumen de alta capacidad montado en /mnt/darat/.Base de Datos (SQLite): /mnt/darat/data/cola_mensajes.dbRepositorio de Clips: /mnt/darat/clips/ (Videos .mp4)Repositorio de Fotos: /mnt/darat/multas_fotos/ (Evidencia JGP + OCR)📡 2. Especificaciones de Antenas (Hardware)Las antenas están configuradas para enviar ráfagas de datos vía Socket TCP al servidor central.AntenaIP de OrigenPuertoProtocoloAcción en Grave (≥60km/h)BAHÍAS192.168.4.1523000TCP SocketCaptura Axis + Video 15sFINESTRE192.168.4.363000TCP SocketCaptura Axis + Video 15s🐳 3. Orquestación Unificada (docker-compose.yml)Ubicación: /root/se-mamo_gemini/docker-compose.ymlYAMLversion: '3.8'
services:
  # MOTOR: Escucha a las antenas y procesa IA OCR
  radar-monitor:
    build: ./radar_proyecto
    container_name: radar_monitor
    network_mode: "host"
    restart: always
    volumes:
      - /mnt/darat:/mnt/darat
    command: python3 app/monitor_radar.py

  # BOT: Gestión de comandos y alertas Telegram
  radar-bot:
    build: ./radar_proyecto
    container_name: radar_bot
    network_mode: "host"
    restart: always
    environment:
      - URL_PUBLICO=https://radar.radar-lcc.site
    volumes:
      - /mnt/darat:/mnt/darat
    command: python3 app/bot_comando.py

  # TÚNEL: Cloudflare Zero Trust
  radar-tunel:
    image: cloudflare/cloudflared:latest
    container_name: radar_tunel_fijo
    network_mode: "host"
    restart: always
    environment:
      - TUNNEL_TOKEN=eyJhIjoiMDk0YmJhYzIzMTBjNTRhMWJhNjcwN2ZlYjNkNjM2MzAiLCJ0IjoiNTk4NDcxMGEtOGUxYS00ZWE4LTg4MjAtNDk5NTIwMGQ3ZjFlIiwicyI6Ik56TTJaV1F5TmpVdE5Ea3pNaTAwTWpRd0xXRm1ORGN0TkdGaE5USTJOelU0Tm1ZMCJ9
    command: tunnel --no-autoupdate run --url http://127.0.0.1:8085

  # DASHBOARD: Interfaz Web Pro v3.8
  radar-dashboard:
    build: ./radar_web
    container_name: radar_dashboard
    restart: always
    ports:
      - "8085:8501"
    volumes:
      - /mnt/darat/data:/app/data_folder
      - /mnt/darat/clips:/app/clips:ro
      - /mnt/darat/multas_fotos:/app/imagenes_multas
📜 4. Protocolo de Clasificación de VelocidadPREVENTIVO (≤ 54 km/h): Solo registro en base de datos.ALERTA (55 - 59 km/h): Notificación en Telegram + Captura de Foto.GRAVE (≥ 60 km/h): Notificación Crítica + OCR Placa + Foto + Video (15s).🚀 5. Comandos de Supervivencia (Main Branch)Levantar el sistema: docker-compose up -d --buildRevisar multas en vivo: docker-compose logs -f radar_monitorVerificar salud de red: Enviar 🌐 Salud de la Red al Bot de Telegram.Backup de Código: git add . && git commit -m "Snapshot se-mamo_gemini"