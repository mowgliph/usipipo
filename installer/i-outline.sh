#!/bin/bash
set -e

# Instalar Docker
curl -fsSL https://get.docker.com | sh
usermod -aG docker vpnuser

# Instalar Outline Server
sudo -u vpnuser bash -c '
docker volume create outline_persist
docker run -d --name outline-server \
  --restart always \
  -v outline_persist:/var/lib/outline \
  -p 8080:8080/tcp \
  -p 9090:9090/udp \
  -e DNS="${PIHOLE_DNS}" \
  ghcr.io/jigsaw-works/outline-server:stable
'

# Esperar a que el servidor esté listo
sleep 30

# Obtener credenciales de Outline
OUTLINE_API_URL=$(docker logs outline-server 2>&1 | grep -oP 'API URL: \K.*')
OUTLINE_CERT_FINGERPRINT=$(docker logs outline-server 2>&1 | grep -oP 'SHA256 fingerprint: \K.*')

# Guardar credenciales
echo "OUTLINE_API_URL=${OUTLINE_API_URL}" >> /home/vpnuser/credentials.env
echo "OUTLINE_CERT_FINGERPRINT=${OUTLINE_CERT_FINGERPRINT}" >> /home/vpnuser/credentials.env

# Permitir puertos en firewall
ufw allow 8080/tcp
ufw allow 9090/udp

echo -e "\n\n✅ Outline instalado"
echo "API URL: ${OUTLINE_API_URL}"
echo "Cert Fingerprint: ${OUTLINE_CERT_FINGERPRINT}"
