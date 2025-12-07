#!/bin/bash
set -e

# =============================================================================
# uSipipo VPN Manager v2.1 - Professional Docker Management Script
# =============================================================================
# Author: uSipipo Team (Optimized by Senior JS Engineer)
# License: MIT
# Description: Automated VPN setup with Outline, WireGuard, and Pi-hole
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
readonly NC='\033[0m'

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
LOG_FILE="$PROJECT_DIR/logs/installation_$(date +%Y%m%d_%H%M%S).log"

# =============================================================================
# Utility Functions
# =============================================================================
log_raw() { echo -e "$1" | tee -a "$LOG_FILE" 2>/dev/null || echo -e "$1"; }
log_info() { log_raw "${BLUE}${INFO_ICON} [INFO]${NC} ${GRAY}$(date '+%H:%M:%S')${NC} │ $1"; }
log_success() { log_raw "${GREEN}${SUCCESS_ICON} [SUCCESS]${NC} ${GRAY}$(date '+%H:%M:%S')${NC} │ $1"; }
log_warning() { log_raw "${YELLOW}${WARNING_ICON} [WARNING]${NC} ${GRAY}$(date '+%H:%M:%S')${NC} │ $1"; }
log_error() { log_raw "${RED}${ERROR_ICON} [ERROR]${NC} ${GRAY}$(date '+%H:%M:%S')${NC} │ $1"; }

log_header() { log_raw "\n${CYAN}${SEPARATOR}${NC}"; log_raw "${WHITE}${1}${NC}"; log_raw "${CYAN}${SEPARATOR}${NC}\n"; }
log_subheader() { log_raw "\n${GRAY}${THIN_SEPARATOR}${NC}"; log_raw "${CYAN}${1}${NC}"; log_raw "${GRAY}${THIN_SEPARATOR}${NC}"; }
log_step() { log_raw "${PURPLE}▶ [STEP $1/$2]${NC} $3"; }

run_sudo() { if [ "$(id -u)" = "0" ]; then "$@"; else sudo -E "$@"; fi; }
create_logs_dir() { mkdir -p "$PROJECT_DIR/logs" 2>/dev/null || true; }
press_any_key() { echo -e "\n${GRAY}Press Enter to continue...${NC}"; read -r; }

get_public_ip() {
    local ip=$(curl -4 -s --connect-timeout 5 ifconfig.co || curl -4 -s --connect-timeout 5 ipinfo.io/ip)
    echo "${ip:-127.0.0.1}"
}

confirm_action() {
    local prompt="$1"
    local default="${2:-N}"
    if [ "$default" = "Y" ]; then read -p "${YELLOW}${WARNING_ICON} ${prompt} [Y/n]: ${NC}" r; r=${r:-Y}; else read -p "${YELLOW}${WARNING_ICON} ${prompt} [y/N]: ${NC}" r; r=${r:-N}; fi
    [[ "$r" =~ ^[Yy]$ ]]
}

# =============================================================================
# Menu & Installation
# =============================================================================
show_menu() {
    clear
    create_logs_dir
    local server_ip=$(get_public_ip)
    
    log_raw "${CYAN}${SEPARATOR}${NC}"
    log_raw "${WHITE}                ${HEADER_ICON} uSipipo VPN Manager v2.1 ${HEADER_ICON}${NC}"
    log_raw "${CYAN}${SEPARATOR}${NC}"
    log_raw "${BLUE}  📍 Server IP:${NC}        ${GREEN}${server_ip}${NC}"
    log_raw ""
    log_raw "  ${GREEN}1)${NC} 🐳 Install Docker & Docker Compose"
    log_raw "  ${YELLOW}2)${NC} ▶️  Start VPN Services ${GRAY}(Outline + WireGuard + Pi-hole)${NC}"
    log_raw "  ${BLUE}3)${NC} 📊 Show Service Status"
    log_raw "  ${PURPLE}4)${NC} 🔄 Restart Services"
    log_raw "  ${CYAN}5)${NC} 📝 Edit Config (.env)"
    log_raw "  ${RED}6)${NC} ⏹️  Stop Services"
    log_raw "  ${RED}7)${NC} 🔥 Uninstall"
    log_raw "  ${WHITE}8)${NC} 👋 Exit"
    log_raw ""
    
    read -p "Select option [1-8]: " choice
    case $choice in
        1) install_docker ;;
        2) start_services ;;
        3) show_status ;;
        4) restart_services ;;
        5) edit_env_config ;;
        6) stop_services ;;
        7) uninstall_docker ;;
        8) exit 0 ;;
        *) show_menu ;;
    esac
}

