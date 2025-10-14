#!/bin/bash
# ======================================================
# 🚀 Script de arranque en modo desarrollo con auto-reload y versionado automático
# ======================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$PROJECT_DIR/venv/bin/activate"

# Instalar watchdog si no está presente
pip show watchdog > /dev/null 2>&1 || pip install watchdog

AUTO_VERSION_SCRIPT="$PROJECT_DIR/scripts/auto_version.sh"

if [ ! -f "$AUTO_VERSION_SCRIPT" ]; then
  echo "⚠️  No se encontró el script de versión automática en:"
  echo "   $AUTO_VERSION_SCRIPT"
  echo "   Crealo con el nombre 'auto_version.sh' dentro de la carpeta scripts/"
  exit 1
fi

echo "🚀 Iniciando uSipipo en modo desarrollo con auto-reload y versionado automático..."
cd "$PROJECT_DIR"

# Función que se ejecutará cada vez que se detecten cambios
reload_command() {
  bash "$AUTO_VERSION_SCRIPT"
  python3 -m bot.main
}

# Iniciar watchmedo con el comando personalizado
watchmedo auto-restart \
  --directory="$PROJECT_DIR" \
  --pattern="*.py" \
  --recursive \
  -- bash -c "bash '$AUTO_VERSION_SCRIPT' && python3 -m bot.main"