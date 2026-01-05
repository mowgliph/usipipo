"""
Handler para el sistema de submenús de llaves VPN del bot uSipipo.
Proporciona gestión avanzada de llaves organizadas por servidor.

Author: uSipipo Team
Version: 2.0.0 - Sistema de submenús para llaves
"""

from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from loguru import logger
from typing import Dict, Any, List, Optional

from application.services.vpn_service import VpnService
from telegram_bot.messages.key_submenu_messages import KeySubmenuMessages
from telegram_bot.keyboard.key_submenu_keyboards import KeySubmenuKeyboards
from telegram_bot.messages.messages import Messages


class KeySubmenuHandler:
    """Handler para el sistema de submenús de llaves VPN."""
    
    def __init__(self, vpn_service: VpnService):
        self.vpn_service = vpn_service
    
    async def show_key_submenu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Muestra el menú principal del submenú de llaves.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = update.effective_user.id
            user_status = await self.vpn_service.get_user_status(user_id)
            keys = user_status.get("keys", [])
            
            # Contar llaves por servidor
            wireguard_keys = [k for k in keys if k.key_type.upper() == 'WIREGUARD']
            outline_keys = [k for k in keys if k.key_type.upper() == 'OUTLINE']
            
            keys_summary = {
                'wireguard_count': len(wireguard_keys),
                'outline_count': len(outline_keys),
                'total_count': len(keys)
            }
            
            # Construir mensaje
            message = KeySubmenuMessages.MAIN_MENU
            message += f"\n🟦 **WireGuard:** {len(wireguard_keys)} llaves"
            message += f"\n🟩 **Outline:** {len(outline_keys)} llaves"
            message += f"\n\n📊 **Total:** {len(keys)} llaves activas"
            
            await query.edit_message_text(
                text=message,
                reply_markup=KeySubmenuKeyboards.main_menu(keys_summary),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_key_submenu: {e}")
            await query.edit_message_text(
                text=Messages.Errors.GENERIC.format(error=str(e)),
                reply_markup=KeySubmenuKeyboards.quick_actions()
            )
    
    async def show_server_keys(self, update: Update, context: ContextTypes.DEFAULT_TYPE, server_type: str, page: int = 1):
        """
        Muestra las llaves de un servidor específico con paginación.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = update.effective_user.id
            user_status = await self.vpn_service.get_user_status(user_id)
            all_keys = user_status.get("keys", [])
            
            # Filtrar llaves por servidor
            if server_type.upper() == 'WIREGUARD':
                server_keys = [k for k in all_keys if k.key_type.upper() == 'WIREGUARD']
                header = KeySubmenuMessages.WIREGUARD_HEADER
                server_name = "WireGuard"
            elif server_type.upper() == 'OUTLINE':
                server_keys = [k for k in all_keys if k.key_type.upper() == 'OUTLINE']
                header = KeySubmenuMessages.OUTLINE_HEADER
                server_name = "Outline"
            else:
                raise ValueError(f"Tipo de servidor desconocido: {server_type}")
            
            # Convertir a diccionarios para compatibilidad
            keys_data = []
            for key in server_keys:
                keys_data.append({
                    'id': str(key.id),
                    'name': key.name,
                    'server_type': key.key_type,
                    'is_active': True,  # Asumir activo si existe
                    'used_gb': key.used_gb,
                    'limit_gb': key.data_limit_gb
                })
            
            # Calcular paginación
            total_pages = max(1, (len(keys_data) + KeySubmenuKeyboards.ITEMS_PER_PAGE - 1) // KeySubmenuKeyboards.ITEMS_PER_PAGE)
            page = max(1, min(page, total_pages))
            
            # Construir mensaje
            if not keys_data:
                message = KeySubmenuMessages.NO_KEYS_IN_SERVER.format(server_name=server_name)
            else:
                keys_list = KeySubmenuMessages.format_key_list(keys_data, server_name)
                message = KeySubmenuMessages.SERVER_KEYS_LIST.format(
                    server_name=server_name,
                    keys_list=keys_list
                )
                message += f"\n\n{KeySubmenuMessages.PAGINATION_INFO.format(current=page, total=total_pages)}"
            
            await query.edit_message_text(
                text=message,
                reply_markup=KeySubmenuKeyboards.server_keys_menu(server_type, keys_data, page, total_pages),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_server_keys: {e}")
            await query.edit_message_text(
                text=KeySubmenuMessages.SERVER_NOT_AVAILABLE.format(server_name=server_type),
                reply_markup=KeySubmenuKeyboards.back_to_server('main')
            )
    
    async def show_key_detail(self, update: Update, context: ContextTypes.DEFAULT_TYPE, key_id: str):
        """
        Muestra el detalle de una llave específica.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            # Obtener datos de la llave
            key_data = await self._get_key_data(key_id)
            if not key_data:
                raise ValueError("Llave no encontrada")
            
            # Construir mensaje detallado
            message = KeySubmenuMessages.KEY_DETAIL_ENHANCED.format(
                name=key_data['name'],
                protocol=key_data['protocol'],
                key_id=key_data['id'],
                created_date=key_data['created_date'],
                used_gb=key_data['used_gb'],
                limit_gb=key_data['limit_gb'],
                status=KeySubmenuMessages.get_status_badge(key_data),
                server_info=KeySubmenuMessages.format_server_info(key_data.get('server_info', {}))
            )
            
            await query.edit_message_text(
                text=message,
                reply_markup=KeySubmenuKeyboards.key_detail_menu(key_id, key_data['name'], key_data['server_type']),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_key_detail: {e}")
            await query.edit_message_text(
                text=f"Error al cargar detalles de la llave: {str(e)}",
                reply_markup=KeySubmenuKeyboards.back_to_server('main')
            )
    
    async def handle_server_migration(self, update: Update, context: ContextTypes.DEFAULT_TYPE, key_id: str, target_server: str):
        """
        Maneja la migración de una llave entre servidores.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            # Obtener datos actuales de la llave
            key_data = await self._get_key_data(key_id)
            if not key_data:
                raise ValueError("Llave no encontrada")
            
            current_server = key_data['server_type']
            
            # Mostrar confirmación de migración
            message = KeySubmenuMessages.CONFIRM_SERVER_SWITCH.format(
                from_server=current_server,
                to_server=target_server,
                key_name=key_data['name']
            )
            
            await query.edit_message_text(
                text=message,
                reply_markup=KeySubmenuKeyboards.migration_confirmation(key_id, current_server, target_server),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en handle_server_migration: {e}")
            await query.edit_message_text(
                text=KeySubmenuMessages.MIGRATION_FAILED,
                reply_markup=KeySubmenuKeyboards.key_detail_menu(key_id, "Llave", key_data.get('server_type', 'unknown'))
            )
    
    async def execute_migration(self, update: Update, context: ContextTypes.DEFAULT_TYPE, key_id: str, target_server: str):
        """
        Ejecuta la migración de la llave.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            # Ejecutar migración a través del servicio VPN
            success = await self.vpn_service.migrate_key(key_id, target_server)
            
            if success:
                await query.edit_message_text(
                    text=KeySubmenuMessages.MIGRATION_SUCCESS.format(
                        key_name="Llave migrada",
                        server_name=target_server
                    ),
                    reply_markup=KeySubmenuKeyboards.back_to_server(target_server.lower())
                )
            else:
                await query.edit_message_text(
                    text=KeySubmenuMessages.MIGRATION_FAILED,
                    reply_markup=KeySubmenuKeyboards.back_to_server('main')
                )
                
        except Exception as e:
            logger.error(f"Error en execute_migration: {e}")
            await query.edit_message_text(
                text=KeySubmenuMessages.MIGRATION_FAILED,
                reply_markup=KeySubmenuKeyboards.back_to_server('main')
            )
    
    async def handle_delete_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, key_id: str):
        """
        Maneja la confirmación de eliminación de llave.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            key_data = await self._get_key_data(key_id)
            if not key_data:
                raise ValueError("Llave no encontrada")
            
            message = f"⚠️ **Confirmar eliminación**\n\n¿Eliminar la llave **{key_data['name']}**?\n\nEsta acción es irreversible."
            
            await query.edit_message_text(
                text=message,
                reply_markup=KeySubmenuKeyboards.confirm_delete(key_id, key_data['name']),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en handle_delete_confirmation: {e}")
            await query.edit_message_text(
                text=f"Error: {str(e)}",
                reply_markup=KeySubmenuKeyboards.back_to_server('main')
            )
    
    async def execute_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE, key_id: str):
        """
        Ejecuta la eliminación de la llave.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            success = await self.vpn_service.revoke_key(key_id)
            
            if success:
                await query.edit_message_text(
                    text="🗑️ **Llave eliminada**\n\nEl acceso ha sido revocado correctamente.",
                    reply_markup=KeySubmenuKeyboards.quick_actions()
                )
            else:
                await query.edit_message_text(
                    text="❌ Error: La llave no pudo ser eliminada.",
                    reply_markup=KeySubmenuKeyboards.quick_actions()
                )
                
        except Exception as e:
            logger.error(f"Error en execute_delete: {e}")
            await query.edit_message_text(
                text=f"Error al eliminar la llave: {str(e)}",
                reply_markup=KeySubmenuKeyboards.quick_actions()
            )
    
    async def show_all_keys_overview(self, update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1):
        """
        Muestra vista general de todas las llaves con paginación.
        """
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = update.effective_user.id
            user_status = await self.vpn_service.get_user_status(user_id)
            all_keys = user_status.get("keys", [])
            
            # Convertir a diccionarios
            keys_data = []
            for key in all_keys:
                keys_data.append({
                    'id': str(key.id),
                    'name': key.name,
                    'server_type': key.key_type,
                    'is_active': True,
                    'used_gb': key.used_gb,
                    'limit_gb': key.data_limit_gb
                })
            
            # Calcular paginación
            total_pages = max(1, (len(keys_data) + KeySubmenuKeyboards.ITEMS_PER_PAGE - 1) // KeySubmenuKeyboards.ITEMS_PER_PAGE)
            page = max(1, min(page, total_pages))
            
            # Construir mensaje
            message = f"🔑 **Todas las Llaves VPN**\n━━━━━━━━━━━━\n\n"
            
            if not keys_data:
                message += "No tienes llaves VPN activas."
            else:
                keys_list = KeySubmenuMessages.format_key_list(keys_data, "Todos los servidores")
                message += keys_list
                message += f"\n\n{KeySubmenuMessages.PAGINATION_INFO.format(current=page, total=total_pages)}"
            
            await query.edit_message_text(
                text=message,
                reply_markup=KeySubmenuKeyboards.all_keys_overview(keys_data, page, total_pages),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en show_all_keys_overview: {e}")
            await query.edit_message_text(
                text=f"Error al cargar llaves: {str(e)}",
                reply_markup=KeySubmenuKeyboards.quick_actions()
            )
    
    async def handle_back_to_servers(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Maneja la navegación de vuelta al menú principal de servidores.
        """
        query = update.callback_query
        await query.answer()
        
        await self.show_key_submenu(update, context)
    
    async def _get_key_data(self, key_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos de una llave específica.
        """
        try:
            # Convertir key_id a UUID para buscar en la base de datos
            from uuid import UUID
            key_uuid = UUID(key_id)
            
            # Obtener la llave real de la base de datos
            key = await self.vpn_service.key_repo.get_by_id(key_uuid)
            if not key:
                return None
            
            # Obtener información del usuario
            user = await self.vpn_service.user_repo.get_by_id(key.user_id)
            
            # Formatear los datos para el mensaje
            return {
                'id': str(key.id),
                'name': key.name,
                'protocol': key.key_type.capitalize(),
                'server_type': key.key_type.lower(),
                'created_date': key.created_at.strftime('%d/%m/%Y'),
                'used_gb': round(key.used_bytes / (1024**3), 1),
                'limit_gb': round(key.data_limit_bytes / (1024**3), 1),
                'is_active': key.is_active,
                'server_info': {
                    'location': 'Miami, USA',  # Esto podría obtenerse de configuración
                    'ping': 45,  # Esto podría obtenerse de monitoreo real
                    'load': 65   # Esto podría obtenerse de monitoreo real
                }
            }
        except Exception as e:
            logger.error(f"Error obteniendo datos de llave {key_id}: {e}")
            return None
    
    def get_handlers(self) -> List[CallbackQueryHandler]:
        """
        Retorna todos los handlers de callbacks para el submenu de llaves.
        """
        handlers = []
        
        # Menú principal
        handlers.append(CallbackQueryHandler(
            self.show_key_submenu, 
            pattern="^key_submenu_main$"
        ))
        
        # Servidores específicos
        handlers.append(CallbackQueryHandler(
            lambda u, c: self.show_server_keys(u, c, "wireguard"), 
            pattern="^key_submenu_server_wireguard$"
        ))
        
        handlers.append(CallbackQueryHandler(
            lambda u, c: self.show_server_keys(u, c, "outline"), 
            pattern="^key_submenu_server_outline$"
        ))
        
        # Paginación por servidor
        handlers.append(CallbackQueryHandler(
            lambda u, c: self._handle_server_pagination(u, c, "wireguard"), 
            pattern="^key_submenu_page_wireguard_"
        ))
        
        handlers.append(CallbackQueryHandler(
            lambda u, c: self._handle_server_pagination(u, c, "outline"), 
            pattern="^key_submenu_page_outline_"
        ))
        
        # Vista general de todas las llaves
        handlers.append(CallbackQueryHandler(
            self.show_all_keys_overview, 
            pattern="^key_submenu_all_keys$"
        ))
        
        # Paginación vista general
        handlers.append(CallbackQueryHandler(
            self._handle_all_keys_pagination, 
            pattern="^key_submenu_all_page_"
        ))
        
        # Detalle de llave específica
        handlers.append(CallbackQueryHandler(
            lambda u, c: self._handle_key_detail(u, c), 
            pattern="^key_detail_"
        ))
        
        # Migración de llaves
        handlers.append(CallbackQueryHandler(
            lambda u, c: self._handle_migration_menu(u, c), 
            pattern="^key_migrate_"
        ))
        
        # Eliminación de llaves
        handlers.append(CallbackQueryHandler(
            lambda u, c: self._handle_delete_flow(u, c), 
            pattern="^key_delete_"
        ))
        
        return handlers
    
    async def _handle_server_pagination(self, update: Update, context: ContextTypes.DEFAULT_TYPE, server_type: str):
        """Maneja la paginación de llaves por servidor."""
        query = update.callback_query
        await query.answer()
        
        # Extraer número de página del callback_data
        page = int(query.data.split('_')[-1])
        await self.show_server_keys(update, context, server_type, page)
    
    async def _handle_all_keys_pagination(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja la paginación de la vista general."""
        query = update.callback_query
        await query.answer()
        
        # Extraer número de página del callback_data
        page = int(query.data.split('_')[-1])
        await self.show_all_keys_overview(update, context, page)
    
    async def _handle_key_detail(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja la visualización de detalle de llave."""
        query = update.callback_query
        await query.answer()
        
        # Extraer ID de llave del callback_data
        key_id = query.data.replace('key_detail_', '')
        await self.show_key_detail(update, context, key_id)
    
    async def _handle_migration_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el menú de migración."""
        query = update.callback_query
        await query.answer()
        
        parts = query.data.split('_')
        
        if len(parts) >= 4:
            action = parts[2]
            key_id = parts[3]
            
            if action == 'menu':
                # Mostrar menú de migración
                await self.show_key_detail(update, context, key_id)
            elif action == 'execute' and len(parts) == 5:
                # Ejecutar migración directa
                target_server = parts[4]
                await self.execute_migration(update, context, key_id, target_server)
    
    async def _handle_delete_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el flujo de eliminación."""
        query = update.callback_query
        await query.answer()
        
        parts = query.data.split('_')
        
        if len(parts) >= 3:
            action = parts[2]
            key_id = parts[3]
            
            if action == 'confirm':
                await self.handle_delete_confirmation(update, context, key_id)
            elif action == 'execute':
                await self.execute_delete(update, context, key_id)


def get_key_submenu_handler(vpn_service: VpnService) -> KeySubmenuHandler:
    """
    Factory function para crear el handler del submenú de llaves.
    """
    return KeySubmenuHandler(vpn_service)