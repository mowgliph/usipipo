#!/bin/bash

# =============================================================================
# Module: Outline VPN Configuration
# Location: modules/configure_outline.sh
# Description: Generates SSL certs, API secrets, and server config for Shadowbox.
# =============================================================================

# Guard Clause
if [ -z "$INSTALLER_ACTIVE" ]; then
    echo "❌ Error: This module cannot be run directly."
    exit 1
fi

outline() {
    log_header "🛡️ CONFIGURING OUTLINE VPN"

    # 1. Require Server IP
    if [ -z "$SERVER_IP" ]; then
        log_error "SERVER_IP is not defined. Cannot configure Outline."
        return 1
    fi

    # 2. Generate Random Ports & Secret
    # We use a loop to ensure ports are distinct
    local API_PORT=$((10000 + RANDOM % 50000))
    local KEYS_PORT=$((10000 + RANDOM % 50000))

    while [ "$API_PORT" -eq "$KEYS_PORT" ]; do
        KEYS_PORT=$((10000 + RANDOM % 50000))
    done

    local API_SECRET=$(tr -dc 'a-zA-Z0-9' </dev/urandom | head -c 32)
    
    log_info "Generated Configuration:"
    log_raw "   • API Port:  $API_PORT"
    log_raw "   • Keys Port: $KEYS_PORT"
    
    # Export variables for the main installer to use later
    export OUTLINE_API_PORT="$API_PORT"
    export OUTLINE_KEYS_PORT="$KEYS_PORT"
    export OUTLINE_API_SECRET="$API_SECRET"

    # 3. Pre-configure Volume Data
    # We use a temporary Alpine container to write to the volume.
    # This ensures permissions are correct relative to the Docker daemon.
    
    local DOCKER_CMD=$(get_docker_cmd)
    
    log_step "1" "2" "Initializing persistent volume..."
    
    # Ensure volume exists
    $DOCKER_CMD volume create outline_data >/dev/null 2>&1

    # Run configuration generator
    log_info "Generating SSL certificates and config inside volume..."
    
    $DOCKER_CMD run --rm -v outline_data:/opt/outline/persisted-state alpine sh -c "
        set -e
        apk add --no-cache openssl >/dev/null 2>&1
        
        mkdir -p /opt/outline/persisted-state
        cd /opt/outline/persisted-state
        
        # A. Generate Self-Signed Certificate if missing
        if [ ! -f shadowbox-selfsigned.crt ]; then
            openssl req -x509 -nodes -days 36500 -newkey rsa:2048 \
                -subj '/CN=${SERVER_IP}' \
                -keyout shadowbox-selfsigned.key \
                -out shadowbox-selfsigned.crt 2>&1
        else
            echo 'Certificates already exist. Skipping.'
        fi
        
        # B. Create Server Config (Critical for preventing boot loops)
        # We inject the KEYS_PORT here so Shadowbox knows where to listen for UDP/TCP traffic
        cat <<EOF > shadowbox_server_config.json
{
  \"rolloutId\": \"vpn-manager-$(date +%s)\",
  \"portForNewAccessKeys\": ${KEYS_PORT},
  \"hostname\": \"${SERVER_IP}\",
  \"created\": $(date +%s)000
}
EOF

        # C. Fix Permissions
        # Shadowbox typically runs as root inside container, but strictly setting 
        # permissions prevents 'Access Denied' issues on some hosts.
        chmod 644 shadowbox-selfsigned.crt shadowbox_server_config.json
        chmod 600 shadowbox-selfsigned.key
    "

    if [ $? -eq 0 ]; then
        log_success "Outline configuration files created successfully."
    else
        log_error "Failed to generate Outline configuration."
        return 1
    fi

    # 4. Extract Certificate Fingerprint (SHA256)
    # Necessary for the client setup string
    log_step "2" "2" "Extracting SSL Fingerprint..."
    
    local CERT_SHA256=$($DOCKER_CMD run --rm -v outline_data:/opt/outline/persisted-state alpine sh -c \
        "apk add --no-cache openssl >/dev/null 2>&1 && \
        openssl x509 -in /opt/outline/persisted-state/shadowbox-selfsigned.crt -noout -fingerprint -sha256" 2>/dev/null | \
        cut -d= -f2 | tr -d :)
    
    if [ -n "$CERT_SHA256" ]; then
        export OUTLINE_CERT_SHA256="$CERT_SHA256"
        log_success "Fingerprint extracted."
    else
        log_error "Could not extract certificate fingerprint."
        export OUTLINE_CERT_SHA256="ERROR_RETRIEVING_FINGERPRINT"
    fi
}
