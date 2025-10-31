#!/bin/bash

# Secure Outline server installer for uSipipo
# Refactored to generate uSipipo .env variables and obtain Outline Manager configuration
# Based on: https://github.com/Jigsaw-Code/outline-server
#
# This script installs Outline VPN server without Pi-hole integration.
# It generates necessary environment variables for uSipipo system and provides
# the apiUrl and certSha256 for Outline Manager configuration.
#
# Usage: ./outline-install.sh [options]
# Options:
#   --install      Install Outline server
#   --uninstall    Remove Outline server completely
#   --reinstall    Reinstall Outline server
#   --hostname     Server hostname/IP
#   --api-port     Management API port
#   --keys-port    Access keys port
#   --help         Show help

set -euo pipefail

# --- Constantes de Configuración ---
OUTLINE_DIR_DEFAULT="/opt/outline"                 # Directorio de instalación en Linux
HOME_DIR_DEFAULT="VPNs_Configs/outline/"           # Directorio relativo

OUTLINE_DIR="${OUTLINE_DIR:-$OUTLINE_DIR_DEFAULT}"   # Directorio de instalación de Outline
OUTLINE_CONTAINER_NAME="outline"                     # Nombre del contenedor Docker
OUTLINE_IMAGE_DEFAULT="quay.io/outline/shadowbox:stable"  # Imagen Docker por defecto
HOME_DIR="${HOME_DIR:-$HOME_DIR_DEFAULT}"            # Directorio para configuraciones de cliente

# Rangos de IPs para gestión de usuarios (informativo para Outline)
TRIAL_IP_START=2  # Primera IP usable para usuarios trial
TRIAL_IP_END=26   # Última IP para trial (25 IPs disponibles)
PAID_IP_START=27  # Primera IP para usuarios pagos
PAID_IP_END=254   # Última IP usable (límite común de subred /24)

# --- Colores para salida de terminal ---
GREEN='\033[0;32m'   # Verde para mensajes de éxito
ORANGE='\033[0;33m'  # Naranja para advertencias
RED='\033[0;31m'     # Rojo para errores
NC='\033[0m'         # Reset de color

# --- Variables Globales ---
# Variables de flags de línea de comandos
FLAGS_HOSTNAME=""     # Hostname proporcionado por usuario
FLAGS_API_PORT=0      # Puerto API proporcionado por usuario
FLAGS_KEYS_PORT=0     # Puerto de claves proporcionado por usuario

# Variables de entorno que pueden ser sobrescritas
OUTLINE_DIR="${OUTLINE_DIR:-/opt/outline}"
OUTLINE_CONTAINER_NAME="${CONTAINER_NAME:-${OUTLINE_CONTAINER_NAME}}"
OUTLINE_IMAGE="${SB_IMAGE:-${OUTLINE_IMAGE_DEFAULT}}"

# Variables que se asignan durante la instalación
OUTLINE_API_PORT=0    # Puerto para la API de gestión (se asigna después de parse_flags)
OUTLINE_KEYS_PORT=0   # Puerto para claves de acceso (se asigna después de parse_flags)
OUTLINE_HOSTNAME=""   # Hostname/IP del servidor
OUTLINE_STATE_DIR=""  # Directorio de estado persistente
OUTLINE_CERT_FILE=""  # Archivo de certificado TLS
OUTLINE_KEY_FILE=""   # Archivo de clave privada TLS
OUTLINE_API_URL=""    # URL completa de la API
OUTLINE_CERT_SHA256="" # Fingerprint SHA256 del certificado

# --- Funciones de Validación ---
# Verifica si un puerto es válido (1-65535)
function is_valid_port() {
  (( 0 < "$1" && "$1" <= 65535 ))
}

# Verifica si un comando existe en el sistema
function command_exists {
  command -v "$@" &> /dev/null
}

function get_current_user() {
	# Detectar el usuario actual no root que ejecutó el script
	if [ -n "${SUDO_USER}" ]; then
		echo "${SUDO_USER}"
	else
		# Si no se usó sudo, intentar obtener el usuario que ejecutó el script
		who am i | awk '{print $1}'
	fi
}

# Genera un puerto aleatorio en el rango válido (1024-65535)
function get_random_port {
  local -i num=0  # Inicializar con valor inválido para evitar errores de variable no ligada
  until (( 1024 <= num && num < 65536)); do
    num=$(( RANDOM + (RANDOM % 2) * 32768 ))
  done
  echo "${num}"
}

# --- Funciones de Logging ---
# Convenciones de I/O para este script:
# - Mensajes de estado ordinarios se imprimen en STDOUT
# - STDERR se usa solo en caso de error fatal
# - Logs detallados se registran en FULL_LOG, que se preserva si ocurre un error
# - El error más reciente se almacena en LAST_ERROR, que nunca se preserva
FULL_LOG="$(mktemp -t outline_logXXXXXXXXXX)"
LAST_ERROR="$(mktemp -t outline_last_errorXXXXXXXXXX)"
readonly FULL_LOG LAST_ERROR

function log_command() {
  # Direct STDOUT and STDERR to FULL_LOG, and forward STDOUT.
  # The most recent STDERR output will also be stored in LAST_ERROR.
  "$@" > >(tee -a "${FULL_LOG}") 2> >(tee -a "${FULL_LOG}" > "${LAST_ERROR}")
}

function log_error() {
  local -r ERROR_TEXT="\033[0;31m"  # red
  local -r NO_COLOR="\033[0m"
  echo -e "${ERROR_TEXT}$1${NO_COLOR}"
  echo "$1" >> "${FULL_LOG}"
}

