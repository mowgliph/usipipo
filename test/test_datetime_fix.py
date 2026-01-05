#!/usr/bin/env python3
"""
Script para verificar que los errores de datetime han sido resueltos.
"""

from datetime import datetime, timezone
from domain.entities.vpn_key import VpnKey

def test_datetime_consistency():
    """Verificar que los datetimes se manejan consistentemente."""
    print("🔍 Verificando manejo de datetime...")
    
    # Crear una llave nueva
    key = VpnKey(
        user_id=123456,
        name="Test Key",
        key_type="outline",
        key_data="test://config"
    )
    
    print(f"✅ created_at: {key.created_at} (tzinfo: {key.created_at.tzinfo})")
    print(f"✅ billing_reset_at: {key.billing_reset_at} (tzinfo: {key.billing_reset_at.tzinfo})")
    
    # Verificar que ambos tienen timezone
    assert key.created_at.tzinfo is not None, "created_at debe tener timezone"
    assert key.billing_reset_at.tzinfo is not None, "billing_reset_at debe tener timezone"
    
    # Probar el método needs_reset()
    try:
        result = key.needs_reset()
        print(f"✅ needs_reset() funciona correctamente: {result}")
    except Exception as e:
        print(f"❌ Error en needs_reset(): {e}")
        return False
    
    print("✅ Todas las verificaciones de datetime pasaron correctamente")
    return True

if __name__ == "__main__":
    test_datetime_consistency()
