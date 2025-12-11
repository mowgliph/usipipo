'use strict';

/**
 * ============================================================================
 * 🎮 AUTH HANDLER - uSipipo VPN Bot
 * ============================================================================
 * Controladores para el módulo de autenticación.
 * Maneja comandos, callbacks y flujos de autorización.
 * ============================================================================
 */

const authService = require('./auth.service');
const authMessages = require('./auth.messages');
const authKeyboards = require('./auth.keyboard');
const notificationService = require('../../../shared/services/notification.service');
const logger = require('../../../core/utils/logger');
const constants = require('../../../config/constants');

class AuthHandler {
  constructor(bot) {
    this.bot = bot;
    this.notificationService = notificationService;
  }

  // ============================================================================
  // 📝 REGISTRO DE COMANDOS Y CALLBACKS
  // ============================================================================

  registerHandlers() {
    // Comandos de administración
    this.bot.command('add', (ctx) => this.handleAddUser(ctx));
    this.bot.command('listusers', (ctx) => this.handleListUsers(ctx));
    this.bot.command('userinfo', (ctx) => this.handleUserInfo(ctx));
    this.bot.command('suspend', (ctx) => this.handleSuspendUser(ctx));
    this.bot.command('reactivate', (ctx) => this.handleReactivateUser(ctx));
    this.bot.command('changerole', (ctx) => this.handleChangeRole(ctx));
    this.bot.command('authstats', (ctx) => this.handleAuthStats(ctx));

    // Comandos de usuario
    this.bot.command('checkstatus', (ctx) => this.handleCheckStatus(ctx));

    // Callbacks
    this.bot.action(/^auth_approve_(.+)$/, (ctx) => this.handleApproveCallback(ctx));
    this.bot.action(/^auth_reject_(.+)$/, (ctx) => this.handleRejectCallback(ctx));
    this.bot.action(/^auth_info_(.+)$/, (ctx) => this.handleInfoCallback(ctx));
    this.bot.action(/^auth_role_(user|admin)_(.+)$/, (ctx) => this.handleRoleSelectionCallback(ctx));
    this.bot.action(/^auth_page_(\d+)$/, (ctx) => this.handlePageCallback(ctx));
    this.bot.action('auth_refresh_list', (ctx) => this.handleRefreshListCallback(ctx));
    this.bot.action('auth_stats', (ctx) => this.handleAuthStats(ctx));
    this.bot.action('auth_check_status', (ctx) => this.handleCheckStatus(ctx));
    this.bot.action('auth_help', (ctx) => this.handleAuthHelp(ctx));

    logger.success('[AuthHandler] Handlers registrados correctamente');
  }

  // ============================================================================
  // 👤 SOLICITUD DE ACCESO (FLUJO AUTOMÁTICO)
  // ============================================================================

  /**
   * Maneja solicitud de acceso de usuario no autorizado
   * Se llama automáticamente desde el middleware de auth
   */
  async handleAccessRequest(ctx) {
    try {
      const user = ctx.from;
      const userId = user.id;

      // Verificar si ya está autorizado
      if (authService.isUserAuthorized(userId)) {
        const role = authService.isUserAdmin(userId) ? 'admin' : 'user';
        await ctx.reply(
          authMessages.getAuthorizedWelcomeMessage(user, role),
          { parse_mode: 'Markdown' }
        );
        return;
      }

      // Enviar mensaje al usuario
      await ctx.reply(
        authMessages.getUnauthorizedWelcomeMessage(user),
        {
          parse_mode: 'Markdown',
          ...authKeyboards.getUnauthorizedHelpKeyboard()
        }
      );

      // Notificar al administrador
      await this.notificationService.bot.telegram.sendMessage(
        authService.getUserAuthInfo(userId).isAdmin ? userId : require('../../../config/environment').ADMIN_ID,
        authMessages.getAccessRequestNotification(user),
        {
          parse_mode: 'Markdown',
          ...authKeyboards.getQuickAuthActionsKeyboard(userId)
        }
      );

      logger.info('[AuthHandler] Solicitud de acceso procesada', {
        userId,
        userName: user.first_name
      });

    } catch (error) {
      logger.error('[AuthHandler] Error en solicitud de acceso', error);
      await ctx.reply(
        `${constants.EMOJI.ERROR} Error al procesar tu solicitud. Por favor, intenta más tarde.`,
        { parse_mode: 'Markdown' }
      );
    }
  }

