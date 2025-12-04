// handlers/vpn.handler.js
const WireGuardService = require('../services/wireguard.service');
const OutlineService = require('../services/outline.service');
const messages = require('../utils/messages');
const formatters = require('../utils/formatters');

class VPNHandler {
  /**
   * Crea configuración WireGuard
   */
  async handleCreateWireGuard(ctx) {
    await ctx.answerCbQuery();
    await ctx.reply(messages.WIREGUARD_CREATING);
    
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
          parse_mode: 'Markdown'
        }
      );
      
      // Enviar QR code
      await ctx.reply(`\`\`\`\n${qr}\n\`\`\``, { parse_mode: 'Markdown' });
      
      // Instrucciones
      await ctx.reply(messages.WIREGUARD_INSTRUCTIONS, { parse_mode: 'Markdown' });
      
      console.log(`✅ WireGuard creado para usuario ${ctx.from.id} - IP: ${clientIP}`);
      
    } catch (error) {
      console.error('WireGuard creation error:', error);
      ctx.reply(messages.ERROR_WIREGUARD(error.message));
    }
  }

  /**
   * Crea clave Outline
   */
  async handleCreateOutline(ctx) {
    await ctx.answerCbQuery();
    await ctx.reply(messages.OUTLINE_CREATING);
    
    try {
      const userId = ctx.from.id;
      const userName = ctx.from.username || ctx.from.first_name || `User${userId}`;
      
      // Crear clave con nombre descriptivo
      const keyName = `TG-${userName}-${Date.now()}`;
      const accessKey = await OutlineService.createAccessKey(keyName);
      
      // Mensaje con la clave de acceso
      const message = 
        `✅ **Clave Outline creada exitosamente**\n\n` +
        `🔑 **ID:** \`${accessKey.id}\`\n` +
        `👤 **Nombre:** ${keyName}\n\n` +
        `📱 **Copia este enlace en tu app Outline:**\n\n` +
        `\`${accessKey.accessUrl}\`\n\n` +
        `📊 **Límite de datos:** 10GB/mes\n` +
        `🛡️ **DNS:** Protección con Pi-hole activada\n\n` +
        `🔗 **Descargar Outline:**\n` +
        `• Android: https://play.google.com/store/apps/details?id=org.outline.android.client\n` +
        `• iOS: https://apps.apple.com/app/outline-app/id1356177741\n` +
        `• Windows/Mac: https://getoutline.org/get-started/`;
      
      await ctx.reply(message, { parse_mode: 'Markdown' });
      
      console.log(`✅ Outline key created for user ${userId} - Key ID: ${accessKey.id}`);
      
    } catch (error) {
      console.error('Outline creation error:', error);
      ctx.reply(messages.ERROR_OUTLINE(error.message));
    }
  }

  /**
   * Lista clientes activos
   */
  async handleListClients(ctx) {
    await ctx.answerCbQuery();
    await ctx.reply('🔍 Consultando clientes activos...');
    
    try {
      const [wgClients, outlineKeys] = await Promise.all([
        WireGuardService.listClients(),
        OutlineService.listAccessKeys()
      ]);
      
      const message = formatters.formatClientsList(wgClients, outlineKeys);
      await ctx.reply(message, { parse_mode: 'Markdown' });
      
    } catch (error) {
      console.error('List clients error:', error);
      ctx.reply(messages.ERROR_LIST_CLIENTS);
    }
  }
}

module.exports = VPNHandler;
