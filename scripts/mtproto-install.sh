#!/bin/bash

# MTProto Proxy Installer for uSipipo
# Enhanced with environment variable generation, secret extraction, and service management
# Based on LugoDev Medium article and uSipipo integration patterns

set -euo pipefail

# --- Constantes ---
MTPROXY_DIR_DEFAULT="/opt/mtproto-proxy"
MTPROXY_CONTAINER_NAME="mtproto-proxy"
MTPROXY_IMAGE="telegrammessenger/proxy:latest"
MTPROXY_HOST_DEFAULT=""  # Will be detected
MTPROXY_PORT_DEFAULT=""
MTPROXY_DATA_DIR="${MTPROXY_DIR_DEFAULT}/data"

# --- Colores para salida ---
GREEN='\033[0;32m'
ORANGE='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

# --- Variables Globales ---
MTPROXY_HOST=""
MTPROXY_PORT=""
MTPROXY_SECRET=""
MTPROXY_DIR=""

# --- Funciones de Validación ---
function isRoot() {
    if [ "${EUID}" -ne 0 ]; then
        echo -e "${RED}You need to run this script as root${NC}"
        exit 1
    fi
}

function get_current_user() {
    if [ -n "${SUDO_USER}" ]; then
        echo "${SUDO_USER}"
    else
        who am i | awk '{print $1}'
    fi
}

function command_exists() {
    command -v "$@" &> /dev/null
}

# --- Funciones de Logging ---
function log_error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

function log_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

function log_info() {
    echo -e "${ORANGE}[INFO] $1${NC}"
}

# --- Funciones de Docker ---
function verify_docker_installed() {
    if command_exists docker; then
        log_success "Docker is installed"
        return 0
    fi
    log_error "Docker not found. Please install Docker first."
    echo "Example for Ubuntu/Debian: sudo apt-get install docker.io"
    exit 1
}

function verify_docker_running() {
    if docker info &>/dev/null; then
        log_success "Docker daemon is running"
        return 0
    fi
    log_error "Docker daemon not running. Starting Docker..."
    if command -v systemctl &>/dev/null; then
        systemctl start docker
    elif command -v service &>/dev/null; then
        service docker start
    else
        dockerd &
        sleep 2
    fi

    if ! docker info &>/dev/null; then
        log_error "Failed to start Docker daemon"
        exit 1
    fi
}

function docker_container_exists() {
    docker ps -a --format '{{.Names}}' | grep -q "^$1$"
}

function remove_docker_container() {
    log_info "Removing Docker container: $1"
    docker rm -f "$1" &>/dev/null || true
}

# --- Funciones de Configuración ---
function detect_external_ip() {
    local urls=(
        'https://icanhazip.com/'
        'https://ipinfo.io/ip'
        'https://domains.google.com/checkip'
    )

    for url in "${urls[@]}"; do
        if command_exists curl; then
            MTPROXY_HOST=$(curl --silent --ipv4 "$url" 2>/dev/null)
            if [[ -n "${MTPROXY_HOST}" ]]; then
                log_success "Detected external IP: ${MTPROXY_HOST}"
                return 0
            fi
        fi
    done

    log_error "Failed to detect external IP address"
    echo "Please specify hostname manually with --hostname option"
    exit 1
}

function create_data_directory() {
    MTPROXY_DIR="${MTPROXY_DIR_DEFAULT}"
    mkdir -p "${MTPROXY_DATA_DIR}"

    # Set proper permissions
    chmod 755 "${MTPROXY_DIR}"
    chmod 755 "${MTPROXY_DATA_DIR}"

    # Change ownership to current user if running with sudo
    CURRENT_USER=$(get_current_user)
    if [ -n "${CURRENT_USER}" ]; then
        chown -R "${CURRENT_USER}:${CURRENT_USER}" "${MTPROXY_DIR}"
        log_success "Directory permissions set for user: ${CURRENT_USER}"
    fi
}