  // ============================================================================
  // ➕ AUTORIZAR USUARIO (COMANDO ADMIN)
  // ============================================================================

  async handleAddUser(ctx) {
    try {
      const adminId = ctx.from.id;

      // Verificar permisos
      if (!authService.isUserAdmin(adminId)) {
        await ctx.reply(
          authMessages.getAuthorizationErrorMessage({ message: 'No tienes permisos de administrador' }),
          { parse_mode: 'Markdown' }
        );
        return;
      }

      // Extraer ID del usuario a autorizar
      const args = ctx.message.text.split(' ').slice(1);
      if (args.length === 0) {
        await ctx.reply(
          `${constants.EMOJI.INFO} *Uso del comando:*\n\n` +
          `\`/add <user_id> [nombre_opcional]\`\n\n` +
          `*Ejemplo:*\n` +
          `\`/add 123456789 Juan Pérez\``,
          { parse_mode: 'Markdown' }
        );
        return;
      }

      const targetUserId = args[0];
      const userName = args.slice(1).join(' ') || null;

      // Verificar si ya está autorizado
      if (authService.isUserAuthorized(targetUserId)) {
        await ctx.reply(
          authMessages.getAlreadyAuthorizedMessage(targetUserId),
          { parse_mode: 'Markdown' }
        );
        return;
      }

      // Autorizar usuario
      const result = await authService.authorizeUser(targetUserId, adminId, { name: userName });

      // Confirmar al admin
      await ctx.reply(
        authMessages.getUserAuthorizedMessage({ id: targetUserId, first_name: userName }, ctx.from),
        {
          parse_mode: 'Markdown',
          ...authKeyboards.getPostAuthActionsKeyboard(targetUserId)
        }
      );

      // Notificar al usuario autorizado
      await this.notificationService.sendDirectMessage(
        targetUserId,
        authMessages.getUserWasAuthorizedNotification()
      );

      logger.success('[AuthHandler] Usuario autorizado por comando', {
        targetUserId,
        adminId,
        userName
      });

    } catch (error) {
      logger.error('[AuthHandler] Error al autorizar usuario', error);
      await ctx.reply(
        authMessages.getAuthorizationErrorMessage(error),
        { parse_mode: 'Markdown' }
      );
    }
  }

  // ============================================================================
  // 📋 LISTAR USUARIOS AUTORIZADOS
  // ============================================================================

  async handleListUsers(ctx) {
    try {
      const userId = ctx.from.id;

      // Verificar permisos
      if (!authService.isUserAdmin(userId)) {
        await ctx.reply(
          `${constants.EMOJI.ERROR} Solo administradores pueden ver la lista de usuarios.`,
          { parse_mode: 'Markdown' }
        );
        return;
      }

      const page = 1;
      const result = authService.getAuthorizedUsersPaginated(page, 10);

      await ctx.reply(
        authMessages.getAuthorizedUsersListMessage(result.users),
        {
          parse_mode: 'Markdown',
          ...authKeyboards.getPaginatedUsersKeyboard(
            result.pagination.currentPage,
            result.pagination.totalPages
          )
        }
      );

      logger.info('[AuthHandler] Lista de usuarios solicitada', { userId, page });

    } catch (error) {
      logger.error('[AuthHandler] Error al listar usuarios', error);
      await ctx.reply(
        `${constants.EMOJI.ERROR} Error al cargar la lista de usuarios.`,
        { parse_mode: 'Markdown' }
      );
    }
  }

  // ============================================================================
  // ℹ️ INFORMACIÓN DE USUARIO
  // ============================================================================

