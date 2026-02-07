#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Radar TSR20 - Lector TCP/IP (Compatible Python 2.7)
Conexion al radar via TCP en puerto 3000

Configuracion:
- IP: 92.168.4.152
- Puerto: 3000
- Usuario: root
- Contrasena: mfmssmcl
"""

import socket
import time
from datetime import datetime
import sys
import os
import codecs

# --- Configuracion de Red ---
RADAR_IP = '192.168.4.152'
RADAR_PORT = 3000
CONNECTION_TIMEOUT = 10.0  # Segundos

# --- Credenciales ---
RADAR_USER = 'root'
RADAR_PASS = 'mfmssmcl'

# --- Configuracion de Logs ---
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'radar_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.log')

# Tamano del buffer antes de escribir al disco
LOG_BUFFER_SIZE = 20

# --- Protocolo del Radar ---
PACKET_SIZE = 4  # Bytes por paquete esperados
HEADER_IN = '\xFC\xFA'  # Direccion ENTRADA
HEADER_OUT = '\xFB\xFD'  # Direccion SALIDA
MIN_SPEED = 5  # km/h
MAX_SPEED = 255  # km/h

# --- Estado del Sistema ---
log_buffer = []
last_speed_was_valid = True
connection_status = "Desconectado"
reconnection_count = 0
data_buffer = ""  # Buffer para datos fragmentados


def create_log_directory():
    """Crea el directorio de logs si no existe."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print("[%s] Directorio de logs creado: %s" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LOG_DIR))