function start_mtproto_container() {
    log_info "Starting MTProto proxy container..."

    # Remove existing container if it exists
    if docker_container_exists "${MTPROXY_CONTAINER_NAME}"; then
        log_info "Removing existing container..."
        remove_docker_container "${MTPROXY_CONTAINER_NAME}"
    fi

    # Run the container
    docker run -d \
        --name "${MTPROXY_CONTAINER_NAME}" \
        --restart always \
        -p "${MTPROXY_PORT}:443" \
        -v "${MTPROXY_DATA_DIR}:/data" \
        "${MTPROXY_IMAGE}"

    if [ $? -eq 0 ]; then
        log_success "MTProto proxy container started"
    else
        log_error "Failed to start MTProto proxy container"
        exit 1
    fi
}

function wait_for_container() {
    log_info "Waiting for container to initialize..."
    local attempts=0
    local max_attempts=30

    while [ $attempts -lt $max_attempts ]; do
        if docker ps | grep -q "${MTPROXY_CONTAINER_NAME}"; then
            log_success "Container is running"
            return 0
        fi
        sleep 2
        ((attempts++))
    done

    log_error "Container failed to start within ${max_attempts} attempts"
    exit 1
}

function extract_secret_from_logs() {
    log_info "Extracting secret from container logs..."
    local attempts=0
    local max_attempts=30

    while [ $attempts -lt $max_attempts ]; do
        # Look for the secret in logs (MTProto proxy logs it on startup)
        MTPROXY_SECRET=$(docker logs "${MTPROXY_CONTAINER_NAME}" 2>&1 | grep -oE 'secret: [a-f0-9]+' | head -1 | cut -d' ' -f2)

        if [[ -n "${MTPROXY_SECRET}" ]]; then
            log_success "Secret extracted: ${MTPROXY_SECRET}"
            return 0
        fi

        sleep 2
        ((attempts++))
    done

    log_error "Failed to extract secret from logs within ${max_attempts} attempts"
    exit 1
}

function generate_env_file() {
    local env_file=".env.mtproto.generated"

    log_info "Generating environment file: ${env_file}"

    cat > "${env_file}" << EOF
# --- uSipipo MTProto Proxy Configuration ---
MTPROXY_HOST="${MTPROXY_HOST}"
MTPROXY_PORT="${MTPROXY_PORT}"
MTPROXY_SECRET="${MTPROXY_SECRET}"
MTPROXY_DIR="${MTPROXY_DIR}"
# MTPROXY_TAG=""  # Optional: Obtain from @MTProxybot after registering

# --- Service Information ---
# Container Name: ${MTPROXY_CONTAINER_NAME}
# Image: ${MTPROXY_IMAGE}
# Data Directory: ${MTPROXY_DATA_DIR}
EOF

    log_success "Environment file generated: ${env_file}"
    echo -e "\n${GREEN}--- MTProto Configuration ---${NC}"
    cat "${env_file}"
    echo -e "\n${ORANGE}Copy these variables to your .env file for uSipipo${NC}"
}

# --- Funciones de Gestión de Servicio ---
function start_service() {
    if docker_container_exists "${MTPROXY_CONTAINER_NAME}"; then
        if docker ps | grep -q "${MTPROXY_CONTAINER_NAME}"; then
            log_info "MTProto service is already running"
            return 0
        else
            log_info "Starting existing MTProto container..."
            docker start "${MTPROXY_CONTAINER_NAME}"
            log_success "MTProto service started"
            return 0
        fi
    fi

    log_error "MTProto service not installed. Run installation first."
    exit 1
}

function stop_service() {
    if docker_container_exists "${MTPROXY_CONTAINER_NAME}"; then
        log_info "Stopping MTProto service..."
        docker stop "${MTPROXY_CONTAINER_NAME}"
        log_success "MTProto service stopped"
    else
        log_info "MTProto service not found"
    fi
}

function restart_service() {
    stop_service
    sleep 2
    start_service
}

