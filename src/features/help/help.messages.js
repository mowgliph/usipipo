'use strict';

const markdown = require('../../core/utils/markdown');
const constants = require('../../config/constants');

/**
 * ============================================================================
 * 📚 HELP MESSAGES - Centro de Ayuda uSipipo VPN
 * ============================================================================
 * Mensajes centralizados con Markdown V1 para máxima compatibilidad.
 * Organizado por categorías para fácil mantenimiento.
 * ============================================================================
 */

module.exports = {
  // ==========================================================================
  // 🎯 MENSAJES PRINCIPALES
  // ==========================================================================
  
  HELP_MAIN: (userName = 'Usuario') => {
    return `📚 *CENTRO DE AYUDA - uSipipo VPN*\n\n` +
           `¡Hola ${markdown.escapeMarkdown(userName)}! Soy tu asistente VPN.\n` +
           `Aquí tienes toda la información para usar el sistema:\n\n` +
           
           `${constants.EMOJI.POINT_RIGHT} *COMANDOS DISPONIBLES:*\n` +
           `${markdown.code('/start')} - Menú principal y bienvenida\n` +
           `${markdown.code('/help')} - Este centro de ayuda\n` +
           `${markdown.code('/info')} - Estado del sistema y estadísticas\n` +
           `${markdown.code('/vpn')} - Gestionar conexiones VPN\n` +
           `${markdown.code('/user')} - Tu perfil y configuración\n` +
           `${markdown.code('/auth')} - Solicitar acceso al sistema\n` +
           `${markdown.code('/admin')} - Panel de administración (solo admins)\n\n` +
           
           `${constants.EMOJI.POINT_RIGHT} *SECCIONES DE AYUDA:*\n` +
           `Selecciona una categoría abajo para más detalles.`;
  },

  // ==========================================================================
  // 🔐 AYUDA VPN
  // ==========================================================================
  
  HELP_VPN_GENERAL: () => {
    return `🔐 *AYUDA SOBRE VPN*\n\n` +
           `El sistema soporta dos tipos de VPN:\n\n` +
           
           `${constants.EMOJI.VPN} *WireGuard:*\n` +
           `• Protocolo moderno y de alto rendimiento\n` +
           `• Encriptación de última generación\n` +
           `• Configuración nativa en dispositivos\n` +
           `• Mayor velocidad y menor latencia\n` +
           `• Ideal para streaming y gaming\n\n` +
           
           `${constants.EMOJI.SERVER} *Outline:*\n` +
           `• Desarrollado por Google (Jigsaw)\n` +
           `• App oficial fácil de usar\n` +
           `• Enlace de conexión directo\n` +
           `• Perfecto para dispositivos móviles\n` +
           `• Gran compatibilidad multiplataforma\n\n` +
           
           `${constants.EMOJI.POINT_RIGHT} *Cómo obtener una VPN:*\n` +
           `1. Usa el comando ${markdown.code('/vpn')}\n` +
           `2. Selecciona el tipo de VPN\n` +
           `3. Sigue las instrucciones\n` +
           `4. Configura en tu dispositivo`;
  },

  HELP_VPN_WIREGUARD: () => {
    return `🛡️ *WireGuard - Guía de Configuración*\n\n` +
           `${constants.EMOJI.POINT_RIGHT} *Apps oficiales:*\n` +
           `• Windows: WireGuard oficial\n` +
           `• macOS: App Store / brew install wireguard-tools\n` +
           `• Linux: sudo apt install wireguard\n` +
           `• Android: WireGuard en Play Store\n` +
           `• iOS: WireGuard en App Store\n\n` +
           
           `${constants.EMOJI.POINT_RIGHT} *Pasos de configuración:*\n` +
           `1. Descarga la app oficial\n` +
           `2. Crea un nuevo túnel\n` +
           `3. Escanea el código QR o copia la configuración\n` +
           `4. Activa la conexión\n` +
           `5. ¡Listo! Tu tráfico está protegido\n\n` +
           
           `${constants.EMOJI.POINT_RIGHT} *Solución de problemas:*\n` +
           `• Verifica que la app tenga permiso VPN\n` +
           `• Asegúrate de tener conexión a Internet\n` +
           `• Reinicia la app si no conecta\n` +
           `• Contacta al admin si persiste`;
  },

  HELP_VPN_OUTLINE: () => {
    return `🌐 *Outline - Guía de Configuración*\n\n` +
           `${constants.EMOJI.POINT_RIGHT} *Apps oficiales:*\n` +
           `• Todos los dispositivos: Outline Client\n` +
           `• Disponible en: outline.net\n\n` +
           
           `${constants.EMOJI.POINT_RIGHT} *Pasos de configuración:*\n` +
           `1. Descarga Outline Client\n` +
           `2. Pega el enlace de conexión\n` +
           `3. La app configurará todo automáticamente\n` +
           `4. Activa el interruptor de VPN\n` +
           `5. ¡Listo! Conexión establecida\n\n` +
           
           `${constants.EMOJI.POINT_RIGHT} *Características:*\n` +
           `• Configuración en un clic\n` +
           `• Interfaz intuitiva\n` +
           `• Uso de datos en tiempo real\n` +
           `• Conexión rápida y estable`;
  },

  // ==========================================================================
  // 👤 AYUDA USUARIO
  // ==========================================================================
  
  HELP_USER_PROFILE: () => {
    return `👤 *AYUDA - PERFIL DE USUARIO*\n\n` +
           `${constants.EMOJI.POINT_RIGHT} *Qué puedes hacer en tu perfil:*\n\n` +
           
           `${constants.EMOJI.ID} *Información personal:*\n` +
           `• Ver tu ID de Telegram\n` +
           `• Nombre de usuario\n` +
           `• Fecha de registro\n` +
           `• Estado de cuenta\n\n` +
           
           `${constants.EMOJI.VPN} *VPN Activas:*\n` +
           `• Lista de conexiones WireGuard\n` +
           `• Lista de claves Outline\n` +
           `• Estado de cada VPN (activa/suspendida)\n` +
           `• Uso de datos en tiempo real\n\n` +
           
           `${constants.EMOJI.CHART} *Estadísticas:*\n` +
           `• Datos consumidos este mes\n` +
           `• Porcentaje de cuota usado\n` +
           `• Tiempo de conexión\n` +
           `• Historial de uso`;
  },

  HELP_USER_QUOTA: () => {
    return `📊 *AYUDA - CUOTAS Y LÍMITES*\n\n` +
           `${constants.EMOJI.POINT_RIGHT} *Límites establecidos:*\n\n` +
           
           `${constants.EMOJI.VPN} *WireGuard:*\n` +
           `• 10 GB mensuales por defecto\n` +
           `• Renovación automática cada mes\n` +
           `• Notificación al 80% de uso\n` +
           `• Suspensión automática al 100%\n\n` +
           
           `${constants.EMOJI.SERVER} *Outline:*\n` +
           `• 10 GB mensuales por defecto\n` +
           `• Renovación automática cada mes\n` +
           `• Notificación al 80% de uso\n` +
           `• Suspensión automática al 100%\n\n` +
           
           `${constants.EMOJI.POINT_RIGHT} *Cómo revisar tu cuota:*\n` +
           `1. Usa ${markdown.code('/user')}\n` +
           `2. Selecciona "Mi Perfil"\n` +
           `3. Verás el uso actual de cada VPN\n\n` +
           
           `${constants.EMOJI.POINT_RIGHT} *Qué pasa si excedes:*\n` +
           `• La VPN afectada se suspenderá\n` +
           `• Recibirás una notificación\n` +
           `• Podrás solicitar más datos al admin\n` +
           `• Se reiniciará automáticamente el próximo mes`;
  },

  // ==========================================================================
  // 🛠️ AYUDA TÉCNICA
  // ==========================================================================
  
  HELP_TROUBLESHOOTING: () => {
    return `🔧 *SOLUCIÓN DE PROBLEMAS*\n\n` +
           `${constants.EMOJI.POINT_RIGHT} *Problemas comunes y soluciones:*\n\n` +
           
           `${constants.EMOJI.PROBLEM} *WireGuard no conecta:*\n` +
           `1. Verifica la configuración copiada\n` +
           `2. Reinicia la app WireGuard\n` +
           `3. Asegúrate de tener Internet\n` +
           `4. Intenta desde otra red\n` +
           `5. Contacta al admin si persiste\n\n` +
           
           `${constants.EMOJI.PROBLEM} *Outline no funciona:*\n` +
           `1. Asegúrate de usar la app oficial\n` +
           `2. Verifica que el enlace sea correcto\n` +
           `3. Reinstala la app si es necesario\n` +
           `4. Intenta desde otra red\n` +
           `5. Solicita una nueva clave\n\n` +
           
           `${constants.EMOJI.PROBLEM} *Sin acceso a Internet con VPN:*\n` +
           `1. Verifica que la VPN esté activa\n` +
           `2. Prueba sin VPN primero\n` +
           `3. Cambia de red DNS\n` +
           `4. Contacta a tu proveedor de Internet\n\n` +
           
           `${constants.EMOJI.PROBLEM} *Lentitud con VPN:*\n` +
           `1. Prueba el otro tipo de VPN\n` +
           `2. Cambia de red (WiFi/4G)\n` +
           `3. Verifica la carga del servidor\n` +
           `4. Contacta al admin para optimización`;
  },

  HELP_SECURITY: () => {
    return `🛡️ *SEGURIDAD Y PRIVACIDAD*\n\n` +
           `${constants.EMOJI.POINT_RIGHT} *Cómo protegemos tu privacidad:*\n\n` +
           
           `${constants.EMOJI.SHIELD} *Encriptación:*\n` +
           `• WireGuard: ChaCha20, Poly1305, Curve25519\n` +
           `• Outline: AES-256-GCM, ChaCha20-Poly1305\n` +
           `• Perfect Forward Secrecy (PFS)\n` +
           `• Handshakes de 1 RTT\n\n` +
           
           `${constants.EMOJI.DATA} *Política de datos:*\n` +
           `• No guardamos logs de conexión\n` +
           `• No monitoreamos tu tráfico\n` +
           `• Solo registramos uso total para cuotas\n` +
           `• Tus datos son anónimos\n\n` +
           
           `${constants.EMOJI.SETTINGS} *Recomendaciones de seguridad:*\n` +
           `• Usa contraseñas seguras en tus cuentas\n` +
           `• Mantén tus apps actualizadas\n` +
           `• No compartas tus configuraciones\n` +
           `• Reporta comportamientos sospechosos`;
  },

  // ==========================================================================
  // 👮 AYUDA ADMINISTRADOR
  // ==========================================================================
  
  HELP_ADMIN: () => {
    return `👮 *AYUDA PARA ADMINISTRADORES*\n\n` +
           `${constants.EMOJI.POINT_RIGHT} *Comandos exclusivos:*\n\n` +
           
           `${markdown.code('/admin users')} - Gestionar usuarios\n` +
           `• Ver todos los usuarios\n` +
           `• Agregar/eliminar usuarios\n` +
           `• Cambiar roles (user/admin)\n` +
           `• Suspender/activar cuentas\n\n` +
           
           `${markdown.code('/admin stats')} - Estadísticas del sistema\n` +
           `• Usuarios activos/totales\n` +
           `• Uso de VPN por tipo\n` +
           `• Consumo de ancho de banda\n` +
           `• Estado de los servidores\n\n` +
           
           `${markdown.code('/admin broadcast')} - Enviar anuncios\n` +
           `• Mensaje a todos los usuarios\n` +
           `• Mensaje con foto\n` +
           `• Filtrar por tipo de usuario\n` +
           `• Programar anuncios\n\n` +
           
           `${markdown.code('/admin system')} - Control del sistema\n` +
           `• Reiniciar servicios\n` +
           `• Ver logs en tiempo real\n` +
           `• Backup de datos\n` +
           `• Actualizar configuración`;
  },

  // ==========================================================================
  // 📞 CONTACTO Y SOPORTE
  // ==========================================================================
  
  HELP_CONTACT: () => {
    return `📞 *CONTACTO Y SOPORTE*\n\n` +
           `${constants.EMOJI.POINT_RIGHT} *Cómo obtener ayuda:*\n\n` +
           
           `${constants.EMOJI.SUPPORT} *Soporte técnico:*\n` +
           `• Usa este bot para reportar problemas\n` +
           `• Los admins recibirán tu solicitud\n` +
           `• Respuesta en 24 horas máximo\n` +
           `• Incluye detalles del problema\n\n` +
           
           `${constants.EMOJI.EMAIL} *Contacto administrativo:*\n` +
           `• Para solicitudes de acceso\n` +
           `• Aumento de cuota\n` +
           `• Problemas de facturación\n` +
           `• Sugerencias y feedback\n\n` +
           
           `${constants.EMOJI.DOCUMENT} *Documentación adicional:*\n` +
           `• Guías detalladas en el sitio web\n` +
           `• FAQs actualizadas\n` +
           `• Tutoriales en video\n` +
           `• Comunidad de usuarios`;
  },

  // ==========================================================================
  // 🎯 MENSAJES DE NAVEGACIÓN
  // ==========================================================================
  
  HELP_SECTION_NOT_FOUND: (section) => {
    return `❌ *Sección no encontrada*\n\n` +
           `La sección "${markdown.escapeMarkdown(section)}" no existe.\n\n` +
           `Usa los botones de abajo para navegar por las categorías de ayuda.`;
  },

  HELP_BACK_TO_MAIN: () => {
    return `↩️ *Volviendo al menú principal de ayuda...*`;
  },

  HELP_CLOSED: () => {
    return `👌 *Centro de ayuda cerrado*\n\n` +
           `Puedes volver a abrirlo con ${markdown.code('/help')} en cualquier momento.`;
  }
};