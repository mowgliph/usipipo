# bot/handlers/info.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.helpers import log_and_notify, log_error_and_notify, safe_chat_id_from_update

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /info handler: muestra información del bot, enlaces y botones rápidos.
    Similar a /start pero orientado a documentación breve y FAQ.
    """
    tg_user = update.effective_user
    bot = context.bot
    chat_id = safe_chat_id_from_update(update)

    info_msg = (
        f"ℹ️ Información de uSipipo\n\n"
        f"Hola <b>{tg_user.first_name}</b> — euSipipo te permite crear y administrar VPNs de Wireguard y Outline fácil, rapido y seguro.\n\n"
        "Comandos importantes:\n"
        "• <code>/register</code> — Registrar tu cuenta\n"
        "• <code>/trialvpn &lt;wireguard|outline&gt;</code> — Solicitar un trial de 7 días\n"
        "• <code>/newvpn</code> — Crear un config de VPN completa\n\n"
        "Soporte y seguridad:\n"
        "- Tus acciones quedan registradas para auditoría.\n"
        "- Los administradores reciben notificaciones de eventos relevantes.\n\n"
        "¿Listo para comenzar? Usa los botones debajo para ejecutar un comando."
    )

    keyboard = [
        [InlineKeyboardButton("Registrar", callback_data='/register'), InlineKeyboardButton("Nueva VPN", callback_data='/newvpn')],
        [InlineKeyboardButton("Trial Wireguard", callback_data='/trialvpn wireguard'), InlineKeyboardButton("Trial Outline", callback_data='/trialvpn outline')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        # Registrar auditoría / log (no enviar desde helpers para añadir botones)
        await log_and_notify(
            None,
            None,
            None,
            None,
            "command_info",
            "Usuario ejecutó /info",
            info_msg,
            parse_mode="HTML",
        )

        await bot.send_message(chat_id=chat_id, text=info_msg, parse_mode="HTML", reply_markup=reply_markup)

    except Exception as e:
        await log_error_and_notify(
            None,
            bot,
            chat_id,
            None,
            "command_info",
            e,
            public_message="Ha ocurrido un error mostrando la información. Intenta más tarde.",
        )
