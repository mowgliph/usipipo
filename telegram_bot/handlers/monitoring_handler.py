import logging
from datetime import datetime, timedelta
from typing import List, Optional
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from loguru import logger

from telegram_bot.messages.messages import Messages


class MonitoringHandler:
    def __init__(self, admin_telegram_id: int):
        self.admin_telegram_id = admin_telegram_id
        self.bot_logs: List[str] = []
        self.max_logs = 1000  # Máximo número de logs a mantener en memoria
        
    def add_log(self, level: str, message: str, user_id: Optional[int] = None):
        """Añade un log al sistema de monitorización."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_info = f" [User:{user_id}]" if user_id else ""
        log_entry = f"[{timestamp}] [{level}]{user_info} {message}"
        
        self.bot_logs.append(log_entry)
        
        # Mantener solo los últimos max_logs
        if len(self.bot_logs) > self.max_logs:
            self.bot_logs = self.bot_logs[-self.max_logs:]
    
    def get_recent_logs(self, lines: int = 50) -> List[str]:
        """Obtiene los logs más recientes."""
        return self.bot_logs[-lines:] if self.bot_logs else ["No hay logs disponibles"]
    
    def get_logs_by_level(self, level: str, hours: int = 24) -> List[str]:
        """Filtra logs por nivel y tiempo."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        filtered_logs = []
        
        for log in self.bot_logs:
            # Extraer timestamp y nivel del log
            try:
                timestamp_str = log.split("]")[0][1:]
                log_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                
                if log_time >= cutoff_time and f"[{level}]" in log:
                    filtered_logs.append(log)
            except (ValueError, IndexError):
                continue
                
        return filtered_logs if filtered_logs else [f"No hay logs de nivel {level} en las últimas {hours} horas"]
    
    async def logs_command_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /logs - solo para admin."""
        user_id = update.effective_user.id
        
        # Verificar si es admin
        if user_id != self.admin_telegram_id:
            await update.message.reply_text("❌ Comando no autorizado")
            return
        
        # Parsear argumentos
        args = context.args if context.args else []
        lines = 10  # Por defecto 10 logs
        level_filter = None
        
        if args:
            try:
                if args[0].startswith("/") and len(args[0]) > 1:
                    # Formato: /logs /ERROR 100
                    level_filter = args[0][1:].upper()
                    if len(args) > 1:
                        lines = int(args[1])
                else:
                    # Formato: /logs 100 o /logs ERROR
                    if args[0].isdigit():
                        lines = int(args[0])
                    else:
                        level_filter = args[0].upper()
                        if len(args) > 1 and args[1].isdigit():
                            lines = int(args[1])
            except (ValueError, IndexError):
                pass
        
        # Obtener logs
        if level_filter:
            logs = self.get_logs_by_level(level_filter)
            title = f"📋 <b>Logs Nivel {level_filter}</b>"
        else:
            logs = self.get_recent_logs(lines)
            title = f"📋 <b>Últimos {len(logs)} Logs</b>"
        
        # Formatear respuesta con HTML
        if not logs:
            logs_text = "No hay logs disponibles"
        else:
            # Limitar a 10 líneas por defecto y formatear con HTML
            logs_to_show = logs[-10:] if len(logs) > 10 else logs
            logs_text = ""
            for log in logs_to_show:
                # Reemplazar caracteres especiales para HTML
                log_html = log.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                # Colorear según nivel
                if "[ERROR]" in log_html:
                    log_html = f"<code style='color: #ff6b6b;'>{log_html}</code>"
                elif "[WARNING]" in log_html:
                    log_html = f"<code style='color: #ffa726;'>{log_html}</code>"
                elif "[INFO]" in log_html:
                    log_html = f"<code style='color: #66bb6a;'>{log_html}</code>"
                else:
                    log_html = f"<code>{log_html}</code>"
                logs_text += f"• {log_html}\n"
        
        # Límite de caracteres de Telegram (4096)
        max_length = 4000  # Dejar margen de seguridad
        
        if len(logs_text) > max_length:
            # Dividir en múltiples mensajes si es muy largo
            lines_list = logs_text.split("\n")
            current_message = title + "\n\n"
            messages = []
            
            for line in lines_list:
                if len(current_message + line + "\n") > max_length:
                    messages.append(current_message)
                    current_message = title + f" (Parte {len(messages) + 1})\n\n" + line + "\n"
                else:
                    current_message += line + "\n"
            
            if current_message.strip():
                messages.append(current_message)
            
            # Enviar mensajes
            for message in messages:
                await update.message.reply_text(
                    message,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
        else:
            # Mensaje único
            await update.message.reply_text(
                f"{title}\n\n{logs_text}",
                parse_mode="HTML",
                disable_web_page_preview=True
            )
    
    async def stats_command_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /stats - estadísticas del bot."""
        user_id = update.effective_user.id
        
        # Verificar si es admin
        if user_id != self.admin_telegram_id:
            await update.message.reply_text("❌ Comando no autorizado")
            return
        
        # Contar logs por nivel
        error_count = len(self.get_logs_by_level("ERROR"))
        warning_count = len(self.get_logs_by_level("WARNING"))
        info_count = len(self.get_logs_by_level("INFO"))
        
        stats_text = f"""📊 <b>Estadísticas del Bot</b>

🔴 <b>Errores (24h):</b> {error_count}
🟡 <b>Advertencias (24h):</b> {warning_count}
🟢 <b>Info (24h):</b> {info_count}
📝 <b>Total Logs:</b> {len(self.bot_logs)}

🕐 <b>Última Actualización:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        await update.message.reply_text(stats_text, parse_mode="HTML")
    
    def get_handlers(self):
        """Retorna los handlers de monitorización."""
        return [
            CommandHandler("logs", self.logs_command_handler),
            CommandHandler("stats", self.stats_command_handler),
        ]


def get_monitoring_handlers(admin_telegram_id: int):
    """Función para obtener los handlers de monitorización."""
    handler = MonitoringHandler(admin_telegram_id)
    return handler.get_handlers(), handler
