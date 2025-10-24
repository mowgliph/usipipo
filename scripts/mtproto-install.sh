#!/bin/bash

# Secure MTProto Proxy installer for Telegram - uSipipo Refactored
# Based on https://github.com/TelegramMessenger/MTProxy
# Generates uSipipo .env variables upon installation.

RED='\033[0;31m'
ORANGE='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# --- Constantes ---
MTPROXY_DIR="/opt/mtproto-proxy"
MTPROXY_SERVICE_FILE="/etc/systemd/system/mtproto-proxy.service"
MTPROXY_CONFIG_FILE="${MTPROXY_DIR}/config.env"
MTPROXY_REPO_URL="https://github.com/TelegramMessenger/MTProxy.git"
MTPROXY_SECRET_FILE="${MTPROXY_DIR}/objs/bin/proxy-secret"
MTPROXY_CONFIG_FILE_URL="https://core.telegram.org/getProxyConfig"
MTPROXY_SECRET_FILE_URL="https://core.telegram.org/getProxySecret"

# --- Funciones de Validación ---
function isRoot() {
    if [ "${EUID}" -ne 0 ]; then
        echo "You need to run this script as root"
        exit 1
    fi
}
function detect_pihole() {
    if [[ -f ".env.pihole.generated" ]]; then
        source ".env.pihole.generated"
        # Validar que Pi-hole esté funcionando
        if curl -s "http://${PIHOLE_HOST}:${PIHOLE_PORT}/admin/api.php" > /dev/null 2>&1; then
            PIHOLE_IP="${PIHOLE_HOST}"
            return 0
        fi
    fi
    return 1
}

function checkOS() {
    source /etc/os-release
    OS="${ID}"
    if [[ ${OS} == "debian" || ${OS} == "raspbian" ]]; then
        if [[ ${VERSION_ID} -lt 10 ]]; then
            echo "Your version of Debian is not supported."
            echo "Please use Debian 10 Buster or later"
            exit 1
        fi
        OS=debian # overwrite if raspbian
    elif [[ ${OS} == "ubuntu" ]]; then
        RELEASE_YEAR=$(echo "${VERSION_ID}" | cut -d'.' -f1)
        if [[ ${RELEASE_YEAR} -lt 18 ]]; then
            echo "Your version of Ubuntu is not supported."
            echo "Please use Ubuntu 18.04 or later"
            exit 1
        fi
    else
        echo "This installer seems to be running on an unsupported distribution."
        echo "Supported distributions are Debian and Ubuntu."
        exit 1
    fi
}

function initialCheck() {
    isRoot
    checkOS
}

# --- Funciones de Instalación ---
function installDependencies() {
    echo "Installing required packages..."
    if ! apt-get update; then
        echo -e "${RED}Failed to update package list. Check your internet connection.${NC}"
        exit 1
    fi

    if ! apt-get install -y git curl build-essential libssl-dev zlib1g-dev xxd; then
        echo -e "${RED}Failed to install required packages.${NC}"
        exit 1
    fi

    echo -e "${GREEN}Dependencies installed successfully.${NC}"
}

