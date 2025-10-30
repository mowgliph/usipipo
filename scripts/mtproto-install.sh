#!/bin/bash

# Free MTProto Proxy installer for Telegram - uSipipo
# Docker-based installation for free Telegram proxy configuration
# Based on https://github.com/TelegramMessenger/MTProxy
# Generates uSipipo .env variables upon installation.

set -euo pipefail

# --- Constantes de Configuración ---
MTPROXY_DIR_DEFAULT="/opt/mtproto-proxy"                 # Directorio de instalación en Linux
HOME_DIR_DEFAULT="VPNs_Configs/mtproto/"                 # Directorio relativo para configuraciones

MTPROXY_DIR="${MTPROXY_DIR:-$MTPROXY_DIR_DEFAULT}"       # Directorio de instalación de MTProto
MTPROXY_CONTAINER_NAME="mtproto-proxy"                   # Nombre del contenedor Docker
MTPROXY_IMAGE_DEFAULT="telegrammessenger/proxy:latest"   # Imagen Docker por defecto
HOME_DIR="${HOME_DIR:-$HOME_DIR_DEFAULT}"                # Directorio para configuraciones de cliente


# --- Colores para salida de terminal ---
GREEN='\033[0;32m'   # Verde para mensajes de éxito
ORANGE='\033[0;33m'  # Naranja para advertencias
RED='\033[0;31m'     # Rojo para errores
NC='\033[0m'         # Reset de color

# --- Variables Globales ---
# Variables de flags de línea de comandos
FLAGS_HOSTNAME=""     # Hostname proporcionado por usuario
FLAGS_PORT=0          # Puerto proporcionado por usuario

# Variables de entorno que pueden ser sobrescritas
MTPROXY_DIR="${MTPROXY_DIR:-/opt/mtproto-proxy}"
MTPROXY_CONTAINER_NAME="${CONTAINER_NAME:-${MTPROXY_CONTAINER_NAME}}"
MTPROXY_IMAGE="${MTPROXY_IMAGE:-${MTPROXY_IMAGE_DEFAULT}}"

# Variables que se asignan durante la instalación
MTPROXY_PORT=0       # Puerto para el proxy MTProto
MTPROXY_HOSTNAME=""   # Hostname/IP del servidor
MTPROXY_STATE_DIR=""  # Directorio de estado persistente
MTPROXY_SECRET=""     # Secreto generado para MTProto


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
FULL_LOG="$(mktemp -t mtproto_logXXXXXXXXXX)"
LAST_ERROR="$(mktemp -t mtproto_last_errorXXXXXXXXXX)"
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
  #   echo "$@" >> "${SENTRY_LOG_FILE}"
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
  MTPROXY_STATE_DIR="${MTPROXY_DIR}/persisted-state"
  mkdir -p "${MTPROXY_STATE_DIR}"
  chmod ug+rwx,g+s,o-rwx "${MTPROXY_STATE_DIR}"

  # Cambiar propietario al usuario actual no root
  CURRENT_USER=$(get_current_user)
  if [ -n "${CURRENT_USER}" ]; then
    chown -R "${CURRENT_USER}:${CURRENT_USER}" "${MTPROXY_STATE_DIR}"
    echo -e "${GREEN}Permisos de directorio de estado cambiados al usuario: ${CURRENT_USER}${NC}"
  fi
}

function generate_secret_key() {
  # Generar secreto para MTProto (32 caracteres hexadecimales)
  MTPROXY_SECRET="$(head -c 16 /dev/urandom | xxd -ps)"
  readonly MTPROXY_SECRET
}

function write_config() {
    echo "Starting write_config() function"
    local -r CONFIG_FILE="${MTPROXY_STATE_DIR}/mtproto_config.env"
    echo "Writing config to: ${CONFIG_FILE}"

    cat <<-EOF > "${CONFIG_FILE}"
# MTProto Proxy Configuration
MTPROXY_HOSTNAME=${MTPROXY_HOSTNAME}
MTPROXY_PORT=${MTPROXY_PORT}
MTPROXY_SECRET=${MTPROXY_SECRET}
EOF
    echo "Config file written to: ${CONFIG_FILE}"
    echo "write_config() completed successfully"
}

