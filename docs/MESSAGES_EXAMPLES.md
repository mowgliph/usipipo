# Ejemplos de Uso de Mensajes - uSipipo VPN Bot

## 📖 Introducción

Esta guía contiene ejemplos prácticos de cómo usar el nuevo sistema de mensajes modular en handlers y otros componentes del bot.

---

## 1️⃣ Ejemplos Básicos

### 1.1 Acceso Directo Simple

```python
from telegram_bot.messages import UserMessages, CommonMessages

# Mensajes simples sin variables
texto = UserMessages.Welcome.START
print(texto)

# Botón reutilizable
boton = CommonMessages.Buttons.BACK
print(boton)  # ⬅️ Volver
```

### 1.2 Mensajes con Variables

```python
from telegram_bot.messages import UserMessages

nombre = "Juan"
texto = UserMessages.Welcome.NEW_USER.format(name=nombre)
print(texto)
# 👋 ¡Hola Juan! Bienvenido a **uSipipo VPN**
```

### 1.3 En un Handler

```python
from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.messages import UserMessages

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    nombre = update.effective_user.first_name
    texto = UserMessages.Welcome.START
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=texto,
        parse_mode="HTML"
    )
```

---

## 2️⃣ Ejemplos Intermedios

### 2.1 Seleccionar Mensaje Condicionalmente

```python
from telegram_bot.messages import UserMessages, OperationMessages

async def check_balance(user):
    """Verificar saldo y mostrar mensaje apropiado"""
    
    if user.balance <= 0:
        texto = OperationMessages.Balance.NO_BALANCE
    elif user.is_vip:
        texto = OperationMessages.VIP.ACTIVE.format(
            plan=user.vip_plan,
            expiration=user.vip_expiration.strftime("%d/%m/%Y"),
            auto_renew="Sí" if user.auto_renew else "No"
        )
    else:
        texto = OperationMessages.Balance.DISPLAY.format(
            balance=user.balance,
            total_deposited=user.total_deposited,
            total_spent=user.total_spent,
            referral_earnings=user.referral_earnings
        )
    
    return texto
```

### 2.2 Mensajes con Múltiples Variables

```python
from telegram_bot.messages import AdminMessages

async def show_user_detail(user, context):
    """Mostrar detalles de usuario en panel admin"""
    
    texto = AdminMessages.Users.USER_DETAIL.format(
        name=user.full_name,
        user_id=user.telegram_id,
        username=user.username or "No disponible",
        join_date=user.created_at.strftime("%d/%m/%Y"),
        status="🟢 Activo" if user.is_active else "🔴 Inactivo",
        blocked="Sí" if user.is_blocked else "No",
        keys_count=user.vpn_keys.count(),
        total_usage=sum(k.data_used for k in user.vpn_keys),
        is_vip="Sí" if user.is_vip else "No",
        balance=user.balance,
        tickets_count=user.tickets.count()
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=texto,
        parse_mode="HTML"
    )
```

### 2.3 Factory Pattern para Acceso Dinámico

```python
from telegram_bot.messages import MessageFactory, MessageType

async def send_message_by_type(message_type: str, category: str, 
                               message_name: str, **kwargs):
    """Enviar mensaje dinámicamente basado en tipo"""
    
    try:
        # Convertir string a enum
        msg_type = MessageType[message_type.upper()]
        
        # Obtener mensaje
        texto = MessageFactory.get_message(
            message_type=msg_type,
            category=category,
            message_name=message_name,
            **kwargs
        )
        
        return texto
    except KeyError as e:
        return f"Mensaje no encontrado: {e}"
```

**Uso:**
```python
# Llamadas dinámicas
msg1 = await send_message_by_type("user", "Welcome", "START")
msg2 = await send_message_by_type("admin", "Users", "LIST_HEADER")
msg3 = await send_message_by_type(
    "operations", "VIP", "PRICING",
    monthly_price=9.99,
    quarterly_price=24.99,
    quarterly_discount="25%",
    yearly_price=79.99,
    yearly_discount="30%"
)
```

---

## 3️⃣ Ejemplos Avanzados

### 3.1 MessageBuilder para Mensajes Complejos

