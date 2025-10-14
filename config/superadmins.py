# config/superadmins.py
"""
Define los IDs de Telegram que serán reconocidos automáticamente como superadmins
al ejecutar /start por primera vez.
"""

# 🧑‍💻 Lista de IDs de Telegram con privilegios de superadmin
SUPERADMINS = [
    1058749165,  
    # Puedes añadir más IDs si deseas múltiples superadmins iniciales
]

def is_superadmin_tg(tg_id: int) -> bool:
    """
    Verifica si el ID de Telegram pertenece a la lista de superadmins automáticos.
    """
    return tg_id in SUPERADMINS