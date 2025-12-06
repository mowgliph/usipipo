// handlers/vpn.handler.js
const WireGuardService = require('../services/wireguard.service');
const OutlineService = require('../services/outline.service');
const messages = require('../utils/messages');
const formatters = require('../utils/formatters');
const logger = require('../utils/logger');

/**
 * Handler para operaciones VPN (WireGuard / Outline).
 * Gestiona la creación, consulta y visualización de clientes VPN a través del bot Telegram.
 */
class VPNHandler {
  /**
   * Crea un nuevo cliente WireGuard y entrega al usuario
   * el archivo de configuración + código QR.
   * @param {import('telegraf').Context} ctx - Contexto del bot Telegraf
   */
  async handleCreateWireGuard(ctx) {
    const userId = ctx.from?.id;
    const userName = ctx.from?.username || ctx.from?.first_name || `User${userId}`;

    await ctx.answerCbQuery();
    await ctx.reply(messages.WIREGUARD_CREATING, { parse_mode: 'MarkdownV2' });

    try {
      const { config, qr, clientIP } = await WireGuardService.createNewClient();

      // Enviar archivo de configuración
      await ctx.replyWithDocument(
        {
          source: Buffer.from(config),
          filename: `wireguard-${clientIP.replace(/./g, '-')}.conf`
        },
        {
          caption: messages.WIREGUARD_SUCCESS(clientIP),
          parse_mode: 'MarkdownV2'
        }
      );

      // Enviar código QR como bloque de texto (MarkdownV2: ```texto```)
      // CORRECCIÓN: Usar concatenación o template string con escape para asegurar el formato ```
      await ctx.reply('```\n' + qr + '\n```', { parse_mode: 'MarkdownV2' });

      // Enviar instrucciones de conexión
      await ctx.reply(messages.WIREGUARD_INSTRUCTIONS, { parse_mode: 'MarkdownV2' });

      logger.success(userId, 'create_wireguard', clientIP, { userName, clientIP });
    } catch (error) {
      logger.error('handleCreateWireGuard', error, { userId, userName });
      await ctx.reply(messages.ERROR_WIREGUARD(error.message), { parse_mode: 'MarkdownV2' });
    }
  }

  /**
   * Crea una nueva clave Outline y la devuelve al usuario.
   * @param {import('telegraf').Context} ctx - Contexto del bot Telegraf
   */
  async handleCreateOutline(ctx) {
    const userId = ctx.from?.id;
    const userName = ctx.from?.username || ctx.from?.first_name || `User${userId}`;

    await ctx.answerCbQuery();
    await ctx.reply(messages.OUTLINE_CREATING, { parse_mode: 'MarkdownV2' });

    try {
      const keyName = `TG-${userName}-${Date.now()}`;
      const accessKey = await OutlineService.createAccessKey(keyName);

      const message = messages.OUTLINE_SUCCESS(accessKey);
      await ctx.reply(message, { parse_mode: 'MarkdownV2' });

      logger.success(userId, 'create_outline', accessKey.id, { keyName, accessUrl: accessKey.accessUrl });
    } catch (error) {
      logger.error('handleCreateOutline', error, { userId, userName });
      await ctx.reply(messages.ERROR_OUTLINE(error.message), { parse_mode: 'MarkdownV2' });
    }
  }

  /**
   * Lista todos los clientes activos de WireGuard y Outline.
   * @param {import('telegraf').Context} ctx - Contexto del bot Telegraf
   */
  async handleListClients(ctx) {
    const userId = ctx.from?.id;
    const userName = ctx.from?.username || ctx.from?.first_name || `User${userId}`;

    await ctx.answerCbQuery();
    await ctx.reply('🔍 Consultando clientes activos...', { parse_mode: 'MarkdownV2' });

    try {
      const [wgClients, outlineKeys] = await Promise.all([
        WireGuardService.listClients(),
        OutlineService.listAccessKeys()
      ]);

      const message = formatters.formatClientsList(wgClients, outlineKeys);
      await ctx.reply(message, { parse_mode: 'MarkdownV2' });

      logger.info(userId, 'list_clients', {
        wireguard_clients: wgClients.length,
        outline_keys: outlineKeys.length
      });
    } catch (error) {
      logger.error('handleListClients', error, { userId, userName });
      await ctx.reply(messages.ERROR_LIST_CLIENTS, { parse_mode: 'MarkdownV2' });
    }
  }
}

module.exports = VPNHandler;
