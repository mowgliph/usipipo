🚀 Guía de Instalación y Puesta en Marcha de uSipipo
Esta guía detalla los tres pasos fundamentales para desplegar y ejecutar el bot uSipipo en tu servidor o sistema personal.
🛠 Requisitos Previos
Asegúrate de tener instalado:
 * Git: Para clonar el repositorio.
 * Node.js: Versión 18 o superior.
 * Docker: Requerido para la instalación de Outline (gestionado por install.sh).
 * PM2 (Process Manager 2): Utilizado para gestionar la aplicación en producción.
📝 Parte 1: Clonación y Configuración del Servidor VPN
En esta fase, clonarás el proyecto y utilizarás el script de instalación provisto para configurar los servicios VPN requeridos.
 * Clonar el Repositorio:
   Navega hasta el directorio donde deseas alojar el proyecto y clona el repositorio:
   git clone https://github.com/mowgliph/usipipo.git
cd usipipo

 * Instalar Dependencias de Node.js:
   Instala todos los módulos necesarios para que el bot funcione:
   npm install

 * Dar Permisos y Ejecutar el Script de Instalación:
   El script install.sh gestionará la instalación de Docker, Outline y WireGuard, y creará el archivo .env con las variables de API.
   # 1. Dar permisos de ejecución
chmod +x install.sh

# 2. Ejecutar el script (requiere permisos de root/sudo para instalar VPNs)
sudo ./install.sh

 * Selección de Servidor:
   Dentro del menú interactivo de install.sh, selecciona la opción para instalar el servidor VPN que deseas (Outline, WireGuard o ambos). El script extraerá automáticamente los secretos de API y los guardará en el archivo .env.
🔑 Parte 2: Configuración de Variables de Acceso del Bot
El script install.sh crea el archivo .env con las variables del servidor VPN, pero requiere que añadas manualmente las credenciales de Telegram.
 * Localizar y Editar el Archivo .env:
   El archivo .env se encuentra en el directorio raíz del proyecto (/usipipo). Ábrelo con un editor de texto (como nano):
   nano .env

 * Insertar Token y Admin ID:
   Añade o edita las siguientes variables cruciales:
   * TELEGRAM_TOKEN: El token de tu bot de Telegram (obtenido desde BotFather).
   * AUTHORIZED_USERS: Tu ID de usuario de Telegram. Es el super administrador del bot (ej. 1058749165 o 123456789). Si necesitas varios administradores, sepáralos por comas.
   Ejemplo del contenido mínimo requerido:
   # ... otras variables generadas por install.sh ...
TELEGRAM_TOKEN=123456789:ABC-DEF-GHIJKLMNOPQRST
AUTHORIZED_USERS=123456789,987654321
# ...

 * Guardar y Cerrar:
   Guarda los cambios en el archivo .env y ciérralo.
🚀 Parte 3: Puesta en Marcha Final (Producción)
Dado que la aplicación debe interactuar con los servicios VPN y APIs a nivel de sistema (puertos, configuraciones de red, etc.), se debe ejecutar PM2 con privilegios de root (sudo) para evitar errores de permisos (EACCES).
 * Instalar PM2 globalmente (Si no está instalado):
   npm install pm2 -g

 * Iniciar el Bot como Root (Producción):
   Inicia la aplicación usando el archivo de configuración pm2.config.js con sudo. Este archivo define el proceso como usipipo.
   # Inicia el proceso 'usipipo'
sudo pm2 start pm2.config.js

 * Verificar y Guardar la Configuración:
   * Verificar logs: Asegúrate de que no haya errores de inicio.
     sudo pm2 logs usipipo

   * Guardar estado: Esto asegura que el bot reinicie automáticamente después de cualquier reinicio del servidor.
     sudo pm2 save

   * Configurar arranque automático: Si es necesario, genera el script de inicio de sistema para root (solo haz esto una vez):
     sudo pm2 startup

 * Configuración de Rotación de Logs (Ahorro de Almacenamiento):
   Para evitar que los archivos de log (pm2-out.log y pm2-error.log) consuman todo el espacio del disco, instala y configura la rotación automática de logs.
   # Instalar el módulo de rotación de logs (como root)
sudo pm2 install pm2-logrotate

# Configurar el límite de tamaño por archivo (ej. 10MB)
sudo pm2 set pm2-logrotate:max_size 10M

# Configurar cuántos archivos rotados mantener (ej. 5 archivos)
sudo pm2 set pm2-logrotate:retain 5

# Activar compresión para archivos antiguos (.gz)
sudo pm2 set pm2-logrotate:compress true

¡Tu bot uSipipo ya estará corriendo de forma robusta y con gestión automática de logs!
