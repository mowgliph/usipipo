#!/bin/bash

# Secure MariaDB server installer for uSipipo
# Refactored to generate uSipipo .env variables and manage database setup
# Based on MariaDB official installation and security best practices

set -euo pipefail

# --- Constantes ---
MARIADB_CONFIG_DIR="/etc/mysql"
MARIADB_DATA_DIR="/var/lib/mysql"
MARIADB_LOG_DIR="/var/log/mysql"
MARIADB_RUN_DIR="/var/run/mysqld"
DEFAULT_DB_NAME="usipipo"
DEFAULT_DB_USER="usipipo"
DEFAULT_DB_HOST="localhost"
DEFAULT_DB_PORT=3306

# --- Variables globales ---
DB_NAME="${DB_NAME:-${DEFAULT_DB_NAME}}"
DB_USER="${DB_USER:-${DEFAULT_DB_USER}}"
DB_HOST="${DB_HOST:-${DEFAULT_DB_HOST}}"
DB_PORT="${DB_PORT:-${DEFAULT_DB_PORT}}"
DB_ROOT_PASS=""
DB_USER_PASS=""

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
FULL_LOG="$(mktemp -t mariadb_install_logXXXXXXXXXX)"
LAST_ERROR="$(mktemp -t mariadb_last_errorXXXXXXXXXX)"
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

function checkDiskSpace() {
  local REQUIRED_SPACE=500  # MB
  local AVAILABLE_SPACE=$(df / | tail -1 | awk '{print $4}')
  AVAILABLE_SPACE=$((AVAILABLE_SPACE / 1024))  # Convert to MB
  if [ "${AVAILABLE_SPACE}" -lt "${REQUIRED_SPACE}" ]; then
    log_error "Insufficient disk space. Required: ${REQUIRED_SPACE}MB, Available: ${AVAILABLE_SPACE}MB"
    exit 1
  fi
}

function checkDependencies() {
  local deps=("software-properties-common" "curl" "wget" "gnupg2")
  for dep in "${deps[@]}"; do
    if ! dpkg -l | grep -q "^ii  ${dep}"; then
      log_start_step "Installing dependency: ${dep}"
      apt-get install -y "${dep}" || {
        log_error "Failed to install dependency: ${dep}"
        return 1
      }
      echo "OK"
    fi
  done
}

function fixBrokenPackages() {
  log_start_step "Fixing broken packages"
  dpkg --configure -a || {
    log_error "Failed to configure broken packages"
    return 1
  }
  echo "OK"
}

function updatePackageLists() {
  log_start_step "Updating package lists"
  if ! apt-get update; then
    log_error "apt-get update failed. Attempting to fix repository issues..."
    # Try to update keys
    apt-key adv --recv-keys --keyserver keyserver.ubuntu.com || true
    apt-get update --allow-unauthenticated || {
      log_error "Failed to update package lists after key update attempt"
      return 1
    }
  fi
  echo "OK"
}

function initialCheck() {
  isRoot
  checkOS
  checkDiskSpace
}

function checkMariaDBInstalled() {
  if command -v mariadb &> /dev/null || command -v mysql &> /dev/null; then
    return 0
  else
    return 1
  fi
}

function checkMariaDBRunning() {
  if systemctl is-active --quiet mariadb; then
    return 0
  else
    return 1
  fi
}

# --- Funciones de Instalación ---
function installMariaDB() {
  fixBrokenPackages
  checkDependencies
  updatePackageLists

  run_step "Installing MariaDB server and client" apt-get install -y mariadb-server mariadb-client

  run_step "Starting MariaDB service" systemctl start mariadb
  run_step "Enabling MariaDB service" systemctl enable mariadb
}

function secureMariaDB() {
  log_start_step "Securing MariaDB installation"

  # Generate random root password
  DB_ROOT_PASS=$(openssl rand -base64 12)

  # Create temporary SQL file for securing MariaDB
  local SECURE_SQL="/tmp/mariadb_secure.sql"
  cat > "${SECURE_SQL}" << EOF
-- Set root password
ALTER USER 'root'@'localhost' IDENTIFIED BY '${DB_ROOT_PASS}';

-- Remove anonymous users
DELETE FROM mysql.user WHERE User='';

-- Disallow root login remotely
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');

-- Remove test database
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';

-- Reload privilege tables
FLUSH PRIVILEGES;
EOF

  # Execute the secure installation
  mariadb < "${SECURE_SQL}"

  # Clean up
  rm -f "${SECURE_SQL}"

  echo "OK"
}

