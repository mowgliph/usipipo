# bot/handlers/qvapay.py

from __future__ import annotations

import logging
from datetime import datetime, timezone

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters, CommandHandler

from database.db import AsyncSessionLocal
from services import qvapay_user_client
from services.qvapay_user_client import QvaPayUserError, QvaPayUserAuthError, QvaPayUserBadRequestError
from database.crud import users as crud_users
from utils.helpers import log_and_notify, log_error_and_notify, send_success, send_warning, send_generic_error
from utils.permissions import require_registered

logger = logging.getLogger("usipipo.handlers.qvapay")

# Estados para ConversationHandler
WAITING_APP_ID, WAITING_USER_ID = range(2)


async def qvapay_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /qvapay - Muestra menú principal de gestión de QvaPay.
    """
    if not update.effective_chat or not update.message or not update.effective_user:
        return

    tg_user = update.effective_user
    bot = context.bot
    chat_id = update.effective_chat.id

    async with AsyncSessionLocal() as session:
        try:
            # Obtener usuario de DB
            db_user = await crud_users.get_user_by_telegram_id(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Debes registrarte primero con /register")
                return

            user_id = str(db_user.id)

            # Verificar si ya tiene cuenta vinculada
            is_linked = db_user.qvapay_app_id and db_user.qvapay_user_id

            # Crear mensaje y teclado
            if is_linked:
                msg = (
                    "💳 <b>Gestión de QvaPay</b>\n\n"
                    f"✅ <b>Cuenta vinculada</b>\n"
                    f"• APP ID: <code>{db_user.qvapay_app_id}</code>\n"
                    f"• USER ID: <code>{db_user.qvapay_user_id}</code>\n"
                    f"• Vinculada: {db_user.qvapay_linked_at.strftime('%Y-%m-%d %H:%M') if db_user.qvapay_linked_at else 'N/A'}\n\n"
                    "Selecciona una opción:"
                )
                keyboard = [
                    [InlineKeyboardButton("💰 Ver Balance", callback_data="qvapay_balance")],
                    [InlineKeyboardButton("🔗 Cambiar Cuenta", callback_data="qvapay_link")],
                    [InlineKeyboardButton("❌ Desvincular", callback_data="qvapay_unlink")],
                    [InlineKeyboardButton("❌ Cancelar", callback_data="qvapay_cancel")]
                ]
            else:
                msg = (
                    "💳 <b>Gestión de QvaPay</b>\n\n"
                    "❌ <b>No tienes cuenta vinculada</b>\n\n"
                    "Para usar QvaPay necesitas vincular tu cuenta primero."
                )
                keyboard = [
                    [InlineKeyboardButton("🔗 Vincular Cuenta", callback_data="qvapay_link")],
                    [InlineKeyboardButton("❌ Cancelar", callback_data="qvapay_cancel")]
                ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await log_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=user_id,
                action="command_qvapay",
                details="Abrió menú de gestión QvaPay",
                message=msg,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )

        except Exception as e:
            logger.exception("Error en qvapay_command: %s", type(e).__name__, extra={"tg_id": tg_user.id})
            await log_error_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=None,
                action="command_qvapay",
                error=e,
                public_message="Ha ocurrido un error al procesar /qvapay. Intenta más tarde.",
            )


async def qvapay_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Maneja callbacks de botones de QvaPay.
    """
    query = update.callback_query
    if not query or not query.data or not update.effective_user:
        return ConversationHandler.END

    await query.answer()
    tg_user = update.effective_user
    bot = context.bot
    chat_id = update.effective_chat.id if update.effective_chat else None
    callback_data = query.data

    async with AsyncSessionLocal() as session:
        try:
            # Obtener usuario
            db_user = await crud_users.get_user_by_telegram_id(session, tg_user.id)
            if not db_user:
                await query.edit_message_text(
                    "Debes registrarte primero con /register",
                    parse_mode="HTML"
                )
                return ConversationHandler.END

            user_id = str(db_user.id)

            if callback_data == "qvapay_balance":
                return await _handle_balance(session, query, db_user, bot, chat_id, user_id)

            elif callback_data == "qvapay_link":
                return await _handle_link_start(session, query, db_user, bot, chat_id, user_id, context)

            elif callback_data == "qvapay_unlink":
                return await _handle_unlink(session, query, db_user, bot, chat_id, user_id)

            elif callback_data == "qvapay_cancel":
                await query.edit_message_text(
                    "❌ Operación cancelada.",
                    parse_mode="HTML"
                )
                await log_and_notify(
                    session=session,
                    bot=bot,
                    chat_id=chat_id,
                    user_id=user_id,
                    action="qvapay_cancel",
                    details="Canceló operación QvaPay",
                    message="Operación cancelada",
                )
                return ConversationHandler.END

            else:
                await query.edit_message_text(
                    "Opción no válida.",
                    parse_mode="HTML"
                )
                return ConversationHandler.END

        except Exception as e:
            logger.exception("Error en qvapay_callback: %s", type(e).__name__, extra={"tg_id": tg_user.id, "callback_data": callback_data})
            await log_error_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=None,
                action="qvapay_callback_error",
                error=e,
                public_message="Ha ocurrido un error. Intenta más tarde.",
            )
            try:
                await query.edit_message_text(
                    "Ha ocurrido un error. Intenta más tarde.",
                    parse_mode="HTML"
                )
            except Exception:
                pass
            return ConversationHandler.END


