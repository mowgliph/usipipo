from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.messages import Messages
from telegram_bot.keyboard import InlineKeyboards
from config import settings
from utils.logger import logger
from application.services.vpn_service import VpnService
from application.services.common.container import get_container


async def info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja el comando /info y muestra el menú principal profesional.
    """
    logger.info(f"📋 info_handler iniciado para usuario {update.effective_user.id}")
    
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    try:
        # Obtener el servicio VPN del contenedor
        container = get_container()
        vpn_service = container.resolve(VpnService)
        
        # Obtener datos reales del usuario
        user_status = await vpn_service.get_user_status(user.id)
        user_data = user_status["user"]
        
        # Obtener estadísticas de llaves
        active_keys = await vpn_service.get_user_keys(user.id)
        key_count = len(active_keys)
        
        # Mensaje profesional del menú principal
        professional_menu_message = (
            "🌐 **uSipipo VPN - Menú Principal Profesional**\n"
            "━━━━━━━━━━━━\n\n"
            
            "👋 ¡Bienvenido a tu **Panel de Control VPN**!\n\n"
            
            "📊 **Servicios Disponibles:**\n"
            "━━━━━━━━━━━━\n\n"
            
            "🔐 **Seguridad y Privacidad:**\n"
            "• 🛡️ **Mis Llaves** - Gestiona tus conexiones VPN activas\n"
            "• ➕ **Crear Nueva** - Genera nuevas llaves de acceso\n"
            "• 📊 **Estado** - Monitorea tu consumo de datos\n\n"
            
            "💰 **Operaciones y Beneficios:**\n"
            "• 👑 **Plan VIP** - Accede a beneficios premium\n"
            "• 🎮 **Juega y Gana** - Obtén estrellas jugando\n"
            "• 👥 **Referidos** - Gana por invitar amigos\n"
            "• ✅ **Centro de Tareas** - Completa misiones\n\n"
            
            "🏆 **Logros y Soporte:**\n"
            "• 🏆 **Logros** - Desbloquea recompensas\n"
            "• ⚙️ **Ayuda** - Guías y soporte técnico\n"
            "• 🎫 **Soporte** - Contacta a nuestro equipo\n\n"
            
            "📈 **Tus Estadísticas Rápidas:**\n"
            "━━━━━━━━━━━━\n\n"
            
            "👤 **Perfil:** {name}\n"
            "🆔 **ID de Usuario:** `{user_id}`\n"
            "🔑 **Llaves Activas:** {key_count}\n"
            "⭐ **Estrellas Disponibles:** {stars}\n"
            "📊 **Consumo Total:** {usage}\n\n"
            
            "💡 **Consejo Profesional:**\n"
            "Usa WireGuard para máxima velocidad en PC/gaming,\n"
            "y Outline para dispositivos móviles.\n\n"
            
            "🔗 **Recursos Adicionales:**\n"
            "• /help - Guía completa de uso\n"
            "• /start - Reiniciar sesión\n"
            "• /cancel - Cancelar operaciones\n\n"
            
            "👇 **Selecciona una opción del menú:**"
        )
        
        # Determinar si es admin para mostrar el menú correspondiente
        is_admin = user.id == int(settings.ADMIN_ID)
        
        # Enviar mensaje profesional con el menú inline
        await update.message.reply_text(
            text=professional_menu_message.format(
                name=user.first_name or user.username or f"Usuario {user.id}",
                user_id=user.id,
                key_count=key_count,
                stars=user_data.balance_stars,
                usage=f"{user_status['total_used_gb']:.1f} GB"
            ),
            reply_markup=InlineKeyboards.main_menu(is_admin=is_admin),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error en info_handler: {e}")
        await update.message.reply_text(
            text=Messages.Errors.GENERIC.format(error="No se pudo mostrar la información del menú.")
        )