def log_message(message, to_buffer=True):
    """Escribe un mensaje con timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    formatted_msg = "[%s] %s\n" % (timestamp, message)
    
    # Imprimir en consola
    sys.stdout.write(formatted_msg)
    sys.stdout.flush()
    
    # Agregar al buffer
    if to_buffer:
        log_buffer.append(formatted_msg)
        
        # Escribir al archivo si el buffer esta lleno
        if len(log_buffer) >= LOG_BUFFER_SIZE:
            write_log_file()


def write_log_file():
    """Escribe el contenido del buffer al archivo de log."""
    global log_buffer
    if log_buffer:
        try:
            with codecs.open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.writelines(log_buffer)
            log_buffer = []
        except IOError as e:
            print("[%s] Error al escribir log: %s" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), e))


def connect_to_radar():
    """Establece conexion TCP con el radar."""
    global connection_status, reconnection_count
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(CONNECTION_TIMEOUT)
    
    try:
        log_message("Conectando a %s:%s..." % (RADAR_IP, RADAR_PORT))
        connection_status = "Conectando..."
        client_socket.connect((RADAR_IP, RADAR_PORT))
        connection_status = "Conectado"
        reconnection_count = 0
        log_message("+ Conexion exitosa al radar %s:%s" % (RADAR_IP, RADAR_PORT))
        return client_socket
    except socket.error as e:
        connection_status = "Error: %s" % e
        reconnection_count += 1
        log_message("- Error al conectar: %s (Intento #%d)" % (e, reconnection_count))
        client_socket.close()
        return None


def parse_packet(data_raw):
    """Analiza un paquete de datos del radar."""
    global last_speed_was_valid
    
    if len(data_raw) != PACKET_SIZE:
        return None
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
    # Determinar direccion
    if data_raw[0:2] == HEADER_IN:
        direction = "ENTRADA"
        direction_code = "IN"
    elif data_raw[0:2] == HEADER_OUT:
        direction = "SALIDA"
        direction_code = "OUT"
    else:
        # Verificar si es un paquete de datos alternativo
        if len(data_raw) >= 2:
            header_byte = ord(data_raw[0]) if isinstance(data_raw[0], str) else data_raw[0]
            if header_byte == 0xAA or header_byte == 0xFC or header_byte == 0xFB:
                # Podria ser un paquete con protocolo diferente
                pass
        return None
    
    # Extraer velocidad (byte 2)
    speed_value = ord(data_raw[2]) if isinstance(data_raw[2], str) else data_raw[2]
    
    # Validar velocidad
    if MIN_SPEED <= speed_value <= MAX_SPEED:
        last_speed_was_valid = True
        result = {
            'timestamp': timestamp,
            'direction': direction,
            'direction_code': direction_code,
            'speed': speed_value,
            'unit': 'km/h',
            'raw_data': data_raw.encode('latin-1').hex() if isinstance(data_raw, str) else data_raw.hex(),
            'valid': True
        }
        return result
    else:
        if last_speed_was_valid:
            log_message("Velocidad fuera de rango descartada: %s km/h" % speed_value)
            last_speed_was_valid = False
        return None


def print_speed_data(data):
    """Imprime los datos de velocidad formateados."""
    if data:
        direction_icon = "->" if data['direction_code'] == "OUT" else "<-"
        print("  %s  [%s] %8s | %3s km/h | RAW: %s" % (
            direction_icon, 
            data['timestamp'], 
            data['direction'], 
            data['speed'],
            data['raw_data']
        ))


def monitor_radar():
    """Funcion principal de monitoreo del radar."""
    global connection_status, data_buffer
    
    create_log_directory()
    
    log_message("=" * 60)
    log_message("INICIO - Monitor de Radar TSR20 TCP/IP")
    log_message("Servidor: %s:%s" % (RADAR_IP, RADAR_PORT))
    log_message("Usuario: %s" % RADAR_USER)
    log_message("=" * 60)
    
    client_socket = None
    
    try:
        while True:
            # Verificar/Establecer conexion
            if client_socket is None:
                data_buffer = ""  # Limpiar buffer al reconectar
                write_log_file()  # Vaciar buffer antes de reconectar
                client_socket = connect_to_radar()
                if client_socket is None:
                    log_message("Esperando 5 segundos antes de reintentar...")
                    time.sleep(5)
                    continue
            
            # Recibir datos
            try:
                data_raw = client_socket.recv(1024)  # Recibir hasta 1KB
                
                if not data_raw:
                    log_message("Conexion cerrada por el dispositivo remoto")
                    raise socket.error("Conexion remota cerrada")
                
                # Acumular datos en el buffer
                if isinstance(data_raw, bytes):
                    data_buffer += data_raw.decode('latin-1', errors='ignore')
                else:
                    data_buffer += data_raw
                
                # Procesar todos los paquetes completos en el buffer
                while len(data_buffer) >= PACKET_SIZE:
                    packet = data_buffer[:PACKET_SIZE]
                    data_buffer = data_buffer[PACKET_SIZE:]
                    
                    # Procesar paquete
                    result = parse_packet(packet)
                    if result:
                        print_speed_data(result)
                        # Agregar al buffer de log
                        log_buffer.append("%s,%s,%s\n" % (result['timestamp'], result['direction_code'], result['speed']))
                        
                        # Escribir si buffer lleno
                        if len(log_buffer) >= LOG_BUFFER_SIZE:
                            write_log_file()
                            
                # Log de datos incompletos solo si hay datos en buffer
                remaining = len(data_buffer)
                if remaining > 0 and remaining < PACKET_SIZE:
                    pass  # No loggear, estamos acumulando
                    
            except socket.timeout:
                # Limpiar buffer si hay datos incompletos y timeout
                if len(data_buffer) > 0:
                    log_message("Timeout - Buffer acumulado: %d bytes, datos: %s" % (len(data_buffer), data_buffer.encode('hex')[:20] if isinstance(data_buffer, str) else data_buffer[:20].hex()))
                    data_buffer = ""
                continue
                
            except socket.error as e:
                log_message("Error de conexion: %s" % e)
                if client_socket:
                    client_socket.close()
                client_socket = None
                connection_status = "Desconectado"
                data_buffer = ""
                time.sleep(2)
                
    except KeyboardInterrupt:
        log_message("\nDetenido por el usuario (Ctrl+C)")
    except Exception as e:
        log_message("Error inesperado: %s" % e)
        import traceback
        log_message(traceback.format_exc())
    finally:
        if client_socket:
            client_socket.close()
        write_log_file()  # Escribir buffer restante
        log_message("Monitor de radar detenido")


def show_status():
    """Muestra el estado actual de la conexion."""
    print("\n" + "=" * 50)
    print("  ESTADO DEL RADAR TSR20")
    print("=" * 50)
    print("  Servidor:     %s:%s" % (RADAR_IP, RADAR_PORT))
    print("  Usuario:      %s" % RADAR_USER)
    print("  Estado:       %s" % connection_status)
    print("  Protocolo:    TCP/IP")
    print("  Buffer Log:  %d registros" % len(log_buffer))
    print("=" * 50 + "\n")


if __name__ == '__main__':
    show_status()
    monitor_radar()
