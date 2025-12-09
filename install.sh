#!/bin/bash
set -euo pipefail

# =============================================================================
# uSipipo install.sh - Manager / Installer for Outline & WireGuard (official)
# =============================================================================
# Author: uSipipo Team (adapted)
# License: MIT
# Description:
#  - Wrapper to run the official Outline and WireGuard installers (provided in
#    the project root), extract API secrets/keys and persist them into .env
#  - Installs Docker if needed (via menu), shows status/logs and supports
#    uninstall helpers.
# Notes:
#  - Outline will be installed under /opt/outline (official path)
#  - WireGuard will be installed under /etc/wireguard (official path)
#  - .env is written to the project root (SCRIPT_DIR/.env)
# =============================================================================

# =============================================================================
# UI / Colors
# =============================================================================
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly GRAY='\033[0;90m'
readonly NC='\033[0m'

readonly SEPARATOR="═══════════════════════════════════════════════════════════════════════════════"
readonly HEADER_ICON="🛡️"
readonly SUCCESS_ICON="✓"
readonly ERROR_ICON="✗"
readonly INFO_ICON="ℹ"

# =============================================================================
# Paths & Files
# =============================================================================
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$SCRIPT_DIR"
ENV_FILE="$PROJECT_DIR/.env"
EXAMPLE_ENV_FILE="$PROJECT_DIR/example.env"
OL_SCRIPT="$SCRIPT_DIR/ol_server.sh"
WG_SCRIPT="$SCRIPT_DIR/wg_server.sh"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/install_$(date +%Y%m%d_%H%M%S).log"

# =============================================================================
# Helpers: Logging & sudo wrapper
# =============================================================================
log() { echo -e "${BLUE}${INFO_ICON} [INFO]${NC} ${GRAY}$(date '+%F %T')${NC} │ $*" | tee -a "$LOG_FILE"; }
log_ok() { echo -e "${GREEN}${SUCCESS_ICON} [OK]${NC} ${GRAY}$(date '+%F %T')${NC} │ $*" | tee -a "$LOG_FILE"; }
log_warn() { echo -e "${YELLOW}${INFO_ICON} [WARN]${NC} ${GRAY}$(date '+%F %T')${NC} │ $*" | tee -a "$LOG_FILE"; }
log_err() { echo -e "${RED}${ERROR_ICON} [ERR]${NC} ${GRAY}$(date '+%F %T')${NC} │ $*" | tee -a "$LOG_FILE"; }

run_sudo() {
    if [ "$(id -u)" = "0" ]; then
        "$@"
    else
        sudo -E "$@"
    fi
}

confirm() {
    local prompt="${1:-Are you sure?}"
    read -p "${YELLOW}${prompt} [y/N]: ${NC}" ans
    [[ "$ans" =~ ^[Yy]$ ]]
}

get_random_port() {
    shuf -i 20000-55000 -n 1
}