  async handleUserInfo(ctx) {
    try {
      const adminId = ctx.from.id;

      if (!authService.isUserAdmin(adminId)) {
        await ctx.reply(
          `${constants.EMOJI.ERROR} Solo administradores pueden ver información de usuarios.`,
          { parse_mode: 'Markdown' }
        );
        return;
      }

      const args = ctx.message.text.split(' ').slice(1);
      if (args.length === 0) {
        await ctx.reply(
          `${constants.EMOJI.INFO} *Uso del comando:*\n\n` +
          `\`/userinfo <user_id>\`\n\n` +
          `*Ejemplo:*\n` +
          `\`/userinfo 123456789\``,
          { parse_mode: 'Markdown' }
        );
        return;
      }

      const targetUserId = args[0];
      const user = authService.getUserCompleteInfo(targetUserId);

      if (!user) {
        await ctx.reply(
          `${constants.EMOJI.WARNING} Usuario no encontrado: \`${targetUserId}\``,
          { parse_mode: 'Markdown' }
        );
        return;
      }

      await ctx.reply(
        authMessages.getUserDetailedInfoMessage(user),
        {
          parse_mode: 'Markdown',
          ...authKeyboards.getUserManagementKeyboard(targetUserId)
        }
      );

      logger.info('[AuthHandler] Información de usuario solicitada', {
        adminId,
        targetUserId
      });

    } catch (error) {
      logger.error('[AuthHandler] Error al obtener información de usuario', error);
      await ctx.reply(
        `${constants.EMOJI.ERROR} Error al cargar información del usuario.`,
        { parse_mode: 'Markdown' }
      );
    }
  }

  // ============================================================================
  // 🔒 SUSPENDER USUARIO
  // ============================================================================

  async handleSuspendUser(ctx) {
    try {
      const adminId = ctx.from.id;

      if (!authService.isUserAdmin(adminId)) {
        await ctx.reply(
          `${constants.EMOJI.ERROR} Solo administradores pueden suspender usuarios.`,
          { parse_mode: 'Markdown' }
        );
        return;
      }

      const args = ctx.message.text.split(' ').slice(1);
      if (args.length === 0) {
        await ctx.reply(
          `${constants.EMOJI.INFO} *Uso del comando:*\n\n` +
          `\`/suspend <user_id> [razón]\`\n\n` +
          `*Ejemplo:*\n` +
          `\`/suspend 123456789 Violación de términos\``,
          { parse_mode: 'Markdown' }
        );
        return;
      }

      const targetUserId = args[0];
      const reason = args.slice(1).join(' ') || 'Sin razón especificada';

      const result = await authService.suspendUser(targetUserId, adminId, reason);

      await ctx.reply(
        `${constants.EMOJI.SUCCESS} *Usuario Suspendido*\n\n` +
        `Usuario \`${targetUserId}\` ha sido suspendido.\n\n` +
        `*Razón:* ${reason}\n` +
        `*Por:* ${ctx.from.first_name}`,
        { parse_mode: 'Markdown' }
      );

      // Notificar al usuario suspendido
      await this.notificationService.sendDirectMessage(
        targetUserId,
        `${constants.EMOJI.WARNING} *Cuenta Suspendida*\n\n` +
        `Tu cuenta ha sido suspendida.\n\n` +
        `*Razón:* ${reason}\n\n` +
        `Para más información, contacta al administrador.`
      );

      logger.warn('[AuthHandler] Usuario suspendido', {
        targetUserId,
        adminId,
        reason
      });

    } catch (error) {
      logger.error('[AuthHandler] Error al suspender usuario', error);
      await ctx.reply(
        `${constants.EMOJI.ERROR} Error: ${error.message}`,
        { parse_mode: 'Markdown' }
      );
    }
  }

  // ============================================================================
  // 🔓 REACTIVAR USUARIO
  // ============================================================================