function start_mtproto() {
  echo "Starting start_mtproto() function"
  local -r START_SCRIPT="${MTPROXY_STATE_DIR}/start_container.sh"
  echo "Creating start script at: ${START_SCRIPT}"

  cat <<-EOF > "${START_SCRIPT}"
# This script starts the MTProto proxy container.
# If you need to customize how the proxy is run, you can edit this script, then restart with:
#
#     "${START_SCRIPT}"

set -eu

docker stop "${MTPROXY_CONTAINER_NAME}" 2> /dev/null || true
docker rm -f "${MTPROXY_CONTAINER_NAME}" 2> /dev/null || true

docker_command=(
  docker
  run
  -d
  --name "${MTPROXY_CONTAINER_NAME}" --restart always
  --net host

  # Used by Watchtower to know which containers to monitor.
  --label 'com.centurylinklabs.watchtower.enable=true'

  # Use log rotation. See https://docs.docker.com/config/containers/logging/configure/.
  --log-driver local

  # Mount the persisted state directory
  -v "${MTPROXY_STATE_DIR}:${MTPROXY_STATE_DIR}"

  # The MTProto proxy image to run.
  "${MTPROXY_IMAGE}"
)

# Add MTProto specific arguments
docker_command+=( -H "${MTPROXY_PORT}" -S "${MTPROXY_SECRET}" )

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
  # Set watchtower to refresh every 30 seconds if a custom MTPROXY_IMAGE is used (for
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
function checkMTProtoInstalled() {
  # Verificar si el contenedor MTProto existe y está ejecutándose
  if docker_container_exists "${MTPROXY_CONTAINER_NAME}"; then
    echo "MTProto container '${MTPROXY_CONTAINER_NAME}' exists"
    return 0
  else
    echo "MTProto container '${MTPROXY_CONTAINER_NAME}' not found"
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
    if MTPROXY_HOSTNAME="$(curl --silent --ipv4 "${url}" 2>/dev/null)"; then
      echo "Successfully obtained IP: ${MTPROXY_HOSTNAME}"
      return 0
    else
      echo "Failed to fetch from ${url}"
    fi
  done
  echo -e "${RED}[ERROR] Failed to determine the server's IP address. Try using --hostname <server IP>.${NC}" >&2
  return 1
}

# --- Función Principal de Instalación ---
install_mtproto() {
  local MACHINE_TYPE
  MACHINE_TYPE="$(uname -m)"
  if [[ "${MACHINE_TYPE}" != "x86_64" && "${MACHINE_TYPE}" != "aarch64" && "${MACHINE_TYPE}" != "arm64" ]]; then
    log_error "Unsupported machine type: ${MACHINE_TYPE}. Please run this script on a x86_64, aarch64, or arm64 machine"
    exit 1
  fi

  # Make sure we don't leak readable files to other users.
  umask 0007

  echo "Starting MTProto installation process"
  run_step "Verifying that Docker is installed" verify_docker_installed
  run_step "Verifying that Docker daemon is running" verify_docker_running

  log_for_sentry "Creating MTProto directory"
  echo "Creating MTProto directory: ${MTPROXY_DIR}"
  mkdir -p "${MTPROXY_DIR}"
  chmod u+s,ug+rwx,o-rwx "${MTPROXY_DIR}"

  # Cambiar propietario al usuario actual no root
  CURRENT_USER=$(get_current_user)
  if [ -n "${CURRENT_USER}" ]; then
    chown -R "${CURRENT_USER}:${CURRENT_USER}" "${MTPROXY_DIR}"
    echo -e "${GREEN}Permisos de directorio MTProto cambiados al usuario: ${CURRENT_USER}${NC}"
  fi

  # Asignar puerto después de parse_flags
  MTPROXY_PORT="${FLAGS_PORT}"
  if (( MTPROXY_PORT == 0 )); then
    MTPROXY_PORT=$(get_random_port)
    echo "Generated random port: ${MTPROXY_PORT}"
  else
    echo "Using provided port: ${MTPROXY_PORT}"
  fi
  readonly MTPROXY_PORT

  MTPROXY_HOSTNAME="${FLAGS_HOSTNAME}"
  if [[ -z "${MTPROXY_HOSTNAME}" ]]; then
    run_step "Setting MTPROXY_HOSTNAME to external IP" set_hostname
  else
    echo "Using provided hostname: ${MTPROXY_HOSTNAME}"
  fi
  readonly MTPROXY_HOSTNAME

  # Make a directory for persistent state
  run_step "Creating config directories" create_config_dirs
  run_step "Creating persistent state dir" create_persisted_state_dir
  run_step "Generating secret key" generate_secret_key
  run_step "Writing config" write_config
  echo "write_config completed, proceeding to start MTProto"

  # TODO(dborkan): if the script fails after docker run, it will continue to fail
  # as the names mtproto-proxy and watchtower will already be in use.  Consider
  # deleting the container in the case of failure (e.g. using a trap, or
  # deleting existing containers on each run).
  run_step "Starting MTProto" start_mtproto
  echo "start_mtproto completed, proceeding to start Watchtower"

  # TODO(fortuna): Don't wait for MTProto to run this.
  run_step "Starting Watchtower" start_watchtower
  echo "start_watchtower completed, proceeding to generate env files"

  # Generar archivos .env al finalizar
  generate_env_files
  echo "Env files generated, installation completed successfully"
  echo "MTProto installation process finished"

  # Mensaje final
  echo -e "\n${GREEN}CONGRATULATIONS! Your MTProto proxy is up and running.${NC}"
  echo -e "\n${GREEN}To connect to your proxy, use this link:${NC}"
  echo -e "${GREEN}tg://proxy?server=${MTPROXY_HOSTNAME}&port=${MTPROXY_PORT}&secret=${MTPROXY_SECRET}${NC}"
  echo -e "\n${ORANGE}Remember to open the proxy port ${MTPROXY_PORT} on your firewall.${NC}"
  echo -e "${ORANGE}Client configurations will be stored in: ${HOME_DIR}${NC}"
}



function checkFirewallAndSuggest() {
    local port=$1
    if command -v ufw &> /dev/null && ufw status | grep -q "Status: active"; then
        echo "Firewall (ufw) is active. Checking port ${port}..."
        if ! ufw status | grep -q "${port}"; then
            echo -e "${ORANGE}Warning: Port ${port} does not appear to be allowed in the firewall.${NC}"
            echo -e "To allow traffic on this port, run the following command:"
            echo -e "${GREEN}sudo ufw allow ${port}/tcp${NC}"
        else
            echo -e "${GREEN}Port ${port} appears to be correctly configured in the firewall.${NC}"
        fi
    fi
}

# --- Función de Generación de .env ---
function generate_env_files() {
     echo "Starting generate_env_files() function"
     # Archivo de configuración principal de MTProto
     ENV_FILE_MTPROXY=".env.mtproto.generated"

     echo "Creating ${ENV_FILE_MTPROXY}"
     echo "# --- uSipipo MTProto Server Configuration ---" > "${ENV_FILE_MTPROXY}"
     echo "MTPROXY_HOST=\"${MTPROXY_HOSTNAME}\"" >> "${ENV_FILE_MTPROXY}"
     echo "MTPROXY_PORT=\"${MTPROXY_PORT}\"" >> "${ENV_FILE_MTPROXY}"
     echo "MTPROXY_SECRET=\"${MTPROXY_SECRET}\"" >> "${ENV_FILE_MTPROXY}"
     echo "MTPROXY_DIR=\"${MTPROXY_DIR}\"" >> "${ENV_FILE_MTPROXY}"
     echo "MTPROXY_CONTAINER_NAME=\"${MTPROXY_CONTAINER_NAME}\"" >> "${ENV_FILE_MTPROXY}"
     echo "MTPROXY_IMAGE=\"${MTPROXY_IMAGE}\"" >> "${ENV_FILE_MTPROXY}"
     echo "MTPROXY_STATE_DIR=\"${MTPROXY_STATE_DIR}\"" >> "${ENV_FILE_MTPROXY}"

     echo "# DNS: Using default DNS configuration" >> "${ENV_FILE_MTPROXY}"

     # No se genera TAG aquí, se haría manualmente o mediante otro proceso
     # echo "MTPROXY_TAG=\"\" # Add your tag here if registered with @MTProxybot" >> "${ENV_FILE_MTPROXY}"
     echo "" >> "${ENV_FILE_MTPROXY}"

     echo -e "\n${GREEN}--- VARIABLES MTPROXY PARA TU .env DE USIPIPO ---${NC}"
     echo -e "${ORANGE}Archivo de configuración generado:${NC} ${ENV_FILE_MTPROXY}"
     echo -e "${GREEN}----------------------------------------------------------${NC}"
     echo -e "\n${GREEN}Contenido de ${ENV_FILE_MTPROXY}:${NC}"
     cat "${ENV_FILE_MTPROXY}"
     echo -e "\n${GREEN}----------------------------------------------------------${NC}"
     echo -e "${GREEN}¡Copia estas variables a tu archivo .env de uSipipo!${NC}"
     echo -e "${ORANGE}IMPORTANTE: Guarda las rutas de certificados de forma segura.${NC}"

     # Verificar que las variables críticas estén definidas
     if [[ -z "${MTPROXY_HOSTNAME}" || -z "${MTPROXY_SECRET}" || -z "${MTPROXY_PORT}" ]]; then
        echo -e "${RED}ERROR: Algunas variables críticas no se generaron correctamente${NC}"
        return 1
     fi
     echo "generate_env_files() completed successfully"
}

# --- Función de Desinstalación Completa ---
function uninstallMTProto() {
  echo -e "${RED}WARNING: This will completely remove MTProto proxy and ALL its data!${NC}"
  echo -e "${RED}This action cannot be undone. Make sure to backup your data first.${NC}"
  echo -n "Are you sure you want to continue? [y/N] "
  read -r response
  response=$(echo "${response}" | tr '[:upper:]' '[:lower:]')
  if [[ "${response}" != "y" && "${response}" != "yes" ]]; then
    echo "Uninstallation cancelled."
    exit 0
  fi

  # Detener y remover contenedor Docker
  if docker_container_exists "${MTPROXY_CONTAINER_NAME}"; then
    run_step "Stopping MTProto container" docker stop "${MTPROXY_CONTAINER_NAME}"
    run_step "Removing MTProto container" docker rm -f "${MTPROXY_CONTAINER_NAME}"
  fi

  # Remover imagen Docker si existe
  if docker images | grep -q "telegrammessenger/proxy"; then
    run_step "Removing MTProto Docker image" docker rmi "$(docker images | grep "telegrammessenger/proxy" | awk '{print $3}')"
  fi

  # Remover contenedor watchtower si existe
  if docker_container_exists "watchtower"; then
    remove_watchtower_container
  fi

  # Remover directorios y archivos
  run_step "Removing MTProto installation directory" rm -rf "${MTPROXY_DIR}"
  run_step "Removing MTProto config directories" rm -rf "${HOME_DIR}"

  # Remover archivos .env generados
  rm -f ".env.mtproto.generated"

  # Limpiar archivos temporales
  rm -f "${FULL_LOG}" "${LAST_ERROR}"

  echo -e "\n${GREEN}MTProto proxy has been completely uninstalled and cleaned.${NC}"
}

# --- Funciones de Ayuda y Parseo ---
function display_usage() {
  cat <<EOF
Usage: $0 [options]

Options:
  --install      Install MTProto proxy (default action if not installed)
  --uninstall    Completely remove MTProto proxy and all its data
  --reinstall    Remove existing MTProto installation and reinstall
  --hostname     The hostname to be used for the proxy
  --port         The port number for the proxy
  --help         Display this help message

Environment variables:
  MTPROXY_DIR        MTProto installation directory (default: /opt/mtproto-proxy)
  MTPROXY_IMAGE      Docker image to use (default: telegrammessenger/proxy:latest)
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
  params="$(getopt --longoptions hostname:,port:,install,uninstall,reinstall,help -n "$0" -- "$0" "$@")"
  eval set -- "${params}"

  while (( $# > 0 )); do
    local flag="$1"
    shift
    case "${flag}" in
      --hostname)
        FLAGS_HOSTNAME="$1"
        shift
        ;;
      --port)
        FLAGS_PORT=$1
        shift
        if ! is_valid_port "${FLAGS_PORT}"; then
          log_error "Invalid value for ${flag}: ${FLAGS_PORT}" >&2
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
  return 0
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
      --help)
        display_usage
        exit 0
        ;;
      *)
        # Pass remaining arguments to parse_flags for hostname, port, etc.
        break
        ;;
    esac
  done

  parse_flags "$@"

  case "${ACTION}" in
    "install")
      if checkMTProtoInstalled; then
        log_error "MTProto is already installed. Use --reinstall if you want to reinstall."
        exit 1
      fi
      install_mtproto
      ;;
    "uninstall")
      if ! checkMTProtoInstalled; then
        log_error "MTProto is not installed."
        exit 1
      fi
      uninstallMTProto
      ;;
    "reinstall")
      if checkMTProtoInstalled; then
        echo -e "${ORANGE}MTProto is currently installed. Proceeding with removal first...${NC}"
        uninstallMTProto
      fi
      install_mtproto
      ;;
    "auto")
      if checkMTProtoInstalled; then
        log_error "MTProto is already installed. Use --reinstall to reinstall or --uninstall to remove."
        exit 1
      else
        install_mtproto
      fi
      ;;
  esac
}

main "$@"