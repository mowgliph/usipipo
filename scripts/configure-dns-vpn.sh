#!/bin/bash

# DNS Configuration Script for VPN Services - uSipipo
# Configures Outline, WireGuard, and MTProto to use Pi-hole as DNS server
# Reads configuration from generated .env files

set -euo pipefail

# --- Constantes ---
SCRIPT_VERSION="1.0.0"
PIHOLE_ENV_FILE=".env.pihole.generated"
OUTLINE_ENV_FILE=".env.outline.generated"
WIREGUARD_ENV_FILE=".env.wireguard.generated"
MTPROXY_ENV_FILE=".env.mtproxy.generated"
DNS_CONFIG_ENV_FILE=".env.dns-config.generated"

# --- Variables globales ---
PIHOLE_HOST=""
PIHOLE_PORT=""
PIHOLE_DNS_PORT=""
OUTLINE_CONTAINER_NAME=""
WIREGUARD_CONFIG_DIR=""
MTPROXY_SERVICE_FILE=""
REVERT_MODE=false

# --- Colores ---
RED='\033[0;31m'
ORANGE='\033[0;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# --- Funciones de Logging ---
FULL_LOG="$(mktemp -t dns_config_logXXXXXXXXXX)"
LAST_ERROR="$(mktemp -t dns_config_last_errorXXXXXXXXXX)"
readonly FULL_LOG LAST_ERROR

function log_command() {
    "$@" > >(tee -a "${FULL_LOG}") 2> >(tee -a "${FULL_LOG}" > "${LAST_ERROR}")
}

function log_error() {
    local ERROR_TEXT="${RED}"
    local NO_COLOR="${NC}"
    echo -e "${ERROR_TEXT}$1${NO_COLOR}"
    echo "$1" >> "${FULL_LOG}"
}