  async handleReactivateUser(ctx) {
    try {
      const adminId = ctx.from.id;

      if (!authService.isUserAdmin(adminId)) {
        await ctx.reply(
          `${constants.EMOJI.ERROR} Solo administradores pueden reactivar usuarios.`,
          { parse_mode: 'Markdown' }
        );
        return;
      }

      const args = ctx.message.text.split(' ').slice(1);
      if (args.length === 0) {
        await ctx.reply(
          `${constants.EMOJI.INFO} *Uso del comando:*\n\n` +
          `\`/reactivate <user_id>\``,
          { parse_mode: 'Markdown' }
        );
        return;
      }

      const targetUserId = args[0];
      const result = await authService.reactivateUser(targetUserId, adminId);

      await ctx.reply(
        `${constants.EMOJI.SUCCESS} *Usuario Reactivado*\n\n` +
        `Usuario \`${targetUserId}\` ha sido reactivado exitosamente.`,
        { parse_mode: 'Markdown' }
      );

      // Notificar al usuario
      await this.notificationService.sendDirectMessage(
        targetUserId,
        `${constants.EMOJI.SUCCESS} *Cuenta Reactivada*\n\n` +
        `Tu cuenta ha sido reactivada.\n\n` +
        `Ya puedes volver a usar todos los servicios VPN.`
      );

      logger.success('[AuthHandler] Usuario reactivado', {
        targetUserId,
        adminId
      });

    } catch (error) {
      logger.error('[AuthHandler] Error al reactivar usuario', error);
      await ctx.reply(
        `${constants.EMOJI.ERROR} Error: ${error.message}`,
        { parse_mode: 'Markdown' }
      );
    }
  }

  // ============================================================================
  // 👑 CAMBIAR ROL DE USUARIO
  // ============================================================================

  async handleChangeRole(ctx) {
    try {
      const adminId = ctx.from.id;

      if (!authService.isUserAdmin(adminId)) {
        await ctx.reply(
          `${constants.EMOJI.ERROR} Solo administradores pueden cambiar roles.`,
          { parse_mode: 'Markdown' }
        );
        return;
      }

      const args = ctx.message.text.split(' ').slice(1);
      if (args.length < 2) {
        await ctx.reply(
          `${constants.EMOJI.INFO} *Uso del comando:*\n\n` +
          `\`/changerole <user_id> <rol>\`\n\n` +
          `*Roles válidos:* \`user\`, \`admin\`\n\n` +
          `*Ejemplo:*\n` +
          `\`/changerole 123456789 admin\``,
          { parse_mode: 'Markdown' }
        );
        return;
      }

      const targetUserId = args[0];
      const newRole = args[1].toLowerCase();

      const result = await authService.changeUserRole(targetUserId, newRole, adminId);

      await ctx.reply(
        `${constants.EMOJI.SUCCESS} *Rol Actualizado*\n\n` +
        `Usuario \`${targetUserId}\` ahora es: *${newRole}*`,
        { parse_mode: 'Markdown' }
      );

      logger.success('[AuthHandler] Rol de usuario cambiado', {
        targetUserId,
        newRole,
        adminId
      });

    } catch (error) {
      logger.error('[AuthHandler] Error al cambiar rol', error);
      await ctx.reply(
        `${constants.EMOJI.ERROR} Error: ${error.message}`,
        { parse_mode: 'Markdown' }
      );
    }
  }

  // ============================================================================
  // 📊 ESTADÍSTICAS DE AUTORIZACIÓN
  // ============================================================================