```python
from telegram_bot.messages import MessageBuilder

async def create_status_message(user):
    """Crear mensaje de estado personalizado"""
    
    builder = MessageBuilder("📊 **Mi Estado en uSipipo**")
    
    # Información personal
    builder.add_header("Información Personal")
    builder.add_bullet(f"Usuario: {user.full_name}")
    builder.add_bullet(f"ID: `{user.telegram_id}`")
    builder.add_bullet(f"Miembro desde: {user.created_at.strftime('%d/%m/%Y')}")
    
    # Resumen de llaves
    builder.add_header("Mis Llaves VPN")
    active_keys = user.vpn_keys.filter(is_active=True).count()
    builder.add_bullet(f"Activas: {active_keys}")
    builder.add_bullet(f"Totales: {user.vpn_keys.count()}")
    
    # Consumo
    builder.add_header("Consumo")
    total_usage = sum(k.data_used for k in user.vpn_keys)
    builder.add_bullet(f"Total: {total_usage:.2f} GB")
    builder.add_bullet(f"Porcentaje: {(total_usage / user.data_limit * 100):.1f}%")
    
    if user.is_vip:
        builder.add_header("Estado VIP")
        builder.add_bullet("✨ VIP Activo")
        builder.add_bullet(f"Expira: {user.vip_expiration.strftime('%d/%m/%Y')}")
    
    builder.add_footer("¿Necesitas ayuda? Abre un ticket")
    
    return builder.build()
```

### 3.2 MessageRegistry para Templates Reutilizables

```python
from telegram_bot.messages import MessageRegistry

# Registrar mensajes personalizados
MessageRegistry.register(
    "welcome_bonus",
    "🎁 **¡Bienvenido!** Tienes {bonus_gb} GB de regalo"
)

MessageRegistry.register(
    "data_warning",
    "⚠️ **Límite próximo** - {remaining_gb} GB restantes"
)

MessageRegistry.register(
    "key_expiring",
    "⏰ **Vencimiento próximo** - {key_name} expira en {days} días"
)

# Usar en handlers
async def notify_users(context: ContextTypes.DEFAULT_TYPE):
    """Notificar a usuarios sobre eventos importantes"""
    
    # Bonificación de bienvenida
    msg1 = MessageRegistry.get("welcome_bonus", bonus_gb=10)
    
    # Advertencia de datos
    msg2 = MessageRegistry.get("data_warning", remaining_gb=2.5)
    
    # Expiración de llave
    msg3 = MessageRegistry.get(
        "key_expiring",
        key_name="Mi VPN",
        days=5
    )
```

### 3.3 MessageFormatter para Utilidades

```python
from telegram_bot.messages import MessageFormatter

# Truncar texto largo
def format_description(desc: str) -> str:
    return MessageFormatter.truncate(desc, max_length=100, suffix="...")

# Formatear lista de usuarios
def format_user_list(users: list) -> str:
    user_names = [u.full_name for u in users]
    return MessageFormatter.format_list(user_names, bullet="👤")

# Formatear tabla de estadísticas
def format_stats_table(stats: dict) -> str:
    headers = ["Métrica", "Valor"]
    rows = [[k, str(v)] for k, v in stats.items()]
    return MessageFormatter.format_table(headers, rows)

# Agregar emoji
def format_status(text: str, is_active: bool) -> str:
    emoji = "🟢" if is_active else "🔴"
    return MessageFormatter.add_emoji(text, emoji, position="start")

# Destacar texto
def format_important(text: str) -> str:
    return MessageFormatter.highlight(text, style="bold")
```

**Uso completo:**
```python
async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar estadísticas formateadas"""
    
    # Obtener datos
    users = await get_active_users()
    stats = {"Usuarios": 1500, "Llaves": 3200, "Consumo": "15.2 GB"}
    
    # Formatear
    user_list = format_user_list(users[:10])
    stats_table = format_stats_table(stats)
    
    # Construir mensaje
    texto = (
        format_important("📊 ESTADÍSTICAS DEL SISTEMA") + "\n\n" +
        "**Usuarios Activos:**\n" + user_list + "\n\n" +
        "**Métricas Principales:**\n" + stats_table
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=texto,
        parse_mode="HTML"
    )
```

---

## 4️⃣ Ejemplos por Módulo

### 4.1 UserMessages (Usuario Regular)

```python
from telegram_bot.messages import UserMessages

# Bienvenida
welcome = UserMessages.Welcome.START
new_user = UserMessages.Welcome.NEW_USER.format(name="Juan")

# Llaves VPN
keys_header = UserMessages.Keys.LIST_HEADER
keys_created = UserMessages.Keys.CREATED.format(type="WireGuard")
keys_detail = UserMessages.Keys.DETAIL_HEADER.format(
    name="Mi VPN",
    server="US-1",
    protocol="WireGuard",
    usage=2.5,
    limit=10,
    expiration="2024-01-31",
    status="🟢 Activa"
)

# Estado
status = UserMessages.Status.HEADER
status_info = UserMessages.Status.USER_INFO.format(
    name="Juan",
    user_id=123456,
    join_date="2023-01-15",
    status="🟢 Activo"
)

# Ayuda
help_main = UserMessages.Help.MAIN_MENU
help_config = UserMessages.Help.CONFIGURATION
```

