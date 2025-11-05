# 🐙 uSipipo

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**uSipipo** is a pure Python tool that operates as a **Telegram bot** for managing VPN configurations (WireGuard and Outline) and MTProto proxies directly from the same VPS where the bot is hosted.

This project is designed to facilitate the creation of access keys, including **7-day free trials**, and offer paid VPN configurations through **Telegram Stars** and **QvaPay** (cryptocurrencies).

## 🏗️ Project Architecture

uSipipo follows a modular and scalable architecture based on the **models-crud-services-handlers** pattern:

- **models**: SQLAlchemy model definitions with static typing
- **crud**: Database operations (queries, insertions, updates)
- **services**: Business logic and external API integrations
- **handlers**: Telegram command and callback controllers

## 🔓 Key Features

- ✅ Automatic generation of **WireGuard** and **Outline** configurations
- 🎁 **7-day free trials**
- 💸 Payment system with **Telegram Stars**
- 💳 Payment system with **QvaPay** (cryptocurrencies)
- 🔄 Management of **MTProto proxies** for Telegram
- 🤖 Everything managed from a **Telegram bot**
- 🛠️ Modular, maintainable, and extensible code
- 📊 Centralized auditing and logging system
- 🔐 Role and permission management
- 📦 **Open Source** repository maintained by [mowgliph](https://github.com/mowgliph)

## 🛠️ Technologies

- **Python 3.11+**
- **python-telegram-bot** for Telegram integration
- **SQLAlchemy** for ORM
- **MariaDB** for database
- **WireGuard** and **Outline** for VPN
- **MTProto** for proxies
- **QvaPay** and **Telegram Stars** for payments

## 📦 Installation

See [docs/INSTALL.md](docs/INSTALL.md) for detailed installation instructions.

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for code style
- Use type hints in all functions
- Write tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for more details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/mowgliph/usipipo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mowgliph/usipipo/discussions)

---

**Thank you for using uSipipo!** 🐙