async def _handle_balance(session, query, db_user, bot, chat_id, user_id) -> int:
    """Maneja ver balance."""
    try:
        if not db_user.qvapay_app_id or not db_user.qvapay_user_id:
            await query.edit_message_text(
                "❌ No tienes cuenta QvaPay vinculada.",
                parse_mode="HTML"
            )
            return ConversationHandler.END

        # Obtener balance usando QvaPay client
        client = qvapay_user_client.QvaPayUserClient()
        balance_data = await client.async_get_user_balance(db_user.qvapay_app_id, db_user.qvapay_user_id)

        # Formatear balance
        balances = balance_data.get("balances", {})
        balance_text = "\n".join([
            f"• <b>{currency}:</b> {amount}"
            for currency, amount in balances.items()
        ])

        msg = (
            "💰 <b>Balance de QvaPay</b>\n\n"
            f"{balance_text}\n\n"
            f"📅 Última verificación: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        )

        # Actualizar last_balance_check
        db_user.qvapay_last_balance_check = datetime.now(timezone.utc)
        await session.commit()

        keyboard = [[InlineKeyboardButton("⬅️ Volver", callback_data="qvapay_back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            msg,
            parse_mode="HTML",
            reply_markup=reply_markup
        )

        await log_and_notify(
            session=session,
            bot=bot,
            chat_id=chat_id,
            user_id=user_id,
            action="qvapay_balance_check",
            details="Consultó balance de QvaPay",
            message=msg,
        )

    except QvaPayUserAuthError:
        await query.edit_message_text(
            "❌ Error de autenticación. Verifica tus credenciales de QvaPay.",
            parse_mode="HTML"
        )
    except QvaPayUserError as e:
        await query.edit_message_text(
            f"❌ Error al obtener balance: {str(e)}",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.exception("Error obteniendo balance: %s", type(e).__name__)
        await query.edit_message_text(
            "❌ Error interno al obtener balance.",
            parse_mode="HTML"
        )

    return ConversationHandler.END


async def _handle_link_start(session, query, db_user, bot, chat_id, user_id, context) -> int:
    """Inicia flujo de vinculación."""
    msg = (
        "🔗 <b>Vincular cuenta QvaPay</b>\n\n"
        "Ingresa tu <b>APP ID</b> de QvaPay:\n\n"
        "💡 Puedes obtenerlo en: https://qvapay.com/app"
    )

    keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data="qvapay_cancel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        msg,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

    # Guardar estado en context
    context.user_data['qvapay_linking'] = True

    await log_and_notify(
        session=session,
        bot=bot,
        chat_id=chat_id,
        user_id=user_id,
        action="qvapay_link_start",
        details="Inició vinculación de cuenta QvaPay",
        message=msg,
    )

    return WAITING_APP_ID


async def _handle_unlink(session, query, db_user, bot, chat_id, user_id) -> int:
    """Desvincula cuenta QvaPay."""
    try:
        if not db_user.qvapay_app_id or not db_user.qvapay_user_id:
            await query.edit_message_text(
                "❌ No tienes cuenta QvaPay vinculada.",
                parse_mode="HTML"
            )
            return ConversationHandler.END

        # Limpiar campos
        db_user.qvapay_app_id = None
        db_user.qvapay_user_id = None
        db_user.qvapay_linked_at = None
        db_user.qvapay_last_balance_check = None
        await session.commit()

        msg = "✅ Cuenta QvaPay desvinculada correctamente."

        keyboard = [[InlineKeyboardButton("🔗 Vincular Nueva", callback_data="qvapay_link")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            msg,
            parse_mode="HTML",
            reply_markup=reply_markup
        )

        await log_and_notify(
            session=session,
            bot=bot,
            chat_id=chat_id,
            user_id=user_id,
            action="qvapay_unlink",
            details="Desvinculó cuenta QvaPay",
            message=msg,
        )

    except Exception as e:
        logger.exception("Error desvinculando cuenta: %s", type(e).__name__)
        await query.edit_message_text(
            "❌ Error al desvincular cuenta.",
            parse_mode="HTML"
        )

    return ConversationHandler.END


async def receive_app_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recibe APP ID del usuario."""
    if not update.message or not update.effective_user:
        return ConversationHandler.END

    tg_user = update.effective_user
    bot = context.bot
    chat_id = update.effective_chat.id if update.effective_chat else None
    app_id = update.message.text.strip() if update.message and update.message.text else ""

    async with AsyncSessionLocal() as session:
        try:
            db_user = await crud_users.get_user_by_telegram_id(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado.")
                return ConversationHandler.END

            user_id = str(db_user.id)

            # Validar APP ID básico
            if not app_id or len(app_id) < 10:
                await update.message.reply_text(
                    "❌ APP ID inválido. Debe tener al menos 10 caracteres.\n\n"
                    "Ingresa tu APP ID nuevamente:",
                    parse_mode="HTML"
                )
                return WAITING_APP_ID

            # Guardar APP ID temporalmente
            if context.user_data is not None:
                context.user_data['qvapay_app_id'] = app_id

            msg = (
                "🔗 <b>Vincular cuenta QvaPay</b>\n\n"
                f"APP ID: <code>{app_id}</code>\n\n"
                "Ahora ingresa tu <b>USER ID</b> de QvaPay:"
            )

            keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data="qvapay_cancel")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                msg,
                parse_mode="HTML",
                reply_markup=reply_markup
            )

            await log_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=user_id,
                action="qvapay_app_id_received",
                details=f"Recibió APP ID: {app_id[:8]}...",
                message=msg,
            )

            return WAITING_USER_ID

        except Exception as e:
            logger.exception("Error recibiendo APP ID: %s", type(e).__name__)
            await log_error_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=None,
                action="qvapay_app_id_error",
                error=e,
                public_message="Error procesando APP ID.",
            )
            return ConversationHandler.END


async def receive_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recibe USER ID y valida credenciales."""
    if not update.message or not update.effective_user:
        return ConversationHandler.END

    tg_user = update.effective_user
    bot = context.bot
    chat_id = update.effective_chat.id if update.effective_chat else None
    user_id_input = update.message.text.strip() if update.message and update.message.text else ""

    async with AsyncSessionLocal() as session:
        try:
            db_user = await crud_users.get_user_by_telegram_id(session, tg_user.id)
            if not db_user:
                await send_warning(update, "Usuario no encontrado.")
                return ConversationHandler.END

            user_id = str(db_user.id)
            app_id = context.user_data.get('qvapay_app_id') if context.user_data else None

            if not app_id:
                await update.message.reply_text(
                    "❌ Error: APP ID no encontrado. Comienza de nuevo con /qvapay",
                    parse_mode="HTML"
                )
                return ConversationHandler.END

            # Validar USER ID básico
            if not user_id_input or len(user_id_input) < 5:
                await update.message.reply_text(
                    "❌ USER ID inválido. Debe tener al menos 5 caracteres.\n\n"
                    "Ingresa tu USER ID nuevamente:",
                    parse_mode="HTML"
                )
                return WAITING_USER_ID

            # Validar credenciales consultando balance
            client = qvapay_user_client.QvaPayUserClient()
            try:
                balance_data = await client.async_get_user_balance(app_id, user_id_input)
            except QvaPayUserAuthError:
                await update.message.reply_text(
                    "❌ Credenciales inválidas. Verifica tu APP ID y USER ID.\n\n"
                    "Intenta nuevamente con /qvapay",
                    parse_mode="HTML"
                )
                return ConversationHandler.END
            except QvaPayUserError as e:
                await update.message.reply_text(
                    f"❌ Error validando credenciales: {str(e)}\n\n"
                    "Intenta nuevamente con /qvapay",
                    parse_mode="HTML"
                )
                return ConversationHandler.END

            # Credenciales válidas - guardar en DB
            db_user.qvapay_app_id = app_id
            db_user.qvapay_user_id = user_id_input
            db_user.qvapay_linked_at = datetime.now(timezone.utc)
            db_user.qvapay_last_balance_check = datetime.now(timezone.utc)
            await session.commit()

            # Limpiar datos temporales
            if context.user_data:
                context.user_data.clear()

            # Formatear balance para mostrar
            balances = balance_data.get("balances", {})
            balance_text = "\n".join([
                f"• <b>{currency}:</b> {amount}"
                for currency, amount in balances.items()
            ])

            msg = (
                "✅ <b>Cuenta QvaPay vinculada correctamente</b>\n\n"
                f"• APP ID: <code>{app_id}</code>\n"
                f"• USER ID: <code>{user_id_input}</code>\n\n"
                f"💰 <b>Balance actual:</b>\n{balance_text}\n\n"
                "Ya puedes usar QvaPay en el bot."
            )

            keyboard = [
                [InlineKeyboardButton("💰 Ver Balance", callback_data="qvapay_balance")],
                [InlineKeyboardButton("✅ Listo", callback_data="qvapay_cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                msg,
                parse_mode="HTML",
                reply_markup=reply_markup
            )

            await log_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=user_id,
                action="qvapay_link_success",
                details=f"Vinculó cuenta QvaPay - APP: {app_id[:8]}..., USER: {user_id_input[:8]}...",
                message=msg,
            )

        except Exception as e:
            logger.exception("Error recibiendo USER ID: %s", type(e).__name__)
            await log_error_and_notify(
                session=session,
                bot=bot,
                chat_id=chat_id,
                user_id=None,
                action="qvapay_user_id_error",
                error=e,
                public_message="Error procesando USER ID.",
            )

        return ConversationHandler.END


async def cancel_qvapay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela la conversación."""
    if update.message:
        await update.message.reply_text(
            "❌ Operación cancelada.",
            parse_mode="HTML"
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            "❌ Operación cancelada.",
            parse_mode="HTML"
        )

    # Limpiar datos temporales
    if context.user_data:
        context.user_data.clear()

    return ConversationHandler.END


# ConversationHandler para el flujo de vinculación
qvapay_conversation = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(qvapay_callback, pattern=r"^qvapay_"),
        CommandHandler("qvapay", qvapay_command)
    ],
    states={
        WAITING_APP_ID: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_app_id),
            CallbackQueryHandler(qvapay_callback, pattern=r"^qvapay_cancel$")
        ],
        WAITING_USER_ID: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_user_id),
            CallbackQueryHandler(qvapay_callback, pattern=r"^qvapay_cancel$")
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_qvapay),
        CallbackQueryHandler(cancel_qvapay, pattern=r"^qvapay_cancel$")
    ],
    per_message=False,
    per_chat=True,
    per_user=True,
)