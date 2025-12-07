#!/bin/bash
set -e

# =============================================================================
# uSipipo VPN Manager - Master Installer
# =============================================================================
# Description: Orchestrates the installation of Docker, Pi-hole, WireGuard,
#              and Outline, generating a unified configuration.
# =============================================================================

# 1. Global Safety & Imports
# -----------------------------------------------------------------------------
export INSTALLER_ACTIVE="true"
export PROJECT_ROOT="$(pwd)"

# Function to safely source modules
source_module() {
    local module_path="./modules/$1"
    if [ -f "$module_path" ]; then
        source "$module_path"
    else
        echo -e "\033[0;31m❌ Critical Error: Module '$1' not found in ./modules/\033[0m"
        exit 1
    fi
}

# Import Modules (Order matters for dependencies)
source_module "utils.sh"            # Core Library (Logging, Colors, Helpers)
source_module "docker.sh"   # Docker Engine
source_module "pihole.sh" # Pi-hole DNS
source_module "wireguard.sh" # WireGuard VPN
source_module "outline.sh"   # Outline VPN

# -----------------------------------------------------------------------------
# 2. Main Installation Logic
# -----------------------------------------------------------------------------
main() {
    clear
    log_header "🚀 STARTING USIPIPO VPN MANAGER INSTALLATION"
    
    # A. Check & Install Docker
    install_docker_engine

    # B. Global Network Detection
    log_step "1" "6" "Detecting Server Public IP..."
    SERVER_IP=$(get_public_ip)
    export SERVER_IP # Export for Outline module to see
    log_success "Server IP detected: $SERVER_IP"

    # C. Module Execution (Configuration Phase)
    # Each function exports variables needed for the .env file
    pihole      # Exports: PIHOLE_WEB_PORT, PIHOLE_WEBPASS, PIHOLE_DNS
    wireguard   # Exports: WIREGUARD_PORT, WIREGUARD_PRIVATE_KEY, WIREGUARD_PUBLIC_KEY
    outline     # Exports: OUTLINE_API_PORT, OUTLINE_KEYS_PORT, OUTLINE_API_SECRET, OUTLINE_CERT_SHA256

    # D. User Inputs (Optional Data)
    log_step "5" "6" "Finalizing User Configuration..."
    echo -e "${GRAY}Leave blank to configure later in .env${NC}"
    
    read -p "$(echo -e "${YELLOW}? Telegram Bot Token:${NC} ")" TELEGRAM_TOKEN
    read -p "$(echo -e "${YELLOW}? Authorized Admin ID (Telegram ID):${NC} ")" AUTHORIZED_USERS

    # E. Generate .env File
    log_step "6" "6" "Generating environment file (.env)..."
    
    # Construct Outline API URL
    OUTLINE_API_URL="https://${SERVER_IP}:${OUTLINE_API_PORT}/${OUTLINE_API_SECRET}"

    cat <<EOF > .env
# =============================================================================
# uSipipo VPN Manager - Production Environment
# Generated: $(date '+%Y-%m-%d %H:%M:%S')
# =============================================================================

# --- Server Settings ---
SERVER_IP=${SERVER_IP}
SERVER_IPV4=${SERVER_IP}
NODE_ENV=production

# --- Telegram Bot ---
TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
AUTHORIZED_USERS=${AUTHORIZED_USERS}

# --- Pi-hole (AdBlock DNS) ---
PIHOLE_WEB_PORT=${PIHOLE_WEB_PORT}
PIHOLE_WEBPASS=${PIHOLE_WEBPASS}
PIHOLE_DNS=${PIHOLE_DNS}

# --- WireGuard VPN ---
WIREGUARD_PORT=${WIREGUARD_PORT}
WIREGUARD_PRIVATE_KEY=${WIREGUARD_PRIVATE_KEY}
WIREGUARD_PUBLIC_KEY=${WIREGUARD_PUBLIC_KEY}

# --- Outline VPN ---
OUTLINE_API_URL=${OUTLINE_API_URL}
OUTLINE_API_SECRET=${OUTLINE_API_SECRET}
OUTLINE_API_PORT=${OUTLINE_API_PORT}
OUTLINE_KEYS_PORT=${OUTLINE_KEYS_PORT}
OUTLINE_CERT_SHA256=${OUTLINE_CERT_SHA256}

EOF
    log_success "Configuration file (.env) created successfully."

    # F. Launch Services
    log_header "🐳 LAUNCHING SERVICES"
    
    local CMD=$(get_compose_cmd)
    
    # Pull first to show progress clearly
    $CMD pull
    
    # Up detached
    if $CMD up -d --remove-orphans; then
        log_success "All containers started successfully."
    else
        log_error "Failed to start containers. Check logs."
        exit 1
    fi

    # G. Final Summary
    display_summary
}

# -----------------------------------------------------------------------------
# 3. Summary Display
# -----------------------------------------------------------------------------
display_summary() {
    log_header "✅ INSTALLATION COMPLETE"
    
    echo -e "${CYAN}Server IP:${NC} ${WHITE}${SERVER_IP}${NC}"
    echo -e "${CYAN}Location:${NC}  ${PROJECT_ROOT}"
    echo -e ""
    echo -e "${YELLOW}🔹 Pi-hole DNS${NC}"
    echo -e "   • Dashboard:   http://${SERVER_IP}:${PIHOLE_WEB_PORT}/admin"
    echo -e "   • Password:    ${GREEN}${PIHOLE_WEBPASS}${NC}"
    echo -e ""
    echo -e "${YELLOW}🔹 WireGuard VPN${NC}"
    echo -e "   • UDP Port:    ${WIREGUARD_PORT}"
    echo -e "   • Public Key:  ${WIREGUARD_PUBLIC_KEY}"
    echo -e ""
    echo -e "${YELLOW}🔹 Outline VPN${NC}"
    echo -e "   • Management API URL (Paste this in Outline Manager):"
    echo -e "     ${WHITE}{\"apiUrl\":\"${OUTLINE_API_URL}\",\"certSha256\":\"${OUTLINE_CERT_SHA256}\"}${NC}"
    echo -e ""
    echo -e "${GRAY}Note: Please save these credentials safely.${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════════════════════════════${NC}"
}

# -----------------------------------------------------------------------------
# 4. Entry Point
# -----------------------------------------------------------------------------

# Ensure executable
chmod +x ./modules/*.sh

# Run Main
main
