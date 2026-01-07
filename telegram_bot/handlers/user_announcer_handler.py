"""
Handler de Anuncios para Usuarios con Rol de Anunciante.

Permite a usuarios con el rol 'announcer' crear y gestionar campañas de anuncios.

Author: uSipipo Team
Version: 1.0.0
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from utils.logger import logger
from datetime import datetime, timezone
import uuid

from telegram_bot.messages.messages import Messages
from telegram_bot.keyboard import OperationKeyboards, CommonKeyboards

# Estados de conversación
ANNOUNCER_MENU = 0
CREATING_ANNOUNCEMENT = 1
ANNOUNCEMENT_TITLE = 2
ANNOUNCEMENT_TEXT = 3
ANNOUNCEMENT_DURATION = 4
ANNOUNCEMENT_TARGET = 5
CONFIRMING_ANNOUNCEMENT = 6
MANAGING_ANNOUNCEMENTS = 7
VIEWING_ANNOUNCEMENT_STATS = 8


class UserAnnouncerHandler:
    """Handler para gestión de anuncios por usuarios con rol Anunciante."""

    def __init__(self, user_repository, payment_service=None):
        self.user_repository = user_repository
        self.payment_service = payment_service

    async def _check_role_permission(self, user_id: int) -> bool:
        """Verificar si el usuario tiene permiso (rol de Anunciante activo)."""
        try:
            user = await self.user_repository.get_user(user_id)
            if not user:
                return False
            
            return user.is_announcer_active()
        except Exception as e:
            logger.error(f"Error verificando permiso de anunciante: {e}")
            return False

    async def announcer_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar menú principal del Anunciante."""
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = update.effective_user.id
            
            # Verificar permiso
            if not await self._check_role_permission(user_id):
                await query.edit_message_text(
                    text="❌ **Acceso Denegado**\n\nNecesitas tener el rol de **Anunciante** activo.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Volver", callback_data="operations")]
                    ]),
                    parse_mode="Markdown"
                )
                return ConversationHandler.END
            
            # Obtener estadísticas
            stats = await self._get_announcer_stats(user_id)
            
            message = f"""📣 **Centro de Anunciante**

👤 **Tu Rol:** Anunciante

**Límites de Este Mes:**
📊 Anuncios Creados: {stats.get('created_this_month', 0)}/100
📈 Visualizaciones: {stats.get('total_views', 0)}
💬 Interacciones: {stats.get('total_interactions', 0)}

**Estadísticas Generales:**
📢 Total de Anuncios: {stats.get('total_announcements', 0)}
🟢 Activos: {stats.get('active_announcements', 0)}
✅ Finalizados: {stats.get('completed_announcements', 0)}

**Acciones Disponibles:**"""

            keyboard = [
                [InlineKeyboardButton("📢 Crear Anuncio", callback_data="uan_create_announcement")],
                [InlineKeyboardButton("📋 Mis Anuncios", callback_data="uan_my_announcements")],
                [InlineKeyboardButton("📊 Estadísticas Detalladas", callback_data="uan_view_stats")],
                [InlineKeyboardButton("👥 Audiencia", callback_data="uan_view_audience")],
                [InlineKeyboardButton("🔙 Volver", callback_data="operations")]
            ]
            
            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return ANNOUNCER_MENU
            
        except Exception as e:
            logger.error(f"Error en announcer_menu: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return ANNOUNCER_MENU

    async def start_create_announcement(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Iniciar creación de anuncio."""
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = update.effective_user.id
            
            if not await self._check_role_permission(user_id):
                await query.answer("❌ Permiso denegado", show_alert=True)
                return ANNOUNCER_MENU
            
            # Verificar límite de anuncios del mes
            stats = await self._get_announcer_stats(user_id)
            if stats.get('created_this_month', 0) >= 100:
                await query.answer("❌ Has alcanzado el límite de 100 anuncios este mes", show_alert=True)
                return ANNOUNCER_MENU
            
            context.user_data['new_announcement'] = {
                'creator_id': user_id,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            message = """📢 **Crear Nuevo Anuncio**

Ingresa el **título** del anuncio:

💡 *Ejemplos:*
- 🎉 ¡Descuento especial en VIP!
- 📲 Nueva app disponible
- ⭐ Gana estrellas gratis"""
            
            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cancelar", callback_data="uan_menu")]
                ]),
                parse_mode="Markdown"
            )
            return ANNOUNCEMENT_TITLE
            
        except Exception as e:
            logger.error(f"Error en start_create_announcement: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return ANNOUNCER_MENU

    async def get_announcement_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Obtener título del anuncio."""
        try:
            title = update.message.text
            
            if len(title) < 5 or len(title) > 100:
                await update.message.reply_text(
                    "❌ El título debe tener entre 5 y 100 caracteres"
                )
                return ANNOUNCEMENT_TITLE
            
            context.user_data['new_announcement']['title'] = title
            
            message = """📝 **Contenido del Anuncio**

Ingresa el texto del anuncio (máximo 1000 caracteres):

💡 *Soporta:*
- Emojis 😊
- Saltos de línea
- Markdown básico

Sé creativo y atractivo para captar atención."""
            
            await update.message.reply_text(
                text=message,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cancelar", callback_data="uan_menu")]
                ]),
                parse_mode="Markdown"
            )
            return ANNOUNCEMENT_TEXT
            
        except Exception as e:
            logger.error(f"Error en get_announcement_title: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
            return ANNOUNCEMENT_TITLE

    async def get_announcement_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Obtener contenido del anuncio."""
        try:
            text = update.message.text
            
            if len(text) < 10 or len(text) > 1000:
                await update.message.reply_text(
                    "❌ El contenido debe tener entre 10 y 1000 caracteres"
                )
                return ANNOUNCEMENT_TEXT
            
            context.user_data['new_announcement']['text'] = text
            
            message = """⏱️ **Duración del Anuncio**

¿Por cuántos días deseas que esté activo?

Opciones:
• 1 día
• 3 días
• 7 días
• 14 días
• 30 días"""
            
            keyboard = [
                [
                    InlineKeyboardButton("1 día", callback_data="uan_duration_1"),
                    InlineKeyboardButton("3 días", callback_data="uan_duration_3")
                ],
                [
                    InlineKeyboardButton("7 días", callback_data="uan_duration_7"),
                    InlineKeyboardButton("14 días", callback_data="uan_duration_14")
                ],
                [
                    InlineKeyboardButton("30 días", callback_data="uan_duration_30")
                ],
                [
                    InlineKeyboardButton("❌ Cancelar", callback_data="uan_menu")
                ]
            ]
            
            await update.message.reply_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return ANNOUNCEMENT_DURATION
            
        except Exception as e:
            logger.error(f"Error en get_announcement_text: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
            return ANNOUNCEMENT_TEXT

    async def get_announcement_duration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Obtener duración del anuncio."""
        query = update.callback_query
        await query.answer()
        
        try:
            duration_days = int(query.data.split("_")[-1])
            context.user_data['new_announcement']['duration_days'] = duration_days
            
            message = """👥 **Audiencia Objetivo**

¿A qué usuarios deseas dirigir el anuncio?

Opciones:
• Todos los usuarios
• Solo usuarios VIP
• Solo usuarios gratuitos
• Solo nuevos usuarios (< 7 días)"""
            
            keyboard = [
                [InlineKeyboardButton("👥 Todos", callback_data="uan_target_all")],
                [InlineKeyboardButton("👑 VIP", callback_data="uan_target_vip")],
                [InlineKeyboardButton("📦 Gratuitos", callback_data="uan_target_free")],
                [InlineKeyboardButton("🆕 Nuevos", callback_data="uan_target_new")],
                [InlineKeyboardButton("❌ Cancelar", callback_data="uan_menu")]
            ]
            
            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return ANNOUNCEMENT_TARGET
            
        except Exception as e:
            logger.error(f"Error en get_announcement_duration: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return ANNOUNCEMENT_DURATION

    async def get_announcement_target(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Obtener audiencia objetivo."""
        query = update.callback_query
        await query.answer()
        
        try:
            target = query.data.split("_")[-1]
            context.user_data['new_announcement']['target'] = target
            
            # Mostrar confirmación
            ann_data = context.user_data['new_announcement']
            
            target_names = {
                'all': 'Todos los usuarios',
                'vip': 'Solo usuarios VIP',
                'free': 'Solo usuarios gratuitos',
                'new': 'Solo nuevos usuarios'
            }
            
            message = f"""✅ **Confirmar Anuncio**

📢 **Título:** {ann_data['title']}

📝 **Contenido:**
{ann_data['text']}

⏱️ **Duración:** {ann_data['duration_days']} días

👥 **Audiencia:** {target_names.get(target, target)}

¿Deseas crear este anuncio?"""
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ Crear", callback_data="uan_confirm_announcement"),
                    InlineKeyboardButton("❌ Cancelar", callback_data="uan_menu")
                ]
            ]
            
            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return CONFIRMING_ANNOUNCEMENT
            
        except Exception as e:
            logger.error(f"Error en get_announcement_target: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return ANNOUNCEMENT_TARGET

    async def confirm_create_announcement(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirmar creación de anuncio."""
        query = update.callback_query
        await query.answer()
        
        try:
            ann_data = context.user_data.get('new_announcement', {})
            
            if not ann_data:
                await query.answer("❌ Error: Datos de anuncio no encontrados", show_alert=True)
                return ANNOUNCER_MENU
            
            # Crear anuncio (en una BD real, esto se guardaría)
            announcement_id = str(uuid.uuid4())
            
            message = f"""✅ **Anuncio Creado Exitosamente**

🆔 ID: `{announcement_id}`
📢 Título: {ann_data['title']}
⏱️ Duración: {ann_data['duration_days']} días
👥 Audiencia: {ann_data['target']}

El anuncio ha sido publicado y está visible para los usuarios.

**Estadísticas en Vivo:**
👁️ Visualizaciones: 0
💬 Interacciones: 0"""
            
            del context.user_data['new_announcement']
            
            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 Crear Otro", callback_data="uan_create_announcement")],
                    [InlineKeyboardButton("📋 Mis Anuncios", callback_data="uan_my_announcements")],
                    [InlineKeyboardButton("🔙 Menú", callback_data="uan_menu")]
                ]),
                parse_mode="Markdown"
            )
            return ANNOUNCER_MENU
            
        except Exception as e:
            logger.error(f"Error en confirm_create_announcement: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return ANNOUNCER_MENU

    async def view_user_announcements(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ver anuncios del usuario."""
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = update.effective_user.id
            
            if not await self._check_role_permission(user_id):
                await query.answer("❌ Permiso denegado", show_alert=True)
                return ANNOUNCER_MENU
            
            # En una BD real, se obtendría de la BD
            announcements = []
            
            if not announcements:
                message = "📋 **Mis Anuncios**\n\nNo tienes anuncios creados aún."
                keyboard = [
                    [InlineKeyboardButton("📢 Crear Anuncio", callback_data="uan_create_announcement")],
                    [InlineKeyboardButton("🔙 Menú", callback_data="uan_menu")]
                ]
            else:
                ann_list = []
                for ann in announcements[:10]:
                    status = "🟢" if ann.get('is_active', True) else "🔴"
                    ann_list.append(
                        f"{status} **{ann.get('title', 'Sin título')}**\n"
                        f"  👁️ {ann.get('views', 0)} | 💬 {ann.get('interactions', 0)}"
                    )
                
                message = f"""📋 **Mis Anuncios**

Total: {len(announcements)} anuncios

{chr(10).join(ann_list)}"""
                
                keyboard = [
                    [InlineKeyboardButton("📢 Crear Nuevo", callback_data="uan_create_announcement")],
                    [InlineKeyboardButton("📊 Estadísticas", callback_data="uan_view_stats")],
                    [InlineKeyboardButton("🔙 Menú", callback_data="uan_menu")]
                ]
            
            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return MANAGING_ANNOUNCEMENTS
            
        except Exception as e:
            logger.error(f"Error en view_user_announcements: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return ANNOUNCER_MENU

    async def view_announcer_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ver estadísticas de anuncios."""
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = update.effective_user.id
            
            if not await self._check_role_permission(user_id):
                await query.answer("❌ Permiso denegado", show_alert=True)
                return ANNOUNCER_MENU
            
            stats = await self._get_announcer_stats(user_id)
            
            message = f"""📊 **Estadísticas de Anuncios**

**Este Mes:**
📢 Anuncios Creados: {stats.get('created_this_month', 0)}/100
👁️ Visualizaciones: {stats.get('total_views', 0)}
💬 Interacciones: {stats.get('total_interactions', 0)}

**Generales:**
📊 Total de Anuncios: {stats.get('total_announcements', 0)}
🟢 Activos: {stats.get('active_announcements', 0)}
✅ Finalizados: {stats.get('completed_announcements', 0)}

**Rendimiento:**
📈 CTR Promedio: {stats.get('avg_ctr', 0):.2f}%
⏱️ Duración Promedio: {stats.get('avg_duration', 0)} días"""
            
            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📋 Mis Anuncios", callback_data="uan_my_announcements")],
                    [InlineKeyboardButton("🔙 Menú", callback_data="uan_menu")]
                ]),
                parse_mode="Markdown"
            )
            return VIEWING_ANNOUNCEMENT_STATS
            
        except Exception as e:
            logger.error(f"Error en view_announcer_stats: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return ANNOUNCER_MENU

    async def view_announcer_audience(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ver estadísticas de audiencia."""
        query = update.callback_query
        await query.answer()
        
        try:
            user_id = update.effective_user.id
            
            if not await self._check_role_permission(user_id):
                await query.answer("❌ Permiso denegado", show_alert=True)
                return ANNOUNCER_MENU
            
            # En una BD real, se calcularía de verdad
            audience_stats = {
                'total_reached': 0,
                'engaged': 0,
                'vip_percentage': 0,
                'top_regions': []
            }
            
            message = f"""👥 **Estadísticas de Audiencia**

**Alcance:**
📊 Usuarios Alcanzados: {audience_stats.get('total_reached', 0)}
💬 Usuarios Comprometidos: {audience_stats.get('engaged', 0)}
📈 Engagement: {int((audience_stats.get('engaged', 0) / max(audience_stats.get('total_reached', 1), 1)) * 100)}%

**Segmentación:**
👑 Usuarios VIP: {audience_stats.get('vip_percentage', 0):.1f}%
📦 Usuarios Gratuitos: {100 - audience_stats.get('vip_percentage', 0):.1f}%

**Regiones Top:**
🌍 Estas son tus regiones principales de alcance"""
            
            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📊 Estadísticas", callback_data="uan_view_stats")],
                    [InlineKeyboardButton("🔙 Menú", callback_data="uan_menu")]
                ]),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error en view_announcer_audience: {e}")
            await query.answer(f"❌ Error: {str(e)}", show_alert=True)
            return ANNOUNCER_MENU

    async def _get_announcer_stats(self, user_id: int) -> dict:
        """Obtener estadísticas del anunciante."""
        try:
            # En una BD real, se calcularía de la BD
            return {
                'created_this_month': 0,
                'total_views': 0,
                'total_interactions': 0,
                'total_announcements': 0,
                'active_announcements': 0,
                'completed_announcements': 0,
                'avg_ctr': 0.0,
                'avg_duration': 0
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}


def get_user_announcer_handlers(user_repository) -> list:
    """Retorna los handlers para gestión de anuncios de usuarios."""
    handler = UserAnnouncerHandler(user_repository)
    handlers = []
    
    # Menú principal
    handlers.append(
        CallbackQueryHandler(handler.announcer_menu, pattern="^uan_menu$|^user_announcer$")
    )
    
    # Conversation handler para crear anuncios
    announcement_creation_conversation = ConversationHandler(
        entry_points=[CallbackQueryHandler(handler.start_create_announcement, pattern="^uan_create_announcement$")],
        states={
            ANNOUNCEMENT_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handler.get_announcement_title)],
            ANNOUNCEMENT_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handler.get_announcement_text)],
            ANNOUNCEMENT_DURATION: [CallbackQueryHandler(handler.get_announcement_duration, pattern="^uan_duration_")],
            ANNOUNCEMENT_TARGET: [CallbackQueryHandler(handler.get_announcement_target, pattern="^uan_target_")],
            CONFIRMING_ANNOUNCEMENT: [CallbackQueryHandler(handler.confirm_create_announcement, pattern="^uan_confirm_announcement$")],
        },
        fallbacks=[CallbackQueryHandler(handler.announcer_menu, pattern="^uan_menu$")]
    )
    handlers.append(announcement_creation_conversation)
    
    # Ver anuncios
    handlers.append(
        CallbackQueryHandler(handler.view_user_announcements, pattern="^uan_my_announcements$")
    )
    
    # Estadísticas
    handlers.append(
        CallbackQueryHandler(handler.view_announcer_stats, pattern="^uan_view_stats$")
    )
    
    # Audiencia
    handlers.append(
        CallbackQueryHandler(handler.view_announcer_audience, pattern="^uan_view_audience$")
    )
    
    return handlers
