#!/bin/bash
set -e

# Función para mostrar el menú de opciones
show_menu() {
    echo -e "\n🚀 uSipipo VPN - Gestor de Instalación"
    echo "============================================="
    echo "1) Instalar todos los componentes (Pi-hole, WireGuard, Outline)"
    echo "2) Desinstalar todo (eliminar todos los componentes)"
    echo "3) Salir"
    read -p "Seleccione una opción [1-3]: " choice
    case $choice in
        1) install_all ;;
        2) uninstall_all ;;
        3) exit 0 ;;
        *) echo "❌ Opción inválida"; show_menu ;;
    esac
}

# Función para instalar todos los componentes
install_all() {
    echo -e "\n🔧 Iniciando instalación completa de uSipipo VPN"
    echo "============================================="

    BASE_DIR=$(dirname "$0")
    cd "$BASE_DIR"

    # Crear archivo de credenciales vacío
    echo "# Archivo de credenciales generadas automáticamente" > /home/vpnuser/credentials.env 2>/dev/null || true
    chmod 600 /home/vpnuser/credentials.env 2>/dev/null || true

    # Ejecutar scripts en orden correcto
    chmod +x *.sh

    echo "🔧 Paso 1: Instalación base"
    ./i-base.sh

    echo "🔧 Paso 2: Instalación de Pi-hole"
    ./i-pihole.sh

    echo "🔧 Paso 3: Instalación de WireGuard"
    ./i-wireguard.sh

    echo "🔧 Paso 4: Instalación de Outline"
    ./i-outline.sh

    # Permisos finales
    chown -R vpnuser:vpnuser /home/vpnuser 2>/dev/null || true
    chmod 600 /home/vpnuser/credentials.env 2>/dev/null || true

    # Verificar servicios críticos
    echo "🔍 Verificando servicios críticos..."
    services=("wg-quick@wg0" "pihole-FTL" "lighttpd" "docker")
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            echo "✅ ${service} - ACTIVO"
        else
            echo "⚠️ ${service} - INACTIVO (revisar después de reiniciar)"
        fi
    done

    echo -e "\n🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE"
    echo "🔑 Credenciales guardadas en: /home/vpnuser/credentials.env"
    echo "🌐 Acceso a Pi-hole: http://$(hostname -I | awk '{print $1}')/admin"
    echo "🔧 Reinicia el servidor para aplicar todos los cambios: sudo reboot"
    echo "💡 Después del reinicio, configura el bot de Telegram con las credenciales"
}

