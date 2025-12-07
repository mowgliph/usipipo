#!/bin/bash
set -e

# =============================================================================
# uSipipo VPN Manager v2.0 - Professional Docker Management Script
# =============================================================================
# Author: uSipipo Team
# License: MIT
# Description: Automated VPN setup with Outline, WireGuard, and Pi-hole
# Repository: https://github.com/usipipo/vpn-manager
# =============================================================================

# =============================================================================
# Color Definitions and UI Elements
# =============================================================================
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly GRAY='\033[0;90m'
readonly NC='\033[0m' # No Color

# UI Separators
readonly SEPARATOR="═══════════════════════════════════════════════════════════════════════════════"
readonly THIN_SEPARATOR="───────────────────────────────────────────────────────────────────────────────"
readonly HEADER_ICON="🛡️"
readonly SUCCESS_ICON="✓"
readonly ERROR_ICON="✗"
readonly WARNING_ICON="⚠"
readonly INFO_ICON="ℹ"

# =============================================================================
# System Variables
# =============================================================================
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$SCRIPT_DIR"
ENV_FILE="$PROJECT_DIR/.env"
ENV_EXAMPLE="$PROJECT_DIR/example.env"
DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
LOG_FILE="$PROJECT_DIR/logs/installation_$(date +%Y%m%d_%H%M%S).log"

# =============================================================================
# Logging Functions
# =============================================================================
log_raw() {
    local message="$1"
    echo -e "$message" | tee -a "$LOG_FILE" 2>/dev/null || echo -e "$message"
}

log_info() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    log_raw "${BLUE}${INFO_ICON} [INFO]${NC} ${GRAY}${timestamp}${NC} │ $1"
}

log_success() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    log_raw "${GREEN}${SUCCESS_ICON} [SUCCESS]${NC} ${GRAY}${timestamp}${NC} │ $1"
}

log_warning() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    log_raw "${YELLOW}${WARNING_ICON} [WARNING]${NC} ${GRAY}${timestamp}${NC} │ $1"
}

log_error() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    log_raw "${RED}${ERROR_ICON} [ERROR]${NC} ${GRAY}${timestamp}${NC} │ $1"
}

log_header() {
    log_raw "\n${CYAN}${SEPARATOR}${NC}"
    log_raw "${WHITE}${1}${NC}"
    log_raw "${CYAN}${SEPARATOR}${NC}\n"
}

log_subheader() {
    log_raw "\n${GRAY}${THIN_SEPARATOR}${NC}"
    log_raw "${CYAN}${1}${NC}"
    log_raw "${GRAY}${THIN_SEPARATOR}${NC}"
}

log_step() {
    log_raw "${PURPLE}▶ [STEP $1/$2]${NC} $3"
}

# =============================================================================
# Utility Functions
# =============================================================================
run_sudo() {
    if [ "$(id -u)" = "0" ]; then 
        "$@"
    else 
        sudo -E "$@"
    fi
}

create_logs_dir() {
    mkdir -p "$PROJECT_DIR/logs" 2>/dev/null || true
}

get_public_ipv4() {
    log_info "Detecting public IPv4 address..." >&2
    local ipv4=$(curl -4 -s --connect-timeout 5 ifconfig.co 2>/dev/null || \
                 curl -4 -s --connect-timeout 5 icanhazip.com 2>/dev/null || \
                 curl -4 -s --connect-timeout 5 ipinfo.io/ip 2>/dev/null)
    echo "$ipv4"
}

get_public_ipv6() {
    log_info "Detecting public IPv6 address..." >&2
    local ipv6=$(curl -6 -s --connect-timeout 5 ifconfig.co 2>/dev/null || \
                 curl -6 -s --connect-timeout 5 icanhazip.com 2>/dev/null)
    echo "$ipv6"
}

get_public_ip() {
    local ipv4=$(get_public_ipv4)
    if [ -n "$ipv4" ]; then
        echo "$ipv4"
    else
        get_public_ipv6
    fi
}

show_progress_bar() {
    local duration=$1
    local message=$2
    local width=50
    
    echo -ne "${BLUE}${message}${NC} ["
    for ((i=1; i<=duration; i++)); do
        local progress=$((i * width / duration))
        printf "\r${BLUE}${message}${NC} ["
        printf "${GREEN}%${progress}s${NC}" | tr ' ' '█'
        printf "%$((width - progress))s" | tr ' ' '░'
        printf "] %d%%" $((i * 100 / duration))
        sleep 0.1
    done
    echo -e "] ${GREEN}${SUCCESS_ICON}${NC}"
}

confirm_action() {
    local prompt="$1"
    local default="${2:-N}"
    
    if [ "$default" = "Y" ]; then
        read -p "${YELLOW}${WARNING_ICON} ${prompt} [Y/n]: ${NC}" response
        response=${response:-Y}
    else
        read -p "${YELLOW}${WARNING_ICON} ${prompt} [y/N]: ${NC}" response
        response=${response:-N}
    fi
    
    [[ "$response" =~ ^[Yy]$ ]]
}

