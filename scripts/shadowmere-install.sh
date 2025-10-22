#!/bin/bash

# Secure Shadowmere proxy detector installer for uSipipo
# Refactored to generate uSipipo .env variables and manage SOCKS5 proxy detection
# Based on: https://github.com/shadowmere-xyz/shadowmere

set -euo pipefail

# --- Constantes ---
SHADOWMERE_DIR="/opt/shadowmere"
SHADOWMERE_REPO="https://github.com/shadowmere-xyz/shadowmere.git"
SHADOWMERE_SERVICE_NAME="shadowmere"
SHADOWMERE_USER="shadowmere"
SHADOWMERE_GROUP="shadowmere"
DEFAULT_SHADOWMERE_HOST="localhost"
DEFAULT_SHADOWMERE_PORT_MIN=5000
DEFAULT_SHADOWMERE_PORT_MAX=6000
DEFAULT_SCAN_INTERVAL=3600  # 1 hora en segundos
DEFAULT_VALIDATION_INTERVAL=1800  # 30 minutos en segundos

# --- Variables globales ---
SHADOWMERE_HOST="${SHADOWMERE_HOST:-${DEFAULT_SHADOWMERE_HOST}}"
SHADOWMERE_PORT=0  # Se asignará aleatoriamente
SCAN_INTERVAL="${SCAN_INTERVAL:-${DEFAULT_SCAN_INTERVAL}}"
VALIDATION_INTERVAL="${VALIDATION_INTERVAL:-${DEFAULT_VALIDATION_INTERVAL}}"
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
FULL_LOG="$(mktemp -t shadowmere_install_logXXXXXXXXXX)"
LAST_ERROR="$(mktemp -t shadowmere_last_errorXXXXXXXXXX)"
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

function checkShadowmereInstalled() {
  if [ -d "${SHADOWMERE_DIR}" ]; then
    return 0
  else
    return 1
  fi
}

function checkShadowmereRunning() {
  if systemctl is-active --quiet "${SHADOWMERE_SERVICE_NAME}"; then
    return 0
  else
    return 1
  fi
}

function get_random_port() {
  local -i num=0
  until (( DEFAULT_SHADOWMERE_PORT_MIN <= num && num <= DEFAULT_SHADOWMERE_PORT_MAX )); do
    num=$(( RANDOM % (DEFAULT_SHADOWMERE_PORT_MAX - DEFAULT_SHADOWMERE_PORT_MIN + 1) + DEFAULT_SHADOWMERE_PORT_MIN ))
  done
  echo "${num}"
}

# --- Funciones de Instalación ---
function installDependencies() {
  run_step "Updating package lists" apt-get update
  
  run_step "Installing build essentials" apt-get install -y \
    build-essential \
    curl \
    git \
    python3 \
    python3-pip \
    python3-dev \
    libssl-dev \
    libffi-dev \
    wget
}

function createShadowmereUser() {
  log_start_step "Creating Shadowmere system user"
  
  if ! id "${SHADOWMERE_USER}" &>/dev/null; then
    useradd -r -s /bin/bash -d "${SHADOWMERE_DIR}" -m "${SHADOWMERE_USER}"
    echo "OK"
  else
    echo "OK (already exists)"
  fi
}

function cloneShadowmereRepository() {
  log_start_step "Cloning Shadowmere repository"
  
  if [ -d "${SHADOWMERE_DIR}" ]; then
    if [ "${REINSTALL}" = true ]; then
      rm -rf "${SHADOWMERE_DIR}"
      mkdir -p "${SHADOWMERE_DIR}"
    else
      echo "OK (already exists)"
      return 0
    fi
  else
    mkdir -p "${SHADOWMERE_DIR}"
  fi
  
  run_step "Cloning from GitHub" git clone "${SHADOWMERE_REPO}" "${SHADOWMERE_DIR}"
}

function installShadowmereDependencies() {
  log_start_step "Installing Shadowmere Python dependencies"
  
  if [ -f "${SHADOWMERE_DIR}/requirements.txt" ]; then
    run_step "Installing Python packages" pip3 install -r "${SHADOWMERE_DIR}/requirements.txt"
  else
    # Instalar dependencias comunes para Shadowmere
    run_step "Installing core Python packages" pip3 install \
      aiohttp \
      asyncio \
      pysocks \
      requests \
      pyyaml \
      python-dotenv
  fi
}

