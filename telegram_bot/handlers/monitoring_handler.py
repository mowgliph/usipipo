import logging
from datetime import datetime, timedelta
from typing import List, Optional
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from utils.logger import logger

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
        lines = 15  # Por defecto 15 logs (aumentado para mejor visibilidad)

        if args:
            try:
                if args[0].isdigit():
                    lines = min(int(args[0]), 50)  # Máximo 50 líneas para evitar sobrecarga
            except (ValueError, IndexError):
                pass

        # Obtener logs del archivo usando el logger unificado
        logs_text = logger.get_last_logs(lines)

        # Información adicional
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        footer = f"\n\n🕐 <i>Generado el {timestamp}</i>"

        # Formatear respuesta profesional
        if "❌ Error leyendo logs" in logs_text or "El archivo de log aún no existe" in logs_text:
            title = "📋 <b>Logs del Sistema</b>"
            message = f"{title}\n\n{logs_text}{footer}"
        else:
            title = f"📋 <b>Últimos {lines} Logs del Sistema</b>"

            # Procesar y formatear las líneas de log
            lines_list = logs_text.strip().split('\n')
            formatted_logs = []

            for line in lines_list:
                if line.strip():
                    # Detectar nivel de log y agregar emoji apropiado
                    if 'ERROR' in line.upper():
                        emoji = "🔴"
                    elif 'WARNING' in line.upper():
                        emoji = "🟡"
                    elif 'INFO' in line.upper():
                        emoji = "🟢"
                    elif 'DEBUG' in line.upper():
                        emoji = "🔵"
                    else:
                        emoji = "⚪"

                    # Escapar caracteres especiales para HTML
                    safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    formatted_logs.append(f"{emoji} <code>{safe_line}</code>")

            logs_content = "\n".join(formatted_logs)
            message = f"{title}\n\n{logs_content}{footer}"

        # Límite de caracteres de Telegram (4096)
        max_length = 4000

        if len(message) > max_length:
            # Dividir en múltiples mensajes si es muy largo
            if "❌ Error leyendo logs" in logs_text or "El archivo de log aún no existe" in logs_text:
                # Para mensajes de error, enviar completo
                await update.message.reply_text(
                    message,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
            else:
                # Dividir logs formateados
                parts = []
                current_part = f"{title}\n\n"

                for line in formatted_logs:
                    if len(current_part + line + "\n") > max_length:
                        parts.append(current_part)
                        current_part = f"{title} (Parte {len(parts) + 1})\n\n{line}\n"
                    else:
                        current_part += line + "\n"

                if current_part.strip():
                    parts.append(current_part)

                # Enviar mensajes
                for i, part in enumerate(parts):
                    is_last = (i == len(parts) - 1)
                    await update.message.reply_text(
                        part + footer if is_last else part,
                        parse_mode="HTML",
                        disable_web_page_preview=True
                    )
        else:
            # Mensaje único
            await update.message.reply_text(
                message,
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
