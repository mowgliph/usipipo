#!/bin/bash
set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$SCRIPT_DIR"
ENV_FILE="$PROJECT_DIR/.env"
DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"

# Funciones de ayuda
run_sudo() {
    if [ "$(id -u)" = "0" ]; then "$@"; else sudo -E "$@"; fi
}

get_public_ip() {
    # Intenta obtener IP IPv4, fallback a IPv6
    IP=$(curl -4 -s --connect-timeout 5 ifconfig.co 2>/dev/null)
    if [ -z "$IP" ]; then
        IP=$(curl -6 -s --connect-timeout 5 ifconfig.co 2>/dev/null)
    fi
    echo "$IP"
}

# Menú Principal
show_menu() {
    clear
    SERVER_IP=$(get_public_ip)
    echo -e "${BLUE}=== uSipipo VPN Manager ===${NC}"
    echo -e "IP Detectada: ${GREEN}${SERVER_IP:-No detectada}${NC}"
    echo -e "1) ${GREEN}Instalar Docker${NC}"
    echo -e "2) ${YELLOW}Iniciar Servicios (VPN + PiHole)${NC}"
    echo -e "3) ${BLUE}Ver Estado${NC}"
    echo -e "4) ${RED}Detener Servicios${NC}"
    echo -e "5) ${RED}Desinstalar Todo${NC}"
    echo -e "6) Salir"
    read -p "Opción: " choice
    
    case $choice in
        1) install_docker ;;
        2) start_services ;;
        3) show_status ;;
        4) stop_services ;;
        5) uninstall_docker ;;
        6) exit 0 ;;
        *) show_menu ;;
    esac
}

install_docker() {
    echo -e "${YELLOW}Instalando Docker...${NC}"
    run_sudo apt-get update
    run_sudo apt-get install -y ca-certificates curl gnupg lsb-release
    
    if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
        run_sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | run_sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    fi
    
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | run_sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    run_sudo apt-get update
    run_sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    run_sudo usermod -aG docker $USER
    echo -e "${GREEN}Docker instalado. Es posible que debas reiniciar sesión.${NC}"
    read -p "Enter para continuar..."
    show_menu
}

start_services() {
    # 1. Validación de IP
    SERVER_IP=$(get_public_ip)
    if [ -z "$SERVER_IP" ]; then
        echo -e "${RED}❌ Error: No se pudo detectar IP pública. Outline fallará sin ella.${NC}"
        read -p "Enter..."
        show_menu; return
    fi

    # 2. Generar .env
    echo -e "${BLUE}Generando configuración...${NC}"
    PIHOLE_PASS=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 12)
    OUTLINE_API_PORT=$((10000 + RANDOM % 50000))
    WIREGUARD_PORT=$((10000 + RANDOM % 50000))
    PIHOLE_WEB_PORT=$((10000 + RANDOM % 50000))

    cat > "$ENV_FILE" <<EOF
