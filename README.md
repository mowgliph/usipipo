# 🐙 uSipipo

**uSipipo** es una herramienta desarrollada en **Python puro** que funciona como un **bot de Telegram** para gestionar configuraciones de VPN (WireGuard y Outline) y proxies MTProto directamente desde el mismo VPS donde se aloja el bot.

Este proyecto está diseñado para facilitar la creación de claves de acceso, incluyendo **pruebas gratuitas de 7 días**, y ofrecer configuraciones de VPN de pago mediante **Estrellas de Telegram** y **QvaPay** (criptomonedas).

---

## 🏗️ Arquitectura del Proyecto

uSipipo sigue una arquitectura modular y escalable basada en el patrón **models-crud-services-handlers**:

- **models**: Definición de modelos SQLAlchemy con tipado estático
- **crud**: Operaciones de base de datos (consultas, inserciones, actualizaciones)
- **services**: Lógica de negocio y integración con APIs externas
- **handlers**: Controladores de comandos y callbacks de Telegram

---

## 🔓 Características principales

- ✅ Generación automática de configuraciones **WireGuard** y **Outline**
- 🎁 Pruebas gratuitas de **7 días**
- 💸 Sistema de pagos con **Estrellas de Telegram**
- 💳 Sistema de pagos con **QvaPay** (criptomonedas)
- 🔄 Gestión de **proxies MTProto** para Telegram
- 🤖 Todo gestionado desde un **bot de Telegram**
- 🛠️ Código modular, mantenible y extensible
- 📊 Sistema de auditoría y logs centralizados
- 🔐 Gestión de roles y permisos
- 📦 Repositorio **Open Source** mantenido por [mowgliph](https://github.com/mowgliph)

---

## 🔒 Seguridad y Mejores Prácticas

- **Logs Centralizados**: Todos los eventos se registran con contexto de usuario
- **Validación de Datos**: Constraints a nivel de base de datos y aplicación
- **Gestión de Permisos**: Sistema de roles para acceso granular
- **Auditoría**: Registro completo de todas las operaciones
- **Rate Limiting**: Protección contra abuso en handlers
- **Secrets Management**: Variables sensibles en archivos .env

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Guías de Desarrollo
- Seguir PEP 8 para estilo de código
- Usar type hints en todas las funciones
- Escribir tests para nuevas funcionalidades
- Actualizar documentación

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/mowgliph/usipipo/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/mowgliph/usipipo/discussions)
- **Email**: mowgliph@github.com

---

**¡Gracias por usar uSipipo!** 🐙

