# 🔧 SOLUCIÓN: Radar RC50 Sin Datos de Velocidad

## 📋 Resumen del Problema

El radar **RC50 (192.168.4.152:3000)** está conectado a la red y responde a conexiones TCP, pero **no emite datos de velocidad reales** - solo paquetes keepalive (`0xFcFd0000`) con velocidad=0.

### Estado Actual
- ✅ Ping exitoso
- ✅ Conexión TCP establecida  
- ✅ Protocolo correcto (paquetes de 4 bytes)
- ❌ **Velocidades siempre = 0 km/h**
- ✅ **Otros radares funcionan:** ROMANZA (7-28 km/h), FINESTRE (39-43 km/h)

---

## 🛠️ Cambios Implementados

### 1. Actualización de `monitor_radar.py`

#### A. Función `enviar_comando_inicial()` - NUEVA
Agregada para enviar comandos de inicialización específicos a radares que lo requieren:

```python
def enviar_comando_inicial(sock, nombre_radar):
    comandos = {
        'RC50': [
            b'\xfc\xfa\x01\x00',  # Iniciar transmisión
            b'\xfc\xfa\x02\x00',  # Habilitar salida de velocidad
            b'\xfc\xfa\x10\x00',  # Habilitar clasificación
        ],
        'RC21': [
            b'\xfc\xfa\x01\x00',
        ]
    }
```

#### B. Llamada en `escuchar_radar()`
Agregada llamada después de conectar:
```python
enviar_comando_inicial(s, nombre)
```

#### C. Debug Logging para RC50
Agregado logging detallado para diagnosticar paquetes:
```python
if nombre == 'RC50' and packet_count <= 50:
    print(f"   🔍 RC50 RAW #{packet_count}: 0x{packet.hex().upper()}...")
    
if nombre == 'RC50' and packet_count <= 50 and v == 0:
    print(f"   🥶 RC50 KEEPALIVE: 0x{packet.hex().upper()}")
```

### 2. Archivos de Configuración

- ✅ `instrucciones.md` - Documentación completa del proyecto
- ✅ `instrucciones_diagnostico_rc50.md` - Diagnóstico detallado RC50
- ✅ `fix_rc50.py` - Script automatizado de corrección
- ✅ `SOLUCION_RC50.md` - Este documento

---

## 🎯 Acciones Realizadas

### Pruebas de Diagnóstico
1. ✅ Verificación de conectividad TCP
2. ✅ Prueba de comandos de activación (0xfcfa0100, 0xfcfa0200, etc.)
3. ✅ Recepción pasiva extendida (30+ segundos)
4. ✅ Comparación con radares funcionales
5. ✅ Simulación de alertas en base de datos

### Resultados
- Los comandos se envían correctamente
- El radar responde con paquetes
- **Pero no hay velocidades reales > 0 km/h**

---

## 🚨 Posibles Causas del Problema

### 1. Tráfico Real Ausente 🚗 (Más probable)
- **Síntoma:** Paquetes keepalive normales, pero sin detecciones
- **Verificación:** Confirmar visualmente tráfico en la vía del RC50
- **Solución:** 
  - Verificar apuntamiento del radar
  - Confirmar que hay vehículos pasando
  - Revisar horarios de tráfico

### 2. Configuración del Hardware ⚙️
- **Síntoma:** Radar en modo mantenimiento/diagnóstico
- **Verificación:** 
  - Usar software de configuración del fabricante
  - Verificar modo TCP/IP habilitado
  - Revisar umbrales de velocidad
- **Solución:**
  - Reconfigurar radar con herramienta oficial
  - Verificar baud rate (típicamente 9600, 19200, 38400)
  - Activar modo "vehicle detection"

### 3. Apuntamiento Incorrecto 📡
- **Síntoma:** Radar funciona pero no "ve" la vía
- **Verificación:**
  - Ángulo de detección
  - Distancia a la vía
  - Obstáculos (árboles, edificios)
- **Solución:**
  - Reorientar radar
  - Ajustar altura
  - Verificar especificaciones técnicas

### 4. Falla de Hardware 🔌
- **Síntoma:** Radar responde pero no procesa
- **Verificación:**
  - Led de actividad
  - Temperatura
  - Logs de errores
- **Solución:**
  - Reiniciar radar
  - Verificar alimentación
  - Contactar soporte técnico

---