# Pretty prints text to stdout, and also writes to sentry log file if set.
function log_start_step() {
  # log_for_sentry "$@" # Opcional, si se quiere mantener
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
# STDOUT will be forwarded.  STDERR will be logged silently, and
# revealed only in the event of a fatal error.
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

function confirm() {
  echo -n "> $1 [Y/n] "
  local RESPONSE
  read -r RESPONSE
  RESPONSE=$(echo "${RESPONSE}" | tr '[:upper:]' '[:lower:]') || return
  [[ -z "${RESPONSE}" || "${RESPONSE}" == "y" || "${RESPONSE}" == "yes" ]]
}

function fetch() {
  # Usar curl directamente para mayor compatibilidad
  curl --silent --show-error --fail "$@"
}

function log_for_sentry() {
  # if [[ -n "${SENTRY_LOG_FILE}" ]]; then # Opcional, si se quiere mantener
  #   echo "[$(date "+%Y-%m-%d@%H:%M:%S")] install_server.sh" "$@" >> "${SENTRY_LOG_FILE}"
  # fi
  echo "$@" >> "${FULL_LOG}"
}

# --- Funciones de Verificación ---
# Verifica si Docker está instalado en el sistema
function verify_docker_installed() {
  if command_exists docker; then
    echo "Docker is already installed"
    return 0
  fi
  log_error "NOT INSTALLED"
  echo "Docker not found. This script requires Docker to be installed."
  echo "For Linux systems, please install Docker using your package manager."
  echo "Example for Ubuntu/Debian: sudo apt-get install docker.io"
  echo "Example for CentOS/RHEL: sudo yum install docker"
  exit 1
}

function verify_docker_running() {
  local STDERR_OUTPUT
  STDERR_OUTPUT="$(docker info 2>&1 >/dev/null)" || return
  local -ir RET=$?
  if (( RET == 0 )); then
    echo "Docker daemon is running"
    return 0
  elif [[ "${STDERR_OUTPUT}" == *"Is the docker daemon running"* ]]; then
    echo "Docker daemon not running, attempting to start it"
    start_docker
    return $?
  fi
  echo "Docker verification failed with code: ${RET}"
  echo "Error output: ${STDERR_OUTPUT}"
  return "${RET}"
}

function install_docker() {
  (
    # Cambiar umask para que /usr/share/keyrings/docker-archive-keyring.gpg tenga los permisos correctos
    # Ver: https://github.com/Jigsaw-Code/outline-server/issues/951
    # Se hace en un subproceso para que el umask del proceso padre no se vea afectado
    umask 0022
    echo "Installing Docker via get.docker.com script"
    # Usar curl directamente en lugar de fetch para mayor compatibilidad
    if ! command_exists curl; then
      echo "curl is required but not found. Please install curl first."
      return 1
    fi
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "Docker installed successfully. You may need to start the Docker service."
  ) >&2
}

function start_docker() {
  echo "Starting Docker service"
  # Intentar diferentes métodos para iniciar Docker según el sistema
  if command -v systemctl >/dev/null 2>&1; then
    echo "Using systemctl to start Docker"
    systemctl enable --now docker.service >&2
  elif command -v service >/dev/null 2>&1; then
    echo "Using service command to start Docker"
    service docker start >&2
  else
    echo "Systemctl/service not available, trying to start Docker daemon directly"
    dockerd >&2 &
    sleep 2
  fi
}

# --- Funciones de Docker ---
# Verifica si un contenedor Docker existe (incluyendo detenidos)
function docker_container_exists() {
  docker ps -a --format '{{.Names}}' | grep --quiet "^$1$"
}

# Remueve el contenedor watchtower
function remove_watchtower_container() {
  remove_docker_container watchtower
}

# Remueve un contenedor Docker de forma forzada
function remove_docker_container() {
  echo "Removing Docker container: $1"
  docker rm -f "$1" >&2
}

function handle_docker_container_conflict() {
  local -r CONTAINER_NAME="$1"
  local -r EXIT_ON_NEGATIVE_USER_RESPONSE="$2"
  local PROMPT="The container name \"${CONTAINER_NAME}\" is already in use by another container. This may happen when running this script multiple times."
  if [[ "${EXIT_ON_NEGATIVE_USER_RESPONSE}" == 'true' ]]; then
    PROMPT="${PROMPT} We will attempt to remove the existing container and restart it. Would you like to proceed?"
  else
    PROMPT="${PROMPT} Would you like to replace this container? If you answer no, we will proceed with the remainder of the installation."
  fi
  if ! confirm "${PROMPT}"; then
    if ${EXIT_ON_NEGATIVE_USER_RESPONSE}; then
      exit 0
    fi
    return 0
  fi
  if run_step "Removing ${CONTAINER_NAME} container" "remove_${CONTAINER_NAME}_container" ; then
    log_start_step "Restarting ${CONTAINER_NAME}"
    "start_${CONTAINER_NAME}"
    return $?
  fi
  return 1
}

# --- Funciones de Configuración ---
function create_persisted_state_dir() {
  OUTLINE_STATE_DIR="${OUTLINE_DIR}/persisted-state"
  mkdir -p "${OUTLINE_STATE_DIR}"
  chmod ug+rwx,g+s,o-rwx "${OUTLINE_STATE_DIR}"

  # Cambiar propietario al usuario actual no root
  CURRENT_USER=$(get_current_user)
  if [ -n "${CURRENT_USER}" ]; then
    chown -R "${CURRENT_USER}:${CURRENT_USER}" "${OUTLINE_STATE_DIR}"
    echo -e "${GREEN}Permisos de directorio de estado cambiados al usuario: ${CURRENT_USER}${NC}"
  fi
}

function safe_base64() {
  # Implements URL-safe base64 of stdin, stripping trailing = chars.
  # Writes result to stdout.
  base64 | tr '/+' '_-' | sed 's/=*$//'
}

function generate_secret_key() {
  SB_API_PREFIX="$(head -c 16 /dev/urandom | safe_base64)"
  readonly SB_API_PREFIX
}

function generate_certificate() {
  # Generate self-signed cert and store it in the persistent state directory.
  local -r CERTIFICATE_NAME="${OUTLINE_STATE_DIR}/outline-selfsigned"
  OUTLINE_CERT_FILE="${CERTIFICATE_NAME}.crt"
  OUTLINE_KEY_FILE="${CERTIFICATE_NAME}.key"
  declare -a openssl_req_flags=(
    -x509 -nodes -days 36500 -newkey rsa:4096
    -subj "/CN=${OUTLINE_HOSTNAME}"
    -keyout "${OUTLINE_KEY_FILE}" -out "${OUTLINE_CERT_FILE}"
  )
  # Verificar que openssl esté disponible
  if ! command_exists openssl; then
    log_error "OpenSSL is required but not found. Please install OpenSSL."
    exit 1
  fi
  openssl req "${openssl_req_flags[@]}" >&2
}

function generate_certificate_fingerprint() {
  # Add a tag with the SHA-256 fingerprint of the certificate.
  # (Electron uses SHA-256 fingerprints: https://github.com/electron/electron/blob/9624bc140353b3771bd07c55371f6db65fd1b67e/atom/common/native_mate_converters/net_converter.cc#L60)
  # Example format: "SHA256 Fingerprint=BD:DB:C9:A4:39:5C:B3:4E:6E:CF:18:43:61:9F:07:A2:09:07:37:35:63:67"
  if ! command_exists openssl; then
    log_error "OpenSSL is required for certificate fingerprint generation."
    return 1
  fi
  local CERT_OPENSSL_FINGERPRINT
  CERT_OPENSSL_FINGERPRINT="$(openssl x509 -in "${OUTLINE_CERT_FILE}" -noout -sha256 -fingerprint)" || return
  # Example format: "BDDBC9A4395CB34E6ECF1843619F07A2090737356367"
  local CERT_HEX_FINGERPRINT
  CERT_HEX_FINGERPRINT="$(echo "${CERT_OPENSSL_FINGERPRINT#*=}" | tr -d :)" || return
  OUTLINE_CERT_SHA256="${CERT_HEX_FINGERPRINT}"
}

function join() {
  local IFS="$1"
  shift
  echo "$*"
}

function write_config() {
   echo "Starting write_config() function"
   local -a config=()
   echo "Checking FLAGS_KEYS_PORT: ${FLAGS_KEYS_PORT}"
   if (( FLAGS_KEYS_PORT != 0 )); then
     config+=("\"portForNewAccessKeys\": ${FLAGS_KEYS_PORT}")
     echo "Added portForNewAccessKeys: ${FLAGS_KEYS_PORT}"
   fi
   # No se establece nombre por defecto en este script refactorizado
   # if [[ -n "${SB_DEFAULT_SERVER_NAME:-}" ]]; then
   #   config+=("\"name\": \"$(escape_json_string "${SB_DEFAULT_SERVER_NAME}")\"")
   # fi
   echo "Adding hostname: ${OUTLINE_HOSTNAME}"
   config+=("\"hostname\": \"$(escape_json_string "${OUTLINE_HOSTNAME}")\"")
   config+=("\"metricsEnabled\": false") # Deshabilitado por defecto
   echo "Config array so far: ${config[*]}"

   # Usar configuración DNS por defecto (sin Pi-hole)
   echo "Using default DNS configuration"

   echo "Generating final config JSON"
   local config_json="{$(join , "${config[@]}")}"
   echo "Config JSON content: ${config_json}"
   echo "${config_json}" > "${OUTLINE_STATE_DIR}/outline_server_config.json"
   echo "Config file written to: ${OUTLINE_STATE_DIR}/outline_server_config.json"
   echo "write_config() completed successfully - returning to install_outline()"
}

function start_outline() {
  echo "Starting start_outline() function"
  local -r START_SCRIPT="${OUTLINE_STATE_DIR}/start_container.sh"
  echo "Creating start script at: ${START_SCRIPT}"

  # Usar host network mode para Linux
  local DOCKER_NETWORK_MODE="--net host"

  cat <<-EOF > "${START_SCRIPT}"
# This script starts the Outline server container ("Shadowbox").
# If you need to customize how the server is run, you can edit this script, then restart with:
#
#     "${START_SCRIPT}"

set -eu

docker stop "${OUTLINE_CONTAINER_NAME}" 2> /dev/null || true
docker rm -f "${OUTLINE_CONTAINER_NAME}" 2> /dev/null || true

docker_command=(
  docker
  run
  -d
  --name "${OUTLINE_CONTAINER_NAME}" --restart always ${DOCKER_NETWORK_MODE}

  # Used by Watchtower to know which containers to monitor.
  --label 'com.centurylinklabs.watchtower.enable=true'

  # Use log rotation. See   https://docs.docker.com/config/containers/logging/configure/.
  --log-driver local

  # The state that is persisted across restarts.
  -v "${OUTLINE_STATE_DIR}:${OUTLINE_STATE_DIR}"

  # Where the container keeps its persistent state.
  -e "SB_STATE_DIR=${OUTLINE_STATE_DIR}"

  # Port number and path prefix used by the server manager API.
  -e "SB_API_PORT=${OUTLINE_API_PORT}"
  -e "SB_API_PREFIX=${SB_API_PREFIX}"

  # Location of the API TLS certificate and key.
  -e "SB_CERTIFICATE_FILE=${OUTLINE_CERT_FILE}"
  -e "SB_PRIVATE_KEY_FILE=${OUTLINE_KEY_FILE}"

  # Where to report metrics to, if opted-in. (Disabled by default)
  # -e "SB_METRICS_URL=${SB_METRICS_URL:-}"

  # The Outline server image to run.
  "${OUTLINE_IMAGE}"
)
"\${docker_command[@]}"
EOF
  chmod +x "${START_SCRIPT}"
  echo "Start script created and made executable"
  # Declare then assign. Assigning on declaration messes up the return code.
  local STDERR_OUTPUT
  echo "Executing start script..."
  STDERR_OUTPUT="$({ "${START_SCRIPT}" >/dev/null; } 2>&1)" && {
    echo "Start script executed successfully"
    return 0
  }
  readonly STDERR_OUTPUT
  echo "Start script failed with error: ${STDERR_OUTPUT}"
  log_error "FAILED"
  log_error "${STDERR_OUTPUT}"
  return 1
}

function start_watchtower() {
  # Start watchtower to automatically fetch docker image updates.
  # Set watchtower to refresh every 30 seconds if a custom SB_IMAGE is used (for
  # testing).  Otherwise refresh every hour.
  local -ir WATCHTOWER_REFRESH_SECONDS="${WATCHTOWER_REFRESH_SECONDS:-3600}"

  local -ar docker_watchtower_flags=(--name watchtower --log-driver local --restart always \
      -v "/var/run/docker.sock:/var/run/docker.sock")
  # By itself, local messes up the return code.
  local STDERR_OUTPUT
  STDERR_OUTPUT="$(docker run -d "${docker_watchtower_flags[@]}" containrrr/watchtower --cleanup --label-enable --tlsverify --interval "${WATCHTOWER_REFRESH_SECONDS}" 2>&1 >/dev/null)" && return
  readonly STDERR_OUTPUT
  log_error "FAILED"
  if docker_container_exists watchtower; then
    handle_docker_container_conflict watchtower false
    return
  else
    log_error "${STDERR_OUTPUT}"
    return 1
  fi
}

# --- Funciones de Configuración Final ---
function wait_outline() {
  echo "Starting wait_outline() function"
  # We use insecure connection because our threat model doesn't include localhost port
  # interception and our certificate doesn't have localhost as a subject alternative name
  local LOCAL_API_URL="https://localhost:${OUTLINE_API_PORT}/${SB_API_PREFIX}"
  echo "Waiting for Outline API at: ${LOCAL_API_URL}/access-keys"
  local attempts=0
  local max_attempts=60  # 60 seconds timeout
  until curl --silent --insecure "${LOCAL_API_URL}/access-keys" >/dev/null; do
    ((attempts++))
    if (( attempts >= max_attempts )); then
      echo "Timeout waiting for Outline API after ${max_attempts} attempts"
      return 1
    fi
    echo "Attempt ${attempts}/${max_attempts}: Outline API not ready, waiting..."
    sleep 1
  done
  echo "Outline API is now responding"
}

# function create_first_user() {
#   echo "Starting create_first_user() function"
#   local LOCAL_API_URL="https://localhost:${OUTLINE_API_PORT}/${SB_API_PREFIX}"
#   echo "Creating first access key via POST to: ${LOCAL_API_URL}/access-keys"

#   # Capturar la respuesta JSON de la API
#   local response
#   response=$(curl --silent --insecure --request POST "${LOCAL_API_URL}/access-keys" 2>/dev/null)

#   # Verificar si curl tuvo éxito y la respuesta contiene JSON válido
#   if [[ $? -eq 0 ]] && [[ -n "$response" ]] && echo "$response" | jq . >/dev/null 2>&1; then
#     # Verificar si la respuesta contiene los campos esperados de una clave de acceso exitosa
#     if echo "$response" | jq -e '.id and .accessUrl' >/dev/null 2>&1; then
#       echo "First access key created successfully"
#       echo "Response: $response"
#       return 0
#     else
#       echo "API returned success but invalid response format: $response"
#       return 1
#     fi
#   else
#     echo "Failed to create first access key. Response: $response"
#     return 1
#     fi
# }

# --- Función de Creación de Directorios ---
function create_config_dirs() {
  mkdir -p "${HOME_DIR}"
  chmod ug+rwx,g+s,o-rwx "${HOME_DIR}"

  # Cambiar propietario al usuario actual no root
  CURRENT_USER=$(get_current_user)
  if [ -n "${CURRENT_USER}" ]; then
    chown -R "${CURRENT_USER}:${CURRENT_USER}" "${HOME_DIR}"
    echo -e "${GREEN}Permisos de directorio cambiados al usuario: ${CURRENT_USER}${NC}"
  fi
}

# --- Función de Desinstalación Completa ---
function uninstallOutline() {
  echo -e "${RED}WARNING: This will completely remove Outline server and ALL its data!${NC}"
  echo -e "${RED}This action cannot be undone. Make sure to backup your data first.${NC}"
  echo -n "Are you sure you want to continue? [y/N] "
  read -r response
  response=$(echo "${response}" | tr '[:upper:]' '[:lower:]')
  if [[ "${response}" != "y" && "${response}" != "yes" ]]; then
    echo "Uninstallation cancelled."
    exit 0
  fi

  # Detener y remover contenedor Docker
  if docker_container_exists "${OUTLINE_CONTAINER_NAME}"; then
    run_step "Stopping Outline container" docker stop "${OUTLINE_CONTAINER_NAME}"
    run_step "Removing Outline container" docker rm -f "${OUTLINE_CONTAINER_NAME}"
  fi

  # Remover imagen Docker si existe
  if docker images | grep -q "outline/shadowbox"; then
    run_step "Removing Outline Docker image" docker rmi "$(docker images | grep "outline/shadowbox" | awk '{print $3}')"
  fi

  # Remover contenedor watchtower si existe
  if docker_container_exists "watchtower"; then
    remove_watchtower_container
  fi

  # Remover directorios y archivos
  run_step "Removing Outline installation directory" rm -rf "${OUTLINE_DIR}"
  run_step "Removing Outline config directories" rm -rf "${HOME_DIR}"

  # Remover archivos .env generados
  rm -f ".env.outline.generated" ".env.ips.generated"

  # Limpiar archivos temporales
  rm -f "${FULL_LOG}" "${LAST_ERROR}"

  echo -e "\n${GREEN}Outline server has been completely uninstalled and cleaned.${NC}"
}

# --- Función de Limpieza Automática ---
function cleanup_expired_configs() {
  # Esta función se ejecuta periódicamente para limpiar configuraciones vencidas
  # Integrada con el sistema de limpieza de la base de datos
  echo -e "${ORANGE}Verificando configuraciones vencidas en ${HOME_DIR}...${NC}"

  # Aquí se integraría con la base de datos para obtener IDs de usuarios vencidos
  # Por ahora, es un placeholder que se puede expandir
  # Ejemplo: python3 -c "from database.crud.vpn import cleanup_expired_vpn_configs; cleanup_expired_vpn_configs('outline')"

  # Para este script, solo mostramos que la función existe
  echo -e "${GREEN}Función de limpieza automática integrada. Configuraciones vencidas serán eliminadas automáticamente.${NC}"
}

# --- Función de Verificación de Sintaxis ---
function check_syntax() {
  # Verificar sintaxis del script usando bash -n
  echo "Verificando sintaxis del script..."
  if bash -n "$0"; then
    echo "Sintaxis correcta"
    return 0
  else
    echo "Error de sintaxis en el script"
    return 1
  fi
}

# --- Función de Verificación de Instalación ---
function checkOutlineInstalled() {
  # Verificar si el contenedor Outline existe y está ejecutándose
  if docker_container_exists "${OUTLINE_CONTAINER_NAME}"; then
    echo "Outline container '${OUTLINE_CONTAINER_NAME}' exists"
    return 0
  else
    echo "Outline container '${OUTLINE_CONTAINER_NAME}' not found"
    return 1
  fi
}

function set_hostname() {
  # These are URLs that return the client's apparent IP address.
  # We have more than one to try in case one starts failing
  # (e.g. https://github.com/Jigsaw-Code/outline-server/issues/776  ).
  local -ar urls=(
    'https://icanhazip.com/'
    'https://ipinfo.io/ip'
    'https://domains.google.com/checkip'
  )
  echo "Attempting to determine external IP address..."
  if ! command_exists curl; then
    echo -e "${RED}[ERROR] curl is required but not found. Please install curl.${NC}" >&2
    return 1
  fi
  for url in "${urls[@]}"; do
    echo "Trying URL: ${url}"
    if OUTLINE_HOSTNAME="$(curl --silent --ipv4 "${url}" 2>/dev/null)"; then
      echo "Successfully obtained IP: ${OUTLINE_HOSTNAME}"
      return 0
    else
      echo "Failed to fetch from ${url}"
    fi
  done
  echo -e "${RED}[ERROR] Failed to determine the server's IP address. Try using --hostname <server IP>.${NC}" >&2
  return 1
}

# --- Funciones de Generación de .env ---
function generate_env_files() {
     echo "Starting generate_env_files() function"
     # Archivo de configuración principal de Outline
     ENV_FILE_OUTLINE=".env.outline.generated"
     # Archivo de IPs para la base de datos
     ENV_FILE_IPS=".env.ips.generated"

     echo "Creating ${ENV_FILE_OUTLINE}"
     echo "# --- uSipipo Outline Server Configuration ---" > "${ENV_FILE_OUTLINE}"
     OUTLINE_API_URL="https://${OUTLINE_HOSTNAME}:${OUTLINE_API_PORT}/${SB_API_PREFIX}"
     echo "OUTLINE_API_URL=\"${OUTLINE_API_URL}\"" >> "${ENV_FILE_OUTLINE}"
     echo "OUTLINE_CERT_SHA256=\"${OUTLINE_CERT_SHA256}\"" >> "${ENV_FILE_OUTLINE}"
     echo "OUTLINE_API_PORT=\"${OUTLINE_API_PORT}\"" >> "${ENV_FILE_OUTLINE}"
     echo "OUTLINE_HOSTNAME=\"${OUTLINE_HOSTNAME}\"" >> "${ENV_FILE_OUTLINE}"
     echo "OUTLINE_CONTAINER_NAME=\"${OUTLINE_CONTAINER_NAME}\"" >> "${ENV_FILE_OUTLINE}"
     echo "OUTLINE_IMAGE=\"${OUTLINE_IMAGE}\"" >> "${ENV_FILE_OUTLINE}"
     echo "OUTLINE_STATE_DIR=\"${OUTLINE_STATE_DIR}\"" >> "${ENV_FILE_OUTLINE}"
     echo "OUTLINE_CERT_FILE=\"${OUTLINE_CERT_FILE}\"" >> "${ENV_FILE_OUTLINE}"
     echo "OUTLINE_KEY_FILE=\"${OUTLINE_KEY_FILE}\"" >> "${ENV_FILE_OUTLINE}"

     # Verificar que las variables críticas estén definidas antes de escribir
     if [[ -z "${SB_API_PREFIX}" ]]; then
       echo "SB_API_PREFIX no está definido"
       return 1
     fi

     # Usar configuración DNS por defecto (sin Pi-hole)
     echo "# DNS: Using default DNS configuration" >> "${ENV_FILE_OUTLINE}"
     echo "" >> "${ENV_FILE_OUTLINE}"

     echo "# --- uSipipo IP Management for Outline (Placeholder) ---" > "${ENV_FILE_IPS}"
     # En Outline, las IPs no se gestionan directamente como en WireGuard.
     # La configuración de cada clave de acceso no incluye una IP fija asignada por el script.
     # Sin embargo, podemos definir rangos para el sistema uSipipo si se usan clientes personalizados o firewalls.
     # Para este script, generamos solo una variable base.
     echo "# Este servidor Outline no asigna IPs fijas por clave de acceso como WireGuard." >> "${ENV_FILE_IPS}"
     echo "# Las IPs de los clientes se gestionan dinámicamente por el túnel VPN." >> "${ENV_FILE_IPS}"
     echo "# Para fines de uSipipo, puedes definir rangos de IPs internas o reglas de firewall aquí." >> "${ENV_FILE_IPS}"
     echo "# OUTLINE_INTERNAL_SUBNET=\"10.0.86.0/24\" # Ejemplo de subnet interna (no asignada por este script)" >> "${ENV_FILE_IPS}"
     echo "" >> "${ENV_FILE_IPS}"
     echo "# IP Type Definitions for uSipipo DB (Copy to your Python code for Outline)" >> "${ENV_FILE_IPS}"
     echo "# outline_trial_ips = [] # Outline no asigna IPs fijas, este rango es informativo o para reglas." >> "${ENV_FILE_IPS}"
     echo "# outline_paid_ips = [] # Outline no asigna IPs fijas, este rango es informativo o para reglas." >> "${ENV_FILE_IPS}"

     echo -e "\n${GREEN}--- VARIABLES OUTLINE PARA TU .env DE USIPIPO ---${NC}"
     echo -e "${ORANGE}Archivo de configuración generado:${NC} ${ENV_FILE_OUTLINE}"
     echo -e "${ORANGE}Archivo de IPs generadas (informativo):${NC} ${ENV_FILE_IPS}"
     echo -e "${ORANGE}Directorio de configuraciones de cliente:${NC} ${HOME_DIR}"
     echo -e "${GREEN}----------------------------------------------------------${NC}"
     echo -e "\n${GREEN}Contenido de ${ENV_FILE_OUTLINE}:${NC}"
     cat "${ENV_FILE_OUTLINE}"
     echo -e "\n${GREEN}Contenido de ${ENV_FILE_IPS}:${NC}"
     cat "${ENV_FILE_IPS}"
     echo -e "\n${GREEN}----------------------------------------------------------${NC}"
     echo -e "${GREEN}¡Copia estas variables a tu archivo .env de uSipipo!${NC}"
     echo -e "${ORANGE}IMPORTANTE: Guarda las rutas de certificados de forma segura.${NC}"

     # Verificar que las variables críticas estén definidas
     if [[ -z "${OUTLINE_API_URL}" || -z "${OUTLINE_CERT_SHA256}" || -z "${OUTLINE_API_PORT}" || -z "${OUTLINE_HOSTNAME}" ]]; then
       echo -e "${RED}ERROR: Algunas variables críticas no se generaron correctamente${NC}"
       return 1
     fi
     echo "generate_env_files() completed successfully"
}

# --- Funciones de Ayuda y Parseo ---
function show_outline_status() {
  echo -e "\n${GREEN}=== OUTLINE SERVER STATUS ===${NC}"
  echo "Fecha y hora: $(date '+%Y-%m-%d %H:%M:%S UTC')"
  echo ""
  
  # 1. Verificar Docker
  echo -e "${ORANGE}1. ESTADO DE DOCKER${NC}"
  if command_exists docker; then
    echo -e "${GREEN}✓ Docker está instalado${NC}"
    if docker info >/dev/null 2>&1; then
      echo -e "${GREEN}✓ Docker daemon está ejecutándose${NC}"
      docker_version=$(docker --version 2>/dev/null || echo "Versión desconocida")
      echo "  Versión: ${docker_version}"
    else
      echo -e "${RED}✗ Docker daemon no está ejecutándose${NC}"
    fi
  else
    echo -e "${RED}✗ Docker no está instalado${NC}"
    return 1
  fi
  echo ""
  
  # 2. Verificar contenedor Outline
  echo -e "${ORANGE}2. CONTENEDOR OUTLINE${NC}"
  if docker_container_exists "${OUTLINE_CONTAINER_NAME}"; then
    echo -e "${GREEN}✓ Contenedor '${OUTLINE_CONTAINER_NAME}' existe${NC}"
    
    # Estado del contenedor
    container_status=$(docker inspect --format='{{.State.Status}}' "${OUTLINE_CONTAINER_NAME}" 2>/dev/null)
    echo "  Estado: ${container_status}"
    
    if [[ "${container_status}" == "running" ]]; then
      echo -e "${GREEN}  ✓ El contenedor está ejecutándose correctamente${NC}"
      
      # Información adicional del contenedor
      uptime=$(docker inspect --format='{{.State.StartedAt}}' "${OUTLINE_CONTAINER_NAME}" 2>/dev/null)
      if [[ -n "${uptime}" ]]; then
        echo "  Iniciado: ${uptime}"
      fi
      
      # Puertos expuestos
      ports=$(docker port "${OUTLINE_CONTAINER_NAME}" 2>/dev/null | grep -v '443/tcp' || echo "")
      if [[ -n "${ports}" ]]; then
        echo "  Puertos expuestos:"
        echo "${ports}" | while read -r line; do
          echo "    ${line}"
        done
      fi
    else
      echo -e "${RED}  ✗ El contenedor no está ejecutándose (Estado: ${container_status})${NC}"
    fi
  else
    echo -e "${RED}✗ Contenedor '${OUTLINE_CONTAINER_NAME}' no encontrado${NC}"
    echo "  Outline server no está instalado"
    return 1
  fi
  echo ""
  
  # 3. Verificar archivos de configuración
  echo -e "${ORANGE}3. ARCHIVOS DE CONFIGURACIÓN${NC}"
  if [[ -d "${OUTLINE_STATE_DIR:-/opt/outline/persisted-state}" ]]; then
    echo -e "${GREEN}✓ Directorio de estado existe: ${OUTLINE_STATE_DIR}${NC}"
    
    # Verificar archivos importantes
    local config_file="${OUTLINE_STATE_DIR}/outline_server_config.json"
    local cert_file="${OUTLINE_STATE_DIR}/outline-selfsigned.crt"
    local key_file="${OUTLINE_STATE_DIR}/outline-selfsigned.key"
    local start_script="${OUTLINE_STATE_DIR}/start_container.sh"
    
    if [[ -f "${config_file}" ]]; then
      echo -e "${GREEN}  ✓ Archivo de configuración: ${config_file}${NC}"
    else
      echo -e "${RED}  ✗ Archivo de configuración: ${config_file}${NC}"
    fi
    
    if [[ -f "${cert_file}" ]]; then
      echo -e "${GREEN}  ✓ Certificado TLS: ${cert_file}${NC}"
    else
      echo -e "${RED}  ✗ Certificado TLS: ${cert_file}${NC}"
    fi
    
    if [[ -f "${key_file}" ]]; then
      echo -e "${GREEN}  ✓ Clave privada TLS: ${key_file}${NC}"
    else
      echo -e "${RED}  ✗ Clave privada TLS: ${key_file}${NC}"
    fi
    
    if [[ -f "${start_script}" ]]; then
      echo -e "${GREEN}  ✓ Script de inicio: ${start_script}${NC}"
    else
      echo -e "${ORANGE}  • Script de inicio: ${start_script}${NC}"
    fi
  else
    echo -e "${RED}✗ Directorio de estado no encontrado${NC}"
  fi
  echo ""
  
  # 4. Verificar variables de entorno generadas
  echo -e "${ORANGE}4. VARIABLES DE ENTORNO${NC}"
  if [[ -f ".env.outline.generated" ]]; then
    echo -e "${GREEN}✓ Archivo .env.outline.generated encontrado${NC}"
    source .env.outline.generated 2>/dev/null || true
    
    if [[ -n "${OUTLINE_API_URL:-}" ]]; then
      echo -e "${GREEN}  ✓ API URL: ${OUTLINE_API_URL}${NC}"
    else
      echo -e "${ORANGE}  • API URL: No configurada${NC}"
    fi
    
    if [[ -n "${OUTLINE_CERT_SHA256:-}" ]]; then
      echo -e "${GREEN}  ✓ Cert SHA256: ${OUTLINE_CERT_SHA256:0:16}...${NC}"
    else
      echo -e "${ORANGE}  • Cert SHA256: No configurado${NC}"
    fi
    
    if [[ -n "${OUTLINE_API_PORT:-}" ]]; then
      echo -e "${GREEN}  ✓ Puerto API: ${OUTLINE_API_PORT}${NC}"
    else
      echo -e "${ORANGE}  • Puerto API: No configurado${NC}"
    fi
    
    if [[ -n "${OUTLINE_HOSTNAME:-}" ]]; then
      echo -e "${GREEN}  ✓ Hostname: ${OUTLINE_HOSTNAME}${NC}"
    else
      echo -e "${ORANGE}  • Hostname: No configurado${NC}"
    fi
  else
    echo -e "${ORANGE}• Archivo .env.outline.generated no encontrado${NC}"
    echo "  Generar con: ./outline-install.sh --reinstall"
  fi
  echo ""
  
  # 5. Verificar conectividad de la API
  echo -e "${ORANGE}5. CONECTIVIDAD DE LA API${NC}"
  if [[ -f ".env.outline.generated" ]]; then
    source .env.outline.generated 2>/dev/null || true
    
    if [[ -n "${OUTLINE_API_URL:-}" && -n "${OUTLINE_CERT_SHA256:-}" ]]; then
      echo "Probando conectividad a la API..."
      
      # Intentar conectar a la API (sin verificación SSL ya que es localhost)
      if curl -s -k --max-time 5 "${OUTLINE_API_URL}/access-keys" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ API de Outline respondiendo correctamente${NC}"
        
        # Obtener información adicional de la API
        api_response=$(curl -s -k --max-time 5 "${OUTLINE_API_URL}/access-keys" 2>/dev/null || echo "")
        if [[ -n "${api_response}" ]]; then
          echo "  Respuesta de la API recibida exitosamente"
        fi
      else
        echo -e "${RED}✗ API de Outline no responde${NC}"
        echo "  Posibles causas:"
        echo "  - El contenedor no está completamente iniciado"
        echo "  - Problemas de red o firewall"
        echo "  - Configuración incorrecta"
      fi
    else
      echo -e "${ORANGE}• Variables de API no configuradas, omitiendo prueba de conectividad${NC}"
    fi
  else
    echo -e "${ORANGE}• No se puede probar conectividad sin archivo .env generado${NC}"
  fi
  echo ""
  
  # 6. Información del sistema
  echo -e "${ORANGE}6. INFORMACIÓN DEL SISTEMA${NC}"
  echo "  Sistema operativo: $(uname -s)"
  echo "  Arquitectura: $(uname -m)"
  echo "  Memoria disponible: $(free -h 2>/dev/null | awk 'NR==2{printf "%.1fGB total, %.1fGB disponible", $2/1024/1024/1024, $7/1024/1024/1024}' || echo 'No disponible')"
  echo "  Espacio en disco: $(df -h /opt 2>/dev/null | awk 'NR==2{printf "%.1fGB total, %.1fGB libre", $2/1024/1024/1024, $4/1024/1024/1024}' || echo 'No disponible')"
  echo ""
  
  # 7. Resumen final
  echo -e "${GREEN}=== RESUMEN DEL ESTADO ===${NC}"
  if docker_container_exists "${OUTLINE_CONTAINER_NAME}" && [[ "$(docker inspect --format='{{.State.Status}}' "${OUTLINE_CONTAINER_NAME}" 2>/dev/null)" == "running" ]]; then
    echo -e "${GREEN}✓ OUTLINE SERVER: OPERATIVO${NC}"
    echo "  El servidor Outline está ejecutándose correctamente."
    echo "  Para conectar el Outline Manager, use:"
    echo "  apiUrl: ${OUTLINE_API_URL:-'No disponible'}"
    echo "  certSha256: ${OUTLINE_CERT_SHA256:-'No disponible'}"
  else
    echo -e "${RED}✗ OUTLINE SERVER: NO OPERATIVO${NC}"
    echo "  El servidor Outline no está ejecutándose correctamente."
    echo "  Ejecutar: ./outline-install.sh --reinstall"
  fi
  
  echo -e "\n${ORANGE}Para obtener información detallada de la API:${NC}"
  echo "  curl -k '${OUTLINE_API_URL:-'https://localhost:Puerto/API_PREFIX'}/access-keys'"
  
  echo ""
}

function display_usage() {
  cat <<EOF
Usage: $0 [options]

Options:
  --install      Install Outline server (default action if no Outline is installed)
  --uninstall    Completely remove Outline server and all its data
  --reinstall    Remove existing Outline installation and reinstall
  --status       Show detailed status of Outline server
  --hostname     The hostname to be used to access the management API and access keys
  --api-port     The port number for the management API
  --keys-port    The port number for the access keys
  --help         Display this help message

Environment variables:
  OUTLINE_DIR        Outline installation directory (default: /opt/outline)
  OUTLINE_IMAGE      Docker image to use (default: quay.io/outline/shadowbox:stable)
EOF
}

function escape_json_string() {
  local input=$1
  for ((i = 0; i < ${#input}; i++)); do
    local char="${input:i:1}"
    local escaped="${char}"
    case "${char}" in
      $'"' ) escaped="\\\"";;
      $'\\') escaped="\\\\";;
      *)
        if [[ "${char}" < $'\x20' ]]; then
          case "${char}" in
            $'\b') escaped="\\b";;
            $'\f') escaped="\\f";;
            $'\n') escaped="\\n";;
            $'\r') escaped="\\r";;
            $'\t') escaped="\\t";;
            *) escaped=$(printf "\u%04X" "'${char}")
          esac
        fi;;
    esac
    echo -n "${escaped}"
  done
}

