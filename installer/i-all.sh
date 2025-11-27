#!/bin/bash
set -e

BASE_DIR=$(dirname "$0")
cd "$BASE_DIR"

# Ejecutar scripts en orden
chmod +x *.sh
./i-base.sh
./i-pihole.sh
./i-wireguard.sh
./i-outline.sh

# Permisos finales
chown -R vpnuser:vpnuser /home/vpnuser
chmod 600 /home/vpnuser/credentials.env

echo -e "\n\n🎉 INSTALACIÓN COMPLETADA"
echo "Credenciales guardadas en: /home/vpnuser/credentials.env"
echo "Reinicia el servidor para aplicar todos los cambios: sudo reboot"