install_docker() {
    log_header "🐳 DOCKER INSTALLATION"
    if command -v docker &> /dev/null; then log_warning "Docker already installed."; press_any_key; show_menu; return; fi

    log_step "1" "3" "Updating system..."
    run_sudo apt-get update > /dev/null 2>&1
    
    log_step "2" "3" "Installing Docker script..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    run_sudo sh get-docker.sh > /dev/null 2>&1
    rm get-docker.sh
    
    log_step "3" "3" "Configuring permissions..."
    run_sudo usermod -aG docker $USER
    
    log_success "Docker installed. Please re-login or run 'newgrp docker'."
    press_any_key; show_menu
}

start_services() {
    log_header "🚀 STARTING VPN SERVICES"
    
    # 1. Detect IP
    local SERVER_IP=$(get_public_ip)
    
    # 2. Generate Ports & Secrets
    local PIHOLE_WEBPASS=$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 16)
    local PIHOLE_WEB_PORT=$((10000 + RANDOM % 5000))
    local WIREGUARD_PORT=51820 # Standard port often works best, or randomize
    local OUTLINE_API_PORT=$((20000 + RANDOM % 5000))
    local OUTLINE_KEYS_PORT=$((30000 + RANDOM % 5000))
    local OUTLINE_API_SECRET=$(tr -dc 'a-zA-Z0-9' </dev/urandom | head -c 32)
    local TELEGRAM_TOKEN=""
    local AUTHORIZED_USERS=""
    
    # 3. Create .env
    cat > "$ENV_FILE" <<EOF
TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
AUTHORIZED_USERS=${AUTHORIZED_USERS}
SERVER_IPV4=${SERVER_IP}
SERVER_IP=${SERVER_IP}
PIHOLE_WEB_PORT=${PIHOLE_WEB_PORT}
PIHOLE_WEBPASS=${PIHOLE_WEBPASS}
PIHOLE_DNS=8.8.8.8;1.1.1.1
WIREGUARD_PORT=${WIREGUARD_PORT}
WIREGUARD_PUBLIC_KEY=PENDING
OUTLINE_API_URL=https://${SERVER_IP}:${OUTLINE_API_PORT}/${OUTLINE_API_SECRET}
OUTLINE_API_SECRET=${OUTLINE_API_SECRET}
OUTLINE_API_PORT=${OUTLINE_API_PORT}
OUTLINE_KEYS_PORT=${OUTLINE_KEYS_PORT}
OUTLINE_CERT_SHA256=PENDING
PRESERVE_CERTS=false
NODE_ENV=production
EOF

    local DOCKER_CMD="docker"
    if ! groups | grep -q docker; then DOCKER_CMD="run_sudo docker"; fi
    local COMPOSE_CMD="$DOCKER_CMD compose"

    # 4. Kernel Tweaks (Host)
    log_step "4" "8" "Configuring Kernel Forwarding..."
    echo -e "net.ipv4.ip_forward=1\nnet.ipv4.conf.all.src_valid_mark=1" | run_sudo tee /etc/sysctl.d/99-vpn.conf > /dev/null
    run_sudo sysctl -p /etc/sysctl.d/99-vpn.conf > /dev/null

    # 5. Generate Outline Certs
    log_step "5" "8" "Generating Outline Certificates..."
    $DOCKER_CMD volume create outline_data > /dev/null
    $DOCKER_CMD run --rm -v outline_data:/opt/outline/persisted-state alpine sh -c "
        apk add --no-cache openssl >/dev/null 2>&1
        mkdir -p /opt/outline/persisted-state
        cd /opt/outline/persisted-state
        if [ ! -f shadowbox-selfsigned.crt ]; then
            openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -subj '/CN=${SERVER_IP}' \
                -keyout shadowbox-selfsigned.key -out shadowbox-selfsigned.crt 2>&1
        fi
        echo '{\"rolloutId\":\"vpn-init\",\"portForNewAccessKeys\":${OUTLINE_KEYS_PORT},\"hostname\":\"${SERVER_IP}\",\"created\":$(date +%s)000}' > shadowbox_server_config.json
        chmod 644 shadowbox-selfsigned.crt shadowbox_server_config.json
        chmod 600 shadowbox-selfsigned.key
    "

    # =========================================================================
    # STEP 6.8: CRITICAL FIX - PRE-CONFIGURE WIREGUARD SERVER WITH NAT
    # =========================================================================
    log_step "6" "8" "Pre-configuring WireGuard Server (NAT Rules)..."
    
    # Crear volumen de WireGuard manualmente
    $DOCKER_CMD volume create wireguard_config > /dev/null 2>&1 || true
    
    # Generamos claves de servidor
    log_info "Generating WireGuard Server Keys..."
    WG_PRIV_KEY=$($DOCKER_CMD run --rm --entrypoint /usr/bin/wg lscr.io/linuxserver/wireguard genkey)
    WG_PUB_KEY=$(echo "$WG_PRIV_KEY" | $DOCKER_CMD run --rm -i --entrypoint /usr/bin/wg lscr.io/linuxserver/wireguard pubkey)
    
    # Creamos el archivo wg0.conf con las reglas de IPTABLES (PostUp/PostDown)
    # Esto es vital para que haya internet.
    log_info "Injecting NAT/Masquerade rules into wg0.conf..."
    
    $DOCKER_CMD run --rm -v wireguard_config:/config lscr.io/linuxserver/wireguard sh -c "
        mkdir -p /config/wg_confs
        cat <<EOF > /config/wg_confs/wg0.conf
