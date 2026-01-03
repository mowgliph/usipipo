"""
Sistema de logging centralizado para el bot uSipipo.
Integra con loguru y el sistema de monitorización.

Author: uSipipo Team
Version: 1.0.0
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from loguru import logger

from config import settings


class BotLogger:
    """Sistema de logging centralizado para el bot."""
    
    def __init__(self):
        self.monitoring_handler = None
        self._setup_logger()
    
    def _setup_logger(self):
        """Configura loguru con los ajustes del sistema."""
        # Remover handlers por defecto
        logger.remove()
        
        # Configurar nivel de log
        log_level = settings.LOG_LEVEL
        
        # Console handler (para desarrollo)
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level,
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        # File handler (para producción)
        log_file = Path(settings.LOG_FILE_PATH)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # Error file handler (solo errores y críticos)
        error_file = log_file.parent / "errors.log"
        logger.add(
            error_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation="5 MB",
            retention="60 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
    
    def set_monitoring_handler(self, monitoring_handler):
        """Establece el handler de monitorización para logs en tiempo real."""
        self.monitoring_handler = monitoring_handler
    
    def log_bot_event(self, level: str, message: str, user_id: Optional[int] = None, **kwargs):
        """Registra un evento del bot y lo añade al sistema de monitorización."""
        # Log con loguru
        log_method = getattr(logger, level.lower(), logger.info)
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
        """Registra errores con contexto."""
        message = f"Error: {str(error)}"
        if context:
            message = f"{context} - {message}"
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


# Instancia global del logger
bot_logger = BotLogger()


def get_logger() -> BotLogger:
    """Retorna la instancia global del logger del bot."""
    return bot_logger
