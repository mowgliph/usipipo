"""
Sistema de logging unificado para el bot uSipipo.
Integra lo mejor de logger.py y bot_logger.py con configuración flexible.

Author: uSipipo Team
Version: 2.0.0
"""

import logging
import sys
import traceback
from pathlib import Path
from typing import Optional, Union
try:
    from loguru import logger as _loguru_logger
except Exception:
    # Fallback to stdlib logging if loguru isn't available (useful for tests/environments
    # where optional deps aren't installed). The proxy implements the minimal API used below.
    import logging as _std_logging

    _std_logger = _std_logging.getLogger("usipipo")
    _std_logger.setLevel(_std_logging.INFO)
    if not _std_logger.handlers:
        _handler = _std_logging.StreamHandler(sys.stdout)
        _handler.setFormatter(_std_logging.Formatter("%(asctime)s | %(levelname)s | %(name)s:%(lineno)s - %(message)s"))
        _std_logger.addHandler(_handler)

    class _StdLoggerProxy:
        def debug(self, *args, **kwargs):
            _std_logger.debug(*args, **kwargs)
        def info(self, *args, **kwargs):
            _std_logger.info(*args, **kwargs)
        def warning(self, *args, **kwargs):
            _std_logger.warning(*args, **kwargs)
        def error(self, *args, **kwargs):
            _std_logger.error(*args, **kwargs)
        def critical(self, *args, **kwargs):
            _std_logger.critical(*args, **kwargs)
        def remove(self):
            # no-op for proxy
            return
        def add(self, *args, **kwargs):
            # no-op for proxy
            return

    _loguru_logger = _StdLoggerProxy()