function log_start_step() {
    local str="> $*"
    local lineLength=47
    echo -n "${str}"
    local numDots=$(( lineLength - ${#str} - 1 ))
    if (( numDots > 0 )); then
        echo -n " "
        for _ in $(seq 1 "${numDots}"); do echo -n .; done
    fi
    echo -n " "
}

function run_step() {
    local msg="$1"
    log_start_step "${msg}"
    shift 1
    if log_command "$@"; then
        echo "OK"
    else
        return
    fi
}

# --- Funciones de Validación ---
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
            echo "Your version of Debian (${VERSION_ID}) is not supported. Please use Debian 10 Buster or later"
            exit 1
        fi
        OS=debian
    elif [[ ${OS} == "ubuntu" ]]; then
        RELEASE_YEAR=$(echo "${VERSION_ID}" | cut -d'.' -f1)
        if [[ ${RELEASE_YEAR} -lt 18 ]]; then
            echo "Your version of Ubuntu (${VERSION_ID}) is not supported. Please use Ubuntu 18.04 or later"
            exit 1
        fi
    else
        echo "Looks like you aren't running this installer on a Debian or Ubuntu system"
        echo "Supported distributions are Debian and Ubuntu."
        exit 1
    fi
}

function initialCheck() {
    isRoot
    checkOS
}

function load_env_files() {
    log_start_step "Loading configuration files"

    # Load Pi-hole configuration
    if [ ! -f "${PIHOLE_ENV_FILE}" ]; then
        log_error "FAILED"
        log_error "Pi-hole configuration file not found: ${PIHOLE_ENV_FILE}"
        log_error "Please run pihole-install.sh first"
        exit 1
    fi
    source "${PIHOLE_ENV_FILE}"

    PIHOLE_HOST="${PIHOLE_HOST:-localhost}"
    PIHOLE_DNS_PORT="${PIHOLE_DNS_PORT:-53}"

    # Load Outline configuration
    if [ -f "${OUTLINE_ENV_FILE}" ]; then
        source "${OUTLINE_ENV_FILE}"
        OUTLINE_CONTAINER_NAME="${OUTLINE_CONTAINER_NAME:-outline}"
    fi

    # Load WireGuard configuration
    if [ -f "${WIREGUARD_ENV_FILE}" ]; then
        source "${WIREGUARD_ENV_FILE}"
        WIREGUARD_CONFIG_DIR="${WG_CONFIG_DIR:-/etc/wireguard}"
    fi

    # Load MTProto configuration
    if [ -f "${MTPROXY_ENV_FILE}" ]; then
        source "${MTPROXY_ENV_FILE}"
        MTPROXY_SERVICE_FILE="${MTPROXY_SERVICE_FILE:-/etc/systemd/system/mtproto-proxy.service}"
    fi

    echo "OK"
}

# --- Funciones de Configuración DNS ---
function configure_outline_dns() {
    if [ -z "${OUTLINE_CONTAINER_NAME}" ]; then
        log_start_step "Outline not configured - skipping"
        echo "SKIP"
        return 0
    fi

    log_start_step "Configuring Outline DNS"

    # Check if Outline container exists and is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${OUTLINE_CONTAINER_NAME}$"; then
        log_error "FAILED"
        log_error "Outline container '${OUTLINE_CONTAINER_NAME}' is not running"
        return 1
    fi

    # Update DNS configuration in Outline container
    # Outline uses environment variables for DNS configuration
    docker exec "${OUTLINE_CONTAINER_NAME}" sh -c "
        echo 'DNS1=${PIHOLE_HOST}' > /tmp/dns_env
        echo 'DNS2=1.0.0.1' >> /tmp/dns_env
        echo 'DNSSEC=false' >> /tmp/dns_env
    " || {
        log_error "FAILED"
        log_error "Failed to update Outline DNS configuration"
        return 1
    }

    # Restart Outline to apply DNS changes
    docker restart "${OUTLINE_CONTAINER_NAME}" || {
        log_error "FAILED"
        log_error "Failed to restart Outline container"
        return 1
    }

    echo "OK"
}

function configure_wireguard_dns() {
    if [ -z "${WIREGUARD_CONFIG_DIR}" ]; then
        log_start_step "WireGuard not configured - skipping"
        echo "SKIP"
        return 0
    fi

    log_start_step "Configuring WireGuard DNS"

    # Check if WireGuard config directory exists
    if [ ! -d "${WIREGUARD_CONFIG_DIR}" ]; then
        log_error "FAILED"
        log_error "WireGuard config directory not found: ${WIREGUARD_CONFIG_DIR}"
        return 1
    fi

    # Find WireGuard interface config file
    local wg_conf_file=""
    for conf_file in "${WIREGUARD_CONFIG_DIR}"/*.conf; do
        if [ -f "$conf_file" ]; then
            wg_conf_file="$conf_file"
            break
        fi
    done

    if [ -z "$wg_conf_file" ]; then
        log_error "FAILED"
        log_error "No WireGuard configuration file found"
        return 1
    fi

    # Update DNS in WireGuard server config (for future clients)
    sed -i "s/CLIENT_DNS_1=.*/CLIENT_DNS_1=${PIHOLE_HOST}/" "${WIREGUARD_CONFIG_DIR}/params" 2>/dev/null || true

    # Update existing client configurations
    local interface_name
    interface_name=$(basename "$wg_conf_file" .conf)

    # Find all client config files and update DNS
    for client_conf in /home/*/"${interface_name}"-client-*.conf /root/"${interface_name}"-client-*.conf; do
        if [ -f "$client_conf" ]; then
            # Update DNS line in client config
            sed -i "s/DNS = .*/DNS = ${PIHOLE_HOST},${PIHOLE_DNS_PORT}/" "$client_conf" || {
                log_error "FAILED"
                log_error "Failed to update DNS in client config: $client_conf"
                return 1
            }
        fi
    done

    # Reload WireGuard configuration
    wg syncconf "$interface_name" <(wg-quick strip "$interface_name") || {
        log_error "FAILED"
        log_error "Failed to reload WireGuard configuration"
        return 1
    }

    echo "OK"
}

function configure_mtproto_dns() {
    if [ -z "${MTPROXY_SERVICE_FILE}" ]; then
        log_start_step "MTProto not configured - skipping"
        echo "SKIP"
        return 0
    fi

    log_start_step "Configuring MTProto DNS"

    # Check if MTProto service file exists
    if [ ! -f "${MTPROXY_SERVICE_FILE}" ]; then
        log_error "FAILED"
        log_error "MTProto service file not found: ${MTPROXY_SERVICE_FILE}"
        return 1
    fi

    # MTProto proxy typically uses system DNS, but we can set environment variables
    # Create a drop-in configuration for systemd to set DNS
    local drop_in_dir="/etc/systemd/system/mtproto-proxy.service.d"
    mkdir -p "$drop_in_dir"

    cat > "${drop_in_dir}/dns.conf" << EOF
[Service]
Environment="DNS_SERVER=${PIHOLE_HOST}:${PIHOLE_DNS_PORT}"
EOF

    # Reload systemd and restart service
    systemctl daemon-reload
    systemctl restart mtproto-proxy || {
        log_error "FAILED"
        log_error "Failed to restart MTProto service"
        return 1
    }

    echo "OK"
}

