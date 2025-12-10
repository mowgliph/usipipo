#!/bin/bash

# =====================================================================
#  uSipipo — WireGuard Server Installer (Debian 12 compatible)
#  Versión modificada para:
#   ✔ Mantener resolvconf instalado
#   ✔ Configurar DNS del servidor correctamente sin romper /etc/resolv.conf
#   ✔ Forzar DNS correcto para evitar pérdida de conectividad
#   ✔ Evitar endpoint = 127.0.0.1 (se autocalcula correctamente)
# =====================================================================

RED='\033[0;31m'
ORANGE='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'

function installPackages() {
    if ! "$@"; then
        echo -e "${RED}Failed to install packages.${NC}"
        exit 1
    fi
}

function isRoot() {
    if [ "${EUID}" -ne 0 ]; then
        echo "You need to run this script as root"
        exit 1
    fi
}

function checkOS() {
    source /etc/os-release
    if [[ "${ID}" != "debian" ]]; then
        echo "ERROR: Este script sólo soporta Debian 12 totalmente validado."
        exit 1
    fi
}

function initialCheck() {
    isRoot
    checkOS
}

function fixServerDNS() {
    echo -e "${GREEN}✔ Aplicando DNS correctos al servidor (sin romper resolv.conf)…${NC}"

    installPackages apt-get install -y resolvconf

    echo "nameserver 1.1.1.1" > /etc/resolvconf/resolv.conf.d/head
    echo "nameserver 1.0.0.1" >> /etc/resolvconf/resolv.conf.d/head
    echo "search local" >> /etc/resolvconf/resolv.conf.d/head

    resolvconf -u

    sleep 1
    echo -e "${GREEN}✔ DNS actual del servidor:${NC}"
    cat /etc/resolv.conf
}

