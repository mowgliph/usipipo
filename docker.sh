#!/bin/bash
set -e

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables de configuración
PROJECT_DIR="$HOME/mowgliph/usipipo"
DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
ENV_FILE="$PROJECT_DIR/.env"

# Función para mostrar el menú principal
show_menu() {
    clear
    echo -e "${BLUE}==============================================${NC}"
    echo -e "${BLUE}       🐳 Gestor de Docker - uSipipo VPN       ${NC}"
    echo -e "${BLUE}==============================================${NC}"
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
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common gnupg lsb-release
    
    # Añadir clave GPG oficial de Docker
    echo -e "${BLUE}🔑 Añadiendo clave GPG de Docker...${NC}"
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Añadir repositorio de Docker
    echo -e "${BLUE}📦 Añadiendo repositorio de Docker...${NC}"
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Instalar Docker Engine
    echo -e "${BLUE}⚙️ Instalando Docker Engine...${NC}"
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Verificar instalación
    echo -e "${BLUE}🔍 Verificando instalación...${NC}"
    sudo docker --version
    sudo docker compose version
    
    # Añadir usuario actual al grupo docker
    echo -e "${BLUE}👥 Configurando permisos de usuario...${NC}"
    sudo usermod -aG docker $USER
    
    # Probar Docker sin sudo
    echo -e "${BLUE}🧪 Probando Docker sin sudo...${NC}"
    docker run --rm hello-world > /dev/null 2>&1 || {
        echo -e "${YELLOW}⚠️ No se pudo ejecutar Docker sin sudo. Deberá reiniciar la sesión o ejecutar: newgrp docker${NC}"
        sleep 3
    }
    
    echo -e "${GREEN}✅ Docker y Docker Compose instalados correctamente${NC}"
    echo -e "${YELLOW}💡 Recuerde: deberá cerrar y abrir sesión nuevamente para usar Docker sin sudo${NC}"
    read -p "Presione Enter para continuar..."
    show_menu
}

# Función para levantar servicios
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
        read -p "¿Desea clonar el repositorio para obtener los archivos? [s/N]: " clone_repo
        if [[ "$clone_repo" =~ [sS] ]]; then
            cd $HOME
            if [ -d "usipipo" ]; then
                echo -e "${YELLOW}⚠️ El directorio usipipo ya existe. ¿Desea sobrescribirlo? [s/N]: ${NC}"
                read -p "" overwrite
                if [[ "$overwrite" =~ [sS] ]]; then
                    rm -rf usipipo
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
        else
            echo -e "${RED}❌ Operación cancelada. No se puede continuar sin el archivo docker-compose.yml${NC}"
            read -p "Presione Enter para continuar..."
            show_menu
            return
        fi
    fi
    
    # Crear archivo .env si no existe
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}⚠️ No se encontró el archivo .env. Creando uno con valores por defecto...${NC}"
        SERVER_IP=$(curl -s ifconfig.me)
        PIHOLE_PASS=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 20)
        
        cat > "$ENV_FILE" <<EOF
# Configuración generada automáticamente para uSipipo VPN
PIHOLE_WEBPASS=${PIHOLE_PASS}
SERVER_IP=${SERVER_IP}
EOF
        echo -e "${GREEN}✅ Archivo .env creado con configuración inicial${NC}"
    fi
    
    # Levantar servicios con docker-compose
    cd "$PROJECT_DIR"
    echo -e "${BLUE}🐳 Iniciando servicios con Docker Compose...${NC}"
    docker compose up -d --force-recreate
    
    # Esperar a que los servicios se inicien
    echo -e "${YELLOW}⏳ Esperando a que los servicios se inicien (30 segundos)...${NC}"
    sleep 30
    
    # Verificar estado de los servicios
    echo -e "${BLUE}🔍 Verificando estado de los servicios...${NC}"
    docker compose ps
    
    # Obtener información útil
    SERVER_IP=$(grep SERVER_IP "$ENV_FILE" | cut -d= -f2)
    PIHOLE_PASS=$(grep PIHOLE_WEBPASS "$ENV_FILE" | cut -d= -f2)
    
    echo -e "\n${GREEN}🎉 SERVICIOS INICIADOS EXITOSAMENTE${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo -e "🌐 Pi-hole Web Interface: http://${SERVER_IP}/admin"
    echo -e "   🔑 Contraseña: ${PIHOLE_PASS}"
    echo -e ""
    echo -e "🔧 WireGuard:"
    echo -e "   📡 Endpoint: ${SERVER_IP}:51820"
    echo -e ""
    echo -e "🌍 Outline Server:"
    echo -e "   📡 API URL: http://${SERVER_IP}:8080"
    echo -e ""
    echo -e "${YELLOW}💡 Para generar credenciales para el bot de Telegram, ejecute:${NC}"
    echo -e "   cd $PROJECT_DIR"
    echo -e "   ./init-services.sh"
    
    read -p "Presione Enter para continuar..."
    show_menu
}

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
    docker compose ps
    
    echo -e "\n${BLUE}📈 Estadísticas de recursos:${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    
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
    docker compose down
    
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
        docker stop $(docker ps -aq 2>/dev/null) 2>/dev/null || true
        docker rm -f $(docker ps -aq 2>/dev/null) 2>/dev/null || true
        docker volume rm $(docker volume ls -q 2>/dev/null) 2>/dev/null || true
        docker network rm $(docker network ls -q 2>/dev/null) 2>/dev/null || true
        docker system prune -a -f --volumes 2>/dev/null || true
    fi
    
    echo -e "${RED}🔧 Eliminando paquetes de Docker...${NC}"
    # Eliminar paquetes de Docker
    sudo apt-get remove -y docker docker-engine docker.io containerd runc docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-model-plugin 2>/dev/null || true
    sudo apt-get autoremove -y 2>/dev/null || true
    
    echo -e "${RED}🔧 Eliminando archivos y directorios de Docker...${NC}"
    # Eliminar archivos y directorios de Docker
    sudo rm -rf /var/lib/docker 2>/dev/null || true
    sudo rm -rf /etc/docker 2>/dev/null || true
    sudo rm -f /etc/systemd/system/docker.service 2>/dev/null || true
    sudo rm -f /etc/systemd/system/docker.socket 2>/dev/null || true
    sudo rm -rf /var/run/docker 2>/dev/null || true
    sudo rm -rf /usr/local/bin/docker-compose 2>/dev/null || true
    sudo rm -f /usr/share/keyrings/docker-archive-keyring.gpg 2>/dev/null || true
    sudo rm -f /etc/apt/sources.list.d/docker.list 2>/dev/null || true
    
    echo -e "${RED}🔧 Recargando systemd...${NC}"
    sudo systemctl daemon-reload 2>/dev/null || true
    sudo systemctl reset-failed 2>/dev/null || true
    
    echo -e "${RED}🔧 Limpiando caché de paquetes...${NC}"
    sudo apt-get clean 2>/dev/null || true
    sudo apt-get autoclean 2>/dev/null || true
}

# Iniciar el script
show_menu