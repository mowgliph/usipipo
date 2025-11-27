#!/bin/bash
set -e

# Directorio del proyecto
PROJECT_DIR=$(dirname "$0")
cd "$PROJECT_DIR"

# Generar contraseña segura para Pi-hole si no existe
if [ ! -f .env ]; then
    echo "Generando archivo de configuración .env..."
    PIHOLE_PASS=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 20)
    SERVER_IP=$(curl -s ifconfig.me)
    
    cat > .env <<EOF
# Configuración generada automáticamente para uSipipo VPN
PIHOLE_WEBPASS=${PIHOLE_PASS}
SERVER_IP=${SERVER_IP}
EOF
    echo "✅ Archivo .env creado con configuración inicial"
fi

# Cargar variables de entorno
source .env

# Iniciar los servicios Docker
echo "🚀 Iniciando servicios VPN en Docker..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios se inicien..."
sleep 30

# Obtener credenciales de WireGuard
echo "🔑 Obteniendo credenciales de WireGuard..."
DOCKER_WG_DIR=$(docker volume inspect wireguard_config --format '{{ .Mountpoint }}')
WG_CONFIG="${DOCKER_WG_DIR}/peer_bot_user/peer_bot_user.conf"

if [ ! -f "$WG_CONFIG" ]; then
    echo "❌ No se encontró la configuración de WireGuard. Reintentando..."
    sleep 10
    WG_CONFIG=$(find "${DOCKER_WG_DIR}" -name "peer_bot_user.conf" 2>/dev/null | head -1)
fi

if [ -f "$WG_CONFIG" ]; then
    SERVER_PUBLIC_KEY=$(grep "PublicKey" "${DOCKER_WG_DIR}/server/peer_bot_user/publickey" | tr -d '[:space:]')
    CLIENT_CONFIG=$(cat "$WG_CONFIG")
    
    echo "WG_SERVER_PUBLIC_KEY=${SERVER_PUBLIC_KEY}" > credentials.env
    echo "WG_SERVER_ENDPOINT=${SERVER_IP}:51820" >> credentials.env
    echo "WG_DNS=10.10.10.2" >> credentials.env
    echo "WG_CLIENT_CONFIG=$(echo "$CLIENT_CONFIG" | base64 -w0)" >> credentials.env
    echo "✅ Credenciales de WireGuard guardadas en credentials.env"
else
    echo "⚠️ Advertencia: No se pudo obtener la configuración de WireGuard"
fi

# Obtener credenciales de Outline
echo "🔑 Obteniendo credenciales de Outline..."
OUTLINE_API_URL=$(docker logs outline 2>&1 | grep -oP 'API URL: \Khttps?://[^ ]+')
OUTLINE_CERT_FINGERPRINT=$(docker logs outline 2>&1 | grep -oP 'SHA256 fingerprint: \K[^ ]+')

if [ -n "$OUTLINE_API_URL" ] && [ -n "$OUTLINE_CERT_FINGERPRINT" ]; then
    echo "OUTLINE_API_URL=${OUTLINE_API_URL}" >> credentials.env
    echo "OUTLINE_CERT_FINGERPRINT=${OUTLINE_CERT_FINGERPRINT}" >> credentials.env
    echo "✅ Credenciales de Outline guardadas en credentials.env"
else
    echo "⚠️ Advertencia: No se pudieron obtener las credenciales de Outline"
    echo "   Espera unos minutos y ejecuta: docker logs outline"
fi

# Obtener contraseña de Pi-hole
if [ -f "${DOCKER_WG_DIR}/../pihole/setupVars.conf" ]; then
    PIHOLE_WEBPASS=$(grep "WEBPASSWORD" "${DOCKER_WG_DIR}/../pihole/setupVars.conf" | cut -d= -f2)
    echo "PIHOLE_WEBPASS=${PIHOLE_WEBPASS}" >> credentials.env
    echo "PIHOLE_DNS=10.10.10.2" >> credentials.env
    echo "✅ Credenciales de Pi-hole guardadas en credentials.env"
fi

# Crear directorio para el bot
mkdir -p bot/credentials
cp credentials.env bot/credentials/credentials.env

# Mostrar información final
echo -e "\n🎉 SERVICIOS INICIADOS EXITOSAMENTE"
echo "======================================="
echo "🌐 Pi-hole Web Interface: http://${SERVER_IP}/admin"
echo "   Contraseña: $(grep PIHOLE_WEBPASS credentials.env | cut -d= -f2 || echo 'Ver credentials.env')"
echo ""
echo "🔧 WireGuard:"
echo "   Configuración del cliente guardada en credentials.env"
echo "   Endpoint: ${SERVER_IP}:51820"
echo ""
echo "🌐 Outline:"
echo "   API URL: $(grep OUTLINE_API_URL credentials.env | cut -d= -f2 || echo 'Ver credentials.env')"
echo ""
echo "🤖 Para el bot de Telegram:"
echo "   Las credenciales están en: bot/credentials/credentials.env"
echo "   Configura tu bot con estas variables"
echo ""
echo "📋 Comandos útiles:"
echo "   Ver logs: docker-compose logs -f"
echo "   Detener servicios: docker-compose down"
echo "   Reiniciar un servicio: docker-compose restart wireguard"