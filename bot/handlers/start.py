# bot/handlers/start.py
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from utils.helpers import log_and_notify, log_error_and_notify, safe_chat_id_from_update

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /start handler asíncrono.
    Envía mensaje de bienvenida y muestra un teclado con comandos útiles.
    Registra la acción mediante log_and_notify (audit/logger) y envía el mensaje con botones.
    """
    tg_user = update.effective_user
    bot = context.bot
    chat_id = safe_chat_id_from_update(update)

    welcome_msg = (
        f"¡Hola <b>{tg_user.first_name}</b>! 👋 Bienvenido a <b>uSipipo</b> 🚀\n\n"
        "Aquí podrás generar configuraciones de VPN <b>Outline</b> y <b>WireGuard</b> "
        "de forma sencilla, rápida y segura.\n\n"
        "Usa <code>/help</code> para ver los comandos disponibles.\n"
        "👉 Recuerda registrarte primero con <code>/register</code>."
    )

    # Teclado rápido con comandos frecuentes
    keyboard = [
        [KeyboardButton("/register"), KeyboardButton("/newvpn")],
        [KeyboardButton("/trialvpn wireguard"), KeyboardButton("/trialvpn outline")],
        [KeyboardButton("/info")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    try:
        # Registrar auditoría / log (no enviamos el mensaje desde helpers aquí para que podamos añadir botones)
        await log_and_notify(
            None,               # session (no DB op aquí)
            None,               # bot None -> helpers solo guardará logger/audit if session provided; here acts as logger step
            None,               # chat_id None to avoid double-send
            None,               # user_id None (no DB user yet)
            "command_start",    # action
            "Usuario ejecutó /start",  # details
            welcome_msg,        # message
            parse_mode="HTML",
        )

        # Enviar mensaje con teclado
        await bot.send_message(chat_id=chat_id, text=welcome_msg, parse_mode="HTML", reply_markup=reply_markup)

    except Exception as e:
        await log_error_and_notify(
            None,
            bot,
            chat_id,
            None,
            "command_start",
            e,
            public_message="Ha ocurrido un error al procesar /start. Intenta más tarde.",
        )
