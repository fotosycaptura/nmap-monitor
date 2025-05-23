# Nmap Monitor

**Nmap Monitor** es un sistema automatizado de escaneos Nmap desarrollado en Python, pensado para ejecutarse de forma continua desde una Raspberry Pi u otro servidor. Lee un archivo CSV con objetivos de escaneo, ejecuta los análisis en segundo plano, guarda reportes y evita repetir escaneos ya realizados.

Esto nació como una solución para poder dejar realizando labores de escaneo mientras duermo o estoy fuera o imposibilitado de realizar el escaneo desde la red en la que me encuentro, entonces me conecto a mi raspberry mediante la nube y dejo el sitio que quiero escanear.

---

## Estructura del proyecto

/var/opt/nmap-monitor/
├── nmap_monitor.py # Script principal
├── sitios.csv # Sitios a escanear (CSV con columnas sitio;escaneado)
├── reportes/ # Resultados Nmap por sitio
├── locks/ # Archivos .lock para evitar duplicados
└── nmapmonitor.service # Servicio systemd


---

## Requisitos

- Python 3.6+
- `nmap` instalado (`sudo apt install nmap`)
- Permisos de root si se usan opciones avanzadas (-A, -p 443, etc.)
- Sistema de archivos Linux (ext4 o similar, no FAT/NTFS)

---

## Instalación y configuración

1. Clona o copia este proyecto en tu Raspberry Pi:

```bash
   cd /var/opt/
   git clone https://github.com/fotosycaptura/nmap-monitor.git
```

2. Edita el archivo sitios.csv:

```csv
sitio;escaneado
scanme.nmap.org;False
192.168.1.1;False
```

3. Asegúrate de que las carpetas tengan los permisos correctos:

```bash
sudo chown -R root:root /var/opt/nmap-monitor
```

4. Instala el servicio systemd:

```bash
sudo cp /var/opt/nmap-monitor/nmapmonitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable nmapmonitor
sudo systemctl start nmapmonitor
```
 
# ¿Cómo funciona?

- El script revisa el archivo sitios.csv cada 60 segundos.
- Si encuentra un sitio con escaneado=False y sin archivo .lock, ejecuta un escaneo Nmap.
- Al finalizar, guarda el reporte en reportes/ y actualiza el CSV.
- Se usa .lock por sitio para evitar escaneos duplicados o concurrentes.

# Seguridad

Este servicio se ejecuta como root para permitir escaneos avanzados con Nmap. Asegúrate de que el contenido del archivo sitios.csv sea controlado y no contenga dominios o direcciones no confiables.

# Archivos clave

- nmap_monitor.py: script principal del monitor.
- sitios.csv: lista de objetivos. Formato sitio;escaneado
- reportes/: guarda los resultados de cada escaneo.
- locks/: guarda .lock mientras el escaneo está en curso.
- nmapmonitor.service: archivo systemd para lanzar el script al inicio.

# Ejecución manual (para pruebas)

```bash
sudo python3 /var/opt/nmap-monitor/nmap_monitor.py
```

# Estado del servicio

```bash
sudo systemctl status nmapmonitor
```

# Contacto

Este proyecto fue desarrollado para uso personal en contextos de ciberseguridad. Puedes modificarlo y adaptarlo según tus necesidades.
Puedes dejarme igual tus recomendaciones, siempre son bienvenidas las retroalimentaciones.