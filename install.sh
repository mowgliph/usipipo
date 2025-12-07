#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# =============================================================================
# uSipipo VPN Manager v2.0 - Hardened
# =============================================================================
# Author: uSipipo Team (refactor por auditor)
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

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$SCRIPT_DIR"
ENV_FILE="$PROJECT_DIR/.env"
ENV_EXAMPLE="$PROJECT_DIR/example.env"
DOCKER_COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/installation_$(date +%Y%m%d_%H%M%S).log"
TMP_DIR="$(mktemp -d -t usipipo.XXXXXX)"
CI_MODE="${CI:-0}"
AUTO_YES=0

# Ensure logs dir
mkdir -p "${LOG_DIR}"

# =============================================================================
# Logging
# =============================================================================
log_raw() {
    local message="$1"
    echo -e "$message" | tee -a "$LOG_FILE" 2>/dev/null || echo -e "$message"
}
log_info(){ log_raw "${BLUE}${INFO_ICON} [INFO]${NC} ${GRAY}$(date '+%Y-%m-%d %H:%M:%S')${NC} │ $1"; }
log_success(){ log_raw "${GREEN}${SUCCESS_ICON} [SUCCESS]${NC} ${GRAY}$(date '+%Y-%m-%d %H:%M:%S')${NC} │ $1"; }
log_warning(){ log_raw "${YELLOW}${WARNING_ICON} [WARNING]${NC} ${GRAY}$(date '+%Y-%m-%d %H:%M:%S')${NC} │ $1"; }
log_error(){ log_raw "${RED}${ERROR_ICON} [ERROR]${NC} ${GRAY}$(date '+%Y-%m-%d %H:%M:%S')${NC} │ $1"; }
log_header(){ log_raw "\n${CYAN}${SEPARATOR}${NC}\n${WHITE}$1${NC}\n${CYAN}${SEPARATOR}${NC}\n"; }
log_subheader(){ log_raw "\n${GRAY}${THIN_SEPARATOR}${NC}\n${CYAN}$1${NC}\n${GRAY}${THIN_SEPARATOR}${NC}"; }

# Print secret safely (mask)
mask_secret() {
    local s="${1:-}"
    if [ -z "$s" ]; then
        echo "NONE"
    else
        echo "${s:0:6}******"
    fi
}

# =============================================================================
# Utilities
# =============================================================================
run_sudo() {
    if [ "$(id -u)" = "0" ]; then
        "$@"
    else
        sudo -E "$@"
    fi
}

cleanup() {
    rm -rf "$TMP_DIR" 2>/dev/null || true
}
trap cleanup EXIT
trap 'log_error "Interrupted"; exit 1' INT TERM

is_interactive() {
    [ "$AUTO_YES" -eq 0 ] && [ -t 0 ]
}

confirm_action() {
    local prompt="$1"
    local default="${2:-N}"
    if [ "$CI_MODE" = "1" ] || [ "$AUTO_YES" -eq 1 ]; then
        log_info "Auto-confirm enabled (CI/AUTO): ${prompt} -> Yes"
        return 0
    fi
    if [ "$default" = "Y" ]; then
        read -r -p "$(echo -e ${YELLOW}${WARNING_ICON} ${prompt} [Y/n]: ${NC})" response
        response=${response:-Y}
    else
        read -r -p "$(echo -e ${YELLOW}${WARNING_ICON} ${prompt} [y/N]: ${NC})" response
        response=${response:-N}
    fi
    [[ "$response" =~ ^[Yy]$ ]]
}

press_any_key() {
    if is_interactive; then
        echo -e "\n${GRAY}Press Enter to continue...${NC}"
        read -r
    fi
}

# Check if port is free (TCP/UDP)
port_is_free() {
    local port=$1
    if ss -lntu | awk '{print $5}' | grep -E -q "(:|\\b)${port}\$"; then
        return 1
    fi
    return 0
}

pick_random_port() {
    local port
    for _ in {1..10}; do
        port=$((10000 + RANDOM % 50000))
        port=$((port<1024 ? port+1024 : port))
        if port_is_free "$port"; then
            echo "$port"
            return 0
        fi
    done
    return 1
}

