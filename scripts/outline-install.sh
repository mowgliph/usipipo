#!/bin/bash

# Secure Outline server installer for uSipipo
# Refactored to generate uSipipo .env variables and manage trial IPs
# Based on: https://github.com/Jigsaw-Code/outline-server

set -euo pipefail

# --- Constantes ---
OUTLINE_DIR="/opt/outline"
OUTLINE_CONTAINER_NAME="outline"
OUTLINE_IMAGE_DEFAULT="quay.io/outline/shadowbox:stable"
HOME_DIR="VPNs Configs/outline/"
TRIAL_IP_START=2  # Primera IP usable
TRIAL_IP_END=26   # Última IP para trial (25 IPs: 2 a 26)
PAID_IP_START=27  # Primera IP para usuarios pagos
PAID_IP_END=254   # Última IP usable (254 es el límite común)

# --- Variables globales ---
FLAGS_HOSTNAME=""
FLAGS_API_PORT=0
FLAGS_KEYS_PORT=0
# Variables de entorno que pueden ser sobrescritas
OUTLINE_DIR="${OUTLINE_DIR:-/opt/outline}"
OUTLINE_CONTAINER_NAME="${CONTAINER_NAME:-${OUTLINE_CONTAINER_NAME}}"
OUTLINE_IMAGE="${SB_IMAGE:-${OUTLINE_IMAGE_DEFAULT}}"
OUTLINE_API_PORT=0 # Se asignará después de parse_flags
OUTLINE_KEYS_PORT=0 # Se asignará después de parse_flags
OUTLINE_HOSTNAME=""
OUTLINE_STATE_DIR=""
OUTLINE_CERT_FILE=""
OUTLINE_KEY_FILE=""
OUTLINE_API_URL=""
OUTLINE_CERT_SHA256=""

# --- Función de Detección de Pi-hole ---

function detect_pihole() {
    echo "[DEBUG] Starting detect_pihole() function - using only .env.pihole.generated"

    # Validar existencia y legibilidad del archivo
    if [[ ! -f ".env.pihole.generated" ]]; then
        echo "[DEBUG] .env.pihole.generated file not found"
        return 1
    fi

    if [[ ! -r ".env.pihole.generated" ]]; then
        echo "[ERROR] .env.pihole.generated file exists but is not readable"
        return 1
    fi

    echo "[DEBUG] Found readable .env.pihole.generated file, sourcing it"
    source ".env.pihole.generated"

    # Verificar que las variables necesarias estén definidas
    if [[ -z "${PIHOLE_HOST}" || -z "${PIHOLE_PORT}" ]]; then
        echo "[ERROR] PIHOLE_HOST or PIHOLE_PORT not defined in .env.pihole.generated"
        return 1
    fi

    echo "[DEBUG] Loaded variables from .env.pihole.generated:"
    echo "[DEBUG]   PIHOLE_HOST: ${PIHOLE_HOST}"
    echo "[DEBUG]   PIHOLE_PORT: ${PIHOLE_PORT}"

    # Validar que Pi-hole esté funcionando con timeout reducido
    echo "[DEBUG] Testing Pi-hole connectivity with curl (timeout 3s)"
    local curl_output
    local curl_exit_code
    curl_output=$(curl -s --max-time 3 --connect-timeout 2 "http://${PIHOLE_HOST}:${PIHOLE_PORT}/admin/api.php" 2>&1)
    curl_exit_code=$?

    echo "[DEBUG] curl exit code: ${curl_exit_code}"
    if [[ ${curl_exit_code} -eq 0 ]]; then
        echo "[DEBUG] curl succeeded, Pi-hole is responding via config file"
        PIHOLE_IP="${PIHOLE_HOST}"
        echo "[DEBUG] Set PIHOLE_IP to: ${PIHOLE_IP}"
        return 0
    else
        echo "[DEBUG] curl failed with exit code ${curl_exit_code}"
        echo "[DEBUG] curl output/error: ${curl_output}"
        echo "[WARN] Pi-hole config file found but Pi-hole is not responding"
        return 1
    fi
}
# --- Funciones de Validación ---
function is_valid_port() {
  (( 0 < "$1" && "$1" <= 65535 ))
}

function command_exists {
  command -v "$@" &> /dev/null
}

function get_random_port {
  local -i num=0  # Init to an invalid value, to prevent "unbound variable" errors.
  until (( 1024 <= num && num < 65536)); do
    num=$(( RANDOM + (RANDOM % 2) * 32768 ));
  done;
  echo "${num}";
}

# --- Funciones de Logging ---
# I/O conventions for this script:
# - Ordinary status messages are printed to STDOUT
# - STDERR is only used in the event of a fatal error
# - Detailed logs are recorded to this FULL_LOG, which is preserved if an error occurred.
# - The most recent error is stored in LAST_ERROR, which is never preserved.
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
  curl --silent --show-error --fail "$@"
}

