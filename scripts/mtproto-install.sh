#!/bin/bash

# Secure MTProto Proxy installer for Telegram
# Based on https://github.com/TelegramMessenger/MTProxy
# and https://gist.github.com/lugodev/05762d0252ed71c6a346f53f60466369

RED='\033[0;31m'
ORANGE='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'

function isRoot() {
    if [ "${EUID}" -ne 0 ]; then
        echo "You need to run this script as root"
        exit 1
    fi
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

function installDependencies() {
    echo "Installing required packages..."
    apt-get update
    apt-get install -y git curl build-essential libssl-dev zlib1g-dev
}

function installMTProxy() {
    # Create directory for MTProxy
    mkdir -p /opt/mtproto-proxy
    cd /opt/mtproto-proxy || exit

    # Clone MTProxy repository
    echo "Cloning MTProxy repository..."
    git clone https://github.com/TelegramMessenger/MTProxy.git .
    
    # Build MTProxy
    echo "Building MTProxy..."
    make && cd objs/bin

    # Generate a secret
    SECRET=$(head -c 16 /dev/urandom | xxd -ps)
    
    # Get your external IP
    IP=$(curl -4 -s https://api.ipify.org)
    
    # Generate a random port between 10000-60000
    PORT=$(( ((RANDOM<<15)|RANDOM) % 49152 + 10000 ))

    # Create systemd service
    echo "Creating systemd service..."
    cat > /etc/systemd/system/mtproto-proxy.service << EOL
[Unit]
Description=MTProxy for Telegram
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/mtproto-proxy/objs/bin
ExecStart=/opt/mtproto-proxy/objs/bin/mtproto-proxy -u nobody -p 8888 -H ${PORT} -S ${SECRET} --aes-pwd /opt/mtproto-proxy/objs/bin/proxy-secret /opt/mtproto-proxy/objs/bin/proxy-multi.conf -M 1
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL

    # Generate proxy secret
    curl -s https://core.telegram.org/getProxySecret -o /opt/mtproto-proxy/objs/bin/proxy-secret
    
    # Generate proxy multi-config
    curl -s https://core.telegram.org/getProxyConfig -o /opt/mtproto-proxy/objs/bin/proxy-multi.conf
    
    # Set permissions
    chmod 755 /etc/systemd/system/mtproto-proxy.service
    
    # Enable and start service
    systemctl daemon-reload
    systemctl enable mtproto-proxy
    systemctl start mtproto-proxy
    
    # Print connection info
    echo -e "${GREEN}MTProto Proxy installed successfully!${NC}"
    echo -e "${GREEN}Configuration:${NC}"
    echo -e "IP: ${IP}"
    echo -e "Port: ${PORT}"
    echo -e "Secret: ${SECRET}"
    echo -e "\n${GREEN}You can use this link to connect to your proxy:${NC}"
    echo -e "tg://proxy?server=${IP}&port=${PORT}&secret=${SECRET}"
    
    # Save configuration
    echo "IP=${IP}
PORT=${PORT}
SECRET=${SECRET}" > /opt/mtproto-proxy/config.env
}

function uninstallMTProxy() {
    echo -e "\n${RED}WARNING: This will uninstall MTProxy and remove all configuration files!${NC}"
    read -rp "Do you really want to remove MTProxy? [y/n]: " -e REMOVE
    
    if [[ $REMOVE == 'y' ]]; then
        systemctl stop mtproto-proxy
        systemctl disable mtproto-proxy
        rm -f /etc/systemd/system/mtproto-proxy.service
        rm -rf /opt/mtproto-proxy
        systemctl daemon-reload
        
        echo -e "${GREEN}MTProxy has been removed successfully!${NC}"
    else
        echo -e "${ORANGE}Uninstall cancelled${NC}"
    fi
}

function showMenu() {
    echo "Welcome to MTProxy installer!"
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
            if [ -f "/opt/mtproto-proxy/config.env" ]; then
                source /opt/mtproto-proxy/config.env
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

# Check if MTProxy is already installed
if [ -f "/opt/mtproto-proxy/config.env" ]; then
    showMenu
else
    # If not installed, start installation
    initialCheck
    installDependencies
    installMTProxy
fi