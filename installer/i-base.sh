#!/bin/bash
set -e

echo "Actualizando sistema y dependencias básicas..."
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
apt-get install -y curl wget git ufw iptables-persistent netfilter-persistent \
    dnsutils lsof sudo unzip python3 python3-pip apache2-utils

# Instalar lighttpd para Pi-hole (crítico)
apt-get install -y lighttpd

# Configurar firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow http
ufw allow https
ufw --force enable

# Habilitar forwarding para VPNs
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
echo "net.ipv6.conf.all.forwarding=1" >> /etc/sysctl.conf
sysctl -p

# Crear usuario para servicios
if ! id "vpnuser" &>/dev/null; then
    adduser --disabled-password --gecos "" vpnuser
    usermod -aG sudo vpnuser
fi

mkdir -p /home/vpnuser/{wireguard,outline,pihole}
chown -R vpnuser:vpnuser /home/vpnuser

apt-get autoremove -y

echo "✅ Instalación base completada"
