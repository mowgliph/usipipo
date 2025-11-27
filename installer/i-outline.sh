#!/bin/bash
set -e

# Cargar variables del entorno
if [ -f /home/vpnuser/credentials.env ]; then
    source /home/vpnuser/credentials.env
else
    echo "❌ Error: No se encontró el archivo de credenciales"
    exit 1
fi

# Asegurar que Docker está instalado
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    usermod -aG docker vpnuser
    systemctl enable docker
    systemctl start docker
    rm get-docker.sh
fi

# Instalar Outline Server
sudo -u vpnuser bash <<EOF
docker volume create outline_persist
docker run -d --name outline-server \
  --restart unless-stopped \
  -v outline_persist:/var/lib/outline \
  -p 8080:8080/tcp \
  -p 9090:9090/udp \
  -e DNS_ADDR="${PIHOLE_DNS}" \
  ghcr.io/jigsaw-works/outline-server:stable
EOF

# Esperar a que el servidor esté listo
echo "⏳ Esperando a que Outline Server se inicie..."
sleep 30

# Obtener credenciales de Outline
if [ "$(docker inspect -f '{{.State.Running}}' outline-server)" != "true" ]; then
    echo "❌ Error: Outline Server no se inició correctamente"
    docker logs outline-server
    exit 1
fi

OUTLINE_API_URL=$(docker logs outline-server 2>&1 | grep -oP 'API URL: \Khttps?://[^ ]+')
OUTLINE_CERT_FINGERPRINT=$(docker logs outline-server 2>&1 | grep -oP 'SHA256 fingerprint: \K[^ ]+')

# Guardar credenciales
echo "OUTLINE_API_URL=${OUTLINE_API_URL}" >> /home/vpnuser/credentials.env
echo "OUTLINE_CERT_FINGERPRINT=${OUTLINE_CERT_FINGERPRINT}" >> /home/vpnuser/credentials.env

# Permitir puertos en firewall
ufw allow 8080/tcp
ufw allow 9090/udp
ufw reload

# Crear directorio para configuraciones
mkdir -p /home/vpnuser/VPNs_Configs/outline
chown -R vpnuser:vpnuser /home/vpnuser/VPNs_Configs

echo -e "\n\n✅ Outline instalado correctamente"
echo "API URL: ${OUTLINE_API_URL}"
echo "Cert Fingerprint: ${OUTLINE_CERT_FINGERPRINT}"
echo "Configuraciones de clientes se guardarán en: /home/vpnuser/VPNs_Configs/outline"