# --- Funciones de Validación DNS ---
function validate_dns_configuration() {
    log_start_step "Validating DNS configuration"

    # Test Pi-hole DNS server
    if ! nslookup google.com "${PIHOLE_HOST}" >/dev/null 2>&1; then
        log_error "FAILED"
        log_error "Pi-hole DNS server is not responding"
        return 1
    fi

    # Test Outline DNS if configured
    if [ -n "${OUTLINE_CONTAINER_NAME}" ]; then
        if ! docker exec "${OUTLINE_CONTAINER_NAME}" nslookup google.com >/dev/null 2>&1; then
            log_error "WARNING"
            log_error "Outline container cannot resolve DNS"
        fi
    fi

    # Test MTProto DNS if configured
    if [ -n "${MTPROXY_SERVICE_FILE}" ] && systemctl is-active --quiet mtproto-proxy; then
        # MTProto uses system DNS, test if service can reach DNS
        if ! timeout 5 bash -c "echo > /dev/tcp/${PIHOLE_HOST}/${PIHOLE_DNS_PORT}" 2>/dev/null; then
            log_error "WARNING"
            log_error "MTProto cannot reach Pi-hole DNS server"
        fi
    fi

    echo "OK"
}

# --- Funciones de Reversión ---
function revert_dns_configuration() {
    log_start_step "Reverting DNS configuration"

    # Revert Outline DNS
    if [ -n "${OUTLINE_CONTAINER_NAME}" ] && docker ps --format '{{.Names}}' | grep -q "^${OUTLINE_CONTAINER_NAME}$"; then
        docker exec "${OUTLINE_CONTAINER_NAME}" sh -c "
            echo 'DNS1=1.1.1.1' > /tmp/dns_env
            echo 'DNS2=1.0.0.1' >> /tmp/dns_env
            echo 'DNSSEC=true' >> /tmp/dns_env
        " 2>/dev/null || true
        docker restart "${OUTLINE_CONTAINER_NAME}" 2>/dev/null || true
    fi

    # Revert WireGuard DNS
    if [ -d "${WIREGUARD_CONFIG_DIR}" ]; then
        sed -i "s/CLIENT_DNS_1=.*/CLIENT_DNS_1=1.1.1.1/" "${WIREGUARD_CONFIG_DIR}/params" 2>/dev/null || true

        local interface_name=""
        for conf_file in "${WIREGUARD_CONFIG_DIR}"/*.conf; do
            if [ -f "$conf_file" ]; then
                interface_name=$(basename "$conf_file" .conf)
                break
            fi
        done

        if [ -n "$interface_name" ]; then
            for client_conf in /home/*/"${interface_name}"-client-*.conf /root/"${interface_name}"-client-*.conf; do
                if [ -f "$client_conf" ]; then
                    sed -i "s/DNS = .*/DNS = 1.1.1.1,1.0.0.1/" "$client_conf" 2>/dev/null || true
                fi
            done
            wg syncconf "$interface_name" <(wg-quick strip "$interface_name") 2>/dev/null || true
        fi
    fi

    # Revert MTProto DNS
    if [ -f "${MTPROXY_SERVICE_FILE}" ]; then
        local drop_in_dir="/etc/systemd/system/mtproto-proxy.service.d"
        rm -f "${drop_in_dir}/dns.conf"
        rmdir "$drop_in_dir" 2>/dev/null || true
        systemctl daemon-reload
        systemctl restart mtproto-proxy 2>/dev/null || true
    fi

    echo "OK"
}

