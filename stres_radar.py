import threading
import time
import os

# Configuración del Test
RADARES_PRUEBA = [
    ("BAHIAS", "192.168.4.152"),
    ("FINESTRE", "192.168.4.36"),
    ("ROMANZA", "192.168.4.99"),
    ("BAHIAS", "192.168.4.152"), # Repetimos para estresar
    ("FINESTRE", "192.168.4.36")
]

def disparar_deteccion(nombre, ip, velocidad):
    print(f"🚀 [TEST] Disparando detección: {nombre} a {velocidad} km/h...")
    # Ejecutamos la función directamente dentro del contenedor
    cmd = f"docker exec -d radar_monitor python3 -c 'from monitor_radar import procesar_deteccion; procesar_deteccion(\"{nombre}\", \"{ip}\", {velocidad})'"
    os.system(cmd)

def iniciar_ataque():
    print("🔥 Iniciando Test de Estrés sobre Clawdbot...")
    print("--------------------------------------------")
    threads = []
    
    for i, (nombre, ip) in enumerate(RADARES_PRUEBA):
        vel = 65 + (i * 5) # Velocidades de 65, 70, 75, 80, 85
        t = threading.Thread(target=disparar_deteccion, args=(nombre, ip, vel))
        threads.append(t)
        t.start()
        time.sleep(1) # Un segundo entre cada uno para no saturar el socket de golpe

    for t in threads:
        t.join()

    print("--------------------------------------------")
    print("✅ Ráfaga enviada. Revisa Telegram y los logs:")
    print("👉 docker logs -f radar_monitor")

if __name__ == "__main__":
    iniciar_ataque()
