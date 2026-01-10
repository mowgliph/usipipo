"""
Handlers para gestión de usuarios de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from typing import Optional
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from application.services.vpn_service import VpnService
from application.services.achievement_service import AchievementService
from application.services.admin_service import AdminService
from .messages import UserManagementMessages
from .keyboards import UserManagementKeyboards
from config import settings
from utils.logger import logger
from utils.spinner import registration_spinner


class UserManagementHandler:
    """Handler para gestión de usuarios."""
    
    def __init__(self, vpn_service: VpnService, achievement_service: AchievementService = None):
        """
        Inicializa el handler de gestión de usuarios.
        
        Args:
            vpn_service: Servicio de VPN
            achievement_service: Servicio de logros (opcional)
        """
        self.vpn_service = vpn_service
        self.achievement_service = achievement_service
        logger.info("👤 UserManagementHandler inicializado")

    @registration_spinner
    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Maneja el comando /start y el registro de usuarios.
        """
        logger.info(f"🔄 start_handler iniciado para usuario {update.effective_user.id}")
        
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        try:
            # Verificar si el usuario ya existe
            existing_user = await self.vpn_service.user_repo.get_by_id(user.id)
            
            if not existing_user:
                # Construir full_name
                full_name = user.first_name or ""
                if user.last_name:
                    full_name = f"{full_name} {user.last_name}".strip()
                
                # Crear nuevo usuario
                await self.vpn_service.user_repo.create_user(
                    user_id=user.id,
                    username=user.username,
                    full_name=full_name
                )
                welcome_message = UserManagementMessages.Welcome.NEW_USER.format(name=user.first_name)
                
                # Inicializar logros para nuevo usuario
                if self.achievement_service:
                    try:
                        await self.achievement_service.initialize_user_achievements(user.id)
                    except Exception as e:
                        logger.warning(f"⚠️ Error inicializando logros para usuario {user.id}: {e}")
                
                logger.info(f"✅ Nuevo usuario registrado: {user.id} - {user.first_name}")
            else:
                welcome_message = UserManagementMessages.Welcome.RETURNING_USER.format(name=user.first_name)
                logger.info(f"👋 Usuario existente: {user.id} - {user.first_name}")
            
            # Determinar si es admin
            is_admin = user.id == int(settings.ADMIN_ID)
            
            await update.message.reply_text(
                text=welcome_message,
                reply_markup=UserManagementKeyboards.main_menu(is_admin=is_admin),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"❌ Error en start_handler para usuario {user.id}: {e}")
            await update.message.reply_text(
                text=UserManagementMessages.Error.REGISTRATION_FAILED,
                reply_markup=UserManagementKeyboards.main_menu()
            )

    async def status_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE, admin_service: Optional[AdminService] = None):
        """
        Muestra el estado del usuario o panel administrativo.
        """
        telegram_id = update.effective_user.id
        user_name = update.effective_user.username or update.effective_user.first_name
        
        try:
            # Validar si es admin
            is_admin = str(telegram_id) == str(settings.ADMIN_ID)
            
            if is_admin and admin_service:
                # Mostrar panel de control administrativo
                stats = await admin_service.get_dashboard_stats()
                text = self._format_admin_dashboard(user_name, stats)
            else:
                # Mostrar estado de usuario regular
                status_data = await self.vpn_service.get_user_status(telegram_id)
                user_entity = status_data.get("user")
                
                # Formatear fecha de unión
                join_date = "N/A"
                if user_entity and hasattr(user_entity, 'created_at') and user_entity.created_at:
                    join_date = user_entity.created_at.strftime("%Y-%m-%d")
                    
                # Determinar estado
                status_text = "Inactivo ⚠️"
                if user_entity and (getattr(user_entity, 'is_active', False) or getattr(user_entity, 'status', None) == 'active'):
                    status_text = "Activo ✅"
                
                text = UserManagementMessages.Status.HEADER + "\n\n" + UserManagementMessages.Status.USER_INFO.format(
                    name=user_name,
                    user_id=telegram_id,
                    join_date=join_date,
                    status=status_text
                )
            
            # Determinar si es admin para el menú
            is_admin_menu = telegram_id == int(settings.ADMIN_ID)
            
            await update.message.reply_text(
                text=text,
                reply_markup=UserManagementKeyboards.main_menu(is_admin=is_admin_menu),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"❌ Error en status_handler para usuario {telegram_id}: {e}")
            await update.message.reply_text(
                text=UserManagementMessages.Error.STATUS_FAILED,
                reply_markup=UserManagementKeyboards.main_menu()
            )

    def _format_admin_dashboard(self, user_name: str, stats: dict) -> str:
        """
        Formatea el panel de control administrativo.
        """
        return UserManagementMessages.Status.ADMIN_DASHBOARD.format(
            name=user_name,
            total_users=stats.get('total_users', 0),
            active_users=stats.get('active_users', 0),
            total_keys=stats.get('total_keys', 0),
            active_keys=stats.get('active_keys', 0),
            server_load=stats.get('server_load', 'N/A')
        )


def get_user_management_handlers(vpn_service: VpnService, achievement_service: AchievementService = None):
    """
    Retorna los handlers de gestión de usuarios.
    
    Args:
        vpn_service: Servicio de VPN
        achievement_service: Servicio de logros (opcional)
        
    Returns:
        list: Lista de handlers
    """
    handler = UserManagementHandler(vpn_service, achievement_service)
    
    return [
        # Comando /start
        CommandHandler("start", handler.start_handler),
        # Botón de estado
        MessageHandler(filters.Regex("^📊 Estado$"), handler.status_handler),
        # Comando /status
        CommandHandler("status", handler.status_handler),
    ]


def get_user_callback_handlers(vpn_service: VpnService, achievement_service: AchievementService = None):
    """
    Retorna los handlers de callbacks para gestión de usuarios.
    
    Args:
        vpn_service: Servicio de VPN
        achievement_service: Servicio de logros (opcional)
        
    Returns:
        list: Lista de CallbackQueryHandler
    """
    handler = UserManagementHandler(vpn_service, achievement_service)
    
    return [
        # Callbacks de estado
        CallbackQueryHandler(
            lambda u, c: handler.status_handler(u, c, None), 
            pattern="^status$"
        ),
    ]
