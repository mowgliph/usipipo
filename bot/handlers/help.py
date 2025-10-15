from telegram import Update
from telegram.ext import ContextTypes
from database.db import SessionLocal
from database.crud import users as crud_user
from utils.helpers import log_and_notify, log_error_and_notify
from database import models


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Responde al comando /help mostrando los comandos disponibles según rol.
    """
    tg_user = update.effective_user
    db = SessionLocal()
    db_user = None

    try:
        # Buscar usuario en DB
        db_user = await crud_user.get_user_by_telegram_id(db, tg_user.id)
        user_id = db_user.id if db_user else None

        # Verificar si es admin o superadmin
        is_admin = crud_user.is_user_admin(db, user_id) if user_id else False
        is_superadmin = crud_user.is_user_superadmin(db, user_id) if user_id else False

        # Base para todos los usuarios
        help_msg = (
            "📖 <b>Comandos disponibles en uSipipo Bot:</b>\n\n"
            "👤 <b>Usuarios</b>\n"
            "  • /start – Iniciar el bot y ver bienvenida\n"
            "  • /register – Registrarte en la base de datos\n"
            "  • /help – Mostrar este menú de ayuda\n"
            "  • /myid – Ver tu ID de Telegram\n"
            "  • /profile – Ver tu perfil\n"
            "  • /whois &lt;@usuario|id&gt; – Consultar perfil de otro usuario\n\n"
            "🌐 <b>VPN</b>\n"
            "  • /trialvpn &lt;wireguard|outline&gt; – Solicitar un VPN de prueba (7 días)\n"
            "  • /newvpn &lt;wireguard|outline&gt; &lt;meses&gt; – Crear nueva VPN\n"
            "  • /myvpns – Listar tus configuraciones VPN\n"
            "  • /revokevpn &lt;id&gt; – Revocar una configuración VPN\n"
        )

        # Extensión para admins/superadmins
        if is_admin or is_superadmin:
            help_msg += (
                "\n🛠️ <b>Administración</b>\n"
                "  • /status – Ver estado del bot\n"
                "  • /logs – Ver acciones recientes\n"
                "  • /mylogs – Ver tus acciones registradas\n"
                "  • /promote &lt;id&gt; – Asignar admin\n"
                "  • /demote &lt;id&gt; – Quitar admin\n"
                "  • /setsuper &lt;id&gt; – Asignar superadmin\n"
                "  • /listadmins – Listar administradores\n"
                "  • /grantrole &lt;id&gt; &lt;rol&gt; – Asignar rol\n"
                "  • /revokerole &lt;id&gt; &lt;rol&gt; – Revocar rol\n"
            )

        # Log + notificación
        chat_id = update.effective_chat.id if update.effective_chat else None
        bot = context.bot
        await log_and_notify(
            db,
            bot,
            chat_id,
            str(user_id) if user_id else None,
            "command_help",
            "Usuario ejecutó /help",
            help_msg,
            parse_mode="HTML",
        )

    except Exception as e:
        chat_id = update.effective_chat.id if update.effective_chat else None
        bot = context.bot
        uid = db_user.id if 'db_user' in locals() and 'db_user' in locals() and isinstance(db_user, models.User) else None
        await log_error_and_notify(db, bot, chat_id, str(uid) if uid else None, "command_help", e)

    finally:
        db.close()