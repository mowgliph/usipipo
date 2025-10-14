#!/bin/bash
# ======================================================
# 📦 Script: auto_version.sh
# 🧠 Descripción:
#   Genera automáticamente una nueva versión del proyecto uSipipo
#   cada vez que se ejecuta este script.
#   Actualiza el archivo VERSION y el valor BOT_VERSION en .env
# ======================================================

set -e

# Detectar la raíz del proyecto (un nivel arriba de scripts/)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="$PROJECT_DIR/VERSION"
ENV_FILE="$PROJECT_DIR/.env"

# Crear archivo VERSION si no existe
if [ ! -f "$VERSION_FILE" ]; then
  echo "1.0.0" > "$VERSION_FILE"
fi

# Leer versión actual
CURRENT_VERSION=$(cat "$VERSION_FILE" | tr -d 'v')
IFS='.' read -r major minor patch <<< "$CURRENT_VERSION"

# Incrementar la versión
patch=$((patch + 1))
if [ "$patch" -ge 1000 ]; then
  patch=0
  minor=$((minor + 1))
fi

NEW_VERSION="${major}.${minor}.${patch}"
echo "$NEW_VERSION" > "$VERSION_FILE"

# Actualizar o agregar BOT_VERSION en .env
if [ -f "$ENV_FILE" ]; then
  if grep -q '^BOT_VERSION=' "$ENV_FILE"; then
    sed -i "s/^BOT_VERSION=.*/BOT_VERSION=$NEW_VERSION/" "$ENV_FILE"
  else
    echo "BOT_VERSION=$NEW_VERSION" >> "$ENV_FILE"
  fi
else
  echo "BOT_VERSION=$NEW_VERSION" > "$ENV_FILE"
fi

echo "✅ Nueva versión generada: uSipipo v${NEW_VERSION}"