# Docker detection (robust)
detect_docker() {
    if ! command -v docker &>/dev/null; then
        log_error "docker CLI not found. Please install Docker first."
        return 1
    fi

    # prefer 'docker compose' plugin, but fallback to 'docker-compose'
    if docker compose version &>/dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
    elif command -v docker-compose &>/dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    else
        log_error "Neither 'docker compose' (plugin) nor 'docker-compose' found."
        return 1
    fi

    DOCKER_BIN="docker"
    log_info "Using Docker: $(docker --version | head -n1)"
    log_info "Using Compose command: ${DOCKER_COMPOSE_CMD}"
    return 0
}

# =============================================================================
# Menu
# =============================================================================
show_menu() {
    clear
    create_logs_dir
    local server_ip=$(get_public_ip)
    local docker_version=$(docker --version 2>/dev/null | cut -d' ' -f3 | tr -d ',' || echo "Not installed")
    local compose_version=$($DOCKER_COMPOSE_CMD version 2>/dev/null | head -n1 || echo "Not installed")

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

    if is_interactive; then
        read -r -p "$(echo -e ${WHITE}Select option [1-8]:${NC} )" choice
    else
        log_info "Non-interactive mode, defaulting to option 8 (Exit). Set AUTO_YES=1 to skip prompts."
        choice=8
    fi

    case $choice in
        1) install_docker ;;
        2) start_services ;;
        3) show_status ;;
        4) restart_services ;;
        5) edit_env_config ;;
        6) stop_services ;;
        7) uninstall_docker ;;
        8) log_info "Goodbye"; exit 0 ;;
        *) log_error "Invalid option"; sleep 1; show_menu ;;
    esac
}

# =============================================================================
# Helpers previously in the original script
# =============================================================================
create_logs_dir() { mkdir -p "$LOG_DIR" 2>/dev/null || true; }

get_public_ipv4() {
    log_info "Detecting public IPv4..."
    curl -4 -s --connect-timeout 5 ifconfig.co 2>/dev/null || \
    curl -4 -s --connect-timeout 5 icanhazip.com 2>/dev/null || \
    curl -4 -s --connect-timeout 5 ipinfo.io/ip 2>/dev/null || echo ""
}

get_public_ipv6() {
    log_info "Detecting public IPv6..."
    curl -6 -s --connect-timeout 5 ifconfig.co 2>/dev/null || \
    curl -6 -s --connect-timeout 5 icanhazip.com 2>/dev/null || echo ""
}

get_public_ip() {
    local ipv4
    ipv4=$(get_public_ipv4 || echo "")
    if [ -n "$ipv4" ]; then
        echo "$ipv4"
        return
    fi
    get_public_ipv6 || echo ""
}

# =============================================================================
# Installer (no cambios funcionales críticos)
# =============================================================================
install_docker() {
    log_header "🐳 DOCKER & DOCKER COMPOSE INSTALLATION"
    if command -v docker &>/dev/null && (docker version &>/dev/null); then
        log_warning "Docker seems present."
        if ! confirm_action "Do you want to reinstall Docker?"; then
            show_menu
            return
        fi
    fi

    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_ID=$ID
    else
        log_error "OS detection failed (/etc/os-release missing)"
        return 1
    fi

    case "$OS_ID" in
        ubuntu|debian)
            log_info "Installing prerequisites and Docker for $OS_ID"
            run_sudo apt-get update -y
            run_sudo apt-get install -y ca-certificates curl gnupg lsb-release apt-transport-https software-properties-common
            run_sudo mkdir -p /etc/apt/keyrings
            # Use upstream install steps (kept succinct)
            curl -fsSL "https://download.docker.com/linux/${OS_ID}/gpg" | run_sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/${OS_ID} $(lsb_release -cs) stable" | run_sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            run_sudo apt-get update -y
            run_sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            run_sudo systemctl enable --now docker
            run_sudo usermod -aG docker "$SUDO_USER" || true
            log_success "Docker installed. You may need to relogin for group changes."
            ;;
        *)
            log_error "Unsupported OS: $OS_ID. Only Debian/Ubuntu supported by this script."
            ;;
    esac
    press_any_key
    show_menu
}

