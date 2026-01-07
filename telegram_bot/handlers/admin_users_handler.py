"""
Handler para gestión de usuarios en el panel de administración.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import settings
from utils.logger import logger
from datetime import datetime

from application.services.admin_service import AdminService
from telegram_bot.messages.admin_messages import AdminMessages
from telegram_bot.keyboard import AdminKeyboards
from utils.spinner import with_spinner

# Estados de conversación
ADMIN_USERS_MENU = 0
ADMIN_USERS_LIST = 1
ADMIN_USER_DETAIL = 2
ADMIN_SELECT_ROLE = 3
ADMIN_SELECT_STATUS = 4
ADMIN_BLOCK_USER = 5
ADMIN_DELETE_USER = 6
ADMIN_CONFIRM_ACTION = 7
ADMIN_ROLE_DURATION = 8


class AdminUsersHandler:
    """Handler para gestión de usuarios del panel de administración."""

    def __init__(self, admin_service: AdminService):
        self.admin_service = admin_service
        self.pending_actions = {}  # Para almacenar acciones en progreso

    async def users_submenu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar submenu de gestión de usuarios."""
        query = update.callback_query
        await query.answer()

        try:
            await query.edit_message_text(
                text=AdminMessages.USERS_SUBMENU_TITLE,
                reply_markup=AdminKeyboards.users_submenu(),
                parse_mode="Markdown"
            )
            return ADMIN_USERS_MENU
        except Exception as e:
            logger.error(f"Error en submenu de usuarios: {e}")
            await query.edit_message_text(
                text=AdminMessages.ERROR.format(error=str(e)),
                reply_markup=AdminKeyboards.main_menu()
            )
            return ConversationHandler.END

    async def show_users_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1):
        """Mostrar lista paginada de usuarios."""
        query = update.callback_query
        await query.answer()

        try:
            # Obtener usuarios paginados
            result = await self.admin_service.get_users_paginated(page=page, per_page=10)
            users = result['users']
            total_pages = result['total_pages']
            total_users = result['total_users']

            if not users:
                await query.edit_message_text(
                    text=AdminMessages.NO_USERS,
                    reply_markup=AdminKeyboards.users_submenu()
                )
                return ADMIN_USERS_MENU

            # Formatear lista de usuarios
            user_lines = []
            for user in users:
                status_emoji = {
                    'active': '🟢',
                    'suspended': '🟡',
                    'blocked': '🔴',
                    'free_trial': '📋'
                }.get(user['status'], '❓')

                vip_status = "👑" if user['is_vip'] else "👤"
                created_date = datetime.fromisoformat(user['created_at']).strftime("%d/%m/%Y")

                user_line = AdminMessages.USER_ENTRY.format(
                    name=user['full_name'] or user['username'] or 'Sin nombre',
                    user_id=user['user_id'],
                    status=status_emoji,
                    role=user['role'].upper(),
                    vip=vip_status,
                    keys=user['active_keys'],
                    balance=user['balance_stars'],
                    created_at=created_date
                )
                user_lines.append(user_line)

            message = AdminMessages.USERS_LIST_HEADER.format(
                total_users=total_users,
                page=page,
                total_pages=total_pages,
                users="\n\n".join(user_lines)
            )

            await query.edit_message_text(
                text=message,
                reply_markup=AdminKeyboards.users_list_pagination(page, total_pages),
                parse_mode="Markdown"
            )
            return ADMIN_USERS_LIST

        except Exception as e:
            logger.error(f"Error mostrando lista de usuarios: {e}")
            await query.edit_message_text(
                text=AdminMessages.ERROR.format(error=str(e)),
                reply_markup=AdminKeyboards.users_submenu()
            )
            return ADMIN_USERS_MENU

    async def handle_pagination(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar paginación de usuarios."""
        query = update.callback_query
        callback_data = query.data

        if callback_data.startswith("admin_users_page_"):
            page = int(callback_data.split("_")[-1])
            return await self.show_users_list(update, context, page=page)
        elif callback_data == "admin_users_list":
            return await self.show_users_list(update, context, page=1)

    async def show_user_detail(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar detalles de un usuario."""
        query = update.callback_query
        await query.answer()

        try:
            # Obtener user_id del callback_data
            user_id = int(context.user_data.get('selected_user_id', 0))
            if not user_id:
                await query.answer("❌ Usuario no seleccionado", show_alert=True)
                return ADMIN_USERS_MENU

            user_info = await self.admin_service.get_user_by_id(user_id)
            if not user_info:
                await query.edit_message_text(
                    text="❌ Usuario no encontrado",
                    reply_markup=AdminKeyboards.users_submenu()
                )
                return ADMIN_USERS_MENU

            # Determinar estado VIP
            vip_status = "✅ Activo" if user_info['is_vip'] else "❌ Inactivo"
            if user_info['vip_expires_at']:
                vip_date = user_info['vip_expires_at'].strftime("%d/%m/%Y %H:%M") if isinstance(user_info['vip_expires_at'], datetime) else str(user_info['vip_expires_at'])
            else:
                vip_date = "N/A"

            # Determinar estado de roles premium
            task_manager_status = "✅ Activo" if user_info['task_manager_expires_at'] else "❌ Inactivo"
            announcer_status = "✅ Activo" if user_info['announcer_expires_at'] else "❌ Inactivo"

            # Formatear mensaje
            message = AdminMessages.USER_DETAIL.format(
                user_id=user_info['user_id'],
                full_name=user_info['full_name'] or 'N/A',
                username=user_info['username'] or 'N/A',
                status=self._format_status(user_info['status']),
                role=user_info['role'].upper(),
                vip_status=f"{vip_status} (Expira: {vip_date})",
                total_keys=user_info['total_keys'],
                active_keys=user_info['active_keys'],
                balance_stars=user_info['balance_stars'],
                total_deposited=user_info['total_deposited'],
                task_manager=task_manager_status,
                announcer=announcer_status,
                created_at=user_info['created_at'].strftime("%d/%m/%Y") if isinstance(user_info['created_at'], datetime) else str(user_info['created_at']),
                vip_expires=vip_date
            )

            await query.edit_message_text(
                text=message,
                reply_markup=AdminKeyboards.user_detail_actions(user_id),
                parse_mode="Markdown"
            )
            return ADMIN_USER_DETAIL

        except Exception as e:
            logger.error(f"Error mostrando detalles de usuario: {e}")
            await query.edit_message_text(
                text=AdminMessages.ERROR.format(error=str(e)),
                reply_markup=AdminKeyboards.users_submenu()
            )
            return ADMIN_USERS_MENU

    async def block_user_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar confirmación para bloquear un usuario."""
        query = update.callback_query
        await query.answer()

        try:
            user_id = int(context.user_data.get('selected_user_id', 0))
            user_info = await self.admin_service.get_user_by_id(user_id)

            if not user_info:
                await query.answer("❌ Usuario no encontrado", show_alert=True)
                return ADMIN_USERS_MENU

            message = AdminMessages.BLOCK_USER_CONFIRM.format(
                user_id=user_id,
                user_name=user_info['full_name'] or user_info['username'] or 'Usuario'
            )

            keyboard = [
                [
                    InlineKeyboardButton("✅ Bloquear", callback_data=f"admin_confirm_block_{user_id}"),
                    InlineKeyboardButton("❌ Cancelar", callback_data="admin_users_list")
                ]
            ]

            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return ADMIN_BLOCK_USER

        except Exception as e:
            logger.error(f"Error en confirmación de bloqueo: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return ADMIN_USERS_MENU

    async def execute_block_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ejecutar bloqueo de usuario."""
        query = update.callback_query
        await query.answer()

        try:
            user_id = int(query.data.split("_")[-1])

            result = await self.admin_service.block_user(user_id)

            if result.success:
                message = AdminMessages.BLOCK_USER_SUCCESS.format(
                    user_id=user_id,
                    user_name=context.user_data.get('blocked_user_name', 'Usuario')
                )
                await query.edit_message_text(
                    text=message,
                    reply_markup=AdminKeyboards.users_submenu(),
                    parse_mode="Markdown"
                )
            else:
                message = AdminMessages.USER_ACTION_ERROR.format(
                    operation="Bloquear Usuario",
                    user_id=user_id,
                    message=result.message
                )
                await query.edit_message_text(
                    text=message,
                    reply_markup=AdminKeyboards.users_submenu(),
                    parse_mode="Markdown"
                )

            return ADMIN_USERS_MENU

        except Exception as e:
            logger.error(f"Error bloqueando usuario: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return ADMIN_USERS_MENU

    async def unblock_user_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar confirmación para desbloquear un usuario."""
        query = update.callback_query
        await query.answer()

        try:
            user_id = int(context.user_data.get('selected_user_id', 0))
            user_info = await self.admin_service.get_user_by_id(user_id)

            if not user_info:
                await query.answer("❌ Usuario no encontrado", show_alert=True)
                return ADMIN_USERS_MENU

            message = AdminMessages.UNBLOCK_USER_CONFIRM.format(
                user_id=user_id,
                user_name=user_info['full_name'] or user_info['username'] or 'Usuario'
            )

            keyboard = [
                [
                    InlineKeyboardButton("✅ Desbloquear", callback_data=f"admin_confirm_unblock_{user_id}"),
                    InlineKeyboardButton("❌ Cancelar", callback_data="admin_users_list")
                ]
            ]

            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return ADMIN_BLOCK_USER

        except Exception as e:
            logger.error(f"Error en confirmación de desbloqueo: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return ADMIN_USERS_MENU

    async def execute_unblock_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ejecutar desbloqueo de usuario."""
        query = update.callback_query
        await query.answer()

        try:
            user_id = int(query.data.split("_")[-1])

            result = await self.admin_service.unblock_user(user_id)

            if result.success:
                message = AdminMessages.UNBLOCK_USER_SUCCESS.format(
                    user_id=user_id,
                    user_name=context.user_data.get('unblocked_user_name', 'Usuario')
                )
                await query.edit_message_text(
                    text=message,
                    reply_markup=AdminKeyboards.users_submenu(),
                    parse_mode="Markdown"
                )
            else:
                message = AdminMessages.USER_ACTION_ERROR.format(
                    operation="Desbloquear Usuario",
                    user_id=user_id,
                    message=result.message
                )
                await query.edit_message_text(
                    text=message,
                    reply_markup=AdminKeyboards.users_submenu(),
                    parse_mode="Markdown"
                )

            return ADMIN_USERS_MENU

        except Exception as e:
            logger.error(f"Error desbloqueando usuario: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return ADMIN_USERS_MENU

    async def delete_user_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar confirmación para eliminar un usuario."""
        query = update.callback_query
        await query.answer()

        try:
            user_id = int(context.user_data.get('selected_user_id', 0))
            user_info = await self.admin_service.get_user_by_id(user_id)

            if not user_info:
                await query.answer("❌ Usuario no encontrado", show_alert=True)
                return ADMIN_USERS_MENU

            message = AdminMessages.DELETE_USER_CONFIRM.format(
                user_name=user_info['full_name'] or user_info['username'] or 'Usuario',
                user_id=user_id,
                total_keys=user_info['total_keys'],
                balance_stars=user_info['balance_stars']
            )

            keyboard = [
                [
                    InlineKeyboardButton("✅ ELIMINAR (escribir ID)", callback_data=f"admin_input_delete_{user_id}"),
                    InlineKeyboardButton("❌ Cancelar", callback_data="admin_users_list")
                ]
            ]

            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return ADMIN_DELETE_USER

        except Exception as e:
            logger.error(f"Error en confirmación de eliminación: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return ADMIN_USERS_MENU

    async def assign_role_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar menú para asignar rol."""
        query = update.callback_query
        await query.answer()

        try:
            user_id = int(context.user_data.get('selected_user_id', 0))
            user_info = await self.admin_service.get_user_by_id(user_id)

            if not user_info:
                await query.answer("❌ Usuario no encontrado", show_alert=True)
                return ADMIN_USERS_MENU

            message = AdminMessages.ASSIGN_ROLE_MENU.format(
                user_name=user_info['full_name'] or user_info['username'] or 'Usuario',
                user_id=user_id
            )

            await query.edit_message_text(
                text=message,
                reply_markup=AdminKeyboards.role_selection(),
                parse_mode="Markdown"
            )
            return ADMIN_SELECT_ROLE

        except Exception as e:
            logger.error(f"Error en menú de asignación de rol: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return ADMIN_USERS_MENU

    async def handle_role_assignment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar asignación de rol."""
        query = update.callback_query
        await query.answer()

        try:
            callback_data = query.data
            user_id = int(context.user_data.get('selected_user_id', 0))

            if callback_data == "admin_assign_role_user":
                role = "user"
                duration = None
            elif callback_data == "admin_assign_role_admin":
                role = "admin"
                duration = None
            elif callback_data == "admin_assign_role_task_manager":
                role = "task_manager"
                context.user_data['pending_role'] = role
                # Mostrar selección de duración
                await query.edit_message_text(
                    text="⏱️ **Selecciona la duración para el rol Gestor de Tareas:**",
                    reply_markup=AdminKeyboards.premium_role_duration(),
                    parse_mode="Markdown"
                )
                return ADMIN_ROLE_DURATION
            elif callback_data == "admin_assign_role_announcer":
                role = "announcer"
                context.user_data['pending_role'] = role
                # Mostrar selección de duración
                await query.edit_message_text(
                    text="⏱️ **Selecciona la duración para el rol Anunciante:**",
                    reply_markup=AdminKeyboards.premium_role_duration(),
                    parse_mode="Markdown"
                )
                return ADMIN_ROLE_DURATION
            else:
                return ADMIN_SELECT_ROLE

            # Si no es rol premium, asignar directamente
            result = await self.admin_service.assign_role_to_user(user_id, role)

            if result.success:
                message = AdminMessages.USER_ACTION_SUCCESS.format(
                    operation=f"Asignar Rol: {role.upper()}",
                    user_name=context.user_data.get('user_name', 'Usuario'),
                    user_id=user_id,
                    message=result.message
                )
            else:
                message = AdminMessages.USER_ACTION_ERROR.format(
                    operation="Asignar Rol",
                    user_id=user_id,
                    message=result.message
                )

            await query.edit_message_text(
                text=message,
                reply_markup=AdminKeyboards.users_submenu(),
                parse_mode="Markdown"
            )
            return ADMIN_USERS_MENU

        except Exception as e:
            logger.error(f"Error asignando rol: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return ADMIN_USERS_MENU

    async def handle_role_duration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar selección de duración para roles premium."""
        query = update.callback_query
        await query.answer()

        try:
            callback_data = query.data
            user_id = int(context.user_data.get('selected_user_id', 0))
            role = context.user_data.get('pending_role')

            # Parsear duración
            if callback_data == "admin_role_duration_30":
                duration = 30
            elif callback_data == "admin_role_duration_90":
                duration = 90
            elif callback_data == "admin_role_duration_180":
                duration = 180
            elif callback_data == "admin_role_duration_365":
                duration = 365
            else:
                duration = None

            if duration and role:
                result = await self.admin_service.assign_role_to_user(user_id, role, duration_days=duration)

                if result.success:
                    message = AdminMessages.USER_ACTION_SUCCESS.format(
                        operation=f"Asignar Rol: {role.upper()} ({duration} días)",
                        user_name=context.user_data.get('user_name', 'Usuario'),
                        user_id=user_id,
                        message=result.message
                    )
                else:
                    message = AdminMessages.USER_ACTION_ERROR.format(
                        operation="Asignar Rol",
                        user_id=user_id,
                        message=result.message
                    )

                await query.edit_message_text(
                    text=message,
                    reply_markup=AdminKeyboards.users_submenu(),
                    parse_mode="Markdown"
                )

            return ADMIN_USERS_MENU

        except Exception as e:
            logger.error(f"Error manejando duración de rol: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return ADMIN_USERS_MENU

    @staticmethod
    def _format_status(status: str) -> str:
        """Formatear estado para mostrar."""
        status_map = {
            'active': '🟢 Activo',
            'suspended': '🟡 Suspendido',
            'blocked': '🔴 Bloqueado',
            'free_trial': '📋 Prueba Gratis'
        }
        return status_map.get(status, '❓ Desconocido')
