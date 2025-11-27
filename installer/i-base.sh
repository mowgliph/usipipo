#!/bin/bash
set -e

# Actualizar sistema y dependencias básicas
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
apt-get install -y curl wget git ufw iptables-persistent netfilter-persistent

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
adduser --disabled-password --gecos "" vpnuser
usermod -aG sudo vpnuser
mkdir -p /home/vpnuser/{wireguard,outline,pihole}
chown -R vpnuser:vpnuser /home/vpnuser

echo "✅ Instalación base completada"
