#!/bin/bash

# =============================================================================
# Module: Shared Utilities (Core Library)
# Location: modules/utils.sh
# Description: Centralized library for logging, UI, network, and crypto helpers.
# =============================================================================

# -----------------------------------------------------------------------------
# 1. UI & Colors Definition
# -----------------------------------------------------------------------------
export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export BLUE='\033[0;34m'
export PURPLE='\033[0;35m'
export CYAN='\033[0;36m'
export GRAY='\033[0;90m'
export WHITE='\033[1;37m'
export NC='\033[0m' # No Color

# UI Elements
export SEPARATOR="═══════════════════════════════════════════════════════════════════════════════"
export INFO_ICON="ℹ"
export SUCCESS_ICON="✓"
export WARNING_ICON="⚠"
export ERROR_ICON="✗"
export STEP_ICON="▶"

# -----------------------------------------------------------------------------
# 2. Logging System
# -----------------------------------------------------------------------------
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/install_$(date +%Y%m%d).log"

_log_to_file() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local clean_message=$(echo -e "$message" | sed 's/\x1b\[[0-9;]*m//g')
    echo "[$timestamp] [$level] $clean_message" >> "$LOG_FILE"
}

log_header() {
    echo -e "\n${CYAN}${SEPARATOR}${NC}"
    echo -e "${WHITE}  $1${NC}"
    echo -e "${CYAN}${SEPARATOR}${NC}\n"
    _log_to_file "HEADER" "$1"
}

log_info() {
    echo -e "${BLUE}${INFO_ICON} [INFO]${NC} $1"
    _log_to_file "INFO" "$1"
}

log_success() {
    echo -e "${GREEN}${SUCCESS_ICON} [OK]${NC}   $1"
    _log_to_file "SUCCESS" "$1"
}

log_warning() {
    echo -e "${YELLOW}${WARNING_ICON} [WARN]${NC} $1"
    _log_to_file "WARNING" "$1"
}

log_error() {
    echo -e "${RED}${ERROR_ICON} [ERR]${NC}  $1" >&2
    _log_to_file "ERROR" "$1"
}

log_step() {
    local current="$1"
    local total="$2"
    local msg="$3"
    echo -e "${PURPLE}${STEP_ICON} [STEP $current/$total]${NC} ${WHITE}$msg${NC}"
    _log_to_file "STEP" "($current/$total) $msg"
}

# -----------------------------------------------------------------------------
# 3. System & Docker Helpers
# -----------------------------------------------------------------------------

# Execute commands with sudo only if needed
run_sudo() {
    if [ "$EUID" -eq 0 ]; then 
        "$@"
    else 
        sudo -E "$@"
    fi
}

# Determine Docker Command (sudoless vs sudo)
get_docker_cmd() {
    if groups | grep -q "docker"; then
        echo "docker"
    else
        echo "run_sudo docker"
    fi
}

# -----------------------------------------------------------------------------
# 4. Network Helpers
# -----------------------------------------------------------------------------

get_public_ip() {
    local ip=""
    # Try multiple services
    ip=$(curl -4 -s --connect-timeout 3 ifconfig.co 2>/dev/null)
    
    if [[ -z "$ip" ]]; then
        ip=$(curl -4 -s --connect-timeout 3 icanhazip.com 2>/dev/null)
    fi
    
    if [[ -z "$ip" ]]; then
        ip=$(curl -4 -s --connect-timeout 3 ipinfo.io/ip 2>/dev/null)
    fi
    
    # Validate IPv4 format
    if [[ "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "$ip"
    else
        log_warning "Could not auto-detect public IP. Falling back to 127.0.0.1" >&2
        echo "127.0.0.1"
    fi
}

# -----------------------------------------------------------------------------
# 5. Generator Helpers (Ports & Secrets)
# -----------------------------------------------------------------------------

# Usage: generate_secret [length]
generate_secret() {
    local length="${1:-32}"
    # Use urandom for secure generation
    tr -dc 'a-zA-Z0-9' </dev/urandom | head -c "$length"
}

# Usage: get_random_port [excluded_port1] [excluded_port2]...
get_random_port() {
    local port=0
    local valid=false
    local excluded_ports=("$@")

    while [ "$valid" = false ]; do
        # Generate range 10000-60000
        port=$((10000 + RANDOM % 50000))
        valid=true
        
        # Check standard reserved ports
        if [[ "$port" -eq 80 || "$port" -eq 443 || "$port" -eq 53 || "$port" -eq 22 ]]; then
            valid=false
            continue
        fi

        # Check against provided exclusions
        for excluded in "${excluded_ports[@]}"; do
            if [[ "$port" -eq "$excluded" ]]; then
                valid=false
                break
            fi
        done
    done
    echo "$port"
}

# -----------------------------------------------------------------------------
# 6. Error Handling
# -----------------------------------------------------------------------------

cleanup_on_interrupt() {
    echo -e "\n"
    log_warning "Script interrupted by user."
    exit 130
}
trap cleanup_on_interrupt SIGINT
