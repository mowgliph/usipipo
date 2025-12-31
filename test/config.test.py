from config import settings

def test_config():
    """Verifica que la configuración esté completa"""
    
    print("🔍 Verificando configuración...\n")
    
    # Test 1: Campos requeridos
    assert settings.SECRET_KEY, "❌ SECRET_KEY faltante"
    assert settings.TELEGRAM_TOKEN, "❌ TELEGRAM_TOKEN faltante"
    assert settings.SUPABASE_URL, "❌ SUPABASE_URL faltante"
    print("✅ Campos requeridos presentes")
    
    # Test 2: Protocolos VPN
    protocols = settings.get_vpn_protocols()
    print(f"✅ Protocolos disponibles: {protocols}")
    assert len(protocols) > 0, "❌ No hay protocolos VPN configurados"
    
    # Test 3: Directorios
    from pathlib import Path
    assert Path(settings.TEMP_PATH).exists(), "❌ TEMP_PATH no existe"
    assert Path(settings.QR_CODE_PATH).exists(), "❌ QR_CODE_PATH no existe"
    print("✅ Directorios creados correctamente")
    
    # Test 4: ADMIN_ID en AUTHORIZED_USERS
    assert settings.ADMIN_ID in settings.AUTHORIZED_USERS, "❌ ADMIN_ID no está en AUTHORIZED_USERS"
    print("✅ ADMIN_ID autorizado correctamente")
    
    # Test 5: Configuración segura
    safe_dump = settings.model_dump_safe()
    assert safe_dump["SECRET_KEY"] == "***HIDDEN***", "❌ SECRET_KEY expuesto"
    print("✅ Secretos protegidos en dumps")
    
    print("\n🎉 Todos los tests pasaron correctamente")

if __name__ == "__main__":
    test_config()