function installMTProxy() {
    # Create directory for MTProxy
    mkdir -p "${MTPROXY_DIR}"
    cd "${MTPROXY_DIR}" || exit

    # Clone MTProxy repository if not already present or if it's empty
    if [ ! -d ".git" ] || [ -z "$(ls -A "${MTPROXY_DIR}")" ]; then
        echo "Cloning MTProxy repository..."
        if ! git clone "${MTPROXY_REPO_URL}" .; then
            echo -e "${RED}Failed to clone MTProxy repository. Check your internet connection.${NC}"
            exit 1
        fi
    else
        echo "MTProxy repository already exists, skipping clone."
    fi

    # Build MTProxy
    echo "Building MTProxy..."
    # Suppress GCC warnings during build
    export CFLAGS="-w"
    export CXXFLAGS="-w"
    if ! make clean; then
        echo -e "${RED}Failed to clean previous build.${NC}"
        exit 1
    fi

    if ! make LDFLAGS="-Wl,--allow-multiple-definition -lssl -lcrypto -lm"; then
        echo -e "${RED}Build failed. Check build dependencies and logs above.${NC}"
        exit 1
    fi

    echo -e "${GREEN}MTProxy built successfully.${NC}"

    # Navigate to binary directory
    cd objs/bin || { echo -e "${RED}Build directory not found.${NC}"; exit 1; }

    # Generate a secret
    SECRET=$(head -c 16 /dev/urandom | xxd -ps)
    if [ -z "$SECRET" ] || [ ${#SECRET} -ne 32 ]; then
        echo -e "${RED}Failed to generate secret.${NC}"
        exit 1
    fi

    # Get your external IP
    IP=$(curl -4 -s https://api.ipify.org)
    if [ -z "$IP" ]; then
        echo -e "${RED}Failed to get external IP.${NC}"
        exit 1
    fi

    # Generate a random port between 10000-60000
    PORT=$(( ((RANDOM<<15)|RANDOM) % 49152 + 10000 ))

    # Create systemd service
    echo "Creating systemd service..."

    # Configurar DNS si Pi-hole está disponible
    DNS_ARG=""
    if detect_pihole; then
        DNS_ARG="-d ${PIHOLE_IP}"
        echo -e "${GREEN}Pi-hole detected. Using ${PIHOLE_IP} as DNS for MTProto proxy.${NC}"
    else
        echo -e "${ORANGE}Pi-hole not detected. Using default DNS configuration.${NC}"
    fi

    cat > "${MTPROXY_SERVICE_FILE}" << EOL
[Unit]
Description=MTProto for Telegram - uSipipo
After=network.target

[Service]
Type=simple
WorkingDirectory=${MTPROXY_DIR}/objs/bin
ExecStart=${MTPROXY_DIR}/objs/bin/mtproto-proxy -u nobody -p 8888 -H ${PORT} -S ${SECRET} ${DNS_ARG} --aes-pwd proxy-secret proxy-multi.conf -M 1
Restart=on-failure
RestartSec=5
User=nobody
Group=nogroup

# Environment variables for better logging
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=HOME=/tmp

[Install]
WantedBy=multi-user.target
EOL

    # Generate proxy secret
    echo "Downloading proxy secret..."
    if ! curl -s --max-time 30 "${MTPROXY_SECRET_FILE_URL}" -o proxy-secret; then
        echo -e "${RED}Failed to download proxy secret from ${MTPROXY_SECRET_FILE_URL}.${NC}"
        echo -e "${ORANGE}Check your internet connection and try again.${NC}"
        exit 1
    fi

    if [ ! -f "proxy-secret" ] || [ ! -s "proxy-secret" ]; then
        echo -e "${RED}Proxy secret file is empty or not created.${NC}"
        echo -e "${ORANGE}File details: $(ls -la proxy-secret 2>/dev/null || echo 'File does not exist')${NC}"
        exit 1
    fi

    echo -e "${GREEN}Proxy secret downloaded successfully (size: $(stat -c%s proxy-secret) bytes).${NC}"

    # Generate proxy multi-config
    echo "Downloading proxy configuration..."
    if ! curl -s --max-time 30 "${MTPROXY_CONFIG_FILE_URL}" -o proxy-multi.conf; then
        echo -e "${RED}Failed to download proxy config from ${MTPROXY_CONFIG_FILE_URL}.${NC}"
        echo -e "${ORANGE}Check your internet connection and try again.${NC}"
        exit 1
    fi

    if [ ! -f "proxy-multi.conf" ] || [ ! -s "proxy-multi.conf" ]; then
        echo -e "${RED}Proxy config file is empty or not created.${NC}"
        echo -e "${ORANGE}File details: $(ls -la proxy-multi.conf 2>/dev/null || echo 'File does not exist')${NC}"
        exit 1
    fi

    echo -e "${GREEN}Proxy configuration downloaded successfully (size: $(stat -c%s proxy-multi.conf) bytes).${NC}"
    echo -e "${GREEN}Configuration files downloaded successfully.${NC}"

    # Set permissions
    echo "Setting proper permissions for MTProxy files..."
    chmod 755 "${MTPROXY_SERVICE_FILE}"
    chmod 644 proxy-secret proxy-multi.conf # Restrict permissions on secrets

    # Ensure the binary has execute permissions
    if [ -f "mtproto-proxy" ]; then
        chmod 755 mtproto-proxy
        echo -e "${GREEN}Binary permissions set.${NC}"
    else
        echo -e "${RED}Warning: mtproto-proxy binary not found in working directory.${NC}"
    fi

    # Ensure working directory permissions
    if [ -d "${MTPROXY_DIR}/objs/bin" ]; then
        chown -R nobody:nogroup "${MTPROXY_DIR}/objs/bin" 2>/dev/null || echo -e "${ORANGE}Warning: Could not change ownership to nobody:nogroup. This may cause permission issues.${NC}"
        echo -e "${GREEN}Working directory permissions set.${NC}"
    fi

    # Enable and start service
    echo "Enabling and starting MTProxy service..."
    systemctl daemon-reload

    if ! systemctl enable mtproto-proxy; then
        echo -e "${RED}Failed to enable MTProxy service.${NC}"
        exit 1
    fi

    if ! systemctl start mtproto-proxy; then
        echo -e "${RED}Failed to start MTProxy service.${NC}"
        echo -e "${ORANGE}Attempting to start service with retries and diagnostics...${NC}"

        # Show diagnostic information before retries
        echo -e "${ORANGE}Diagnostic information:${NC}"
        echo -e "Service file: ${MTPROXY_SERVICE_FILE}"
        echo -e "Working directory: ${MTPROXY_DIR}/objs/bin"
        echo -e "Binary exists: $([ -f "${MTPROXY_DIR}/objs/bin/mtproto-proxy" ] && echo 'Yes' || echo 'No')"
        echo -e "Secret file exists: $([ -f "${MTPROXY_DIR}/objs/bin/proxy-secret" ] && echo 'Yes' || echo 'No')"
        echo -e "Config file exists: $([ -f "${MTPROXY_DIR}/objs/bin/proxy-multi.conf" ] && echo 'Yes' || echo 'No')"

        # Check systemd status
        systemctl status mtproto-proxy --no-pager -l || echo -e "${RED}Could not get service status.${NC}"

        # Retry starting the service up to 3 times
        for i in {1..3}; do
            echo -e "${ORANGE}Retry attempt $i/3...${NC}"
            sleep 3
            if systemctl start mtproto-proxy; then
                echo -e "${GREEN}Service started successfully on retry $i.${NC}"
                break
            fi
            if [ $i -eq 3 ]; then
                echo -e "${RED}Service failed to start after 3 attempts.${NC}"
                echo -e "${ORANGE}Troubleshooting commands:${NC}"
                echo -e "  systemctl status mtproto-proxy"
                echo -e "  journalctl -u mtproto-proxy -f --no-pager -n 50"
                echo -e "  journalctl -xe --no-pager -n 20"
                echo -e "${ORANGE}Installation completed but service may need manual intervention.${NC}"
                # Don't exit here, continue with configuration
            fi
        done
    fi

    # Check service status and provide detailed information
    echo "Checking final service status..."
    if systemctl is-active --quiet mtproto-proxy; then
        echo -e "${GREEN}MTProxy service is running successfully.${NC}"
        # Show listening ports
        ss -tlnp | grep :${PORT} || echo -e "${ORANGE}Warning: Port ${PORT} not found in listening sockets.${NC}"
    else
        echo -e "${RED}Warning: MTProxy service is not active.${NC}"
        echo -e "${ORANGE}Service status details:${NC}"
        systemctl status mtproto-proxy --no-pager -l || echo -e "${RED}Could not retrieve service status.${NC}"

        echo -e "${ORANGE}Recent logs:${NC}"
        journalctl -u mtproto-proxy --no-pager -n 10 -q || echo -e "${RED}Could not retrieve logs.${NC}"

        echo -e "${ORANGE}Common troubleshooting steps:${NC}"
        echo -e "1. Check if all required files exist: ls -la ${MTPROXY_DIR}/objs/bin/"
        echo -e "2. Verify permissions: ls -ld ${MTPROXY_DIR}/objs/bin/"
        echo -e "3. Test manual execution: cd ${MTPROXY_DIR}/objs/bin && sudo -u nobody ./mtproto-proxy --version"
        echo -e "4. Check systemd logs: journalctl -u mtproto-proxy -f"
    fi

    # Save configuration
    cat > "${MTPROXY_CONFIG_FILE}" << EOL
IP=${IP}
PORT=${PORT}
SECRET=${SECRET}
MTPROXY_DIR=${MTPROXY_DIR}
MTPROXY_SERVICE_FILE=${MTPROXY_SERVICE_FILE}
EOL

    # --- Generación de .env para uSipipo ---
    generate_env_files

    # Print connection info
    echo -e "\n${GREEN}MTProto Proxy installed successfully!${NC}"
    echo -e "${GREEN}Configuration:${NC}"
    echo -e "IP: ${IP}"
    echo -e "Port: ${PORT}"
    echo -e "Secret: ${SECRET}"
    echo -e "\n${GREEN}You can use this link to connect to your proxy:${NC}"
    echo -e "tg://proxy?server=${IP}&port=${PORT}&secret=${SECRET}"
}

function generate_env_files() {
    # Archivo de configuración principal de MTProxy para uSipipo
    ENV_FILE_MTPROXY=".env.mtproxy.generated"

    echo "# --- uSipipo MTProto Server Configuration ---" > "${ENV_FILE_MTPROXY}"
    echo "MTPROXY_HOST=\"${IP}\"" >> "${ENV_FILE_MTPROXY}"
    echo "MTPROXY_PORT=\"${PORT}\"" >> "${ENV_FILE_MTPROXY}"
    echo "MTPROXY_SECRET=\"${SECRET}\"" >> "${ENV_FILE_MTPROXY}"
    echo "MTPROXY_DIR=\"${MTPROXY_DIR}\"" >> "${ENV_FILE_MTPROXY}"

    # Agregar configuración DNS si Pi-hole está disponible
    if detect_pihole; then
        echo "MTPROXY_DNS=\"${PIHOLE_IP}\"" >> "${ENV_FILE_MTPROXY}"
        echo "# DNS: Using Pi-hole (${PIHOLE_IP}) for DNS resolution" >> "${ENV_FILE_MTPROXY}"
    else
        echo "# DNS: Using default DNS configuration" >> "${ENV_FILE_MTPROXY}"
    fi

    # No se genera TAG aquí, se haría manualmente o mediante otro proceso
    # echo "MTPROXY_TAG=\"\" # Add your tag here if registered with @MTProxybot" >> "${ENV_FILE_MTPROXY}"
    echo "" >> "${ENV_FILE_MTPROXY}"

    echo -e "\n${GREEN}--- VARIABLES MTPROXY PARA TU .env DE USIPIPO ---${NC}"
    echo -e "${ORANGE}Archivo de configuración generado:${NC} ${ENV_FILE_MTPROXY}"
    echo -e "${GREEN}----------------------------------------------------------${NC}"
    echo -e "\n${GREEN}Contenido de ${ENV_FILE_MTPROXY}:${NC}"
    cat "${ENV_FILE_MTPROXY}"
    echo -e "\n${GREEN}----------------------------------------------------------${NC}"
    echo -e "¡Copia estas variables a tu archivo .env de uSipipo!
    "
}

function uninstallMTProxy() {
    local FORCE_REMOVE="${1:-false}"

    if [[ "${FORCE_REMOVE}" != "true" ]]; then
        echo -e "\n${RED}WARNING: This will uninstall MTProxy and remove all configuration files!${NC}"
        read -rp "Do you really want to remove MTProxy? [y/n]: " -e REMOVE

        if [[ $REMOVE != 'y' ]]; then
            echo -e "${ORANGE}Uninstall cancelled${NC}"
            return 1
        fi
    fi

    echo "Stopping and disabling MTProxy service..."
    systemctl stop mtproto-proxy 2>/dev/null || echo -e "${ORANGE}Service was not running.${NC}"
    systemctl disable mtproto-proxy 2>/dev/null || echo -e "${ORANGE}Service was not enabled.${NC}"

    echo "Removing service file and installation directory..."
    rm -f "${MTPROXY_SERVICE_FILE}"
    rm -rf "${MTPROXY_DIR}"

    echo "Reloading systemd daemon..."
    systemctl daemon-reload

    # Remove generated .env file
    rm -f ".env.mtproxy.generated"

    # Remove config file if it exists
    rm -f "${MTPROXY_CONFIG_FILE}"

    echo -e "${GREEN}MTProxy has been completely removed!${NC}"
    return 0
}

function showMenu() {
    echo "Welcome to MTProto installer for uSipipo!"
    echo ""
    echo "What do you want to do?"
    echo "   1) Install MTProxy"
    echo "   2) Uninstall MTProxy"
    echo "   3) Show current configuration"
    echo "   4) Exit"

    until [[ ${MENU_OPTION} =~ ^[1-4]$ ]]; do
        read -rp "Select an option [1-4]: " MENU_OPTION
    done

    case "${MENU_OPTION}" in
        1)
            initialCheck
            installDependencies
            installMTProxy
            ;;
        2)
            uninstallMTProxy
            ;;
        3)
            if [ -f "${MTPROXY_CONFIG_FILE}" ]; then
                source "${MTPROXY_CONFIG_FILE}"
                echo -e "${GREEN}Current MTProxy Configuration:${NC}"
                echo -e "IP: ${IP}"
                echo -e "Port: ${PORT}"
                echo -e "Secret: ${SECRET}"
                echo -e "Directory: ${MTPROXY_DIR}"
                echo -e "Service File: ${MTPROXY_SERVICE_FILE}"
                echo -e "\nConnection Link:"
                echo -e "tg://proxy?server=${IP}&port=${PORT}&secret=${SECRET}"

                echo -e "\n${GREEN}Service Status:${NC}"
                if systemctl is-active --quiet mtproto-proxy; then
                    echo -e "${GREEN}Service is running${NC}"
                    # Show listening port
                    ss -tlnp | grep :${PORT} && echo -e "${GREEN}Port ${PORT} is listening${NC}" || echo -e "${ORANGE}Warning: Port ${PORT} not found in listening sockets${NC}"
                else
                    echo -e "${RED}Service is not running${NC}"
                    echo -e "${ORANGE}Last logs:${NC}"
                    journalctl -u mtproto-proxy --no-pager -n 5 -q 2>/dev/null || echo -e "${RED}Could not retrieve logs${NC}"
                fi

                echo -e "\n${GREEN}File Status:${NC}"
                echo -e "Binary: $([ -f "${MTPROXY_DIR}/objs/bin/mtproto-proxy" ] && echo 'Present' || echo 'Missing')"
                echo -e "Secret: $([ -f "${MTPROXY_DIR}/objs/bin/proxy-secret" ] && echo 'Present' || echo 'Missing')"
                echo -e "Config: $([ -f "${MTPROXY_DIR}/objs/bin/proxy-multi.conf" ] && echo 'Present' || echo 'Missing')"
            else
                echo -e "${RED}MTProxy is not installed or configuration file not found.${NC}"
            fi
            ;;
        4)
            exit 0
            ;;
    esac
}