function createDatabaseAndUser() {
  log_start_step "Creating database and user"

  # Generate random user password
  DB_USER_PASS=$(openssl rand -base64 12)

  # Create database and user
  local CREATE_SQL="/tmp/mariadb_create.sql"
  cat > "${CREATE_SQL}" << EOF
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'${DB_HOST}' IDENTIFIED BY '${DB_USER_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'${DB_HOST}';
FLUSH PRIVILEGES;
EOF

  # Execute as root
  mariadb -u root -p"${DB_ROOT_PASS}" < "${CREATE_SQL}"

  # Clean up
  rm -f "${CREATE_SQL}"

  echo "OK"
}

function validateInstallation() {
  log_start_step "Validating MariaDB installation"

  # Test connection with new user
  if mariadb -h "${DB_HOST}" -P "${DB_PORT}" -u "${DB_USER}" -p"${DB_USER_PASS}" "${DB_NAME}" -e "SELECT 1;" > /dev/null 2>&1; then
    log_info "Database connection test successful"
    echo "OK"
  else
    log_error "FAILED"
    log_error "Could not connect to MariaDB with the created user"
    log_error "Please check the database credentials and service status"
    return 1
  fi

  # Additional validations
  log_start_step "Checking MariaDB service status"
  if systemctl is-active --quiet mariadb; then
    log_info "MariaDB service is running"
    echo "OK"
  else
    log_error "FAILED"
    log_error "MariaDB service is not running"
    return 1
  fi

  log_start_step "Checking database permissions"
  if mariadb -u "${DB_USER}" -p"${DB_USER_PASS}" "${DB_NAME}" -e "CREATE TABLE test_permissions (id INT PRIMARY KEY); DROP TABLE test_permissions;" > /dev/null 2>&1; then
    log_info "Database user has proper permissions"
    echo "OK"
  else
    log_error "FAILED"
    log_error "Database user does not have proper permissions"
    return 1
  fi
}

# --- Funciones de Generación de .env ---
function generate_env_files() {
  # Archivo de configuración principal de MariaDB para uSipipo
  ENV_FILE_MARIADB=".env.mariadb.generated"

  # Construir URLs
  DB_URL_SYNC="mysql+pymysql://${DB_USER}:${DB_USER_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
  DB_URL_ASYNC="mysql+asyncmy://${DB_USER}:${DB_USER_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

  echo "# --- uSipipo MariaDB Database Configuration ---" > "${ENV_FILE_MARIADB}"
  echo "DATABASE_URL=\"${DB_URL_SYNC}\"" >> "${ENV_FILE_MARIADB}"
  echo "DATABASE_ASYNC_URL=\"${DB_URL_ASYNC}\"" >> "${ENV_FILE_MARIADB}"
  echo "DATABASE_SYNC_URL=\"${DB_URL_SYNC}\"" >> "${ENV_FILE_MARIADB}"
  echo "DB_HOST=\"${DB_HOST}\"" >> "${ENV_FILE_MARIADB}"
  echo "DB_PORT=\"${DB_PORT}\"" >> "${ENV_FILE_MARIADB}"
  echo "DB_NAME=\"${DB_NAME}\"" >> "${ENV_FILE_MARIADB}"
  echo "DB_USER=\"${DB_USER}\"" >> "${ENV_FILE_MARIADB}"
  echo "# DB_USER_PASS=\"${DB_USER_PASS}\"  # Keep this secret!" >> "${ENV_FILE_MARIADB}"
  echo "# DB_ROOT_PASS=\"${DB_ROOT_PASS}\"  # Keep this secret!" >> "${ENV_FILE_MARIADB}"
  echo "" >> "${ENV_FILE_MARIADB}"
  echo "# Additional database settings" >> "${ENV_FILE_MARIADB}"
  echo "DB_POOL_PRE_PING=true" >> "${ENV_FILE_MARIADB}"
  echo "DB_ECHO_SQL=false" >> "${ENV_FILE_MARIADB}"
  echo "DB_MAX_OVERFLOW=10" >> "${ENV_FILE_MARIADB}"
  echo "DB_POOL_SIZE=5" >> "${ENV_FILE_MARIADB}"
  echo "DB_POOL_TIMEOUT=30" >> "${ENV_FILE_MARIADB}"
  echo "DB_CHARSET=utf8mb4" >> "${ENV_FILE_MARIADB}"
  echo "" >> "${ENV_FILE_MARIADB}"

  echo -e "\n${GREEN}--- VARIABLES MARIADB PARA TU .env DE USIPIPO ---${NC}"
  echo -e "${ORANGE}Archivo de configuración generado:${NC} ${ENV_FILE_MARIADB}"
  echo -e "${GREEN}----------------------------------------------------------${NC}"
  echo -e "\n${GREEN}Contenido de ${ENV_FILE_MARIADB}:${NC}"
  cat "${ENV_FILE_MARIADB}"
  echo -e "\n${GREEN}----------------------------------------------------------${NC}"
  echo -e "${GREEN}¡Copia estas variables a tu archivo .env de uSipipo!${NC}"
  echo -e "${ORANGE}IMPORTANTE: Guarda las contraseñas de forma segura y no las compartas.${NC}"
  echo -e "${ORANGE}Root password: ${DB_ROOT_PASS}${NC}"
  echo -e "${ORANGE}User password: ${DB_USER_PASS}${NC}"
}

