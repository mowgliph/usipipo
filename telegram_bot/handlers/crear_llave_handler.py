import os
from telegram import Update
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    CallbackQueryHandler
)
from loguru import logger

from application.services.vpn_service import VpnService
from telegram_bot.messages.messages import Messages
from telegram_bot.keyboard.keyboard import Keyboards
from utils.qr_generator import QrGenerator

# Estados de la conversación
SELECT_TYPE, INPUT_NAME = range(2)

async def start_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el flujo de creación preguntando el tipo de VPN."""
    await update.message.reply_text(
        text=Messages.Keys.SELECT_TYPE,
        reply_markup=Keyboards.vpn_types(),
        parse_mode="Markdown"
    )
    return SELECT_TYPE

async def type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la selección del protocolo y pide el nombre de la llave."""
    query = update.callback_query
    await query.answer()
    
    # Extraer tipo de los callback_data (type_outline o type_wireguard)
    key_type = "outline" if "outline" in query.data else "wireguard"
    context.user_data["tmp_key_type"] = key_type
    
    await query.edit_message_text(
        text=f"🛡️ Has seleccionado **{key_type.upper()}**.\n\nEscribe un nombre para identificar tu nueva llave (ej: Mi Laptop):",
        parse_mode="Markdown"
    )
    return INPUT_NAME

async def name_received(update: Update, context: ContextTypes.DEFAULT_TYPE, vpn_service: VpnService):
    """Finaliza la creación, genera archivos/QR y entrega al usuario."""
    key_name = update.message.text
    key_type = context.user_data.get("tmp_key_type")
    telegram_id = update.effective_user.id

    loading_msg = await update.message.reply_text("⏳ Generando acceso seguro, por favor espera...")

    try:
        # 1. Crear llave mediante el Servicio de Aplicación
        new_key = await vpn_service.create_key(telegram_id, key_type, key_name)
        
        # 2. Preparar ID de archivo único
        safe_name = "".join(x for x in key_name if x.isalnum())
        file_id = f"{telegram_id}_{safe_name}"

        # 3. Generar Código QR
        qr_path = QrGenerator.generate_vpn_qr(new_key.key_data, file_id)

        # 4. Entrega diferenciada
        if key_type == "outline":
            # Escapar caracteres especiales para MarkdownV2
            escaped_data = new_key.key_data.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('`', '\\`').replace('>', '\\>').replace('#', '\\#').replace('+', '\\+').replace('-', '\\-').replace('=', '\\=').replace('|', '\\|').replace('{', '\\{').replace('}', '\\}').replace('.', '\\.').replace('!', '\\!')
            
            caption = (
                f"✅ ¡Llave *OUTLINE* generada con éxito\\!\n\n"
                f"Copia el siguiente código en tu aplicación Outline:\n"
                f"```\n{escaped_data}\n```"
            )
            
            with open(qr_path, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo, 
                    caption=caption, 
                    parse_mode="MarkdownV2",
                    reply_markup=Keyboards.main_menu()
                )

        elif key_type == "wireguard":
            conf_path = QrGenerator.save_conf_file(new_key.key_data, file_id)
            
            caption = (
                f"✅ ¡Llave **WIREGUARD** generada con éxito!\n\n"
                "Escanea el QR en tu móvil o usa el archivo adjunto en tu PC."
            )
            
            with open(qr_path, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo, 
                    caption=caption,
                    parse_mode="Markdown"
                )
            
            with open(conf_path, "rb") as document:
                await update.message.reply_document(
                    document=document, 
                    filename=f"{key_name}.conf",
                    caption="📄 Configuración de WireGuard",
                    reply_markup=Keyboards.main_menu()
                )

        await loading_msg.delete()
        logger.info(f"✅ Llave {key_type} creada para usuario {telegram_id}")

    except Exception as e:
        logger.error(f"❌ Error en creación de llave: {e}")
        if loading_msg:
            await loading_msg.delete()
        await update.message.reply_text(
            text=Messages.Errors.GENERIC.format(error=str(e)),
            reply_markup=Keyboards.main_menu()
        )
    
    return ConversationHandler.END

async def cancel_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela la conversación."""
    await update.message.reply_text(
        "❌ Operación cancelada.",
        reply_markup=Keyboards.main_menu()
    )
    return ConversationHandler.END

def get_creation_handler(vpn_service: VpnService) -> ConversationHandler:
    """Configuración del ConversationHandler para ser registrado en main.py."""
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^➕ Crear Nueva$"), start_creation)],
        states={
            SELECT_TYPE: [CallbackQueryHandler(type_selected, pattern="^type_")],
            INPUT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, 
                         lambda u, c: name_received(u, c, vpn_service))]
        },
        fallbacks=[CommandHandler("cancel", cancel_creation)],
        # CORRECCIÓN: Agregar configuración explícita
        per_message=True,
        per_chat=True,
        per_user=True,
        allow_reentry=True
    )
