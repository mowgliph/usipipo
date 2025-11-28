#!/bin/bash
set -e

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Determinar el HOME correcto incluso cuando se usa sudo
if [ "$(id -u)" = "0" ] && [ ! -z "$SUDO_USER" ]; then
    # Ejecutado con sudo, usar el home del usuario original
    ACTUAL_USER_HOME=$(eval echo "~$SUDO_USER")
else
    # Ejecutado sin sudo o sin SUDO_USER
    ACTUAL_USER_HOME=$HOME
fi

# Directorio donde se encuentra este script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$SCRIPT_DIR"  # Asumimos que el proyecto está donde está el script

# Rutas corregidas
BOT_DIR="$PROJECT_DIR/bot"
DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
ENV_FILE="$BOT_DIR/.env"

# Global variables for service configuration
# Detectar IP pública IPv4 o IPv6
SERVER_IP=$(curl -4 -s ifconfig.co 2>/dev/null || ip -4 addr | sed -ne 's|^.* inet \([^/]*\)/.* scope global.*$|\1|p' | awk '{print $1}' | head -1)
if [[ -z ${SERVER_IP} ]]; then
  # Detectar IP pública IPv6 si no se encontró IPv4
  SERVER_IP=$(curl -6 -s ifconfig.co 2>/dev/null || ip -6 addr | sed -ne 's|^.* inet6 \([^/]*\)/.* scope global.*$|\1|p' | head -1)
fi

# Opcional: Separar IPv4 e IPv6 para mayor claridad
SERVER_IPV4=$(curl -4 -s ifconfig.co 2>/dev/null || ip -4 addr | sed -ne 's|^.* inet \([^/]*\)/.* scope global.*$|\1|p' | awk '{print $1}' | head -1)
SERVER_IPV6=$(curl -6 -s ifconfig.co 2>/dev/null || ip -6 addr | sed -ne 's|^.* inet6 \([^/]*\)/.* scope global.*$|\1|p' | head -1)

PIHOLE_PASS=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 20)

# Función para ejecutar comandos con sudo manteniendo el entorno
run_sudo() {
    if [ "$(id -u)" = "0" ]; then
        "$@"
    else
        sudo -E "$@"  # -E preserva las variables de entorno
    fi
}

# Función para mostrar el menú principal
show_menu() {
    clear
    echo -e "${BLUE}==============================================${NC}"
    echo -e "${BLUE}       🐳 Gestor de Docker - uSipipo VPN       ${NC}"
    echo -e "${BLUE}==============================================${NC}"
    echo -e "Usuario actual: $USER"
    echo -e "Directorio del proyecto: $PROJECT_DIR"
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
        *) echo -e "${RED}❌ Opción inválida. Intente nuevamente.${NC}"; sleep 2; show_menu ;;
    esac
}

# Función para instalar Docker y Docker Compose
install_docker() {
    clear
    echo -e "${YELLOW}🚀 Instalando Docker y Docker Compose...${NC}"
    
    # Verificar si ya está instalado
    if command -v docker &> /dev/null; then
        echo -e "${YELLOW}⚠️ Docker ya está instalado. Versión actual:${NC}"
        docker --version
        read -p "¿Desea reinstalar Docker? [s/N]: " reinstall
        if [[ ! "$reinstall" =~ [sS] ]]; then
            show_menu
            return
        fi
        uninstall_docker_force
    fi
    
    # Instalar dependencias previas
    echo -e "${BLUE}🔧 Instalando dependencias...${NC}"
    run_sudo apt-get update
    run_sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common gnupg lsb-release
    
    # Añadir clave GPG oficial de Docker
    echo -e "${BLUE}🔑 Añadiendo clave GPG de Docker...${NC}"
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | run_sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Añadir repositorio de Docker
    echo -e "${BLUE}📦 Añadiendo repositorio de Docker...${NC}"
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | run_sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Instalar Docker Engine
    echo -e "${BLUE}⚙️ Instalando Docker Engine...${NC}"
    run_sudo apt-get update
    run_sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Verificar instalación
    echo -e "${BLUE}🔍 Verificando instalación...${NC}"
    docker --version
    docker compose version
    
    # Añadir usuario actual al grupo docker
    echo -e "${BLUE}👥 Configurando permisos de usuario...${NC}"
    if [ "$(id -u)" = "0" ] && [ ! -z "$SUDO_USER" ]; then
        run_sudo usermod -aG docker "$SUDO_USER"
    else
        run_sudo usermod -aG docker $USER
    fi
    
    # Probar Docker sin sudo
    echo -e "${BLUE}🧪 Probando Docker sin sudo...${NC}"
    if [ "$(id -u)" = "0" ] && [ ! -z "$SUDO_USER" ]; then
        sudo -u "$SUDO_USER" docker run --rm hello-world > /dev/null 2>&1 || {
            echo -e "${YELLOW}⚠️ No se pudo ejecutar Docker sin sudo para $SUDO_USER. Deberá reiniciar la sesión o ejecutar: newgrp docker${NC}"
            sleep 3
        }
    else
        docker run --rm hello-world > /dev/null 2>&1 || {
            echo -e "${YELLOW}⚠️ No se pudo ejecutar Docker sin sudo. Deberá reiniciar la sesión o ejecutar: newgrp docker${NC}"
            sleep 3
        }
    fi
    
    echo -e "${GREEN}✅ Docker y Docker Compose instalados correctamente${NC}"
    echo -e "${YELLOW}💡 Recuerde: deberá cerrar y abrir sesión nuevamente para usar Docker sin sudo${NC}"
    read -p "Presione Enter para continuar..."
    show_menu
}

