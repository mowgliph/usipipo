# 🛡️ uSipipo VPN Bot

Sistema integrado para gestión de conexiones VPN (WireGuard + Outline) con bloqueo de anuncios mediante Pi-hole. Incluye bot de Telegram para auto-servicio de configuraciones.

![Arquitectura](https://img.shields.io/badge/Arquitectura-Cliente/Servidor-blue?style=flat)
![Licencia](https://img.shields.io/badge/Licencia-MIT-green?style=flat)

## 📦 Componentes

- **Pi-hole**: Servidor DNS para bloqueo de anuncios
- **WireGuard**: VPN de alto rendimiento
- **Outline**: Sistema de acceso remoto
- **Bot de Telegram**: Gestión automática de conexiones

## ⚙️ Requisitos

- Servidor VPS con Ubuntu 22.04 LTS (mínimo 2GB RAM)
- Node.js 18+
- Acceso root al servidor
- Bot de Telegram creado en [@BotFather](https://t.me/BotFather)

## 🔐 Seguridad

- Solo usuarios autorizados pueden generar configuraciones
- Aislamiento completo entre servicios
- Claves efímeras para cada conexión
- Firewall estricto por defecto

## 🤖 Uso del Bot

1. Inicia conversación con el bot
2. Selecciona tipo de VPN (WireGuard u Outline)
3. Recibe configuración automáticamente:
   - WireGuard: Archivo `.conf` + código QR
   - Outline: Enlace de conexión listo para copiar

## 📄 Licencia

Distribuido bajo licencia MIT. Ver [LICENSE](LICENSE) para detalles.

