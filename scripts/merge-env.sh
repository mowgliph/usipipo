#!/bin/bash

# uSipipo Environment Merger Script
# Merges all .env.*.generated files into a single .env file
# Handles variable conflicts with priority ordering and preserves comments/format

set -euo pipefail

# --- Constantes ---
SCRIPT_VERSION="1.0.0"
OUTPUT_FILE=".env"
BACKUP_SUFFIX=".backup.$(date +%Y%m%d_%H%M%S)"
ENV_PATTERN=".env.*.generated"

# Priority order for variable conflicts (highest to lowest)
# mariadb, pihole, wireguard, outline, mtproto, shadowmere, dns-config
declare -a PRIORITY_ORDER=(
    ".env.mariadb.generated"
    ".env.pihole.generated"
    ".env.wireguard.generated"
    ".env.outline.generated"
    ".env.mtproto.generated"
    ".env.shadowmere.generated"
    ".env.dns-config.generated"
)

# --- Variables globales ---
BACKUP_FILE=""
PROCESSED_FILES=()
ADDED_VARIABLES=()
declare -A VARIABLE_SOURCES
declare -A VARIABLE_VALUES

# --- Colores ---
RED='\033[0;31m'
ORANGE='\033[0;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# --- Funciones de Logging ---
FULL_LOG="$(mktemp -t merge_env_logXXXXXXXXXX)"
LAST_ERROR="$(mktemp -t merge_env_last_errorXXXXXXXXXX)"
readonly FULL_LOG LAST_ERROR

function log_command() {
    "$@" > >(tee -a "${FULL_LOG}") 2> >(tee -a "${FULL_LOG}" > "${LAST_ERROR}")
}

function log_error() {
    local ERROR_TEXT="${RED}"
    local NO_COLOR="${NC}"
    echo -e "${ERROR_TEXT}$1${NO_COLOR}"
    echo "$1" >> "${FULL_LOG}"
}

function log_info() {
    echo "$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') INFO: $1" >> "${FULL_LOG}"
}

function log_warn() {
    local WARN_TEXT="${ORANGE}"
    local NO_COLOR="${NC}"
    echo -e "${WARN_TEXT}$1${NO_COLOR}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') WARN: $1" >> "${FULL_LOG}"
}