function status_service() {
    if docker_container_exists "${MTPROXY_CONTAINER_NAME}"; then
        if docker ps | grep -q "${MTPROXY_CONTAINER_NAME}"; then
            echo -e "${GREEN}MTProto service is RUNNING${NC}"
            echo "Container: ${MTPROXY_CONTAINER_NAME}"
            echo "Port: ${MTPROXY_PORT}"
            echo "Host: ${MTPROXY_HOST}"
            return 0
        else
            echo -e "${ORANGE}MTProto service is STOPPED${NC}"
            return 1
        fi
    else
        echo -e "${RED}MTProto service is NOT INSTALLED${NC}"
        return 1
    fi
}

function uninstall_service() {
    log_info "Uninstalling MTProto service..."

    # Stop and remove container
    if docker_container_exists "${MTPROXY_CONTAINER_NAME}"; then
        stop_service
        remove_docker_container "${MTPROXY_CONTAINER_NAME}"
    fi

    # Remove data directory
    if [ -d "${MTPROXY_DIR}" ]; then
        log_info "Removing data directory: ${MTPROXY_DIR}"
        rm -rf "${MTPROXY_DIR}"
    fi

    # Remove generated env file
    if [ -f ".env.mtproto.generated" ]; then
        rm -f ".env.mtproto.generated"
    fi

    log_success "MTProto service uninstalled"
}

# --- Función de Instalación ---
function install_mtproto() {
    log_info "Starting MTProto proxy installation for uSipipo..."

    # Verify prerequisites
    verify_docker_installed
    verify_docker_running

    # Set configuration
    if [[ -z "${MTPROXY_PORT}" ]]; then
        MTPROXY_PORT=$(shuf -i 1024-65535 -n 1)
        log_info "Generated random port: ${MTPROXY_PORT}"
    fi
    detect_external_ip

    # Create directories
    create_data_directory

    # Start container
    start_mtproto_container

    # Wait for initialization
    wait_for_container

    # Extract secret
    extract_secret_from_logs

    # Generate environment file
    generate_env_file

    log_success "MTProto proxy installation completed!"
    echo -e "\n${GREEN}Your MTProto proxy is ready for uSipipo integration.${NC}"
    echo -e "${ORANGE}Don't forget to copy the generated variables to your .env file.${NC}"
}

# --- Función de Ayuda ---
function display_usage() {
    cat << EOF
Usage: $0 [command] [options]

Commands:
    install     Install MTProto proxy (default if no command given)
    start       Start MTProto service
    stop        Stop MTProto service
    restart     Restart MTProto service
    status      Show MTProto service status
    uninstall   Completely remove MTProto proxy and all data

Options:
     --hostname  Override detected hostname/IP
     --port      Override default port (randomly generated)
     --help      Display this help message

Examples:
     $0 install                    # Install with auto-detected settings and random port
     $0 install --hostname 1.2.3.4 # Install with specific hostname
     $0 install --port 12345       # Install with specific port
     $0 status                     # Check service status
     $0 restart                    # Restart service

Environment Variables:
    MTPROXY_DIR    Installation directory (default: /opt/mtproto-proxy)
EOF
}

# --- Parseo de Argumentos ---
function parse_args() {
    COMMAND="install"

    while [[ $# -gt 0 ]]; do
        case $1 in
            install|start|stop|restart|status|uninstall)
                COMMAND="$1"
                shift
                ;;
            --hostname)
                MTPROXY_HOST="$2"
                shift 2
                ;;
            --port)
                MTPROXY_PORT="$2"
                shift 2
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
}

# --- Función Principal ---
function main() {
    # Parse arguments
    parse_args "$@"

    # Check if root (required for Docker operations)
    isRoot

    # Execute command
    case "${COMMAND}" in
        install)
            if docker_container_exists "${MTPROXY_CONTAINER_NAME}"; then
                log_error "MTProto proxy is already installed. Use 'uninstall' first if you want to reinstall."
                exit 1
            fi
            install_mtproto
            ;;
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            status_service
            ;;
        uninstall)
            uninstall_service
            ;;
        *)
            log_error "Unknown command: ${COMMAND}"
            display_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"