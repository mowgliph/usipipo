#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Configurando permisos ejecutables para todos los archivos .sh en $SCRIPT_DIR..."

for file in *.sh; do
    if [ -f "$file" ]; then
        chmod +x "$file"
        echo "Permisos aplicados a: $file"
    fi
done

echo "Todos los archivos .sh han sido procesados."