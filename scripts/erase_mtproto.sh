#!/usr/bin/env bash
# limpiar-mtproto.sh
# Uso:
#   sudo ./limpiar-mtproto.sh          # modo interactivo (pregunta antes de eliminar)
#   sudo ./limpiar-mtproto.sh --yes    # no preguntar, eliminar
#   sudo ./limpiar-mtproto.sh --dry    # mostrar acciones sin ejecutar

set -euo pipefail

DRY_RUN=0
ASSUME_YES=0

for arg in "$@"; do
  case "$arg" in
    --dry) DRY_RUN=1 ;;
    --yes) ASSUME_YES=1 ;;
    -h|--help)
      cat <<EOF
limpiar-mtproto.sh - Elimina archivos y configuraciones comunes de mtproto-proxy

Opciones:
  --dry    Mostrar acciones sin ejecutar
  --yes    Ejecutar sin pedir confirmación
  -h|--help  Muestra esta ayuda
EOF
      exit 0
      ;;
    *) echo "Parámetro desconocido: $arg"; exit 2 ;;
  esac
done

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[DRY] $*"
  else
    echo "[RUN] $*"
    bash -c "$*"
  fi
}

confirm() {
  if [ "$ASSUME_YES" -eq 1 ]; then
    return 0
  fi
  read -r -p "$1 [s/N]: " ans
  case "$ans" in
    s|S|y|Y) return 0 ;;
    *) return 1 ;;
  esac
}

echo
echo "Operación: limpieza de mtproto-proxy y archivos relacionados"
echo

# 1) Detener y deshabilitar service systemd
UNIT_NAMES=(
  mtproto-proxy.service
  mtproto.service
  mtproxy.service
)
for u in "${UNIT_NAMES[@]}"; do
  if systemctl list-units --full -all | grep -q "^${u}"; then
    if confirm "Detener y deshabilitar unidad systemd ${u}?"; then
      run "systemctl stop ${u} || true"
      run "systemctl disable ${u} || true"
      run "systemctl kill ${u} || true"
      run "rm -f /etc/systemd/system/${u} || true"
    fi
  else
    echo "No encontrada unidad ${u}"
  fi
done

# Recargar systemd si hemos eliminado algo
if [ "$DRY_RUN" -eq 0 ]; then
  run "systemctl daemon-reload || true"
fi

# 2) Archivos y directorios comunes
PATHS=(
  /opt/mtproto-proxy
  /opt/mtproxy
  /usr/local/bin/mtproto-proxy
  /usr/bin/mtproto-proxy
  /usr/sbin/mtproto-proxy
  /etc/mtproto-proxy
  /etc/mtproto
  /etc/mtproxy
  /var/lib/mtproto-proxy
  /var/run/mtproto-proxy
  /var/log/mtproto-proxy
  /var/log/mtproxy
  /tmp/mtproxy*
  /tmp/min-proxy.conf
  /tmp/mtproxy*
)

echo
for p in "${PATHS[@]}"; do
  if [ -e "$p" ]; then
    if confirm "Eliminar ${p}?"; then
      run "rm -rf ${p} || true"
    fi
  fi
done

# 3) Ficheros en working directories habituales
CANDIDATES=(
  /opt/mtproto-proxy/objs/bin/proxy-multi.conf
  /opt/mtproto-proxy/objs/bin/proxy-secret
  /opt/mtproto-proxy/objs/bin/mtproto-proxy
  /opt/mtproto-proxy/proxy-multi.conf
  /opt/mtproto-proxy/proxy-secret
)
echo
for f in "${CANDIDATES[@]}"; do
  if [ -e "$f" ]; then
    if confirm "Eliminar fichero ${f}?"; then
      run "rm -f ${f} || true"
    fi
  fi
done

# 4) Usuarios y grupos típicos
USERS=(mtproxy mtproto mtproxyuser)
GROUPS=(mtproxy mtproto)

echo
for u in "${USERS[@]}"; do
  if id "$u" >/dev/null 2>&1; then
    if confirm "Eliminar usuario ${u} y su home?"; then
      run "userdel -r ${u} || true"
    fi
  fi
done

for g in "${GROUPS[@]}"; do
  if getent group "$g" >/dev/null 2>&1; then
    if confirm "Eliminar grupo ${g}?"; then
      run "groupdel ${g} || true"
    fi
  fi
done

# 5) Reglas de firewall comunes (ufw, iptables)
echo
if command -v ufw >/dev/null 2>&1; then
  if confirm "Eliminar reglas ufw relacionadas con puertos 47105, 8888 u otros usados por mtproto?"; then
    run "ufw delete allow 47105 || true"
    run "ufw delete allow 8888 || true"
  fi
fi

if command -v iptables >/dev/null 2>&1; then
  if confirm "Eliminar reglas iptables que mencionen 'mtproxy' o puertos 47105/8888? (solo líneas detectadas serán mostradas)"; then
    echo "Reglas que contienen mtproxy o puertos candidatos:"
    run "iptables -S | grep -E 'mtproxy|47105|8888' || true"
    run "iptables -D INPUT -p tcp --dport 47105 -j ACCEPT || true"
    run "iptables -D INPUT -p tcp --dport 8888 -j ACCEPT || true"
  fi
fi

# 6) Packages instalados (solo listar, no eliminar por defecto)
PKG_CANDIDATES=(mtproto-proxy mtproxy mtproxy-binary)
echo
echo "Buscar paquetes relacionados (solo listado):"
for pkg in "${PKG_CANDIDATES[@]}"; do
  if dpkg -l 2>/dev/null | awk '{print $2}' | grep -q "^${pkg}$"; then
    echo "Paquete instalado detectado: ${pkg}"
    if confirm "Deseas eliminar el paquete apt ${pkg}?"; then
      run "apt-get remove --purge -y ${pkg} || true"
    fi
  fi
done

# 7) Limpieza de journal y logs
echo
if confirm "Vaciar journalctl del servicio mtproto-proxy y eliminar logs detectados?"; then
  run "journalctl --rotate || true"
  run "journalctl --vacuum-time=1s || true"
  run "rm -f /var/log/mtproto-proxy* /var/log/mtproxy* 2>/dev/null || true"
fi

# 8) Confirmación final
echo
echo "Limpieza completada (o mostrada en dry-run). Recomendación: reiniciar el sistema para liberar sockets/pids si es necesario."