# --- Función Principal de Instalación ---
function installMariaDBFull() {
  log_info "Starting MariaDB installation process..."

  run_step "Installing MariaDB server" installMariaDB
  run_step "Securing MariaDB installation" secureMariaDB
  run_step "Creating database and user" createDatabaseAndUser
  run_step "Validating installation" validateInstallation

  # Generar archivos .env al finalizar
  generate_env_files

  log_info "MariaDB installation completed successfully"
  echo -e "\n${GREEN}CONGRATULATIONS! MariaDB is installed and configured for uSipipo.${NC}"
  echo -e "${GREEN}Database: ${DB_NAME}${NC}"
  echo -e "${GREEN}User: ${DB_USER}@${DB_HOST}:${DB_PORT}${NC}"
  echo -e "${ORANGE}Remember to copy the generated environment variables to your .env file.${NC}"
}

# --- Función de Desinstalación Completa ---
function uninstallMariaDB() {
  echo -e "${RED}WARNING: This will completely remove MariaDB and ALL its data!${NC}"
  echo -e "${RED}This action cannot be undone. Make sure to backup your data first.${NC}"
  echo -n "Are you sure you want to continue? [y/N] "
  read -r response
  response=$(echo "${response}" | tr '[:upper:]' '[:lower:]')
  if [[ "${response}" != "y" && "${response}" != "yes" ]]; then
    echo "Uninstallation cancelled."
    exit 0
  fi

  if checkMariaDBRunning; then
    run_step "Stopping MariaDB service" systemctl stop mariadb
    run_step "Disabling MariaDB service" systemctl disable mariadb
  fi

  run_step "Removing MariaDB packages" apt-get remove -y --purge mariadb-server mariadb-client mariadb-common

  # Limpieza profunda
  run_step "Removing MariaDB data directories" rm -rf "${MARIADB_DATA_DIR}" "${MARIADB_LOG_DIR}" "${MARIADB_RUN_DIR}" "${MARIADB_CONFIG_DIR}"
  run_step "Removing any remaining MariaDB files" find / -name "*mariadb*" -type f -delete 2>/dev/null || true
  run_step "Removing MariaDB user and group" userdel mysql 2>/dev/null || true
  run_step "Removing MariaDB group" groupdel mysql 2>/dev/null || true

  # Limpieza de paquetes
  run_step "Autoremoving unused packages" apt-get autoremove -y
  run_step "Autocleaning package cache" apt-get autoclean -y
  run_step "Cleaning package cache" apt-get clean -y

  echo -e "\n${GREEN}MariaDB has been completely uninstalled and cleaned.${NC}"
}

# --- Función de Reinstalación ---
function reinstallMariaDB() {
  if checkMariaDBInstalled; then
    echo -e "${ORANGE}MariaDB is currently installed. Proceeding with removal first...${NC}"
    uninstallMariaDB
  fi

  installMariaDBFull
}

# --- Función de Ayuda ---
function display_usage() {
  cat <<EOF
Usage: $0 [options]

Options:
  --install      Install MariaDB (default action if no MariaDB is installed)
  --uninstall    Completely remove MariaDB and all its data
  --reinstall    Remove existing MariaDB installation and reinstall
  --help         Display this help message

Environment variables:
  DB_NAME        Database name (default: usipipo)
  DB_USER        Database user (default: usipipo)
  DB_HOST        Database host (default: localhost)
  DB_PORT        Database port (default: 3306)
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
    "install")
      if checkMariaDBInstalled; then
        log_error "MariaDB is already installed. Use --reinstall if you want to reinstall."
        exit 1
      fi
      installMariaDBFull
      ;;
    "uninstall")
      if ! checkMariaDBInstalled; then
        log_error "MariaDB is not installed."
        exit 1
      fi
      uninstallMariaDB
      ;;
    "reinstall")
      reinstallMariaDB
      ;;
    "auto")
      if checkMariaDBInstalled; then
        log_error "MariaDB is already installed. Use --reinstall to reinstall or --uninstall to remove."
        exit 1
      else
        installMariaDBFull
      fi
      ;;
  esac
}

main "$@"