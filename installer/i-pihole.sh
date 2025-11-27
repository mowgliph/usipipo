#!/bin/bash
set -e

# Variables de configuración
PIHOLE_IP="10.10.10.1"  # IP interna para Pi-hole
PIHOLE_PORT="53"
ADMIN_PASS=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 20)

# Instalar Pi-hole en modo no interactivo
export PIHOLE_INTERFACE="wg0"  # WireGuard interface
export PIHOLE_IPV4="${PIHOLE_IP}/24"
export PIHOLE_DNS_1="1.1.1.1"
export PIHOLE_DNS_2="8.8.8.8"
export WEB_PORT="80"
export ADMIN_EMAIL="usipipo@etlgr.com"
export WEBPASSWORD="${ADMIN_PASS}"

curl -sSL https://install.pi-hole.net | bash /dev/stdin --unattended

# Configurar Pi-hole para bloquear anuncios en todas las interfaces VPN
cat > /etc/dnsmasq.d/99-custom.conf <<EOF
interface=wg0
interface=docker0
bind-interfaces
EOF

# Reiniciar servicios
systemctl restart pihole-FTL
systemctl restart lighttpd

# Guardar credenciales
echo "PIHOLE_WEBPASS=${ADMIN_PASS}" >> /home/vpnuser/credentials.env
echo "PIHOLE_DNS=${PIHOLE_IP}" >> /home/vpnuser/credentials.env

echo -e "\n\n✅ Pi-hole instalado"
echo "IP Interna: ${PIHOLE_IP}"
echo "Contraseña Web: ${ADMIN_PASS}"
echo "Acceso Web: http://$(hostname -I | awk '{print $1}')/admin"