function configureShadowmere() {
  log_start_step "Generating Shadowmere configuration"
  
  # Generate random port for API
  SHADOWMERE_PORT=$(get_random_port)
  
  # Create configuration directory
  mkdir -p "${SHADOWMERE_DIR}/config"
  
  # Create main configuration file
  cat > "${SHADOWMERE_DIR}/config/shadowmere.yml" << EOF
# Shadowmere Configuration for uSipipo
# Auto-generated configuration file

# API Server Configuration
api:
  host: 0.0.0.0
  port: ${SHADOWMERE_PORT}
  debug: false

# Proxy Scanner Configuration
scanner:
  # Scan interval in seconds (default: 1 hour)
  interval: ${SCAN_INTERVAL}
  
  # Proxy validation interval in seconds (default: 30 minutes)
  validation_interval: ${VALIDATION_INTERVAL}
  
  # Maximum concurrent proxy checks
  max_concurrent: 50
  
  # Timeout for proxy connection tests (seconds)
  timeout: 10
  
  # Proxy types to scan
  proxy_types:
    - socks5
    - socks4
    - http
    - https

# Storage Configuration
storage:
  # Database type (sqlite, postgresql, mysql)
  type: sqlite
  
  # Database path for SQLite
  path: "${SHADOWMERE_DIR}/data/proxies.db"
  
  # Retention policy (days)
  retention_days: 30

# Logging Configuration
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "${SHADOWMERE_DIR}/logs/shadowmere.log"
  max_size: 10485760  # 10MB
  backup_count: 5

# Proxy Validation Rules
validation:
  # Minimum uptime percentage to keep proxy
  min_uptime: 70
  
  # Maximum response time (milliseconds)
  max_response_time: 5000
  
  # Test endpoints
  test_endpoints:
    - "http://httpbin.org/ip"
    - "http://api.ipify.org?format=json"

# Performance Settings
performance:
  # Enable caching
  cache_enabled: true
  cache_ttl: 300  # 5 minutes
  
  # Connection pool size
  pool_size: 100
EOF
  
  # Set proper permissions
  chown -R "${SHADOWMERE_USER}:${SHADOWMERE_GROUP}" "${SHADOWMERE_DIR}"
  chmod 755 "${SHADOWMERE_DIR}"
  chmod 644 "${SHADOWMERE_DIR}/config/shadowmere.yml"
  
  echo "OK"
}

function createShadowmereService() {
  log_start_step "Creating Shadowmere systemd service"
  
  cat > "/etc/systemd/system/${SHADOWMERE_SERVICE_NAME}.service" << EOF
[Unit]
Description=Shadowmere SOCKS5 Proxy Detector for uSipipo
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=${SHADOWMERE_USER}
Group=${SHADOWMERE_GROUP}
WorkingDirectory=${SHADOWMERE_DIR}
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONUNBUFFERED=1"

# Main process
ExecStart=/usr/bin/python3 ${SHADOWMERE_DIR}/main.py --config ${SHADOWMERE_DIR}/config/shadowmere.yml

# Restart policy
Restart=on-failure
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=${SHADOWMERE_DIR}

# Resource limits
LimitNOFILE=65536
LimitNPROC=512

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=shadowmere

[Install]
WantedBy=multi-user.target
EOF
  
  # Reload systemd daemon
  systemctl daemon-reload
  
  echo "OK"
}

function validateInstallation() {
  log_start_step "Validating Shadowmere installation"
  
  # Check if directory exists
  if [ ! -d "${SHADOWMERE_DIR}" ]; then
    log_error "FAILED"
    log_error "Shadowmere directory not found at ${SHADOWMERE_DIR}"
    return 1
  fi
  
  # Check if configuration file exists
  if [ ! -f "${SHADOWMERE_DIR}/config/shadowmere.yml" ]; then
    log_error "FAILED"
    log_error "Shadowmere configuration file not found"
    return 1
  fi
  
  # Check if service file exists
  if [ ! -f "/etc/systemd/system/${SHADOWMERE_SERVICE_NAME}.service" ]; then
    log_error "FAILED"
    log_error "Shadowmere systemd service file not found"
    return 1
  fi
  
  echo "OK"
}

function startShadowmereService() {
  log_start_step "Starting Shadowmere service"
  
  systemctl start "${SHADOWMERE_SERVICE_NAME}"
  
  # Wait for service to be ready
  local max_attempts=30
  local attempt=0
  
  while (( attempt < max_attempts )); do
    if systemctl is-active --quiet "${SHADOWMERE_SERVICE_NAME}"; then
      echo "OK"
      return 0
    fi
    sleep 1
    (( attempt++ ))
  done
  
  log_error "FAILED"
  log_error "Shadowmere service did not start in time"
  return 1
}

function enableShadowmereService() {
  run_step "Enabling Shadowmere service on boot" systemctl enable "${SHADOWMERE_SERVICE_NAME}"
}

