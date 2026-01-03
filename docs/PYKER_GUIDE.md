# Guía de Configuración de Pyker para uSipipo VPN Bot

## 📋 Tabla de Contenidos

- [¿Qué es Pyker?](#qué-es-pyker)
- [Ventajas sobre PM2](#ventajas-sobre-pm2)
- [Instalación](#instalación)
- [Configuración para uSipipo](#configuración-para-usipipo)
- [Comandos Básicos](#comandos-básicos)
- [Configuración Avanzada](#configuración-avanzada)
- [Troubleshooting](#troubleshooting)
- [Integración con Sistema](#integración-con-sistema)

---

## 🚀 ¿Qué es Pyker?

**Pyker** es un gestor de procesos diseñado específicamente para Python. Es la alternativa moderna a PM2, pero construido desde cero para aplicaciones Python con características nativas como soporte para entornos virtuales y logs optimizados.

### ✨ Características Principales

- 🐍 **Nativo Python**: Diseñado específicamente para aplicaciones Python
- 🔄 **Auto-reinicio**: Reinicia automáticamente los procesos si fallan
- 📊 **Monitoreo en tiempo real**: Interfaz elegante para ver procesos activos
- 🛠️ **Instalación sin sudo**: Instala en espacio de usuario
- 📝 **Logs centralizados**: Todos los logs en un solo lugar con rotación
- 🎯 **Cross-platform**: Linux, macOS y Windows

---

## 🏆 Ventajas sobre PM2 para uSipipo

| Característica | Pyker | PM2 |
|---|---|---|
| **Lenguaje nativo** | ✅ Python | ❌ Node.js |
| **Entornos virtuales** | ✅ Automático | ⚠️ Manual |
| **Instalación** | ✅ Sin sudo | ❌ Requiere npm |
| **Logs Python-friendly** | ✅ Optimizado | ⚠️ Genérico |
| **Configuración** | ✅ Simple | ⚠️ JSON complejo |
| **Recursos** | ✅ Ligero | ⚠️ Más pesado |

---

## 📦 Instalación

### Método 1: Instalación Automática (Recomendado)

```bash
curl -sSL https://raw.githubusercontent.com/mrvi0/pyker/main/install.sh | bash
```

O con wget:

```bash
wget -qO- https://raw.githubusercontent.com/mrvi0/pyker/main/install.sh | bash
```

### Método 2: Instalación con Python

```bash
# Descargar y ejecutar instalador Python
curl -sSL https://raw.githubusercontent.com/mrvi0/pyker/main/install.py | python3
```

### Método 3: Instalación Manual

```bash
# Clonar el repositorio
git clone https://github.com/mrvi0/pyker.git
cd pyker

# Instalar (no requiere sudo!)
python3 install.py
```

### Método 4: Desde Código Fuente

```bash
# Instalar dependencia psutil
pip3 install --user psutil

# Copiar pyker al bin local
mkdir -p ~/.local/bin
cp pyker.py ~/.local/bin/pyker
chmod +x ~/.local/bin/pyker

# Agregar al PATH (agregar esta línea a ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"
```

### Verificar Instalación

```bash
# Verificar que pyker está en el PATH
which pyker

# Ver versión
pyker --version

# Ver ayuda
pyker --help
```

> **Nota**: Pyker se instala en `~/.local/bin` y configura automáticamente tu PATH.

---

## ⚙️ Configuración para uSipipo

### 1. Preparar el Entorno

```bash
# Navegar al proyecto
cd /ruta/a/tu/proyecto/usipipo

# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Verificar que el bot funciona manualmente
python main.py
```

### 2. Iniciar el Bot con Pyker

```bash
# Iniciar el bot como proceso en background
pyker start usipipo-bot main.py

# Verificar que está corriendo
pyker list
```

### 3. Configuración Recomendada para uSipipo

```bash
# Iniciar con opciones específicas para uSipipo
pyker start usipipo-bot main.py \
  --env PYTHONPATH=. \
  --env NODE_ENV=production \
  --restart-delay 5000 \
  --max-restarts 10
```

### 4. Verificar Funcionamiento

```bash
# Ver todos los procesos
pyker list

# Ver logs en tiempo real
pyker logs usipipo-bot -f

# Ver información detallada del proceso
pyker info usipipo-bot
```

---

## 🎮 Comandos Básicos

### Gestión de Procesos

```bash
# Iniciar un proceso
pyker start <nombre> <script.py>

# Listar todos los procesos
pyker list
pyker ls

# Ver información de un proceso específico
pyker info <nombre>

# Reiniciar un proceso
pyker restart <nombre>

# Detener un proceso
pyker stop <nombre>

# Eliminar un proceso
pyker delete <nombre>
```

### Gestión de Logs

```bash
# Ver logs de un proceso
pyker logs <nombre>

# Ver logs en tiempo real
pyker logs <nombre> -f
pyker logs <nombre> --follow

# Ver últimas N líneas
pyker logs <nombre> -n 50

# Ver logs de todos los procesos
pyker logs --all
```

### Monitoreo

```bash
# Ver estado en tiempo real
pyker monit

# Ver uso de recursos
pyker stats

# Ver historial de reinicios
pyker history <nombre>
```

---

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# Iniciar con variables de entorno personalizadas
pyker start usipipo-bot main.py \
  --env DATABASE_URL="postgresql://..." \
  --env TELEGRAM_TOKEN="..." \
  --env LOG_LEVEL="INFO" \
  --env PYTHONPATH="."
```

### Configuración de Reinicio

```bash
# Configurar política de reinicios
pyker start usipipo-bot main.py \
  --restart-delay 10000 \      # 10 segundos entre reinicios
  --max-restarts 5 \            # Máximo 5 reinicios
  --restart-on-failure \       # Reiniciar solo si falla
  --restart-on-crash           # Reiniciar si hay crash
```

### Configuración de Logs

```bash
# Configurar rotación de logs
pyker start usipipo-bot main.py \
  --log-file logs/usipipo.log \
  --log-max-size 10M \
  --log-backups 5
```

### Archivo de Configuración (Opcional)

Crea un archivo `pyker.yaml` en tu proyecto:

```yaml
# pyker.yaml
apps:
  - name: usipipo-bot
    script: main.py
    cwd: /ruta/a/tu/proyecto/usipipo
    interpreter: python3
    env:
      PYTHONPATH: .
      NODE_ENV: production
    restart_delay: 5000
    max_restarts: 10
    log_file: logs/usipipo.log
    log_max_size: 10M
    log_backups: 5
```

Luego inicia con:
```bash
pyker start --config pyker.yaml
```

---

## 🛠️ Troubleshooting

### Problemas Comunes

#### 1. Pyker no encontrado después de la instalación

```bash
# Agregar al PATH manualmente
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# O reinicia tu terminal
```

#### 2. El bot no inicia con Pyker

```bash
# Verificar el entorno virtual
which python
python --version

# Verificar dependencias
pip install -r requirements.txt

# Verificar archivo .env
ls -la .env
```

#### 3. Problemas con logs

```bash
# Crear directorio de logs
mkdir -p logs

# Verificar permisos
chmod 755 logs
```

#### 4. El bot se reinicia constantemente

```bash
# Ver logs de errores
pyker logs usipipo-bot -f

# Ver historial de reinicios
pyker history usipipo-bot

# Revisar configuración
pyker info usipipo-bot
```

### Depuración

```bash
# Iniciar en modo debug
pyker start usipipo-bot main.py --debug

# Ver logs detallados
pyker logs usipipo-bot -f --level debug

# Ver información del sistema
pyker doctor
```

---

## 🔄 Integración con Sistema

### Inicio Automático (Linux)

```bash
# Crear servicio systemd
sudo nano /etc/systemd/system/usipipo-bot.service
```

```ini
[Unit]
Description=uSipipo VPN Bot
After=network.target

[Service]
Type=forking
User=mowgli
WorkingDirectory=/home/mowgli/us
Environment=PATH=/home/mowgli/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/mowgli/.local/bin/pyker start usipipo-bot main.py
ExecStop=/home/mowgli/.local/bin/pyker stop usipipo-bot
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y arrancar el servicio
sudo systemctl enable usipipo-bot
sudo systemctl start usipipo-bot

# Ver estado
sudo systemctl status usipipo-bot
```

### Scripts de Mantenimiento

Crea `scripts/bot_manager.sh`:

```bash
#!/bin/bash

case "$1" in
    start)
        echo "🚀 Iniciando uSipipo Bot..."
        pyker start usipipo-bot main.py
        ;;
    stop)
        echo "🛑 Deteniendo uSipipo Bot..."
        pyker stop usipipo-bot
        ;;
    restart)
        echo "🔄 Reiniciando uSipipo Bot..."
        pyker restart usipipo-bot
        ;;
    status)
        echo "📊 Estado del uSipipo Bot:"
        pyker list
        ;;
    logs)
        echo "📝 Logs del uSipipo Bot:"
        pyker logs usipipo-bot -f
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
```

```bash
# Hacer ejecutable
chmod +x scripts/bot_manager.sh

# Usar
./scripts/bot_manager.sh start
./scripts/bot_manager.sh status
```

---

## 📊 Monitoreo y Mantenimiento

### Checklist Diario

```bash
# 1. Verificar estado del bot
pyker list

# 2. Verificar logs recientes
pyker logs usipipo-bot -n 50

# 3. Verificar uso de recursos
pyker stats

# 4. Verificar reinicios
pyker history usipipo-bot
```

### Backup de Logs

```bash
# Script para backup de logs
#!/bin/bash
BACKUP_DIR="backups/logs/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Copiar logs de Pyker
cp -r ~/.pyker/logs/* "$BACKUP_DIR/"

# Comprimir
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

echo "✅ Logs backup completado: $BACKUP_DIR.tar.gz"
```

---

## 🎯 Mejores Prácticas

### 1. Seguridad

- Nunca incluir tokens sensibles en comandos
- Usar variables de entorno para configuración
- Mantener el archivo `.env` fuera del control de versiones

### 2. Rendimiento

- Limitar el número máximo de reinicios
- Configurar rotación de logs
- Monitorear el uso de memoria y CPU

### 3. Mantenimiento

- Revisar logs regularmente
- Actualizar Pyker periódicamente
- Documentar cambios en la configuración

---

## 📚 Referencias Útiles

- [Pyker GitHub Repository](https://github.com/mrvi0/pyker)
- [Documentación de uSipipo](./README.md)
- [Guía de Alembic](./ALEMBIC_GUIDE.md)
- [Comandos del Bot](./BOT_COMMANDS.md)

---

## 🤝 Soporte

Si encuentras problemas con Pyker:

1. Revisa el [GitHub Issues](https://github.com/mrvi0/pyker/issues)
2. Consulta la documentación oficial
3. Revisa el troubleshooting en esta guía

---

**¡Listo! Tu bot uSipipo ahora correrá 24/7 con Pyker.** 🎉

---

*Última actualización: 3 de Enero 2026*
