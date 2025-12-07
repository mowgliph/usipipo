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
    // Sanitizar username: Solo letras y números, fallback a 'UserID'
    let safeUserName = (ctx.from?.username || ctx.from?.first_name || `User${userId}`).replace(/[^a-zA-Z0-9]/g, '');
    if (!safeUserName) safeUserName = `User${userId}`;

    await ctx.answerCbQuery();
    await ctx.reply(messages.WIREGUARD_CREATING, { parse_mode: 'HTML' });

    try {
      const { config, qr, clientIP } = await WireGuardService.createNewClient();

      // CORRECCIÓN 1: Nombre de archivo estricto (ej: UserName_10-13-13-2.conf)
      // WireGuard odia espacios y caracteres raros en el nombre del archivo.
      const ipSuffix = clientIP.split('.').pop(); // Obtiene el último octeto (ej: 2)
      const safeFilename = `${safeUserName}_WG_${ipSuffix}.conf`;

      // Enviar archivo de configuración
      await ctx.replyWithDocument(
        {
          source: Buffer.from(config),
          filename: safeFilename
        },
        {
          caption: messages.WIREGUARD_SUCCESS(clientIP),
          parse_mode: 'HTML'
        }
      );

      // QR Code
      const qrMessage = `<pre>${qr}</pre>`;
      await ctx.reply(qrMessage, { parse_mode: 'HTML' });

      // Enviar instrucciones de conexión
      await ctx.reply(messages.WIREGUARD_INSTRUCTIONS, { parse_mode: 'HTML' });

      logger.success(userId, 'create_wireguard', clientIP, { userName: safeUserName, clientIP });
    } catch (error) {
      logger.error('handleCreateWireGuard', error, { userId, userName: safeUserName });
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
      await ctx.reply(message, { parse_mode: 'HTML' });

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
    await ctx.reply('⏳ Consultando clientes activos...', { parse_mode: 'HTML' });

    try {
      const [wgClients, outlineKeys] = await Promise.all([
        WireGuardService.listClients(),
        OutlineService.listAccessKeys()
      ]);

      const message = formatters.formatClientsList(wgClients, outlineKeys);
      await ctx.reply(message, { parse_mode: 'HTML' });

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
