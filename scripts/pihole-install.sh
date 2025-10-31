#!/bin/bash

# Secure Pi-hole server installer for uSipipo
# Refactored to be a fully integrated version with uSipipo system
# Based on Pi-hole official Docker installation (v6 compatible)
# Includes uninstall functionality adapted from pihole-uninstall.sh
# Compatible with official Pi-hole Docker image: https://github.com/pi-hole/docker-pi-hole

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
# Nuevas constantes para compatibilidad con Pi-hole v6
DEFAULT_TIMEZONE="UTC"
DEFAULT_UPSTREAM_DNS="8.8.8.8;8.8.4.4"

# --- Variables globales ---
PIHOLE_HOST="${PIHOLE_HOST:-${DEFAULT_PIHOLE_HOST}}"
PIHOLE_PORT=0  # Se asignará aleatoriamente
PIHOLE_DNS_PORT="${PIHOLE_DNS_PORT:-${DEFAULT_PIHOLE_DNS_PORT}}"
PIHOLE_PASSWORD=""
PIHOLE_API_KEY=""
PIHOLE_IMAGE="${PIHOLE_IMAGE:-${PIHOLE_IMAGE_DEFAULT}}"
PIHOLE_TIMEZONE="${PIHOLE_TIMEZONE:-${DEFAULT_TIMEZONE}}"
PIHOLE_UPSTREAM_DNS="${PIHOLE_UPSTREAM_DNS:-${DEFAULT_UPSTREAM_DNS}}"
DOCKER_INSTALLED=false
REINSTALL=false
UNINSTALL=false
HELP=false

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
  echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: $1" >> "${FULL_LOG}"
}

function log_info() {
  echo "$1"
  echo "$(date '+%Y-%m-%d %H:%M:%S') INFO: $1" >> "${FULL_LOG}"
}