# =============================================================================
# START SERVICES (reforzado)
# =============================================================================
start_services() {
    log_header "🚀 STARTING VPN SERVICES"

    # defaults
    local SERVER_IPV4="" SERVER_IPV6="" SERVER_IP=""
    local PIHOLE_WEBPASS PIHOLE_WEB_PORT PIHOLE_DNS="8.8.8.8;1.1.1.1"
    local WIREGUARD_PORT WIREGUARD_PUBLIC_KEY WIREGUARD_ENDPOINT
    local WIREGUARD_PATH="/config"
    local OUTLINE_API_PORT OUTLINE_KEYS_PORT OUTLINE_API_SECRET OUTLINE_API_URL OUTLINE_CERT_SHA256
    local PRESERVE_CERTS="false"
    local TELEGRAM_TOKEN="" AUTHORIZED_USERS=""

    # detect IP
    log_step_msg() { log_step "$1" "$2" "$3"; }
    log_step_msg "1" "8" "Detecting public IP..."
    SERVER_IPV4=$(get_public_ipv4 || echo "")
    SERVER_IPV6=$(get_public_ipv6 || echo "")
    if [ -n "$SERVER_IPV4" ]; then
        SERVER_IP="$SERVER_IPV4"
        log_success "IPv4 detected: ${SERVER_IPV4}"
    elif [ -n "$SERVER_IPV6" ]; then
        SERVER_IP="$SERVER_IPV6"
        log_success "IPv6 detected: ${SERVER_IPV6}"
    else
        log_error "No public IP detected. Aborting."
        press_any_key
        show_menu
        return 1
    fi

    # Step 2: random ports but check availability
    log_step_msg "2" "8" "Generating ports and secrets"
    PIHOLE_WEBPASS=$(tr -dc 'A-Za-z0-9!@#$%^&*' </dev/urandom | head -c 16 || echo "piholepass")
    PIHOLE_WEB_PORT="$(pick_random_port || echo 8080)"
    WIREGUARD_PORT="$(pick_random_port || echo 51820)"
    OUTLINE_API_PORT="$(pick_random_port || echo 8443)"
    OUTLINE_KEYS_PORT="$(pick_random_port || echo 8444)"

    # ensure uniqueness
    while [ "$OUTLINE_KEYS_PORT" = "$OUTLINE_API_PORT" ] || [ "$OUTLINE_KEYS_PORT" = "$WIREGUARD_PORT" ] || [ "$OUTLINE_KEYS_PORT" = "$PIHOLE_WEB_PORT" ]; do
        OUTLINE_KEYS_PORT="$(pick_random_port || echo $((OUTLINE_API_PORT+1)))"
    done

    OUTLINE_API_SECRET=$(tr -dc 'a-zA-Z0-9' </dev/urandom | head -c 32 || echo "secretfallback")
    log_success "Generated ports (masked secrets): Pi-hole:${PIHOLE_WEB_PORT} WireGuard:${WIREGUARD_PORT} Outline:${OUTLINE_API_PORT}"
    log_info "Pi-hole admin pwd: $(mask_secret "$PIHOLE_WEBPASS")"
    log_info "Outline API secret (masked): $(mask_secret "$OUTLINE_API_SECRET")"

    # preliminary .env (safe permissions)
    log_step_msg "3" "8" "Writing preliminary .env"
    umask 077
    cat > "$ENV_FILE" <<EOF
# uSipipo VPN Manager - Auto-Generated
# Generated: $(date -u +"%Y-%m-%d %H:%M:%SZ")
TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
AUTHORIZED_USERS=${AUTHORIZED_USERS}
SERVER_IPV4=${SERVER_IPV4}
SERVER_IPV6=${SERVER_IPV6}
SERVER_IP=${SERVER_IP}
PIHOLE_WEB_PORT=${PIHOLE_WEB_PORT}
PIHOLE_WEBPASS=${PIHOLE_WEBPASS}
PIHOLE_DNS=${PIHOLE_DNS}
WIREGUARD_PORT=${WIREGUARD_PORT}
WIREGUARD_PATH=${WIREGUARD_PATH}
OUTLINE_API_SECRET=${OUTLINE_API_SECRET}
OUTLINE_API_PORT=${OUTLINE_API_PORT}
OUTLINE_KEYS_PORT=${OUTLINE_KEYS_PORT}
PRESERVE_CERTS=${PRESERVE_CERTS}
NODE_ENV=production
EOF
    chmod 600 "$ENV_FILE"
    log_success "Preliminary .env written to ${ENV_FILE} (600)"

    # detect docker compose
    detect_docker || { log_error "Docker not available"; return 1; }

    # create volumes and prepopulate outline config/certs
    log_step_msg "4" "8" "Preparing volumes and Outline persisted-state"
    "$DOCKER_BIN" volume create outline_data >/dev/null 2>&1 || true

    # create files in volume and set permissions correctly
    "$DOCKER_BIN" run --rm -v outline_data:/opt/outline/persisted-state alpine sh -c "
        set -e
        apk add --no-cache openssl >/dev/null 2>&1 || true
        mkdir -p /opt/outline/persisted-state
        cd /opt/outline/persisted-state
        if [ ! -f shadowbox-selfsigned.crt ]; then
            openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -subj '/CN=${SERVER_IP}' -keyout shadowbox-selfsigned.key -out shadowbox-selfsigned.crt
        fi
        cat > shadowbox_server_config.json <<JSON
{
  \"rolloutId\": \"vpn-manager-$(date +%s)\",
  \"portForNewAccessKeys\": ${OUTLINE_KEYS_PORT},
  \"hostname\": \"${SERVER_IP}\",
  \"created\": $(date +%s)000
}
JSON
        chmod 644 shadowbox-selfsigned.crt shadowbox_server_config.json || true
        chmod 600 shadowbox-selfsigned.key || true
        chown 1000:1000 shadowbox-selfsigned.* shadowbox_server_config.json || true
        ls -lh /opt/outline/persisted-state/
    " >/dev/null 2>&1 || { log_warning "Warning: could not prepopulate outline volume; check docker permissions"; }

    # Kernel networking (single atomic write)
    log_step_msg "5" "8" "Configuring kernel networking (sysctl)"
    run_sudo tee /etc/sysctl.d/99-vpn-manager.conf > /dev/null <<'SYSCTL'
net.ipv4.ip_forward=1
net.ipv4.conf.all.src_valid_mark=1
net.ipv6.conf.all.disable_ipv6=0
SYSCTL
    run_sudo sysctl --system >/dev/null 2>&1 || true
    log_success "Kernel parameters applied"

    # Start containers
    log_step_msg "6" "8" "Starting containers via compose"
    # ensure env exists for compose
    export $(grep -v '^#' "$ENV_FILE" | xargs -d '\n' -n1 2>/dev/null || true)

    # Use the detected compose command
    # Expand to array for safe exec
    COMPOSE_CMD=()
    read -r -a COMPOSE_CMD <<< "$(echo $DOCKER_COMPOSE_CMD)"
    "${COMPOSE_CMD[@]}" up -d --remove-orphans || { log_error "docker compose up failed"; show_menu; return 1; }
    log_success "Compose up requested"

    # Wait for Outline persisted state file (healthcheck)
    log_step_msg "7" "8" "Waiting for Outline to initialize (max 90s)"
    local MAX_RETRIES=90
    local COUNT=0
    local SUCCESS=false
    while [ $COUNT -lt $MAX_RETRIES ]; do
        if "$DOCKER_BIN" run --rm -v outline_data:/opt/outline/persisted-state alpine test -f /opt/outline/persisted-state/shadowbox_server_config.json >/dev/null 2>&1; then
            SUCCESS=true; break
        fi
        sleep 1
        COUNT=$((COUNT+1))
    done

    if [ "$SUCCESS" != "true" ]; then
        log_error "Timeout waiting for Outline persisted config"
        log_info "Check container logs with: $DOCKER_COMPOSE_CMD logs outline"
        press_any_key
    else
        log_success "Outline persisted-state detected in ${COUNT}s"
    fi

    # Extract certificate fingerprint
    log_step_msg "8" "8" "Extracting certificate fingerprint (sha256)"
    OUTLINE_CERT_SHA256=$("$DOCKER_BIN" run --rm -v outline_data:/opt/outline/persisted-state alpine sh -c "apk add --no-cache openssl >/dev/null 2>&1 || true; openssl x509 -in /opt/outline/persisted-state/shadowbox-selfsigned.crt -noout -fingerprint -sha256" 2>/dev/null | cut -d'=' -f2 | tr -d ':' || echo "")
    if [ -n "$OUTLINE_CERT_SHA256" ]; then
        log_info "Outline cert SHA256: ${OUTLINE_CERT_SHA256:0:40}..."
    else
        log_warning "Could not compute Outline cert fingerprint automatically"
    fi

    # WireGuard public key (best effort)
    log_info "Attempting to read WireGuard public key from container (if available)..."
    WIREGUARD_PUBLIC_KEY=$("$DOCKER_BIN" exec -i wireguard cat /config/server/publickey 2>/dev/null | tr -d '[:space:]' || echo "")
    if [ -n "$WIREGUARD_PUBLIC_KEY" ]; then
        log_info "WireGuard public key: $(mask_secret "$WIREGUARD_PUBLIC_KEY")"
    else
        log_info "WireGuard public key pending (container may still be initializing)"
    fi

    # Final .env (production)
    log_subheader "Finalizing .env"
    umask 077
    cat > "$ENV_FILE" <<EOF
# uSipipo VPN Manager - Production Configuration
# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
TELEGRAM_TOKEN=${TELEGRAM_TOKEN:-your_telegram_bot_token_here}
AUTHORIZED_USERS=${AUTHORIZED_USERS:-123456789}
SERVER_IPV4=${SERVER_IPV4}
SERVER_IPV6=${SERVER_IPV6}
SERVER_IP=${SERVER_IP}
PIHOLE_WEB_PORT=${PIHOLE_WEB_PORT}
PIHOLE_WEBPASS=${PIHOLE_WEBPASS}
PIHOLE_DNS=${PIHOLE_DNS}
WIREGUARD_PORT=${WIREGUARD_PORT}
WIREGUARD_PUBLIC_KEY=${WIREGUARD_PUBLIC_KEY}
WIREGUARD_ENDPOINT=${SERVER_IP}:${WIREGUARD_PORT}
WIREGUARD_PATH=${WIREGUARD_PATH}
OUTLINE_API_SECRET=${OUTLINE_API_SECRET}
OUTLINE_API_PORT=${OUTLINE_API_PORT}
OUTLINE_KEYS_PORT=${OUTLINE_KEYS_PORT}
OUTLINE_API_URL=https://${SERVER_IP}:${OUTLINE_API_PORT}/${OUTLINE_API_SECRET}
OUTLINE_CERT_SHA256=${OUTLINE_CERT_SHA256}
PRESERVE_CERTS=${PRESERVE_CERTS}
NODE_ENV=production
EOF
    chmod 600 "$ENV_FILE"
    log_success "Production .env written (600): ${ENV_FILE}"

    # Display summary (mask secrets)
    clear
    log_header "🎉 INSTALLATION COMPLETED SUCCESSFULLY"
    log_subheader "📋 Service Access (masked)"
    echo -e "\n${CYAN}Pi-hole:${NC} http://${SERVER_IP}:${PIHOLE_WEB_PORT}/admin"
    echo -e "Admin password: $(mask_secret "$PIHOLE_WEBPASS")"
    echo -e "\n${CYAN}WireGuard:${NC} Endpoint: ${SERVER_IP}:${WIREGUARD_PORT}"
    echo -e "Public Key: $(mask_secret "$WIREGUARD_PUBLIC_KEY")"
    echo -e "\n${CYAN}Outline:${NC} API URL: https://${SERVER_IP}:${OUTLINE_API_PORT}/<secret>"
    echo -e "Manager JSON: {\"apiUrl\":\"https://${SERVER_IP}:${OUTLINE_API_PORT}/...\",\"certSha256\":\"${OUTLINE_CERT_SHA256}\"}"
    log_warning "Secrets are masked in this output. See ${ENV_FILE} (600) for full values."
    press_any_key
    show_menu
}

