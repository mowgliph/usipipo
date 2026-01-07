"""
EJEMPLOS DE USO - Sistema de Gestión de Usuarios y Shop

Este archivo contiene ejemplos de cómo usar las nuevas funcionalidades implementadas.
"""

# ============================================================
# EJEMPLO 1: Usar AdminService para gestionar usuarios
# ============================================================

from application.services.admin_service import AdminService
from domain.entities.user import UserRole, UserStatus
import asyncio

async def ejemplo_gestion_usuarios(admin_service: AdminService):
    """Ejemplos de uso de métodos de gestión de usuarios."""
    
    user_id = 123456789  # ID de Telegram del usuario
    
    # 1. Obtener información detallada de un usuario
    user_info = await admin_service.get_user_by_id(user_id)
    print(f"Usuario: {user_info['full_name']}")
    print(f"Estado: {user_info['status']}")
    print(f"Rol: {user_info['role']}")
    print(f"VIP: {'Sí' if user_info['is_vip'] else 'No'}")
    
    # 2. Cambiar estado del usuario a BLOQUEADO
    result = await admin_service.block_user(user_id)
    if result.success:
        print(f"✅ Usuario bloqueado: {result.message}")
    else:
        print(f"❌ Error: {result.message}")
    
    # 3. Desbloquear usuario
    result = await admin_service.unblock_user(user_id)
    if result.success:
        print(f"✅ Usuario desbloqueado: {result.message}")
    
    # 4. Asignar rol de GESTOR DE TAREAS por 30 días
    result = await admin_service.assign_role_to_user(
        user_id=user_id,
        role=UserRole.TASK_MANAGER.value,
        duration_days=30
    )
    if result.success:
        print(f"✅ Rol asignado: {result.message}")
        print(f"Expira en: {result.details['duration_days']} días")
    
    # 5. Asignar rol de ADMIN (sin expiración)
    result = await admin_service.assign_role_to_user(
        user_id=user_id,
        role=UserRole.ADMIN.value
    )
    if result.success:
        print(f"✅ {result.message}")
    
    # 6. Cambiar estado a SUSPENDIDO
    result = await admin_service.update_user_status(
        user_id=user_id,
        status=UserStatus.SUSPENDED.value
    )
    if result.success:
        print(f"✅ {result.message}")
    
    # 7. Obtener usuarios paginados
    paginated = await admin_service.get_users_paginated(page=1, per_page=10)
    print(f"Total de usuarios: {paginated['total_users']}")
    print(f"Página actual: {paginated['page']}/{paginated['total_pages']}")
    for user in paginated['users']:
        print(f"  - {user['full_name']} ({user['role']})")
    
    # 8. Eliminar usuario (CUIDADO - acción irreversible)
    result = await admin_service.delete_user(user_id)
    if result.success:
        print(f"✅ {result.message}")
        print(f"Claves eliminadas: {result.details['deleted_keys']}")


# ============================================================
# EJEMPLO 2: Usar ShopHandler para compras
# ============================================================

from telegram_bot.handlers.shop_handler import ShopHandler

async def ejemplo_shop_handler(payment_service):
    """Ejemplos de funcionalidades del shop."""
    
    shop = ShopHandler(payment_service)
    
    # 1. Obtener información de un producto VIP
    product_info = shop._get_product_info('vip', '1month')
    print(f"Producto: {product_info['name']}")
    print(f"Costo: {product_info['cost']} ⭐")
    print(f"Duración: {product_info['duration_days']} días")
    
    # 2. Obtener información de rol premium
    product_info = shop._get_product_info('role', 'task_manager_1month')
    print(f"\nProducto: {product_info['name']}")
    print(f"Costo: {product_info['cost']} ⭐")
    
    # 3. Obtener información de almacenamiento
    product_info = shop._get_product_info('storage', '50gb')
    print(f"\nProducto: {product_info['name']}")
    print(f"Costo: {product_info['cost']} ⭐")
    print(f"GB incluidos: {product_info['gb']}")


# ============================================================
# EJEMPLO 3: Roles y sus características
# ============================================================

from domain.entities.user import User, UserRole, UserStatus

def ejemplo_roles_usuarios():
    """Ejemplos de creación de usuarios con diferentes roles."""
    
    # 1. Usuario regular
    usuario_regular = User(
        telegram_id=111111111,
        username="usuario1",
        full_name="Juan Pérez",
        role=UserRole.USER
    )
    print(f"Rol: {usuario_regular.role.value}")
    print(f"¿Es admin?: {usuario_regular.role == UserRole.ADMIN}")
    
    # 2. Admin
    admin = User(
        telegram_id=222222222,
        username="admin",
        full_name="Admin Bot",
        role=UserRole.ADMIN
    )
    print(f"\nRol: {admin.role.value}")
    print(f"¿Es admin?: {admin.role == UserRole.ADMIN}")
    
    # 3. Usuario con rol GESTOR DE TAREAS
    from datetime import datetime, timedelta, timezone
    
    gestor = User(
        telegram_id=333333333,
        username="gestor",
        full_name="Gestor Bot",
        role=UserRole.TASK_MANAGER,
        task_manager_expires_at=datetime.now(timezone.utc) + timedelta(days=30)
    )
    print(f"\nRol: {gestor.role.value}")
    print(f"¿Gestor activo?: {gestor.is_task_manager_active()}")
    
    # 4. Usuario con rol ANUNCIANTE
    anunciante = User(
        telegram_id=444444444,
        username="anunciante",
        full_name="Anunciante Bot",
        role=UserRole.ANNOUNCER,
        announcer_expires_at=datetime.now(timezone.utc) + timedelta(days=60)
    )
    print(f"\nRol: {anunciante.role.value}")
    print(f"¿Anunciante activo?: {anunciante.is_announcer_active()}")