# Función para levantar servicios (corregida)
start_services() {
    clear
    echo -e "${YELLOW}🚀 Levantando servicios VPN...${NC}"
    
    # Verificar si Docker está instalado
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker no está instalado. Instálelo primero desde el menú.${NC}"
        read -p "Presione Enter para continuar..."
        show_menu
        return
    fi
    
    # Verificar si existe el archivo docker-compose.yml
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        echo -e "${RED}❌ No se encontró el archivo docker-compose.yml en: $DOCKER_COMPOSE_FILE${NC}"
        echo -e "${YELLOW}Directorio actual: $(pwd)${NC}"
        ls -la "$PROJECT_DIR"
        read -p "¿Desea clonar el repositorio para obtener los archivos? [s/N]: " clone_repo
        if [[ "$clone_repo" =~ [sS] ]]; then
            cd "$ACTUAL_USER_HOME"
            if [ -d "usipipo" ]; then
                echo -e "${YELLOW}⚠️ El directorio usipipo ya existe. ¿Desea sobrescribirlo? [s/N]: ${NC}"
                read -p "" overwrite
                if [[ "$overwrite" =~ [sS] ]]; then
                    run_sudo rm -rf usipipo
                else
                    echo -e "${RED}❌ Operación cancelada. Clone el repositorio manualmente${NC}"
                    read -p "Presione Enter para continuar..."
                    show_menu
                    return
                fi
            fi
            git clone https://github.com/mowgliph/usipipo.git
            cd usipipo
            echo -e "${GREEN}✅ Repositorio clonado correctamente${NC}"
            # Actualizar las rutas después de clonar
            PROJECT_DIR="$ACTUAL_USER_HOME/usipipo"
            DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
            ENV_FILE="$PROJECT_DIR/.env"
        else
            echo -e "${RED}❌ Operación cancelada. No se puede continuar sin el archivo docker-compose.yml${NC}"
            read -p "Presione Enter para continuar..."
            show_menu
            return
        fi
    fi

    # Ensure bot directory exists
    if [ ! -d "$BOT_DIR" ]; then
        mkdir -p "$BOT_DIR"
    fi

    # Crear archivo .env si no existe
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}⚠️ No se encontró el archivo .env. Creando uno copiando de example.env...${NC}"
        cp "$PROJECT_DIR/bot/example.env" "$ENV_FILE"
        # Append service variables
        echo "" >> "$ENV_FILE"
        echo "# Service configuration" >> "$ENV_FILE"
        echo "PIHOLE_WEBPASS=${PIHOLE_PASS}" >> "$ENV_FILE"
        echo "SERVER_IP=${SERVER_IP}" >> "$ENV_FILE"
        echo -e "${GREEN}✅ Archivo .env creado copiando de example.env y añadiendo variables de servicio${NC}"
    fi

    # Generate random ports and update .env
    PIHOLE_WEB_PORT=$((1024 + RANDOM % (65535 - 1024 + 1)))
    WIREGUARD_PORT=$((1024 + RANDOM % (65535 - 1024 + 1)))
    OUTLINE_API_PORT=$((1024 + RANDOM % (65535 - 1024 + 1)))
    SERVER_IPV6=$(curl -6 -s ifconfig.me 2>/dev/null || echo "")
    
    # Remove existing SERVER_IP and append new one
    sed -i "/^SERVER_IP=/d" "$ENV_FILE"
    echo "SERVER_IP=${SERVER_IP}" >> "$ENV_FILE"
    
    # Update .env with new variables
    sed -i "/^SERVER_IPV4=/d" "$ENV_FILE"
    echo "SERVER_IPV4=${SERVER_IP}" >> "$ENV_FILE"
    sed -i "/^PIHOLE_WEB_PORT=/d" "$ENV_FILE"
    echo "PIHOLE_WEB_PORT=${PIHOLE_WEB_PORT}" >> "$ENV_FILE"
    sed -i "/^WIREGUARD_PORT=/d" "$ENV_FILE"
    echo "WIREGUARD_PORT=${WIREGUARD_PORT}" >> "$ENV_FILE"
    sed -i "/^OUTLINE_API_PORT=/d" "$ENV_FILE"
    echo "OUTLINE_API_PORT=${OUTLINE_API_PORT}" >> "$ENV_FILE"
    sed -i "/^SERVERPORT=/d" "$ENV_FILE"
    echo "SERVERPORT=${WIREGUARD_PORT}" >> "$ENV_FILE"
    if [ -n "$SERVER_IPV6" ]; then
      sed -i "/^SERVER_IPV6=/d" "$ENV_FILE"
      echo "SERVER_IPV6=${SERVER_IPV6}" >> "$ENV_FILE"
    fi

    # Outline server setup
    if groups | grep &>/dev/null '\bdocker\b'; then
        DOCKER_CMD="docker"
    else
        DOCKER_CMD="run_sudo docker"
    fi

    # Check if Outline config exists
    # Preparar volumen de Outline
    echo -e "${BLUE}🔧 Preparando volumen para Outline...${NC}"
    if groups | grep &>/dev/null '\bdocker\b'; then
      docker volume create outline_data 2>/dev/null || true
    else
      run_sudo docker volume create outline_data 2>/dev/null || true
    fi
    echo -e "${GREEN}✅ Volumen de Outline preparado${NC}"

    # Levantar servicios con docker-compose
    cd "$PROJECT_DIR"
    echo -e "${BLUE}🐳 Iniciando servicios con Docker Compose...${NC}"
    
    # Determinar cómo ejecutar docker-compose según los permisos
    if docker compose version &>/dev/null; then
        # Usar docker compose (plugin moderno)
        if groups | grep &>/dev/null '\bdocker\b'; then
            docker compose up -d --force-recreate
        else
            run_sudo docker compose up -d --force-recreate
        fi
    else
        # Usar docker-compose (paquete antiguo)
        if groups | grep &>/dev/null '\bdocker\b'; then
            docker-compose up -d --force-recreate
        else
            run_sudo docker-compose up -d --force-recreate
        fi
    fi
    
    # Esperar a que los servicios se inicien
    echo -e "${YELLOW}⏳ Esperando a que los servicios se inicien (30 segundos)...${NC}"
    sleep 30
    
    # Verificar estado de los servicios
    echo -e "${BLUE}🔍 Verificando estado de los servicios...${NC}"
    if groups | grep &>/dev/null '\bdocker\b'; then
        docker compose ps
    else
        run_sudo docker compose ps
    fi
    
    # Obtener información útil
    SERVER_IPV4=$SERVER_IP
    PIHOLE_WEB_PORT=$(grep PIHOLE_WEB_PORT "$ENV_FILE" | cut -d= -f2)
    WIREGUARD_PORT=$(grep WIREGUARD_PORT "$ENV_FILE" | cut -d= -f2)
    OUTLINE_API_PORT=$(grep OUTLINE_API_PORT "$ENV_FILE" | cut -d= -f2)

    # Extract WireGuard public key
    if groups | grep &>/dev/null '\bdocker\b'; then
        WIREGUARD_PUBLIC_KEY=$(docker exec wireguard wg show wg0 public-key 2>/dev/null || echo "")
    else
        WIREGUARD_PUBLIC_KEY=$(run_sudo docker exec wireguard wg show wg0 public-key 2>/dev/null || echo "")
    fi

    # Append new variables to .env
    echo "PIHOLE_DNS=${SERVER_IP}" >> "$ENV_FILE"
    echo -e "${BLUE}🔑 Retrieving Outline API secret...${NC}"
    OUTLINE_API_SECRET=$($DOCKER_CMD run --rm -v outline_data:/data python:alpine python3 -c "import json; print(json.load(open('/data/shadowbox_server_config.json'))['managementUdpSecret'])")

    echo "WIREGUARD_PUBLIC_KEY=${WIREGUARD_PUBLIC_KEY}" >> "$ENV_FILE"
    echo "WIREGUARD_ENDPOINT=${SERVER_IP}:${WIREGUARD_PORT}" >> "$ENV_FILE"
    echo "WIREGUARD_PATH=/config" >> "$ENV_FILE"
    echo "OUTLINE_API_URL=http://${SERVER_IP}:${OUTLINE_API_PORT}" >> "$ENV_FILE"
    echo "OUTLINE_API_SECRET=$OUTLINE_API_SECRET" >> "$ENV_FILE"

    echo -e "\n${GREEN}🎉 SERVICIOS INICIADOS EXITOSAMENTE${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo -e "🌐 Pi-hole Web Interface: http://${SERVER_IPV4}:${PIHOLE_WEB_PORT}/admin"
    echo -e "   🔑 Contraseña: ${PIHOLE_PASS}"
    echo -e ""
    echo -e "🔧 WireGuard:"
    echo -e "   📡 Endpoint: ${SERVER_IPV4}:${WIREGUARD_PORT}"
    echo -e ""
    echo -e "🌍 Outline Server:"
    echo -e "   📡 API URL: http://${SERVER_IPV4}:${OUTLINE_API_PORT}"
    echo -e ""

    echo -e "🔧 Variables de configuración añadidas al .env:"
    echo -e "   📡 PIHOLE_DNS: ${SERVER_IP}"
    echo -e "   🔑 WIREGUARD_PUBLIC_KEY: ${WIREGUARD_PUBLIC_KEY}"
    echo -e "   📡 WIREGUARD_ENDPOINT: ${SERVER_IP}:${WIREGUARD_PORT}"
    echo -e "   📁 WIREGUARD_PATH: /config"
    echo -e "   🌍 OUTLINE_API_URL: http://${SERVER_IP}:${OUTLINE_API_PORT}"
    echo -e "   🔑 OUTLINE_API_SECRET: $OUTLINE_API_SECRET"
    echo -e ""

    # Asegurar permisos correctos en los archivos generados
    chown $(stat -c "%U:%G" "$BOT_DIR") "$ENV_FILE" 2>/dev/null || true
    
    read -p "Presione Enter para continuar..."
    show_menu
}