# =============================================================================
# Robust public IP detection (tries metadata, direct IP services, then local iface)
# =============================================================================
get_public_ip() {
    # 1) Cloud metadata (works on many VPS providers)
    ip=$(curl -4 -s --max-time 2 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || true)
    if [[ -n "$ip" ]]; then
        echo "$ip"
        return 0
    fi

    # 2) Direct IP-based endpoints (some providers resolve these without DNS; keep short timeouts)
    ip=$(curl -4 -s --max-time 3 http://4.icanhazip.com 2>/dev/null || true)
    if [[ -n "$ip" ]]; then
        echo "$ip"
        return 0
    fi

    # 3) Regular external services (requires DNS)
    ip=$(curl -4 -s --max-time 3 https://api.ipify.org 2>/dev/null || true)
    if [[ -n "$ip" ]]; then
        echo "$ip"
        return 0
    fi

    # 4) Fallback: detect from primary network interface (eth0 or default route)
    # Try to find interface used for default route
    iface=$(ip route 2>/dev/null | awk '/default/ {print $5; exit}' || true)
    if [[ -z "$iface" ]]; then
        iface="eth0"
    fi
    ip=$(ip -4 addr show dev "$iface" 2>/dev/null | awk '/inet /{print $2}' | cut -d/ -f1 | head -n1 || true)
    if [[ -n "$ip" ]]; then
        echo "$ip"
        return 0
    fi

    # final fallback: empty string (caller must handle)
    echo ""
    return 1
}

# =============================================================================
# .env helpers: preserve user values, update or add keys
# =============================================================================
ensure_env_exists() {
    if [ ! -f "$ENV_FILE" ]; then
        log_warn ".env not found — creating from example if available, otherwise empty."
        if [ -f "$EXAMPLE_ENV_FILE" ]; then
            cp "$EXAMPLE_ENV_FILE" "$ENV_FILE"
        else
            touch "$ENV_FILE"
        fi
    fi
}

# set or update a key in .env (keeps comments intact)
env_set() {
    local key="$1"; local value="$2"
    ensure_env_exists
    # escape slashes for sed replacement
    local esc_value=$(printf '%s\n' "$value" | sed -e 's/[\/&]/\\&/g')
    if grep -qE "^${key}=" "$ENV_FILE"; then
        # replace existing
        sed -i "s/^${key}=.*/${key}=${esc_value}/" "$ENV_FILE"
    else
        # append
        echo "${key}=${value}" >> "$ENV_FILE"
    fi
}

# =============================================================================
# DNS helpers: ensure resolvconf (if present) has sane head; otherwise ensure /etc/resolv.conf
# =============================================================================
fix_dns() {
    # Desired fallback nameservers
    local NS1="1.1.1.1"
    local NS2="8.8.8.8"

    # If resolvconf is installed, populate its head file so generated resolv.conf contains valid entries
    if command -v resolvconf &>/dev/null; then
        log "Ensuring resolvconf head contains fallback nameservers..."
        # create directory if missing
        run_sudo mkdir -p /etc/resolvconf/resolv.conf.d
        # create or update head with our nameservers (preserve if already contains nameserver entries)
        if ! run_sudo grep -qE '^\s*nameserver' /etc/resolvconf/resolv.conf.d/head 2>/dev/null; then
            run_sudo tee /etc/resolvconf/resolv.conf.d/head >/dev/null <<EOF
# uSipipo fallback nameservers (added by install.sh)
nameserver ${NS1}
nameserver ${NS2}
EOF
            log_ok "Wrote /etc/resolvconf/resolv.conf.d/head"
        else
            log "resolvconf head already contains nameserver(s); leaving intact."
        fi

        # Regenerate resolv.conf
        log "Updating resolvconf..."
        run_sudo resolvconf -u || {
            log_warn "resolvconf -u failed or not supported; falling back to writing /etc/resolv.conf directly."
        }
    else
        # If resolvconf not installed (yet), ensure /etc/resolv.conf has sane entries
        if ! grep -qE '^\s*nameserver' /etc/resolv.conf 2>/dev/null; then
            log_warn "/etc/resolv.conf has no nameserver entries — writing fallback nameservers."
            run_sudo tee /etc/resolv.conf >/dev/null <<EOF
# uSipipo fallback resolv.conf
nameserver ${NS1}
nameserver ${NS2}
EOF
            log_ok "Wrote /etc/resolv.conf with fallback nameservers"
        else
            log "Existing /etc/resolv.conf contains nameserver(s); leaving intact."
        fi
    fi
}

# Check DNS resolution and basic connectivity
check_dns() {
    # 1) Quick check: ping a known IP (cloudflare)
    if ! ping -c1 -W2 1.1.1.1 &>/dev/null; then
        log_err "Network connectivity to 1.1.1.1 failed. Check upstream network before proceeding."
        return 1
    fi

    # 2) Check presence of nameserver entries
    if ! grep -qE '^\s*nameserver' /etc/resolv.conf 2>/dev/null; then
        log_warn "/etc/resolv.conf has no nameserver. Attempting to fix DNS."
        fix_dns
    fi

    # 3) Try resolve a domain using getent (no extra deps)
    if getent hosts google.com >/dev/null 2>&1; then
        log_ok "DNS resolution OK (getent)."
        return 0
    fi

    # 4) Fallback: try nslookup if available
    if command -v nslookup &>/dev/null; then
        if nslookup google.com 1.1.1.1 >/dev/null 2>&1; then
            log_ok "DNS resolution OK (nslookup to 1.1.1.1)."
            return 0
        fi
    fi

    # 5) Last attempt: attempt to use curl to fetch a known host (requires DNS)
    if curl -s --head --max-time 3 https://www.google.com >/dev/null 2>&1; then
        log_ok "DNS resolution and HTTP connectivity OK."
        return 0
    fi

    log_warn "DNS resolution still failing after attempts. Forcing fallback resolv.conf and rechecking."
    # Force fallback resolv.conf and recheck
    fix_dns
    sleep 1
    if getent hosts google.com >/dev/null 2>&1 || curl -s --head --max-time 3 https://www.google.com >/dev/null 2>&1; then
        log_ok "DNS fixed using fallback."
        return 0
    fi

    log_err "DNS resolution could not be established. Aborting installation."
    return 1
}

# =============================================================================
# Docker installer (kept lightweight; used by Outline script if needed)
# =============================================================================
install_docker_wrapper() {
    if command -v docker &> /dev/null; then
        log_ok "Docker already installed."
        return 0
    fi

    log "Installing Docker using get.docker.com..."
    run_sudo bash -c "curl -fsSL https://get.docker.com | sh" | tee -a "$LOG_FILE"
    run_sudo systemctl enable --now docker || true
    if command -v docker &> /dev/null; then
        log_ok "Docker installed successfully."
    else
        log_err "Docker installation failed. Please install docker manually."
        return 1
    fi
}

# =============================================================================
# Outline: installer wrapper
# =============================================================================
install_outline() {
    if [ ! -f "$OL_SCRIPT" ]; then
        log_err "Outline installer script not found at: $OL_SCRIPT"
        return 1
    fi

    log_header="🚀 INSTALL OUTLINE (official wrapper)"
    log "$log_header"

    # Ensure Docker
    if ! command -v docker &> /dev/null; then
        log_warn "Docker not found. Installing..."
        install_docker_wrapper || { log_err "Docker is required for Outline. Aborting."; return 1; }
    fi

    # ensure DNS is working before detecting public IP or running the installer
    check_dns || { log_err "DNS check failed. Fix DNS and retry Outline installation."; return 1; }

    local server_ip
    server_ip=$(get_public_ip)
    if [[ -z "$server_ip" ]]; then
        log_warn "Could not auto-detect public IP via metadata/external services. Falling back to primary interface address."
        iface=$(ip route 2>/dev/null | awk '/default/ {print $5; exit}' || true)
        iface=${iface:-eth0}
        server_ip=$(ip -4 addr show dev "$iface" 2>/dev/null | awk '/inet /{print $2}' | cut -d/ -f1 | head -n1 || true)
    fi
    log "Detected public IP: ${server_ip:-<none>}"

    # Choose random ports but allow user override
    local api_port keys_port
    api_port=$(get_random_port)
    keys_port=$(get_random_port)
    # ensure different
    while [ "$keys_port" = "$api_port" ]; do keys_port=$(get_random_port); done

    echo ""
    echo "Outline installation will run with:"
    echo "  Hostname / IP: ${server_ip:-<none>}"
    echo "  API port: $api_port"
    echo "  Keys port: $keys_port"
    echo ""
    if ! confirm "Proceed to run official Outline installer now (interactive prompts may appear)?"; then
        log_warn "User cancelled Outline install."
        return 1
    fi

    # Run official script with chosen args (interactive script will still run)
    log "Running Outline installer script..."
    # run as root, since outline script expects root privileges
    run_sudo bash "$OL_SCRIPT" --hostname "${server_ip:-}" --api-port "$api_port" --keys-port "$keys_port" 2>&1 | tee -a "$LOG_FILE"

    log_ok "Outline installer finished. Attempting to extract API info..."

    # The official script writes access config to SHADOWBOX_DIR/access.txt (default /opt/outline/access.txt)
    local access_file="/opt/outline/access.txt"
    if [ ! -f "$access_file" ]; then
        log_warn "Outline access file not found at ${access_file}. Searching persisted-state..."
        # try persisted-state location used by the script
        if run_sudo test -f /opt/outline/persisted-state/access.txt; then
            access_file="/opt/outline/persisted-state/access.txt"
        fi
    fi

    if [ -f "$access_file" ]; then
        log "Found Outline access file at: $access_file"
        # extract apiUrl and certSha256 lines if present (format "apiUrl:..." "certSha256:...")
        local apiUrl certSha
        apiUrl=$(run_sudo awk -F'apiUrl:' '/apiUrl/{print substr($0, index($0,$2))}' "$access_file" | tr -d '\r' | sed -n '1p' || true)
        certSha=$(run_sudo awk -F'certSha256:' '/certSha256/{print substr($0, index($0,$2))}' "$access_file" | tr -d '\r' | sed -n '1p' || true)
        # sometimes the file uses "apiUrl:..." exact; fallback to grep
        if [ -z "$apiUrl" ]; then
            apiUrl=$(run_sudo grep -E "^apiUrl:" "$access_file" 2>/dev/null | sed 's/^apiUrl://' | tr -d '[:space:]' || true)
        fi
        if [ -z "$certSha" ]; then
            certSha=$(run_sudo grep -E "^certSha256:" "$access_file" 2>/dev/null | sed 's/^certSha256://' | tr -d '[:space:]' || true)
        fi

        # compute server IP and dashboard url
        local outline_server_ip outline_dashboard
        outline_server_ip="${server_ip:-}"
        outline_dashboard="${apiUrl:-}"

        # persist to .env
        if [ -n "$apiUrl" ]; then
            env_set "OUTLINE_API_URL" "$apiUrl"
            log_ok "OUTLINE_API_URL saved"
        else
            log_warn "Could not extract OUTLINE_API_URL from ${access_file}"
        fi
        if [ -n "$certSha" ]; then
            env_set "OUTLINE_CERT_SHA256" "$certSha"
            log_ok "OUTLINE_CERT_SHA256 saved"
        else
            log_warn "Could not extract OUTLINE_CERT_SHA256 from ${access_file}"
        fi

        env_set "OUTLINE_API_PORT" "$api_port"
        env_set "OUTLINE_KEYS_PORT" "$keys_port"
        env_set "OUTLINE_SERVER_IP" "$outline_server_ip"
        env_set "OUTLINE_DASHBOARD_URL" "$outline_dashboard"

        log_ok "Outline variables exported to ${ENV_FILE}"
    else
        log_err "Outline access file not found; manual extraction may be required."
        return 1
    fi
}


# =============================================================================
# WireGuard: installer wrapper
# =============================================================================
install_wireguard() {
    if [ ! -f "$WG_SCRIPT" ]; then
        log_err "WireGuard installer script not found at: $WG_SCRIPT"
        return 1
    fi

    log_header="🚀 INSTALL WIREGUARD (official wrapper)"
    log "$log_header"

    # The official wireguard installer is interactive (asks questions). We'll run it
    # with sudo so it can write to /etc/wireguard and then extract params file.
    echo ""
    log "The WireGuard installer is interactive. It will ask a few questions (interface, IPs, port)."

    if ! confirm "Proceed to run official WireGuard installer now?"; then
        log_warn "User cancelled WireGuard install."
        return 1
    fi

    # Ensure DNS is sane before running the installer (resolvconf may be installed by the wg script,
    # but we proactively ensure we have fallback nameservers so server doesn't lose DNS).
    fix_dns
    check_dns || { log_err "DNS check failed. Fix DNS and retry WireGuard installation."; return 1; }

    # Run official installer (interactive)
    run_sudo bash "$WG_SCRIPT" 2>&1 | tee -a "$LOG_FILE"

    # After installation, the official script writes /etc/wireguard/params
    local params_file="/etc/wireguard/params"
    if run_sudo test -f "$params_file"; then
        log_ok "WireGuard params found: $params_file"
        # source the params (use a subshell to avoid polluting environment)
        local WG_SERVER_PUB_IP WG_SERVER_PUB_NIC WG_SERVER_WG_NIC WG_SERVER_WG_IPV4 WG_SERVER_WG_IPV6 WG_SERVER_PORT WG_SERVER_PRIV_KEY WG_SERVER_PUB_KEY CLIENT_DNS_1 CLIENT_DNS_2 ALLOWED_IPS
        # read values safely
        WG_SERVER_PUB_IP=$(run_sudo awk -F'=' '/^SERVER_PUB_IP=/{print $2}' "$params_file" | tr -d '"' || true)
        WG_SERVER_PUB_NIC=$(run_sudo awk -F'=' '/^SERVER_PUB_NIC=/{print $2}' "$params_file" | tr -d '"' || true)
        WG_SERVER_WG_NIC=$(run_sudo awk -F'=' '/^SERVER_WG_NIC=/{print $2}' "$params_file" | tr -d '"' || true)
        WG_SERVER_WG_IPV4=$(run_sudo awk -F'=' '/^SERVER_WG_IPV4=/{print $2}' "$params_file" | tr -d '"' || true)
        WG_SERVER_WG_IPV6=$(run_sudo awk -F'=' '/^SERVER_WG_IPV6=/{print $2}' "$params_file" | tr -d '"' || true)
        WG_SERVER_PORT=$(run_sudo awk -F'=' '/^SERVER_PORT=/{print $2}' "$params_file" | tr -d '"' || true)
        WG_SERVER_PRIV_KEY=$(run_sudo awk -F'=' '/^SERVER_PRIV_KEY=/{print $2}' "$params_file" | tr -d '"' || true)
        WG_SERVER_PUB_KEY=$(run_sudo awk -F'=' '/^SERVER_PUB_KEY=/{print $2}' "$params_file" | tr -d '"' || true)
        CLIENT_DNS_1=$(run_sudo awk -F'=' '/^CLIENT_DNS_1=/{print $2}' "$params_file" | tr -d '"' || true)
        CLIENT_DNS_2=$(run_sudo awk -F'=' '/^CLIENT_DNS_2=/{print $2}' "$params_file" | tr -d '"' || true)
        ALLOWED_IPS=$(run_sudo awk -F'=' '/^ALLOWED_IPS=/{print $2}' "$params_file" | tr -d '"' || true)

        # Write into .env
        [ -n "$WG_SERVER_WG_NIC" ] && env_set "WG_INTERFACE" "$WG_SERVER_WG_NIC"
        [ -n "$WG_SERVER_WG_IPV4" ] && env_set "WG_SERVER_IPV4" "$WG_SERVER_WG_IPV4"
        [ -n "$WG_SERVER_WG_IPV6" ] && env_set "WG_SERVER_IPV6" "$WG_SERVER_WG_IPV6"
        [ -n "$WG_SERVER_PORT" ] && env_set "WG_SERVER_PORT" "$WG_SERVER_PORT"
        [ -n "$WG_SERVER_PUB_KEY" ] && env_set "WG_SERVER_PUBKEY" "$WG_SERVER_PUB_KEY"
        [ -n "$WG_SERVER_PRIV_KEY" ] && env_set "WG_SERVER_PRIVKEY" "$WG_SERVER_PRIV_KEY"
        [ -n "$ALLOWED_IPS" ] && env_set "WG_ALLOWED_IPS" "$ALLOWED_IPS"

        # If the wg params provided DNS for clients, preserve them; otherwise use server resolv.conf
        if [ -n "$CLIENT_DNS_1" ]; then
            env_set "WG_CLIENT_DNS_1" "$CLIENT_DNS_1"
            log_ok "Using CLIENT_DNS_1 from wg params: $CLIENT_DNS_1"
        else
            # try to obtain server DNS from /etc/resolv.conf
            server_dns=$(grep -E '^\s*nameserver' /etc/resolv.conf | awk '{print $2}' | head -n1 || true)
            if [ -n "$server_dns" ]; then
                env_set "WG_CLIENT_DNS_1" "$server_dns"
                log_ok "Set WG_CLIENT_DNS_1 to server DNS from /etc/resolv.conf: $server_dns"
            else
                env_set "WG_CLIENT_DNS_1" "1.1.1.1"
                log_warn "No DNS found in /etc/resolv.conf; defaulting WG_CLIENT_DNS_1 to 1.1.1.1"
            fi
        fi

        if [ -n "$CLIENT_DNS_2" ]; then
            env_set "WG_CLIENT_DNS_2" "$CLIENT_DNS_2"
        else
            server_dns2=$(grep -E '^\s*nameserver' /etc/resolv.conf | awk '{print $2}' | sed -n '2p' || true)
            if [ -n "$server_dns2" ]; then
                env_set "WG_CLIENT_DNS_2" "$server_dns2"
            else
                env_set "WG_CLIENT_DNS_2" "8.8.8.8"
            fi
        fi

        # Compute endpoint from public IP detection if not present (avoid 127.0.0.1)
        local server_ip
        server_ip=$(get_public_ip)
        if [[ -z "$server_ip" ]]; then
            log_warn "get_public_ip returned empty; falling back to interface IP for SERVER_IP."
            iface=$(ip route 2>/dev/null | awk '/default/ {print $5; exit}' || true)
            iface=${iface:-eth0}
            server_ip=$(ip -4 addr show dev "$iface" 2>/dev/null | awk '/inet /{print $2}' | cut -d/ -f1 | head -n1 || true)
        fi

        if [[ -n "$server_ip" ]]; then
            env_set "SERVER_IP" "$server_ip"
            if [ -n "$WG_SERVER_PORT" ]; then
                env_set "WG_ENDPOINT" "${server_ip}:${WG_SERVER_PORT}"
            else
                log_warn "WG_SERVER_PORT empty; WG_ENDPOINT not set."
            fi
        else
            log_err "Could not determine SERVER_IP; leaving SERVER_IP and WG_ENDPOINT unset."
        fi

        log_ok "WireGuard variables exported to ${ENV_FILE}"
    else
        log_err "WireGuard params file not found at /etc/wireguard/params. Installation may have failed."
        return 1
    fi
}

# =============================================================================
# Extract (re-extract) variables from existing installs (non-destructive)
# =============================================================================
extract_vpn_vars() {
    log "Extracting variables from existing installations..."

    # Outline extraction (attempt)
    local access_file="/opt/outline/access.txt"
    if run_sudo test -f "$access_file"; then
        log "Reading Outline access file..."
        local apiUrl certSha
        apiUrl=$(run_sudo grep -E "^apiUrl:" "$access_file" 2>/dev/null | sed 's/^apiUrl://' | tr -d '[:space:]' || true)
        certSha=$(run_sudo grep -E "^certSha256:" "$access_file" 2>/dev/null | sed 's/^certSha256://' | tr -d '[:space:]' || true)

        [ -n "$apiUrl" ] && env_set "OUTLINE_API_URL" "$apiUrl"
        [ -n "$certSha" ] && env_set "OUTLINE_CERT_SHA256" "$certSha"

        # also try persisted-state location
        if run_sudo test -f /opt/outline/persisted-state/shadowbox_server_config.json; then
            local cfg="/opt/outline/persisted-state/shadowbox_server_config.json"
            # extract hostname and portForNewAccessKeys
            local hostname portForNewAccessKeys
            hostname=$(run_sudo jq -r '.hostname' "$cfg" 2>/dev/null || true)
            portForNewAccessKeys=$(run_sudo jq -r '.portForNewAccessKeys' "$cfg" 2>/dev/null || true)
            [ -n "$hostname" ] && env_set "OUTLINE_SERVER_IP" "$hostname"
            [ -n "$portForNewAccessKeys" ] && env_set "OUTLINE_KEYS_PORT" "$portForNewAccessKeys"
        fi
    else
        log_warn "Outline access file not found at ${access_file}"
    fi

    # WireGuard extraction (params)
    local params_file="/etc/wireguard/params"
    if run_sudo test -f "$params_file"; then
        log "Reading WireGuard params..."
        # reuse extraction code from installer
        install_wireguard_extract_only
    else
        log_warn "WireGuard params file not found at ${params_file}"
    fi

    log_ok "Extraction completed."
}

install_wireguard_extract_only() {
    local params_file="/etc/wireguard/params"
    if ! run_sudo test -f "$params_file"; then
        return 1
    fi
    local WG_SERVER_WG_NIC WG_SERVER_WG_IPV4 WG_SERVER_WG_IPV6 WG_SERVER_PORT WG_SERVER_PRIV_KEY WG_SERVER_PUB_KEY CLIENT_DNS_1 CLIENT_DNS_2 ALLOWED_IPS
    WG_SERVER_WG_NIC=$(run_sudo awk -F'=' '/^SERVER_WG_NIC=/{print $2}' "$params_file" | tr -d '"' || true)
    WG_SERVER_WG_IPV4=$(run_sudo awk -F'=' '/^SERVER_WG_IPV4=/{print $2}' "$params_file" | tr -d '"' || true)
    WG_SERVER_WG_IPV6=$(run_sudo awk -F'=' '/^SERVER_WG_IPV6=/{print $2}' "$params_file" | tr -d '"' || true)
    WG_SERVER_PORT=$(run_sudo awk -F'=' '/^SERVER_PORT=/{print $2}' "$params_file" | tr -d '"' || true)
    WG_SERVER_PRIV_KEY=$(run_sudo awk -F'=' '/^SERVER_PRIV_KEY=/{print $2}' "$params_file" | tr -d '"' || true)
    WG_SERVER_PUB_KEY=$(run_sudo awk -F'=' '/^SERVER_PUB_KEY=/{print $2}' "$params_file" | tr -d '"' || true)
    CLIENT_DNS_1=$(run_sudo awk -F'=' '/^CLIENT_DNS_1=/{print $2}' "$params_file" | tr -d '"' || true)
    CLIENT_DNS_2=$(run_sudo awk -F'=' '/^CLIENT_DNS_2=/{print $2}' "$params_file" | tr -d '"' || true)
    ALLOWED_IPS=$(run_sudo awk -F'=' '/^ALLOWED_IPS=/{print $2}' "$params_file" | tr -d '"' || true)

    [ -n "$WG_SERVER_WG_NIC" ] && env_set "WG_INTERFACE" "$WG_SERVER_WG_NIC"
    [ -n "$WG_SERVER_WG_IPV4" ] && env_set "WG_SERVER_IPV4" "$WG_SERVER_WG_IPV4"
    [ -n "$WG_SERVER_WG_IPV6" ] && env_set "WG_SERVER_IPV6" "$WG_SERVER_WG_IPV6"
    [ -n "$WG_SERVER_PORT" ] && env_set "WG_SERVER_PORT" "$WG_SERVER_PORT"
    [ -n "$WG_SERVER_PUB_KEY" ] && env_set "WG_SERVER_PUBKEY" "$WG_SERVER_PUB_KEY"
    [ -n "$WG_SERVER_PRIV_KEY" ] && env_set "WG_SERVER_PRIVKEY" "$WG_SERVER_PRIV_KEY"
    [ -n "$ALLOWED_IPS" ] && env_set "WG_ALLOWED_IPS" "$ALLOWED_IPS"
    [ -n "$CLIENT_DNS_1" ] && env_set "WG_CLIENT_DNS_1" "$CLIENT_DNS_1"
    [ -n "$CLIENT_DNS_2" ] && env_set "WG_CLIENT_DNS_2" "$CLIENT_DNS_2"

    # ensure SERVER_IP and WG_ENDPOINT
    local server_ip
    server_ip=$(get_public_ip)
    if [[ -z "$server_ip" ]]; then
        iface=$(ip route 2>/dev/null | awk '/default/ {print $5; exit}' || true)
        iface=${iface:-eth0}
        server_ip=$(ip -4 addr show dev "$iface" 2>/dev/null | awk '/inet /{print $2}' | cut -d/ -f1 | head -n1 || true)
    fi
    if [[ -n "$server_ip" ]]; then
        env_set "SERVER_IP" "$server_ip"
        if [ -n "$WG_SERVER_PORT" ]; then
            env_set "WG_ENDPOINT" "${server_ip}:${WG_SERVER_PORT}"
        fi
    else
        log_warn "Could not determine public IP during extraction."
    fi

    return 0
}

# =============================================================================
# Status & logs helpers
# =============================================================================
vpn_status() {
    log_header="📊 VPN STATUS"
    log "$log_header"
    # Outline container (shadowbox)
    if command -v docker &> /dev/null; then
        if docker ps --format '{{.Names}}' | grep -qw shadowbox; then
            docker ps --filter name=shadowbox --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        else
            log_warn "Outline (shadowbox) container not running or not present."
        fi
    else
        log_warn "Docker not installed, cannot show Outline status."
    fi

    # WireGuard service
    if systemctl list-units --type=service --all | grep -q 'wg-quick@'; then
        systemctl status --no-pager 'wg-quick@*' || true
    else
        # try to detect wg-quick@<iface>
        if run_sudo systemctl is-active --quiet "wg-quick@wg0" 2>/dev/null; then
            systemctl status --no-pager wg-quick@wg0 || true
        else
            log_warn "WireGuard service (wg-quick@...) not active or not installed via systemd."
        fi
    fi
}

vpn_logs() {
    echo ""
    echo "Select logs to view:"
    echo "  1) Outline container logs (shadowbox)"
    echo "  2) Watchtower logs"
    echo "  3) WireGuard syslogs / systemctl (wg-quick)"
    echo "  4) Tail install logs (this script)"
    read -p "Choice [1-4]: " ch
    case "$ch" in
        1)
            if docker ps --format '{{.Names}}' | grep -qw shadowbox; then
                docker logs --tail 200 shadowbox
            else
                log_warn "shadowbox container not found."
            fi
            ;;
        2)
            if docker ps --format '{{.Names}}' | grep -qw watchtower; then
                docker logs --tail 200 watchtower
            else
                log_warn "watchtower container not found."
            fi
            ;;
        3)
            # show recent syslog for wg-quick if available
            journalctl -u "wg-quick@*" --no-pager -n 200 || journalctl -t wg-quick --no-pager -n 200 || log_warn "No wg logs found"
            ;;
        4)
            tail -n 200 "$LOG_FILE"
            ;;
        *)
            log_warn "Invalid choice"
            ;;
    esac
}

