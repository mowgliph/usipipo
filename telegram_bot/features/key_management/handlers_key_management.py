"""
Handlers para gestión avanzada de llaves VPN de uSipipo.

Author: uSipipo Team
Version: 2.0.0 - Feature-based architecture
"""

from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters, CommandHandler
from application.services.vpn_service import VpnService
from .messages_key_management import KeyManagementMessages
from .keyboards_key_management import KeyManagementKeyboards
from config import settings
from utils.logger import logger
from telegram_bot.common.base_handler import BaseHandler


class KeyManagementHandler(BaseHandler):
    """Handler para gestión avanzada de llaves VPN."""
    
    def __init__(self, vpn_service: VpnService):
        """
        Inicializa el handler de gestión de llaves.
        
        Args:
            vpn_service: Servicio de VPN
        """
        super().__init__(vpn_service, "VpnService")
        logger.info("🔑 KeyManagementHandler inicializado")

    async def show_key_submenu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el menú principal de gestión de llaves.
        """
        query = update.callback_query
        
        # Handle both command and callback scenarios
        if query is None:
            # This is a direct command, send a new message
            user_id = update.effective_user.id
            try:
                user_status = await self.vpn_service.get_user_status(user_id)
                keys = user_status.get("keys", [])
                
                # Contar llaves por servidor dinámicamente
                keys_summary = {'total_count': len(keys)}
                message = KeyManagementMessages.MAIN_MENU
                
                for protocol in settings.get_vpn_protocols():
                    count = len([k for k in keys if k.key_type.lower() == protocol.lower()])
                    keys_summary[f'{protocol}_count'] = count
                    
                # Formatear mensaje con conteo
                message = KeyManagementMessages.MAIN_MENU.format(
                    total_keys=keys_summary['total_count'],
                    outline_count=keys_summary.get('outline_count', 0),
                    wireguard_count=keys_summary.get('wireguard_count', 0)
                )
                
                await update.message.reply_text(
                    text=message,
                    reply_markup=KeyManagementKeyboards.main_menu(keys_summary),
                    parse_mode="Markdown"
                )
                
            except Exception as e:
                logger.error(f"Error mostrando submenú de llaves: {e}")
                await update.message.reply_text(
                    text=KeyManagementMessages.Error.SYSTEM_ERROR,
                    parse_mode="Markdown"
                )
        else:
            # This is a callback, edit the existing message
            await self._safe_answer_query(query)
            user_id = update.effective_user.id
             
            try:
                user_status = await self.vpn_service.get_user_status(user_id)
                keys = user_status.get("keys", [])
                 
                # Contar llaves por servidor dinámicamente
                keys_summary = {'total_count': len(keys)}
                 
                for protocol in settings.get_vpn_protocols():
                    count = len([k for k in keys if k.key_type.lower() == protocol.lower()])
                    keys_summary[f'{protocol}_count'] = count
                     
                # Formatear mensaje con conteo
                message = KeyManagementMessages.MAIN_MENU.format(
                    total_keys=keys_summary['total_count'],
                    outline_count=keys_summary.get('outline_count', 0),
                    wireguard_count=keys_summary.get('wireguard_count', 0)
                )
                 
                await self._safe_edit_message(
                    query, context,
                    text=message,
                    reply_markup=KeyManagementKeyboards.main_menu(keys_summary),
                    parse_mode="Markdown"
                )
                 
            except Exception as e:
                logger.error(f"Error mostrando submenú de llaves: {e}")
                await self._safe_edit_message(
                    query, context,
                    text=KeyManagementMessages.Error.SYSTEM_ERROR,
                    reply_markup=KeyManagementKeyboards.back_to_main(),
                    parse_mode="Markdown"
                )

    async def show_keys_by_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra llaves filtradas por tipo.
        """
        query = update.callback_query
        await self._safe_answer_query(query)
         
        # Extraer tipo del callback_data
        key_type = query.data.replace("keys_", "")
        user_id = update.effective_user.id
         
        try:
            user_status = await self.vpn_service.get_user_status(user_id)
            all_keys = user_status.get("keys", [])
             
            # Filtrar llaves por tipo
            filtered_keys = [k for k in all_keys if k.key_type.lower() == key_type.lower()]
             
            if not filtered_keys:
                message = KeyManagementMessages.NO_KEYS_TYPE.format(type=key_type.upper())
                keyboard = KeyManagementKeyboards.back_to_submenu()
            else:
                message = KeyManagementMessages.KEYS_LIST_HEADER.format(type=key_type.upper())
                keyboard = KeyManagementKeyboards.keys_list(filtered_keys)
                 
                # Agregar información de cada llave
                for key in filtered_keys:
                    status = "🟢 Activa" if key.is_active else "🔴 Inactiva"
                    message += f"\n🔑 {key.name}\n   📊 {key.usage_gb}/{key.limit_gb} GB\n   {status}\n"
             
            await self._safe_edit_message(
                query, context,
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
             
        except Exception as e:
            logger.error(f"Error mostrando llaves por tipo: {e}")
            await self._safe_edit_message(
                query, context,
                text=KeyManagementMessages.Error.SYSTEM_ERROR,
                reply_markup=KeyManagementKeyboards.back_to_submenu(),
                parse_mode="Markdown"
            )

    async def show_key_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra detalles de una llave específica.
        """
        query = update.callback_query
        await self._safe_answer_query(query)
         
        # Extraer key_id del callback_data
        key_id = int(query.data.split("_")[-1])
        user_id = update.effective_user.id
         
        try:
            key = await self.vpn_service.get_key_by_id(key_id)
             
            if not key or key.user_id != user_id:
                message = KeyManagementMessages.KEY_NOT_FOUND
            else:
                status = "🟢 Activa" if key.is_active else "🔴 Inactiva"
                usage_percentage = (key.usage_gb / key.limit_gb) * 100 if key.limit_gb > 0 else 0
                 
                message = KeyManagementMessages.KEY_DETAILS.format(
                    name=key.name,
                    type=key.key_type.upper(),
                    server=key.server or "N/A",
                    usage=key.usage_gb,
                    limit=key.limit_gb,
                    percentage=usage_percentage,
                    status=status,
                    created=key.created_at.strftime("%d/%m/%Y") if key.created_at else "N/A",
                    expires=key.expires_at.strftime("%d/%m/%Y") if key.expires_at else "N/A"
                )
                 
                keyboard = KeyManagementKeyboards.key_actions(key_id, key.is_active)
             
            await self._safe_edit_message(
                query, context,
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
             
        except Exception as e:
            logger.error(f"Error mostrando detalles de llave: {e}")
            await self._safe_edit_message(
                query, context,
                text=KeyManagementMessages.Error.SYSTEM_ERROR,
                reply_markup=KeyManagementKeyboards.back_to_submenu(),
                parse_mode="Markdown"
            )

    async def show_key_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra estadísticas detalladas de las llaves.
        """
        query = update.callback_query
        await self._safe_answer_query(query)
         
        user_id = update.effective_user.id
         
        try:
            user_status = await self.vpn_service.get_user_status(user_id)
            keys = user_status.get("keys", [])
             
            if not keys:
                message = KeyManagementMessages.NO_KEYS_STATS
            else:
                # Calcular estadísticas
                total_keys = len(keys)
                active_keys = len([k for k in keys if k.is_active])
                total_usage = sum(k.usage_gb for k in keys)
                total_limit = sum(k.limit_gb for k in keys)
                overall_percentage = (total_usage / total_limit * 100) if total_limit > 0 else 0
                 
                # Estadísticas por tipo
                outline_keys = [k for k in keys if k.key_type.lower() == "outline"]
                wireguard_keys = [k for k in keys if k.key_type.lower() == "wireguard"]
                 
                message = KeyManagementMessages.STATISTICS.format(
                    total_keys=total_keys,
                    active_keys=active_keys,
                    total_usage=total_usage,
                    total_limit=total_limit,
                    percentage=overall_percentage,
                    outline_count=len(outline_keys),
                    wireguard_count=len(wireguard_keys),
                    outline_usage=sum(k.usage_gb for k in outline_keys),
                    wireguard_usage=sum(k.usage_gb for k in wireguard_keys)
                )
             
            keyboard = KeyManagementKeyboards.back_to_submenu()
             
            await self._safe_edit_message(
                query, context,
                text=message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
             
        except Exception as e:
            logger.error(f"Error mostrando estadísticas: {e}")
            await self._safe_edit_message(
                query, context,
                text=KeyManagementMessages.Error.SYSTEM_ERROR,
                reply_markup=KeyManagementKeyboards.back_to_submenu(),
                parse_mode="Markdown"
            )

    async def back_to_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Vuelve al menú principal.
        """
        query = update.callback_query
        await self._safe_answer_query(query)
         
        await self._safe_edit_message(
            query, context,
            text=KeyManagementMessages.BACK_TO_MAIN,
            reply_markup=KeyManagementKeyboards.back_to_main_menu(),
            parse_mode="Markdown"
        )


def get_key_management_handlers(vpn_service: VpnService):
    """
    Retorna los handlers de gestión de llaves.
    
    Args:
        vpn_service: Servicio de VPN
        
    Returns:
        list: Lista de handlers
    """
    handler = KeyManagementHandler(vpn_service)
    
    return [
        MessageHandler(filters.Regex("^🛡️ Mis Llaves$"), handler.show_key_submenu),
        CommandHandler("mykeys", handler.show_key_submenu),
    ]


def get_key_management_callback_handlers(vpn_service: VpnService):
    """
    Retorna los handlers de callbacks para gestión de llaves.
    
    Args:
        vpn_service: Servicio de VPN
        
    Returns:
        list: Lista de CallbackQueryHandler
    """
    handler = KeyManagementHandler(vpn_service)
    
    return [
        CallbackQueryHandler(handler.show_keys_by_type, pattern="^keys_"),
        CallbackQueryHandler(handler.show_key_details, pattern="^key_details_"),
        CallbackQueryHandler(handler.show_key_statistics, pattern="^key_stats$"),
        CallbackQueryHandler(handler.back_to_main_menu, pattern="^back_to_main$"),
    ]
