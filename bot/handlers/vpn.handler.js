const WireGuardService = require('../services/wireguard.service');
const OutlineService = require('../services/outline.service');
const messages = require('../utils/messages');
const formatters = require('../utils/formatters');
const logger = require('../utils/logger');

class VPNHandler {
  /**
   * Crear cliente WireGuard
   */
  async handleCreateWireGuard(ctx) {
    const userId = ctx.from?.id;
    let safeUser = (ctx.from?.username || ctx.from?.first_name || `User${userId}`)
      .replace(/[^a-zA-Z0-9]/g, '');
    if (!safeUser) safeUser = `User${userId}`;

    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
    await ctx.reply(messages.WIREGUARD_CREATING);

    try {
      const { config, qr, clientIP } = await WireGuardService.createNewClient();

      // Nombre de archivo seguro (Ej: User_WG_23.conf)
      const ipSuffix = clientIP.split('.').pop();
      const fileName = `${safeUser}_WG_${ipSuffix}.conf`;

      // Archivo de configuración
      await ctx.replyWithDocument(
        {
          source: Buffer.from(config),
          filename: fileName
        },
        {
          caption: messages.WIREGUARD_SUCCESS(clientIP)
        }
      );

      // QR
      await ctx.reply(`<pre>${qr}</pre>`);

      // Instrucciones compactas
      await ctx.reply(messages.WIREGUARD_INSTRUCTIONS);

      logger.success(userId, 'create_wireguard', clientIP, {
        userName: safeUser,
        clientIP
      });
    } catch (err) {
      logger.error('handleCreateWireGuard', err, { userId, safeUser });
      await ctx.reply(messages.ERROR_WIREGUARD(err.message));
    }
  }

  /**
   * Crear clave Outline
   */
  async handleCreateOutline(ctx) {
    const userId = ctx.from?.id;
    const safeName =
      (ctx.from?.username || ctx.from?.first_name || `User${userId}`).replace(/[^a-zA-Z0-9]/g, '') ||
      `User${userId}`;

    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
    await ctx.reply(messages.OUTLINE_CREATING);

    try {
      const keyName = `TG-${safeName}-${Date.now()}`;
      const accessKey = await OutlineService.createAccessKey(keyName);

      await ctx.reply(messages.OUTLINE_SUCCESS(accessKey));

      logger.success(userId, 'create_outline', accessKey.id, {
        keyName,
        accessUrl: accessKey.accessUrl
      });
    } catch (err) {
      logger.error('handleCreateOutline', err, { userId, safeName });
      await ctx.reply(messages.ERROR_OUTLINE(err.message));
    }
  }

  /**
   * Lista clientes activos (WireGuard + Outline)
   */
  async handleListClients(ctx) {
    const userId = ctx.from?.id;

    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
    await ctx.reply('⏳ Consultando...', { parse_mode: 'HTML' });

    try {
      const [wg, outline] = await Promise.all([
        WireGuardService.listClients(),
        OutlineService.listAccessKeys()
      ]);

      const msg = formatters.formatClientsList(wg, outline);
      await ctx.reply(msg);

      logger.info(userId, 'list_clients', {
        wireguard_clients: wg.length,
        outline_keys: outline.length
      });
    } catch (err) {
      logger.error('handleListClients', err, { userId });
      await ctx.reply(messages.ERROR_LIST_CLIENTS);
    }
  }
}

module.exports = VPNHandler;