# =============================================================================
# Uninstall helpers (best-effort)
# =============================================================================
uninstall_outline() {
    log "Removing Outline containers & persisted state (best-effort)."
    if docker ps --format '{{.Names}}' | grep -qw shadowbox; then
        run_sudo docker rm -f shadowbox || true
    fi
    if docker ps --format '{{.Names}}' | grep -qw watchtower; then
        run_sudo docker rm -f watchtower || true
    fi
    run_sudo rm -rf /opt/outline || true
    log_ok "Outline removed (files at /opt/outline deleted)."
}

uninstall_wireguard() {
    log "Attempting to uninstall WireGuard (best-effort)."
    if run_sudo test -f "$WG_SCRIPT"; then
        # try to run uninstall flow inside script if available
        log "If your wg installer provides an uninstall option, run it manually."
    fi
    run_sudo rm -rf /etc/wireguard || true
    run_sudo rm -f /etc/sysctl.d/wg.conf || true
    log_ok "WireGuard files removed from /etc/wireguard (manual cleanup may still be required)."
}

# =============================================================================
# Configuración de Permisos para el Bot (uSipipoVPNBot)
# =============================================================================
configure_bot_permissions() {
    log_ok "🛡️ Configurando permisos de WireGuard para el bot"
    
    
    # Determinar el usuario que está ejecutando el script
    BOT_USER=${SUDO_USER:-$(whoami)}
    WG_PATH="/etc/wireguard" # Ruta por defecto de WireGuard

    log "Usuario del bot identificado: ${BOT_USER}"
    
    if [ "${BOT_USER}" = "root" ]; then
        log_warn "El bot se está ejecutando como 'root'. NO se modificará el sudoers, pero se asegurará la carpeta."
    else
        # 1. Añadir reglas NOPASSWD para los comandos críticos de WireGuard
        log "Añadiendo reglas NOPASSWD para ${BOT_USER} en sudoers..."

        SUDOERS_FILE="/etc/sudoers.d/usipipo_wg_bot"

        cat > "$SUDOERS_FILE" <<EOF
# Permisos de WireGuard para el bot ${BOT_USER}
${BOT_USER} ALL=(root) NOPASSWD: /usr/bin/mkdir -p /etc/wireguard/clients
${BOT_USER} ALL=(root) NOPASSWD: /usr/bin/chown -R * /etc/wireguard/clients
${BOT_USER} ALL=(root) NOPASSWD: /usr/bin/wg set *
${BOT_USER} ALL=(root) NOPASSWD: /usr/bin/wg show *
EOF
        # Establecer permisos seguros para el archivo sudoers
        run_sudo chmod 0440 "$SUDOERS_FILE"
        log_ok "Reglas de NOPASSWD añadidas a ${SUDOERS_FILE}."
    fi

    # 2. Asegurar que el directorio de clientes existe y es propiedad del BOT_USER
    log "Asegurando el directorio de clientes: ${WG_PATH}/clients"
    
    # Crear la carpeta con run_sudo 
    run_sudo mkdir -p "${WG_PATH}/clients"
    
    # Dar propiedad al usuario del bot.
    run_sudo chown -R "${BOT_USER}:${BOT_USER}" "${WG_PATH}/clients"

    log_ok "✔ Permisos y directorios de WireGuard configurados correctamente."
    
}

