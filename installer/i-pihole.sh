#!/bin/bash
set -e

# Variables de configuración
PIHOLE_IP="10.10.10.1"
PIHOLE_PORT="53"
ADMIN_PASS=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 20)

# Asegurar que lighttpd está instalado y funcionando
systemctl enable lighttpd
systemctl start lighttpd

# Prevenir conflictos con systemd-resolved
if systemctl is-active --quiet systemd-resolved; then
    systemctl stop systemd-resolved
    systemctl disable systemd-resolved
    rm -f /etc/resolv.conf
    echo "nameserver 1.1.1.1" > /etc/resolv.conf
fi

# Instalar Pi-hole en modo no interactivo
export PIHOLE_INTERFACE="eth0"
export PIHOLE_IPV4="0.0.0.0"
export PIHOLE_DNS_1="1.1.1.1"
export PIHOLE_DNS_2="8.8.8.8"
export PIHOLE_WEB_PORT="80"
export PIHOLE_DISABLE_IPV6="false"
export PIHOLE_INSTALL_WEB_SERVER="true"
export PIHOLE_WEBPASSWORD="${ADMIN_PASS}"

# Método seguro de instalación
curl -sSL https://install.pi-hole.net | bash /dev/stdin --unattended

# Forzar reinicio de servicios
systemctl restart lighttpd
systemctl restart pihole-FTL

# Configurar Pi-hole para bloquear anuncios en todas las interfaces VPN
mkdir -p /etc/dnsmasq.d
cat > /etc/dnsmasq.d/99-custom.conf <<EOF
interface=wg0
bind-interfaces
EOF

# Reiniciar servicios nuevamente
systemctl restart pihole-FTL
systemctl restart lighttpd

# Guardar credenciales
echo "PIHOLE_WEBPASS=${ADMIN_PASS}" >> /home/vpnuser/credentials.env
echo "PIHOLE_DNS=${PIHOLE_IP}" >> /home/vpnuser/credentials.env

# Verificar que el servicio web está funcionando
if ! curl -s --head http://localhost/admin | grep "200 OK" >/dev/null; then
    echo "⚠️ ADVERTENCIA: La interfaz web de Pi-hole podría no estar funcionando correctamente"
    echo "Verifica manualmente en http://$(hostname -I | awk '{print $1}')/admin"
fi

echo -e "\n\n✅ Pi-hole instalado correctamente"
echo "IP Interna: ${PIHOLE_IP}"
echo "Contraseña Web: ${ADMIN_PASS}"
echo "Acceso Web: http://$(hostname -I | awk '{print $1}')/admin"