press_any_key() {
    echo -e "\n${GRAY}Press Enter to continue...${NC}"
    read -r
}

# =============================================================================
# Main Menu
# =============================================================================
show_menu() {
    clear
    create_logs_dir
    
    local server_ip=$(get_public_ip)
    local docker_version=$(docker --version 2>/dev/null | cut -d' ' -f3 | tr -d ',' || echo "Not installed")
    local compose_version=$(docker compose version 2>/dev/null | cut -d' ' -f4 || echo "Not installed")
    
    log_raw "${CYAN}${SEPARATOR}${NC}"
    log_raw "${WHITE}                ${HEADER_ICON} uSipipo VPN Manager v2.0 ${HEADER_ICON}${NC}"
    log_raw "${CYAN}${SEPARATOR}${NC}"
    
    log_subheader "System Information"
    log_raw "${BLUE}  📍 Server IP:${NC}        ${GREEN}${server_ip:-Not detected}${NC}"
    log_raw "${BLUE}  📁 Project Root:${NC}     ${YELLOW}${PROJECT_DIR}${NC}"
    log_raw "${BLUE}  🐳 Docker:${NC}           ${docker_version}"
    log_raw "${BLUE}  🔧 Compose:${NC}          ${compose_version}"
    log_raw "${BLUE}  ⏰ System Time:${NC}      $(date '+%Y-%m-%d %H:%M:%S %Z')"
    
    log_subheader "Available Actions"
    log_raw ""
    log_raw "  ${GREEN}1)${NC} 🐳 Install Docker & Docker Compose"
    log_raw "  ${YELLOW}2)${NC} ▶️  Start VPN Services ${GRAY}(Outline + WireGuard + Pi-hole)${NC}"
    log_raw "  ${BLUE}3)${NC} 📊 Show Service Status & Logs"
    log_raw "  ${PURPLE}4)${NC} 🔄 Restart Services"
    log_raw "  ${CYAN}5)${NC} 📝 View/Edit Environment Configuration"
    log_raw "  ${RED}6)${NC} ⏹️  Stop VPN Services"
    log_raw "  ${RED}7)${NC} 🔥 Complete Uninstall ${GRAY}(Remove everything)${NC}"
    log_raw "  ${WHITE}8)${NC} 👋 Exit"
    log_raw ""
    log_raw "${CYAN}${SEPARATOR}${NC}"
    
    read -p "$(echo -e ${WHITE}Select option [1-8]:${NC} )" choice
    
    case $choice in
        1) install_docker ;;
        2) start_services ;;
        3) show_status ;;
        4) restart_services ;;
        5) edit_env_config ;;
        6) stop_services ;;
        7) uninstall_docker ;;
        8) log_info "Thank you for using uSipipo VPN Manager! 👋"; exit 0 ;;
        *) 
            log_error "Invalid option. Please select a number between 1-8."
            sleep 2
            show_menu
            ;;
    esac
}

# =============================================================================
# Docker Installation (Updated for Ubuntu & Debian)
# =============================================================================
install_docker() {
    log_header "🐳 DOCKER & DOCKER COMPOSE INSTALLATION"
    
    # Check if already installed
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        log_warning "Docker and Docker Compose are already installed."
        if ! confirm_action "Do you want to reinstall?"; then
            show_menu
            return
        fi
    fi
    
    # 1. OS Detection
    log_step "1" "6" "Detecting Operating System..."
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_ID=$ID
    else
        log_error "Could not detect OS. /etc/os-release not found."
        return 1
    fi

    # Configurar URLs basadas en la distro
    local GPG_URL=""
    local REPO_URL=""
    
    case "$OS_ID" in
        ubuntu)
            log_info "Detected OS: Ubuntu"
            GPG_URL="https://download.docker.com/linux/ubuntu/gpg"
            REPO_URL="https://download.docker.com/linux/ubuntu"
            ;;
        debian)
            log_info "Detected OS: Debian"
            GPG_URL="https://download.docker.com/linux/debian/gpg"
            REPO_URL="https://download.docker.com/linux/debian"
            ;;
        *)
            log_error "Unsupported OS: $OS_ID. Only Ubuntu and Debian are supported."
            press_any_key
            show_menu
            return 1
            ;;
    esac

    log_step "2" "6" "Updating system package lists..."
    run_sudo apt-get update > /dev/null 2>&1
    log_success "Package lists updated successfully"
    
    log_step "3" "6" "Installing required dependencies..."
    run_sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        apt-transport-https \
        software-properties-common > /dev/null 2>&1
    log_success "Dependencies installed"
    
    log_step "4" "6" "Configuring Docker official repository..."
    if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
        run_sudo mkdir -p /etc/apt/keyrings
        curl -fsSL "$GPG_URL" | \
            run_sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg > /dev/null 2>&1
        log_success "Docker GPG key added to system keyring"
    else
        log_info "Docker GPG key already exists, skipping..."
    fi
    
    # Añadir el repositorio usando las variables dinámicas
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] $REPO_URL $(lsb_release -cs) stable" | \
        run_sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    log_success "Docker repository configured for $OS_ID"
    
    log_step "5" "6" "Installing Docker Engine and Docker Compose..."
    run_sudo apt-get update > /dev/null 2>&1
    run_sudo apt-get install -y \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-compose-plugin > /dev/null 2>&1
        
    # Verificar instalación
    if command -v docker &> /dev/null; then
        log_success "Docker CE $(docker --version | cut -d' ' -f3 | tr -d ',') installed"
        log_success "Docker Compose $(docker compose version | cut -d' ' -f4) installed"
    else
        log_error "Docker installation failed."
        return 1
    fi
    
    log_step "6" "6" "Configuring user permissions and system settings..."
    run_sudo usermod -aG docker $USER
    run_sudo systemctl enable docker > /dev/null 2>&1
    run_sudo systemctl start docker > /dev/null 2>&1
    log_success "User '$USER' added to 'docker' group"
    log_success "Docker service enabled and started"
    
    log_header "✅ INSTALLATION COMPLETED SUCCESSFULLY"
    log_warning "IMPORTANT: You need to log out and log back in for group changes to take effect."
    log_info "Alternatively, run: newgrp docker"
    
    press_any_key
    show_menu
}


