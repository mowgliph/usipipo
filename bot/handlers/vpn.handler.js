'use strict';

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');

const WireGuardService = require('../services/wireguard.service');
const OutlineService = require('../services/outline.service');
const userManager = require('../services/userManager.service');

const messages = require('../utils/messages');
const keyboards = require('../utils/keyboards');
const logger = require('../utils/logger');

class VPNHandler {
  constructor() {
    // nothing to inject (services are singletons)
  }

  // -----------------------------
  // Comandos públicos (opcional)
  // -----------------------------
  async cmdVpn(ctx) {
    const userId = ctx.from?.id;
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
    await ctx.reply('🔐 Panel VPN', {
      reply_markup: keyboards.vpnMenu().reply_markup
    });
    logger.info('open_vpn_menu', { userId });
  }

  async cmdMyWg(ctx) {
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
    await ctx.reply('🔐 WireGuard — acciones', {
      reply_markup: keyboards.wgMenu().reply_markup
    });
  }

  async cmdMyOutline(ctx) {
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
    await ctx.reply('🌐 Outline — acciones', {
      reply_markup: keyboards.outlineMenu().reply_markup
    });
  }

  async cmdUsage(ctx) {
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
    await ctx.reply('⏳ Consultando consumo...', { parse_mode: 'HTML' });
    try {
      const userId = ctx.from?.id;
      const wgClient = WireGuardService.getUserClient(userId);
      const wgUsage = wgClient ? await WireGuardService.getClientUsageByName(wgClient.clientName) : { rx: 0, tx: 0, total: 0 };

      const user = userManager.getUser(String(userId));
      let outlineUsage = { rx: 0, tx: 0, total: 0 };
      if (user && user.outline && user.outline.keyId) {
        try {
          outlineUsage = await OutlineService.getKeyUsage(user.outline.keyId);
        } catch (e) {
          logger.debug('Outline usage fetch failed', { userId, err: e.message });
        }
      }

      const msg =
        `<b>📊 Consumo</b>\n\n` +
        `<b>WireGuard</b>\n` +
        `• Recibido: ${formatBytes(wgUsage.rx || 0)}\n` +
        `• Enviado: ${formatBytes(wgUsage.tx || 0)}\n` +
        `• Total: ${formatBytes(wgUsage.total || (wgUsage.rx || 0) + (wgUsage.tx || 0))}\n\n` +
        `<b>Outline</b>\n` +
        `• Recibido: ${formatBytes(outlineUsage.rx || 0)}\n` +
        `• Enviado: ${formatBytes(outlineUsage.tx || 0)}\n` +
        `• Total: ${formatBytes(outlineUsage.total || 0)}\n`;

      await ctx.reply(msg, { parse_mode: 'HTML', ...keyboards.backButton() });
      logger.info('cmdUsage', { userId });
    } catch (err) {
      logger.error('cmdUsage error', err);
      await ctx.reply('❌ No se pudo obtener el consumo. Intenta más tarde.');
    }
  }

  // -----------------------------
  // ACTION: show vpn main menu (called from bot.instance)
  // -----------------------------
  async actionVpnMenu(ctx) {
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
    await ctx.editMessageText('🔐 Menú VPN', {
      reply_markup: keyboards.vpnMenu().reply_markup
    }).catch(() => {
      ctx.reply('🔐 Menú VPN', { reply_markup: keyboards.vpnMenu().reply_markup });
    });
  }

  async actionWgMenu(ctx) {
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
    await ctx.editMessageText('🔐 WireGuard — Acciones', {
      reply_markup: keyboards.wgMenu().reply_markup
    }).catch(() => {
      ctx.reply('🔐 WireGuard — Acciones', { reply_markup: keyboards.wgMenu().reply_markup });
    });
  }

  async actionOutlineMenu(ctx) {
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
    await ctx.editMessageText('🌐 Outline — Acciones', {
      reply_markup: keyboards.outlineMenu().reply_markup
    }).catch(() => {
      ctx.reply('🌐 Outline — Acciones', { reply_markup: keyboards.outlineMenu().reply_markup });
    });
  }

