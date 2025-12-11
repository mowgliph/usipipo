'use strict';

const markdown = require('../../core/utils/markdown');
const constants = require('../../config/constants');

/**
 * Mensajes para el módulo de inicio (Start)
 */
module.exports = {

  /**
   * Mensaje para administradores
   */
  getAdminWelcome: (user) => {
    return `${constants.EMOJI.ADMIN} *Panel de Administración*\n\n` +
           `Hola, ${markdown.bold(user.first_name)}. Tienes privilegios de administrador.\n\n` +
           `🛠 *Estado:* Sistema Operativo\n` +
           `🔐 *Rol:* Administrador\n\n` +
           `Selecciona una opción del menú para gestionar el servidor VPN o los usuarios.`;
  },

  /**
   * Mensaje para usuarios autorizados estándar
   */
  getAuthorizedWelcome: (user) => {
    return `${constants.EMOJI.SUCCESS} *Bienvenido a uSipipo VPN*\n\n` +
           `Hola ${markdown.bold(user.first_name)}, tu acceso está activo.\n\n` +
           `Desde aquí puedes generar tus claves de acceso para:\n` +
           `⚡️ *WireGuard* (Alta velocidad)\n` +
           `🌐 *Outline* (Alta compatibilidad)\n\n` +
           `Usa el menú inferior para comenzar.`;
  },

  /**
   * Mensaje para usuarios NO autorizados (Invitados)
   */
  getUnauthorizedWelcome: (user) => {
    return `${constants.EMOJI.ERROR} *Acceso Restringido*\n\n` +
           `Hola ${markdown.escapeMarkdown(user.first_name)}.\n` +
           `Este es un bot privado para gestión de VPN.\n\n` +
           `🆔 *Tu ID:* ${markdown.code(user.id)}\n` +
           `👤 *Usuario:* ${user.username ? '@' + markdown.escapeMarkdown(user.username) : 'Sin alias'}\n\n` +
           `⛔️ No tienes permisos para usar este sistema.\n` +
           `Por favor, envía tu ID al administrador para solicitar acceso.`;
  },

  /**
   * Mensaje para usuarios suspendidos
   */
  getSuspendedMessage: () => {
    return `${constants.EMOJI.WARNING} *Cuenta Suspendida*\n\n` +
           `Tu acceso al sistema ha sido suspendido temporalmente.\n` +
           `Si crees que es un error, contacta al administrador.`;
  }
};