[Interface]
Address = 10.13.13.1
ListenPort = ${WIREGUARD_PORT}
PrivateKey = ${WG_PRIV_KEY}
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# Los clientes se añadirán debajo
EOF
        chmod 600 /config/wg_confs/wg0.conf
        echo '${WG_PUB_KEY}' > /config/server_public_key
    "
    log_success "WireGuard Server Configured with NAT rules."

    # 7. Start Services
    log_step "7" "8" "Starting Containers..."
    $COMPOSE_CMD up -d --remove-orphans

    # 8. Final Updates to .env
    log_step "8" "8" "Finalizing Configuration..."
    
    # Get Outline Cert Fingerprint
    CERT_SHA=$($DOCKER_CMD run --rm -v outline_data:/opt/outline/persisted-state alpine sh -c \
        "apk add --no-cache openssl >/dev/null && openssl x509 -in /opt/outline/persisted-state/shadowbox-selfsigned.crt -noout -fingerprint -sha256" | cut -d= -f2 | tr -d :)
    
    # Update .env with real WireGuard Key
    sed -i "s|WIREGUARD_PUBLIC_KEY=PENDING|WIREGUARD_PUBLIC_KEY=${WG_PUB_KEY}|" "$ENV_FILE"
    sed -i "s|OUTLINE_CERT_SHA256=PENDING|OUTLINE_CERT_SHA256=${CERT_SHA}|" "$ENV_FILE"

    log_header "🎉 SUCCESS"
    echo -e "${CYAN}WireGuard Config:${NC}"
    echo -e "  Endpoint: ${SERVER_IP}:${WIREGUARD_PORT}"
    echo -e "  Public Key: ${WG_PUB_KEY}"
    echo -e "${CYAN}Outline Manager Config:${NC}"
    echo -e "  {\"apiUrl\":\"https://${SERVER_IP}:${OUTLINE_API_PORT}/${OUTLINE_API_SECRET}\",\"certSha256\":\"${CERT_SHA}\"}"
    echo ""
    log_warning "Don't forget to edit .env to add your TELEGRAM_TOKEN and restart!"
    
    press_any_key; show_menu
}

show_status() {
    local DOCKER_CMD="docker"
    if ! groups | grep -q docker; then DOCKER_CMD="run_sudo docker"; fi
    $DOCKER_CMD compose ps
    press_any_key; show_menu
}

restart_services() {
    local DOCKER_CMD="docker"
    if ! groups | grep -q docker; then DOCKER_CMD="run_sudo docker"; fi
    $DOCKER_CMD compose down && $DOCKER_CMD compose up -d
    press_any_key; show_menu
}

edit_env_config() { ${EDITOR:-nano} "$ENV_FILE"; show_menu; }

stop_services() {
    local DOCKER_CMD="docker"
    if ! groups | grep -q docker; then DOCKER_CMD="run_sudo docker"; fi
    $DOCKER_CMD compose down
    show_menu
}

uninstall_docker() {
    if ! confirm_action "DELETE EVERYTHING (Docker, Data, Volumes)?"; then show_menu; return; fi
    run_sudo docker stop $(docker ps -aq) 2>/dev/null
    run_sudo docker rm -f $(docker ps -aq) 2>/dev/null
    run_sudo docker system prune -a -f --volumes
    run_sudo apt-get purge -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    rm -rf "$PROJECT_DIR/logs" "$ENV_FILE"
    log_success "Uninstalled."
    exit 0
}

# Main
if [ "$EUID" -eq 0 ]; then log_warning "Don't run as root directly."; fi
create_logs_dir
show_menu