function installQuestions() {
    echo ""
    echo "=== WireGuard — Configuración Inicial ==="
    echo ""

    SERVER_PUB_IP=$(curl -s https://api.ipify.org || wget -qO- https://api.ipify.org)
    if [[ -z "$SERVER_PUB_IP" ]]; then
        echo -e "${RED}ERROR: No se pudo obtener IP pública. DNS roto. Aborta.${NC}"
        exit 1
    fi

    read -rp "IP pública del servidor: " -e -i "$SERVER_PUB_IP" SERVER_PUB_IP

    SERVER_NIC=$(ip route get 1.1.1.1 | grep -oP 'dev \K\w+' | head -1)
    read -rp "Interfaz pública: " -e -i "$SERVER_NIC" SERVER_PUB_NIC

    read -rp "Nombre de interfaz WG: " -e -i wg0 SERVER_WG_NIC
    read -rp "IP interna WG IPv4: " -e -i 10.66.66.1 SERVER_WG_IPV4
    read -rp "IP interna WG IPv6: " -e -i fd42:42:42::1 SERVER_WG_IPV6

    RANDOM_PORT=$(shuf -i 49152-65535 -n1)
    read -rp "Puerto WireGuard: " -e -i "$RANDOM_PORT" SERVER_PORT

    read -rp "Cliente DNS 1: " -e -i 1.1.1.1 CLIENT_DNS_1
    read -rp "Cliente DNS 2: " -e -i 1.0.0.1 CLIENT_DNS_2

    read -rp "AllowedIPs: " -e -i "0.0.0.0/0,::/0" ALLOWED_IPS
}

function installWireGuard() {
    installQuestions
    fixServerDNS

    echo -e "${GREEN}✔ Instalando WireGuard...${NC}"
    apt-get update
    installPackages apt-get install -y wireguard qrencode iptables resolvconf

    mkdir -p /etc/wireguard
    chmod 600 /etc/wireguard

    SERVER_PRIV_KEY=$(wg genkey)
    SERVER_PUB_KEY=$(echo "$SERVER_PRIV_KEY" | wg pubkey)

    echo "
SERVER_PUB_IP=$SERVER_PUB_IP
SERVER_PUB_NIC=$SERVER_PUB_NIC
SERVER_WG_NIC=$SERVER_WG_NIC
SERVER_WG_IPV4=$SERVER_WG_IPV4
SERVER_WG_IPV6=$SERVER_WG_IPV6
SERVER_PORT=$SERVER_PORT
SERVER_PRIV_KEY=$SERVER_PRIV_KEY
SERVER_PUB_KEY=$SERVER_PUB_KEY
CLIENT_DNS_1=$CLIENT_DNS_1
CLIENT_DNS_2=$CLIENT_DNS_2
ALLOWED_IPS=$ALLOWED_IPS
" > /etc/wireguard/params

    # 🟢 AÑADIR MTU AQUÍ
    echo "[Interface]
Address = ${SERVER_WG_IPV4}/24,${SERVER_WG_IPV6}/64
ListenPort = ${SERVER_PORT}
PrivateKey = ${SERVER_PRIV_KEY}
MTU = 1420
PostUp = iptables -I INPUT -p udp --dport ${SERVER_PORT} -j ACCEPT
PostUp = iptables -t nat -A POSTROUTING -o ${SERVER_PUB_NIC} -j MASQUERADE
PostDown = iptables -D INPUT -p udp --dport ${SERVER_PORT} -j ACCEPT
PostDown = iptables -t nat -D POSTROUTING -o ${SERVER_PUB_NIC} -j MASQUERADE
" > "/etc/wireguard/${SERVER_WG_NIC}.conf"

    echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/99-wireguard-forward.conf
    echo "net.ipv6.conf.all.forwarding=1" >> /etc/sysctl.d/99-wireguard-forward.conf
    sysctl -p /etc/sysctl.d/99-wireguard-forward.conf

    systemctl enable --now "wg-quick@${SERVER_WG_NIC}"

    newClient
}


function newClient() {
    source /etc/wireguard/params

    # Si la IP pública es IPv6, envolver en [ ]
    if [[ ${SERVER_PUB_IP} =~ .*:.* ]]; then
        if [[ ${SERVER_PUB_IP} != *"["* ]]; then
            SERVER_PUB_IP="[${SERVER_PUB_IP}]"
        fi
    fi

    ENDPOINT="${SERVER_PUB_IP}:${SERVER_PORT}"

    echo ""
    echo "=== Crear nuevo cliente ==="
    echo ""

    until [[ ${CLIENT_NAME} =~ ^[a-zA-Z0-9_-]+$ && ${#CLIENT_NAME} -lt 16 ]]; do
        read -rp "Nombre del cliente: " CLIENT_NAME
    done

    for DOT_IP in {2..254}; do
        if ! grep -q "${SERVER_WG_IPV4::-1}${DOT_IP}" "/etc/wireguard/${SERVER_WG_NIC}.conf"; then
            break
        fi
    done

    BASE_V4=$(echo "$SERVER_WG_IPV4" | awk -F '.' '{ print $1"."$2"."$3 }')
    CLIENT_WG_IPV4="${BASE_V4}.${DOT_IP}"

    BASE_V6=$(echo "$SERVER_WG_IPV6" | awk -F '::' '{ print $1 }')
    CLIENT_WG_IPV6="${BASE_V6}::${DOT_IP}"

    CLIENT_PRIV_KEY=$(wg genkey)
    CLIENT_PUB_KEY=$(echo "$CLIENT_PRIV_KEY" | wg pubkey)
    CLIENT_PSK=$(wg genpsk)

    HOME_DIR="/root"

    CLIENT_FILE="${HOME_DIR}/${SERVER_WG_NIC}-client-${CLIENT_NAME}.conf"

    # 🟢 AÑADIR MTU Y PERSISTENTKEEPALIVE AQUÍ
    echo "[Interface]
PrivateKey = ${CLIENT_PRIV_KEY}
Address = ${CLIENT_WG_IPV4}/32,${CLIENT_WG_IPV6}/128
DNS = ${CLIENT_DNS_1},${CLIENT_DNS_2}
MTU = 1420

[Peer]
PublicKey = ${SERVER_PUB_KEY}
PresharedKey = ${CLIENT_PSK}
Endpoint = ${ENDPOINT}
AllowedIPs = ${ALLOWED_IPS}
PersistentKeepalive = 15
" > "${CLIENT_FILE}"

    echo "### Client ${CLIENT_NAME}
[Peer]
PublicKey = ${CLIENT_PUB_KEY}
PresharedKey = ${CLIENT_PSK}
AllowedIPs = ${CLIENT_WG_IPV4}/32,${CLIENT_WG_IPV6}/128
" >> "/etc/wireguard/${SERVER_WG_NIC}.conf"

    wg syncconf "${SERVER_WG_NIC}" <(wg-quick strip "${SERVER_WG_NIC}")

    echo -e "${GREEN}✔ Cliente creado:${NC} ${CLIENT_FILE}"

    if command -v qrencode &>/dev/null; then
        echo -e "${GREEN}\nQR para conexión móvil:\n${NC}"
        qrencode -t ansiutf8 < "${CLIENT_FILE}"
    fi
}


function listClients() {
    NUMBER_OF_CLIENTS=$(grep -c -E "^### Client" "/etc/wireguard/${SERVER_WG_NIC}.conf")
    if [[ ${NUMBER_OF_CLIENTS} -eq 0 ]]; then
        echo "No hay clientes."
        exit 1
    fi

    echo ""
    echo "=== Lista de clientes ==="
    grep -E "^### Client" "/etc/wireguard/${SERVER_WG_NIC}.conf" | cut -d ' ' -f3 | nl -s ') '
}

function revokeClient() {
    NUMBER_OF_CLIENTS=$(grep -c -E "^### Client" "/etc/wireguard/${SERVER_WG_NIC}.conf")
    if [[ ${NUMBER_OF_CLIENTS} -eq 0 ]]; then
        echo "No hay clientes para revocar."
        exit 1
    fi

    echo ""
    echo "=== Revocar cliente ==="
    grep -E "^### Client" "/etc/wireguard/${SERVER_WG_NIC}.conf" | cut -d ' ' -f3 | nl -s ') '

    until [[ ${CLIENT_NUMBER} -ge 1 && ${CLIENT_NUMBER} -le ${NUMBER_OF_CLIENTS} ]]; do
        read -rp "Seleccione un cliente [1-${NUMBER_OF_CLIENTS}]: " CLIENT_NUMBER
    done

    CLIENT_NAME=$(grep -E "^### Client" "/etc/wireguard/${SERVER_WG_NIC}.conf" | cut -d ' ' -f3 | sed -n "${CLIENT_NUMBER}"p)

    sed -i "/^### Client ${CLIENT_NAME}\$/,/^$/d" "/etc/wireguard/${SERVER_WG_NIC}.conf"

    rm -f "/root/${SERVER_WG_NIC}-client-${CLIENT_NAME}.conf"

    wg syncconf "${SERVER_WG_NIC}" <(wg-quick strip "${SERVER_WG_NIC}")

    echo -e "${GREEN}✔ Cliente ${CLIENT_NAME} revocado.${NC}"
}

function uninstallWg() {
    read -rp "¿Deseas desinstalar completamente WireGuard? [y/N]: " REMOVE
    REMOVE=${REMOVE:-n}

    if [[ $REMOVE != "y" ]]; then
        echo "Cancelado."
        return
    fi

    systemctl stop "wg-quick@${SERVER_WG_NIC}"
    systemctl disable "wg-quick@${SERVER_WG_NIC}"

    apt-get remove -y wireguard wireguard-tools qrencode

    rm -rf /etc/wireguard
    rm -f /etc/sysctl.d/99-wireguard-forward.conf
    sysctl --system

    echo -e "${GREEN}WireGuard desinstalado correctamente.${NC}"
}

function manageMenu() {
    echo ""
    echo "=== WireGuard ya está instalado ==="
    echo ""
    echo "1) Añadir cliente"
    echo "2) Listar clientes"
    echo "3) Revocar cliente"
    echo "4) Desinstalar WireGuard"
    echo "5) Salir"

    until [[ ${MENU_OPTION} =~ ^[1-5]$ ]]; do
        read -rp "Opción [1-5]: " MENU_OPTION
    done

    case "$MENU_OPTION" in
        1) newClient ;;
        2) listClients ;;
        3) revokeClient ;;
        4) uninstallWg ;;
        5) exit 0 ;;
    esac
}

# =====================================================
#          EJECUCIÓN PRINCIPAL DEL SCRIPT
# =====================================================

initialCheck

if [[ -e /etc/wireguard/params ]]; then
    source /etc/wireguard/params
    manageMenu
else
    installWireGuard
fi