SERVER_IP=${SERVER_IP}
PIHOLE_WEBPASS=${PIHOLE_PASS}
PIHOLE_WEB_PORT=${PIHOLE_WEB_PORT}
WIREGUARD_PORT=${WIREGUARD_PORT}
OUTLINE_API_PORT=${OUTLINE_API_PORT}
EOF

    # 3. Levantar contenedores (con limpieza de volumen)
    if groups | grep -q docker; then CMD="docker compose"; else CMD="run_sudo docker compose"; fi
    DOCKER_CMD="docker"
    if ! groups | grep -q docker; then DOCKER_CMD="run_sudo docker"; fi
    
    # CRÍTICO: Eliminar el volumen antes de iniciar para evitar archivos corruptos
    $DOCKER_CMD volume rm outline_data 2>/dev/null || true
    
    echo -e "${YELLOW}Levantando contenedores...${NC}"
    $CMD up -d --remove-orphans

    # 4. Espera Activa (Lógica tipo Jigsaw)
    echo -e "${BLUE}⏳ Esperando a que Outline genere certificados y configuración (máx 80s)...${NC}"
    
    MAX_RETRIES=40
    COUNT=0
    SUCCESS=false
    
    while [ $COUNT -lt $MAX_RETRIES ]; do
        # Verificar si el contenedor está corriendo y no está reiniciando
        STATUS=$($DOCKER_CMD inspect -f '{{.State.Status}}' outline 2>/dev/null || echo "missing")
        
        if [ "$STATUS" == "restarting" ] || [ "$STATUS" == "dead" ] || [ "$STATUS" == "exited" ]; then
             echo -e "\n${RED}🛑 El contenedor Outline falló (Status: $STATUS).${NC}"
             echo -e "${YELLOW}--- LOGS DE OUTLINE (Debug) ---${NC}"
             $DOCKER_CMD logs outline --tail 20
             echo -e "${YELLOW}--------------------------------${NC}"
             read -p "Presione Enter para volver..."
             show_menu; return
        fi

        # Verificar si existe el archivo de configuración
        if $DOCKER_CMD run --rm -v outline_data:/data alpine test -f /data/shadowbox_server_config.json; then
            SUCCESS=true
            break
        fi
        
        echo -ne "."
        sleep 2
        COUNT=$((COUNT+1))
    done
    echo ""

    if [ "$SUCCESS" = true ]; then
        echo -e "${GREEN}✅ Configuración detectada. Extrayendo credenciales...${NC}"
        
        # Extraer Secret ID
        SECRET_ID=$($DOCKER_CMD run --rm -v outline_data:/data alpine cat /data/shadowbox_server_config.json | grep -o '"managementUdpSecret":"[^"]*"' | cut -d'"' -f4)
        
        # Extraer Certificado SHA256 (Método Jigsaw)
        CERT_SHA=$($DOCKER_CMD run --rm -v outline_data:/data alpine/openssl x509 -in /data/shadowbox-selfsigned.crt -noout -fingerprint -sha256 | cut -d= -f2 | tr -d :)
        
        # Construir URL API
        API_URL="https://${SERVER_IP}:${OUTLINE_API_PORT}/${SECRET_ID}"
        
        # Generar JSON final para Outline Manager
        OUTLINE_ACCESS_CONFIG="{\"apiUrl\":\"${API_URL}\",\"certSha256\":\"${CERT_SHA}\"}"
        
        # Obtener info Wireguard
        WG_PUB_KEY=$($DOCKER_CMD exec wireguard wg show wg0 public-key 2>/dev/null || echo "Error")
        
        clear
        echo -e "${BLUE}====================================================${NC}"
        echo -e "${GREEN}🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE 🎉${NC}"
        echo -e "${BLUE}====================================================${NC}"
        echo -e ""
        echo -e "${YELLOW}1. PI-HOLE (Bloqueo de Anuncios)${NC}"
        echo -e "   Web:    http://${SERVER_IP}:${PIHOLE_WEB_PORT}/admin"
        echo -e "   Pass:   ${PIHOLE_PASS}"
        echo -e ""
        echo -e "${YELLOW}2. WIREGUARD VPN${NC}"
        echo -e "   Endpoint: ${SERVER_IP}:${WIREGUARD_PORT}"
        echo -e "   Pub Key:  ${WG_PUB_KEY}"
        echo -e ""
        echo -e "${YELLOW}3. OUTLINE VPN (Para Outline Manager)${NC}"
        echo -e "   Copia y pega la siguiente línea COMPLETA en Outline Manager:"
        echo -e ""
        echo -e "${GREEN}${OUTLINE_ACCESS_CONFIG}${NC}"
        echo -e ""
        echo -e "${BLUE}====================================================${NC}"
    else
        echo -e "${RED}Tiempo de espera agotado. Outline no pudo iniciar.${NC}"
    fi

    read -p "Presione Enter para volver al menú..."
    show_menu
}

show_status() {
    clear
    if groups | grep -q docker; then CMD="docker"; else CMD="run_sudo docker"; fi
    $CMD compose ps
    read -p "Enter..."
    show_menu
}

stop_services() {
    if groups | grep -q docker; then CMD="docker"; else CMD="run_sudo docker"; fi
    $CMD compose down
    show_menu
}

uninstall_docker() {
    run_sudo docker system prune -a -f --volumes
    run_sudo apt-get purge -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    run_sudo rm -rf /var/lib/docker
    rm -f "$ENV_FILE"
    echo -e "${RED}Desinstalado.${NC}"
    show_menu
}

show_menu