  // -----------------------------
  // CREAR CLIENTE WIREGUARD (botón)
  // -----------------------------
  async handleCreateWireGuard(ctx) {
    const userId = ctx.from?.id;
    const uid = String(userId);

    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
    await ctx.reply(messages.WIREGUARD_CREATING);

    try {
      // Enforce quota before creation
      const quotaExceeded = await WireGuardService.hasQuotaExceededForUser(uid);
      if (quotaExceeded && !userManager.isAdmin(uid)) {
        await ctx.reply('⚠️ Ha excedido su cuota de datos. Contacta al administrador.');
        // Optionally enforce
        await WireGuardService.enforceQuotaForUser(uid);
        return;
      }

      const res = await WireGuardService.createClientForUser(uid);

      // Send .conf as file
      const fileName = path.basename(res.clientFilePath) || `${res.clientName}.conf`;
      try {
        // Prefer send as file from disk if exists (so Telegram shows file size)
        await ctx.replyWithDocument(
          { source: res.clientFilePath, filename: fileName },
          { caption: messages.WIREGUARD_SUCCESS(res.ip), parse_mode: 'HTML' }
        );
      } catch (err) {
        // fallback: send buffer
        await ctx.replyWithDocument(
          { source: Buffer.from(res.clientConfig || ''), filename: fileName },
          { caption: messages.WIREGUARD_SUCCESS(res.ip), parse_mode: 'HTML' }
        );
      }

      // Send QR ASCII if available
      if (res.qr) {
        try {
          await ctx.reply(`<pre>${res.qr}</pre>`, { parse_mode: 'HTML' });
        } catch (_) {
          // ignore
        }
      } else {
        // optionally attempt to render a QR using qrencode if present
        try {
          const ascii = execSync(`echo "${res.clientConfig.replace(/"/g,'\\"')}" | qrencode -t UTF8 -o -`, { encoding: 'utf8' });
          if (ascii) await ctx.reply(`<pre>${ascii}</pre>`, { parse_mode: 'HTML' });
        } catch (_) {
          // no qravailable
        }
      }

      // After creation show quick action buttons
      await ctx.reply(messages.WIREGUARD_INSTRUCTIONS, {
        parse_mode: 'HTML',
        reply_markup: keyboards.wgMenu().reply_markup
      });

      logger.success(userId, 'create_wireguard', { clientName: res.clientName, ip: res.ip });
    } catch (err) {
      logger.error('handleCreateWireGuard error', err, { userId });
      await ctx.reply(messages.ERROR_WIREGUARD(err.message));
    }
  }

