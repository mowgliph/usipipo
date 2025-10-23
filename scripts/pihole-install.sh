#!/bin/bash

# Secure Pi-hole server installer for uSipipo
# Refactored to generate uSipipo .env variables and manage DNS configuration
# Based on Pi-hole official installation and Docker best practices

set -euo pipefail

# --- Constantes ---
PIHOLE_DIR="/opt/pihole"
PIHOLE_CONTAINER_NAME="pihole"
PIHOLE_IMAGE_DEFAULT="pihole/pihole:latest"
PIHOLE_NETWORK_NAME="pihole-network"
PIHOLE_VOLUME_NAME="pihole-data"
PIHOLE_DNSMASQ_VOLUME_NAME="pihole-dnsmasq"
DEFAULT_PIHOLE_HOST="localhost"
DEFAULT_PIHOLE_DNS_PORT=53
DEFAULT_PIHOLE_PORT_MIN=8000
DEFAULT_PIHOLE_PORT_MAX=9000

# --- Variables globales ---
PIHOLE_HOST="${PIHOLE_HOST:-${DEFAULT_PIHOLE_HOST}}"
PIHOLE_PORT=0  # Se asignará aleatoriamente
PIHOLE_DNS_PORT="${PIHOLE_DNS_PORT:-${DEFAULT_PIHOLE_DNS_PORT}}"
PIHOLE_PASSWORD=""
PIHOLE_API_KEY=""
PIHOLE_IMAGE="${PIHOLE_IMAGE:-${PIHOLE_IMAGE_DEFAULT}}"
DOCKER_INSTALLED=false
REINSTALL=false

# --- Colores ---
RED='\033[0;31m'
ORANGE='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# --- Funciones de Logging ---
# I/O conventions for this script:
# - Ordinary status messages are printed to STDOUT
# - STDERR is only used in the event of a fatal error
# - Detailed logs are recorded to this FULL_LOG, which is preserved if an error occurred.
# - The most recent error is stored in LAST_ERROR, which is never preserved.
FULL_LOG="$(mktemp -t pihole_install_logXXXXXXXXXX)"
LAST_ERROR="$(mktemp -t pihole_last_errorXXXXXXXXXX)"
readonly FULL_LOG LAST_ERROR

function log_command() {
  # Direct STDOUT and STDERR to FULL_LOG, and forward STDOUT.
  # The most recent STDERR output will also be stored in LAST_ERROR.
  "$@" > >(tee -a "${FULL_LOG}") 2> >(tee -a "${FULL_LOG}" > "${LAST_ERROR}")
}

function log_error() {
  local -r ERROR_TEXT="${RED}"  # red
  local -r NO_COLOR="${NC}"
  echo -e "${ERROR_TEXT}$1${NO_COLOR}"
  echo "$1" >> "${FULL_LOG}"
}

