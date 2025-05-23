import csv
import os
import sys
import subprocess
import threading
import time

CSV_PATH = "/var/opt/nmap-monitor/sitios.csv"
OUTPUT_DIR = "/var/opt/nmap-monitor/reportes"
LOCK_DIR = "/var/opt/nmap-monitor/locks"
CHECK_INTERVAL = 60  # segundos

def asegurar_permisos_csv():
    try:
        stat_info = os.stat(CSV_PATH)
        propietario = pwd.getpwuid(stat_info.st_uid).pw_name
        if propietario != "nmapscan":
            os.system(f"sudo chown nmapscan:nmapscan {CSV_PATH}")
            os.system(f"sudo chmod +rw nmapscan:nmapscan {CSV_PATH}")
    except Exception as e:
        print(f"[!] No se pudo ajustar permisos del CSV: {e}")

def leer_opciones_nmap():
    with open("/var/opt/nmap-monitor/opciones.conf", "r") as f:
        line = f.readline().strip()
        return line.split()

def cargar_sitios():
    #asegurar_permisos_csv()
    with open(CSV_PATH, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        return list(reader)

def guardar_sitios(sitios):
    #asegurar_permisos_csv()
    with open(CSV_PATH, 'w', newline='') as csvfile:
        fieldnames = ['sitio', 'escaneado']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for sitio in sitios:
            writer.writerow(sitio)

def get_lock_path(sitio):
    nombre = sitio.replace("/", "_").replace(":", "_")
    return os.path.join(LOCK_DIR, f"{nombre}.lock")

def tiene_lock(sitio):
    return os.path.exists(get_lock_path(sitio))

def crear_lock(sitio):
    with open(get_lock_path(sitio), 'w') as f:
        f.write("en curso")

def eliminar_lock(sitio):
    os.remove(get_lock_path(sitio))

def escanear(sitio):
    print(f"[+] Escaneando {sitio}")
    crear_lock(sitio)

    output_file = os.path.join(OUTPUT_DIR, f"{sitio.replace('/', '_')}.txt")
    opciones = leer_opciones_nmap()
    comando = ["sudo", "nmap"] + opciones + [sitio, "-oN", output_file]
    subprocess.run(comando)

    sitios = cargar_sitios()
    for s in sitios:
        if s["sitio"] == sitio:
            s["escaneado"] = "True"
            break
    guardar_sitios(sitios)

    eliminar_lock(sitio)
    print(f"[✓] Escaneo terminado para {sitio}")

def monitor():
    while True:
        sitios = cargar_sitios()
        for sitio in sitios:
            if sitio["escaneado"].lower() == "false" and not tiene_lock(sitio["sitio"]):
                hilo = threading.Thread(target=escanear, args=(sitio["sitio"],))
                hilo.start()
        time.sleep(CHECK_INTERVAL)

def presentacion():
        print(f"******************************************************")
        print(f"               nmap monitor                         ")
        print(f"               Para escaneos desatendidos            ")
        print(f"               2025            ")
        print(f"Por @fotosycaptura                                    ")
        print(f"******************************************************")


if __name__ == "__main__":
    presentacion()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(LOCK_DIR, exist_ok=True)

    print("[*] Iniciando monitor de escaneos con locks...")
    try:
        monitor()
    except KeyboardInterrupt:
        print ('[!] Monitereo interrumpido')
        sys.exit(0)
