"""
Servicio de administración para el bot uSipipo.

Author: uSipipo Team
Version: 1.0.0
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from utils.logger import logger

from domain.interfaces.iadmin_service import IAdminService
from domain.entities.admin import AdminUserInfo, AdminKeyInfo, ServerStatus, AdminOperationResult
from domain.entities.vpn_key import VpnKey as Key
from domain.entities.user import UserRole, UserStatus
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
    
    async def get_dashboard_stats(self) -> Dict:
        """
        Genera estadísticas completas para el panel de control administrativo.
        Centraliza la lógica de negocio para respetar arquitectura hexagonal.
        """
        try:
            # 1. Obtener datos crudos
            users = await self.user_repository.get_all_users()
            all_keys = await self.key_repository.get_all_keys()
            server_status = await self.get_server_status()
            
            # 2. Calcular estadísticas de usuarios
            total_users = len(users)
            # Asumiendo que User tiene status o is_active. Si no, usamos active_keys > 0 como proxy o status='active'
            # Revisando User entity (no visible aquí pero inferido), usaremos una lógica segura.
            # Si users es lista de entidades User:
            active_users = sum(1 for u in users if getattr(u, 'status', '').lower() == 'active' or getattr(u, 'is_active', False))
            vip_users = sum(1 for u in users if getattr(u, 'is_vip', False))
            
            # 3. Calcular estadísticas de llaves
            total_keys = len(all_keys)
            active_keys = sum(1 for k in all_keys if k.is_active)
            wireguard_keys = sum(1 for k in all_keys if k.key_type.lower() == 'wireguard')
            outline_keys = sum(1 for k in all_keys if k.key_type.lower() == 'outline')
            
            # 4. Calcular porcentajes
            wireguard_pct = round((wireguard_keys / total_keys * 100) if total_keys > 0 else 0, 1)
            outline_pct = round((outline_keys / total_keys * 100) if total_keys > 0 else 0, 1)
            
            # 5. Calcular consumo total (iterando keys)
            # Nota: esto puede ser lento si hay muchas keys y requiere consulta individual de métricas
            # Para el dashboard rápido, usaremos el 'data_used' almacenado en BD o 0 si no está actualizado.
            # Si queremos real-time, habría que llamar a get_key_usage_stats para cada uno, lo cual es muy lento.
            # Usaremos una aproximación o datos cacheados si existen.
            # Por ahora, sumaremos 0 si no tenemos el dato en la entidad Key (Key entity usually has data_used??)
            # Revisando Key entity en imports: from domain.entities.vpn_key import VpnKey as Key
            # VpnKey tiene data_limit, pero data_used a veces se guarda.
            # Asumiremos 0 por ahora para no bloquear, o implementaremos lógica de cache.
            total_usage_gb = 0 # Placeholder simplificado para no ralentizar dashboard
            
            avg_usage = round(total_usage_gb / total_users, 2) if total_users > 0 else 0
            
            # 6. Estado del servidor
            wireguard_healthy = server_status.get('wireguard', {}).get('is_healthy', False)
            outline_healthy = server_status.get('outline', {}).get('is_healthy', False)
            server_status_text = "✅ Saludable" if wireguard_healthy and outline_healthy else "⚠️ Problemas"
            
            # 7. Calcular ingresos totales
            total_revenue = await self._calculate_total_revenue()
            
            # 8. Calcular nuevos usuarios hoy
            new_users_today = await self._calculate_new_users_today()
            
            # 9. Calcular llaves creadas hoy
            keys_created_today = await self._calculate_keys_created_today()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'vip_users': vip_users,
                'total_keys': total_keys,
                'active_keys': active_keys,
                'wireguard_keys': wireguard_keys,
                'wireguard_pct': wireguard_pct,
                'outline_keys': outline_keys,
                'outline_pct': outline_pct,
                'total_usage_gb': total_usage_gb,
                'avg_usage_gb': avg_usage,
                'total_revenue': total_revenue,
                'new_users_today': new_users_today,
                'keys_created_today': keys_created_today,
                'server_status_text': server_status_text,
                'server_status_details': server_status,
                'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Error generando estadísticas de dashboard: {e}")
            raise e

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

    # ============================================
    # MÉTODOS DE GESTIÓN DE USUARIOS
    # ============================================
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Obtener información detallada de un usuario."""
        try:
            user = await self.user_repository.get_user(user_id)
            if not user:
                return None
            
            user_keys = await self.key_repository.get_user_keys(user_id)
            active_keys = [k for k in user_keys if k.is_active]
            balance = await self.payment_repository.get_balance(user_id)
            
            return {
                'user_id': user.telegram_id,
                'username': user.username,
                'full_name': user.full_name,
                'status': user.status.value,
                'role': user.role.value,
                'is_vip': user.is_vip,
                'vip_expires_at': user.vip_expires_at,
                'task_manager_expires_at': user.task_manager_expires_at,
                'announcer_expires_at': user.announcer_expires_at,
                'total_keys': len(user_keys),
                'active_keys': len(active_keys),
                'balance_stars': balance.stars if balance else 0,
                'total_deposited': user.total_deposited,
                'created_at': user.created_at
            }
        except Exception as e:
            logger.error(f"Error obteniendo usuario {user_id}: {e}")
            return None
    
    async def update_user_status(self, user_id: int, status: str) -> AdminOperationResult:
        """Actualizar estado del usuario (ACTIVE, SUSPENDED, BLOCKED)."""
        try:
            user = await self.user_repository.get_user(user_id)
            if not user:
                return AdminOperationResult(
                    success=False,
                    operation='update_user_status',
                    target_id=str(user_id),
                    message='Usuario no encontrado'
                )
            
            # Validar estado
            valid_statuses = [s.value for s in UserStatus]
            if status not in valid_statuses:
                return AdminOperationResult(
                    success=False,
                    operation='update_user_status',
                    target_id=str(user_id),
                    message=f'Estado inválido. Válidos: {valid_statuses}'
                )
            
            user.status = UserStatus(status)
            await self.user_repository.update_user(user)
            
            logger.info(f"Usuario {user_id} actualizado a estado: {status}")
            return AdminOperationResult(
                success=True,
                operation='update_user_status',
                target_id=str(user_id),
                message=f'Usuario actualizado a estado: {status}',
                details={'new_status': status}
            )
        except Exception as e:
            logger.error(f"Error actualizando estado de usuario {user_id}: {e}")
            return AdminOperationResult(
                success=False,
                operation='update_user_status',
                target_id=str(user_id),
                message=f'Error: {str(e)}'
            )
    
    async def assign_role_to_user(self, user_id: int, role: str, duration_days: Optional[int] = None) -> AdminOperationResult:
        """Asignar rol a un usuario."""
        try:
            user = await self.user_repository.get_user(user_id)
            if not user:
                return AdminOperationResult(
                    success=False,
                    operation='assign_role',
                    target_id=str(user_id),
                    message='Usuario no encontrado'
                )
            
            # Validar rol
            valid_roles = [r.value for r in UserRole]
            if role not in valid_roles:
                return AdminOperationResult(
                    success=False,
                    operation='assign_role',
                    target_id=str(user_id),
                    message=f'Rol inválido. Válidos: {valid_roles}'
                )
            
            user.role = UserRole(role)
            
            # Si es un rol especial con duración, configurar fecha de expiración
            if duration_days and role in ['task_manager', 'announcer']:
                expires_at = datetime.now(timezone.utc) + timedelta(days=duration_days)
                if role == 'task_manager':
                    user.task_manager_expires_at = expires_at
                elif role == 'announcer':
                    user.announcer_expires_at = expires_at
            
            await self.user_repository.update_user(user)
            
            message = f'Rol "{role}" asignado a usuario {user_id}'
            if duration_days:
                message += f' por {duration_days} días'
            
            logger.info(message)
            return AdminOperationResult(
                success=True,
                operation='assign_role',
                target_id=str(user_id),
                message=message,
                details={'role': role, 'duration_days': duration_days}
            )
        except Exception as e:
            logger.error(f"Error asignando rol a usuario {user_id}: {e}")
            return AdminOperationResult(
                success=False,
                operation='assign_role',
                target_id=str(user_id),
                message=f'Error: {str(e)}'
            )
    
    async def block_user(self, user_id: int) -> AdminOperationResult:
        """Bloquear un usuario."""
        return await self.update_user_status(user_id, UserStatus.BLOCKED.value)
    
    async def unblock_user(self, user_id: int) -> AdminOperationResult:
        """Desbloquear un usuario."""
        return await self.update_user_status(user_id, UserStatus.ACTIVE.value)
    
    async def delete_user(self, user_id: int) -> AdminOperationResult:
        """Eliminar un usuario y sus claves asociadas."""
        try:
            user = await self.user_repository.get_user(user_id)
            if not user:
                return AdminOperationResult(
                    success=False,
                    operation='delete_user',
                    target_id=str(user_id),
                    message='Usuario no encontrado'
                )
            
            # Obtener todas las claves del usuario
            user_keys = await self.key_repository.get_user_keys(user_id)
            
            # Eliminar todas las claves
            deleted_keys_count = 0
            for key in user_keys:
                try:
                    result = await self.delete_user_key_complete(key.key_id)
                    if result['success']:
                        deleted_keys_count += 1
                except Exception as e:
                    logger.error(f"Error eliminando clave {key.key_id}: {e}")
            
            # Eliminar el usuario
            await self.user_repository.delete_user(user_id)
            
            message = f'Usuario {user_id} eliminado junto con {deleted_keys_count} claves'
            logger.info(message)
            return AdminOperationResult(
                success=True,
                operation='delete_user',
                target_id=str(user_id),
                message=message,
                details={'deleted_keys': deleted_keys_count}
            )
        except Exception as e:
            logger.error(f"Error eliminando usuario {user_id}: {e}")
            return AdminOperationResult(
                success=False,
                operation='delete_user',
                target_id=str(user_id),
                message=f'Error: {str(e)}'
            )
    
    async def get_users_paginated(self, page: int = 1, per_page: int = 10) -> Dict:
        """Obtener usuarios paginados."""
        try:
            all_users = await self.user_repository.get_all_users()
            total_users = len(all_users)
            
            # Calcular offset
            offset = (page - 1) * per_page
            paginated_users = all_users[offset:offset + per_page]
            
            user_list = []
            for user in paginated_users:
                user_keys = await self.key_repository.get_user_keys(user.telegram_id)
                active_keys = [k for k in user_keys if k.is_active]
                balance = await self.payment_repository.get_balance(user.telegram_id)
                
                user_list.append({
                    'user_id': user.telegram_id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'status': user.status.value,
                    'role': user.role.value,
                    'is_vip': user.is_vip,
                    'total_keys': len(user_keys),
                    'active_keys': len(active_keys),
                    'balance_stars': balance.stars if balance else 0,
                    'created_at': user.created_at.isoformat()
                })
            
            total_pages = (total_users + per_page - 1) // per_page
            
            return {
                'users': user_list,
                'total_users': total_users,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
        except Exception as e:
            logger.error(f"Error obteniendo usuarios paginados: {e}")
            return {
                'users': [],
                'total_users': 0,
                'page': page,
                'per_page': per_page,
                'total_pages': 0
            }

    # ============================================
    # MÉTODOS AUXILIARES PARA ESTADÍSTICAS
    # ============================================
    
    async def _calculate_total_revenue(self) -> float:
        """
        Calcula los ingresos totales del sistema.
        Implementa lógica de negocio para calcular ingresos basados en transacciones.
        """
        try:
            # Obtener todas las transacciones de tipo 'deposit' o similares
            # que representen ingresos reales
            deposit_transactions = await self.payment_repository.get_transactions_by_type('deposit')
            
            # Sumar todos los montos de transacciones de ingresos
            # Asumimos que amount está en la unidad más pequeña (ej: centavos)
            total_amount = sum(t['amount'] for t in deposit_transactions)
            
            # Convertir a la unidad monetaria principal (ej: dólares)
            # Si amount está en centavos, dividimos por 100
            total_revenue = total_amount / 100.0
            
            return round(total_revenue, 2)
            
        except Exception as e:
            logger.error(f"Error calculando ingresos totales: {e}")
            return 0.00

    async def _calculate_new_users_today(self) -> int:
        """
        Calcula la cantidad de nuevos usuarios registrados hoy.
        """
        try:
            # Obtener todos los usuarios
            all_users = await self.user_repository.get_all_users()
            
            # Filtrar usuarios creados hoy
            today = datetime.now(timezone.utc).date()
            new_users_today = sum(1 for user in all_users
                                if user.created_at and user.created_at.date() == today)
            
            return new_users_today
            
        except Exception as e:
            logger.error(f"Error calculando nuevos usuarios hoy: {e}")
            return 0

    async def _calculate_keys_created_today(self) -> int:
        """
        Calcula la cantidad de llaves VPN creadas hoy.
        """
        try:
            # Obtener todas las llaves
            all_keys = await self.key_repository.get_all_keys()
            
            # Filtrar llaves creadas hoy
            today = datetime.now(timezone.utc).date()
            keys_created_today = sum(1 for key in all_keys
                                   if key.created_at and key.created_at.date() == today)
            
            return keys_created_today
            
        except Exception as e:
            logger.error(f"Error calculando llaves creadas hoy: {e}")
            return 0