# Pretty prints text to stdout, and also writes to sentry log file if set.
function log_start_step() {
  local -r str="> $*"
  local -ir lineLength=47
  echo -n "${str}"
  local -ir numDots=$(( lineLength - ${#str} - 1 ))
  if (( numDots > 0 )); then
    echo -n " "
    for _ in $(seq 1 "${numDots}"); do echo -n .; done
  fi
  echo -n " "
}

# Prints $1 as the step name and runs the remainder as a command.
# STDOUT will be forwarded.  STDERR will be logged silently,
# and revealed only in the event of a fatal error.
function run_step() {
  local -r msg="$1"
  log_start_step "${msg}"
  shift 1
  if log_command "$@"; then
    echo "OK"
  else
    # Propagates the error code
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
    OS=debian # overwrite if raspbian
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

function checkDockerInstalled() {
  if command -v docker &> /dev/null; then
    DOCKER_INSTALLED=true
    return 0
  else
    return 1
  fi
}

function checkPiholeInstalled() {
  if docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^${PIHOLE_CONTAINER_NAME}$"; then
    return 0
  else
    return 1
  fi
}

function get_random_port() {
  local -i num=0
  until (( DEFAULT_PIHOLE_PORT_MIN <= num && num <= DEFAULT_PIHOLE_PORT_MAX )); do
    num=$(( RANDOM % (DEFAULT_PIHOLE_PORT_MAX - DEFAULT_PIHOLE_PORT_MIN + 1) + DEFAULT_PIHOLE_PORT_MIN ))
  done
  echo "${num}"
}

function resolve_dns_conflict() {
  log_start_step "Checking for DNS port 53 conflict"

  # Improved detection using netstat and lsof
  local conflict_detected=false
  local process_using_port=""

  # Check with netstat
  if netstat -tlnp 2>/dev/null | grep -q ":53 "; then
    process_using_port=$(netstat -tlnp 2>/dev/null | grep ":53 " | awk '{print $7}' | cut -d'/' -f2 | head -1)
    if [[ "$process_using_port" == "systemd-resolved" ]]; then
      conflict_detected=true
      echo "OK (systemd-resolved detected on port 53)"
    else
      echo "OK (port 53 in use by: $process_using_port)"
    fi
  else
    echo "OK (no process using port 53)"
  fi

  # Additional check with lsof if netstat didn't find systemd-resolved
  if ! $conflict_detected && command -v lsof &> /dev/null; then
    if lsof -i :53 2>/dev/null | grep -q systemd-resolved; then
      conflict_detected=true
      echo "OK (systemd-resolved detected on port 53 via lsof)"
    fi
  fi

  if $conflict_detected; then
    run_step "Stopping systemd-resolved" systemctl stop systemd-resolved
    run_step "Disabling systemd-resolved" systemctl disable systemd-resolved

    # Verify systemd-resolved is stopped
    local max_attempts=10
    local attempt=0
    while (( attempt < max_attempts )); do
      if ! systemctl is-active --quiet systemd-resolved; then
        echo "systemd-resolved stopped successfully"
        break
      fi
      sleep 1
      (( attempt++ ))
    done
    if (( attempt >= max_attempts )); then
      log_error "Failed to stop systemd-resolved completely"
      return 1
    fi

    # Reconfigure /etc/resolv.conf
    run_step "Reconfiguring /etc/resolv.conf" bash -c "
      rm -f /etc/resolv.conf
      echo 'nameserver 1.1.1.1' > /etc/resolv.conf
      echo 'nameserver 8.8.8.8' >> /etc/resolv.conf
    "

    # Force restart Docker service
    run_step "Restarting Docker service" systemctl restart docker

    # Verify port 53 is free
    if netstat -tlnp 2>/dev/null | grep -q ":53 "; then
      log_error "Port 53 still in use after resolving conflict"
      return 1
    else
      echo "Port 53 is now free"
    fi
  else
    echo "No DNS conflict detected, skipping systemd-resolved actions"
  fi
}

# --- Funciones de Instalación ---
function installDocker() {
  run_step "Updating package lists" apt-get update
  
  run_step "Installing Docker dependencies" apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
  
  run_step "Adding Docker GPG key" curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  
  run_step "Adding Docker repository" echo \
    "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
  
  run_step "Updating package lists again" apt-get update
  
  run_step "Installing Docker" apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  
  run_step "Starting Docker service" systemctl start docker
  run_step "Enabling Docker service" systemctl enable docker
}

function createPiholeNetwork() {
  log_start_step "Creating Docker network for Pi-hole"
  
  if ! docker network ls --format '{{.Name}}' | grep -q "^${PIHOLE_NETWORK_NAME}$"; then
    docker network create "${PIHOLE_NETWORK_NAME}"
    echo "OK"
  else
    echo "OK (already exists)"
  fi
}

function createPiholeVolumes() {
  log_start_step "Creating Docker volumes for Pi-hole"
  
  if ! docker volume ls --format '{{.Name}}' | grep -q "^${PIHOLE_VOLUME_NAME}$"; then
    docker volume create "${PIHOLE_VOLUME_NAME}"
  fi
  
  if ! docker volume ls --format '{{.Name}}' | grep -q "^${PIHOLE_DNSMASQ_VOLUME_NAME}$"; then
    docker volume create "${PIHOLE_DNSMASQ_VOLUME_NAME}"
  fi
  
  echo "OK"
}

function installPihole() {
  log_start_step "Generating Pi-hole configuration"
  
  # Generate random port for web interface
  PIHOLE_PORT=$(get_random_port)
  
  # Generate random password
  PIHOLE_PASSWORD=$(openssl rand -base64 12)
  
  # Generate API key (32 character hex string)
  PIHOLE_API_KEY=$(openssl rand -hex 16)
  
  echo "OK"
  
  run_step "Pulling Pi-hole Docker image" docker pull "${PIHOLE_IMAGE}"
  
  run_step "Creating Pi-hole container" docker run -d \
    --name "${PIHOLE_CONTAINER_NAME}" \
    --network "${PIHOLE_NETWORK_NAME}" \
    -p "${PIHOLE_PORT}:80/tcp" \
    -p "${PIHOLE_DNS_PORT}:53/tcp" \
    -p "${PIHOLE_DNS_PORT}:53/udp" \
    -e WEBPASSWORD="${PIHOLE_PASSWORD}" \
    -e PIHOLE_UID=0 \
    -e PIHOLE_GID=0 \
    -e DNSMASQ_LISTENING=all \
    -e DNS1=1.1.1.1 \
    -e DNS2=1.0.0.1 \
    -e DNSSEC=true \
    -e CONDITIONAL_FORWARDING=false \
    -v "${PIHOLE_VOLUME_NAME}:/etc/pihole" \
    -v "${PIHOLE_DNSMASQ_VOLUME_NAME}:/etc/dnsmasq.d" \
    --restart unless-stopped \
    "${PIHOLE_IMAGE}"
}

function configurePihole() {
  log_start_step "Waiting for Pi-hole to be ready"
  
  # Wait for Pi-hole to be ready
  local max_attempts=30
  local attempt=0
  
  while (( attempt < max_attempts )); do
    if docker exec "${PIHOLE_CONTAINER_NAME}" curl -s http://localhost/admin/api.php > /dev/null 2>&1; then
      echo "OK"
      return 0
    fi
    sleep 2
    (( attempt++ ))
  done
  
  log_error "FAILED"
  log_error "Pi-hole did not become ready in time"
  return 1
}

function validateInstallation() {
  log_start_step "Validating Pi-hole installation"
  
  # Check if container is running
  if ! docker ps --format '{{.Names}}' | grep -q "^${PIHOLE_CONTAINER_NAME}$"; then
    log_error "FAILED"
    log_error "Pi-hole container is not running"
    return 1
  fi
  
  # Check if web interface is accessible
  if ! curl -s "http://localhost:${PIHOLE_PORT}/admin/" > /dev/null 2>&1; then
    log_error "FAILED"
    log_error "Pi-hole web interface is not accessible"
    return 1
  fi
  
  echo "OK"
}

# --- Funciones de Generación de .env ---
function generate_env_files() {
  # Archivo de configuración principal de Pi-hole para uSipipo
  ENV_FILE_PIHOLE=".env.pihole.generated"
  
  echo "# --- uSipipo Pi-hole DNS Configuration ---" > "${ENV_FILE_PIHOLE}"
  echo "PIHOLE_HOST=\"${PIHOLE_HOST}\"" >> "${ENV_FILE_PIHOLE}"
  echo "PIHOLE_PORT=\"${PIHOLE_PORT}\"" >> "${ENV_FILE_PIHOLE}"
  echo "PIHOLE_DNS_PORT=\"${PIHOLE_DNS_PORT}\"" >> "${ENV_FILE_PIHOLE}"
  echo "# PIHOLE_PASSWORD=\"${PIHOLE_PASSWORD}\"  # Keep this secret!" >> "${ENV_FILE_PIHOLE}"
  echo "# PIHOLE_API_KEY=\"${PIHOLE_API_KEY}\"  # Keep this secret!" >> "${ENV_FILE_PIHOLE}"
  echo "" >> "${ENV_FILE_PIHOLE}"
  echo "# Pi-hole Docker configuration" >> "${ENV_FILE_PIHOLE}"
  echo "PIHOLE_CONTAINER_NAME=\"${PIHOLE_CONTAINER_NAME}\"" >> "${ENV_FILE_PIHOLE}"
  echo "PIHOLE_NETWORK_NAME=\"${PIHOLE_NETWORK_NAME}\"" >> "${ENV_FILE_PIHOLE}"
  echo "PIHOLE_VOLUME_NAME=\"${PIHOLE_VOLUME_NAME}\"" >> "${ENV_FILE_PIHOLE}"
  echo "PIHOLE_DNSMASQ_VOLUME_NAME=\"${PIHOLE_DNSMASQ_VOLUME_NAME}\"" >> "${ENV_FILE_PIHOLE}"
  echo "" >> "${ENV_FILE_PIHOLE}"
  
  echo -e "\n${GREEN}--- VARIABLES PI-HOLE PARA TU .env DE USIPIPO ---${NC}"
  echo -e "${ORANGE}Archivo de configuración generado:${NC} ${ENV_FILE_PIHOLE}"
  echo -e "${GREEN}----------------------------------------------------------${NC}"
  echo -e "\n${GREEN}Contenido de ${ENV_FILE_PIHOLE}:${NC}"
  cat "${ENV_FILE_PIHOLE}"
  echo -e "\n${GREEN}----------------------------------------------------------${NC}"
  echo -e "${GREEN}¡Copia estas variables a tu archivo .env de uSipipo!${NC}"
  echo -e "${ORANGE}IMPORTANTE: Guarda las contraseñas de forma segura y no las compartas.${NC}"
  echo -e "${ORANGE}Web Password: ${PIHOLE_PASSWORD}${NC}"
  echo -e "${ORANGE}API Key: ${PIHOLE_API_KEY}${NC}"
}

# --- Función Principal de Instalación ---
function installPiholeFull() {
  if checkPiholeInstalled; then
    log_error "Pi-hole is already installed. Use --reinstall if you want to reinstall."
    exit 1
  fi

  if ! checkDockerInstalled; then
    run_step "Installing Docker" installDocker
  fi

  run_step "Resolving DNS port conflict" resolve_dns_conflict

  run_step "Creating Pi-hole network" createPiholeNetwork
  run_step "Creating Pi-hole volumes" createPiholeVolumes
  run_step "Installing Pi-hole container" installPihole
  run_step "Configuring Pi-hole" configurePihole
  run_step "Validating installation" validateInstallation

  # Generar archivos .env al finalizar
  generate_env_files

  echo -e "\n${GREEN}CONGRATULATIONS! Pi-hole is installed and configured for uSipipo.${NC}"
  echo -e "${GREEN}Web Interface: http://${PIHOLE_HOST}:${PIHOLE_PORT}/admin${NC}"
  echo -e "${GREEN}DNS Port: ${PIHOLE_DNS_PORT}${NC}"
  echo -e "${ORANGE}Remember to copy the generated environment variables to your .env file.${NC}"
}

# --- Función de Desinstalación ---
function uninstallPihole() {
  echo -e "${ORANGE}WARNING: This will remove the Pi-hole installation!${NC}"
  echo -n "Are you sure you want to continue? [y/N] "
  read -r response
  response=$(echo "${response}" | tr '[:upper:]' '[:lower:]')
  if [[ "${response}" != "y" && "${response}" != "yes" ]]; then
    echo "Uninstallation cancelled."
    exit 0
  fi
  
  run_step "Stopping Pi-hole container" docker stop "${PIHOLE_CONTAINER_NAME}" || true
  run_step "Removing Pi-hole container" docker rm "${PIHOLE_CONTAINER_NAME}" || true
  run_step "Removing Pi-hole volumes" docker volume rm "${PIHOLE_VOLUME_NAME}" "${PIHOLE_DNSMASQ_VOLUME_NAME}" || true
  run_step "Removing Pi-hole network" docker network rm "${PIHOLE_NETWORK_NAME}" || true
  
  echo -e "\n${GREEN}Pi-hole has been uninstalled.${NC}"
}

# --- Función de Reinstalación ---
function reinstallPihole() {
  echo -e "${ORANGE}WARNING: This will remove the existing Pi-hole installation!${NC}"
  echo -n "Are you sure you want to continue? [y/N] "
  read -r response
  response=$(echo "${response}" | tr '[:upper:]' '[:lower:]')
  if [[ "${response}" != "y" && "${response}" != "yes" ]]; then
    echo "Reinstallation cancelled."
    exit 0
  fi
  
  uninstallPihole
  installPiholeFull
}

# --- Función de Ayuda ---
function display_usage() {
  cat <<EOF
Usage: $0 [options]

Options:
  --reinstall    Remove existing Pi-hole installation and reinstall
  --uninstall    Remove Pi-hole installation
  --help         Display this help message

Environment variables:
  PIHOLE_HOST    Pi-hole host (default: localhost)
  PIHOLE_DNS_PORT DNS port (default: 53)
EOF
}

# --- Función Principal ---
function main() {
  # Set trap which publishes error tag only if there is an error.
  function finish {
    local -ir EXIT_CODE=$?
    if (( EXIT_CODE != 0 )); then
      if [[ -s "${LAST_ERROR}" ]]; then
        log_error "\nLast error: $(< "${LAST_ERROR}")" >&2
      fi
      log_error "\nSorry! Something went wrong. If you can't figure this out, please copy and paste all this output into the uSipipo issue tracker." >&2
      log_error "Full log: ${FULL_LOG}" >&2
    else
      rm "${FULL_LOG}"
    fi
    rm "${LAST_ERROR}"
  }
  trap finish EXIT
  
  # Parse arguments
  while [[ $# -gt 0 ]]; do
    case $1 in
      --reinstall)
        REINSTALL=true
        shift
        ;;
      --uninstall)
        uninstallPihole
        exit 0
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
  
  if [[ "${REINSTALL:-false}" == "true" ]]; then
    reinstallPihole
  else
    installPiholeFull
  fi
}

main "$@"
