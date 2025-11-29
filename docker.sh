#!/bin/bash
set -e

# =============================================================================
# uSipipo VPN Manager v2.0 - Professional Docker Management Script
# Author: uSipipo Team
# Description: Automated VPN setup with Outline, WireGuard, and Pi-hole
# =============================================================================

# Colores y estilos
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Separadores
SEPARATOR="═══════════════════════════════════════════════════════════════════════════════"
DOUBLE_SEPARATOR="═══════════════════════════════════════════════════════════════════════════════"

# Funciones de logging profesional
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%H:%M:%S') - $1"
}

log_header() {
    echo -e "\n${CYAN}${SEPARATOR}${NC}"
    echo -e "${WHITE}$1${NC}"
    echo -e "${CYAN}${SEPARATOR}${NC}\n"
}

log_step() {
    echo -e "${PURPLE}[STEP $1]${NC} $2"
}

# Variables del sistema
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$SCRIPT_DIR"
ENV_FILE="$PROJECT_DIR/.env"
DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"

# Funciones de ayuda
run_sudo() {
    if [ "$(id -u)" = "0" ]; then "$@"; else sudo -E "$@"; fi
}

get_public_ip() {
    log_info "Detecting public IP address..."
    IP=$(curl -4 -s --connect-timeout 5 ifconfig.co 2>/dev/null)
    if [ -z "$IP" ]; then
        IP=$(curl -6 -s --connect-timeout 5 ifconfig.co 2>/dev/null)
    fi
    echo "$IP"
}

show_progress() {
    local duration=$1
    local message=$2
    echo -ne "${BLUE}${message}${NC} "
    for ((i=1; i<=duration; i++)); do
        echo -ne "█"
        sleep 0.1
    done
    echo -e " ${GREEN}✓${NC}"
}

# Menú Principal
show_menu() {
    clear
    SERVER_IP=$(get_public_ip)

    echo -e "${CYAN}${DOUBLE_SEPARATOR}${NC}"
    echo -e "${WHITE}                    🚀 uSipipo VPN Manager v2.0${NC}"
    echo -e "${CYAN}${DOUBLE_SEPARATOR}${NC}"
    echo -e "${BLUE}📍 Server IP:${NC} ${GREEN}${SERVER_IP:-Not detected}${NC}"
    echo -e "${BLUE}📁 Project:${NC} ${YELLOW}$PROJECT_DIR${NC}"
    echo -e "${BLUE}⏰ Time:${NC} $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${CYAN}${SEPARATOR}${NC}"

    echo -e "${GREEN}1)${NC} 🐳 Install Docker & Docker Compose"
    echo -e "${YELLOW}2)${NC} ▶️  Start VPN Services (Outline + WireGuard + Pi-hole)"
    echo -e "${BLUE}3)${NC} 📊 Show Services Status"
    echo -e "${RED}4)${NC} ⏹️  Stop VPN Services"
    echo -e "${RED}5)${NC} 🔥 Complete Uninstall"
    echo -e "${WHITE}6)${NC} 👋 Exit"
    echo -e "${CYAN}${SEPARATOR}${NC}"

    read -p "Select option [1-6]: " choice

    case $choice in
        1) install_docker ;;
        2) start_services ;;
        3) show_status ;;
        4) stop_services ;;
        5) uninstall_docker ;;
        6) log_info "Goodbye! 👋"; exit 0 ;;
        *) log_error "Invalid option. Please select 1-6."; sleep 2; show_menu ;;
    esac
}

install_docker() {
    log_header "🐳 DOCKER INSTALLATION"

    log_step "1" "Updating package lists..."
    run_sudo apt-get update > /dev/null 2>&1
    log_success "Package lists updated"

    log_step "2" "Installing prerequisites..."
    run_sudo apt-get install -y ca-certificates curl gnupg lsb-release > /dev/null 2>&1
    log_success "Prerequisites installed"

    log_step "3" "Setting up Docker repository..."
    if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
        run_sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | run_sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg > /dev/null 2>&1
    fi

    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | run_sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    log_step "4" "Installing Docker components..."
    run_sudo apt-get update > /dev/null 2>&1
    run_sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin > /dev/null 2>&1

    log_step "5" "Configuring user permissions..."
    run_sudo usermod -aG docker $USER

    log_success "Docker installation completed!"
    log_warning "You may need to restart your session for Docker to work without sudo."

    echo -e "\n${YELLOW}Press Enter to continue...${NC}"
    read -r
    show_menu
}