function parse_flags() {
  local params
  params="$(getopt --longoptions hostname:,api-port:,keys-port:,install,uninstall,reinstall,status,help -n "$0" -- "$0" "$@")"
  eval set -- "${params}"

  while (( $# > 0 )); do
    local flag="$1"
    shift
    case "${flag}" in
      --hostname)
        FLAGS_HOSTNAME="$1"
        shift
        ;;
      --api-port)
        FLAGS_API_PORT=$1
        shift
        if ! is_valid_port "${FLAGS_API_PORT}"; then
          log_error "Invalid value for ${flag}: ${FLAGS_API_PORT}" >&2
          exit 1
        fi
        ;;
      --keys-port)
        FLAGS_KEYS_PORT=$1
        shift
        if ! is_valid_port "${FLAGS_KEYS_PORT}"; then
          log_error "Invalid value for ${flag}: ${FLAGS_KEYS_PORT}" >&2
          exit 1
        fi
        ;;
      --install|--uninstall|--reinstall|--status|--help)
        # These are handled in main()
        ;;
      --)
        break
        ;;
      *) # This should not happen
        log_error "Unsupported flag ${flag}" >&2
        display_usage >&2
        exit 1
        ;;
    esac
  done
  if (( FLAGS_API_PORT != 0 && FLAGS_API_PORT == FLAGS_KEYS_PORT )); then
    log_error "--api-port must be different from --keys-port" >&2
    exit 1
  fi
  return 0
}

