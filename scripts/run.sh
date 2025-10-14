#!/bin/bash
# Script de arranque para el bot Usipipo

set -e

# Ruta al directorio raíz del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Activar entorno virtual
source "$PROJECT_DIR/venv/bin/activate"

# Ejecutar el bot como módulo desde la raíz
cd "$PROJECT_DIR"
python3 -m bot.main