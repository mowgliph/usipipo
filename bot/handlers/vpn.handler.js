const WireGuardService = require('../services/wireguard.service');
const OutlineService = require('../services/outline.service');
const messages = require('../utils/messages');
const formatters = require('../utils/formatters');
const logger = require('../utils/logger');

/**
 * Handler para operaciones VPN (WireGuard / Outline).
 * Gestiona la creación, consulta y visualización de clientes VPN.
 */
class VPNHandler {
  /**
   * Crea un nuevo cliente WireGuard.
   */
  async handleCreateWireGuard(ctx) {
    const userId = ctx.from?.id;
    const userName = ctx.from?.username || ctx.from?.first_name || `User${userId}`;

    await ctx.answerCbQuery();
    // CORREGIDO: parse_mode a HTML
    await ctx.reply(messages.WIREGUARD_CREATING, { parse_mode: 'HTML' });

    try {
      const { config, qr, clientIP } = await WireGuardService.createNewClient();

      // Enviar archivo de configuración
      await ctx.replyWithDocument(
        {
          source: Buffer.from(config),
          filename: `wireguard-${clientIP.replace(/\./g, '-')}.conf`
        },
        {
          caption: messages.WIREGUARD_SUCCESS(clientIP),
          parse_mode: 'HTML' // CORREGIDO: HTML para interpretar <b> y <code>
        }
      );

      // CORREGIDO: El bloque de código ``` no funciona en HTML mode.
      // Usamos la etiqueta <pre> para bloque de código o <code> para inline.
      const qrMessage = `<pre>${qr}</pre>`;
      await ctx.reply(qrMessage, { parse_mode: 'HTML' });

      // Enviar instrucciones de conexión
      await ctx.reply(messages.WIREGUARD_INSTRUCTIONS, { parse_mode: 'HTML' });

      logger.success(userId, 'create_wireguard', clientIP, { userName, clientIP });
    } catch (error) {
      logger.error('handleCreateWireGuard', error, { userId, userName });
      await ctx.reply(messages.ERROR_WIREGUARD(error.message), { parse_mode: 'HTML' });
    }
  }

  /**
   * Crea una nueva clave Outline.
   */
  async handleCreateOutline(ctx) {
    const userId = ctx.from?.id;
    const userName = ctx.from?.username || ctx.from?.first_name || `User${userId}`;

    await ctx.answerCbQuery();
    await ctx.reply(messages.OUTLINE_CREATING, { parse_mode: 'HTML' });

    try {
      const keyName = `TG-${userName}-${Date.now()}`;
      const accessKey = await OutlineService.createAccessKey(keyName);

      const message = messages.OUTLINE_SUCCESS(accessKey);
      await ctx.reply(message, { parse_mode: 'HTML' }); // CORREGIDO

      logger.success(userId, 'create_outline', accessKey.id, { keyName, accessUrl: accessKey.accessUrl });
    } catch (error) {
      logger.error('handleCreateOutline', error, { userId, userName });
      await ctx.reply(messages.ERROR_OUTLINE(error.message), { parse_mode: 'HTML' });
    }
  }

  /**
   * Lista todos los clientes activos.
   */
  async handleListClients(ctx) {
    const userId = ctx.from?.id;
    const userName = ctx.from?.username || ctx.from?.first_name || `User${userId}`;

    await ctx.answerCbQuery();
    // Usar HTML para mantener consistencia, aunque este mensaje sea texto plano
    await ctx.reply('⏳ Consultando clientes activos...', { parse_mode: 'HTML' });

    try {
      const [wgClients, outlineKeys] = await Promise.all([
        WireGuardService.listClients(),
        OutlineService.listAccessKeys()
      ]);

      const message = formatters.formatClientsList(wgClients, outlineKeys);
      await ctx.reply(message, { parse_mode: 'HTML' }); // CORREGIDO

      logger.info(userId, 'list_clients', {
        wireguard_clients: wgClients.length,
        outline_keys: outlineKeys.length
      });
    } catch (error) {
      logger.error('handleListClients', error, { userId, userName });
      await ctx.reply(messages.ERROR_LIST_CLIENTS, { parse_mode: 'HTML' });
    }
  }
}

module.exports = VPNHandler;