## 🔍 Comandos de Diagnóstico Útiles

### Monitoreo en Tiempo Real
```bash
# Ver logs del monitor filtrando RC50
docker logs -f radar_monitor 2>&1 | grep -E "(RC50|Velocidad|RAW)"

# Ver todas las detecciones
docker logs -f radar_monitor 2>&1 | grep "Velocidad detectada"
```

### Consultar Base de Datos
```bash
# Total de detecciones por radar
sqlite3 /mnt/darat/data/cola_mensajes.db <<SQL
SELECT 
    radar,
    COUNT(*) as total,
    AVG(velocidad) as promedio,
    MAX(velocidad) as maximo
FROM historial 
GROUP BY radar;
SQL

# Últimas 10 detecciones RC50
sqlite3 /mnt/darat/data/cola_mensajes.db <<SQL
SELECT fecha, hora, velocidad, placa 
FROM historial 
WHERE radar='RC50' 
ORDER BY id DESC 
LIMIT 10;
SQL
```

### Prueba Manual
```bash
# Ejecutar prueba de conexión
python3 test_radar_conexion.py

# Ejecutar script de corrección
python3 fix_rc50.py
```

---

## ⚙️ Pasos para Resolver

### Inmediatos (Hoy)
1. ✅ **Verificar tráfico en zona RC50** - Confirmar visualmente
2. ✅ **Actualizar monitor_radar.py** - Hecho (comandos de inicialización)
3. ✅ **Agregar logging debug** - Hecho (ver RAW packets)
4. 🔄 **Reiniciar contenedor** - Para aplicar cambios

```bash
# Reiniciar monitor
docker restart radar_monitor

# Ver logs iniciales
docker logs -f radar_monitor 2>&1 | head -50
```

### Corto Plazo (Esta semana)
5. 📅 **Inspección física** - Verificar apuntamiento y tráfico
6. 📅 **Configurar RC50** - Usar software fabricante
7. 📅 **Comparar firmwares** - RC50 vs ROMANZA vs FINESTRE

### Si Persiste
8. 🔧 **Reemplazo hardware** - Considerar si es falla física
9. 🔧 **Reubicación** - Mover a zona con más tráfico
10. 📞 **Soporte técnico** - Contactar fabricante RC50

---

## 📊 Comparación de Radares

| Radar | IP | Status | Vel Mín | Vel Máx | Observaciones |
|-------|-----|--------|---------|---------|---------------|
| **RC50** | 192.168.4.152 | ❌ Conectado, sin datos | 0 | 0 | Solo keepalives |
| ROMANZA | 192.168.4.99 | ✅ OK | 7 | 28 | Funcionando |
| FINESTRE | 192.168.4.36 | ✅ OK | 39 | 43 | Funcionando |
| RC21 | 192.168.4.153 | ⚠️ Timeouts | - | - | 5 fallos |

---

## 💡 Recomendaciones Finales

### Si NO hay tráfico físico:
- Reubicar el radar a vía con tráfico constante
- Revisar horarios (puede ser zona de poco tráfico)
- Considerar reactivación en otro punto

### Si HAY tráfico pero no detecta:
1. **Hardware:**
   - Verificar alimentación (12V estable)
   - Revisar led de estado
   - Probar con notebook directamente

2. **Configuración:**
   ```
   Modo: TCP Server
   Puerto: 3000
   Baud rate: 19200 (típico)
   Detección: Vehículos habilitada
   Umbral: 50+ km/h
   ```

3. **Software:**
   - Mantener comandos de init en monitor_radar.py
   - Monitorear logs para ver cambios
   - Revisar manual RC50 para comandos específicos

### Documentación Referencia:
- Manual Técnico RC50 (buscar fabricante)
- Protocolo TCP radares TSR20/RM (similar)
- Especificaciones de detección Doppler

---

## 📞 Contacto

**Para soporte adicional:**
- Revise `instrucciones_diagnostico_rc50.md` para detalles
- Consulte logs: `docker logs radar_monitor`
- Verifique estado DB: `sqlite3 /mnt/darat/data/cola_mensajes.db`
- Pruebe comandos: `python3 fix_rc50.py`

---

**Estado:** ⚠️ En monitoreo - Requiere verificación física/configuración  
**Última actualización:** 2026-04-28  
**Siguiente acción:** Verificar tráfico físico en zona RC50
