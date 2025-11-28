#!/bin/bash
set -e

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorio donde se encuentra este script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$SCRIPT_DIR"

# Rutas corregidas - EL ENV DEBE ESTAR EN LA RAIZ PARA DOCKER COMPOSE
BOT_DIR="$PROJECT_DIR/bot"
DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
ENV_FILE="$PROJECT_DIR/.env" 

# Determinar el HOME correcto
if [ "$(id -u)" = "0" ] && [ ! -z "$SUDO_USER" ]; then
    ACTUAL_USER_HOME=$(eval echo "~$SUDO_USER")
else
    ACTUAL_USER_HOME=$HOME
fi

# Variables globales de IP (Detectar una sola vez)
SERVER_IPV4=$(curl -4 -s ifconfig.co 2>/dev/null || ip -4 addr | sed -ne 's|^.* inet \([^/]*\)/.* scope global.*$|\1|p' | awk '{print $1}' | head -1)
SERVER_IPV6=$(curl -6 -s ifconfig.co 2>/dev/null || ip -6 addr | sed -ne 's|^.* inet6 \([^/]*\)/.* scope global.*$|\1|p' | head -1)

# Priorizar IPv4 para SERVER_IP
if [[ -n ${SERVER_IPV4} ]]; then
    SERVER_IP=$SERVER_IPV4
else
    SERVER_IP=$SERVER_IPV6
fi

PIHOLE_PASS=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 20)

# Función para ejecutar comandos con sudo
run_sudo() {
    if [ "$(id -u)" = "0" ]; then
        "$@"
    else
        sudo -E "$@"
    fi
}

show_menu() {
    clear
    echo -e "${BLUE}==============================================${NC}"
    echo -e "${BLUE}       🐳 Gestor de Docker - uSipipo VPN       ${NC}"
    echo -e "${BLUE}==============================================${NC}"
    echo -e "Usuario: $USER | IP: $SERVER_IP"
    echo -e "Directorio: $PROJECT_DIR"
    echo -e "1) ${GREEN}✅ Instalar Docker y Docker Compose${NC}"
    echo -e "2) ${YELLOW}🚀 Levantar servicios VPN${NC}"
    echo -e "3) ${BLUE}📊 Ver estado de los contenedores${NC}"
    echo -e "4) ${RED}🛑 Detener servicios VPN${NC}"
    echo -e "5) ${RED}🔥 Desinstalar Docker completamente${NC}"
    echo -e "6) ${NC}Salir"
    echo -e "${BLUE}==============================================${NC}"
    read -p "Seleccione una opción [1-6]: " choice
    
    case $choice in
        1) install_docker ;;
        2) start_services ;;
        3) show_status ;;
        4) stop_services ;;
        5) uninstall_docker ;;
        6) exit 0 ;;
        *) echo -e "${RED}❌ Opción inválida.${NC}"; sleep 2; show_menu ;;
    esac
}

install_docker() {
    clear
    echo -e "${YELLOW}🚀 Instalando Docker...${NC}"
    if command -v docker &> /dev/null; then
        echo -e "${YELLOW}⚠️ Docker ya está instalado.${NC}"
        read -p "¿Reinstalar? [s/N]: " reinstall
        if [[ ! "$reinstall" =~ [sS] ]]; then show_menu; return; fi
        uninstall_docker_force
    fi
    
    echo -e "${BLUE}🔧 Instalando dependencias y Docker...${NC}"
    run_sudo apt-get update
    run_sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common gnupg lsb-release
    
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | run_sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | run_sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    run_sudo apt-get update
    run_sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Añadir usuario al grupo docker
    if [ "$(id -u)" = "0" ] && [ ! -z "$SUDO_USER" ]; then
        run_sudo usermod -aG docker "$SUDO_USER"
    else
        run_sudo usermod -aG docker $USER
    fi
    
    echo -e "${GREEN}✅ Docker instalado. Reinicie sesión para usar sin sudo.${NC}"
    read -p "Presione Enter..."
    show_menu
}

