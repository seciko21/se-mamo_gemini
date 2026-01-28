# 🏎️ Radar Proyecto V2.0 - Sistema Profesional

Sistema automatizado de monitoreo de infracciones con almacenamiento masivo (900GB), reporte vía Telegram y Dashboard analítico.

## 🚀 Arquitectura del Sistema
El proyecto está dividido en servicios independientes gestionados por Docker:
1. **Monitor**: Captura datos y gestiona el almacenamiento en `/mnt/darat`.
2. **Bot (@Rocket_lcc_bot)**: Interfaz de comandos en Telegram y alertas al grupo **LCC-RADAR**.
3. **Dashboard**: Interfaz web en Streamlit para visualización de métricas y videos.
4. **Túnel Cloudflare**: Conexión segura y dominio fijo en `https://radar.radar-lcc.site`.

## 📦 Requisitos de Almacenamiento
* **Ruta de Datos**: `/mnt/darat` (Disco de 900GB).
* **Limpieza Automática**: Configurada vía Crontab para eliminar clips mayores a 30 días.

## 🛠️ Instalación y Despliegue
Para levantar el sistema completo:
```bash
cd /root/radar_proyecto
docker-compose up -d
```

## 📊 Dashboard y Red
* **URL Local**: http://localhost:8085
* **URL Pública**: https://radar.radar-lcc.site
* **Puerto Interno**: 8501 (Mapeado al 8085)

## 📝 Mantenimiento (Crontab)
El sistema cuenta con dos tareas críticas:
1. Limpieza de disco a las 00:00 hrs.
2. Actualización de IP DuckDNS cada 5 minutos.

---
**Versión Tag:** v2.0.0-estable