# --- Generación de Archivo de Configuración ---
function generate_dns_config_file() {
    log_start_step "Generating DNS configuration file"

    echo "# --- uSipipo DNS Configuration for VPN Services ---" > "${DNS_CONFIG_ENV_FILE}"
    echo "# Generated by configure-dns-vpn.sh v${SCRIPT_VERSION}" >> "${DNS_CONFIG_ENV_FILE}"
    echo "# This file documents the DNS configuration applied to VPN services" >> "${DNS_CONFIG_ENV_FILE}"
    echo "" >> "${DNS_CONFIG_ENV_FILE}"

    echo "# Pi-hole DNS Server Configuration" >> "${DNS_CONFIG_ENV_FILE}"
    echo "PIHOLE_DNS_HOST=\"${PIHOLE_HOST}\"" >> "${DNS_CONFIG_ENV_FILE}"
    echo "PIHOLE_DNS_PORT=\"${PIHOLE_DNS_PORT}\"" >> "${DNS_CONFIG_ENV_FILE}"
    echo "" >> "${DNS_CONFIG_ENV_FILE}"

    echo "# Configured Services" >> "${DNS_CONFIG_ENV_FILE}"
    if [ -n "${OUTLINE_CONTAINER_NAME}" ]; then
        echo "OUTLINE_DNS_CONFIGURED=true" >> "${DNS_CONFIG_ENV_FILE}"
    fi
    if [ -n "${WIREGUARD_CONFIG_DIR}" ]; then
        echo "WIREGUARD_DNS_CONFIGURED=true" >> "${DNS_CONFIG_ENV_FILE}"
    fi
    if [ -n "${MTPROXY_SERVICE_FILE}" ]; then
        echo "MTPROXY_DNS_CONFIGURED=true" >> "${DNS_CONFIG_ENV_FILE}"
    fi
    echo "" >> "${DNS_CONFIG_ENV_FILE}"

    echo "# Configuration applied on: $(date)" >> "${DNS_CONFIG_ENV_FILE}"

    echo "OK"
}

# --- Función Principal ---
function configure_dns() {
    run_step "Loading environment configurations" load_env_files
    run_step "Configuring Outline DNS" configure_outline_dns
    run_step "Configuring WireGuard DNS" configure_wireguard_dns
    run_step "Configuring MTProto DNS" configure_mtproto_dns
    run_step "Validating DNS configuration" validate_dns_configuration
    run_step "Generating configuration file" generate_dns_config_file

    echo -e "\n${GREEN}DNS configuration completed successfully!${NC}"
    echo -e "${GREEN}All VPN services are now configured to use Pi-hole as DNS server.${NC}"
    echo -e "${ORANGE}Configuration file: ${DNS_CONFIG_ENV_FILE}${NC}"
}

# --- Función de Ayuda ---
function display_usage() {
    cat <<EOF
Usage: $0 [options]

Configure VPN services to use Pi-hole as DNS server.

Options:
  --revert    Revert DNS configuration to default (use system DNS)
  --help      Display this help message

Requirements:
  - Pi-hole must be installed and configured (.env.pihole.generated exists)
  - VPN services must be installed with their respective .env files

Generated files:
  - .env.dns-config.generated  DNS configuration documentation

Examples:
  $0                    # Configure DNS for all installed VPN services
  $0 --revert           # Revert to default DNS configuration
  $0 --help             # Show this help message
EOF
}

# --- Función Principal del Script ---
function main() {
    # Set trap which publishes error tag only if there is an error.
    function finish {
        local EXIT_CODE=$?
        if (( EXIT_CODE != 0 )); then
            if [[ -s "${LAST_ERROR}" ]]; then
                log_error "\nLast error: $(< "${LAST_ERROR}")" >&2
            fi
            log_error "\nSorry! Something went wrong. Check the log: ${FULL_LOG}" >&2
        else
            rm "${FULL_LOG}"
        fi
        rm "${LAST_ERROR}"
    }
    trap finish EXIT

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --revert)
                REVERT_MODE=true
                shift
                ;;
            --help)
                display_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                display_usage
                exit 1
                ;;
        esac
    done

    initialCheck

    if [[ "${REVERT_MODE}" == "true" ]]; then
        echo -e "${ORANGE}Reverting DNS configuration to defaults...${NC}"
        revert_dns_configuration
        echo -e "\n${GREEN}DNS configuration reverted successfully!${NC}"
    else
        echo -e "${BLUE}Configuring VPN services to use Pi-hole DNS...${NC}"
        configure_dns
    fi
}

main "$@"