import os
import argparse
import subprocess

# Configuración
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(BASE_DIR, 'version.txt')

def load_version():
    if not os.path.exists(VERSION_FILE):
        return "0.0.0"
    with open(VERSION_FILE, 'r') as f:
        return f.read().strip()

def save_version(version):
    with open(VERSION_FILE, 'w') as f:
        f.write(version)

def increment_version(part):
    current = load_version()
    try:
        major, minor, patch = map(int, current.split('.'))
    except ValueError:
        print(f"❌ Error: El formato de versión actual '{current}' no es válido (debe ser X.Y.Z)")
        return current

    if part == 'major':
        major += 1
        minor = 0
        patch = 0
    elif part == 'minor':
        minor += 1
        patch = 0
    elif part == 'patch':
        patch += 1
    
    new_version = f"{major}.{minor}.{patch}"
    save_version(new_version)
    print(f"✅ Versión actualizada: {current} ➡️  {new_version}")

# # Git automático (Opcional)
#     try:
#         subprocess.run(["git", "add", "version.txt"], check=True)
#         subprocess.run(["git", "commit", "-m", f"🔖 Bump version a v{new_version}"], check=True)
#         print("✅ Git Commit creado automáticamente.")
#     except Exception as e:
#         print(f"⚠️ No se pudo hacer commit automático: {e}")

    return new_version

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Actualizar versión del bot")
    parser.add_argument('part', choices=['major', 'minor', 'patch'], help="Qué parte de la versión subir (major.minor.patch)")
    
    args = parser.parse_args()
    increment_version(args.part)