  async handleAuthStats(ctx) {
    try {
      const userId = ctx.from.id;

      if (!authService.isUserAdmin(userId)) {
        await ctx.reply(
          `${constants.EMOJI.ERROR} Solo administradores pueden ver estadísticas.`,
          { parse_mode: 'Markdown' }
        );
        return;
      }

      const stats = authService.getAuthStatistics();

      const message = 
        `${constants.EMOJI.INFO} *Estadísticas de Autorización*\n\n` +
        `👥 *Total de Usuarios:* ${stats.total}\n` +
        `✅ *Activos:* ${stats.active}\n` +
        `⏸ *Suspendidos:* ${stats.suspended}\n\n` +
        `👑 *Administradores:* ${stats.admins}\n` +
        `👤 *Usuarios:* ${stats.users}\n\n` +
        `🔐 *Con VPN Configurada:* ${stats.withVPN}\n` +
        `  • WireGuard: ${stats.withWireGuard}\n` +
        `  • Outline: ${stats.withOutline}\n` +
        `  • Ambos: ${stats.withBothVPN}`;

      await ctx.reply(message, {
        parse_mode: 'Markdown',
        ...authKeyboards.getAuthorizedUsersListKeyboard()
      });

      logger.info('[AuthHandler] Estadísticas solicitadas', { userId });

    } catch (error) {
      logger.error('[AuthHandler] Error al obtener estadísticas', error);
      await ctx.reply(
        `${constants.EMOJI.ERROR} Error al cargar estadísticas.`,
        { parse_mode: 'Markdown' }
      );
    }
  }

  // ============================================================================
  // 🔍 VERIFICAR ESTADO (USUARIO)
  // ============================================================================

  async handleCheckStatus(ctx) {
    try {
      const userId = ctx.from.id;
      const status = authService.checkAccessRequestStatus(userId);

      let message = `${constants.EMOJI.INFO} *Estado de tu Solicitud*\n\n`;

      switch (status.status) {
        case 'approved':
          message += `${constants.EMOJI.SUCCESS} *Estado:* Aprobado\n\n`;
          message += `Ya tienes acceso completo al bot.\n`;
          message += `Usa /menu para ver las opciones disponibles.`;
          break;

        case 'suspended':
          message += `${constants.EMOJI.WARNING} *Estado:* Suspendido\n\n`;
          message += `*Razón:* ${status.reason || 'No especificada'}\n\n`;
          message += `Contacta al administrador para más información.`;
          break;

        case 'pending':
          message += `${constants.EMOJI.LOADING} *Estado:* Pendiente\n\n`;
          message += `Tu solicitud está siendo revisada.\n`;
          message += `Recibirás una notificación cuando sea aprobada.`;
          break;

        default:
          message += `${constants.EMOJI.WARNING} *Estado:* No registrado\n\n`;
          message += `Usa /start para solicitar acceso.`;
      }

      await ctx.reply(message, { parse_mode: 'Markdown' });

    } catch (error) {
      logger.error('[AuthHandler] Error al verificar estado', error);
      await ctx.reply(
        `${constants.EMOJI.ERROR} Error al verificar tu estado.`,
        { parse_mode: 'Markdown' }
      );
    }
  }

  // ============================================================================
  // ℹ️ AYUDA DE AUTORIZACIÓN
  // ============================================================================

  async handleAuthHelp(ctx) {
    try {
      const message =
        `${constants.EMOJI.INFO} *Sistema de Autorización*\n\n` +
        `*¿Cómo funciona?*\n\n` +
        `1. Al usar /start, tu solicitud se envía automáticamente\n` +
        `2. El administrador revisa tu solicitud\n` +
        `3. Recibes notificación cuando seas aprobado\n` +
        `4. Una vez aprobado, tendrás acceso completo\n\n` +
        `*Comandos útiles:*\n` +
        `• /checkstatus - Ver estado de tu solicitud\n` +
        `• /help - Ayuda general del bot\n\n` +
        `*¿Necesitas ayuda?*\n` +
        `Contacta al administrador si tienes dudas.`;

      await ctx.reply(message, {
        parse_mode: 'Markdown',
        ...authKeyboards.getUnauthorizedHelpKeyboard()
      });

    } catch (error) {
      logger.error('[AuthHandler] Error en ayuda de auth', error);
    }
  }

  // ============================================================================
  // 🔘 CALLBACKS
  // ============================================================================

