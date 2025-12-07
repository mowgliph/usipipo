#!/bin/bash

# =============================================================================
# Module: Uninstaller & Purge
# Location: modules/uninstall.sh
# Description: completely removes containers, volumes, networks, and files.
# =============================================================================

if [ -z "$INSTALLER_ACTIVE" ]; then
    echo "❌ Error: This module cannot be run directly."
    exit 1
fi

purge_system() {
    log_header "🔥 SYSTEM PURGE INITIATED"
    
    echo -e "${RED}${WARNING_ICON} WARNING: This will delete ALL data, VPN keys, and configs!${NC}"
    echo -e "${RED}Are you absolutely sure you want to proceed?${NC}"
    read -p "Type 'DELETE' to confirm: " confirmation

    if [ "$confirmation" != "DELETE" ]; then
        log_info "Purge cancelled by user."
        return 0
    fi

    local DOCKER_CMD=$(get_docker_cmd)
    local COMPOSE_CMD=$(get_compose_cmd)

    # 1. Stop and Remove Containers/Networks via Compose
    log_step "1" "5" "Stopping and removing containers..."
    if [ -f "docker-compose.yml" ]; then
        $COMPOSE_CMD down --volumes --remove-orphans >/dev/null 2>&1
        log_success "Containers and networks removed."
    else
        log_warning "docker-compose.yml not found, skipping compose down."
    fi

    # 2. Bruteforce Docker Cleanup (Fail-safe)
    # Stops any container related to our known names just in case compose failed
    log_step "2" "5" "Deep cleaning Docker artifacts..."
    local containers=("outline" "wireguard" "pihole" "watchtower")
    
    for container in "${containers[@]}"; do
        if $DOCKER_CMD ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
            $DOCKER_CMD stop "$container" >/dev/null 2>&1
            $DOCKER_CMD rm -f "$container" >/dev/null 2>&1
            log_info "Force removed container: $container"
        fi
    done

    # 3. Prune Docker Volumes (Specific to this project)
    log_step "3" "5" "Removing persistent data volumes..."
    # We attempt to remove volumes created by our modules
    $DOCKER_CMD volume rm wireguard_config outline_data pihole_config pihole_dns >/dev/null 2>&1 || true
    log_success "Project volumes removed."

    # 4. Clean System Configurations
    log_step "4" "5" "Reverting system network configurations..."
    
    # Remove Sysctl config
    if [ -f "/etc/sysctl.d/99-vpn-manager.conf" ]; then
        run_sudo rm -f /etc/sysctl.d/99-vpn-manager.conf
        run_sudo sysctl --system >/dev/null 2>&1
        log_success "Sysctl forwarding rules removed."
    fi

    # Restore /etc/resolv.conf if we modified it (Pi-hole step)
    # Check if we forced nameservers and systemd-resolved is disabled
    if systemctl is-enabled systemd-resolved >/dev/null 2>&1; then
        log_info "systemd-resolved is already active. No DNS changes needed."
    else
        log_info "Restoring systemd-resolved..."
        run_sudo systemctl enable systemd-resolved >/dev/null 2>&1
        run_sudo systemctl start systemd-resolved >/dev/null 2>&1
        # Re-link resolv.conf
        run_sudo rm -f /etc/resolv.conf
        run_sudo ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
        log_success "System DNS restored to default."
    fi

    # 5. Remove Local Files
    log_step "5" "5" "Removing local configuration files..."
    rm -f .env
    # Optional: remove logs? 
    # rm -rf ./logs
    
    log_header "✅ PURGE COMPLETE. SYSTEM IS CLEAN."
}
