#!/bin/bash
set -e

# Cargar variables del entorno
source /home/vpnuser/credentials.env

# Variables
WG_INTERFACE="wg0"
WG_SUBNET="10.10.10.0/24"
WG_IP="10.10.10.1"
WG_PORT="51820"
SERVER_IP=$(curl -s ifconfig.me)
PIHOLE_IP=$(grep PIHOLE_DNS /home/vpnuser/credentials.env | cut -d= -f2)

# Instalar WireGuard y dependencias
apt-get install -y wireguard qrencode iptables-persistent netfilter-persistent

# Generar claves
umask 077
mkdir -p /etc/wireguard
wg genkey | tee /etc/wireguard/server_private.key | wg pubkey > /etc/wireguard/server_public.key
SERVER_PRIVATE_KEY=$(cat /etc/wireguard/server_private.key)
SERVER_PUBLIC_KEY=$(cat /etc/wireguard/server_public.key)

# Configurar interfaz
cat > /etc/wireguard/${WG_INTERFACE}.conf <<EOF
[Interface]
Address = ${WG_IP}/24
ListenPort = ${WG_PORT}
PrivateKey = ${SERVER_PRIVATE_KEY}
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE; ip6tables -A FORWARD -i %i -j ACCEPT; ip6tables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE; ip6tables -D FORWARD -i %i -j ACCEPT; ip6tables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
SaveConfig = false
EOF

chmod 600 /etc/wireguard/${WG_INTERFACE}.conf

# Habilitar y arrancar servicio
systemctl enable wg-quick@${WG_INTERFACE}
systemctl start wg-quick@${WG_INTERFACE}

# Configurar NAT para IPv4 e IPv6
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
ip6tables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
netfilter-persistent save

# Permitir en firewall
ufw allow ${WG_PORT}/udp
ufw reload

# Guardar información del servidor
echo "WG_SERVER_PUBLIC_KEY=${SERVER_PUBLIC_KEY}" >> /home/vpnuser/credentials.env
echo "WG_SERVER_ENDPOINT=${SERVER_IP}:${WG_PORT}" >> /home/vpnuser/credentials.env
echo "WG_DNS=${PIHOLE_IP}" >> /home/vpnuser/credentials.env

# Crear directorio para configuraciones de clientes
mkdir -p /home/vpnuser/VPNs_Configs/wireguard
chown -R vpnuser:vpnuser /home/vpnuser/VPNs_Configs

echo -e "\n\n✅ WireGuard instalado correctamente"
echo "Endpoint: ${SERVER_IP}:${WG_PORT}"
echo "Clave Pública: ${SERVER_PUBLIC_KEY}"
echo "Configuraciones de clientes se guardarán en: /home/vpnuser/VPNs_Configs/wireguard"