start_services() {
    clear
    echo -e "${YELLOW}🚀 Levantando servicios VPN...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker no instalado.${NC}"; read -p "Enter..."; show_menu; return;
    fi
    
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Falta docker-compose.yml${NC}"
        read -p "¿Clonar repo? [s/N]: " clone_repo
        if [[ "$clone_repo" =~ [sS] ]]; then
            cd "$ACTUAL_USER_HOME"
            [ -d "usipipo" ] && run_sudo rm -rf usipipo
            git clone https://github.com/mowgliph/usipipo.git
            cd usipipo
            # Recargar variables de ruta tras clonar
            PROJECT_DIR="$ACTUAL_USER_HOME/usipipo"
            DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
            ENV_FILE="$PROJECT_DIR/.env"
        else
            show_menu; return
        fi
    fi

    mkdir -p "$BOT_DIR"

    # Generar o actualizar .env
    echo -e "${BLUE}📝 Configurando variables de entorno en $ENV_FILE...${NC}"
    
    # Puertos aleatorios si no existen
    PIHOLE_WEB_PORT=$((1024 + RANDOM % (65535 - 1024 + 1)))
    WIREGUARD_PORT=$((1024 + RANDOM % (65535 - 1024 + 1)))
    OUTLINE_API_PORT=$((1024 + RANDOM % (65535 - 1024 + 1)))
    
    # Crear archivo limpio
    echo "# Configuración generada automáticamente" > "$ENV_FILE"
    echo "SERVER_IP=${SERVER_IP}" >> "$ENV_FILE"
    echo "SERVER_IPV4=${SERVER_IPV4}" >> "$ENV_FILE"
    if [ -n "$SERVER_IPV6" ]; then echo "SERVER_IPV6=${SERVER_IPV6}" >> "$ENV_FILE"; fi
    
    echo "PIHOLE_WEBPASS=${PIHOLE_PASS}" >> "$ENV_FILE"
    echo "PIHOLE_WEB_PORT=${PIHOLE_WEB_PORT}" >> "$ENV_FILE"
    echo "WIREGUARD_PORT=${WIREGUARD_PORT}" >> "$ENV_FILE"
    echo "OUTLINE_API_PORT=${OUTLINE_API_PORT}" >> "$ENV_FILE"
    echo "SERVERPORT=${WIREGUARD_PORT}" >> "$ENV_FILE"

    # Determinar comando Docker
    if groups | grep &>/dev/null '\bdocker\b'; then
        DOCKER_CMD="docker"
        COMPOSE_CMD="docker compose"
    else
        DOCKER_CMD="run_sudo docker"
        COMPOSE_CMD="run_sudo docker compose"
    fi

    # Volumen Outline
    $DOCKER_CMD volume create outline_data 2>/dev/null || true

    # Levantar
    cd "$PROJECT_DIR"
    echo -e "${BLUE}🐳 Iniciando contenedores...${NC}"
    $COMPOSE_CMD up -d --force-recreate
    
    echo -e "${YELLOW}⏳ Esperando 30 segundos para arranque inicial...${NC}"
    sleep 30
    
    # Obtener variables dinámicas
    WIREGUARD_PUBLIC_KEY=$($DOCKER_CMD exec wireguard wg show wg0 public-key 2>/dev/null || echo "Error_Obtaining_Key")

    # === CORRECCIÓN PRINCIPAL: ESPERA ACTIVA PARA OUTLINE ===
    echo -e "${BLUE}🔑 Esperando configuración de Outline...${NC}"
    MAX_RETRIES=30
    COUNT=0
    OUTLINE_READY=false
    
    while [ $COUNT -lt $MAX_RETRIES ]; do
        if $DOCKER_CMD run --rm -v outline_data:/data alpine ls /data/shadowbox_server_config.json >/dev/null 2>&1; then
            OUTLINE_READY=true
            break
        fi
        echo -ne "${YELLOW}.${NC}"
        sleep 2
        COUNT=$((COUNT+1))
    done
    echo ""

    if [ "$OUTLINE_READY" = true ]; then
        OUTLINE_API_SECRET=$($DOCKER_CMD run --rm -v outline_data:/data python:alpine python3 -c "import json; print(json.load(open('/data/shadowbox_server_config.json'))['managementUdpSecret'])")
    else
        echo -e "${RED}⚠️ Error: Outline tardó demasiado en generar la configuración.${NC}"
        OUTLINE_API_SECRET="Error_Timeout"
    fi

    # Guardar datos finales en .env
    echo "PIHOLE_DNS=${SERVER_IP}" >> "$ENV_FILE"
    echo "WIREGUARD_PUBLIC_KEY=${WIREGUARD_PUBLIC_KEY}" >> "$ENV_FILE"
    echo "WIREGUARD_ENDPOINT=${SERVER_IP}:${WIREGUARD_PORT}" >> "$ENV_FILE"
    echo "OUTLINE_API_URL=http://${SERVER_IP}:${OUTLINE_API_PORT}" >> "$ENV_FILE"
    echo "OUTLINE_API_SECRET=$OUTLINE_API_SECRET" >> "$ENV_FILE"
    
    # Asegurar permisos del .env
    if [ ! -z "$SUDO_USER" ]; then
        chown "$SUDO_USER:$(id -gn $SUDO_USER)" "$ENV_FILE" 2>/dev/null || true
    else
         chown "$USER:$(id -gn $USER)" "$ENV_FILE" 2>/dev/null || true
    fi

    echo -e "\n${GREEN}🎉 SERVICIOS INICIADOS${NC}"
    echo -e "🌐 Pi-hole: http://${SERVER_IP}:${PIHOLE_WEB_PORT}/admin (Pass: ${PIHOLE_PASS})"
    echo -e "🔧 WireGuard Endpoint: ${SERVER_IP}:${WIREGUARD_PORT}"
    echo -e "🌍 Outline API: http://${SERVER_IP}:${OUTLINE_API_PORT}"
    echo -e "🔑 Outline Secret: ${OUTLINE_API_SECRET}"
    
    read -p "Presione Enter..."
    show_menu
}