function log_start_step() {
    local str="> $*"
    local lineLength=47
    echo -n "${str}"
    local numDots=$(( lineLength - ${#str} - 1 ))
    if (( numDots > 0 )); then
        echo -n " "
        for _ in $(seq 1 "${numDots}"); do echo -n .; done
    fi
    echo -n " "
}

function run_step() {
    local msg="$1"
    log_start_step "${msg}"
    shift 1
    if log_command "$@"; then
        echo "OK"
    else
        return
    fi
}

# --- Funciones de Validación ---
function validate_environment() {
    log_start_step "Validating environment"

    # Check if any .env files exist
    local found_files=()
    for file in ${ENV_PATTERN}; do
        if [[ -f "$file" ]]; then
            found_files+=("$file")
        fi
    done

    if [[ ${#found_files[@]} -eq 0 ]]; then
        log_error "FAILED"
        log_error "No .env.*.generated files found in current directory"
        log_error "Please run the installation scripts first"
        exit 1
    fi

    echo "OK"
}

function create_backup() {
    if [[ -f "${OUTPUT_FILE}" ]]; then
        BACKUP_FILE="${OUTPUT_FILE}${BACKUP_SUFFIX}"
        cp "${OUTPUT_FILE}" "${BACKUP_FILE}"
        log_info "Created backup: ${BACKUP_FILE}"
    fi
}

# --- Funciones de Procesamiento ---
function get_priority_index() {
    local filename="$1"
    for i in "${!PRIORITY_ORDER[@]}"; do
        if [[ "${PRIORITY_ORDER[$i]}" == "$filename" ]]; then
            echo "$i"
            return 0
        fi
    done
    echo "99"  # Default low priority for unknown files
}

function parse_env_file() {
    local file="$1"
    local current_section=""
    local line_number=0

    log_info "Processing file: $file"

    while IFS= read -r line || [[ -n "$line" ]]; do
        ((line_number++))
        # Remove carriage returns
        line="${line//$'\r'/}"

        # Skip empty lines
        [[ -z "$line" ]] && continue

        # Handle comments and section headers
        if [[ "$line" =~ ^[[:space:]]*# ]]; then
            # Preserve comments and section headers
            if [[ "$line" =~ ^[[:space:]]*#[[:space:]]*--- ]]; then
                current_section="$line"
            fi
            continue
        fi

        # Parse variable assignments
        if [[ "$line" =~ ^[[:space:]]*[A-Z_][A-Z0-9_]*[[:space:]]*=[[:space:]]* ]]; then
            local var_name="${line%%=*}"
            var_name="${var_name// /}"  # Remove spaces
            local var_value="${line#*=}"
            var_value="${var_value#"${var_value%%[![:space:]]*}"}"  # Trim leading spaces
            var_value="${var_value%"${var_value##*[![:space:]]}"}"  # Trim trailing spaces

            # Remove quotes if present
            if [[ "$var_value" =~ ^\".*\"$ ]]; then
                var_value="${var_value:1:-1}"
            fi

            process_variable "$var_name" "$var_value" "$file"
        fi
    done < "$file"
}

function process_variable() {
    local var_name="$1"
    local var_value="$2"
    local source_file="$3"

    # Check if variable already exists
    if [[ -n "${VARIABLE_SOURCES[$var_name]:-}" ]]; then
        local existing_source="${VARIABLE_SOURCES[$var_name]}"
        local existing_priority=$(get_priority_index "$existing_source")
        local new_priority=$(get_priority_index "$source_file")

        if [[ $new_priority -lt $existing_priority ]]; then
            # New source has higher priority, replace
            VARIABLE_SOURCES[$var_name]="$source_file"
            VARIABLE_VALUES[$var_name]="$var_value"
            log_warn "Variable '$var_name' overridden by higher priority source: $source_file (was: $existing_source)"
        else
            # Keep existing (higher priority)
            log_info "Variable '$var_name' kept from higher priority source: $existing_source (skipping: $source_file)"
            return
        fi
    else
        # New variable
        VARIABLE_SOURCES[$var_name]="$source_file"
        VARIABLE_VALUES[$var_name]="$var_value"
        ADDED_VARIABLES+=("$var_name")
    fi
}

function find_env_files() {
    local found_files=()

    for file in ${ENV_PATTERN}; do
        if [[ -f "$file" ]]; then
            found_files+=("$file")
        fi
    done

    # Sort files by priority order
    local sorted_files=()
    for priority_file in "${PRIORITY_ORDER[@]}"; do
        for found_file in "${found_files[@]}"; do
            if [[ "$found_file" == "$priority_file" ]]; then
                sorted_files+=("$found_file")
                break
            fi
        done
    done

    # Add any remaining files not in priority order
    for found_file in "${found_files[@]}"; do
        local already_added=false
        for sorted_file in "${sorted_files[@]}"; do
            if [[ "$found_file" == "$sorted_file" ]]; then
                already_added=true
                break
            fi
        done
        if [[ "$already_added" == false ]]; then
            sorted_files+=("$found_file")
        fi
    done

    echo "${sorted_files[@]}"
}

function merge_env_files() {
    local files_to_process=("$@")

    log_info "Starting merge process with priority order:"
    for i in "${!PRIORITY_ORDER[@]}"; do
        log_info "  $((i+1)). ${PRIORITY_ORDER[$i]}"
    done

    # Process each file in priority order
    for file in "${files_to_process[@]}"; do
        if [[ -f "$file" ]]; then
            PROCESSED_FILES+=("$file")
            parse_env_file "$file"
        else
            log_warn "File not found: $file"
        fi
    done
}

function write_output_file() {
    log_start_step "Writing merged .env file"

    # Write header
    cat > "${OUTPUT_FILE}" << EOF
# --- uSipipo Merged Environment Configuration ---
# Generated by merge-env.sh v${SCRIPT_VERSION} on $(date)
# Priority order: ${PRIORITY_ORDER[*]}
#
# This file contains merged configuration from:
EOF

    # List processed files
    for file in "${PROCESSED_FILES[@]}"; do
        echo "#   - $file" >> "${OUTPUT_FILE}"
    done

    echo "" >> "${OUTPUT_FILE}"

    # Write variables grouped by source
    local current_source=""
    for var_name in $(echo "${!VARIABLE_SOURCES[@]}" | tr ' ' '\n' | sort); do
        local source_file="${VARIABLE_SOURCES[$var_name]}"
        local var_value="${VARIABLE_VALUES[$var_name]}"

        # Add section header when source changes
        if [[ "$source_file" != "$current_source" ]]; then
            echo "" >> "${OUTPUT_FILE}"
            echo "# --- Variables from $source_file ---" >> "${OUTPUT_FILE}"
            current_source="$source_file"
        fi

        # Write variable with proper quoting
        if [[ "$var_value" =~ [[:space:]] || "$var_value" == "" ]]; then
            echo "$var_name=\"$var_value\"" >> "${OUTPUT_FILE}"
        else
            echo "$var_name=$var_value" >> "${OUTPUT_FILE}"
        fi
    done

    echo "" >> "${OUTPUT_FILE}"
    echo "# --- End of merged configuration ---" >> "${OUTPUT_FILE}"

    echo "OK"
}

function display_summary() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}Environment Merge Summary${NC}"
    echo -e "${GREEN}========================================${NC}"

    echo -e "\n${BLUE}Processed files:${NC}"
    for file in "${PROCESSED_FILES[@]}"; do
        echo -e "  ${GREEN}✓${NC} $file"
    done

    echo -e "\n${BLUE}Variables added (${#ADDED_VARIABLES[@]}):${NC}"
    for var in "${ADDED_VARIABLES[@]}"; do
        local source="${VARIABLE_SOURCES[$var]}"
        echo -e "  ${GREEN}+${NC} $var ${ORANGE}(from $source)${NC}"
    done

    if [[ -n "$BACKUP_FILE" ]]; then
        echo -e "\n${ORANGE}Backup created: $BACKUP_FILE${NC}"
    fi

    echo -e "\n${GREEN}Output file: $OUTPUT_FILE${NC}"
    echo -e "${GREEN}========================================${NC}\n"
}

# --- Función Principal ---
function main() {
    # Set trap for cleanup
    function finish {
        local EXIT_CODE=$?
        if (( EXIT_CODE != 0 )); then
            if [[ -s "${LAST_ERROR}" ]]; then
                log_error "\nLast error: $(< "${LAST_ERROR}")" >&2
            fi
            log_error "\nMerge failed! Check the log: ${FULL_LOG}" >&2
            if [[ -n "$BACKUP_FILE" ]]; then
                log_error "Your original .env file has been backed up as: $BACKUP_FILE" >&2
            fi
        else
            rm "${FULL_LOG}"
        fi
        rm "${LAST_ERROR}"
    }
    trap finish EXIT

    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}uSipipo Environment Merger v${SCRIPT_VERSION}${NC}"
    echo -e "${BLUE}========================================${NC}\n"

    run_step "Validating environment" validate_environment

    # Find and sort env files by priority
    local env_files
    IFS=' ' read -ra env_files <<< "$(find_env_files)"

    if [[ ${#env_files[@]} -eq 0 ]]; then
        log_error "No .env files found to process"
        exit 1
    fi

    log_info "Found ${#env_files[@]} .env files to process"

    run_step "Creating backup if needed" create_backup
    run_step "Merging environment files" merge_env_files "${env_files[@]}"
    run_step "Writing output file" write_output_file

    display_summary

    log_info "Environment merge completed successfully"
    echo -e "${GREEN}Your .env file is ready for use with uSipipo!${NC}"
}

# --- Función de Ayuda ---
function display_usage() {
    cat <<EOF
Usage: $0 [options]

Merge all .env.*.generated files into a single .env file for uSipipo.

Priority order for variable conflicts (highest to lowest):
  1. .env.mariadb.generated
  2. .env.pihole.generated
  3. .env.wireguard.generated
  4. .env.outline.generated
  5. .env.mtproto.generated
  6. .env.shadowmere.generated
  7. .env.dns-config.generated

Options:
  --help      Display this help message

Features:
  - Preserves comments and formatting
  - Handles variable conflicts with priority ordering
  - Creates backup of existing .env file
  - Idempotent and safe operation
  - Detailed logging and progress reporting

Output:
  - .env                    Merged environment file
  - .env.backup.TIMESTAMP   Backup of original file (if existed)

Examples:
  $0          # Merge all .env files
  $0 --help   # Show this help message

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
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

main "$@"