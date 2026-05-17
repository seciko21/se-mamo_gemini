#!/usr/bin/env python3
"""
Script de prueba real para radar RC50
Prueba diferentes métodos para obtener velocidades reales
"""
import socket
import time
import sys
import struct

RADAR_IP = '192.168.4.152'
RADAR_PORT = 3000

def test_method_1():
    """Método 1: Comando 0xfcfa0200 (dio velocidad 6)"""
    print("\n" + "="*60)
    print("MÉTODO 1: Comando 0xfcfa0200")
    print("="*60)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((RADAR_IP, RADAR_PORT))
        time.sleep(0.5)
        
        # Enviar comando que antes dio resultado
        sock.sendall(b'\xfc\xfa\x02\x00')
        print("Comando enviado: 0xfcfa0200")
        
        time.sleep(1)
        sock.settimeout(1)
        
        start = time.time()
        velocidades = []
        
        while time.time() - start < 20:
            try:
                data = sock.recv(1024)
                if data:
                    for i in range(0, len(data)-3, 4):
                        pkt = data[i:i+4]
                        if len(pkt) == 4:
                            speed = pkt[2]
                            if speed > 0 and speed < 255:
                                velocidades.append(speed)
                                ts = time.strftime('%H:%M:%S')
                                dir_str = "ENTRADA" if pkt[:2] == b'\xfc\xfa' else "SALIDA"
                                print(f"  [{ts}] {dir_str}: {speed} km/h")
            except socket.timeout:
                continue
        
        sock.close()
        
        if velocidades:
            print(f"\n✅ Velocidades detectadas: {velocidades}")
            print(f"   Promedio: {sum(velocidades)/len(velocidades):.1f} km/h")
            return True
        else:
            print("\n❌ Sin velocidades válidas")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_method_2():
    """Método 2: Mantener conexión activa y leer continuamente"""
    print("\n" + "="*60)
    print("MÉTODO 2: Conexión persistente + comandos periódicos")
    print("="*60)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((RADAR_IP, RADAR_PORT))
        sock.settimeout(1)
        
        # Limpiar buffer inicial
        time.sleep(0.5)
        try:
            sock.recv(4096)
        except:
            pass
        
        velocidades = []
        start = time.time()
        cmd_count = 0
        
        while time.time() - start < 30:
            # Enviar comando periódicamente
            sock.sendall(b'\xfc\xfa\x02\x00')
            cmd_count += 1
            
            time.sleep(0.5)
            
            # Leer respuesta
            try:
                data = sock.recv(4096)
                if data:
                    for i in range(0, len(data)-3, 4):
                        pkt = data[i:i+4]
                        if len(pkt) == 4:
                            speed = pkt[2]
                            if 1 <= speed <= 250:
                                velocidades.append(speed)
                                ts = time.strftime('%H:%M:%S')
                                print(f"  [{ts}] Comando #{cmd_count} - Vel: {speed} km/h")
            except socket.timeout:
                pass
            
            time.sleep(0.5)
        
        sock.close()
        
        print(f"\n📊 Resultados:")
        print(f"   Comandos enviados: {cmd_count}")
        print(f"   Velocidades válidas: {len(velocidades)}")
        if velocidades:
            print(f"   Valores: {velocidades}")
            print(f"   Promedio: {sum(velocidades)/len(velocidades):.1f} km/h")
            return True
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_method_3():
    """Método 3: Prueba de que el radar esté configurado"""
    print("\n" + "="*60)
    print("MÉTODO 3: Verificación de configuración del radar")
    print("="*60)
    print()
    print("El radar RC50 puede necesitar configuración adicional:")
    print("  1. Modo de transmisión TCP/IP habilitado")
    print("  2. Umbral de velocidad configurado")
    print("  3. Detección de vehículos activa")
    print()
    print("Posibles comandos a probar:")
    
    test_cmds = [
        b'\xfc\xfa\x01\x00',
        b'\xfc\xfa\x02\x00', 
        b'\xfc\xfa\x03\x00',
        b'\xfc\xfa\x00\x01',
    ]
    
    for cmd in test_cmds:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((RADAR_IP, RADAR_PORT))
            time.sleep(0.3)
            
            sock.sendall(cmd)
            time.sleep(1)
            
            data = b''
            try:
                data = sock.recv(1024)
            except:
                pass
            
            sock.close()
            
            speeds = []
            for i in range(0, len(data)-3, 4):
                pkt = data[i:i+4]
                if len(pkt) == 4:
                    s = pkt[2]
                    if 1 <= s <= 250:
                        speeds.append(s)
            
            print(f"  Comando 0x{cmd.hex()}: {len(speeds)} velocidades válidas")
            if speeds:
                print(f"    → {speeds}")
                
        except Exception as e:
            print(f"  Comando 0x{cmd.hex()}: Error - {e}")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔍 PRUEBAS DE LECTURA REAL RC50")
    print("="*60)
    
    # Método 1
    r1 = test_method_1()
    
    if not r1:
        # Método 2
        r2 = test_method_2()
        
        if not r2:
            # Método 3
            test_method_3()
    
    print("\n" + "="*60)
    print("📌 CONCLUSIÓN")
    print("="*60)
    print("""
Si el radar no devuelve velocidades reales, posibles causas:

1. 🚗 No hay vehículos pasando por la zona de medición
2. ⚙️ El radar necesita configuración (modo TCP/IP, umbrales)
3. 🔌 Problema de alimentación o hardware
4. 📡 Interferencia o mal apuntamiento del radar
5. 🛠️ El radar está en modo mantenimiento/prueba

Recomendaciones:
- Verificar que haya tráfico real en la zona
- Usar software de configuración del fabricante
- Revisar manual del RC50 para comandos específicos
- Probar apuntando a una vía con tráfico constante
- Consultar logs: docker logs radar_monitor
    """)
    print("="*60)