### 4.2 AdminMessages (Administrador)

```python
from telegram_bot.messages import AdminMessages

# Menú principal
admin_menu = AdminMessages.Menu.MAIN
users_menu = AdminMessages.Menu.USERS_SUBMENU

# Usuarios
users_header = AdminMessages.Users.LIST_HEADER
user_detail = AdminMessages.Users.USER_DETAIL.format(
    name="Juan Pérez",
    user_id=123456,
    username="juanperez",
    join_date="2023-01-15",
    status="🟢 Activo",
    blocked="No",
    keys_count=3,
    total_usage=15.5,
    is_vip="Sí",
    balance=50.00,
    tickets_count=2
)

# Estadísticas
stats = AdminMessages.Statistics.GENERAL.format(
    total_users=1500,
    active_today=450,
    new_today=12,
    vip_users=200,
    total_keys=3200,
    active_keys=2800,
    wireguard_count=1600,
    outline_count=1600,
    total_traffic=500.5,
    avg_per_user=0.33,
    traffic_today=12.3,
    total_revenue=5000,
    vip_revenue=3000,
    revenue_today=150
)
```

### 4.3 OperationMessages (Operaciones)

```python
from telegram_bot.messages import OperationMessages

# Balance
balance_display = OperationMessages.Balance.DISPLAY.format(
    balance=100.50,
    total_deposited=500.00,
    total_spent=399.50,
    referral_earnings=50.00
)

# VIP
vip_menu = OperationMessages.VIP.MENU
vip_pricing = OperationMessages.VIP.PRICING.format(
    monthly_price=9.99,
    quarterly_price=24.99,
    quarterly_discount="25%",
    yearly_price=79.99,
    yearly_discount="30%"
)
vip_active = OperationMessages.VIP.ACTIVE.format(
    plan="Anual",
    expiration="2024-12-31",
    auto_renew="Sí"
)

# Referidos
referral_menu = OperationMessages.Referral.MENU.format(
    referral_link="https://usipipo.bot?ref=abc123",
    total_earned=250.00,
    referral_count=5
)
```

### 4.4 SupportMessages (Soporte)

```python
from telegram_bot.messages import SupportMessages, TaskMessages

# Tickets
ticket_menu = SupportMessages.Tickets.MENU
ticket_created = SupportMessages.Tickets.CREATED.format(
    ticket_id="TICK-001",
    created_time="2024-01-15 10:30"
)

# FAQ
faq_connection = SupportMessages.FAQ.CONNECTION_ISSUES
faq_payment = SupportMessages.FAQ.PAYMENT_ISSUES

# Tareas
user_tasks = TaskMessages.UserTasks.MENU.format(
    available_count=5,
    completed_today=2,
    total_points=350
)

# Logros
achievements = SupportMessages.Achievements.MENU.format(
    completed_count=8,
    in_progress_count=3,
    total_points=500,
    pending_count=1
)
```

### 4.5 CommonMessages (Común/Reutilizable)

```python
from telegram_bot.messages import CommonMessages

# Navegación
back_btn = CommonMessages.Buttons.BACK
home_btn = CommonMessages.Home
next_btn = CommonMessages.Buttons.NEXT

# Confirmaciones
confirm = CommonMessages.Confirmation.GENERIC.format(
    message="¿Estás seguro?"
)
delete_confirm = CommonMessages.Confirmation.DELETE.format(
    item="Llave VPN - Mi Conexión"
)

# Errores
error_generic = CommonMessages.Errors.GENERIC
error_network = CommonMessages.Errors.NETWORK
error_unauthorized = CommonMessages.Errors.UNAUTHORIZED

# Estados
loading = CommonMessages.Status.LOADING
active = CommonMessages.Status.ACTIVE
inactive = CommonMessages.Status.INACTIVE
```

---

## 5️⃣ Patrones Comunes

### 5.1 Mensaje Condicional Simple

