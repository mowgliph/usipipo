#!/bin/bash

# =============================================================================
# Module: Docker Installation Engine
# Location: modules/install_docker.sh
# Description: Handles fresh installation of Docker Engine & Compose Plugin
#              on Debian/Ubuntu systems.
# =============================================================================

# Guard Clause: Prevent direct execution without the main context
if [ -z "$INSTALLER_ACTIVE" ]; then
    echo "❌ Error: This module cannot be run directly. Please run the main 'install.sh'."
    exit 1
fi

docker() {
    log_header "🐳 DOCKER ENGINE INSTALLATION"

    # 1. Check if Docker is already installed and functional
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        log_info "Docker is already installed:"
        log_raw "   • $(docker --version)"
        log_raw "   • $(docker compose version)"
        
        log_warning "Skipping installation steps to prevent conflicts."
        return 0
    fi

    # 2. OS Detection
    log_step "1" "5" "Detecting Operating System..."
    if [ -f /etc/os-release ]; then
        . /etc/os-release
    else
        log_error "Cannot detect OS distribution. /etc/os-release missing."
        return 1
    fi

    local SUPPORTED_DISTROS="ubuntu debian"
    if [[ ! " $SUPPORTED_DISTROS " =~ " $ID " ]]; then
        log_error "Unsupported OS: $ID. Only Ubuntu and Debian are supported."
        return 1
    fi
    log_success "Detected valid OS: $PRETTY_NAME"

    # 3. Clean old versions (Conflict prevention)
    log_step "2" "5" "Cleaning potential conflicting packages..."
    run_sudo apt-get remove -y docker.io docker-doc docker-compose podman-docker containerd runc 2>/dev/null || true
    
    # 4. Install Dependencies & GPG Keys
    log_step "3" "5" "Setting up repositories and keys..."
    run_sudo apt-get update -qq
    run_sudo apt-get install -y ca-certificates curl gnupg

    # Create keyring directory
    run_sudo install -m 0755 -d /etc/apt/keyrings
    
    # Download GPG Key (Idempotent check)
    local GPG_URL="https://download.docker.com/linux/$ID/gpg"
    local KEYRING_PATH="/etc/apt/keyrings/docker.gpg"

    if [ ! -f "$KEYRING_PATH" ]; then
        curl -fsSL "$GPG_URL" | run_sudo gpg --dearmor -o "$KEYRING_PATH"
        run_sudo chmod a+r "$KEYRING_PATH"
        log_success "GPG Key added successfully."
    else
        log_info "GPG Key already exists."
    fi

    # 5. Add Repository
    log_step "4" "5" "Adding stable repository..."
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=$KEYRING_PATH] https://download.docker.com/linux/$ID \
      $(lsb_release -cs 2>/dev/null || echo "$VERSION_CODENAME") stable" | \
      run_sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    run_sudo apt-get update -qq
    log_success "Repository configured."

    # 6. Install Docker Engine
    log_step "5" "5" "Installing Docker Engine & Compose Plugin..."
    run_sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # 7. Validation & Post-Install
    if command -v docker &> /dev/null; then
        log_success "Docker installed successfully."
        
        # Add current user to docker group
        if [ "$ID_USER" != "0" ]; then
            run_sudo usermod -aG docker "$USER"
            log_info "User '$USER' added to 'docker' group."
            log_warning "NOTE: You may need to log out and back in for group changes to take effect."
        fi

        # Enable service
        run_sudo systemctl enable docker > /dev/null 2>&1
        run_sudo systemctl start docker > /dev/null 2>&1
    else
        log_error "Installation failed. 'docker' command not found."
        return 1
    fi
}