# =============================================================================
# Menu
# =============================================================================
show_menu() {
    clear
    echo -e "${CYAN}${SEPARATOR}${NC}"
    echo -e "${WHITE}              ${HEADER_ICON} uSipipo Installer & Manager ${HEADER_ICON}${NC}"
    echo -e "${CYAN}${SEPARATOR}${NC}"
    echo ""
    echo -e "  ${GREEN}1)${NC} 🐳 Install Docker (helper)"
    echo -e "  ${GREEN}2)${NC} ⚙️  Install Outline Server (official)"
    echo -e "  ${GREEN}3)${NC} ⚙️  Install WireGuard Server (official)"
    echo -e "  ${BLUE}4)${NC} 🔁  Extract / Sync VPN variables into .env"
    echo -e "  ${PURPLE}5)${NC} 📊  VPN Status"
    echo -e "  ${YELLOW}6)${NC} 📄  View VPN Logs"
    echo -e "  ${RED}7)${NC} 🧹  Uninstall Outline (best-effort)"
    echo -e "  ${RED}8)${NC} 🧹  Uninstall WireGuard (best-effort)"
    echo -e "  ${WHITE}9)${NC} ❓  Show .env"
    echo -e "  ${WHITE}0)${NC} Exit"
    echo ""
    read -p "$(echo -e ${WHITE}Select option [0-9]:${NC} )" choice

    case "$choice" in
        1) install_docker_wrapper ;;
        2) install_outline ;;
        3) 
            install_wireguard
            configure_bot_permissions
            ;;
        4) extract_vpn_vars ;;
        5) vpn_status ;;
        6) vpn_logs ;;
        7) uninstall_outline ;;
        8) uninstall_wireguard ;;
        9)
            ensure_env_exists
            echo ""
            echo "----- $ENV_FILE -----"
            sed -n '1,200p' "$ENV_FILE" || true
            echo "---------------------"
            ;;
        0) log "Exiting."; exit 0 ;;
        *) log_err "Invalid option"; sleep 1 ;;
    esac

    echo ""
    read -p "Press Enter to continue..." dummy
    show_menu
}