# =============================================================================
# STATUS / LOGS / RESTART / STOP / UNINSTALL (fixes)
# =============================================================================
show_status() {
    log_header "📊 SYSTEM STATUS & DIAGNOSTICS"
    detect_docker || return 1

    $DOCKER_COMPOSE_CMD ps || true
    "$DOCKER_BIN" stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" || true

    # health via ps + service name check
    for svc in outline wireguard pihole; do
        if "$DOCKER_BIN" ps --filter "name=${svc}" --filter "status=running" | grep -q "${svc}"; then
            log_success "${svc}: Running"
        else
            log_error "${svc}: Not running"
        fi
    done

    if is_interactive; then
        read -r -p "$(echo -e ${YELLOW}Show container logs? [y/N]:${NC} )" show_logs
        if [[ "$show_logs" =~ ^[Yy]$ ]]; then
            echo " 1) Outline  2) WireGuard  3) Pi-hole  4) All"
            read -r -p "Choice [1-4]: " log_choice
            case $log_choice in
                1) "$DOCKER_BIN" logs --tail 50 outline ;;
                2) "$DOCKER_BIN" logs --tail 50 wireguard ;;
                3) "$DOCKER_BIN" logs --tail 50 pihole ;;
                4) "$DOCKER_BIN" logs --tail 20 outline; "$DOCKER_BIN" logs --tail 20 wireguard; "$DOCKER_BIN" logs --tail 20 pihole ;;
            esac
        fi
    fi
    press_any_key
    show_menu
}

