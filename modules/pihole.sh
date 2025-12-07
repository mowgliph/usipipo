#!/bin/bash

# =============================================================================
# Module: Pi-hole Configuration
# Location: modules/pihole.sh
# Description: Prepares host DNS settings (Port 53) and generates Pi-hole creds.
# =============================================================================

# Guard Clause
if [ -z "$INSTALLER_ACTIVE" ]; then
    echo "❌ Error: This module cannot be run directly."
    exit 1
fi

pihole() {
    log_header "🛡️ CONFIGURING PI-HOLE DNS"

    # 1. Port 53 Conflict Resolution (Critical)
    # -------------------------------------------------------------------------
    log_step "1" "3" "Checking Port 53 availability..."

    if lsof -i :53 -t >/dev/null 2>&1 || ss -lptn 'sport = :53' | grep -q 53; then
        log_warning "Port 53 is currently in use (likely by systemd-resolved)."
        log_info "Disabling systemd-resolved stub listener to free up Port 53..."

        # Stop and disable systemd-resolved
        run_sudo systemctl stop systemd-resolved
        run_sudo systemctl disable systemd-resolved >/dev/null 2>&1

        # Fix /etc/resolv.conf so the host maintains internet access
        # We replace the symlink with a static file pointing to reliable upstream DNS
        log_info "Updating host DNS to maintain internet connectivity..."
        run_sudo rm -f /etc/resolv.conf
        
        echo "nameserver 1.1.1.1" | run_sudo tee /etc/resolv.conf > /dev/null
        echo "nameserver 8.8.8.8" | run_sudo tee -a /etc/resolv.conf > /dev/null

        log_success "Port 53 freed and host DNS updated."
    else
        log_success "Port 53 is free. No system conflicts detected."
    fi

    # 2. Credential & Port Generation
    # -------------------------------------------------------------------------
    log_step "2" "3" "Generating secure credentials..."

    # Generate a random web port (avoiding standard 80/443/53)
    # We explicitly exclude 80 and 443 to avoid conflicts if you add Nginx later
    local WEB_PORT=$(get_random_port 80 443 53)
    
    # Generate a strong password
    local WEB_PASS=$(generate_secret 16)

    # Export variables for the main installer to capture
    export PIHOLE_WEB_PORT="$WEB_PORT"
    export PIHOLE_WEBPASS="$WEB_PASS"
    export PIHOLE_DNS="8.8.8.8;1.1.1.1" # Default upstream for Pi-hole container

    log_info "Generated Configuration:"
    log_raw "   • Web Interface Port: $PIHOLE_WEB_PORT"
    log_raw "   • Web Password:       [HIDDEN] (Saved to .env)"

    # 3. Create Persistent Directories (Optional but recommended)
    # -------------------------------------------------------------------------
    log_step "3" "3" "Preparing Docker volumes..."
    
    # Although Docker Compose creates volumes automatically, 
    # ensuring the directory structure is clean helps avoid permission issues.
    local DOCKER_CMD=$(get_docker_cmd)
    
    # We just ensure the volume commands will work later. 
    # No specific action needed here as we use named volumes in compose.
    log_success "Pi-hole configuration ready."
}