# =============================================================================
# Bootstrap: ensure example.env exists (create from template if missing)
# =============================================================================
bootstrap() {
    # if example.env missing, write a helpful template skeleton (minimal)
    if [ ! -f "$EXAMPLE_ENV_FILE" ]; then
        cat > "$EXAMPLE_ENV_FILE" <<'EOF'
# example.env - minimal template (uSipipo)
TELEGRAM_TOKEN=
AUTHORIZED_USERS=
SERVER_IPV4=
SERVER_IPV6=
SERVER_IP=
WG_INTERFACE=
WG_SERVER_IPV4=
WG_SERVER_IPV6=
WG_SERVER_PORT=
WG_SERVER_PUBKEY=
WG_SERVER_PRIVKEY=
WG_ALLOWED_IPS=
WG_PATH=/etc/wireguard
WG_ENDPOINT=
OUTLINE_API_URL=
OUTLINE_CERT_SHA256=
OUTLINE_API_PORT=
OUTLINE_KEYS_PORT=
OUTLINE_SERVER_IP=
OUTLINE_DASHBOARD_URL=
LOG_LEVEL=info
NODE_ENV=production
EOF
        log "Created example.env template."
    fi
    ensure_env_exists
}

# =============================================================================
# Main
# =============================================================================
main() {
    bootstrap
    show_menu
}

main "$@"
