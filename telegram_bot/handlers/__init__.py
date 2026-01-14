"""
Handlers package for uSipipo VPN Manager Bot.

This package contains the handler initializer that centralizes
all Telegram bot handlers across different features.

Author: uSipipo Team
Version: 2.0.0
"""

from .handler_initializer import initialize_handlers

__all__ = ['initialize_handlers']
