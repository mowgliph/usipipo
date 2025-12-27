"""
Configuración central de la aplicación uSipipo VPN Manager.
Todas las variables se cargan desde el archivo .env
"""
import os
from typing import List, Optional
from pydantic import field_validator, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # =========================================================================
    # Configuración Base
    # =========================================================================
    PROJECT_NAME: str = "uSipipo VPN Manager"
    APP_ENV: str = "development" # development | production
    
    # =========================================================================
    # Security & API
    # =========================================================================
    SECRET_KEY: str
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    # Pydantic parsea automáticamente strings separados por comas a listas
    CORS_ORIGINS: List[str] = ["*"] 
    
    # =========================================================================
    # Telegram Bot
    # =========================================================================
    TELEGRAM_TOKEN: str
    AUTHORIZED_USERS: List[int] = [] # Ejemplo en .env: 12345,67890

    # =========================================================================
    # Supabase (Database)
    # =========================================================================
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    
    # =========================================================================
    # VPN Network Info
    # =========================================================================
    SERVER_IP: str # IP Pública del VPS
    
    # WireGuard
    WG_SERVER_PRIVKEY: Optional[str] = None
    WG_SERVER_PORT: int = 51820
    WG_INTERFACE: str = "wg0"
    
    # Outline
    OUTLINE_API_URL: Optional[str] = None
    OUTLINE_CERT_SHA256: Optional[str] = None

    # =========================================================================
    # Paths & System
    # =========================================================================
    LOG_LEVEL: str = "INFO"
    TEMP_PATH: str = "./temp"
    QR_CODE_PATH: str = "./static/qr_codes"
    CLIENT_CONFIGS_PATH: str = "./static/configs"

    # Configuración de Pydantic para leer .env
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore", # Ignorar variables extra en .env que no estén aquí
        case_sensitive=True
    )

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"

    @field_validator("AUTHORIZED_USERS", mode="before")
    @classmethod
    def parse_list_int(cls, v):
        """Parsea '123,456' a [123, 456] si viene como string del .env"""
        if isinstance(v, str) and v.strip():
            return [int(x) for x in v.split(",") if x.strip().isdigit()]
        return v if isinstance(v, list) else []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_list_str(cls, v):
        if isinstance(v, str) and v.strip():
            return [x.strip() for x in v.split(",")]
        return v if isinstance(v, list) else []

# Instancia Global
# Al instanciar, Pydantic lee el .env y lanza error si falta algo requerido (como SECRET_KEY)
try:
    settings = Settings()
except Exception as e:
    print("❌ Error crítico de configuración (Revisa tu .env):")
    print(e)
    exit(1)