start_services() {
    log_header "🚀 STARTING VPN SERVICES"

    # 1. IP Validation
    log_step "1" "Validating server IP..."
    SERVER_IP=$(get_public_ip)
    if [ -z "$SERVER_IP" ]; then
        log_error "Unable to detect public IP. Outline requires a valid IP address."
        echo -e "\n${YELLOW}Press Enter to return to menu...${NC}"
        read -r
        show_menu
        return
    fi
    log_success "IP detected: ${SERVER_IP}"

    # 2. Generate Configuration
    log_step "2" "Generating service configuration..."
    PIHOLE_PASS=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 12)
    OUTLINE_API_PORT=$((10000 + RANDOM % 50000))
    WIREGUARD_PORT=$((10000 + RANDOM % 50000))
    PIHOLE_WEB_PORT=$((10000 + RANDOM % 50000))

    cat > "$ENV_FILE" <<EOF
# Auto-generated configuration - $(date)
SERVER_IP=${SERVER_IP}
PIHOLE_WEBPASS=${PIHOLE_PASS}
PIHOLE_WEB_PORT=${PIHOLE_WEB_PORT}
WIREGUARD_PORT=${WIREGUARD_PORT}
OUTLINE_API_PORT=${OUTLINE_API_PORT}
EOF
    log_success "Configuration file created at ${ENV_FILE}"

    # 3. Start Containers
    log_step "3" "Preparing Docker environment..."
    if groups | grep -q docker; then
        CMD="docker compose"
        DOCKER_CMD="docker"
    else
        CMD="run_sudo docker compose"
        DOCKER_CMD="run_sudo docker"
    fi

    # Critical: Remove volume to prevent corruption
    log_info "Cleaning up previous Outline data volume..."
    $DOCKER_CMD volume rm outline_data 2>/dev/null || true

    log_step "4" "Starting containers..."
    $CMD up -d --remove-orphans > /dev/null 2>&1
    log_success "Containers started successfully"

    # 4. Active Waiting (Jigsaw Logic)
    log_step "5" "Waiting for Outline to generate certificates and configuration..."
    echo -e "${BLUE}⏳ Progress:${NC} ["

    MAX_RETRIES=40
    COUNT=0
    SUCCESS=false

    while [ $COUNT -lt $MAX_RETRIES ]; do
        # Check container status
        STATUS=$($DOCKER_CMD inspect -f '{{.State.Status}}' outline 2>/dev/null || echo "missing")

        if [ "$STATUS" == "restarting" ] || [ "$STATUS" == "dead" ] || [ "$STATUS" == "exited" ]; then
            echo -e "\n"
            log_error "Outline container failed (Status: $STATUS)"
            echo -e "${YELLOW}┌─ Outline Debug Logs ──────────────────────────────┐${NC}"
            $DOCKER_CMD logs outline --tail 20 | sed 's/^/│ /'
            echo -e "${YELLOW}└────────────────────────────────────────────────────┘${NC}"
            echo -e "\n${YELLOW}Press Enter to return to menu...${NC}"
            read -r
            show_menu
            return
        fi

        # Check for configuration file
        if $DOCKER_CMD run --rm -v outline_data:/opt/outline/persisted-state alpine test -f /opt/outline/persisted-state/shadowbox_server_config.json > /dev/null 2>&1; then
            SUCCESS=true
            echo -e "${GREEN}█] ✓${NC}"
            break
        fi

        echo -ne "${GREEN}█${NC}"
        sleep 2
        COUNT=$((COUNT+1))
    done

    if [ "$SUCCESS" != true ]; then
        echo -e "\n"
        log_error "Timeout waiting for Outline configuration. Service may not start properly."
        echo -e "\n${YELLOW}Press Enter to return to menu...${NC}"
        read -r
        show_menu
        return
    fi

    # 5. Extract Credentials
    log_step "6" "Extracting service credentials..."

    # Extract Secret ID
    SECRET_ID=$($DOCKER_CMD run --rm -v outline_data:/opt/outline/persisted-state alpine cat /opt/outline/persisted-state/shadowbox_server_config.json | grep -o '"managementUdpSecret":"[^"]*"' | cut -d'"' -f4)

    # Extract Certificate SHA256
    CERT_SHA=$($DOCKER_CMD run --rm -v outline_data:/opt/outline/persisted-state alpine openssl x509 -in /opt/outline/persisted-state/shadowbox-selfsigned.crt -noout -fingerprint -sha256 | cut -d= -f2 | tr -d :)

    # Build API URL
    API_URL="https://${SERVER_IP}:${OUTLINE_API_PORT}/${SECRET_ID}"

    # Generate Outline Manager JSON
    OUTLINE_ACCESS_CONFIG="{\"apiUrl\":\"${API_URL}\",\"certSha256\":\"${CERT_SHA}\"}"

    # Get WireGuard info
    WG_PUB_KEY=$($DOCKER_CMD exec wireguard wg show wg0 public-key 2>/dev/null || echo "Error retrieving key")

    # Display Results
    clear
    echo -e "${GREEN}${DOUBLE_SEPARATOR}${NC}"
    echo -e "${WHITE}              🎉 INSTALLATION COMPLETED SUCCESSFULLY! 🎉${NC}"
    echo -e "${GREEN}${DOUBLE_SEPARATOR}${NC}\n"

    echo -e "${CYAN}📋 SERVICE CONFIGURATION${NC}"
    echo -e "${SEPARATOR}"

    echo -e "${YELLOW}🌐 PI-HOLE (Ad Blocking)${NC}"
    echo -e "   ├─ Web Interface: ${GREEN}http://${SERVER_IP}:${PIHOLE_WEB_PORT}/admin${NC}"
    echo -e "   └─ Password: ${GREEN}${PIHOLE_PASS}${NC}\n"

    echo -e "${YELLOW}🔒 WIREGUARD VPN${NC}"
    echo -e "   ├─ Endpoint: ${GREEN}${SERVER_IP}:${WIREGUARD_PORT}${NC}"
    echo -e "   └─ Public Key: ${GREEN}${WG_PUB_KEY}${NC}\n"

    echo -e "${YELLOW}🚀 OUTLINE VPN${NC}"
    echo -e "   └─ Manager Config: ${GREEN}${OUTLINE_ACCESS_CONFIG}${NC}\n"

    echo -e "${BLUE}💡 Copy the Outline configuration above into Outline Manager${NC}"
    echo -e "${GREEN}${DOUBLE_SEPARATOR}${NC}"

    echo -e "\n${YELLOW}Press Enter to return to menu...${NC}"
    read -r
    show_menu
}