show_status() {
    clear
    cd "$PROJECT_DIR"
    if groups | grep &>/dev/null '\bdocker\b'; then
        docker compose ps
        echo ""
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    else
        run_sudo docker compose ps
        echo ""
        run_sudo docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    fi
    read -p "Presione Enter..."
    show_menu
}

stop_services() {
    clear
    cd "$PROJECT_DIR"
    echo -e "${YELLOW}🛑 Deteniendo...${NC}"
    if groups | grep &>/dev/null '\bdocker\b'; then
        docker compose down
    else
        run_sudo docker compose down
    fi
    show_menu
}

uninstall_docker() {
    clear
    echo -e "${RED}🔥 DESINSTALACIÓN COMPLETA${NC}"
    read -p "¿Seguro? [s/N]: " confirm
    if [[ ! "$confirm" =~ [sS] ]]; then show_menu; return; fi
    uninstall_docker_force
    show_menu
}

uninstall_docker_force() {
    echo -e "${RED}🔧 Eliminando contenedores y volúmenes...${NC}"
    run_sudo docker stop $(docker ps -aq) 2>/dev/null || true
    run_sudo docker rm -f $(docker ps -aq) 2>/dev/null || true
    run_sudo docker volume rm $(docker volume ls -q) 2>/dev/null || true
    run_sudo docker system prune -a -f --volumes 2>/dev/null || true
    
    echo -e "${RED}🔧 Eliminando Docker...${NC}"
    run_sudo apt-get remove -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-compose 2>/dev/null || true
    run_sudo rm -rf /var/lib/docker /etc/docker 2>/dev/null || true
    
    # Limpiar archivos del proyecto
    rm -f "$ENV_FILE"
}

show_menu
