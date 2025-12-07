#!/bin/bash

# =============================================================================
# Module: WireGuard VPN Configuration
# Location: modules/configure_wireguard.sh
# Description: Sets up Kernel forwarding, generates keys, and creates wg0 config.
# =============================================================================

# Guard Clause
if [ -z "$INSTALLER_ACTIVE" ]; then
    echo "❌ Error: This module cannot be run directly."
    exit 1
fi

wireguard() {
    log_header "🔒 CONFIGURING WIREGUARD VPN"

    # 1. Kernel Network Configuration (Critical for VPN Routing)
    log_step "1" "4" "Configuring Kernel IP Forwarding..."
    
    # Enable instantly
    run_sudo sysctl -w net.ipv4.ip_forward=1 > /dev/null
    run_sudo sysctl -w net.ipv4.conf.all.src_valid_mark=1 > /dev/null
    
    # Make persistent via file
    echo "net.ipv4.ip_forward=1" | run_sudo tee /etc/sysctl.d/99-vpn-manager.conf > /dev/null
    echo "net.ipv4.conf.all.src_valid_mark=1" | run_sudo tee -a /etc/sysctl.d/99-vpn-manager.conf > /dev/null
    
    # Reload sysctl to be sure
    run_sudo sysctl -p /etc/sysctl.d/99-vpn-manager.conf > /dev/null
    
    log_success "Kernel forwarding enabled."

    # 2. Port Selection
    # Avoid conflicts with Outline ports if they are already set
    local WG_PORT=$((51820 + RANDOM % 100))
    # Simple check to ensure it doesn't clash with standard ports
    while [ "$WG_PORT" -eq 53 ] || [ "$WG_PORT" -eq 80 ] || [ "$WG_PORT" -eq 443 ]; do
        WG_PORT=$((51820 + RANDOM % 100))
    done
    
    export WIREGUARD_PORT="$WG_PORT"
    log_info "Selected WireGuard Port: $WG_PORT"

    # 3. Key Generation via Docker
    log_step "2" "4" "Generating Cryptographic Keys..."
    
    local DOCKER_CMD=$(get_docker_cmd)
    
    # Create volume if not exists
    $DOCKER_CMD volume create wireguard_config > /dev/null 2>&1

    # Generate Private Key
    local PRIV_KEY=$($DOCKER_CMD run --rm --entrypoint /usr/bin/wg lscr.io/linuxserver/wireguard:latest genkey)
    
    if [ -z "$PRIV_KEY" ]; then
        log_error "Failed to generate WireGuard Private Key."
        return 1
    fi

    # Generate Public Key from Private Key
    local PUB_KEY=$(echo "$PRIV_KEY" | $DOCKER_CMD run --rm -i --entrypoint /usr/bin/wg lscr.io/linuxserver/wireguard:latest pubkey)

    export WIREGUARD_PRIVATE_KEY="$PRIV_KEY"
    export WIREGUARD_PUBLIC_KEY="$PUB_KEY"
    
    log_success "Keys generated successfully."

    # 4. Detect Host Network Interface
    # Necessary for IPTables MASQUERADE rules
    log_step "3" "4" "Detecting Default Network Interface..."
    
    local DEFAULT_IFACE=$(ip -4 route ls | grep default | grep -Po '(?<=dev )(\S+)' | head -1)
    
    if [ -z "$DEFAULT_IFACE" ]; then
        DEFAULT_IFACE="eth0" # Fallback
        log_warning "Could not detect interface. Defaulting to eth0."
    else
        log_info "Detected active interface: $DEFAULT_IFACE"
    fi

    # 5. Inject Server Configuration (wg0.conf)
    log_step "4" "4" "Creating Server Configuration (wg0.conf)..."
    
    # We write directly to the volume to ensure the container finds the config on boot.
    # We include PostUp/PostDown rules to ensure internet access works via NAT.
    
    $DOCKER_CMD run --rm -v wireguard_config:/config alpine sh -c "
        mkdir -p /config/wg_confs
        
        cat <<EOF > /config/wg_confs/wg0.conf
[Interface]
Address = 10.13.13.1
ListenPort = ${WG_PORT}
PrivateKey = ${PRIV_KEY}
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o ${DEFAULT_IFACE} -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o ${DEFAULT_IFACE} -j MASQUERADE

# Client peers will be added automatically by the container logic or management tools
EOF
        chmod 600 /config/wg_confs/wg0.conf
    "

    if [ $? -eq 0 ]; then
        log_success "WireGuard configuration injected."
    else
        log_error "Failed to write WireGuard config."
        return 1
    fi
}
