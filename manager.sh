#!/bin/bash

# =============================================================================
# uSipipo VPN Manager - Command Center
# =============================================================================
# Description: Interactive menu to Manage, Install, Monitor, and Uninstall.
# =============================================================================

# Global Flag for modules
export INSTALLER_ACTIVE="true"

# Import Utils
if [ -f "./modules/utils.sh" ]; then
    source "./modules/utils.sh"
else
    echo "Error: ./modules/utils.sh not found."
    exit 1
fi

# -----------------------------------------------------------------------------
# Helper Functions for Menu
# -----------------------------------------------------------------------------

show_status() {
    log_header "📊 SYSTEM STATUS"
    local CMD=$(get_compose_cmd)
    
    if [ ! -f ".env" ]; then
        log_warning "No .env file found. System might not be installed."
    else
        echo -e "${CYAN}--- Active Configuration ---${NC}"
        grep -E "SERVER_IP|WIREGUARD_PORT|PIHOLE_WEB_PORT|OUTLINE_API_PORT" .env | sed 's/=/ = /'
    fi

    echo -e "\n${CYAN}--- Docker Containers ---${NC}"
    $CMD ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo -e "\n${GRAY}Press Enter to return to menu...${NC}"
    read
}

show_logs() {
    local CMD=$(get_compose_cmd)
    echo -e "\n${CYAN}Which service logs do you want to see?${NC}"
    echo "1) All Services"
    echo "2) WireGuard"
    echo "3) Outline"
    echo "4) Pi-hole"
    echo "5) Cancel"
    read -p "Select option: " opt

    case $opt in
        1) $CMD logs --tail 50 -f ;;
        2) $CMD logs --tail 50 -f wireguard ;;
        3) $CMD logs --tail 50 -f outline ;;
        4) $CMD logs --tail 50 -f pihole ;;
        *) return ;;
    esac
}

run_install() {
    # Calls the existing install.sh logic
    # We execute it as a separate process to ensure clean environment
    chmod +x install.sh
    ./install.sh
    
    echo -e "\n${GRAY}Press Enter to return to menu...${NC}"
    read
}

run_uninstall() {
    if [ -f "./modules/uninstall.sh" ]; then
        source "./modules/uninstall.sh"
        purge_system
    else
        log_error "Uninstall module missing."
    fi
    echo -e "\n${GRAY}Press Enter to return to menu...${NC}"
    read
}

# -----------------------------------------------------------------------------
# Main Menu Loop
# -----------------------------------------------------------------------------
while true; do
    clear
    echo -e "${CYAN}══════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}   uSipipo VPN Manager - Control Center${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════════════════════════════${NC}"
    echo -e ""
    echo -e "  ${GREEN}1)${NC} Install / Reinstall System"
    echo -e "  ${BLUE}2)${NC} Show System Status"
    echo -e "  ${YELLOW}3)${NC} View Logs (Live)"
    echo -e "  ${RED}4)${NC} Uninstall & Purge Everything"
    echo -e "  ${GRAY}0)${NC} Exit"
    echo -e ""
    read -p "Choose an option [0-4]: " option

    case $option in
        1) run_install ;;
        2) show_status ;;
        3) show_logs ;;
        4) run_uninstall ;;
        0) echo -e "Exiting..."; exit 0 ;;
        *) echo -e "${RED}Invalid option.${NC}"; sleep 1 ;;
    esac
done