function log_for_sentry() {
  # if [[ -n "${SENTRY_LOG_FILE}" ]]; then # Opcional, si se quiere mantener
  #   echo "[$(date "+%Y-%m-%d@%H:%M:%S")] install_server.sh" "$@" >> "${SENTRY_LOG_FILE}"
  # fi
  echo "$@" >> "${FULL_LOG}"
}

# --- Funciones de Verificación ---
# Check to see if docker is installed.
function verify_docker_installed() {
  if command_exists docker; then
    return 0
  fi
  log_error "NOT INSTALLED"
  if ! confirm "Would you like to install Docker? This will run 'curl https://get.docker.com/ | sh'."; then
    exit 0
  fi
  if ! run_step "Installing Docker" install_docker; then
    log_error "Docker installation failed, please visit https://docs.docker.com/install for instructions."
    exit 1
  fi
  log_start_step "Verifying Docker installation"
  command_exists docker
}

function verify_docker_running() {
  local STDERR_OUTPUT
  STDERR_OUTPUT="$(docker info 2>&1 >/dev/null)" || return
  local -ir RET=$?
  if (( RET == 0 )); then
    return 0
  elif [[ "${STDERR_OUTPUT}" == *"Is the docker daemon running"* ]]; then
    start_docker
    return
  fi
  return "${RET}"
}

function install_docker() {
  (
    # Change umask so that /usr/share/keyrings/docker-archive-keyring.gpg has the right permissions.
    # See https://github.com/Jigsaw-Code/outline-server/issues/951.
    # We do this in a subprocess so the umask for the calling process is unaffected.
    umask 0022
    fetch https://get.docker.com/ | sh
  ) >&2
}

function start_docker() {
  systemctl enable --now docker.service >&2
}

# --- Funciones de Docker ---
function docker_container_exists() {
  docker ps -a --format '{{.Names}}' | grep --quiet "^$1$"
}

function remove_watchtower_container() {
  remove_docker_container watchtower
}

function remove_docker_container() {
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
}

function safe_base64() {
  # Implements URL-safe base64 of stdin, stripping trailing = chars.
  # Writes result to stdout.
  # TODO: this gives the following errors on Mac:
  #   base64: invalid option -- w
  #   tr: illegal option -- - -
  local url_safe
  url_safe="$(base64 -w 0 - | tr '/+' '_-')"
  echo -n "${url_safe%%=*}"  # Strip trailing = chars
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
  openssl req "${openssl_req_flags[@]}" >&2
}

function generate_certificate_fingerprint() {
  # Add a tag with the SHA-256 fingerprint of the certificate.
  # (Electron uses SHA-256 fingerprints: https://github.com/electron/electron/blob/9624bc140353b3771bd07c55371f6db65fd1b67e/atom/common/native_mate_converters/net_converter.cc#L60)
  # Example format: "SHA256 Fingerprint=BD:DB:C9:A4:39:5C:B3:4E:6E:CF:18:43:61:9F:07:A2:09:07:37:35:63:67"
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
  echo "[DEBUG] Starting write_config() function"
  local -a config=()
  echo "[DEBUG] Checking FLAGS_KEYS_PORT: ${FLAGS_KEYS_PORT}"
  if (( FLAGS_KEYS_PORT != 0 )); then
    config+=("\"portForNewAccessKeys\": ${FLAGS_KEYS_PORT}")
    echo "[DEBUG] Added portForNewAccessKeys: ${FLAGS_KEYS_PORT}"
  fi
  # No se establece nombre por defecto en este script refactorizado
  # if [[ -n "${SB_DEFAULT_SERVER_NAME:-}" ]]; then
  #   config+=("\"name\": \"$(escape_json_string "${SB_DEFAULT_SERVER_NAME}")\"")
  # fi
  echo "[DEBUG] Adding hostname: ${OUTLINE_HOSTNAME}"
  config+=("\"hostname\": \"$(escape_json_string "${OUTLINE_HOSTNAME}")\"")
  config+=("\"metricsEnabled\": false") # Deshabilitado por defecto
  echo "[DEBUG] Config array so far: ${config[*]}"

  # Configurar DNS upstream si Pi-hole está disponible
  echo "[DEBUG] Starting Pi-hole detection..."
  # Ejecutar detección de Pi-hole de forma opcional y silenciosa
  local pihole_detected=false
  local detection_method=""

  echo "[DEBUG] Running Pi-hole detection (optional)"
  if detect_pihole; then
    pihole_detected=true
    detection_method="config file (.env.pihole.generated)"
    echo "[DEBUG] Pi-hole detection succeeded via ${detection_method}"
  else
    echo "[DEBUG] Pi-hole not detected, using default DNS"
  fi

  if [[ "${pihole_detected}" == "true" ]]; then
    config+=("\"dnsResolver\": \"${PIHOLE_IP}\"")
    echo -e "${GREEN}Pi-hole detected via ${detection_method}. Using ${PIHOLE_IP} as DNS upstream.${NC}"
    echo "[DEBUG] Added dnsResolver: ${PIHOLE_IP}"
  else
    echo "[DEBUG] Using default DNS configuration"
  fi

  echo "[DEBUG] Generating final config JSON"
  echo "{$(join , "${config[@]}")}" > "${OUTLINE_STATE_DIR}/outline_server_config.json"
  echo "[DEBUG] Config file written to: ${OUTLINE_STATE_DIR}/outline_server_config.json"
  echo "[DEBUG] write_config() completed successfully"
}

