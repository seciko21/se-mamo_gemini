#!/bin/bash

# Configuración de rutas
PROYECTO_DIR="/root/radar_proyecto"
DOCKER_COMPOSE="/usr/local/bin/docker-compose"

# 1. Extraer la URL más reciente de los logs del túnel
NUEVA_URL=$(docker logs radar_tunel 2>&1 | grep -oE "https://[a-zA-Z0-9.-]+\.lhr\.life" | tail -n 1)

if [ -z "$NUEVA_URL" ]; then
    echo "$(date): Error - No se detectó URL en radar_tunel."
    exit 1
fi

# 2. Obtener la URL que tiene el bot actualmente
URL_ACTUAL=$(docker inspect radar_bot --format='{{range .Config.Env}}{{println .}}{{end}}' | grep URL_PUBLICO | cut -d'=' -f2)

# 3. Comparar y actuar
if [ "$NUEVA_URL" != "$URL_ACTUAL" ]; then
    echo "$(date): URL distinta detectada. Actualizando a: $NUEVA_URL"
    # Ejecutamos el comando usando la ruta absoluta y el archivo yml específico
    export URL_PUBLICO=$NUEVA_URL
    $DOCKER_COMPOSE -f $PROYECTO_DIR/docker-compose.yml up -d radar-bot
else
    echo "$(date): La URL no ha cambiado. Todo en orden."
fi