  // -----------------------------
  // ACTION: Mostrar configuración (texto o archivo)
  // -----------------------------
  async actionWgShowConfig(ctx) {
    const userId = ctx.from?.id;
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});

    try {
      const client = WireGuardService.getUserClient(userId);
      if (!client) {
        await ctx.reply('ℹ️ No tienes una configuración WireGuard. Crea una desde el menú.', keyboards.wgMenu());
        return;
      }

      if (client.clientFilePath) {
        // send as text (safe)
        const raw = await fs.readFile(client.clientFilePath, 'utf8');
        await ctx.reply(`<pre>${raw}</pre>`, { parse_mode: 'HTML' });
      } else if (client.clientConfig) {
        await ctx.reply(`<pre>${client.clientConfig}</pre>`, { parse_mode: 'HTML' });
      } else {
        await ctx.reply('⚠️ No pude recuperar tu archivo .conf.', keyboards.wgMenu());
      }
      logger.info(userId, 'wg_show_config', { clientName: client.clientName });
    } catch (err) {
      logger.error('actionWgShowConfig', err, { userId });
      await ctx.reply('❌ Error mostrando configuración WireGuard.');
    }
  }

  // -----------------------------
  // ACTION: Descargar .conf
  // -----------------------------
  async actionWgDownload(ctx) {
    const userId = ctx.from?.id;
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});

    try {
      const client = WireGuardService.getUserClient(userId);
      if (!client) {
        await ctx.reply('ℹ️ No tienes configuración WireGuard.', keyboards.wgMenu());
        return;
      }

      const filename = `${client.clientName || `wg_${userId}`}.conf`;

      if (client.clientFilePath) {
        await ctx.replyWithDocument({ source: client.clientFilePath, filename }, { caption: '✅ Tu archivo .conf' });
      } else if (client.clientConfig) {
        await ctx.replyWithDocument({ source: Buffer.from(client.clientConfig, 'utf8'), filename }, { caption: '✅ Tu archivo .conf' });
      } else {
        await ctx.reply('⚠️ No está disponible el archivo .conf.', keyboards.wgMenu());
      }

      logger.info(userId, 'wg_download', { clientName: client.clientName });
    } catch (err) {
      logger.error('actionWgDownload', err, { userId });
      await ctx.reply('❌ Error descargando .conf');
    }
  }

  // -----------------------------
  // ACTION: Mostrar QR
  // -----------------------------
  async actionWgShowQr(ctx) {
    const userId = ctx.from?.id;
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});

    try {
      const client = WireGuardService.getUserClient(userId);
      if (!client) {
        await ctx.reply('ℹ️ No tienes configuración WireGuard.', keyboards.wgMenu());
        return;
      }

      if (client.qr) {
        await ctx.reply(`<pre>${client.qr}</pre>`, { parse_mode: 'HTML' });
      } else if (client.clientConfig) {
        // attempt quick local generation (if qrencode present)
        try {
          const ascii = execSync(`echo "${client.clientConfig.replace(/"/g,'\\"')}" | qrencode -t UTF8 -o -`, { encoding: 'utf8' });
          if (ascii) {
            await ctx.reply(`<pre>${ascii}</pre>`, { parse_mode: 'HTML' });
            return;
          }
        } catch (_) {}
        await ctx.reply('⚠️ No se pudo generar QR en este servidor.', keyboards.wgMenu());
      } else {
        await ctx.reply('⚠️ No hay configuración para generar QR.', keyboards.wgMenu());
      }

      logger.info(userId, 'wg_show_qr', { clientName: client.clientName });
    } catch (err) {
      logger.error('actionWgShowQr', err, { userId });
      await ctx.reply('❌ Error mostrando QR.');
    }
  }

  // -----------------------------
  // ACTION: Ver consumo WG
  // -----------------------------
  async actionWgUsage(ctx) {
    const userId = ctx.from?.id;
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});

    try {
      const client = WireGuardService.getUserClient(userId);
      if (!client) {
        await ctx.reply('ℹ️ No tienes configuración WireGuard.', keyboards.wgMenu());
        return;
      }

      const usage = await WireGuardService.getClientUsageByName(client.clientName);

      const msg =
        `<b>📈 Uso WireGuard</b>\n\n` +
        `• Recibido: ${formatBytes(usage.rx || 0)}\n` +
        `• Enviado: ${formatBytes(usage.tx || 0)}\n` +
        `• Total: ${formatBytes(usage.total || (usage.rx || 0) + (usage.tx || 0))}\n`;

      await ctx.reply(msg, { parse_mode: 'HTML', ...keyboards.backButton() });
      logger.info(userId, 'wg_usage', { clientName: client.clientName, usage });
    } catch (err) {
      logger.error('actionWgUsage', err, { userId });
      await ctx.reply('❌ No se pudo obtener el consumo WireGuard.');
    }
  }

  // -----------------------------
  // ACTION: Solicitar eliminación (muestra confirmación compacta)
  // -----------------------------
  async actionWgDelete(ctx) {
    const userId = ctx.from?.id;
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});

    try {
      const client = WireGuardService.getUserClient(userId);
      if (!client) {
        await ctx.reply('ℹ️ No tienes configuración WireGuard para eliminar.', keyboards.wgMenu());
        return;
      }

      const clientName = client.clientName;
      const keyboard = {
        reply_markup: {
          inline_keyboard: [
            [
              { text: '✅ Confirmar', callback_data: `confirm_delete_wg_${clientName}` },
              { text: '❌ Cancelar', callback_data: 'cancel_action' }
            ]
          ]
        }
      };

      await ctx.reply(`⚠️ ¿Confirmas eliminar tu configuración WireGuard (${clientName})?`, keyboard);
    } catch (err) {
      logger.error('actionWgDelete', err, { userId });
      await ctx.reply('❌ Error preparando eliminación.');
    }
  }

  // -----------------------------
  // CALLBACK: Confirm deletion (invocado desde bot.instance)
  // signature: confirmDeleteWireGuard(ctx, clientName)
  // -----------------------------
  async confirmDeleteWireGuard(ctx, clientName) {
    const userId = ctx.from?.id;
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});

    try {
      // double-check ownership or admin
      const client = WireGuardService.getUserClient(userId);
      if (!client || client.clientName !== clientName) {
        // if admin, allow deletion by name (admin flows not implemented here)
        if (!userManager.isAdmin(String(userId))) {
          await ctx.reply('⛔ No tienes permiso para eliminar esta configuración.');
          return;
        }
      }

      await WireGuardService.deleteClientByName(clientName);

      // update userManager mapping already handled in service; still ensure we save
      await userManager.saveUsers();

      await ctx.reply('✅ Tu configuración WireGuard ha sido eliminada.', keyboards.wgMenu());
      logger.warn(userId, 'wg_deleted', { clientName });
    } catch (err) {
      logger.error('confirmDeleteWireGuard', err, { userId, clientName });
      await ctx.reply('❌ No se pudo eliminar la configuración WireGuard.');
    }
  }

  // -----------------------------
  // OUTLINE: Crear clave
  // -----------------------------
  async handleCreateOutline(ctx) {
    const userId = ctx.from?.id;
    const uid = String(userId);

    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
    await ctx.reply(messages.OUTLINE_CREATING);

    try {
      // build nice key name
      const safeName = (ctx.from?.username || ctx.from?.first_name || `User${uid}`).replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 20);
      const keyName = `TG-${safeName}-${Date.now()}`;

      const accessKey = await OutlineService.createAccessKey(keyName);

      // Store in userManager
      let user = userManager.getUser(uid);
      if (!user) {
        // create minimal user entry
        await userManager.addUser(uid, 'system', `TG ${uid}`);
        user = userManager.getUser(uid);
      }
      user.outline = {
        keyId: accessKey.id,
        accessUrl: accessKey.accessUrl,
        createdAt: new Date().toISOString()
      };
      await userManager.saveUsers();

      // Append branding to link as requested e.g. "#uSipipo VPN, MIAMI, US" — Outline link must support fragment
      const branded = `${accessKey.accessUrl}#uSipipo%20VPN,%20MIAMI,%20US`;

      await ctx.reply(messages.OUTLINE_SUCCESS({ id: accessKey.id, accessUrl: branded }), { parse_mode: 'HTML', reply_markup: keyboards.outlineMenu().reply_markup });

      logger.success(userId, 'create_outline', { keyId: accessKey.id, accessUrl: accessKey.accessUrl });
    } catch (err) {
      logger.error('handleCreateOutline', err, { userId });
      await ctx.reply(messages.ERROR_OUTLINE(err.message));
    }
  }

  // -----------------------------
  // OUTLINE: Mostrar enlace
  // -----------------------------
  async actionOutlineShow(ctx) {
    const userId = ctx.from?.id;
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});

    try {
      const user = userManager.getUser(String(userId));
      if (!user || !user.outline) {
        await ctx.reply('ℹ️ No tienes una clave Outline asignada.', keyboards.outlineMenu());
        return;
      }

      await ctx.reply(`<b>🔗 Tu enlace Outline</b>\n\n${user.outline.accessUrl}`, { parse_mode: 'HTML', ...keyboards.backButton() });
      logger.info(userId, 'outline_show', { keyId: user.outline.keyId });
    } catch (err) {
      logger.error('actionOutlineShow', err, { userId });
      await ctx.reply('❌ Error obteniendo tu enlace Outline.');
    }
  }

  // -----------------------------
  // OUTLINE: Uso
  // -----------------------------
  async actionOutlineUsage(ctx) {
    const userId = ctx.from?.id;
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});

    try {
      const user = userManager.getUser(String(userId));
      if (!user || !user.outline) {
        await ctx.reply('ℹ️ No tienes clave Outline asignada.', keyboards.outlineMenu());
        return;
      }

      const usage = await OutlineService.getKeyUsage(user.outline.keyId);

      const msg =
        `<b>📈 Uso Outline</b>\n\n` +
        `• Recibido: ${formatBytes(usage.rx || 0)}\n` +
        `• Enviado: ${formatBytes(usage.tx || 0)}\n` +
        `• Total: ${formatBytes(usage.total || 0)}\n`;

      await ctx.reply(msg, { parse_mode: 'HTML', ...keyboards.backButton() });
      logger.info(userId, 'outline_usage', { keyId: user.outline.keyId, usage });
    } catch (err) {
      logger.error('actionOutlineUsage', err, { userId });
      await ctx.reply('❌ No se pudo obtener el consumo Outline.');
    }
  }

  // -----------------------------
  // OUTLINE: solicitar eliminación (muestra confirm)
  // -----------------------------
  async actionOutlineDelete(ctx) {
    const userId = ctx.from?.id;
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});

    try {
      const user = userManager.getUser(String(userId));
      if (!user || !user.outline) {
        await ctx.reply('ℹ️ No tienes clave Outline para eliminar.', keyboards.outlineMenu());
        return;
      }

      const keyId = user.outline.keyId;
      const keyboard = {
        reply_markup: {
          inline_keyboard: [
            [
              { text: '✅ Confirmar', callback_data: `confirm_delete_outline_${keyId}` },
              { text: '❌ Cancelar', callback_data: 'cancel_action' }
            ]
          ]
        }
      };

      await ctx.reply(`⚠️ ¿Confirmas eliminar tu clave Outline?`, keyboard);
    } catch (err) {
      logger.error('actionOutlineDelete', err, { userId });
      await ctx.reply('❌ Error preparando eliminación Outline.');
    }
  }

  // -----------------------------
  // CALLBACK: confirm delete outline
  // signature: confirmDeleteOutlineKey(ctx, keyId)
  // -----------------------------
  async confirmDeleteOutlineKey(ctx, keyId) {
    const userId = ctx.from?.id;
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});

    try {
      const user = userManager.getUser(String(userId));
      if (!user || !user.outline || user.outline.keyId !== keyId) {
        if (!userManager.isAdmin(String(userId))) {
          await ctx.reply('⛔ No tienes permiso para eliminar esta clave.');
          return;
        }
      }

      await OutlineService.deleteKeyForUser(String(userId));

      // remove local mapping
      if (user && user.outline && user.outline.keyId === keyId) {
        delete user.outline;
        await userManager.saveUsers();
      }

      await ctx.reply('✅ Tu clave Outline ha sido eliminada.', keyboards.outlineMenu());
      logger.warn(userId, 'outline_deleted', { keyId });
    } catch (err) {
      logger.error('confirmDeleteOutlineKey', err, { userId, keyId });
      await ctx.reply('❌ No se pudo eliminar la clave Outline.');
    }
  }

  // -----------------------------
  // LISTAR CLIENTES (WireGuard + Outline)
  // -----------------------------
  async handleListClients(ctx) {
    const userId = ctx.from?.id;
    if (ctx.answerCbQuery) await ctx.answerCbQuery().catch(() => {});
    await ctx.reply('⏳ Consultando...', { parse_mode: 'HTML' });

    try {
      const [wgClients, outlineKeys] = await Promise.all([
        WireGuardService.listClients(),
        OutlineService.listAccessKeys()
      ]);

      // format compact message
      const wgLines = (wgClients || []).map((c, i) => `${i + 1}) ${c.ip} • ${formatBytes(c.dataReceived || 0)} ↓ • ${formatBytes(c.dataSent || 0)} ↑`).join('\n') || 'No hay clientes WireGuard';
      const olLines = (outlineKeys || []).map((k, i) => `${i + 1}) ${k.id} • ${k.name || 'Sin nombre'}`).join('\n') || 'No hay claves Outline';

      const msg = `<b>📊 CLIENTES ACTIVOS</b>\n\n<b>🔐 WireGuard</b>\n${wgLines}\n\n<b>🌐 Outline</b>\n${olLines}`;

      await ctx.reply(msg, { parse_mode: 'HTML', ...keyboards.backButton() });

      logger.info(userId, 'list_clients', { wg: (wgClients || []).length, outline: (outlineKeys || []).length });
    } catch (err) {
      logger.error('handleListClients', err, { userId });
      await ctx.reply(messages.ERROR_LIST_CLIENTS, keyboards.backButton());
    }
  }
}

// -----------------------------
// Helpers locales
// -----------------------------
function formatBytes(bytes) {
  if (!bytes || bytes <= 0) return '0 B';
  const k = 1024;
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const val = (bytes / Math.pow(k, i)).toFixed(2);
  return `${val} ${units[i]}`;
}

module.exports = new VPNHandler();