# --- Funciones de Argumentos ---
function showHelp() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --install          Install MTProxy (default if not installed)"
    echo "  --uninstall        Uninstall MTProxy completely"
    echo "  --reinstall        Reinstall MTProxy (uninstall then install)"
    echo "  --help             Show this help message"
    echo ""
    echo "If no options are provided, an interactive menu will be shown."
}

function parseArgs() {
    ACTION=""
    while [[ $# -gt 0 ]]; do
        case $1 in
            --install)
                ACTION="install"
                shift
                ;;
            --uninstall)
                ACTION="uninstall"
                shift
                ;;
            --reinstall)
                ACTION="reinstall"
                shift
                ;;
            --help)
                showHelp
                exit 0
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                showHelp
                exit 1
                ;;
        esac
    done
}

# --- Punto de entrada ---
parseArgs "$@"

case "${ACTION}" in
    "install")
        if [ -f "${MTPROXY_CONFIG_FILE}" ]; then
            echo -e "${ORANGE}MTProxy is already installed. Use --reinstall to reinstall.${NC}"
            exit 0
        fi
        initialCheck
        installDependencies
        installMTProxy
        ;;
    "uninstall")
        if [ ! -f "${MTPROXY_CONFIG_FILE}" ]; then
            echo -e "${ORANGE}MTProxy is not installed.${NC}"
            exit 0
        fi
        uninstallMTProxy
        ;;
    "reinstall")
        if [ -f "${MTPROXY_CONFIG_FILE}" ]; then
            echo "Uninstalling existing MTProxy installation..."
            uninstallMTProxy true
        fi
        echo "Starting fresh installation..."
        initialCheck
        installDependencies
        installMTProxy
        ;;
    "")
        # No arguments provided, show interactive menu
        if [ -f "${MTPROXY_CONFIG_FILE}" ]; then
            showMenu
        else
            # If not installed, start installation
            initialCheck
            installDependencies
            installMTProxy
        fi
        ;;
esac