# =============================================================================
# Service Startup
# =============================================================================
start_services() {
    log_header "🚀 STARTING VPN SERVICES"
    
        # Variables para el .env
    local SERVER_IPV4=""
    local SERVER_IPV6=""
    local SERVER_IP=""
    local PIHOLE_WEBPASS=""
    local PIHOLE_WEB_PORT=""
    local PIHOLE_DNS="8.8.8.8;1.1.1.1"
    local WIREGUARD_PORT=""
    local WIREGUARD_PUBLIC_KEY=""
    local WIREGUARD_ENDPOINT=""
    local WIREGUARD_PATH="/config"
    local OUTLINE_API_PORT=""
    local OUTLINE_API_URL=""
    local OUTLINE_API_SECRET=""  # <--- IMPORTANTE
    local OUTLINE_CERT_SHA256=""
    local PRESERVE_CERTS="false"
    local TELEGRAM_TOKEN=""
    local AUTHORIZED_USERS=""
    
    # =========================================================================
    # STEP 1: IP Detection
    # =========================================================================
    log_step "1" "8" "Detecting server network configuration..."
    
    SERVER_IPV4=$(get_public_ipv4)
    SERVER_IPV6=$(get_public_ipv6)
    
    if [ -n "$SERVER_IPV4" ]; then
        SERVER_IP="$SERVER_IPV4"
        log_success "IPv4 detected: ${SERVER_IPV4}"
    elif [ -n "$SERVER_IPV6" ]; then
        SERVER_IP="$SERVER_IPV6"
        log_success "IPv6 detected: ${SERVER_IPV6}"
    else
        log_error "Failed to detect public IP address. Outline requires a valid public IP."
        log_warning "Please check your internet connection and firewall settings."
        press_any_key
        show_menu
        return 1
    fi
    
    [ -n "$SERVER_IPV6" ] && log_info "IPv6 also available: ${SERVER_IPV6}"
    
    #    # =========================================================================
    # STEP 2: Generate Random Ports and Passwords
    # =========================================================================
    log_step "2" "8" "Generating secure random configuration..."
    
    PIHOLE_WEBPASS=$(tr -dc 'A-Za-z0-9!@#$%^&*' </dev/urandom | head -c 16)
    PIHOLE_WEB_PORT=$((10000 + RANDOM % 50000))
    WIREGUARD_PORT=$((10000 + RANDOM % 50000))
    
    # --- CORRECCIÓN OUTLINE ---
    # Generamos dos puertos distintos para evitar conflicto de protocolos
    OUTLINE_API_PORT=$((10000 + RANDOM % 50000))
    OUTLINE_KEYS_PORT=$((10000 + RANDOM % 50000))
    
    # Aseguramos que no sean el mismo puerto ni colisionen con otros
    while [[ "$OUTLINE_KEYS_PORT" == "$OUTLINE_API_PORT" || \
             "$OUTLINE_KEYS_PORT" == "$WIREGUARD_PORT" || \
             "$OUTLINE_KEYS_PORT" == "$PIHOLE_WEB_PORT" ]]; do
        OUTLINE_KEYS_PORT=$((10000 + RANDOM % 50000))
    done
    
    OUTLINE_API_SECRET=$(tr -dc 'a-zA-Z0-9' </dev/urandom | head -c 32)
    
    log_success "Pi-hole password: ${PIHOLE_WEBPASS:0:4}****** (16 characters)"
    log_success "Pi-hole web port: ${PIHOLE_WEB_PORT}"
    log_success "WireGuard port: ${WIREGUARD_PORT}"
    log_success "Outline API port: ${OUTLINE_API_PORT}"
    log_success "Outline Keys port: ${OUTLINE_KEYS_PORT}"
    
    # =========================================================================
    # STEP 3: Create Preliminary .env
    # =========================================================================
    log_step "3" "8" "Creating preliminary environment configuration..."
    
    cat > "$ENV_FILE" <<EOF
# =============================================================================
# uSipipo VPN Manager - Auto-Generated Configuration
# Generated: $(date '+%Y-%m-%d %H:%M:%S %Z')
# =============================================================================

# Telegram Bot Configuration
TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
AUTHORIZED_USERS=${AUTHORIZED_USERS}

# Server Network Configuration
SERVER_IPV4=${SERVER_IPV4}
SERVER_IPV6=${SERVER_IPV6}
SERVER_IP=${SERVER_IP}

# Pi-hole Configuration
PIHOLE_WEB_PORT=${PIHOLE_WEB_PORT}
PIHOLE_WEBPASS=${PIHOLE_WEBPASS}
PIHOLE_DNS=${PIHOLE_DNS}

# WireGuard Configuration
WIREGUARD_PORT=${WIREGUARD_PORT}
WIREGUARD_PUBLIC_KEY=${WIREGUARD_PUBLIC_KEY}
WIREGUARD_ENDPOINT=${WIREGUARD_ENDPOINT}
WIREGUARD_PATH=${WIREGUARD_PATH}

# Outline Configuration
OUTLINE_API_URL=${OUTLINE_API_URL}
OUTLINE_API_SECRET=${OUTLINE_API_SECRET}
OUTLINE_API_PORT=${OUTLINE_API_PORT}
OUTLINE_KEYS_PORT=${OUTLINE_KEYS_PORT}
OUTLINE_CERT_SHA256=${OUTLINE_CERT_SHA256}
PRESERVE_CERTS=${PRESERVE_CERTS}

# =============================================================================
# End of Configuration
# =============================================================================
EOF
    
    log_success "Preliminary .env file created at: ${ENV_FILE}"
    
    # =========================================================================
    # STEP 4: Determine Docker Command
    # =========================================================================
    log_step "4" "8" "Preparing Docker environment..."
    
    local CMD DOCKER_CMD
    if groups | grep -q docker; then
        CMD="docker compose"
        DOCKER_CMD="docker"
        log_success "Docker commands will run without sudo"
    else
        CMD="run_sudo docker compose"
        DOCKER_CMD="run_sudo docker"
        log_warning "Docker commands will require sudo privileges"
    fi
    
    # =========================================================================
    # STEP 5: Clean Previous Volumes (Optional)
    # =========================================================================
    log_step "5" "8" "Cleaning previous Outline data..."
    
    if [ "$PRESERVE_CERTS" != "true" ]; then
        $DOCKER_CMD volume rm outline_data 2>/dev/null && \
            log_success "Previous Outline volume removed" || \
            log_info "No previous volume found"
    else
        log_info "Certificate preservation enabled, keeping existing volume"
    fi
    
    # =========================================================================
    # STEP 6: Generate SSL Certificates for Outline
    # =========================================================================
    log_step "6" "8" "Generating SSL certificates and configuration..."
    
    # 2. Asegurar que el volumen existe
    $DOCKER_CMD volume create outline_data 2>/dev/null || true
    
    # 3. Generar archivos dentro del volumen usando la ruta NATIVA (/opt/outline/persisted-state)
    # Usamos una imagen Alpine para escribir en el volumen antes de arrancar Outline
    $DOCKER_CMD run --rm -v outline_data:/opt/outline/persisted-state alpine sh -c "
        set -e
        apk add --no-cache openssl >/dev/null 2>&1
        
        # Crear directorio si no existe (aunque el volumen lo maneja)
        mkdir -p /opt/outline/persisted-state
        cd /opt/outline/persisted-state
        
        echo '--- Generating Certificates ---'
        if [ ! -f shadowbox-selfsigned.crt ]; then
            openssl req -x509 -nodes -days 36500 -newkey rsa:2048 \
                -subj '/CN=${SERVER_IP}' \
                -keyout shadowbox-selfsigned.key \
                -out shadowbox-selfsigned.crt 2>&1
        else
            echo 'Certificates already exist.'
        fi
        
        echo '--- Generating Server Config ---'
        # Outline necesita este archivo para saber su ID y Puerto
        # Esto evita que intente autoconfigurarse y falle
        cat <<EOF > shadowbox_server_config.json
{
  \"rolloutId\": \"vpn-manager-$(date +%s)\",
  \"portForNewAccessKeys\": ${OUTLINE_KEYS_PORT},
  \"hostname\": \"${SERVER_IP}\",
  \"created\": $(date +%s)000
}
EOF

        # 4. CORRECCIÓN DE PERMISOS
        # Damos permisos de lectura global a los certificados y config
        # Esto soluciona el error 'ENOENT' si el usuario del contenedor no es root
        chmod 644 shadowbox-selfsigned.crt
        chmod 644 shadowbox_server_config.json
        chmod 600 shadowbox-selfsigned.key
        
        echo '--- File Verification ---'
        ls -lh /opt/outline/persisted-state/
    "
    
    if [ $? -eq 0 ]; then
        log_success "Configuration generated successfully in /opt/outline/persisted-state"
    else
        log_error "Failed to generate configuration files"
        return 1
    fi
    
    # =========================================================================
    # STEP 6.5: Configure Kernel Networking
    # =========================================================================
    log_info "Configuring host kernel for WIREGUARD VPN routing..."
    
    # Aplicar configuraciones en caliente
    run_sudo sysctl -w net.ipv4.ip_forward=1 > /dev/null
    run_sudo sysctl -w net.ipv4.conf.all.src_valid_mark=1 > /dev/null
    run_sudo sysctl -w net.ipv6.conf.all.disable_ipv6=0 > /dev/null

    # Hacerlo persistente tras reiniciar
    echo -e "net.ipv4.ip_forward=1\nnet.ipv4.conf.all.src_valid_mark=1\nnet.ipv6.conf.all.disable_ipv6=0" | \
        run_sudo tee /etc/sysctl.d/99-vpn-manager.conf > /dev/null
    
    run_sudo sysctl -p /etc/sysctl.d/99-vpn-manager.conf > /dev/null
    
    log_success "Kernel IP forwarding enabled successfully"


    # Hacerlo persistente tras reiniciar
    sudo tee /etc/sysctl.d/99-vpn-manager.conf > /dev/null <<EOF
net.ipv4.ip_forward=1
net.ipv4.conf.all.src_valid_mark=1
net.ipv6.conf.all.disable_ipv6=0
EOF
    sudo sysctl -p /etc/sysctl.d/99-vpn-manager.conf
    
    # Creamos el archivo wg0.conf con las reglas de IPTABLES (PostUp/PostDown)
    # Esto es vital para que haya internet.
    log_info "Injecting NAT/Masquerade rules into wg0.conf..."
    

    # =========================================================================
    # STEP 7: Start Docker Containers
    # =========================================================================
    log_step "7" "8" "Starting Docker containers..."
    
    $CMD up -d --remove-orphans 2>&1 | grep -v "Pulling" || true
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "Containers started: outline, wireguard, pihole"
    else
        log_error "Failed to start containers"
        log_info "Run 'docker compose logs' for detailed error information"
        press_any_key
        show_menu
        return 1
    fi
    
    # =========================================================================
    # STEP 8: Wait for Outline Configuration
    # =========================================================================
    log_step "8" "8" "Waiting for Outline to initialize..."
    
    local MAX_RETRIES=60
    local COUNT=0
    local SUCCESS=false
    
    echo -ne "${BLUE}Progress: [${NC}"
    
    while [ $COUNT -lt $MAX_RETRIES ]; do
        # Check container health status
        local STATUS=$($DOCKER_CMD inspect -f '{{.State.Status}}' outline 2>/dev/null || echo "missing")
        
        # Si el contenedor está reiniciando constantemente, hay un error fatal
        if [ "$STATUS" == "restarting" ] || [ "$STATUS" == "dead" ] || [ "$STATUS" == "exited" ]; then
            echo -e "${NC}]"
            log_error "Outline container failed with status: ${STATUS}"
            log_subheader "Container Debug Logs"
            $DOCKER_CMD logs outline --tail 50
            
            # Verificar contenido del volumen usando la MISMA RUTA que el contenedor
            log_subheader "Volume Content Verification"
            log_info "Listing /opt/outline/persisted-state inside volume..."
            
            $DOCKER_CMD run --rm -v outline_data:/opt/outline/persisted-state alpine \
                ls -la /opt/outline/persisted-state/ 2>&1 | while read line; do
                    log_info "  $line"
                done
            
            press_any_key
            show_menu
            return 1
        fi
        
        # Check for configuration file existence
        # CORREGIDO: Usamos la ruta /opt/outline/persisted-state para coincidir con el montaje del paso 6
        if $DOCKER_CMD run --rm -v outline_data:/opt/outline/persisted-state alpine \
            test -f /opt/outline/persisted-state/shadowbox_server_config.json > /dev/null 2>&1; then
            SUCCESS=true
            echo -e "${GREEN}█${NC}] ${SUCCESS_ICON}"
            break
        fi
        
        echo -ne "${GREEN}█${NC}"
        sleep 1
        COUNT=$((COUNT+1))
    done
    
    if [ "$SUCCESS" != "true" ]; then
        echo -e "${NC}]"
        log_error "Timeout waiting for Outline configuration (waited ${MAX_RETRIES}s)"
        log_warning "The service may still be initializing. Check logs with option 3."
        
        press_any_key
        show_menu
        return 1
    fi
    
    log_success "Outline initialized successfully in ${COUNT} seconds"

    
    # =========================================================================
    # Extract Service Credentials
    # =========================================================================
    log_subheader "Finalizing Configuration"
    
    # Construir la API URL
    OUTLINE_API_URL="https://${SERVER_IP}:${OUTLINE_API_PORT}/${OUTLINE_API_SECRET}"
    log_success "Outline API URL constructed"

    # Extract Certificate SHA256
    # CORREGIDO: Usar ruta consistente /opt/outline/persisted-state
    log_info "Calculating SSL certificate fingerprint..."
    OUTLINE_CERT_SHA256=$($DOCKER_CMD run --rm -v outline_data:/opt/outline/persisted-state alpine sh -c \
        "apk add --no-cache openssl >/dev/null 2>&1 && \
        openssl x509 -in /opt/outline/persisted-state/shadowbox-selfsigned.crt -noout -fingerprint -sha256" 2>/dev/null | \
        cut -d= -f2 | tr -d :)
    
    if [ -n "$OUTLINE_CERT_SHA256" ]; then
        log_success "Certificate SHA256: ${OUTLINE_CERT_SHA256:0:40}..."
    else
        log_error "Failed to extract certificate fingerprint"
        OUTLINE_CERT_SHA256="MANUAL_CHECK_REQUIRED"
    fi
    
    # WireGuard Public Key
    log_info "Waiting for WireGuard keys..."
    sleep 3
    WIREGUARD_PUBLIC_KEY=$($DOCKER_CMD exec wireguard cat /config/server/publickey 2>/dev/null | tr -d '[:space:]' || echo "")
    
    if [ -z "$WIREGUARD_PUBLIC_KEY" ]; then
         WIREGUARD_PUBLIC_KEY=$($DOCKER_CMD exec wireguard wg show wg0 public-key 2>/dev/null || echo "PENDING")
    fi
    log_success "WireGuard Key: ${WIREGUARD_PUBLIC_KEY:0:20}..."
    
    
    # =========================================================================
    # Generate Final .env File
    # =========================================================================
    log_subheader "Generating Final Environment Configuration"
    
    cat > "$ENV_FILE" <<EOF
# =============================================================================
# uSipipo VPN Manager - Production Configuration
# Generated: $(date '+%Y-%m-%d %H:%M:%S %Z')
# =============================================================================

# Telegram Bot Configuration
TELEGRAM_TOKEN=${TELEGRAM_TOKEN:-your_telegram_bot_token_here}
AUTHORIZED_USERS=${AUTHORIZED_USERS:-123456789}

# Server Network Configuration
SERVER_IPV4=${SERVER_IPV4}
SERVER_IPV6=${SERVER_IPV6}
SERVER_IP=${SERVER_IP}

# Pi-hole Configuration
PIHOLE_WEB_PORT=${PIHOLE_WEB_PORT}
PIHOLE_WEBPASS=${PIHOLE_WEBPASS}
PIHOLE_DNS=${PIHOLE_DNS}

# WireGuard Configuration
WIREGUARD_PORT=${WIREGUARD_PORT}
WIREGUARD_PUBLIC_KEY=${WIREGUARD_PUBLIC_KEY}
WIREGUARD_ENDPOINT=${SERVER_IP}:${WIREGUARD_PORT}
WIREGUARD_PATH=${WIREGUARD_PATH}

# Outline Configuration
# Esta variable es INYECTADA en docker-compose como SB_API_PREFIX
OUTLINE_API_SECRET=${OUTLINE_API_SECRET}
OUTLINE_API_PORT=${OUTLINE_API_PORT}
OUTLINE_KEYS_PORT=${OUTLINE_KEYS_PORT}
OUTLINE_API_URL=${OUTLINE_API_URL}
OUTLINE_CERT_SHA256=${OUTLINE_CERT_SHA256}
PRESERVE_CERTS=${PRESERVE_CERTS}

# Node Environment
NODE_ENV=production
EOF
    
    log_success "Final .env configuration saved to: ${ENV_FILE}"
    
    # =========================================================================
    # Display Results
    # =========================================================================
    clear
    log_header "🎉 INSTALLATION COMPLETED SUCCESSFULLY"
    
    log_subheader "📋 Service Access Information"
    
    echo -e "\n${CYAN}┌─ Pi-hole (Ad Blocking DNS) ────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│${NC} ${BLUE}Web Interface:${NC} http://${SERVER_IP}:${PIHOLE_WEB_PORT}/admin"
    echo -e "${CYAN}│${NC} ${BLUE}Admin Password:${NC} ${GREEN}${PIHOLE_WEBPASS}${NC}"
    echo -e "${CYAN}│${NC} ${GRAY}Configure your devices to use this DNS for ad blocking${NC}"
    echo -e "${CYAN}└────────────────────────────────────────────────────────────────┘${NC}\n"
    
    echo -e "${CYAN}┌─ WireGuard VPN ────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│${NC} ${BLUE}Endpoint:${NC} ${GREEN}${WIREGUARD_ENDPOINT}${NC}"
    echo -e "${CYAN}│${NC} ${BLUE}Public Key:${NC} ${GREEN}${WIREGUARD_PUBLIC_KEY}${NC}"
    echo -e "${CYAN}│${NC} ${GRAY}Use the Telegram bot to generate client configurations${NC}"
    echo -e "${CYAN}└────────────────────────────────────────────────────────────────┘${NC}\n"
    
    echo -e "${CYAN}┌─ Outline VPN ──────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│${NC} ${BLUE}API URL:${NC} ${GREEN}${OUTLINE_API_URL}${NC}"
    echo -e "${CYAN}│${NC}"
    echo -e "${CYAN}│${NC} ${YELLOW}Manager Configuration (Copy this):${NC}"
    echo -e "${CYAN}│${NC} ${WHITE}{\"apiUrl\":\"${OUTLINE_API_URL}\",\"certSha256\":\"${OUTLINE_CERT_SHA256}\"}${NC}"
    echo -e "${CYAN}│${NC}"
    echo -e "${CYAN}│${NC} ${GRAY}1. Download Outline Manager from getoutline.org/get-started${NC}"
    echo -e "${CYAN}│${NC} ${GRAY}2. Click 'Set up Outline anywhere'${NC}"
    echo -e "${CYAN}│${NC} ${GRAY}3. Paste the configuration above${NC}"
    echo -e "${CYAN}└────────────────────────────────────────────────────────────────┘${NC}\n"
    
    log_subheader "📝 Next Steps"
    echo -e "  ${GREEN}1.${NC} Edit ${YELLOW}.env${NC} file to add your Telegram bot token"
    echo -e "  ${GREEN}2.${NC} Add authorized user IDs to the AUTHORIZED_USERS variable"
    echo -e "  ${GREEN}3.${NC} Restart services (option 4 in menu) after editing .env"
    echo -e "  ${GREEN}4.${NC} Configure Outline Manager with the JSON above"
    echo -e "  ${GREEN}5.${NC} Start the Telegram bot: ${CYAN}cd bot && npm install && npm start${NC}\n"
    
    log_warning "Save the credentials above in a secure location!"
    
    press_any_key
    show_menu
}

