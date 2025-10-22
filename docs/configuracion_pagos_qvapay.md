# Configuración de Pagos con QvaPay

## Introducción a QvaPay

QvaPay es una plataforma de pago en criptomonedas que permite realizar transacciones rápidas y seguras. En uSipipo, hemos integrado QvaPay como una opción adicional de pago para adquirir servicios VPN, ofreciendo a los usuarios más flexibilidad en sus métodos de pago.

## Requisitos Previos

Antes de poder utilizar QvaPay para pagar servicios VPN, necesitas:

1. Tener una cuenta en [QvaPay](https://qvapay.com)
2. Tener fondos suficientes en tu cuenta QvaPay
3. Tener un bot de Telegram con uSipipo instalado y configurado
4. Contar con credenciales de API de QvaPay (APP ID y USER ID)

## Configuración Paso a Paso

### 1. Obtener Credenciales de QvaPay

1. Accede a tu cuenta en [QvaPay](https://qvapay.com)
2. Ve a la sección de "Aplicaciones" o "Apps"
3. Crea una nueva aplicación para obtener tu:
   - **APP ID**: Identificador único de tu aplicación
   - **USER ID**: Tu identificador de usuario en QvaPay

### 2. Configurar Variables de Entorno

Agrega las siguientes variables a tu archivo `.env`:

```env
# QvaPay
QVAPAY_APP_ID=tu_app_id_aqui
QVAPAY_API_KEY=tu_api_key_aqui
QVAPAY_BASE_URL=https://qvapay.com/api/v1
QVAPAY_TIMEOUT=30
```

### 3. Vincular Cuenta QvaPay al Bot

Para vincular tu cuenta QvaPay al bot de Telegram:

1. Inicia una conversación con tu bot
2. Ejecuta el comando `/qvapay`
3. Selecciona "Vincular Cuenta"
4. Ingresa tu **APP ID** cuando se te solicite
5. Ingresa tu **USER ID** cuando se te solicite
6. El bot verificará tus credenciales y mostrará tu balance actual

## Comandos Disponibles

### `/qvapay`

Muestra el menú principal de gestión de QvaPay con las siguientes opciones:

- **Ver Balance**: Consulta tu balance actual en QvaPay
- **Cambiar Cuenta**: Permite actualizar tus credenciales de QvaPay
- **Desvincular**: Desconecta tu cuenta de QvaPay del bot
- **Vincular Cuenta**: (Si no tienes cuenta vinculada) Inicia el proceso de vinculación

### `/newvpn`

Crea una nueva VPN con pago mediante QvaPay:

```
/newvpn <tipo> <meses>
```

Ejemplo:
```
/newvpn wireguard 3
```

Al ejecutar este comando, se mostrará una interfaz con opciones de pago donde podrás seleccionar "Pagar con QvaPay" si tienes tu cuenta vinculada.

## Flujo de Pago Detallado

1. **Solicitud de Servicio**: El usuario ejecuta `/newvpn wireguard 3`
2. **Selección de Método de Pago**: El bot muestra opciones de pago (Estrellas de Telegram y QvaPay)
3. **Verificación de Cuenta**: Si se selecciona QvaPay, el bot verifica que la cuenta esté vinculada
4. **Verificación de Balance**: El bot consulta el balance del usuario en QvaPay
5. **Procesamiento del Pago**: Si hay fondos suficientes, se procesa el pago automáticamente
6. **Activación del Servicio**: Una vez confirmado el pago, se crea y entrega la configuración VPN al usuario

## Manejo de Errores Comunes

### "Credenciales inválidas"

- Verifica que tu APP ID y USER ID sean correctos
- Asegúrate de haberlos obtenido de la sección correcta en QvaPay
- Comprueba que no haya espacios adicionales al ingresarlos

### "Balance insuficiente"

- Recarga fondos en tu cuenta QvaPay
- Verifica que tengas la moneda correcta (USD) en tu balance
- Confirma el monto requerido para el servicio que deseas adquirir

### "Error procesando pago"

- Intenta nuevamente después de unos minutos
- Verifica tu conexión a internet
- Contacta al soporte si el problema persiste

## Preguntas Frecuentes

### ¿Es seguro vincular mi cuenta QvaPay al bot?

Sí, el bot solo almacena tu APP ID y USER ID de forma segura en la base de datos. No se almacenan claves privadas ni información sensible.

### ¿Puedo desvincular mi cuenta en cualquier momento?

Sí, puedes desvincular tu cuenta QvaPay en cualquier momento desde el menú `/qvapay`.

### ¿Qué monedas soporta QvaPay en uSipipo?

Actualmente se soporta USD como moneda principal para los pagos de servicios VPN.

### ¿Qué pasa si tengo problemas con un pago?

El sistema registra todas las transacciones. Si tienes problemas, contacta al administrador del bot proporcionando detalles de la transacción.

## Seguridad y Privacidad

- Las credenciales de QvaPay se almacenan de forma cifrada en la base de datos
- Las comunicaciones con la API de QvaPay se realizan mediante HTTPS
- El bot no almacena información de transacciones más allá del necesario para el funcionamiento del servicio
- Los usuarios pueden desvincular sus cuentas en cualquier momento

## Soporte

Si encuentras problemas con la integración de QvaPay:

1. Verifica que todas las variables de entorno estén correctamente configuradas
2. Asegúrate de tener la última versión de uSipipo
3. Revisa los logs del bot para identificar errores específicos
4. Contacta al soporte técnico proporcionando detalles del problema