# Función mejorada para desinstalar TODO
uninstall_all() {
    echo -e "\n⚠️ ⚠️ ⚠️ ADVERTENCIA: DESINSTALACIÓN COMPLETA ⚠️ ⚠️ ⚠️"
    echo "Esta operación eliminará permanentemente:"
    echo "- Pi-hole y toda su configuración"
    echo "- WireGuard y todas las conexiones de usuarios"
    echo "- Outline Server y todas las claves de acceso"
    echo "- Usuarios y grupos creados (vpnuser)"
    echo "- Archivos de configuración y credenciales"
    echo "- Reglas de firewall personalizadas"
    echo ""
    echo "Los datos NO podrán ser recuperados después de esta operación."
    
    read -p "¿Está SEGURO de que quiere continuar? [s/N]: " confirm
    if [[ ! "$confirm" =~ [sS] ]]; then
        echo "❌ Operación cancelada por el usuario"
        exit 0
    fi
    
    echo -e "\n🗑️ Iniciando desinstalación completa de uSipipo VPN"
    echo "============================================="
    
    # 1. Eliminar Outline Server primero (evitar conflictos)
    echo "🔧 Paso 1: Eliminando Outline Server"
    if command -v docker &> /dev/null && docker ps -a | grep -q outline-server; then
        echo "   ⏳ Deteniendo contenedor de Outline..."
        timeout 30 docker stop outline-server 2>/dev/null || true
        echo "   ⏳ Eliminando contenedor de Outline..."
        timeout 30 docker rm -f outline-server 2>/dev/null || true
    fi
    
    # Eliminar volumen de Outline
    if command -v docker &> /dev/null; then
        docker volume rm outline_persist 2>/dev/null || true
    fi
    
    # 2. Eliminar WireGuard
    echo "🔧 Paso 2: Eliminando WireGuard"
    if ip link show wg0 &> /dev/null; then
        echo "   ⏳ Bajando interfaz WireGuard..."
        timeout 10 wg-quick down wg0 2>/dev/null || true
    fi
    
    if systemctl is-active --quiet wg-quick@wg0 2>/dev/null; then
        echo "   ⏳ Deteniendo servicio WireGuard..."
        systemctl stop wg-quick@wg0 2>/dev/null || true
        systemctl disable wg-quick@wg0 2>/dev/null || true
    fi
    
    # Eliminar interfaz de red
    ip link delete wg0 2>/dev/null || true
    
    # Eliminar paquetes de WireGuard
    apt-get remove -y --purge wireguard wireguard-tools qrencode 2>/dev/null || true
    apt-get autoremove -y 2>/dev/null || true
    
    # Eliminar archivos de configuración
    rm -rf /etc/wireguard 2>/dev/null || true
    rm -f /etc/systemd/system/wg-quick@wg0.service 2>/dev/null || true
    rm -f /etc/systemd/system/multi-user.target.wants/wg-quick@wg0.service 2>/dev/null || true
    systemctl daemon-reload 2>/dev/null || true
    
    # 3. Eliminar Pi-hole (METODO CORREGIDO)
    echo "🔧 Paso 3: Eliminando Pi-hole (método mejorado)"
    
    # Método 1: Intentar desinstalación oficial con timeout
    if command -v pihole &> /dev/null; then
        echo "   ⏳ Intentando desinstalación oficial de Pi-hole..."
        echo "y" | timeout 60 pihole uninstall --confirm 2>/dev/null || true
    fi
    
    # Método 2: Forzar eliminación manual si el método 1 falla
    echo "   ⏳ Realizando limpieza manual de Pi-hole..."
    
    # Detener servicios relacionados
    for service in "pihole-FTL" "lighttpd" "dnsmasq"; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            echo "      ⏳ Deteniendo $service..."
            systemctl stop "$service" 2>/dev/null || true
            systemctl disable "$service" 2>/dev/null || true
        fi
    done
    
    # Eliminar paquetes de Pi-hole y dependencias
    echo "   ⏳ Eliminando paquetes de Pi-hole..."
    apt-get remove -y --purge pihole-FTL pihole-core pihole-common lighttpd php-* dnsmasq-base dnsutils 2>/dev/null || true
    apt-get autoremove -y 2>/dev/null || true
    
    # Eliminar archivos y directorios restantes
    echo "   ⏳ Eliminando archivos de configuración restantes..."
    directories=(
        "/etc/pihole"
        "/var/www/html/admin"
        "/etc/.pihole"
        "/etc/dnsmasq.d"
        "/etc/lighttpd"
        "/var/log/pihole"
        "/var/log/pihole-ftl"
        "/run/pihole"
    )
    
    for dir in "${directories[@]}"; do
        if [ -d "$dir" ]; then
            echo "      ⏳ Eliminando $dir..."
            rm -rf "$dir" 2>/dev/null || true
        fi
    done
    
    # Eliminar archivos de configuración específicos
    files=(
        "/etc/lighttpd/conf-enabled/20-pihole.conf"
        "/etc/lighttpd/lighttpd.conf"
        "/etc/dnsmasq.conf"
        "/etc/dnsmasq.d/01-pihole.conf"
        "/etc/resolv.conf"
    )
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            echo "      ⏳ Eliminando $file..."
            rm -f "$file" 2>/dev/null || true
        fi
    done
    
    # Restaurar resolv.conf a valores por defecto
    echo "nameserver 8.8.8.8" > /etc/resolv.conf 2>/dev/null || true
    
    # 4. Eliminar Docker completamente
    echo "🔧 Paso 4: Eliminando Docker"
    if command -v docker &> /dev/null; then
        echo "   ⏳ Deteniendo todos los contenedores Docker..."
        timeout 30 docker stop $(docker ps -aq 2>/dev/null) 2>/dev/null || true
        echo "   ⏳ Eliminando todos los contenedores Docker..."
        timeout 30 docker rm -f $(docker ps -aq 2>/dev/null) 2>/dev/null || true
        echo "   ⏳ Eliminando todas las imágenes Docker..."
        timeout 30 docker rmi -f $(docker images -q 2>/dev/null) 2>/dev/null || true
        
        # Detener y deshabilitar servicio
        systemctl stop docker 2>/dev/null || true
        systemctl disable docker 2>/dev/null || true
        
        # Eliminar paquetes de Docker
        apt-get remove -y --purge docker docker-engine docker.io containerd runc docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-model-plugin 2>/dev/null || true
        apt-get autoremove -y 2>/dev/null || true
        
        # Eliminar archivos y directorios de Docker
        rm -rf /var/lib/docker 2>/dev/null || true
        rm -rf /etc/docker 2>/dev/null || true
        rm -f /etc/systemd/system/docker.service 2>/dev/null || true
        rm -f /etc/systemd/system/docker.socket 2>/dev/null || true
        rm -rf /var/run/docker 2>/dev/null || true
        systemctl daemon-reload 2>/dev/null || true
    fi
    
    # 5. Restaurar configuración de red
    echo "🔧 Paso 5: Restaurando configuración de red"
    
    # Restaurar sysctl.conf a valores predeterminados
    echo "   ⏳ Restaurando configuración de red..."
    sed -i '/net.ipv4.ip_forward/d' /etc/sysctl.conf 2>/dev/null || true
    sed -i '/net.ipv6.conf.all.forwarding/d' /etc/sysctl.conf 2>/dev/null || true
    sysctl -p 2>/dev/null || true
    
    # Eliminar reglas de iptables personalizadas
    echo "   ⏳ Limpiando reglas de firewall..."
    iptables -F 2>/dev/null || true
    iptables -t nat -F 2>/dev/null || true
    iptables -t mangle -F 2>/dev/null || true
    iptables -P FORWARD ACCEPT 2>/dev/null || true
    
    ip6tables -F 2>/dev/null || true
    ip6tables -t nat -F 2>/dev/null || true
    ip6tables -t mangle -F 2>/dev/null || true
    ip6tables -P FORWARD ACCEPT 2>/dev/null || true
    
    netfilter-persistent save 2>/dev/null || true
    
    # 6. Restaurar firewall a configuración predeterminada
    echo "🔧 Paso 6: Restaurando firewall"
    ufw --force reset 2>/dev/null || true
    ufw default deny incoming 2>/dev/null || true
    ufw default allow outgoing 2>/dev/null || true
    ufw allow OpenSSH 2>/dev/null || true
    ufw --force enable 2>/dev/null || true
    
    # 7. Eliminar usuario y grupos
    echo "🔧 Paso 7: Eliminando usuarios y grupos"
    if id "vpnuser" &>/dev/null; then
        echo "   ⏳ Eliminando usuario vpnuser..."
        userdel -r vpnuser 2>/dev/null || true
    fi
    
    # 8. Eliminar archivos y directorios del proyecto
    echo "🔧 Paso 8: Limpiando archivos del proyecto"
    rm -f /home/vpnuser/credentials.env 2>/dev/null || true
    rm -rf /home/vpnuser/VPNs_Configs 2>/dev/null || true
    rm -rf /home/vpnuser 2>/dev/null || true
    
    # 9. Instalar paquetes esenciales que podrían haber sido eliminados
    echo "🔧 Paso 9: Reinstalando paquetes esenciales"
    apt-get update 2>/dev/null || true
    apt-get install -y --reinstall openssh-server net-tools iproute2 curl wget 2>/dev/null || true
    
    # 10. Limpiar caché de paquetes
    echo "🔧 Paso 10: Limpiando caché del sistema"
    apt-get clean 2>/dev/null || true
    apt-get autoclean 2>/dev/null || true
    
    echo -e "\n✅ DESINSTALACIÓN COMPLETA FINALIZADA"
    echo "🔍 Verificando que no queden procesos residuales..."
    
    # Verificar procesos residuales
    residual_processes=$(ps aux | grep -E 'pihole|wireguard|wg-quick|docker|outline' | grep -v grep | wc -l)
    if [ "$residual_processes" -gt 0 ]; then
        echo "⚠️ Se detectaron $residual_processes procesos residuales. Reinicie el servidor para eliminarlos completamente."
        ps aux | grep -E 'pihole|wireguard|wg-quick|docker|outline' | grep -v grep
    fi
    
    echo "🔄 Se recomienda reiniciar el servidor para limpiar completamente todos los procesos:"
    echo "sudo reboot"
}

# Iniciar el script
clear
show_menu
