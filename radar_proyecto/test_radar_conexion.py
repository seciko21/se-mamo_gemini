#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la conexión TCP al radar de Bahías
"""
import socket
import time
from datetime import datetime

RADAR_IP = '192.168.4.152'
RADAR_PORT = 3000
TIMEOUT = 5

def test_radar_connection():
    print("=" * 60)
    print("DIAGNÓSTICO DE CONEXIÓN AL RADAR BAHÍAS")
    print("=" * 60)
    print(f"Target: {RADAR_IP}:{RADAR_PORT}")
    print()
    
    # Test 1: Conexión básica
    print("📡 Test 1: Conexión TCP básica...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        start_time = time.time()
        sock.connect((RADAR_IP, RADAR_PORT))
        elapsed = time.time() - start_time
        print(f"   ✅ CONEXIÓN EXITOSA ({elapsed:.2f}s)")
        
        # Test 2: Recibir datos
        print("\n📡 Test 2: Recibiendo datos del radar...")
        data_buffer = b""
        start_time = time.time()
        
        while time.time() - start_time < 10:  # 10 segundos de escucha
            try:
                sock.settimeout(2)
                data = sock.recv(1024)
                if data:
                    data_buffer += data
                    print(f"   📥 Recibidos {len(data)} bytes")
                    
                    # Procesar packets de 4 bytes
                    while len(data_buffer) >= 4:
                        packet = data_buffer[:4]
                        data_buffer = data_buffer[4:]
                        
                        print(f"   📦 Packet: {packet.hex()} | Raw: {packet}")
                        
                        # Verificar headers
                        if packet[:2] == b'\xfc\xfa':
                            speed = packet[2]
                            print(f"   🚗 ENTRADA: {speed} km/h")
                        elif packet[:2] == b'\xfb\xfd':
                            speed = packet[2]
                            print(f"   🚗 SALIDA: {speed} km/h")
                        else:
                            print(f"   ⚠️ Header desconocido: {packet[:2].hex()}")
                else:
                    print("   ⚠️ Conexión cerrada por el servidor")
                    break
            except socket.timeout:
                print("   ⏱️ Timeout (esperando más datos...)")
                break
        
        if not data_buffer:
            print("   ⚠️ No se recibieron datos en 10 segundos")
            print("   💡 Posibles causas:")
            print("      - El radar no está enviando datos")
            print("      - Hay un firewall bloqueando")
            print("      - El radar no está configurado para enviar datos TCP")
        
        sock.close()
        
    except socket.timeout:
        print(f"   ❌ TIMEOUT: No se pudo conectar en {TIMEOUT}s")
        print("   💡 Verificar:")
        print("      - La IP 192.168.4.152 es correcta")
        print("      - El puerto 3000 está abierto")
        print("      - No hay firewall bloqueando")
    except ConnectionRefusedError:
        print("   ❌ CONEXIÓN RECHAZADA")
        print("   💡 El servidor no está escuchando en ese puerto")
    except OSError as e:
        print(f"   ❌ ERROR DE RED: {e}")
    
    print("\n" + "=" * 60)
    print("FIN DEL DIAGNÓSTICO")
    print("=" * 60)

if __name__ == "__main__":
    test_radar_connection()