# =============================================================================
# Service Status
# =============================================================================
show_status() {
    log_header "📊 SYSTEM STATUS & DIAGNOSTICS"
    
    local CMD DOCKER_CMD
    if groups | grep -q docker; then
        CMD="docker compose"
        DOCKER_CMD="docker"
    else
        CMD="run_sudo docker compose"
        DOCKER_CMD="run_sudo docker"
    fi
    
    log_subheader "Container Status"
    $CMD ps
    
    log_subheader "Resource Usage"
    $DOCKER_CMD stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    
    log_subheader "Service Health Check"
    
    # Check Outline
    if $DOCKER_CMD ps --filter "name=outline" --filter "status=running" | grep -q outline; then
        log_success "Outline VPN: Running"
    else
        log_error "Outline VPN: Not running"
    fi
    
    # Check WireGuard
    if $DOCKER_CMD ps --filter "name=wireguard" --filter "status=running" | grep -q wireguard; then
        log_success "WireGuard VPN: Running"
    else
        log_error "WireGuard VPN: Not running"
    fi
    
    # Check Pi-hole
    if $DOCKER_CMD ps --filter "name=pihole" --filter "status=running" | grep -q pihole; then
        log_success "Pi-hole DNS: Running"
    else
        log_error "Pi-hole DNS: Not running"
    fi
    
    log_subheader "Recent Logs"
    read -p "$(echo -e ${YELLOW}Show container logs? [y/N]:${NC} )" show_logs
    
    if [[ "$show_logs" =~ ^[Yy]$ ]]; then
        echo -e "\n${CYAN}Select container:${NC}"
        echo "  1) Outline"
        echo "  2) WireGuard"
        echo "  3) Pi-hole"
        echo "  4) All"
        read -p "Choice [1-4]: " log_choice
        
        case $log_choice in
            1) $DOCKER_CMD logs --tail 50 outline ;;
            2) $DOCKER_CMD logs --tail 50 wireguard ;;
            3) $DOCKER_CMD logs --tail 50 pihole ;;
            4) 
                log_subheader "Outline Logs"
                $DOCKER_CMD logs --tail 20 outline
                log_subheader "WireGuard Logs"
                $DOCKER_CMD logs --tail 20 wireguard
                log_subheader "Pi-hole Logs"
                $DOCKER_CMD logs --tail 20 pihole
                ;;
        esac
    fi
    
    press_any_key
    show_menu
}


