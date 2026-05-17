#!/usr/bin/env python3
"""
RC50 Radar Fix Script
Diagnoses and applies fixes for RC50 not sending speed data
"""
import socket
import time
import sqlite3
import json
import os
from datetime import datetime

RADAR_IP = '192.168.4.152'
RADAR_PORT = 3000
RADAR_NAME = 'RC50'
DB_FILE = '/mnt/darat/data/cola_mensajes.db'
RADARES_FILE = '/mnt/darat/data/radares.json'

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def step_1_diagnose():
    """Diagnose current RC50 state"""
    print_header("STEP 1: Diagnose RC50 State")
    
    # Check DB
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*), AVG(velocidad), MAX(velocidad) FROM historial WHERE radar=?",
            (RADAR_NAME,)
        )
        count, avg, maxv = cursor.fetchone()
        conn.close()
        
        print(f"📊 Database records for {RADAR_NAME}:")
        print(f"   Total: {count or 0}")
        print(f"   Average speed: {avg or 0:.1f} km/h")
        print(f"   Max speed: {maxv or 0} km/h")
    except Exception as e:
        print(f"   ❌ DB error: {e}")
    
    # Check TCP connection
    print(f"\n🔌 Testing TCP connection to {RADAR_IP}:{RADAR_PORT}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        start = time.time()
        sock.connect((RADAR_IP, RADAR_PORT))
        elapsed = time.time() - start
        print(f"   ✅ Connected in {elapsed:.3f}s")
        
        # Check for keepalives
        sock.settimeout(2)
        time.sleep(0.5)
        data = sock.recv(1024)
        if data:
            packets = len(data) // 4
            speeds = [data[i+2] for i in range(0, len(data)-3, 4)]
            unique_speeds = set(speeds)
            print(f"   📦 Received {packets} packets")
            print(f"   Speed values: {unique_speeds}")
            
            if unique_speeds == {0}:
                print("   ⚠️  ONLY KEEPALIVES (speed=0)")
        
        sock.close()
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    return True

def step_2_send_commands():
    """Send RC50-specific initialization commands"""
    print_header("STEP 2: Send RC50 Initialization Commands")
    
    # RC50 command set
    commands = [
        (b'\xfc\xfa\x01\x00', 'Start transmission'),
        (b'\xfc\xfa\x02\x00', 'Enable speed output'),
        (b'\xfc\xfa\x03\x01', 'Vehicle detection mode'),
        (b'\xfc\xfa\x10\x00', 'Enable vehicle classification'),
        (b'\xfc\xfa\x20\x00', 'Enable TCP streaming'),
        (b'\xfc\xfa\x40\x00', 'Disable keepalive-only mode'),
    ]
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((RADAR_IP, RADAR_PORT))
        print("✅ Connected to RC50")
        time.sleep(0.5)
        
        # Clear buffer
        try:
            sock.recv(4096)
        except:
            pass
        
        for cmd, desc in commands:
            sock.sendall(cmd)
            cmd_hex = cmd.hex().upper()
            print(f"   📤 {desc}: 0x{cmd_hex}")
            time.sleep(0.5)
        
        # Wait and listen for responses
        print("\n   ⏳ Waiting for responses (10s)...")
        sock.settimeout(2)
        start = time.time()
        speeds_detected = []
        
        while time.time() - start < 10:
            try:
                data = sock.recv(1024)
                if data:
                    for i in range(0, len(data)-3, 4):
                        pkt = data[i:i+4]
                        if len(pkt) == 4:
                            speed = pkt[2]
                            if 1 <= speed <= 250:
                                speeds_detected.append(speed)
                                ts = datetime.now().strftime('%H:%M:%S')
                                print(f"   ✅ [{ts}] Speed: {speed} km/h")
            except socket.timeout:
                continue
        
        sock.close()
        
        if speeds_detected:
            print(f"\n🎉 SUCCESS! Detected {len(speeds_detected)} speeds")
            print(f"   Values: {speeds_detected}")
            return True
        else:
            print(f"\n⚠️  No real speeds detected")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def step_3_update_config():
    """Update RC50 configuration in radares.json"""
    print_header("STEP 3: Update RC50 Configuration")
    
    try:
        # Load existing
        if os.path.exists(RADARES_FILE):
            with open(RADARES_FILE, 'r') as f:
                radares = json.load(f)
        else:
            radares = {}
        
        # Update RC50
        radares[RADAR_NAME] = {
            "ip": RADAR_IP,
            "puerto": RADAR_PORT,
            "tipo": "RC50",
            "umbral": 50,
            "ultima_actualizacion": datetime.now().isoformat()
        }
        
        # Save
        os.makedirs(os.path.dirname(RADARES_FILE), exist_ok=True)
        with open(RADARES_FILE, 'w') as f:
            json.dump(radares, f, indent=2)
        
        print(f"✅ Updated {RADARES_FILE}")
        print(f"   RC50 config: {json.dumps(radares[RADAR_NAME], indent=2)}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def step_4_update_monitor():
    """Update monitor_radar.py with RC50 initialization"""
    print_header("STEP 4: Update Monitor for RC50 Support")
    
    monitor_file = '/root/se-mamo_gemini/radar_proyecto/app/monitor_radar.py'
    
    try:
        with open(monitor_file, 'r') as f:
            content = f.read()
        
        # Check if already modified
        if 'enviar_comando_inicial' in content:
            print("⚠️  Monitor already has RC50 init support")
            return True
        
        # Add initialization function after imports
        init_func = '''
def enviar_comando_inicial(sock, nombre_radar):
    """Enviar comandos de inicialización específicos por radar"""
    comandos = {
        'RC50': [
            b'\\xfc\\xfa\\x01\\x00',
            b'\\xfc\\xfa\\x02\\x00',
            b'\\xfc\\xfa\\x10\\x00',
        ],
        'RC21': [
            b'\\xfc\\xfa\\x01\\x00',
        ]
    }
    if nombre_radar in comandos:
        for cmd in comandos[nombre_radar]:
            try:
                sock.sendall(cmd)
                time.sleep(0.3)
            except:
                pass
'''
        
        # Find the escuchar_radar function and add call
        if 'def escuchar_radar' in content:
            # Insert init function before escuchar_radar
            insert_pos = content.find('def escuchar_radar')
            content = content[:insert_pos] + init_func + '\n' + content[insert_pos:]
            
            # Add call after connection
            old_connect = 'print(f"✅ [SOCKET] Conectado a {nombre}")'
            new_connect = old_connect + '\n                enviar_comando_inicial(s, nombre)'
            content = content.replace(old_connect, new_connect)
            
            # Write back
            with open(monitor_file, 'w') as f:
                f.write(content)
            
            print(f"✅ Updated {monitor_file}")
            print("   - Added enviar_comando_inicial()")
            print("   - Called in escuchar_radar()")
            return True
        else:
            print("⚠️  Could not find escuchar_radar function")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def step_5_test():
    """Test RC50 after fixes"""
    print_header("STEP 5: Test RC50")
    
    print("⏳ Monitoring RC50 for 15 seconds...\n")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((RADAR_IP, RADAR_PORT))
        
        # Send init commands
        sock.sendall(b'\xfc\xfa\x01\x00')
        sock.sendall(b'\xfc\xfa\x02\x00')
        time.sleep(0.5)
        
        # Listen
        sock.settimeout(1)
        start = time.time()
        speeds = []
        
        while time.time() - start < 15:
            try:
                data = sock.recv(1024)
                if data:
                    for i in range(0, len(data)-3, 4):
                        pkt = data[i:i+4]
                        if len(pkt) == 4:
                            sp = pkt[2]
                            if 1 <= sp <= 250:
                                speeds.append(sp)
                                ts = datetime.now().strftime('%H:%M:%S')
                                print(f"   ✅ [{ts}] Speed: {sp} km/h")
            except socket.timeout:
                continue
        
        sock.close()
        
        print(f"\n📊 Results: {len(speeds)} speeds detected")
        if speeds:
            print(f"   Values: {speeds}")
            print(f"   Average: {sum(speeds)/len(speeds):.1f} km/h")
            return True
        else:
            print("   ❌ No speeds detected")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  🔧 RC50 RADAR FIX SCRIPT")
    print("="*60)
    
    # Run all steps
    results = []
    
    results.append(("Diagnose", step_1_diagnose()))
    results.append(("Send Commands", step_2_send_commands()))
    results.append(("Update Config", step_3_update_config()))
    results.append(("Update Monitor", step_4_update_monitor()))
    results.append(("Test", step_5_test()))
    
    # Summary
    print_header("SUMMARY")
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {name}")
    
    all_ok = all(s for _, s in results)
    if all_ok:
        print("\n🎉 RC50 is now working!")
    else:
        print("\n⚠️  Some steps failed. Check:")
        print("   - Physical traffic presence")
        print("   - Radar power/connection")
        print("   - Manual: instrucciones_diagnostico_rc50.md")
    
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
PYEOF
chmod +x /root/se-mamo_gemini/fix_rc50.py
echo "Fix script created: fix_rc50.py"