```python
async def send_key_status(key, context):
    if key.is_active:
        msg = UserMessages.Keys.DETAIL_HEADER.format(...)
    elif key.is_expired:
        msg = UserMessages.Errors.KEY_EXPIRED
    else:
        msg = CommonMessages.Errors.GENERIC
    
    await context.bot.send_message(chat_id=..., text=msg)
```

### 5.2 Mensaje con Lista Dinámica

```python
from telegram_bot.messages import MessageFormatter

async def show_keys(user):
    keys = user.vpn_keys.all()
    
    if not keys:
        return UserMessages.Keys.NO_KEYS
    
    header = UserMessages.Keys.LIST_HEADER
    key_list = []
    
    for key in keys:
        entry = UserMessages.Keys.ENTRY.format(
            name=key.name,
            protocol=key.protocol,
            usage=key.data_used,
            limit=key.data_limit,
            expiration=key.expiration.strftime("%d/%m/%Y")
        )
        key_list.append(entry)
    
    return header + "\n" + "\n".join(key_list)
```

### 5.3 Mensaje Paginado

```python
from telegram_bot.messages import MessageFormatter, CommonMessages

async def show_users_paginated(page: int, per_page: int = 10):
    total_users = User.objects.count()
    total_pages = (total_users + per_page - 1) // per_page
    
    users = User.objects.all()[
        (page - 1) * per_page:page * per_page
    ]
    
    header = AdminMessages.Users.LIST_HEADER
    pagination = CommonMessages.Pagination.HEADER.format(
        current=page,
        total=total_pages,
        count=len(users)
    )
    
    user_entries = []
    for user in users:
        entry = AdminMessages.Users.USER_ENTRY.format(
            name=user.full_name,
            user_id=user.telegram_id,
            join_date=user.created_at.strftime("%d/%m/%Y"),
            status="🟢 Activo" if user.is_active else "🔴"
        )
        user_entries.append(entry)
    
    return header + pagination + "\n" + "\n".join(user_entries)
```

### 5.4 Manejo de Errores

```python
from telegram_bot.messages import CommonMessages

async def safe_operation(operation_func):
    try:
        result = await operation_func()
        return result
    except ConnectionError:
        return CommonMessages.Errors.NETWORK
    except ValueError as e:
        return CommonMessages.Errors.VALIDATION_ERROR.format(details=str(e))
    except Exception as e:
        return CommonMessages.Errors.SERVER_ERROR
```

---

## 6️⃣ Tips y Trucos

### 6.1 Alias para Acceso Rápido

```python
from telegram_bot.messages import (
    UserMessages as UM,
    AdminMessages as AM,
    OperationMessages as OM,
    CommonMessages as CM
)

# Más conciso
msg = UM.Welcome.START
msg = AM.Users.LIST_HEADER
msg = OM.VIP.PRICING.format(...)
msg = CM.Buttons.BACK
```

### 6.2 Factory con Enum

```python
from enum import Enum
from telegram_bot.messages import MessageFactory, MessageType

class MessageConfig(Enum):
    WELCOME = (MessageType.USER, "Welcome", "START")
    USER_LIST = (MessageType.ADMIN, "Users", "LIST_HEADER")
    VIP_MENU = (MessageType.OPERATIONS, "VIP", "MENU")

# Uso simple
msg = MessageFactory.get_message(*MessageConfig.WELCOME.value)
```

### 6.3 Cache de Mensajes

```python
from functools import lru_cache
from telegram_bot.messages import UserMessages

@lru_cache(maxsize=100)
def get_formatted_message(msg_key: str, **kwargs):
    parts = msg_key.split(".")
    cls = getattr(__import__('telegram_bot.messages', fromlist=[parts[0]]), parts[0])
    for part in parts[1:]:
        cls = getattr(cls, part)
    return cls.format(**kwargs) if kwargs else cls
```

---

## 📝 Resumen

### Acceso Directo
```python
UserMessages.Welcome.START
AdminMessages.Users.LIST_HEADER
```

### Con Formateo
```python
msg.format(name="Juan", user_id=123)
```

### Factory
```python
MessageFactory.get_message(MessageType.USER, "Welcome", "START")
```

### Builder
```python
MessageBuilder("Título").add_section(...).build()
```

### Registry
```python
MessageRegistry.register("key", "template")
MessageRegistry.get("key", var=value)
```

### Formatter
```python
MessageFormatter.truncate(text, 100)
MessageFormatter.format_list(items)
```

---

**Documento:** MESSAGES_EXAMPLES.md  
**Versión:** 1.0.0  
**Última Actualización:** 2024  
**Estado:** ✅ Completo
