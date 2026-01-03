"""
Servicio de administración para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from loguru import logger

from domain.interfaces.iadmin_service import IAdminService
from domain.entities.admin import AdminUserInfo, AdminKeyInfo, ServerStatus, AdminOperationResult
from domain.entities.vpn_key import VpnKey as Key
from infrastructure.api_clients.client_wireguard import WireGuardClient
from infrastructure.api_clients.client_outline import OutlineClient

class AdminService(IAdminService):
    """Implementación del servicio de administración."""
    
    def __init__(self, key_repository, user_repository, payment_repository):
        self.key_repository = key_repository
        self.user_repository = user_repository
        self.payment_repository = payment_repository
        self.wireguard_client = WireGuardClient()
        self.outline_client = OutlineClient()
    
    async def get_all_users(self) -> List[Dict]:
        """Obtener lista de todos los usuarios registrados."""
        try:
            users = await self.user_repository.get_all_users()
            
            user_list = []
            for user in users:
                # Obtener claves del usuario
                user_keys = await self.key_repository.get_user_keys(user.user_id)
                active_keys = [k for k in user_keys if k.is_active]
                
                # Obtener balance de estrellas
                balance = await self.payment_repository.get_balance(user.user_id)
                
                user_info = AdminUserInfo(
                    user_id=user.user_id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    is_vip=user.is_vip,
                    vip_expiry=user.vip_expiry,
                    total_keys=len(user_keys),
                    active_keys=len(active_keys),
                    stars_balance=balance.stars if balance else 0,
                    registration_date=user.created_at,
                    last_activity=user.last_activity
                )
                user_list.append(user_info.__dict__)
            
            return user_list
            
        except Exception as e:
            logger.error(f"Error obteniendo todos los usuarios: {e}")
            return []
    
    async def get_user_keys(self, user_id: int) -> List[Key]:
        """Obtener todas las claves de un usuario específico."""
        try:
            return await self.key_repository.get_user_keys(user_id)
        except Exception as e:
            logger.error(f"Error obteniendo claves del usuario {user_id}: {e}")
            return []
    
    async def get_all_keys(self) -> List[Dict]:
        """Obtener todas las claves de todos los usuarios."""
        try:
            all_keys = await self.key_repository.get_all_keys()
            
            key_list = []
            for key in all_keys:
                # Obtener información del usuario
                user = await self.user_repository.get_user(key.user_id)
                user_name = f"{user.first_name} {user.last_name or ''}" if user else "Unknown"
                
                # Obtener estadísticas de uso según el tipo
                usage_stats = await self.get_key_usage_stats(key.key_id)
                
                key_info = AdminKeyInfo(
                    key_id=key.key_id,
                    user_id=key.user_id,
                    user_name=user_name,
                    key_type=key.key_type,
                    key_name=key.key_name,
                    access_url=key.access_url,
                    created_at=key.created_at,
                    last_used=key.last_used,
                    data_limit=key.data_limit,
                    data_used=usage_stats.get('data_used', 0),
                    is_active=key.is_active,
                    server_status=usage_stats.get('server_status', 'unknown')
                )
                key_list.append(key_info.__dict__)
            
            return key_list
            
        except Exception as e:
            logger.error(f"Error obteniendo todas las claves: {e}")
            return []
    
    async def delete_key_from_servers(self, key_id: str, key_type: str) -> bool:
        """Eliminar una clave de los servidores VPN (WireGuard y Outline)."""
        try:
            key = await self.key_repository.get_key(key_id)
            if not key:
                logger.error(f"Clave {key_id} no encontrada en BD")
                return False
            
            success = True
            
            if key_type.lower() == 'wireguard':
                # Eliminar de WireGuard
                wg_result = await self.wireguard_client.delete_client(key.key_name)
                if not wg_result:
                    logger.error(f"Error eliminando clave {key_id} de WireGuard")
                    success = False
                else:
                    logger.info(f"Clave {key_id} eliminada de WireGuard")
                    
            elif key_type.lower() == 'outline':
                # Eliminar de Outline
                outline_result = await self.outline_client.delete_key(key_id)
                if not outline_result:
                    logger.error(f"Error eliminando clave {key_id} de Outline")
                    success = False
                else:
                    logger.info(f"Clave {key_id} eliminada de Outline")
            
            return success
            
        except Exception as e:
            logger.error(f"Error eliminando clave {key_id} de servidores: {e}")
            return False
    
    async def delete_key_from_db(self, key_id: str) -> bool:
        """Eliminar una clave de la base de datos."""
        try:
            result = await self.key_repository.delete_key(key_id)
            if result:
                logger.info(f"Clave {key_id} eliminada de la base de datos")
            else:
                logger.error(f"Error eliminando clave {key_id} de la base de datos")
            return result
        except Exception as e:
            logger.error(f"Error eliminando clave {key_id} de BD: {e}")
            return False
    
    async def delete_user_key_complete(self, key_id: str) -> Dict[str, bool]:
        """Eliminar completamente una clave (servidores + BD)."""
        try:
            key = await self.key_repository.get_key(key_id)
            if not key:
                return {
                    'success': False,
                    'server_deleted': False,
                    'db_deleted': False,
                    'error': 'Clave no encontrada'
                }
            
            # Eliminar de servidores
            server_deleted = await self.delete_key_from_servers(key_id, key.key_type)
            
            # Eliminar de BD
            db_deleted = await self.delete_key_from_db(key_id)
            
            success = server_deleted and db_deleted
            
            result = {
                'success': success,
                'server_deleted': server_deleted,
                'db_deleted': db_deleted,
                'key_type': key.key_type,
                'key_name': key.key_name
            }
            
            if success:
                logger.info(f"Clave {key_id} eliminada completamente")
            else:
                logger.error(f"Error en eliminación completa de clave {key_id}: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en eliminación completa de clave {key_id}: {e}")
            return {
                'success': False,
                'server_deleted': False,
                'db_deleted': False,
                'error': str(e)
            }
    
    async def get_server_status(self) -> Dict[str, Dict]:
        """Obtener estado de los servidores VPN."""
        try:
            status = {}
            
            # Estado de WireGuard
            try:
                wg_usage = await self.wireguard_client.get_usage()
                wg_status = ServerStatus(
                    server_type='wireguard',
                    is_healthy=True,
                    total_keys=len(wg_usage),
                    active_keys=len([u for u in wg_usage if u.get('total', 0) > 0]),
                    version='1.0.0',
                    uptime='Unknown',
                    error_message=None
                )
                status['wireguard'] = wg_status.__dict__
            except Exception as e:
                wg_status = ServerStatus(
                    server_type='wireguard',
                    is_healthy=False,
                    total_keys=0,
                    active_keys=0,
                    version=None,
                    uptime=None,
                    error_message=str(e)
                )
                status['wireguard'] = wg_status.__dict__
                logger.error(f"Error obteniendo estado de WireGuard: {e}")
            
            # Estado de Outline
            try:
                outline_info = await self.outline_client.get_server_info()
                outline_status = ServerStatus(
                    server_type='outline',
                    is_healthy=outline_info.get('is_healthy', False),
                    total_keys=outline_info.get('total_keys', 0),
                    active_keys=outline_info.get('total_keys', 0),  # Outline no distingue activas/inactivas fácilmente
                    version=outline_info.get('version'),
                    uptime='Unknown',
                    error_message=outline_info.get('error') if not outline_info.get('is_healthy') else None
                )
                status['outline'] = outline_status.__dict__
            except Exception as e:
                outline_status = ServerStatus(
                    server_type='outline',
                    is_healthy=False,
                    total_keys=0,
                    active_keys=0,
                    version=None,
                    uptime=None,
                    error_message=str(e)
                )
                status['outline'] = outline_status.__dict__
                logger.error(f"Error obteniendo estado de Outline: {e}")
            
            return status
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de servidores: {e}")
            return {}
    
    async def get_key_usage_stats(self, key_id: str) -> Dict:
        """Obtener estadísticas de uso de una clave."""
        try:
            key = await self.key_repository.get_key(key_id)
            if not key:
                return {'data_used': 0, 'server_status': 'not_found'}
            
            data_used = 0
            server_status = 'unknown'
            
            if key.key_type.lower() == 'wireguard':
                try:
                    metrics = await self.wireguard_client.get_peer_metrics(key.key_name)
                    data_used = metrics.get('transfer_total', 0)
                    server_status = 'active' if data_used > 0 else 'inactive'
                except Exception as e:
                    logger.error(f"Error obteniendo métricas WireGuard para {key_id}: {e}")
                    server_status = 'error'
                    
            elif key.key_type.lower() == 'outline':
                try:
                    metrics = await self.outline_client.get_key_usage(key_id)
                    data_used = metrics.get('bytes', 0)
                    server_status = 'active' if data_used > 0 else 'inactive'
                except Exception as e:
                    logger.error(f"Error obteniendo métricas Outline para {key_id}: {e}")
                    server_status = 'error'
            
            return {
                'data_used': data_used,
                'server_status': server_status,
                'last_updated': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de uso para {key_id}: {e}")
            return {'data_used': 0, 'server_status': 'error'}
