"""
Handler de Operaciones del Usuario.

Maneja el menú de operaciones: balance, VIP, juegos, referidos, etc.
Los teclados se gestionan en telegram_bot/keyboard/inline_keyboards.py

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from telegram_bot.keyboard import OperationKeyboards, UserKeyboards
from telegram_bot.messages import OperationMessages, UserMessages, CommonMessages
from utils.logger import logger


async def mi_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, vpn_service):
    """Handler para el botón 'Mi Balance'."""
    user_id = update.effective_user.id
    try:
        user_status = await vpn_service.get_user_status(user_id)
        user = user_status["user"]
        
        text = OperationMessages.Balance.DISPLAY.format(
            name=user.full_name or user.username or f"Usuario {user.telegram_id}",
            balance=user.balance_stars,
            total_deposited=user.total_deposited,
            referral_earnings=user.total_referral_earnings
        )
        
        await update.message.reply_text(
            text=text,
            reply_markup=OperationKeyboards.operations_menu(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.log_error(e, context='mi_balance_handler', user_id=user_id)
        await update.message.reply_text(
            text=CommonMessages.Errors.GENERIC.format(error=str(e)),
            reply_markup=OperationKeyboards.operations_menu()
        )


async def referidos_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, referral_service):
    """Handler para el botón 'Referidos'."""
    user_id = update.effective_user.id
    try:
        referral_data = await referral_service.get_user_referral_data(user_id)
        
        text = OperationMessages.Referral.MENU.format(
            bot_username="usipipo_vpn_bot",
            referral_code=referral_data.get("code", "N/A"),
            direct_referrals=referral_data.get("direct_referrals", 0),
            total_earnings=referral_data.get("total_earnings", 0),
            commission=10
        )
        
        await update.message.reply_text(
            text=text,
            reply_markup=OperationKeyboards.referral_actions(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.log_error(e, context='referidos_handler', user_id=user_id)
        await update.message.reply_text(
            text=CommonMessages.Errors.GENERIC.format(error=str(e)),
            reply_markup=OperationKeyboards.operations_menu()
        )


async def atras_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para el botón 'Atrás' en el menú de operaciones."""
    user = update.effective_user
    is_admin = user.id == int(settings.ADMIN_ID)
    
    await update.message.reply_text(
        text="👇 Menú Principal",
        reply_markup=UserKeyboards.main_menu(is_admin=is_admin),
        parse_mode="Markdown"
    )


async def operations_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para el callback 'operations_menu'."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        text=OperationMessages.Menu.MAIN,
        reply_markup=OperationKeyboards.operations_menu(),
        parse_mode="Markdown"
    )


async def operations_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para el botón '💰 Operaciones'."""
    await update.message.reply_text(
        text=OperationMessages.Menu.MAIN,
        reply_markup=OperationKeyboards.operations_menu(),
        parse_mode="Markdown"
    )
