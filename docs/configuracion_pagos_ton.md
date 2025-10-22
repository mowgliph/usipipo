# Guía de Configuración: Pagos con TON

## Tabla de Contenidos
- [Introducción](#introducción)
- [Configuración de TON API](#configuración-de-ton-api)
- [Configuración de Billetera TON](#configuración-de-billetera-ton)
- [Variables de Entorno Requeridas](#variables-de-entorno-requeridas)
- [Solución de Problemas](#solución-de-problemas)
- [Buenas Prácticas de Seguridad](#buenas-prácticas-de-seguridad)

## Introducción

Esta guía te ayudará a configurar los pagos con TON (The Open Network) para tu aplicación. El sistema utiliza TON API como proveedor principal con un fallback a ton.py.

## Configuración de TON API

### 1. Creación de Cuenta
1. Regístrate en [tonapi.io](https://tonapi.io/)
2. Verifica tu correo electrónico

### 2. Obtención de la Clave API
1. Inicia sesión en tu cuenta de TON API
2. Navega a la sección de "API Keys"
3. Haz clic en "Generate New Key"
4. Configura los permisos necesarios:
   - `wallet.send` (para crear transacciones)
   - `wallet.getAddress` (para verificar direcciones)
5. Copia la clave generada

## Configuración de Billetera TON

### 1. Elección de Billetera
Se recomienda usar una de estas opciones:
- **Tonkeeper** ([tonkeeper.com](https://tonkeeper.com/))
- **OpenMask** ([openmask.app](https://openmask.app/))
- **TON Wallet** ([ton.org/wallets](https://ton.org/wallets))

### 2. Creación de Billetera
1. Descarga e instala la billetera elegida
2. Crea una nueva billetera
3. **IMPORTANTE**: Guarda la frase de recuperación en un lugar seguro
4. Copia la dirección de tu billetera (empieza con "EQ..." o "UQ...")

## Variables de Entorno Requeridas

Configura las siguientes variables en tu archivo `.env`:

```env
# TON Payments
TONAPI_KEY=tu_api_key_de_tonapi
TONAPI_URL=https://tonapi.io/v2
TON_WALLET_ADDRESS=tu_direccion_ton
```

## Solución de Problemas

### Error: "TONAPI_KEY not configured"
- Verifica que la variable de entorno `TONAPI_KEY` esté configurada correctamente
- Asegúrate de que la clave API tenga los permisos necesarios
- Verifica que la URL de TON API sea accesible desde tu servidor

### Error: Invalid wallet address
- Verifica que la dirección de la billetera sea válida
- Asegúrate de que la dirección pertenezca a la red principal de TON

## Buenas Prácticas de Seguridad

1. **Protección de Claves API**:
   - Nunca expongas `TONAPI_KEY` en el código fuente
   - Usa variables de entorno o un gestor de secretos
   - Regenera las claves periódicamente

2. **Seguridad de la Billetera**:
   - Usa una billetera dedicada solo para depósitos
   - Mantén la mayoría de los fondos en una billetera fría
   - Habilita la autenticación de dos factores si está disponible

3. **Monitoreo**:
   - Configura alertas para transacciones entrantes
   - Monitorea regularmente el saldo de la billetera
   - Revisa los logs de la aplicación frecuentemente

## Recursos Adicionales

- [Documentación de TON API](https://tonapi.io/docs)
- [Guía de Seguridad de TON](https://ton.org/security)
- [Foro de la Comunidad TON](https://t.me/tondev_eng)

---

*Última actualización: Octubre 2025*