# Resto de las funciones (show_status, stop_services, uninstall_docker) mantienen la misma lógica
# pero usando "run_sudo" para comandos que requieren privilegios

# Función para mostrar estado de los contenedores
show_status() {
    clear
    echo -e "${BLUE}📊 Estado de los contenedores Docker${NC}"
    echo -e "${BLUE}====================================${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker no está instalado${NC}"
        read -p "Presione Enter para continuar..."
        show_menu
        return
    fi
    
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        echo -e "${RED}❌ No se encontró el archivo docker-compose.yml${NC}"
        read -p "Presione Enter para continuar..."
        show_menu
        return
    fi
    
    cd "$PROJECT_DIR"
    
    echo -e "${BLUE}🐳 Servicios en ejecución:${NC}"
    if groups | grep &>/dev/null '\bdocker\b'; then
        docker compose ps
        echo -e "\n${BLUE}📈 Estadísticas de recursos:${NC}"
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    else
        run_sudo docker compose ps
        echo -e "\n${BLUE}📈 Estadísticas de recursos (requiere sudo):${NC}"
        run_sudo docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    fi
    
    read -p "Presione Enter para continuar..."
    show_menu
}

# Función para detener servicios
stop_services() {
    clear
    echo -e "${YELLOW}🛑 Deteniendo servicios VPN...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker no está instalado${NC}"
        read -p "Presione Enter para continuar..."
        show_menu
        return
    fi
    
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        echo -e "${RED}❌ No se encontró el archivo docker-compose.yml${NC}"
        read -p "Presione Enter para continuar..."
        show_menu
        return
    fi
    
    cd "$PROJECT_DIR"
    
    if groups | grep &>/dev/null '\bdocker\b'; then
        docker compose down
    else
        run_sudo docker compose down
    fi
    
    echo -e "${GREEN}✅ Servicios detenidos correctamente${NC}"
    read -p "Presione Enter para continuar..."
    show_menu
}