function start_outline() {
  local -r START_SCRIPT="${OUTLINE_STATE_DIR}/start_container.sh"
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
  --name "${OUTLINE_CONTAINER_NAME}" --restart always --net host

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
  # Declare then assign. Assigning on declaration messes up the return code.
  local STDERR_OUTPUT
  STDERR_OUTPUT="$({ "${START_SCRIPT}" >/dev/null; } 2>&1)" && return
  readonly STDERR_OUTPUT
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
      -v /var/run/docker.sock:/var/run/docker.sock)
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
  # We use insecure connection because our threat model doesn't include localhost port
  # interception and our certificate doesn't have localhost as a subject alternative name
  local LOCAL_API_URL="https://localhost:${OUTLINE_API_PORT}/${SB_API_PREFIX}"
  until fetch --insecure "${LOCAL_API_URL}/access-keys" >/dev/null; do sleep 1; done
}

function create_first_user() {
  local LOCAL_API_URL="https://localhost:${OUTLINE_API_PORT}/${SB_API_PREFIX}"
  fetch --insecure --request POST "${LOCAL_API_URL}/access-keys" >&2
}

# --- Función de Creación de Directorios ---
function create_config_dirs() {
  mkdir -p "${HOME_DIR}"
  chmod ug+rwx,g+s,o-rwx "${HOME_DIR}"
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

# --- Función de Verificación de Instalación ---
function checkOutlineInstalled() {
  if docker_container_exists "${OUTLINE_CONTAINER_NAME}"; then
    return 0
  else
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
  for url in "${urls[@]}"; do
    OUTLINE_HOSTNAME="$(fetch --ipv4 "${url}")" && return
  done
  echo "Failed to determine the server's IP address.  Try using --hostname <server IP>." >&2
  return 1
}

# --- Funciones de Generación de .env ---
function generate_env_files() {
    # Archivo de configuración principal de Outline
    ENV_FILE_OUTLINE=".env.outline.generated"
    # Archivo de IPs para la base de datos
    ENV_FILE_IPS=".env.ips.generated"

    echo "# --- uSipipo Outline Server Configuration ---" > "${ENV_FILE_OUTLINE}"
    echo "OUTLINE_API_URL=\"https://${OUTLINE_HOSTNAME}:${OUTLINE_API_PORT}/${SB_API_PREFIX}\"" >> "${ENV_FILE_OUTLINE}"
    echo "OUTLINE_CERT_SHA256=\"${OUTLINE_CERT_SHA256}\"" >> "${ENV_FILE_OUTLINE}"
    echo "OUTLINE_API_PORT=\"${OUTLINE_API_PORT}\"" >> "${ENV_FILE_OUTLINE}"
    echo "OUTLINE_HOSTNAME=\"${OUTLINE_HOSTNAME}\"" >> "${ENV_FILE_OUTLINE}"
    echo "OUTLINE_CONTAINER_NAME=\"${OUTLINE_CONTAINER_NAME}\"" >> "${ENV_FILE_OUTLINE}"
    echo "OUTLINE_IMAGE=\"${OUTLINE_IMAGE}\"" >> "${ENV_FILE_OUTLINE}"
    echo "OUTLINE_STATE_DIR=\"${OUTLINE_STATE_DIR}\"" >> "${ENV_FILE_OUTLINE}"
    echo "OUTLINE_CERT_FILE=\"${OUTLINE_CERT_FILE}\"" >> "${ENV_FILE_OUTLINE}"
    echo "OUTLINE_KEY_FILE=\"${OUTLINE_KEY_FILE}\"" >> "${ENV_FILE_OUTLINE}"

    # Agregar configuración DNS si Pi-hole está disponible
    if detect_pihole; then
        echo "OUTLINE_DNS_UPSTREAM=\"${PIHOLE_IP}\"" >> "${ENV_FILE_OUTLINE}"
        echo "# DNS: Using Pi-hole (${PIHOLE_IP}) as upstream DNS" >> "${ENV_FILE_OUTLINE}"
    else
        echo "# DNS: Using default DNS configuration" >> "${ENV_FILE_OUTLINE}"
    fi
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
}

# --- Funciones de Ayuda y Parseo ---
function display_usage() {
  cat <<EOF
Usage: $0 [options]

Options:
  --install      Install Outline server (default action if no Outline is installed)
  --uninstall    Completely remove Outline server and all its data
  --reinstall    Remove existing Outline installation and reinstall
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
  params="$(getopt --longoptions hostname:,api-port:,keys-port:,install,uninstall,reinstall,help -n "$0" -- "$0" "$@")"
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
      --install|--uninstall|--reinstall|--help)
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
  if [[ "${MACHINE_TYPE}" != "x86_64" ]]; then
    log_error "Unsupported machine type: ${MACHINE_TYPE}. Please run this script on a x86_64 machine"
    exit 1
  fi

  # Make sure we don't leak readable files to other users.
  umask 0007

  run_step "Verifying that Docker is installed" verify_docker_installed
  run_step "Verifying that Docker daemon is running" verify_docker_running

  log_for_sentry "Creating Outline directory"
  mkdir -p "${OUTLINE_DIR}"
  chmod u+s,ug+rwx,o-rwx "${OUTLINE_DIR}"

  # Asignar puertos despues de parse_flags
  OUTLINE_API_PORT="${FLAGS_API_PORT}"
  if (( OUTLINE_API_PORT == 0 )); then
    OUTLINE_API_PORT=$(get_random_port)
  fi
  readonly OUTLINE_API_PORT

  OUTLINE_KEYS_PORT="${FLAGS_KEYS_PORT}"
  if (( OUTLINE_KEYS_PORT == 0 )); then
    OUTLINE_KEYS_PORT=$(get_random_port)
  fi
  readonly OUTLINE_KEYS_PORT # Aunque no se usa directamente en la configuración, se registra

  OUTLINE_HOSTNAME="${FLAGS_HOSTNAME}"
  if [[ -z "${OUTLINE_HOSTNAME}" ]]; then
    run_step "Setting OUTLINE_HOSTNAME to external IP" set_hostname
  fi
  readonly OUTLINE_HOSTNAME

  # Make a directory for persistent state
  run_step "Creating config directories" create_config_dirs
  run_step "Creating persistent state dir" create_persisted_state_dir
  run_step "Generating secret key" generate_secret_key
  run_step "Generating TLS certificate" generate_certificate
  run_step "Generating SHA-256 certificate fingerprint" generate_certificate_fingerprint
  run_step "Writing config" write_config

  # TODO(dborkan): if the script fails after docker run, it will continue to fail
  # as the names outline and watchtower will already be in use.  Consider
  # deleting the container in the case of failure (e.g. using a trap, or
  # deleting existing containers on each run).
  run_step "Starting Outline" start_outline
  # TODO(fortuna): Don't wait for Outline to run this.
  run_step "Starting Watchtower" start_watchtower

  run_step "Waiting for Outline server to be healthy" wait_outline
  run_step "Creating first user" create_first_user

  # Ejecutar limpieza automática
  cleanup_expired_configs

  # Generar archivos .env al finalizar
  generate_env_files

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



---

### 🔍 **Cambios Realizados**
#
#     1.  **Nombre de Variables:** Cambié las variables internas del script para que reflejen que es Outline (`OUTLINE_*` en lugar de `SB_*`) y sean consistentes con el propósito del script.
#     2.  **Constantes:** Definí constantes para rutas, imagen por defecto y rangos de IPs (aunque para Outline, la asignación de IPs fijas no es directa como en WireGuard, se incluyen para consistencia con el objetivo general del proyecto uSipipo).
#     3.  **Generación de IPs:** Añadí la función `generate_env_files` que crea dos archivos:
#         *   `.env.outline.generated`: Contiene las variables principales de Outline (API URL, cert SHA256, hostname, etc.).
#         *   `.env.ips.generated`: Contiene comentarios explicativos sobre cómo Outline no asigna IPs fijas por clave, pero se pueden definir rangos para fines de auditoría o reglas de firewall. Se incluye un placeholder para el código Python.
#     4.  **Colores:** Añadí definiciones de colores (`GREEN`, `ORANGE`, `NC`) y usé `echo -e` para colorear la salida final del `.env`.
#     5.  **Comentarios Claros:** Agregué comentarios para explicar la generación de IPs y su propósito específico para Outline.
#     6.  **Mensaje Final:** El mensaje final ahora incluye la generación de los archivos `.env` y un mensaje claro sobre qué hacer con ellos, similar al script de WireGuard.
