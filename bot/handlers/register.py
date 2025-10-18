# bot/handlers/register.py

from __future__ import annotations

import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from config import superadmins as config_superadmins
from database.db import AsyncSessionLocal
from services import register as register_service
from services import admin as admin_service
from utils.helpers import log_and_notify, log_error_and_notify

logger = logging.getLogger("usipipo.handlers.register")

async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /register handler asíncrono.
    - Asegura usuario en DB usando service layer
    - Marca superadmin si corresponde según config/superadmins.py
    - Usa helpers asíncronos para logging y notificaciones
    """
    if not update.effective_chat or not update.message or not update.effective_user:
        return

    tg_user = update.effective_user
    chat_id = update.effective_chat.id
    bot = context.bot

    async with AsyncSessionLocal() as session:
        db_user = None
        try:
            # Registrar usuario usando service layer
            tg_payload = {
                "id": tg_user.id,
                "username": tg_user.username,
                "first_name": tg_user.first_name,
                "last_name": tg_user.last_name,
            }

            result = await register_service.register_user(
                session,
                tg_payload,
                create_trial=True,
                trial_days=None,  # Usará valor por defecto de config
                notify=None,  # Por ahora sin notificaciones
            )
            db_user = result["user"]
            trial_created = result.get("trial") is not None

            # Crear teclado inline con botones de comandos
            keyboard = [
                [
                    InlineKeyboardButton("🆓 Obtener VPN de prueba", callback_data="trialvpn"),
                    InlineKeyboardButton("🛒 Comprar VPN", callback_data="newvpn")
                ],
                [
                    InlineKeyboardButton("📝 Mis registros", callback_data="mylogs"),
                    InlineKeyboardButton("❓ Ayuda", callback_data="help")
                ]
            ]

            # Si es superadmin, configurar y mostrar mensaje especial
            if config_superadmins.is_superadmin_tg(tg_user.id):
                await admin_service.set_superadmin(session, db_user.id, acting_user_id=None, commit=True)
                keyboard.append([
                    InlineKeyboardButton("⚙️ Panel de Administración", callback_data="admin")
                ])
                await update.message.reply_text(
                    f"👑 <b>Usuario reconocido como Superadmin</b>\n"
                    f"ID <code>{tg_user.id}</code> activado con privilegios completos.",
                    parse_mode="HTML"
                )

            # Crear el teclado inline
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Mensaje de bienvenida para todos los usuarios
            welcome_msg = (
                f"✨ <b>¡Hola {tg_user.first_name}!</b> ✨\n\n"
                "¡Bienvenido a <b>uSipipo</b>! 🚀\n\n"
                "Aquí podrás gestionar tus servicios VPN de forma rápida y segura. "
                "Estoy aquí para ayudarte con lo que necesites.\n\n"
                "🔹 <b>¿Qué te gustaría hacer?</b>"
            )

            # Si no es superadmin, incluir mensaje de registro exitoso
            if not config_superadmins.is_superadmin_tg(tg_user.id):
                welcome_msg = "✅ Usuario registrado correctamente.\n\n" + welcome_msg

            # Enviar mensaje con botones
            await update.message.reply_text(
                welcome_msg,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )

            # Log + notify
            status_msg = (
                f"Mensaje de bienvenida enviado con botones de comandos. "
                f"Trial creado: {trial_created}"
            )
            await log_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=db_user.id,
                action="command_register",
                details="Usuario ejecutó /register",
                message=status_msg,
                parse_mode="HTML",
            )

        except Exception as e:  # pylint: disable=broad-except
            logger.exception(
                "Error in register_command: %s",
                type(e).__name__,
                extra={"user_id": getattr(db_user, "id", None)}
            )
            await log_error_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=getattr(db_user, "id", None),
                action="command_register",
                error=e,
                public_message="Ha ocurrido un error registrando tu usuario. Intenta más tarde.",
            )