# Función para desinstalar Docker completamente
uninstall_docker() {
    clear
    echo -e "${RED}🔥 ADVERTENCIA: Desinstalación completa de Docker${NC}"
    echo -e "${RED}==============================================${NC}"
    echo -e "Esta operación eliminará permanentemente:"
    echo -e "- Todos los contenedores en ejecución"
    echo -e "- Todas las imágenes de Docker"
    echo -e "- Todos los volúmenes y redes"
    echo -e "- Los paquetes de Docker del sistema"
    echo -e ""
    echo -e "${YELLOW}⚠️ Se perderán todos los datos de los contenedores, incluyendo:"
    echo -e "  - Configuraciones de Pi-hole"
    echo -e "  - Claves y conexiones de WireGuard"
    echo -e "  - Configuraciones de Outline Server"
    echo -e ""
    
    read -p "¿Está SEGURO de que quiere continuar? [s/N]: " confirm
    if [[ ! "$confirm" =~ [sS] ]]; then
        echo -e "${YELLOW}❌ Operación cancelada por el usuario${NC}"
        read -p "Presione Enter para continuar..."
        show_menu
        return
    fi
    
    uninstall_docker_force
    
    echo -e "${GREEN}✅ Docker desinstalado completamente${NC}"
    echo -e "${YELLOW}💡 Puede reinstalarlo en cualquier momento desde el menú${NC}"
    read -p "Presione Enter para continuar..."
    show_menu
}