restart_services() {
    log_header "🔄 RESTARTING VPN SERVICES"
    detect_docker || return 1
    "$DOCKER_COMPOSE_CMD" down || true
    "$DOCKER_COMPOSE_CMD" up -d || { log_error "Failed to start after restart"; return 1; }
    log_success "Services restarted"
    press_any_key
    show_menu
}

stop_services() {
    log_header "⏹️ STOPPING VPN SERVICES"
    if ! confirm_action "Are you sure you want to stop all services?"; then
        log_info "Cancelled"
        show_menu
        return
    fi
    detect_docker || return 1
    # stop and remove by name
    "$DOCKER_COMPOSE_CMD" stop outline wireguard pihole || true
    "$DOCKER_COMPOSE_CMD" rm -f outline wireguard pihole || true
    log_success "Services stopped (containers removed). Volumes preserved."
    press_any_key
    show_menu
}

uninstall_docker() {
    log_header "🔥 COMPLETE DOCKER UNINSTALLATION"
    log_warning "This will remove ALL docker data on host. Proceed with extreme caution."
    if ! confirm_action "Type Y to proceed with complete removal" "N"; then
        show_menu; return
    fi
    read -r -p "$(echo -e ${RED}Type 'DELETE EVERYTHING' to confirm:${NC} )" final_confirm
    if [ "$final_confirm" != "DELETE EVERYTHING" ]; then log_info "Cancelled"; show_menu; return; fi
    detect_docker || return 1
    run_sudo "$DOCKER_BIN" stop $("$DOCKER_BIN" ps -aq) 2>/dev/null || true
    run_sudo "$DOCKER_BIN" rm -f $("$DOCKER_BIN" ps -aq) 2>/dev/null || true
    run_sudo "$DOCKER_BIN" volume rm $("$DOCKER_BIN" volume ls -q) 2>/dev/null || true
    run_sudo "$DOCKER_BIN" system prune -a -f --volumes >/dev/null 2>&1 || true
    run_sudo apt-get purge -y docker-ce docker-ce-cli containerd.io docker-compose-plugin docker-compose 2>/dev/null || true
    run_sudo apt-get autoremove -y >/dev/null 2>&1 || true
    run_sudo rm -rf /var/lib/docker /etc/docker /var/lib/containerd 2>/dev/null || true
    [ -f "$ENV_FILE" ] && rm -f "$ENV_FILE"
    log_success "Uninstallation completed"
    press_any_key
    show_menu
}

# =============================================================================
# Edit .env
# =============================================================================
edit_env_config() {
    log_header "📝 ENV EDIT"
    if [ ! -f "$ENV_FILE" ]; then
        log_error ".env not found. Run start first."
        press_any_key
        show_menu
        return
    fi
    log_info "Opening $ENV_FILE (600)"
    if is_interactive; then
        ${EDITOR:-nano} "$ENV_FILE"
        log_success "Saved"
    else
        log_warning "Non-interactive: cannot open editor"
    fi
    press_any_key
    show_menu
}

# =============================================================================
# Main
# =============================================================================
main() {
    # Accept --yes flag for automation
    while [ "${1:-}" != "" ]; do
        case "$1" in
            --yes|-y) AUTO_YES=1 ;;
        esac
        shift
    done

    if [ "$(id -u)" -eq 0 ]; then
        log_warning "Running as root is discouraged; script will use sudo where needed."
    fi

    create_logs_dir
    log_info "uSipipo VPN Manager started"
    detect_docker >/dev/null || true
    show_menu
}

main "$@"