function log_warn() {
  local -r WARN_TEXT="${ORANGE}"
  local -r NO_COLOR="${NC}"
  echo -e "${WARN_TEXT}$1${NO_COLOR}"
  echo "$(date '+%Y-%m-%d %H:%M:%S') WARN: $1" >> "${FULL_LOG}"
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

  local conflict_detected=false
  local systemd_resolved_conflict=false
  local other_processes=()
  local docker_containers=()

  # Function to log detailed port usage
  function log_port_usage() {
    local tool="$1"
    local output="$2"
    echo "Port 53 usage detected by $tool:"
    echo "$output"
    echo "---"
  }

  # Check with ss (modern replacement for netstat)
  if command -v ss &> /dev/null; then
    local ss_output
    ss_output=$(ss -tlnp 2>/dev/null | grep ":53 " || true)
    if [[ -n "$ss_output" ]]; then
      log_port_usage "ss" "$ss_output"
      local process
      process=$(echo "$ss_output" | awk '{print $6}' | sed 's/.*pid=\([0-9]*\).*/\1/' | head -1)
      if [[ -n "$process" ]]; then
        local proc_name
        proc_name=$(ps -p "$process" -o comm= 2>/dev/null || echo "unknown")
        if [[ "$proc_name" == "systemd-resolve" ]]; then
          systemd_resolved_conflict=true
        else
          other_processes+=("$proc_name (PID: $process)")
        fi
      fi
    fi
  fi

  # Check with netstat (fallback)
  if command -v netstat &> /dev/null; then
    local netstat_output
    netstat_output=$(netstat -tlnp 2>/dev/null | grep ":53 " || true)
    if [[ -n "$netstat_output" ]]; then
      log_port_usage "netstat" "$netstat_output"
      local process
      process=$(echo "$netstat_output" | awk '{print $7}' | cut -d'/' -f1 | head -1)
      if [[ -n "$process" ]]; then
        local proc_name
        proc_name=$(ps -p "$process" -o comm= 2>/dev/null || echo "unknown")
        if [[ "$proc_name" == "systemd-resolve" ]]; then
          systemd_resolved_conflict=true
        else
          other_processes+=("$proc_name (PID: $process)")
        fi
      fi
    fi
  fi

  # Check with lsof
  if command -v lsof &> /dev/null; then
    local lsof_output
    lsof_output=$(lsof -i :53 2>/dev/null || true)
    if [[ -n "$lsof_output" ]]; then
      log_port_usage "lsof" "$lsof_output"
      while IFS= read -r line; do
        local proc_name
        proc_name=$(echo "$line" | awk '{print $1}')
        local pid
        pid=$(echo "$line" | awk '{print $2}')
        if [[ "$proc_name" == "systemd-resolve" ]]; then
          systemd_resolved_conflict=true
        else
          other_processes+=("$proc_name (PID: $pid)")
        fi
      done <<< "$lsof_output"
    fi
  fi

  # Check Docker containers
  if command -v docker &> /dev/null; then
    local docker_output
    docker_output=$(docker ps --format "table {{.Names}}\t{{.Ports}}" 2>/dev/null | grep ":53" || true)
    if [[ -n "$docker_output" ]]; then
      log_port_usage "docker ps" "$docker_output"
      while IFS= read -r line; do
        local container_name
        container_name=$(echo "$line" | awk '{print $1}')
        docker_containers+=("$container_name")
      done <<< "$docker_output"
    fi
  fi

  # Determine conflict status
  if $systemd_resolved_conflict; then
    conflict_detected=true
    echo "OK (systemd-resolved detected on port 53)"
  elif [[ ${#other_processes[@]} -gt 0 ]]; then
    conflict_detected=true
    echo "WARNING: Port 53 in use by other processes: ${other_processes[*]}"
  elif [[ ${#docker_containers[@]} -gt 0 ]]; then
    conflict_detected=true
    echo "WARNING: Port 53 in use by Docker containers: ${docker_containers[*]}"
  else
    echo "OK (no process using port 53)"
  fi

  if $conflict_detected; then
    if $systemd_resolved_conflict; then
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
      if ss -tlnp 2>/dev/null | grep -q ":53 " || netstat -tlnp 2>/dev/null | grep -q ":53 "; then
        log_error "Port 53 still in use after resolving conflict"
        return 1
      else
        echo "Port 53 is now free"
      fi
    else
      log_error "Port 53 is in use by other processes or Docker containers. Please stop them manually before installing Pi-hole."
      log_error "Processes: ${other_processes[*]}"
      log_error "Docker containers: ${docker_containers[*]}"
      return 1
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
    -e TZ="${PIHOLE_TIMEZONE}" \
    -e FTLCONF_webserver_api_password="${PIHOLE_PASSWORD}" \
    -e FTLCONF_dns_upstreams="${PIHOLE_UPSTREAM_DNS}" \
    -e FTLCONF_dns_listeningMode=all \
    -e FTLCONF_dns_dnssec=true \
    -e FTLCONF_dns_conditional_forwarding=false \
    -e PIHOLE_UID=0 \
    -e PIHOLE_GID=0 \
    --cap-add NET_ADMIN \
    --cap-add SYS_TIME \
    --cap-add SYS_NICE \
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

# --- Función de Desinstalación Completa (Adaptada para Docker) ---
function uninstallPihole() {
  echo -e "${RED}WARNING: This will completely remove the Pi-hole Docker installation!${NC}"
  echo -e "${RED}This action cannot be undone. All Pi-hole data and configurations will be lost.${NC}"
  echo -n "Are you sure you want to continue? [y/N] "
  read -r response
  response=$(echo "${response}" | tr '[:upper:]' '[:lower:]')
  if [[ "${response}" != "y" && "${response}" != "yes" ]]; then
    echo "Uninstallation cancelled."
    exit 0
  fi

  # Stop and remove Pi-hole container
  if checkPiholeInstalled; then
    run_step "Stopping Pi-hole container" docker stop "${PIHOLE_CONTAINER_NAME}" || true
    run_step "Removing Pi-hole container" docker rm "${PIHOLE_CONTAINER_NAME}" || true
  fi

  # Remove Pi-hole volumes
  run_step "Removing Pi-hole volumes" docker volume rm "${PIHOLE_VOLUME_NAME}" "${PIHOLE_DNSMASQ_VOLUME_NAME}" || true

  # Remove Pi-hole network
  run_step "Removing Pi-hole network" docker network rm "${PIHOLE_NETWORK_NAME}" || true

  # Remove generated .env files
  run_step "Removing generated .env files" rm -f .env.pihole.generated || true

  # Clean up Docker system (optional but recommended)
  run_step "Cleaning up Docker system" docker system prune -f || true

  echo -e "\n${GREEN}Pi-hole has been completely uninstalled from Docker.${NC}"
  echo -e "${ORANGE}Note: Docker itself remains installed. Use 'apt-get remove docker-ce' to remove Docker if needed.${NC}"
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

# --- Función de Status ---
function showPiholeStatus() {
  echo -e "\n${GREEN}==============================================${NC}"
  echo -e "${GREEN}    PI-HOLE STATUS - uSipipo Integration     ${NC}"
  echo -e "${GREEN}==============================================${NC}\n"
  
  local container_running=false
  local web_interface_ok=false
  local dns_service_ok=false
  local api_accessible=false
  
  # Check 1: Docker Container Status
  echo -e "${ORANGE}🔍 Checking Docker Container Status...${NC}"
  if checkPiholeInstalled; then
    local container_status
    container_status=$(docker inspect "${PIHOLE_CONTAINER_NAME}" --format='{{.State.Status}}' 2>/dev/null || echo "unknown")
    
    if [[ "$container_status" == "running" ]]; then
      container_running=true
      echo -e "   ${GREEN}✅ Container Status:${NC} RUNNING"
      
      # Get additional container info
      local uptime
      uptime=$(docker inspect "${PIHOLE_CONTAINER_NAME}" --format='{{.State.StartedAt}}' 2>/dev/null || echo "unknown")
      if [[ "$uptime" != "unknown" ]]; then
        # Convert to human readable uptime
        local start_time
        start_time=$(date -d "$uptime" '+%s' 2>/dev/null || echo "0")
        local current_time
        current_time=$(date '+%s')
        local diff_seconds
        diff_seconds=$((current_time - start_time))
        local uptime_hours
        uptime_hours=$((diff_seconds / 3600))
        echo -e "   ${GREEN}⏰ Uptime:${NC} ${uptime_hours}h"
      fi
      
      # Get container ports
      local ports
      ports=$(docker port "${PIHOLE_CONTAINER_NAME}" 2>/dev/null || echo "none")
      if [[ "$ports" != "none" ]]; then
        echo -e "   ${GREEN}🔌 Ports:${NC}"
        while IFS= read -r port_line; do
          echo -e "      ${GREEN}${port_line}${NC}"
        done <<< "$ports"
      fi
      
      # Get resource usage
      local cpu_usage
      cpu_usage=$(docker stats "${PIHOLE_CONTAINER_NAME}" --no-stream --format "{{.CPUPerc}}" 2>/dev/null || echo "N/A")
      local mem_usage
      mem_usage=$(docker stats "${PIHOLE_CONTAINER_NAME}" --no-stream --format "{{.MemUsage}}" 2>/dev/null || echo "N/A")
      echo -e "   ${GREEN}📊 CPU Usage:${NC} ${cpu_usage}"
      echo -e "   ${GREEN}💾 Memory Usage:${NC} ${mem_usage}"
      
    else
      echo -e "   ${RED}❌ Container Status:${NC} $container_status"
    fi
  else
    echo -e "   ${RED}❌ Container Status:${NC} NOT INSTALLED"
  fi
  
  echo
  
  # Check 2: Web Interface Status
  if $container_running; then
    echo -e "${ORANGE}🌐 Checking Web Interface Status...${NC}"
    
    # Try to get the actual port from container
    local web_port
    web_port=$(docker port "${PIHOLE_CONTAINER_NAME}" 80/tcp 2>/dev/null | cut -d':' -f2 || echo "")
    if [[ -z "$web_port" ]]; then
      web_port="8080"  # fallback
    fi
    
    # Check web interface accessibility
    local web_response
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:${web_port}/admin/" >/tmp/pihole_web_status 2>/dev/null; then
      local http_code
      http_code=$(cat /tmp/pihole_web_status)
      if [[ "$http_code" == "200" ]]; then
        web_interface_ok=true
        echo -e "   ${GREEN}✅ Web Interface:${NC} ACCESSIBLE (HTTP $http_code)"
        echo -e "   ${GREEN}🔗 URL:${NC} http://${PIHOLE_HOST}:${web_port}/admin/"
      else
        echo -e "   ${ORANGE}⚠️  Web Interface:${NC} HTTP $http_code"
      fi
    else
      echo -e "   ${RED}❌ Web Interface:${NC} NOT ACCESSIBLE"
    fi
    rm -f /tmp/pihole_web_status
    
    # Check DNS Service
    echo -e "\n${ORANGE}🔍 Checking DNS Service Status...${NC}"
    
    local dns_port
    dns_port=$(docker port "${PIHOLE_CONTAINER_NAME}" 53/tcp 2>/dev/null | cut -d':' -f2 || echo "53")
    
    # Check if DNS port is listening
    if command -v ss >/dev/null 2>&1; then
      if ss -tln | grep -q ":${dns_port} "; then
        dns_service_ok=true
        echo -e "   ${GREEN}✅ DNS Service:${NC} LISTENING on port ${dns_port}"
      else
        echo -e "   ${RED}❌ DNS Service:${NC} NOT LISTENING on port ${dns_port}"
      fi
    elif command -v netstat >/dev/null 2>&1; then
      if netstat -tln | grep -q ":${dns_port} "; then
        dns_service_ok=true
        echo -e "   ${GREEN}✅ DNS Service:${NC} LISTENING on port ${dns_port}"
      else
        echo -e "   ${RED}❌ DNS Service:${NC} NOT LISTENING on port ${dns_port}"
      fi
    else
      echo -e "   ${ORANGE}⚠️  DNS Service:${NC} Cannot verify (no ss/netstat available)"
    fi
    
    # Check Pi-hole API
    echo -e "\n${ORANGE}🔌 Checking Pi-hole API Status...${NC}"
    
    local api_response
    if curl -s "http://localhost:${web_port}/admin/api.php" >/dev/null 2>&1; then
      api_accessible=true
      echo -e "   ${GREEN}✅ Pi-hole API:${NC} ACCESSIBLE"
      
      # Get some API statistics if available
      local api_stats
      api_stats=$(curl -s "http://localhost:${web_port}/admin/api.php?summary" 2>/dev/null || echo "")
      if [[ -n "$api_stats" ]]; then
        echo -e "   ${GREEN}📊 API Data Available:${NC} Yes"
        # Extract some basic stats (non-sensitive)
        local domains_blocked
        domains_blocked=$(echo "$api_stats" | grep -o '"domains_being_blocked":[0-9]*' | cut -d':' -f2 || echo "N/A")
        if [[ "$domains_blocked" != "N/A" ]]; then
          echo -e "   ${GREEN}🚫 Domains Blocked:${NC} $domains_blocked"
        fi
      fi
    else
      echo -e "   ${RED}❌ Pi-hole API:${NC} NOT ACCESSIBLE"
    fi
  fi
  
  echo
  
  # Check 3: Network Configuration
  echo -e "${ORANGE}🌐 Checking Network Configuration...${NC}"
  
  # Check Pi-hole network
  if docker network ls --format '{{.Name}}' | grep -q "^${PIHOLE_NETWORK_NAME}$"; then
    echo -e "   ${GREEN}✅ Docker Network:${NC} ${PIHOLE_NETWORK_NAME} (EXISTS)"
  else
    echo -e "   ${RED}❌ Docker Network:${NC} ${PIHOLE_NETWORK_NAME} (MISSING)"
  fi
  
  # Check volumes
  if docker volume ls --format '{{.Name}}' | grep -q "^${PIHOLE_VOLUME_NAME}$"; then
    echo -e "   ${GREEN}✅ Data Volume:${NC} ${PIHOLE_VOLUME_NAME} (EXISTS)"
  else
    echo -e "   ${RED}❌ Data Volume:${NC} ${PIHOLE_VOLUME_NAME} (MISSING)"
  fi
  
  if docker volume ls --format '{{.Name}}' | grep -q "^${PIHOLE_DNSMASQ_VOLUME_NAME}$"; then
    echo -e "   ${GREEN}✅ DNSMASQ Volume:${NC} ${PIHOLE_DNSMASQ_VOLUME_NAME} (EXISTS)"
  else
    echo -e "   ${RED}❌ DNSMASQ Volume:${NC} ${PIHOLE_DNSMASQ_VOLUME_NAME} (MISSING)"
  fi
  
  echo
  
  # Check 4: Configuration Files
  echo -e "${ORANGE}📁 Checking Configuration Files...${NC}"
  
  if [[ -f ".env.pihole.generated" ]]; then
    echo -e "   ${GREEN}✅ Generated Config:${NC} .env.pihole.generated (EXISTS)"
  else
    echo -e "   ${ORANGE}⚠️  Generated Config:${NC} .env.pihole.generated (NOT FOUND)"
  fi
  
  # Check for custom .env variables
  if grep -q "PIHOLE" .env 2>/dev/null; then
    echo -e "   ${GREEN}✅ Environment Variables:${NC} PIHOLE config found in .env"
  else
    echo -e "   ${ORANGE}⚠️  Environment Variables:${NC} No PIHOLE config in .env"
  fi
  
  echo
  
  # Overall Status Summary
  echo -e "${GREEN}==============================================${NC}"
  echo -e "${GREEN}           STATUS SUMMARY                     ${NC}"
  echo -e "${GREEN}==============================================${NC}"
  
  if $container_running && $web_interface_ok && $dns_service_ok && $api_accessible; then
    echo -e "${GREEN}🎉 OVERALL STATUS: HEALTHY & OPERATIONAL${NC}"
    echo -e "${GREEN}✅ All systems are running correctly${NC}"
  elif $container_running; then
    echo -e "${ORANGE}⚠️  OVERALL STATUS: PARTIALLY OPERATIONAL${NC}"
    echo -e "${ORANGE}Container is running but some services need attention${NC}"
  else
    echo -e "${RED}❌ OVERALL STATUS: NOT OPERATIONAL${NC}"
    echo -e "${RED}Pi-hole is not running properly${NC}"
  fi
  
  echo -e "\n${GREEN}📝 Additional Information:${NC}"
  echo -e "   🐳 Docker Image: ${PIHOLE_IMAGE}"
  echo -e "   🏠 Host: ${PIHOLE_HOST}"
  echo -e "   🔌 Web Port: ${web_port:-N/A}"
  echo -e "   🌐 DNS Port: ${dns_port:-N/A}"
  echo -e "   🕐 Check Time: $(date '+%Y-%m-%d %H:%M:%S UTC')"
  
  # Performance tips
  if $container_running; then
    echo -e "\n${ORANGE}💡 Performance Tips:${NC}"
    local mem_usage_num
    mem_usage_num=$(echo "$mem_usage" | grep -o '[0-9.]*' | head -1 || echo "0")
    if [[ $(echo "$mem_usage_num > 100" | bc -l 2>/dev/null || echo "0") == "1" ]]; then
      echo -e "   ${ORANGE}⚠️  Memory usage seems high (>100MB)${NC}"
    fi
    
    local cpu_usage_num
    cpu_usage_num=$(echo "$cpu_usage" | sed 's/%//' 2>/dev/null || echo "0")
    if [[ $cpu_usage_num -gt 80 ]]; then
      echo -e "   ${ORANGE}⚠️  CPU usage is high (>80%)${NC}"
    fi
  fi
  
  echo
}

# --- Función de Ayuda ---
function display_usage() {
  cat <<EOF
Usage: $0 [options]

Pi-hole Docker Installer for uSipipo - Fully integrated DNS server setup

Options:
   --status       Show detailed Pi-hole status and health check
   --install      Install Pi-hole (default action if no Pi-hole is installed)
   --uninstall    Completely remove Pi-hole Docker installation and all data
   --reinstall    Remove existing Pi-hole installation and reinstall
   --help         Display this help message

Environment variables:
   PIHOLE_HOST           Pi-hole host (default: localhost)
   PIHOLE_DNS_PORT       DNS port (default: 53)
   PIHOLE_IMAGE          Docker image to use (default: pihole/pihole:latest)
   PIHOLE_TIMEZONE       Timezone for Pi-hole (default: UTC)
   PIHOLE_UPSTREAM_DNS   Upstream DNS servers (default: 8.8.8.8;8.8.4.4)

Examples:
   $0                           # Install Pi-hole if not installed
   $0 --install                 # Explicitly install Pi-hole
   $0 --uninstall               # Remove Pi-hole completely
   $0 --reinstall               # Reinstall Pi-hole
   PIHOLE_HOST=pi.hole $0       # Install with custom host
   PIHOLE_TIMEZONE=America/New_York $0  # Install with custom timezone

This script installs Pi-hole as a Docker container with full uSipipo integration,
including automatic .env file generation for easy configuration management.
Compatible with Pi-hole v6 Docker official image.

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
  ACTION="auto"  # auto: install if not installed, error if installed
  while [[ $# -gt 0 ]]; do
    case $1 in
      --status)
        ACTION="status"
        shift
        ;;
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

  case "${ACTION}" in
    "status")
      showPiholeStatus
      ;;
    "install")
      if checkPiholeInstalled; then
        log_error "Pi-hole is already installed. Use --reinstall to reinstall or --uninstall to remove."
        exit 1
      fi
      installPiholeFull
      ;;
    "uninstall")
      if ! checkPiholeInstalled; then
        log_error "Pi-hole is not installed."
        exit 1
      fi
      uninstallPihole
      ;;
    "reinstall")
      reinstallPihole
      ;;
    "auto")
      if checkPiholeInstalled; then
        log_error "Pi-hole is already installed. Use --reinstall to reinstall or --uninstall to remove."
        exit 1
      else
        installPiholeFull
      fi
      ;;
  esac
}

main "$@"