# Función interna para desinstalación forzada (sin confirmación)
uninstall_docker_force() {
    echo -e "${RED}🔧 Deteniendo todos los contenedores...${NC}"
    # Detener todos los contenedores si existen
    if command -v docker &> /dev/null; then
        if groups | grep &>/dev/null '\bdocker\b'; then
            docker stop $(docker ps -aq 2>/dev/null) 2>/dev/null || true
            docker rm -f $(docker ps -aq 2>/dev/null) 2>/dev/null || true
            docker volume rm $(docker volume ls -q 2>/dev/null) 2>/dev/null || true
            docker network rm $(docker network ls -q 2>/dev/null) 2>/dev/null || true
            docker system prune -a -f --volumes 2>/dev/null || true
        else
            run_sudo docker stop $(run_sudo docker ps -aq 2>/dev/null) 2>/dev/null || true
            run_sudo docker rm -f $(run_sudo docker ps -aq 2>/dev/null) 2>/dev/null || true
            run_sudo docker volume rm $(run_sudo docker volume ls -q 2>/dev/null) 2>/dev/null || true
            run_sudo docker network rm $(run_sudo docker network ls -q 2>/dev/null) 2>/dev/null || true
            run_sudo docker system prune -a -f --volumes 2>/dev/null || true
        fi
    fi
    
    echo -e "${RED}🔧 Eliminando paquetes de Docker...${NC}"
    # Eliminar paquetes de Docker
    run_sudo apt-get remove -y docker docker-engine docker.io containerd runc docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-model-plugin 2>/dev/null || true
    run_sudo apt-get autoremove -y 2>/dev/null || true
    
    echo -e "${RED}🔧 Eliminando archivos y directorios de Docker...${NC}"
    # Eliminar archivos y directorios de Docker
    run_sudo rm -rf /var/lib/docker 2>/dev/null || true
    run_sudo rm -rf /etc/docker 2>/dev/null || true
    run_sudo rm -f /etc/systemd/system/docker.service 2>/dev/null || true
    run_sudo rm -f /etc/systemd/system/docker.socket 2>/dev/null || true
    run_sudo rm -rf /var/run/docker 2>/dev/null || true
    run_sudo rm -rf /usr/local/bin/docker-compose 2>/dev/null || true
    run_sudo rm -f /usr/share/keyrings/docker-archive-keyring.gpg 2>/dev/null || true
    run_sudo rm -f /etc/apt/sources.list.d/docker.list 2>/dev/null || true
    
    echo -e "${RED}🔧 Recargando systemd...${NC}"
    run_sudo systemctl daemon-reload 2>/dev/null || true
    run_sudo systemctl reset-failed 2>/dev/null || true
    
    echo -e "${RED}🔧 Limpiando caché de paquetes...${NC}"
    run_sudo apt-get clean 2>/dev/null || true
    run_sudo apt-get autoclean 2>/dev/null || true
}

# Iniciar el script
show_menu