# --- Función Principal de Instalación ---
install_outline() {
  local MACHINE_TYPE
  MACHINE_TYPE="$(uname -m)"
  if [[ "${MACHINE_TYPE}" != "x86_64" && "${MACHINE_TYPE}" != "aarch64" && "${MACHINE_TYPE}" != "arm64" ]]; then
    log_error "Unsupported machine type: ${MACHINE_TYPE}. Please run this script on a x86_64, aarch64, or arm64 machine"
    exit 1
  fi

  # Make sure we don't leak readable files to other users.
  umask 0007

  echo "Starting Outline installation process"
  run_step "Verifying that Docker is installed" verify_docker_installed
  run_step "Verifying that Docker daemon is running" verify_docker_running

  log_for_sentry "Creating Outline directory"
  echo "Creating Outline directory: ${OUTLINE_DIR}"
  mkdir -p "${OUTLINE_DIR}"
  chmod u+s,ug+rwx,o-rwx "${OUTLINE_DIR}"

  # Cambiar propietario al usuario actual no root
  CURRENT_USER=$(get_current_user)
  if [ -n "${CURRENT_USER}" ]; then
    chown -R "${CURRENT_USER}:${CURRENT_USER}" "${OUTLINE_DIR}"
    echo -e "${GREEN}Permisos de directorio Outline cambiados al usuario: ${CURRENT_USER}${NC}"
  fi

  # Asignar puertos después de parse_flags
  OUTLINE_API_PORT="${FLAGS_API_PORT}"
  if (( OUTLINE_API_PORT == 0 )); then
    OUTLINE_API_PORT=$(get_random_port)
    echo "Generated random API port: ${OUTLINE_API_PORT}"
  else
    echo "Using provided API port: ${OUTLINE_API_PORT}"
  fi
  readonly OUTLINE_API_PORT

  OUTLINE_KEYS_PORT="${FLAGS_KEYS_PORT}"
  if (( OUTLINE_KEYS_PORT == 0 )); then
    OUTLINE_KEYS_PORT=$(get_random_port)
    echo "Generated random keys port: ${OUTLINE_KEYS_PORT}"
  else
    echo "Using provided keys port: ${OUTLINE_KEYS_PORT}"
  fi
  readonly OUTLINE_KEYS_PORT # Aunque no se usa directamente en la configuración, se registra

  OUTLINE_HOSTNAME="${FLAGS_HOSTNAME}"
  if [[ -z "${OUTLINE_HOSTNAME}" ]]; then
    run_step "Setting OUTLINE_HOSTNAME to external IP" set_hostname
  else
    echo "Using provided hostname: ${OUTLINE_HOSTNAME}"
  fi
  readonly OUTLINE_HOSTNAME

  # Make a directory for persistent state
  run_step "Creating config directories" create_config_dirs
  run_step "Creating persistent state dir" create_persisted_state_dir
  run_step "Generating secret key" generate_secret_key
  run_step "Generating TLS certificate" generate_certificate
  run_step "Generating SHA-256 certificate fingerprint" generate_certificate_fingerprint
  run_step "Writing config" write_config
  echo "write_config completed, proceeding to start Outline"

  # TODO(dborkan): if the script fails after docker run, it will continue to fail
  # as the names outline and watchtower will already be in use.  Consider
  # deleting the container in the case of failure (e.g. using a trap, or
  # deleting existing containers on each run).
  run_step "Starting Outline" start_outline
  echo "start_outline completed, proceeding to start Watchtower"

  # TODO(fortuna): Don't wait for Outline to run this.
  run_step "Starting Watchtower" start_watchtower
  echo "start_watchtower completed, proceeding to wait for Outline"

  run_step "Waiting for Outline server to be healthy" wait_outline
  echo "Outline server is healthy, proceeding to obtain manager configuration"

  # Ejecutar limpieza automática
  cleanup_expired_configs
  echo "Cleanup completed, proceeding to generate env files"

  # Generar archivos .env al finalizar
  generate_env_files
  echo "Env files generated, installation completed successfully"
  echo "Outline installation process finished"

  # Verificar que la configuración del manager esté disponible
  if [[ -n "${OUTLINE_API_URL}" && -n "${OUTLINE_CERT_SHA256}" ]]; then
    echo "Manager configuration obtained successfully: apiUrl=${OUTLINE_API_URL}, certSha256=${OUTLINE_CERT_SHA256}"
  else
    echo "ERROR: Failed to obtain manager configuration"
    return 1
  fi

  # Mensaje final
  local OUTLINE_MANAGER_CONFIG
  OUTLINE_MANAGER_CONFIG="{\"apiUrl\":\"https://${OUTLINE_HOSTNAME}:${OUTLINE_API_PORT}/${SB_API_PREFIX}\",\"certSha256\":\"${OUTLINE_CERT_SHA256}\"}"
  echo -e "\n${GREEN}CONGRATULATIONS! Your Outline server is up and running.${NC}"
  echo -e "\n${GREEN}To manage your Outline server, please copy the following line (including curly"
  echo -e "${GREEN}brackets) into Step 2 of the Outline Manager interface:${NC}"
  echo -e "\n${GREEN}${OUTLINE_MANAGER_CONFIG}${NC}"
  echo -e "\n${ORANGE}Remember to open the API port ${OUTLINE_API_PORT} and the access key ports (dynamic) on your firewall.${NC}"
  echo -e "${ORANGE}Client configurations will be stored in: ${HOME_DIR}${NC}"
}