# ============================================================
# EJEMPLO 4: Estados de usuario
# ============================================================

from domain.entities.user import User, UserStatus

def ejemplo_estados_usuarios():
    """Ejemplos de diferentes estados de usuario."""
    
    # 1. Usuario activo
    user_active = User(
        telegram_id=111111111,
        username="user1",
        status=UserStatus.ACTIVE
    )
    print(f"Estado: {user_active.status.value}")
    print(f"¿Está activo?: {user_active.is_active}")
    print(f"¿Está bloqueado?: {user_active.is_blocked}")
    
    # 2. Usuario bloqueado
    user_blocked = User(
        telegram_id=222222222,
        username="user2",
        status=UserStatus.BLOCKED
    )
    print(f"\nEstado: {user_blocked.status.value}")
    print(f"¿Está activo?: {user_blocked.is_active}")
    print(f"¿Está bloqueado?: {user_blocked.is_blocked}")
    
    # 3. Usuario en prueba gratis
    user_trial = User(
        telegram_id=333333333,
        username="user3",
        status=UserStatus.FREE_TRIAL
    )
    print(f"\nEstado: {user_trial.status.value}")
    print(f"¿Está activo?: {user_trial.is_active}")
    print(f"¿Está bloqueado?: {user_trial.is_blocked}")
    
    # 4. Usuario suspendido
    user_suspended = User(
        telegram_id=444444444,
        username="user4",
        status=UserStatus.SUSPENDED
    )
    print(f"\nEstado: {user_suspended.status.value}")


# ============================================================
# EJEMPLO 5: Precios de productos en Shop
# ============================================================

def ejemplo_precios_shop():
    """Ejemplos de precios de productos disponibles."""
    
    from telegram_bot.handlers.shop_handler import ShopHandler
    
    # Crear instancia (dummy)
    handler = ShopHandler(None)
    
    print("=" * 60)
    print("PLANES VIP")
    print("=" * 60)
    for key in ['1month', '3months', '6months', '12months']:
        info = handler._get_product_info('vip', key)
        print(f"{info['name']:30} {info['cost']:3}⭐ ({info['duration_days']} días)")
    
    print("\n" + "=" * 60)
    print("ROLES PREMIUM - GESTOR DE TAREAS")
    print("=" * 60)
    for key in ['task_manager_1month', 'task_manager_3months', 'task_manager_6months', 'task_manager_1year']:
        info = handler._get_product_info('role', key)
        print(f"{info['name']:30} {info['cost']:3}⭐ ({info['duration_days']} días)")
    
    print("\n" + "=" * 60)
    print("ROLES PREMIUM - ANUNCIANTE")
    print("=" * 60)
    for key in ['announcer_1month', 'announcer_3months', 'announcer_6months', 'announcer_1year']:
        info = handler._get_product_info('role', key)
        print(f"{info['name']:30} {info['cost']:3}⭐ ({info['duration_days']} días)")
    
    print("\n" + "=" * 60)
    print("ALMACENAMIENTO")
    print("=" * 60)
    for key in ['10gb', '25gb', '50gb', '200gb']:
        info = handler._get_product_info('storage', key)
        print(f"{info['name']:30} {info['cost']:3}⭐ ({info['gb']} GB)")


# ============================================================
# EJEMPLO 6: Callbacks en el Handler de Admin
# ============================================================

"""
# Ejemplo de cómo se llamarían los callbacks en inline_callbacks_handler.py

# 1. Mostrar submenu de usuarios
callbacks.append(
    CallbackQueryHandler(
        admin_users_handler.users_submenu,
        pattern="^admin_users_submenu$"
    )
)

# 2. Bloquear usuario
callbacks.append(
    CallbackQueryHandler(
        admin_users_handler.block_user_confirm,
        pattern="^admin_block_user$"
    )
)

# 3. Asignar rol
callbacks.append(
    CallbackQueryHandler(
        admin_users_handler.assign_role_menu,
        pattern="^admin_assign_roles$"
    )
)
"""


# ============================================================
# EJEMPLO 7: Flujo completo de una compra en el Shop
# ============================================================

"""
Flujo de usuario en el Shop:

1. Usuario presiona: Operaciones → 🛒 Shop
   → Llama: ShopHandler.shop_menu()
   
2. Usuario selecciona: 👑 Planes VIP
   → Llama: ShopHandler.show_vip_plans()
   
3. Usuario selecciona: 1 Mes - 10⭐
   → Llama: ShopHandler.confirm_purchase() con callback_data="shop_vip_1month"
   
4. Sistema verifica balance y muestra confirmación
   
5. Usuario confirma compra
   → Llama: ShopHandler.execute_purchase()
   
6. Si balance > costo:
   - ShopHandler._process_purchase()
   - Descontar balance
   - Activar VIP (llamar PaymentService.activate_vip())
   - Mostrar confirmación
   
7. Si balance < costo:
   - Mostrar error de balance insuficiente
   - Ofrecer recargar estrellas
"""


if __name__ == "__main__":
    print("📋 EJEMPLOS DE USO - Sistema de Gestión de Usuarios y Shop\n")
    
    # Ejecutar ejemplos que no requieren async
    print("1. ROLES DE USUARIOS")
    print("-" * 60)
    ejemplo_roles_usuarios()
    
    print("\n\n2. ESTADOS DE USUARIOS")
    print("-" * 60)
    ejemplo_estados_usuarios()
    
    print("\n\n3. PRECIOS EN SHOP")
    print("-" * 60)
    ejemplo_precios_shop()
    
    print("\n\n✅ Ejemplos completados")
