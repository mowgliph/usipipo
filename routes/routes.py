# routes/routes.py

from telegram.ext import Application, CommandHandler

# =============================
# 📜 Importar handlers de comandos
# =============================
from bot.handlers.logs import register_logs_handlers
from bot.handlers.status import status_command
from bot.handlers.help import help_command
from bot.handlers.admin import register_admin_handlers
from bot.handlers.myid import myid_command
from bot.handlers.roles import register_roles_handlers
from bot.handlers.perfil import profile_command, whois_command
from bot.handlers.vpn import register_vpn_handlers
from bot.handlers.register import register_command
from bot.handlers.start import start_command
from bot.handlers.ms import ms_handler


def register_handlers(app: Application):
    """
    Registra todos los handlers de comandos y eventos en la aplicación Telegram.
    """
    # --------------------------
    # Comandos básicos y de admin
    # --------------------------
    app.add_handler(CommandHandler("start", start_command))
    register_logs_handlers(app) 
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("help", help_command))
    register_admin_handlers(app)
    app.add_handler(CommandHandler("myid", myid_command))
    register_roles_handlers(app)
    app.add_handler(CommandHandler("ms", ms_handler))

    # --------------------------
    # Perfil, roles y VPN
    # --------------------------
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("whois", whois_command))
    app.add_handler(CommandHandler("register", register_command))
    register_vpn_handlers(app)