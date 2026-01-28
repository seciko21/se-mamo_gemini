# 📖 Manual de Operación - Sistema Radar v4.0

## 🔧 Requisitos de Instalación
1. **FFmpeg:** Debe estar instalado en el host o dentro del contenedor.
2. **Acceso RTSP:** La cámara AXIS debe tener habilitado el acceso Anonymous o un usuario con permisos de visualización.
3. **Samba/NFS:** Carpeta montada en `/mnt/md0/radar/clips` con permisos 777.

## 🚀 Despliegue Directo
Para iniciar el servicio:
```bash
docker-compose up -d --build




//////////////////////////////////////////



🛰️ Sistema de Radar & Bot de Gestión
Servidor: Rocky Linux | Almacenamiento: 900GB HDD | Acceso: Túnel Dinámico

Este sistema monitorea eventos de radar en tiempo real, almacena clips de video en un disco de alta capacidad y ofrece un Dashboard web accesible desde cualquier parte del mundo sin necesidad de abrir puertos en el router.

🏗️ Arquitectura del Sistema
El proyecto se basa en una infraestructura de contenedores Docker interconectados:

Radar Monitor: Captura y procesa los eventos.

Radar Bot: Interfaz de control vía Telegram (reportes, estado del disco, alertas).

Radar Tunnel: Puente SSH seguro que expone el panel local a internet.

🚀 Guía de Operación Rápida
1. Reconstrucción Total

Si el sistema se detiene o realizas cambios profundos:

Bash
cd /root/radar_proyecto
docker-compose down
docker-compose up -d --build
2. Sincronización de la URL Pública

Debido a que usamos una URL gratuita de localhost.run, esta cambia cada vez que el contenedor se reinicia. Para actualizar el Bot con el nuevo enlace:

Extraer la URL activa:

Bash
docker logs radar_tunel 2>&1 | grep "https://"
Vincular al Bot (Paso Crítico): Copia la URL obtenida y pégala en el siguiente comando:

Bash
URL_PUBLICO="https://TU-URL-DETECTADA.lhr.life" docker-compose up -d radar-bot
💾 Gestión de Almacenamiento
El sistema utiliza un punto de montaje dedicado para evitar saturar el disco de arranque:

Ruta Física: /mnt/darat

Capacidad: 900GB

Mantenimiento: Un script en crontab limpia automáticamente los clips con más de 30 días de antigüedad cada medianoche.

Comando de emergencia para permisos: Si el bot reporta errores de lectura en el disco:

Bash
sudo chmod -R 755 /mnt/darat
🛠️ Panel de Control de Servicios (Docker)
Comando	Función
docker ps	Ver servicios activos y su tiempo de vida.
docker logs -f radar_bot	Ver en tiempo real qué está haciendo el bot.
docker restart radar_tunel	Forzar el cambio de la URL pública.
docker-compose top	Ver consumo de recursos (CPU/RAM) del proyecto.
📅 Automatizaciones Programadas (Cron)
El sistema es autónomo gracias a estas tareas:

DuckDNS: Mantiene vinculado el dominio lcc-radar.duckdns.org.

Auto-Update URL: El script actualizar_url.sh intenta refrescar el enlace del bot cada 15 min.

Purga de Datos: Limpieza automática de espacio en disco.

🔒 Próxima Mejora: Dominio Permanente
Para eliminar la necesidad de actualizar la URL manualmente, el siguiente paso es migrar a Cloudflare Tunnel.

Requisito: Dominio propio .com o similar.

Beneficio: URL fija (ej: https://panel.radar-lcc.com) y seguridad de nivel empresarial.