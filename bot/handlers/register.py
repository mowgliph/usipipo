# bot/handlers/register.py

from __future__ import annotations
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import crud_users
from bot.handlers.helpers import log_and_notify, log_error_and_notify
from bot.services.register import register_user
from bot.config import is_superadmin_tg
from bot.services.exceptions import RegistrationError
import asyncio

async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /register handler asíncrono.
    - Asegura usuario en DB usando services.register.register_user
    - Marca superadmin si corresponde según config/superadmins.py
    - Usa helpers asíncronos para logging y notificaciones
    """
    if not update.effective_chat or not update.message or not update.effective_user:
        return

    tg_user = update.effective_user
    chat_id = update.effective_chat.id
    bot = context.bot
    db_user = None

    try:
        tg_payload = {
            "id": tg_user.id,
            "username": tg_user.username,
            "first_name": tg_user.first_name,
            "last_name": tg_user.last_name,
        }

        async with AsyncSession(bot.get("db")) as session:
            # Registrar al usuario en la base de datos
            result = await register_user(
                session,
                tg_payload,
                create_trial=True,
                trial_days=7,
                notify=None,
            )
            db_user = result["user"]

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
            if is_superadmin_tg(tg_user.id):
                await crud_users.set_user_superadmin(session, db_user.id, True, commit=True)
                keyboard.append([
                    InlineKeyboardButton("⚙️ Panel de Administración", callback_data="admin")
                ])
                await update.message.reply_text(
                    f"👑 <b>Usuario reconocido como Superadmin</b>\n"
                    f"ID <code>{tg_user.id}</code> activado con privilegios completos.",
                    parse_mode="HTML"
                )
                await asyncio.sleep(2)  # Pequeña pausa

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
            if not is_superadmin_tg(tg_user.id):
                welcome_msg = "✅ Usuario registrado correctamente.\n\n" + welcome_msg

            # Enviar mensaje con botones
            await update.message.reply_text(
                welcome_msg,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )

            # Para mantener compatibilidad con el log_and_notify existente
            status_msg = "Mensaje de bienvenida enviado con botones de comandos"

            # Log + notify outside DB context; pass None session if helpers don't need the DB here
            await log_and_notify(
                None,
                bot,
                chat_id,
                getattr(db_user, "id", None),
                "command_register",
                "Usuario ejecutó /register",
                status_msg,
                parse_mode="HTML",
            )

    except RegistrationError as re:
        await log_error_and_notify(
            None,
            bot,
            chat_id,
            getattr(db_user, "id", None),
            "command_register",
            re,
            public_message="Ha ocurrido un error registrando tu usuario. Intenta más tarde.",
        )
    except Exception as e:
        await log_error_and_notify(
            None,
            bot,
            chat_id,
            getattr(db_user, "id", None),
            "command_register",
            e,
            public_message="Ha ocurrido un error registrando tu usuario. Intenta más tarde.",
        )
    except Exception as e:
        await log_error_and_notify(
            None,
            bot,
            chat_id,
            getattr(db_user, "id", None),
            "command_register",
            e,
            public_message="Ha ocurrido un error registrando tu usuario. Intenta más tarde.",
        )