class Logger:
    """
    Logger unificado que combina las mejores características de logger.py y bot_logger.py.
    Se inicializa de forma mínima para evitar importaciones circulares con `config`.
    Use `configure_from_settings(settings)` para aplicar la configuración completa cuando `settings` esté disponible.
    """

    def __init__(self):
        self.monitoring_handler = None
        self._configured_with_settings = False
        self.log_file_path = None
        # Initialize a minimal console logger so `logger` can be imported safely during bootstrap
        self._setup_basic_logger()

    def _setup_basic_logger(self):
        """Minimal console-only logger (used during early import to avoid circular imports)."""
        _loguru_logger.remove()
        _loguru_logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO",
            colorize=True,
            backtrace=True,
            diagnose=False
        )

    def configure_from_settings(self, settings):
        """Apply full configuration using provided Settings object."""
        if self._configured_with_settings:
            return
        # Set up handlers and levels based on settings
        self._setup_logger(settings)
        self.log_file_path = settings.LOG_FILE_PATH
        self._configured_with_settings = True

    def _setup_logger(self, settings):
        """Configura loguru con los ajustes provistos en el objeto `settings`."""
        # Remover handlers por defecto
        _loguru_logger.remove()

        # Configurar nivel de log desde settings
        log_level = settings.LOG_LEVEL

        # Console handler (para desarrollo)
        _loguru_logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level,
            colorize=True,
            backtrace=True,
            diagnose=True
        )

        # File handler (para producción) - rotativo como en logger.py
        log_file = Path(settings.LOG_FILE_PATH)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        _loguru_logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )

        # Error file handler (solo errores y críticos) - como en bot_logger.py
        error_file = log_file.parent / "errors.log"
        _loguru_logger.add(
            error_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation="5 MB",
            retention="60 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )

    def _format_clean_traceback(self, error: Exception) -> str:
        """
        Formatea un traceback limpio, enfocándose en el código de la aplicación
        y evitando ruido de bibliotecas estándar.

        Args:
            error: La excepción capturada

        Returns:
            String con el traceback formateado
        """
        tb_lines = traceback.format_exception(type(error), error, error.__traceback__)

        # Filtrar líneas irrelevantes (de bibliotecas estándar)
        filtered_lines = []
        skip_next = False

        for line in tb_lines:
            # Saltar líneas de bibliotecas estándar comunes
            if any(lib in line for lib in ['/lib/python', 'site-packages', '<frozen']):
                if 'File "' in line and not any(app_dir in line for app_dir in ['usipipo', 'application', 'telegram_bot', 'infrastructure', 'domain']):
                    skip_next = True
                    continue
            if skip_next:
                skip_next = False
                continue

            filtered_lines.append(line)

        # Si se filtró demasiado, usar el original
        if len(filtered_lines) < 3:
            filtered_lines = tb_lines

        # Limitar longitud para producción
        tb_str = "".join(filtered_lines).strip()
        if len(tb_str) > 2000:  # Limitar a 2000 caracteres
            tb_str = tb_str[:2000] + "\n... (traceback truncado)"

        return tb_str

    def set_monitoring_handler(self, monitoring_handler):
        """Establece el handler de monitorización para logs en tiempo real."""
        self.monitoring_handler = monitoring_handler

    # Métodos de logging estándar (compatibles con logging estándar)
    def debug(self, message: str, *args, **kwargs):
        """Log de nivel DEBUG."""
        _loguru_logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log de nivel INFO."""
        _loguru_logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log de nivel WARNING."""
        _loguru_logger.warning(message, *args, **kwargs)

    def error(self, message: Union[str, Exception], error: Optional[Exception] = None, *args, **kwargs):
        """Log de nivel ERROR con manejo opcional de excepciones.

        Permite pasar directamente una Exception como primer argumento
        (compatibilidad con llamadas existentes que hacían `logger.error(e, ...)`).
        """
        # Compatibilidad: si pasaron la excepción como primer arg
        if isinstance(message, Exception) and error is None:
            error = message
            message = str(message)

        if error:
            # Obtener traceback completo y limpio
            tb_str = self._format_clean_traceback(error)
            message = f"{message}\n   ╚══ 💥 Detalles del Error:\n{tb_str}"

        _loguru_logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log de nivel CRITICAL."""
        _loguru_logger.critical(message, *args, **kwargs)

    def log(self, level: str, message: str, *args, **kwargs):
        """Log genérico con nivel especificado."""
        log_method = getattr(_loguru_logger, level.lower(), _loguru_logger.info)
        log_method(message, *args, **kwargs)

    # Método compatible con logger.py
    def add_log_line(self, message: str, level: str = "INFO", error: Optional[Exception] = None):
        """
        Registra un mensaje en el log (compatible con logger.py).

        Args:
            message (str): El mensaje a registrar.
            level (str): "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
            error (Exception, opcional): El objeto de excepción si ocurrió un error.
        """
        if error:
            level = "ERROR"
            tb_str = self._format_clean_traceback(error)
            message = f"{message}\n   ╚══ 💥 Detalles del Error:\n{tb_str}"

        self.log(level, message)

    # Métodos especializados de bot_logger.py
    def log_bot_event(self, level: str, message: str, user_id: Optional[int] = None, **kwargs):
        """Registra un evento del bot y lo añade al sistema de monitorización."""
        # Log con loguru
        log_method = getattr(_loguru_logger, level.lower(), _loguru_logger.info)
        extra_info = f"[User:{user_id}]" if user_id else ""
        log_method(f"{extra_info} {message}", **kwargs)

        # Añadir al sistema de monitorización si está disponible
        if self.monitoring_handler:
            self.monitoring_handler.add_log(level.upper(), message, user_id)

    def log_user_action(self, action: str, user_id: int, details: Optional[str] = None):
        """Registra acciones de usuarios."""
        message = f"User action: {action}"
        if details:
            message += f" - {details}"
        self.log_bot_event("INFO", message, user_id)

    def log_error(self, error: Exception, context: Optional[str] = None, user_id: Optional[int] = None):
        """Registra errores con contexto y traceback limpio."""
        message = f"Error: {str(error)}"
        if context:
            message = f"{context} - {message}"

        # Incluir traceback limpio
        tb_str = self._format_clean_traceback(error)
        message += f"\nTraceback:\n{tb_str}"

        self.log_bot_event("ERROR", message, user_id)

    def log_vpn_operation(self, operation: str, success: bool, user_id: Optional[int] = None, details: Optional[str] = None):
        """Registra operaciones VPN."""
        level = "INFO" if success else "ERROR"
        status = "✅" if success else "❌"
        message = f"VPN {operation} {status}"
        if details:
            message += f" - {details}"
        self.log_bot_event(level, message, user_id)

    def log_payment_event(self, event_type: str, amount: int, user_id: int, success: bool, details: Optional[str] = None):
        """Registra eventos de pagos."""
        level = "INFO" if success else "ERROR"
        status = "✅" if success else "❌"
        message = f"Payment {event_type} {status} - {amount} stars"
        if details:
            message += f" - {details}"
        self.log_bot_event(level, message, user_id)

    def log_referral_event(self, event_type: str, user_id: int, details: Optional[str] = None):
        """Registra eventos de referidos."""
        message = f"Referral {event_type}"
        if details:
            message += f" - {details}"
        self.log_bot_event("INFO", message, user_id)

    def log_system_event(self, event: str, level: str = "INFO", details: Optional[str] = None):
        """Registra eventos del sistema."""
        message = f"System: {event}"
        if details:
            message += f" - {details}"
        self.log_bot_event(level, message)

    # Utilidades adicionales
    def get_last_logs(self, lines: int = 15) -> str:
        """
        Devuelve las últimas N líneas del archivo de log de forma segura.
        Compatible con logger.py.
        """
        log_file_path = self.log_file_path
        if not log_file_path:
            try:
                from config import settings
                log_file_path = settings.LOG_FILE_PATH
            except Exception:
                return "📂 El archivo de log aún no existe."

        log_file = Path(log_file_path)
        if not log_file.exists():
            return "📂 El archivo de log aún no existe."

        try:
            with open(log_file, "r", encoding="utf-8", errors='ignore') as f:
                all_lines = f.readlines()

                if len(all_lines) < lines:
                    return "".join(all_lines)

                return "".join(all_lines[-lines:])
        except Exception as e:
            return f"❌ Error leyendo logs: {str(e)}"


# Instancia global del logger unificado
logger = Logger()


def get_logger() -> Logger:
    """Retorna la instancia global del logger unificado."""
    return logger