# Diagnóstico RC50 - Radar Sin Datos de Velocidad

## 🔍 Situación Actual

El radar **RC50 (192.168.4.152:3000)** está conectado y responde a peticiones TCP, pero **no emite datos de velocidad reales** (solo paquetes keepalive con velocidad=0).

### Evidencias:
- ✅ Ping exitoso al radar
- ✅ Conexión TCP establecida
- ✅ Paquetes recibidos (formato correcto: 4 bytes)
- ❌ Velocidades siempre = 0 km/h (paquetes keepalive `0xFcFd0000`)
- ❌ Comandos de activación no generan datos reales

### Comparación con otros radares:
- ✅ **ROMANZA (192.168.4.99)**: Detectando velocidades (7, 28 km/h)
- ✅ **FINESTRE (192.168.4.36)**: Detectando velocidades (39-43 km/h)
- ❌ **RC50 (192.168.4.152)**: Solo keepalives, sin velocidades
- ❌ **RC21 (192.168.4.153)**: Timeouts (5 fallos consecutivos)

## 📊 Resultados de Pruebas

### Prueba 1: Conexión TCP básica
```
Comando: 0xfcfa0200
Resultado: 5 paquetes recibidos, 0 velocidades válidas
```

### Prueba 2: Conexión persistente con comandos periódicos
```
Comandos enviados: 30 en 30 segundos
Velocidades válidas: 0
```

### Prueba 3: Recepción pasiva (30s)
```
Total packets: 62 (todos keepalive)
Velocidades >0: 0
```

### Desde contenedor Docker:
```
Conexión: OK
Comando: 0xfcfa0200
Velocidades válidas: []
```

## 🎯 Posibles Causas

### 1. Tráfico Real Ausente 🚗
- **Probabilidad**: Alta
- **Descripción**: No hay vehículos pasando por la zona de detección del radar
- **Verificación**: Confirmar visualmente que hay tráfico en la vía
- **Solución**: Esperar o verificar apuntamiento del radar

### 2. Configuración del Radar ⚙️
- **Probabilidad**: Media
- **Descripción**: El RC50 puede necesitar:
  - Modo TCP/IP habilitado en configuración
  - Umbral de velocidad configurado
  - Activación de transmisión continua
- **Verificación**: Revisar software de configuración del fabricante
- **Solución**: 
  - Usar herramienta de configuración RC50
  - Verificar manual: comandos específicos de activación
  - Revisar configuración de puerto serial/USB

### 3. Hardware / Alimentación 🔌
- **Probabilidad**: Baja-Media
- **Descripción**: Problema de alimentación o sensor defectuoso
- **Verificación**: 
  - Led de actividad del radar
  - Logs de errores de hardware
  - Temperatura del dispositivo

### 4. Apuntamiento / Instalación 📡
- **Probabilidad**: Media
- **Descripción**: Radar mal orientado o muy alejado de la vía
- **Verificación**: 
  - Ángulo de detección
  - Distancia a la vía
  - Obstáculos en el haz

### 5. Modo Mantenimiento 🛠️
- **Probabilidad**: Media
- **Descripción**: Radar en modo diagnóstico/prueba
- **Solución**: Reiniciar o reconfigurar

## 🔧 Acciones Recomendadas

### Inmediatas (Prioridad Alta):
1. ✅ **Verificar tráfico real** en la zona del RC50
   - Confirmar visualmente que hay vehículos
   - Verificar horarios de tráfico

2. ⚙️ **Revisar configuración del RC50**:
   ```bash
   # Conectarse al radar con software específico
   # Verificar:
   # - Modo de transmisión: TCP/IP habilitado
   # - Puerto: 3000
   # - Umbral: Configurado
   # - ID del radar: RC50
   ```

3. 🔄 **Reiniciar el radar**:
   - Desconectar/alimentar
   - Esperar 30 segundos
   - Reconectar y monitorear

### Corto Plazo (Prioridad Media):
4. 📡 **Verificar apuntamiento**:
   - Confirmar que apunta a la vía con tráfico
   - Revisar obstáculos
   - Verificar distancia óptima

5. 🔍 **Comparar con ROMANZA/FINESTRE**:
   - Misma configuración de red?
   - Mismo firmware?
   - Mismo hardware?

6. 📄 **Consultar manual RC50**:
   - Buscar comandos específicos de activación
   - Verificar protocolo TCP
   - Revisar configuración de baud rate

### Monitoreo Continuo:
7. 📈 **Monitoreo logs**:
   ```bash
   docker logs -f radar_monitor | grep RC50
   ```

8. 🔔 **Alertas**:
   - Configurar alerta si RC50 no reporta en 1 hora
   - Notificación por Telegram si estado = OFFLINE

## 📋 Comandos Útiles

### Monitoreo en tiempo real:
```bash
# Ver logs del monitor
docker logs -f radar_monitor | grep -E "(RC50|Velocidad)"

# Ver estado de todos los radares
python3 -c "from app.gestor_radares import RADARES; print(RADARES)"

# Probar conexión manual
python3 test_radar_conexion.py
```

### Consultar base de datos:
```bash
sqlite3 /mnt/darat/data/cola_mensajes.db
SELECT radar, COUNT(*) FROM historial WHERE radar='RC50' GROUP BY radar;
SELECT * FROM historial WHERE radar='RC50' ORDER BY fecha DESC LIMIT 10;
```

## 📞 Contacto Soporte

Si persiste el problema:
- Revisar manual técnico del RC50
- Contactar fabricante para comandos específicos
- Verificar garantía/soporte del hardware

## 📝 Notas Adicionales

- El sistema funciona correctamente con ROMANZA y FINESTRE
- RC21 también presenta problemas (timeouts)
- Podría ser problema de red física o configuración específica
- Considerar reemplazo/reubicación si persiste

---
**Última actualización**: 2026-04-28
**Estado**: En diagnóstico
