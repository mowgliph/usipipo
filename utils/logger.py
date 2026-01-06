import logging
import os
import traceback
from logging.handlers import RotatingFileHandler

# Definimos ruta y aseguramos que la carpeta exista
LOG_DIR = "data"
LOG_FILE = os.path.join(LOG_DIR, "bot_activity.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# --- CONFIGURACIÓN DEL LOGGER ROBUSTO ---
# Creamos un logger específico para no mezclar con logs de librerías externas
logger = logging.getLogger("uSipipoBot")
logger.setLevel(logging.INFO)

# Evitar duplicar handlers si se recarga el módulo
if not logger.handlers:
    # Formato: [FECHA] [NIVEL] [ARCHIVO:LINEA] Mensaje
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # 1. Handler de Archivo (Rotativo: Máx 5MB, guarda 3 archivos previos)
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 2. Handler de Consola (Para ver en vivo en el VPS)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def add_log_line(message, level="INFO", error=None):
    """
    Registra un mensaje en el log.
    
    Args:
        message (str): El mensaje a registrar.
        level (str): "INFO", "WARNING", "ERROR".
        error (Exception, opcional): El objeto de excepción si ocurrió un error.
    """
    # Si hay un error, enriquecemos el mensaje con detalles técnicos
    if error:
        level = "ERROR"
        # Obtener el traceback limpio (solo la última llamada y el error real)
        tb_list = traceback.format_exception(None, error, error.__traceback__)
        
        # Filtramos para obtener la causa raíz (últimas lineas del traceback)
        # Esto nos da: "File x, line y, in z: Error..."
        trace_summary = "".join(tb_list[-2:]).strip() 
        
        message = f"{message}\n   ╚══ 💥 Causa Técnica: {trace_summary}"

    # Mapear niveles de texto a funciones de logging
    if level.upper() == "ERROR":
        logger.error(message)
    elif level.upper() == "WARNING":
        logger.warning(message)
    else:
        logger.info(message)

def get_last_logs(lines=15):
    """Devuelve las últimas N líneas del archivo de log de forma segura."""
    if not os.path.exists(LOG_FILE):
        return "📂 El archivo de log aún no existe."
    
    try:
        with open(LOG_FILE, "r", encoding="utf-8", errors='ignore') as f:
            # Leemos todo el archivo (con seek para archivos gigantes sería mejor, 
            # pero para 5MB esto es instantáneo)
            all_lines = f.readlines()
            
            # Si hay pocas líneas, devolvemos todo
            if len(all_lines) < lines:
                return "".join(all_lines)
                
            return "".join(all_lines[-lines:])
    except Exception as e:
        return f"❌ Error leyendo logs: {str(e)}"