# --- Funciones de Generación de .env ---
function generate_env_files() {
  # Archivo de configuración principal de Shadowmere para uSipipo
  ENV_FILE_SHADOWMERE=".env.shadowmere.generated"
  
  echo "# --- uSipipo Shadowmere Proxy Detector Configuration ---" > "${ENV_FILE_SHADOWMERE}"
  echo "SHADOWMERE_HOST=\"${SHADOWMERE_HOST}\"" >> "${ENV_FILE_SHADOWMERE}"
  echo "SHADOWMERE_PORT=\"${SHADOWMERE_PORT}\"" >> "${ENV_FILE_SHADOWMERE}"
  echo "SHADOWMERE_API_URL=\"http://${SHADOWMERE_HOST}:${SHADOWMERE_PORT}\"" >> "${ENV_FILE_SHADOWMERE}"
  echo "SHADOWMERE_SCAN_INTERVAL=\"${SCAN_INTERVAL}\"" >> "${ENV_FILE_SHADOWMERE}"
  echo "SHADOWMERE_VALIDATION_INTERVAL=\"${VALIDATION_INTERVAL}\"" >> "${ENV_FILE_SHADOWMERE}"
  echo "" >> "${ENV_FILE_SHADOWMERE}"
  echo "# Shadowmere service configuration" >> "${ENV_FILE_SHADOWMERE}"
  echo "SHADOWMERE_SERVICE_NAME=\"${SHADOWMERE_SERVICE_NAME}\"" >> "${ENV_FILE_SHADOWMERE}"
  echo "SHADOWMERE_DIR=\"${SHADOWMERE_DIR}\"" >> "${ENV_FILE_SHADOWMERE}"
  echo "SHADOWMERE_USER=\"${SHADOWMERE_USER}\"" >> "${ENV_FILE_SHADOWMERE}"
  echo "" >> "${ENV_FILE_SHADOWMERE}"
  
  echo -e "\n${GREEN}--- VARIABLES SHADOWMERE PARA TU .env DE USIPIPO ---${NC}"
  echo -e "${ORANGE}Archivo de configuración generado:${NC} ${ENV_FILE_SHADOWMERE}"
  echo -e "${GREEN}----------------------------------------------------------${NC}"
  echo -e "\n${GREEN}Contenido de ${ENV_FILE_SHADOWMERE}:${NC}"
  cat "${ENV_FILE_SHADOWMERE}"
  echo -e "\n${GREEN}----------------------------------------------------------${NC}"
  echo -e "${GREEN}¡Copia estas variables a tu archivo .env de uSipipo!${NC}"
  echo -e "${GREEN}----------------------------------------------------------${NC}\n"
}

# --- Funciones de Desinstalación ---
function uninstallShadowmere() {
  echo -e "${ORANGE}Uninstalling Shadowmere...${NC}"
  
  # Stop service
  if systemctl is-active --quiet "${SHADOWMERE_SERVICE_NAME}"; then
    run_step "Stopping Shadowmere service" systemctl stop "${SHADOWMERE_SERVICE_NAME}"
  fi
  
  # Disable service
  if systemctl is-enabled --quiet "${SHADOWMERE_SERVICE_NAME}"; then
    run_step "Disabling Shadowmere service" systemctl disable "${SHADOWMERE_SERVICE_NAME}"
  fi
  
  # Remove service file
  if [ -f "/etc/systemd/system/${SHADOWMERE_SERVICE_NAME}.service" ]; then
    run_step "Removing systemd service file" rm -f "/etc/systemd/system/${SHADOWMERE_SERVICE_NAME}.service"
    systemctl daemon-reload
  fi
  
  # Remove installation directory
  if [ -d "${SHADOWMERE_DIR}" ]; then
    run_step "Removing Shadowmere directory" rm -rf "${SHADOWMERE_DIR}"
  fi
  
  # Remove user
  if id "${SHADOWMERE_USER}" &>/dev/null; then
    run_step "Removing Shadowmere user" userdel -r "${SHADOWMERE_USER}"
  fi
  
  # Remove generated env file
  if [ -f ".env.shadowmere.generated" ]; then
    run_step "Removing generated .env file" rm -f ".env.shadowmere.generated"
  fi
  
  echo -e "${GREEN}Shadowmere has been successfully uninstalled${NC}"
}

# --- Funciones de Gestión de Servicio ---
function startService() {
  if checkShadowmereRunning; then
    echo -e "${ORANGE}Shadowmere service is already running${NC}"
    return 0
  fi
  
  echo -e "${ORANGE}Starting Shadowmere service...${NC}"
  systemctl start "${SHADOWMERE_SERVICE_NAME}"
  
  if systemctl is-active --quiet "${SHADOWMERE_SERVICE_NAME}"; then
    echo -e "${GREEN}Shadowmere service started successfully${NC}"
  else
    echo -e "${RED}Failed to start Shadowmere service${NC}"
    return 1
  fi
}

