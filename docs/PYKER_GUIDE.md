Guía de Pyker para uSipipo VPN Bot

📋 Tabla de Contenidos

· Instalación Rápida
· Inicio del Bot
· Comandos Esenciales
· Configuración para uSipipo
· Monitoreo y Logs
· Solución de Problemas

---

🚀 Instalación Rápida

Instalar Pyker desde tu Fork

```bash
# Usa tu fork personal de GitHub
curl -sSL https://raw.githubusercontent.com/mowgliph/pyker/main/install.sh | bash
```

O desde el repositorio original

```bash
# Instalación oficial
curl -sSL https://raw.githubusercontent.com/mrvi0/pyker/main/install.sh | bash
```

Verificar instalación

```bash
# Verifica que se instaló correctamente
which pyker
pyker --version
```

Nota: Reinicia tu terminal después de instalar para activar el autocompletado con Tab.

---

🎯 Inicio del Bot

Método básico

```bash
# Navega a tu proyecto uSipipo
cd /home/mowgli/us

# Inicia el bot con Pyker
pyker start usipipo-bot main.py
```

Con entorno virtual

```bash
# Especifica el entorno virtual
pyker start usipipo-bot main.py --venv ./venv
```

Con reinicio automático

```bash
# Para producción - reinicia si falla
pyker start usipipo-bot main.py --venv ./venv --auto-restart
```

Con variables de entorno

```bash
# Configura variables específicas
pyker start usipipo-bot main.py \
  --venv ./venv \
  --auto-restart \
  --env PYTHONPATH=. \
  --env LOG_LEVEL=INFO
```

---

📋 Comandos Esenciales

Gestión del Bot

```bash
# Iniciar
pyker start usipipo-bot main.py

# Detener
pyker stop usipipo-bot

# Reiniciar
pyker restart usipipo-bot

# Eliminar
pyker delete usipipo-bot
```

Monitoreo

```bash
# Ver todos los procesos
pyker list

# Ver información detallada
pyker info usipipo-bot

# Ver logs
pyker logs usipipo-bot

# Ver logs en tiempo real
pyker logs usipipo-bot -f
```

Verificación

```bash
# Ver estado del bot
pyker list | grep usipipo

# Ver versión de Pyker
pyker --version

# Ver ayuda
pyker --help
```

---

⚙️ Configuración para uSipipo

Estructura recomendada

```bash
/home/mowgli/us/
├── main.py              # Tu bot principal
├── venv/               # Entorno virtual
├── requirements.txt    # Dependencias
└── .env               # Variables (NO subir a Git)
```

Script de gestión

Crea manage_bot.sh:

```bash
#!/bin/bash
# Script para gestionar uSipipo Bot con Pyker

case "$1" in
    start)
        cd /home/mowgli/us
        pyker start usipipo-bot main.py --venv ./venv --auto-restart
        ;;
    stop)
        pyker stop usipipo-bot
        ;;
    restart)
        pyker restart usipipo-bot
        ;;
    status)
        pyker list
        ;;
    logs)
        pyker logs usipipo-bot -f
        ;;
    update)
        cd /home/mowgli/us
        git pull
        source venv/bin/activate
        pip install -r requirements.txt
        pyker restart usipipo-bot
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|logs|update}"
        ;;
esac
```

Hacer ejecutable

```bash
chmod +x manage_bot.sh
./manage_bot.sh start
```

---

📊 Monitoreo y Logs

Ver estado

```bash
# Tabla completa (CPU, RAM, fechas)
pyker list

# Solo el estado
pyker info usipipo-bot
```

Ver logs

```bash
# Últimas 50 líneas
pyker logs usipipo-bot -n 50

# Seguir logs en tiempo real
pyker logs usipipo-bot -f

# Buscar errores
pyker logs usipipo-bot | grep -i "error\|exception"
```

Logs de Pyker

Los logs se guardan en:

```
~/.pyker/logs/usipipo-bot.log
```

Pyker hace rotación automática:

· usipipo-bot.log - Log actual
· usipipo-bot.log.1 - Rotado más reciente
· usipipo-bot.log.2 - Rotado anterior

---

🔧 Solución de Problemas

Problemas comunes

El bot no inicia:

```bash
# 1. Verifica que funciona manualmente
cd /home/mowgli/us
source venv/bin/activate
python main.py

# 2. Revisa logs de Pyker
pyker logs usipipo-bot

# 3. Verifica el entorno virtual
pyker info usipipo-bot | grep "Virtual env"
```

Pyker no está en PATH:

```bash
# Agrega al PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Error de permisos:

```bash
# Verifica permisos
ls -la ~/.local/bin/pyker
chmod +x ~/.local/bin/pyker
```

Proceso atascado:

```bash
# Mata el proceso manualmente
ps aux | grep "python.*main.py"
kill -9 <PID>

# Limpia en Pyker
pyker delete usipipo-bot
pyker start usipipo-bot main.py
```

Comandos de diagnóstico

```bash
# Ver todo el sistema
pyker list --all

# Ver configuración
cat ~/.pyker/config.json

# Ver procesos del sistema
ps aux | grep -i "usipipo\|python"

# Ver uso de memoria
free -h
```

---

📌 Resumen Rápido

Para empezar:

```bash
# 1. Instalar
curl -sSL https://raw.githubusercontent.com/mowgliph/pyker/main/install.sh | bash

# 2. Iniciar bot
cd /home/mowgli/us
pyker start usipipo-bot main.py --venv ./venv --auto-restart

# 3. Verificar
pyker list
```

Comandos diarios:

```bash
# Ver estado
pyker list

# Ver logs recientes
pyker logs usipipo-bot -n 20

# Reiniciar si es necesario
pyker restart usipipo-bot
```

Mantenimiento:

```bash
# Backup de logs (opcional)
cp ~/.pyker/logs/usipipo-bot.log ~/backup/usipipo-$(date +%Y%m%d).log

# Limpiar logs viejos
find ~/.pyker/logs -name "usipipo-bot.log.*" -mtime +7 -delete
```

---

🎯 Configuración Final Recomendada

Para uSipipo en producción:

```bash
pyker start usipipo-bot main.py \
  --venv /home/mowgli/us/venv \
  --auto-restart \
  --env PYTHONPATH=/home/mowgli/us \
  --env LOG_LEVEL=INFO
```

Esto garantiza:

· ✅ Reinicio automático si falla
· ✅ Uso del entorno virtual correcto
· ✅ Logs nivel INFO (evita spam)
· ✅ PATH de Python configurado

---

📞 Soporte Rápido

¿El bot no arranca?

```bash
pyker logs usipipo-bot
```

¿Proceso desaparecido?

```bash
pyker list
```

¿Error extraño?

```bash
pyker info usipipo-bot
```

¿Reinstalar Pyker?

```bash
curl -sSL https://raw.githubusercontent.com/mowgliph/pyker/main/install.sh | bash
```

---

¡Listo! Tu bot uSipipo ahora está gestionado por Pyker.

Comandos principales a recordar:

· pyker list - Ver estado
· pyker logs usipipo-bot -f - Ver logs
· pyker restart usipipo-bot - Reiniciar
· pyker stop usipipo-bot - Detener

---

Guía específica para uSipipo VPN Bot - Usando Pyker v1.0+