# =============================================================================
# Restart Services
# =============================================================================
restart_services() {
    log_header "🔄 RESTARTING VPN SERVICES"
    
    local CMD
    if groups | grep -q docker; then
        CMD="docker compose"
    else
        CMD="run_sudo docker compose"
    fi
    
    log_info "Stopping containers..."
    $CMD down
    
    log_info "Starting containers with updated configuration..."
    $CMD up -d
    
    log_success "Services restarted successfully"
    
    press_any_key
    show_menu
}

# =============================================================================
# View/Edit Environment Configuration
# =============================================================================
edit_env_config() {
    log_header "📝 ENVIRONMENT CONFIGURATION"
    
    if [ ! -f "$ENV_FILE" ]; then
        log_error ".env file not found at: ${ENV_FILE}"
        log_info "Please run option 2 (Start VPN Services) first to generate it."
        press_any_key
        show_menu
        return
    fi
    
    log_info "Current configuration file: ${ENV_FILE}"
    echo ""
    
    cat "$ENV_FILE"
    
    echo ""
    read -p "$(echo -e ${YELLOW}Do you want to edit this file? [y/N]:${NC} )" edit_choice
    
    if [[ "$edit_choice" =~ ^[Yy]$ ]]; then
        local editor="${EDITOR:-nano}"
        
        if ! command -v "$editor" &> /dev/null; then
            editor="vi"
        fi
        
        log_info "Opening file with ${editor}..."
        $editor "$ENV_FILE"
        
        log_success "File saved"
        log_warning "Remember to restart services (option 4) to apply changes"
    fi
    
    press_any_key
    show_menu
}