function stopService() {
  if ! checkShadowmereRunning; then
    echo -e "${ORANGE}Shadowmere service is not running${NC}"
    return 0
  fi
  
  echo -e "${ORANGE}Stopping Shadowmere service...${NC}"
  systemctl stop "${SHADOWMERE_SERVICE_NAME}"
  
  if ! systemctl is-active --quiet "${SHADOWMERE_SERVICE_NAME}"; then
    echo -e "${GREEN}Shadowmere service stopped successfully${NC}"
  else
    echo -e "${RED}Failed to stop Shadowmere service${NC}"
    return 1
  fi
}

function restartService() {
  echo -e "${ORANGE}Restarting Shadowmere service...${NC}"
  systemctl restart "${SHADOWMERE_SERVICE_NAME}"
  
  if systemctl is-active --quiet "${SHADOWMERE_SERVICE_NAME}"; then
    echo -e "${GREEN}Shadowmere service restarted successfully${NC}"
  else
    echo -e "${RED}Failed to restart Shadowmere service${NC}"
    return 1
  fi
}

function statusService() {
  echo -e "${ORANGE}Shadowmere Service Status:${NC}"
  systemctl status "${SHADOWMERE_SERVICE_NAME}" --no-pager
}

function viewLogs() {
  echo -e "${ORANGE}Shadowmere Service Logs (last 50 lines):${NC}"
  journalctl -u "${SHADOWMERE_SERVICE_NAME}" -n 50 --no-pager
}

# --- Función Principal ---
function main() {
  local action="${1:-install}"
  
  case "${action}" in
    install)
      echo -e "${GREEN}========================================${NC}"
      echo -e "${GREEN}Shadowmere Installation for uSipipo${NC}"
      echo -e "${GREEN}========================================${NC}\n"
      
      initialCheck
      
      if checkShadowmereInstalled; then
        echo -e "${ORANGE}Shadowmere is already installed${NC}"
        read -p "Do you want to reinstall? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
          REINSTALL=true
        else
          exit 0
        fi
      fi
      
      installDependencies
      createShadowmereUser
      cloneShadowmereRepository
      installShadowmereDependencies
      configureShadowmere
      createShadowmereService
      validateInstallation
      startShadowmereService
      enableShadowmereService
      generate_env_files
      
      echo -e "${GREEN}========================================${NC}"
      echo -e "${GREEN}Shadowmere installation completed!${NC}"
      echo -e "${GREEN}========================================${NC}"
      echo -e "${GREEN}Service: ${SHADOWMERE_SERVICE_NAME}${NC}"
      echo -e "${GREEN}Port: ${SHADOWMERE_PORT}${NC}"
      echo -e "${GREEN}API URL: http://${SHADOWMERE_HOST}:${SHADOWMERE_PORT}${NC}"
      echo -e "${GREEN}========================================${NC}\n"
      ;;
      
    uninstall)
      echo -e "${ORANGE}========================================${NC}"
      echo -e "${ORANGE}Shadowmere Uninstallation${NC}"
      echo -e "${ORANGE}========================================${NC}\n"
      
      initialCheck
      
      if ! checkShadowmereInstalled; then
        echo -e "${ORANGE}Shadowmere is not installed${NC}"
        exit 0
      fi
      
      read -p "Are you sure you want to uninstall Shadowmere? (y/n) " -n 1 -r
      echo
      if [[ $REPLY =~ ^[Yy]$ ]]; then
        uninstallShadowmere
      else
        echo -e "${ORANGE}Uninstallation cancelled${NC}"
        exit 0
      fi
      ;;
      
    start)
      initialCheck
      startService
      ;;
      
    stop)
      initialCheck
      stopService
      ;;
      
    restart)
      initialCheck
      restartService
      ;;
      
    status)
      initialCheck
      statusService
      ;;
      
    logs)
      initialCheck
      viewLogs
      ;;
      
    validate)
      echo -e "${GREEN}Validating Shadowmere installation...${NC}"
      initialCheck
      validateInstallation
      ;;
      
    *)
      echo "Usage: $0 {install|uninstall|start|stop|restart|status|logs|validate}"
      echo ""
      echo "Commands:"
      echo "  install    - Install Shadowmere"
      echo "  uninstall  - Uninstall Shadowmere"
      echo "  start      - Start Shadowmere service"
      echo "  stop       - Stop Shadowmere service"
      echo "  restart    - Restart Shadowmere service"
      echo "  status     - Show Shadowmere service status"
      echo "  logs       - View Shadowmere service logs"
      echo "  validate   - Validate Shadowmere installation"
      exit 1
      ;;
  esac
}

# Ejecutar función principal
main "$@"
