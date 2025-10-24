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
    apt-get update
    apt-get install -y git curl build-essential libssl-dev zlib1g-dev xxd
}

function installMTProxy() {
    # Create directory for MTProxy
    mkdir -p "${MTPROXY_DIR}"
    cd "${MTPROXY_DIR}" || exit

    # Clone MTProxy repository if not already present or if it's empty
    if [ ! -d ".git" ] || [ -z "$(ls -A "${MTPROXY_DIR}")" ]; then
        echo "Cloning MTProxy repository..."
        git clone "${MTPROXY_REPO_URL}" .
    else
        echo "MTProxy repository already exists, skipping clone."
    fi

    # Build MTProxy
    echo "Building MTProxy..."
    make clean # Ensure clean build
    make LDFLAGS="-Wl,--allow-multiple-definition" || { echo -e "${RED}Build failed.${NC}"; exit 1; }

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

[Install]
WantedBy=multi-user.target
EOL

    # Generate proxy secret
    curl -s "${MTPROXY_SECRET_FILE_URL}" -o proxy-secret
    if [ ! -f "proxy-secret" ] || [ ! -s "proxy-secret" ]; then
        echo -e "${RED}Failed to download proxy secret.${NC}"
        exit 1
    fi

    # Generate proxy multi-config
    curl -s "${MTPROXY_CONFIG_FILE_URL}" -o proxy-multi.conf
    if [ ! -f "proxy-multi.conf" ] || [ ! -s "proxy-multi.conf" ]; then
        echo -e "${RED}Failed to download proxy config.${NC}"
        exit 1
    fi

    # Set permissions
    chmod 755 "${MTPROXY_SERVICE_FILE}"
    chmod 644 proxy-secret proxy-multi.conf # Restrict permissions on secrets

    # Enable and start service
    systemctl daemon-reload
    systemctl enable mtproto-proxy
    systemctl start mtproto-proxy

    # Verify service is running
    if ! systemctl is-active --quiet mtproto-proxy; then
        echo -e "${RED}MTProxy service failed to start.${NC}"
        exit 1
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
    echo -e "\n${RED}WARNING: This will uninstall MTProxy and remove all configuration files!${NC}"
    read -rp "Do you really want to remove MTProxy? [y/n]: " -e REMOVE

    if [[ $REMOVE == 'y' ]]; then
        systemctl stop mtproto-proxy
        systemctl disable mtproto-proxy
        rm -f "${MTPROXY_SERVICE_FILE}"
        rm -rf "${MTPROXY_DIR}"
        systemctl daemon-reload

        # Remove generated .env file
        rm -f ".env.mtproxy.generated"

        echo -e "${GREEN}MTProxy has been removed successfully!${NC}"
    else
        echo -e "${ORANGE}Uninstall cancelled${NC}"
    fi
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
                echo -e "\nConnection Link:"
                echo -e "tg://proxy?server=${IP}&port=${PORT}&secret=${SECRET}"
            else
                echo -e "${RED}MTProxy is not installed or configuration file not found.${NC}"
            fi
            ;;
        4)
            exit 0
            ;;
    esac
}

# --- Punto de entrada ---
# Check if MTProxy is already installed
if [ -f "${MTPROXY_CONFIG_FILE}" ]; then
    showMenu
else
    # If not installed, start installation
    initialCheck
    installDependencies
    installMTProxy
fi