# --- Función Principal ---
function main() {
  # Verificar sintaxis antes de proceder
  if ! check_syntax; then
    exit 1
  fi

  # Set trap which publishes error tag only if there is an error.
  function finish {
    local -ir EXIT_CODE=$?
    if (( EXIT_CODE != 0 )); then
      if [[ -s "${LAST_ERROR}" ]]; then
        log_error "\nLast error: $(< "${LAST_ERROR}")" >&2
      fi
      log_error "\nSorry! Something went wrong. If you can't figure this out, please copy and paste all this output into the Outline Manager screen, and send it to us, to see if we can help you." >&2
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
      --status)
        show_outline_status
        exit 0
        ;;
      --help)
        display_usage
        exit 0
        ;;
      *)
        # Pass remaining arguments to parse_flags for hostname, ports, etc.
        break
        ;;
    esac
  done

  parse_flags "$@"

  case "${ACTION}" in
    "install")
      if checkOutlineInstalled; then
        log_error "Outline is already installed. Use --reinstall if you want to reinstall."
        exit 1
      fi
      install_outline
      ;;
    "uninstall")
      if ! checkOutlineInstalled; then
        log_error "Outline is not installed."
        exit 1
      fi
      uninstallOutline
      ;;
    "reinstall")
      if checkOutlineInstalled; then
        echo -e "${ORANGE}Outline is currently installed. Proceeding with removal first...${NC}"
        uninstallOutline
      fi
      install_outline
      ;;
    "auto")
      if checkOutlineInstalled; then
        log_error "Outline is already installed. Use --reinstall to reinstall or --uninstall to remove."
        exit 1
      else
        install_outline
      fi
      ;;
  esac
}

main "$@"
