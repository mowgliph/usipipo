# Guía de Configuración: Pagos Lightning con BTCPay Server y OpenNode

## Tabla de Contenidos
- [Introducción](#introducción)
- [Configuración de BTCPay Server](#configuración-de-btcpay-server)
- [Configuración de OpenNode](#configuración-de-opennode)
- [Variables de Entorno Requeridas](#variables-de-entorno-requeridas)
- [Buenas Prácticas de Seguridad](#buenas-prácticas-de-seguridad)

## Introducción

Esta guía te ayudará a configurar los servicios de pago Lightning Network (BTCPay Server y OpenNode) para tu aplicación. Ambos servicios permiten aceptar pagos en Bitcoin a través de la red Lightning.

## Configuración de BTCPay Server

### 1. Creación de Cuenta
1. Regístrate en [btcpayserver.org](https://btcpayserver.org/)
2. Verifica tu correo electrónico y completa el proceso de registro

### 2. Configuración de la Tienda
1. Inicia sesión en tu panel de control de BTCPay Server
2. Navega a "Tiendas" en el menú lateral
3. Crea una nueva tienda o selecciona una existente
4. Configura la moneda, descuentos y otras preferencias según sea necesario

### 3. Obtención de Credenciales
1. **BTCPAY_URL**: 
   - Es la URL de tu instancia de BTCPay Server (ej: `https://tudominio.btcpayserver.com`)

2. **BTCPAY_STORE_ID**:
   - Ve a la configuración de tu tienda
   - El ID de la tienda se muestra en la URL o en la sección de configuración

3. **BTCPAY_API_KEY**:
   - Navega a "API Keys" en el menú de usuario
   - Haz clic en "Crear nueva clave API"
   - Selecciona los permisos necesarios (mínimo: `btcpay.store.canviewinvoices` y `btcpay.store.cancreateinvoice`)
   - Copia la clave generada y guárdala de forma segura

## Configuración de OpenNode

### 1. Creación de Cuenta
1. Regístrate en [opennode.com](https://www.opennode.com/)
2. Completa el proceso de verificación de identidad (KYC/AML)

### 2. Obtención de la Clave API
1. Inicia sesión en tu cuenta de OpenNode
2. Navega a "Developers" o "API Keys" en el menú de configuración
3. Haz clic en "Generate New Key"
4. Asigna un nombre descriptivo a la clave
5. Selecciona los permisos necesarios (mínimo: `create_charge` y `read_charge`)
6. Copia la clave generada y guárdala de forma segura
   - Esta será tu `OPENNODE_API_KEY`

## Variables de Entorno Requeridas

Asegúrate de configurar las siguientes variables de entorno en tu servidor de producción:

```env
# BTCPay Server
BTCPAY_URL=tu_url_de_btcpay
BTCPAY_API_KEY=tu_api_key_de_btcpay
BTCPAY_STORE_ID=tu_store_id_de_btcpay

# OpenNode
OPENNODE_API_KEY=tu_api_key_de_opennode
```

## Buenas Prácticas de Seguridad

1. **Protección de Claves**:
   - Nunca guardes las claves API en el código fuente
   - No las subas a repositorios públicos
   - Utiliza variables de entorno o un gestor de secretos

2. **Seguridad de la Cuenta**:
   - Habilita la autenticación de dos factores (2FA) en ambas plataformas
   - Usa contraseñas fuertes y únicas
   - Revisa regularmente los accesos y actividades sospechosas

3. **Permisos Mínimos**:
   - Otorga solo los permisos necesarios a las claves API
   - Revisa y actualiza los permisos periódicamente

4. **Monitoreo**:
   - Configura alertas para transacciones sospechosas
   - Monitorea regularmente los pagos recibidos

5. **Copia de Seguridad**:
   - Mantén copias de seguridad seguras de tus claves API
   - Ten un plan de recuperación en caso de pérdida de acceso

## Soporte

- **BTCPay Server**: [Documentación oficial](https://docs.btcpayserver.org/)
- **OpenNode**: [Documentación de la API](https://developers.opennode.com/)

---

*Última actualización: Octubre 2025*