show_status() {
    log_header "📊 SERVICE STATUS"

    if groups | grep -q docker; then
        CMD="docker"
    else
        CMD="run_sudo docker"
    fi

    echo -e "${BLUE}Container Status:${NC}\n"
    $CMD compose ps

    echo -e "\n${BLUE}Resource Usage:${NC}\n"
    $CMD stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

    echo -e "\n${YELLOW}Press Enter to return to menu...${NC}"
    read -r
    show_menu
}

stop_services() {
    log_header "⏹️ STOPPING VPN SERVICES"

    if groups | grep -q docker; then
        CMD="docker compose"
    else
        CMD="run_sudo docker compose"
    fi

    log_info "Stopping all containers..."
    $CMD down > /dev/null 2>&1
    log_success "All services stopped"

    show_menu
}

uninstall_docker() {
    log_header "🔥 COMPLETE DOCKER UNINSTALLATION"

    read -p "⚠️  This will remove ALL Docker containers, images, and volumes. Continue? [y/N]: " confirm
    if [[ ! "$confirm" =~ [yY] ]]; then
        log_info "Operation cancelled"
        show_menu
        return
    fi

    log_warning "Removing all Docker data..."
    run_sudo docker stop $($DOCKER_CMD ps -aq) 2>/dev/null || true
    run_sudo docker rm -f $($DOCKER_CMD ps -aq) 2>/dev/null || true
    run_sudo docker volume rm $($DOCKER_CMD volume ls -q) 2>/dev/null || true
    run_sudo docker system prune -a -f --volumes > /dev/null 2>&1

    log_info "Removing Docker packages..."
    run_sudo apt-get purge -y docker-ce docker-ce-cli containerd.io docker-compose-plugin docker-compose 2>/dev/null || true
    run_sudo rm -rf /var/lib/docker /etc/docker 2>/dev/null || true

    rm -f "$ENV_FILE"
    log_success "Complete uninstallation finished"

    show_menu
}

# Main execution
log_info "uSipipo VPN Manager v2.0 started"
show_menu