# =============================================================================
# Stop Services
# =============================================================================
stop_services() {
    log_header "⏹️ STOPPING VPN SERVICES"
    
    if ! confirm_action "Are you sure you want to stop all services?"; then
        log_info "Operation cancelled"
        show_menu
        return
    fi
    
    local CMD
    if groups | grep -q docker; then
        CMD="docker compose"
    else
        CMD="run_sudo docker compose"
    fi
    
    local WIREGUARD
    local OUTLINE 
    local PIHOLE 
    
    log_info "Stopping containers..."
    $CMD down WIREGUARD OUTLINE PIHOLE
    
    log_success "All services stopped successfully"
    log_info "Data volumes preserved. Use option 2 to restart services."
    
    press_any_key
    show_menu
}

# =============================================================================
# Complete Uninstallation
# =============================================================================
uninstall_docker() {
    log_header "🔥 COMPLETE DOCKER UNINSTALLATION"
    
    log_error "⚠️  WARNING: This action is IRREVERSIBLE!"
    echo -e "${RED}This will remove:${NC}"
    echo -e "  • All Docker containers"
    echo -e "  • All Docker images"
    echo -e "  • All Docker volumes (including VPN configurations)"
    echo -e "  • All Docker networks"
    echo -e "  • Docker Engine itself"
    echo ""
    
    if ! confirm_action "Type 'Y' to proceed with complete removal" "N"; then
        log_info "Uninstallation cancelled"
        show_menu
        return
    fi
    
    read -p "$(echo -e ${RED}Type 'DELETE EVERYTHING' to confirm:${NC} )" final_confirm
    
    if [ "$final_confirm" != "DELETE EVERYTHING" ]; then
        log_info "Confirmation failed. Uninstallation cancelled."
        show_menu
        return
    fi
    
    local DOCKER_CMD
    if groups | grep -q docker; then
        DOCKER_CMD="docker"
    else
        DOCKER_CMD="run_sudo docker"
    fi
    
    log_step "1" "5" "Stopping all running containers..."
    run_sudo docker stop $($DOCKER_CMD ps -aq) 2>/dev/null || true
    log_success "All containers stopped"
    
    log_step "2" "5" "Removing all containers..."
    run_sudo docker rm -f $($DOCKER_CMD ps -aq) 2>/dev/null || true
    log_success "All containers removed"
    
    log_step "3" "5" "Removing all volumes..."
    run_sudo docker volume rm $($DOCKER_CMD volume ls -q) 2>/dev/null || true
    log_success "All volumes removed"
    
    log_step "4" "5" "Removing all images and cached data..."
    run_sudo docker system prune -a -f --volumes > /dev/null 2>&1
    log_success "System cleaned"
    
    log_step "5" "5" "Removing Docker packages..."
    run_sudo apt-get purge -y \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-compose-plugin \
        docker-compose 2>/dev/null || true
    run_sudo apt-get autoremove -y > /dev/null 2>&1
    run_sudo rm -rf /var/lib/docker /etc/docker /var/lib/containerd 2>/dev/null || true
    log_success "Docker packages removed"
    
    if [ -f "$ENV_FILE" ]; then
        rm -f "$ENV_FILE"
        log_success "Environment configuration file removed"
    fi
    
    log_header "✅ UNINSTALLATION COMPLETED"
    log_info "Docker and all related data have been completely removed from your system"
    
    press_any_key
    show_menu
}

# =============================================================================
# Main Execution
# =============================================================================
main() {
    # Ensure script is run with proper permissions
    if [ "$EUID" -eq 0 ]; then
        log_warning "This script should not be run as root directly"
        log_info "It will request sudo access when needed"
    fi
    
    # Create logs directory
    create_logs_dir
    
    # Start logging
    log_info "uSipipo VPN Manager v2.0 started"
    log_info "Script directory: ${SCRIPT_DIR}"
    log_info "Log file: ${LOG_FILE}"
    
    # Show main menu
    show_menu
}

# Run main function
main