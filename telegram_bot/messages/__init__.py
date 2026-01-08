# Legacy imports for backward compatibility
from .messages import Messages

# New modular message classes
from .user_messages import UserMessages
from .admin_messages import AdminMessages
from .operations_messages import OperationMessages
from .support_messages import SupportMessages, TaskMessages, AchievementMessages
from .common_messages import CommonMessages
from .shop_messages import ShopMessages

# Factory and utilities
from .message_factory import (
    MessageFactory,
    MessageBuilder,
    MessageRegistry,
    MessageFormatter,
    MessageType,
    MessageCategory,
)

__all__ = [
    # Legacy
    'Messages',
    
    # Feature-based message classes
    'UserMessages',
    'AdminMessages',
    'OperationMessages',
    'SupportMessages',
    'TaskMessages',
    'AchievementMessages',
    'CommonMessages',
    'ShopMessages',
    
    # Factory and utilities
    'MessageFactory',
    'MessageBuilder',
    'MessageRegistry',
    'MessageFormatter',
    'MessageType',
    'MessageCategory',
]