  async handleApproveCallback(ctx) {
    try {
      await ctx.answerCbQuery();
      const userId = ctx.match[1];
      const adminId = ctx.from.id;

      if (!authService.isUserAdmin(adminId)) {
        await ctx.answerCbQuery('No tienes permisos de administrador');
        return;
      }

      // Mostrar selector de rol
      await ctx.editMessageReplyMarkup(
        authKeyboards.getRoleSelectionKeyboard(userId).reply_markup
      );

    } catch (error) {
      logger.error('[AuthHandler] Error en callback approve', error);
      await ctx.answerCbQuery('Error al procesar acción');
    }
  }

  async handleRoleSelectionCallback(ctx) {
    try {
      await ctx.answerCbQuery();
      const role = ctx.match[1];
      const userId = ctx.match[2];
      const adminId = ctx.from.id;

      const result = await authService.authorizeUser(userId, adminId, {});
      await authService.changeUserRole(userId, role, adminId);

      await ctx.editMessageText(
        authMessages.getUserAuthorizedMessage({ id: userId }, ctx.from),
        {
          parse_mode: 'Markdown',
          ...authKeyboards.getPostAuthActionsKeyboard(userId)
        }
      );

      // Notificar al usuario
      await this.notificationService.sendDirectMessage(
        userId,
        authMessages.getUserWasAuthorizedNotification()
      );

    } catch (error) {
      logger.error('[AuthHandler] Error en callback role', error);
      await ctx.answerCbQuery('Error al autorizar usuario');
    }
  }

  async handleRejectCallback(ctx) {
    try {
      await ctx.answerCbQuery('Solicitud rechazada');
      const userId = ctx.match[1];

      await ctx.editMessageText(
        `${constants.EMOJI.ERROR} Solicitud rechazada para usuario \`${userId}\``,
        { parse_mode: 'Markdown' }
      );

      // Notificar al usuario
      await this.notificationService.sendDirectMessage(
        userId,
        `${constants.EMOJI.ERROR} *Solicitud Rechazada*\n\n` +
        `Tu solicitud de acceso ha sido rechazada.\n\n` +
        `Para más información, contacta al administrador.`
      );

    } catch (error) {
      logger.error('[AuthHandler] Error en callback reject', error);
    }
  }

  async handleInfoCallback(ctx) {
    try {
      await ctx.answerCbQuery();
      const userId = ctx.match[1];
      const user = authService.getUserCompleteInfo(userId);

      if (!user) {
        await ctx.answerCbQuery('Usuario no encontrado');
        return;
      }

      await ctx.reply(
        authMessages.getUserDetailedInfoMessage(user),
        {
          parse_mode: 'Markdown',
          ...authKeyboards.getUserManagementKeyboard(userId)
        }
      );

    } catch (error) {
      logger.error('[AuthHandler] Error en callback info', error);
      await ctx.answerCbQuery('Error al cargar información');
    }
  }

  async handlePageCallback(ctx) {
    try {
      await ctx.answerCbQuery();
      const page = parseInt(ctx.match[1]);

      const result = authService.getAuthorizedUsersPaginated(page, 10);

      await ctx.editMessageText(
        authMessages.getAuthorizedUsersListMessage(result.users),
        {
          parse_mode: 'Markdown',
          ...authKeyboards.getPaginatedUsersKeyboard(
            result.pagination.currentPage,
            result.pagination.totalPages
          )
        }
      );

    } catch (error) {
      logger.error('[AuthHandler] Error en callback page', error);
      await ctx.answerCbQuery('Error al cambiar página');
    }
  }

  async handleRefreshListCallback(ctx) {
    try {
      await ctx.answerCbQuery('Lista actualizada');
      const result = authService.getAuthorizedUsersPaginated(1, 10);

      await ctx.editMessageText(
        authMessages.getAuthorizedUsersListMessage(result.users),
        {
          parse_mode: 'Markdown',
          ...authKeyboards.getPaginatedUsersKeyboard(
            result.pagination.currentPage,
            result.pagination.totalPages
          )
        }
      );

    } catch (error) {
      logger.error('[AuthHandler] Error en callback refresh', error);
    }
  }
}

module.exports = AuthHandler;
