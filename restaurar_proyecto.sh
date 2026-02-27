#!/bin/bash
# Script de restauración del proyecto Radar
# Uso: ./restaurar_proyecto.sh

BACKUP_FILE="${1:-/root/backups_python314/proyecto_radar_backup_20260226_192928.tar.gz}"

echo "========================================="
echo "  RESTAURACIÓN DEL PROYECTO RADAR"
echo "========================================="
echo ""

# Verificar que existe el backup
if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: No se encontró el archivo de backup: $BACKUP_FILE"
    exit 1
fi

# Confirmación
echo "Se restaurará desde: $BACKUP_FILE"
echo "ADVERTENCIA: Esto sobrescribirá cualquier cambio no guardado."
echo ""
read -p "¿Continuar? (s/n): " confirm

if [ "$confirm" != "s" ]; then
    echo "Restauración cancelada."
    exit 0
fi

# Restaurar el backup
echo ""
echo "Restaurando proyecto..."
cd /root || { echo "ERROR: No se pudo cambiar al directorio /root"; exit 1; }
tar -xzvf "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "  ✅ RESTAURACIÓN COMPLETADA"
    echo "========================================="
    echo ""
    echo "El proyecto ha sido restaurado a su estado anterior."
    echo "Ubicación: /root/se-mamo_gemini/"
else
    echo ""
    echo "ERROR: La restauración falló."
    exit 1
fi
