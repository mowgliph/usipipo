"""
Configuración central de la aplicación uSipipo VPN Manager.
Gestiona variables de entorno con validación estricta y valores seguros por defecto.

Author: uSipipo Team
Version: 2.0.0
Last Updated: 2025-12-31
"""

import os
import secrets
from typing import List, Optional, Union
from pathlib import Path

from pydantic import (
    Field,
    field_validator,
    model_validator,
    AnyHttpUrl,
    PostgresDsn,
    validator
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración centralizada con validación automática.
    Todas las variables se cargan desde .env con valores por defecto seguros.
    """
    
    # =========================================================================
    # APLICACIÓN BASE
    # =========================================================================
    PROJECT_NAME: str = Field(
        default="uSipipo VPN Manager",
        description="Nombre del proyecto"
    )
    
    APP_ENV: str = Field(
        default="development",
        description="Entorno de ejecución: development | production | staging"
    )
    
    NODE_ENV: str = Field(
        default="production",
        description="Modo de Node.js (si aplica)"
    )
    
    DEFAULT_LANG: str = Field(
        default="es",
        description="Idioma por defecto de la aplicación"
    )
    
    # =========================================================================
    # SEGURIDAD Y API
    # =========================================================================
    SECRET_KEY: str = Field(
        ...,  # Campo REQUERIDO
        min_length=32,
        description="Clave secreta para JWT y encriptación (generada con openssl rand -hex 32)"
    )
    
    ALGORITHM: str = Field(
        default="HS256",
        description="Algoritmo de firma JWT"
    )
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        ge=5,
        le=1440,
        description="Tiempo de expiración del token en minutos"
    )
    
    API_HOST: str = Field(
        default="0.0.0.0",
        description="Host donde escucha la API"
    )
    
    API_PORT: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="Puerto de la API"
    )
    
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="Orígenes permitidos para CORS (usar dominios específicos en producción)"
    )
    
    # =========================================================================
    # TELEGRAM BOT
    # =========================================================================
    TELEGRAM_TOKEN: str = Field(
        ...,  # REQUERIDO
        min_length=30,
        description="Token del bot de Telegram obtenido de @BotFather"
    )
    
    AUTHORIZED_USERS: List[int] = Field(
        default_factory=list,
        description="Lista de IDs de usuarios autorizados para gestionar el bot"
    )
    
    ADMIN_ID: int = Field(
        ...,  # REQUERIDO
        description="ID de Telegram del administrador principal"
    )
    
    ADMIN_EMAIL: Optional[str] = Field(
        default=None,
        description="Email del administrador (opcional)"
    )
    
    TELEGRAM_RATE_LIMIT: int = Field(
        default=30,
        ge=1,
        description="Límite de peticiones por minuto por usuario en Telegram"
    )

    BOT_USERNAME: str = Field(
        default="usipipo_bot",
        description="Nombre de usuario del bot de Telegram (sin @)"
    )

    TELEGRAM_WEBHOOK_URL: Optional[str] = Field(
        default=None,
        description="URL del webhook de Telegram (opcional, usar polling por defecto)"
    )

    # =========================================================================
    # GROQ IA API
    # =========================================================================
    # GROQ_API_KEY: str = Field(
    #     default="",
    #     description="API Key de Groq para el asistente IA Sip"
    # )
    
    # GROQ_MODEL: str = Field(
    #     default="openai/gpt-oss-120b",
    #     description="Modelo de IA a usar en Groq (openai/gpt-oss-120b, llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768)"
    # )

    GROQ_API_KEY: str = Field(
        default="",
        description="API Key de Groq"
    )
    
    GROQ_MODEL: str = Field(
        default="openai/gpt-oss-120b",
        description="Modelo principal: openai/gpt-oss-120b"
    )

    GROQ_MAX_TOKENS: int = Field(
        default=4096, # Puedes subir esto si necesitas respuestas más largas
        description="Tokens máximos de respuesta"
    )
    
    GROQ_TEMPERATURE: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperatura para respuestas de IA (0.0 = determinista, 2.0 = creativo)"
    )
    
    # GROQ_MAX_TOKENS: int = Field(
    #     default=2000,
    #     ge=100,
    #     le=8000,
    #     description="Máximo de tokens en respuesta de IA (usado como max_completion_tokens)"
    # )
    
    GROQ_TIMEOUT: int = Field(
        default=30,
        ge=10,
        le=120,
        description="Timeout en segundos para peticiones a Groq API"
    )
    
    GROQ_MAX_RETRIES: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Número máximo de reintentos para peticiones fallidas"
    )
    
    # =========================================================================
    # SUPABASE / POSTGRESQL
    # =========================================================================
    SUPABASE_URL: str = Field(
        ...,  # REQUERIDO
        description="URL del proyecto de Supabase"
    )
    
    SUPABASE_SERVICE_KEY: str = Field(
        ...,  # REQUERIDO
        min_length=30,
        description="Service Role Key de Supabase (tiene privilegios totales)"
    )
    
    SUPABASE_SECRET_KEY: str = Field(
        ...,  # REQUERIDO
        description="Secret Key de Supabase"
    )
    
    SUPABASE_ANON_KEY: str = Field(
        ...,  # REQUERIDO
        description="Anon Key de Supabase"
    )
    
    SUPABASE_JWT_SECRET: str = Field(
        ...,  # REQUERIDO
        description="JWT Secret de Supabase"
    )
    
    DATABASE_URL: str = Field(
        ...,  # REQUERIDO
        description="URL completa de conexión PostgreSQL"
    )
    
    DB_POOL_SIZE: int = Field(
        default=10,
        ge=5,
        le=50,
        description="Tamaño del pool de conexiones a la base de datos"
    )
    
    DB_TIMEOUT: int = Field(
        default=30,
        ge=10,
        le=120,
        description="Timeout de conexión en segundos"
    )
    
    # =========================================================================
    # INFORMACIÓN DE RED DEL SERVIDOR
    # =========================================================================
    SERVER_IP: str = Field(
        ...,  # REQUERIDO
        description="IP pública principal del VPS"
    )
    
    SERVER_IPV4: str = Field(
        ...,  # REQUERIDO
        description="Dirección IPv4 pública"
    )
    
    SERVER_IPV6: Optional[str] = Field(
        default=None,
        description="Dirección IPv6 pública (opcional)"
    )
    
    # =========================================================================
    # WIREGUARD
    # =========================================================================
    WG_INTERFACE: str = Field(
        default="wg0",
        description="Nombre de la interfaz WireGuard"
    )
    
    WG_SERVER_IPV4: str = Field(
        default="10.88.88.1",
        description="IP interna del servidor WireGuard (IPv4)"
    )
    
    WG_SERVER_IPV6: str = Field(
        default="fd42:42:42::1",
        description="IP interna del servidor WireGuard (IPv6)"
    )
    
    WG_SERVER_PORT: int = Field(
        default=51820,
        ge=1024,
        le=65535,
        description="Puerto UDP de WireGuard"
    )
    
    WG_SERVER_PUBKEY: Optional[str] = Field(
        default=None,
        description="Clave pública del servidor WireGuard"
    )
    
    WG_SERVER_PRIVKEY: Optional[str] = Field(
        default=None,
        description="Clave privada del servidor WireGuard (CONFIDENCIAL)"
    )
    
    WG_ALLOWED_IPS: str = Field(
        default="0.0.0.0/0,::/0",
        description="IPs permitidas en configuraciones de clientes"
    )
    
    WG_PATH: str = Field(
        default="/etc/wireguard",
        description="Ruta de configuraciones de WireGuard"
    )
    
    WG_ENDPOINT: Optional[str] = Field(
        default=None,
        description="Endpoint público de WireGuard (se autoconstruye si no existe)"
    )
    
    WG_CLIENT_DNS_1: str = Field(
        default="1.1.1.1",
        description="DNS primario para clientes WireGuard"
    )
    
    WG_CLIENT_DNS_2: str = Field(
        default="1.0.0.1",
        description="DNS secundario para clientes WireGuard"
    )
    
    # =========================================================================
    # OUTLINE VPN (SHADOWBOX)
    # =========================================================================
    OUTLINE_API_URL: Optional[str] = Field(
        default=None,
        description="URL completa de la API de Outline (incluye secret)"
    )
    
    OUTLINE_CERT_SHA256: Optional[str] = Field(
        default=None,
        description="SHA256 del certificado autofirmado de Outline"
    )
    
    OUTLINE_API_PORT: Optional[int] = Field(
        default=None,
        ge=1024,
        le=65535,
        description="Puerto de la API de Outline"
    )
    
    OUTLINE_KEYS_PORT: Optional[int] = Field(
        default=None,
        ge=1024,
        le=65535,
        description="Puerto de acceso de clientes Outline"
    )
    
    OUTLINE_SERVER_IP: Optional[str] = Field(
        default=None,
        description="IP pública usada por Outline (normalmente igual a SERVER_IP)"
    )
    
    OUTLINE_DASHBOARD_URL: Optional[str] = Field(
        default=None,
        description="URL del dashboard de Outline Manager"
    )
    
    # =========================================================================
    # LÍMITES Y CUOTAS
    # =========================================================================
    VPN_KEY_EXPIRE_DAYS: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Días de validez de llaves VPN"
    )
    
    MAX_KEYS_PER_USER: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Máximo de llaves permitidas por usuario"
    )
    
    API_RATE_LIMIT: int = Field(
        default=60,
        ge=10,
        description="Límite de peticiones por minuto a la API"
    )
    
    # =========================================================================
    # SISTEMA DE PLANES Y REFERIDOS
    # =========================================================================
    FREE_PLAN_MAX_KEYS: int = Field(
        default=2,
        ge=1,
        description="Máximo de llaves para el plan gratuito"
    )
    
    FREE_PLAN_DATA_LIMIT_GB: int = Field(
        default=10,
        ge=1,
        description="Límite de datos por clave en GB para el plan gratuito"
    )
    
    VIP_PLAN_MAX_KEYS: int = Field(
        default=10,
        ge=1,
        description="Máximo de llaves para el plan VIP"
    )
    
    VIP_PLAN_DATA_LIMIT_GB: int = Field(
        default=50,
        ge=1,
        description="Límite de datos por clave en GB para el plan VIP"
    )
    
    VIP_PLAN_COST_STARS: int = Field(
        default=10,
        ge=1,
        description="Costo en Telegram Stars por mes de VIP"
    )
    
    REFERRAL_COMMISSION_PERCENT: int = Field(
        default=10,
        ge=0,
        le=100,
        description="Porcentaje de comisión por referidos (0-100)"
    )
    
    KEY_CLEANUP_DAYS: int = Field(
        default=90,
        ge=30,
        description="Días de inactividad para limpiar una clave"
    )
    
    BILLING_CYCLE_DAYS: int = Field(
        default=30,
        ge=1,
        description="Días del ciclo de facturación (reset de datos)"
    )
    
    MIN_DEPOSIT_FOR_DELETE: int = Field(
        default=1,
        ge=0,
        description="Depósito mínimo requerido para poder eliminar claves"
    )
    
    # =========================================================================
    # LOGGING Y MONITOREO
    # =========================================================================
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Nivel de logging: DEBUG | INFO | WARNING | ERROR | CRITICAL"
    )
    
    LOG_FILE_PATH: str = Field(
        default="./logs/vpn_manager.log",
        description="Ruta del archivo de logs"
    )
    
    ENABLE_METRICS: bool = Field(
        default=False,
        description="Habilitar recolección de métricas (Prometheus, etc.)"
    )
    
    SENTRY_DSN: Optional[str] = Field(
        default=None,
        description="DSN de Sentry para tracking de errores (opcional)"
    )
    
    # =========================================================================
    # SEGURIDAD AVANZADA
    # =========================================================================
    ENABLE_IP_WHITELIST: bool = Field(
        default=False,
        description="Habilitar whitelist de IPs para la API"
    )
    
    API_ALLOWED_IPS: List[str] = Field(
        default_factory=list,
        description="Lista de IPs permitidas si ENABLE_IP_WHITELIST=true"
    )
    
    # =========================================================================
    # RUTAS Y DIRECTORIOS
    # =========================================================================
    VPN_TEMPLATES_PATH: str = Field(
        default="./templates",
        description="Ruta de plantillas de configuración"
    )
    
    TEMP_PATH: str = Field(
        default="./temp",
        description="Directorio temporal"
    )
    
    QR_CODE_PATH: str = Field(
        default="./static/qr_codes",
        description="Directorio para códigos QR generados"
    )
    
    CLIENT_CONFIGS_PATH: str = Field(
        default="./static/configs",
        description="Directorio para configuraciones de clientes"
    )
    
    # =========================================================================
    # CONFIGURACIÓN DE PYDANTIC
    # =========================================================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignorar variables extra no definidas
        case_sensitive=True,
        validate_assignment=True  # Validar también al asignar valores después de instanciar
    )
    
    # =========================================================================
    # VALIDADORES PERSONALIZADOS
    # =========================================================================
    
    @field_validator("AUTHORIZED_USERS", mode="before")
    @classmethod
    def parse_authorized_users(cls, v):
        """Convierte string '123,456' a lista [123, 456]"""
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            # Limpiar corchetes si existen
            v = v.strip("[]")
            try:
                return [int(x.strip()) for x in v.split(",") if x.strip()]
            except ValueError:
                from utils.logger import logger
                logger.warning(f"Error parseando AUTHORIZED_USERS: {v}")
                return []
        return v if isinstance(v, list) else []
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Convierte string de orígenes CORS a lista"""
        if isinstance(v, str):
            v = v.strip()
            # Limpiar corchetes y comillas si existen
            v = v.strip("[]").replace('"', '').replace("'", "")
            if not v:
                return ["*"]
            return [x.strip() for x in v.split(",") if x.strip()]
        return v if isinstance(v, list) else ["*"]
    
    @field_validator("API_ALLOWED_IPS", mode="before")
    @classmethod
    def parse_allowed_ips(cls, v):
        """Parsea lista de IPs permitidas"""
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            return [x.strip() for x in v.split(",") if x.strip()]
        return v if isinstance(v, list) else []
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Valida que el nivel de log sea correcto"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            from utils.logger import logger
            logger.warning(f"LOG_LEVEL inválido '{v}', usando 'INFO'")
            return "INFO"
        return v
    
    @model_validator(mode="after")
    def validate_environment(self):
        """Validaciones cruzadas después de cargar todos los valores"""
        from utils.logger import logger

        # Autocompletar WG_ENDPOINT si no existe
        if not self.WG_ENDPOINT and self.SERVER_IP and self.WG_SERVER_PORT:
            self.WG_ENDPOINT = f"{self.SERVER_IP}:{self.WG_SERVER_PORT}"
            logger.info(f"WG_ENDPOINT autoconstruido: {self.WG_ENDPOINT}")

        # Autocompletar OUTLINE_SERVER_IP si no existe
        if not self.OUTLINE_SERVER_IP and self.SERVER_IP:
            self.OUTLINE_SERVER_IP = self.SERVER_IP
            logger.info(f"OUTLINE_SERVER_IP autoconstruido: {self.OUTLINE_SERVER_IP}")

        # Advertir si se usa CORS_ORIGINS=* en producción
        if self.is_production and "*" in self.CORS_ORIGINS:
            logger.warning(
                "⚠️ CORS_ORIGINS='*' en producción es un riesgo de seguridad. "
                "Define dominios específicos."
            )

        # Validar que ADMIN_ID esté en AUTHORIZED_USERS
        if self.ADMIN_ID not in self.AUTHORIZED_USERS:
            self.AUTHORIZED_USERS.append(self.ADMIN_ID)
            logger.info(f"ADMIN_ID {self.ADMIN_ID} agregado automáticamente a AUTHORIZED_USERS")

        # Crear directorios si no existen
        for path_attr in ["TEMP_PATH", "QR_CODE_PATH", "CLIENT_CONFIGS_PATH", "VPN_TEMPLATES_PATH"]:
            path_value = getattr(self, path_attr)
            Path(path_value).mkdir(parents=True, exist_ok=True)

        # Crear directorio de logs
        log_dir = Path(self.LOG_FILE_PATH).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        return self
    
    # =========================================================================
    # PROPIEDADES COMPUTADAS
    # =========================================================================
    
    @property
    def is_production(self) -> bool:
        """Verifica si está en modo producción"""
        return self.APP_ENV.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Verifica si está en modo desarrollo"""
        return self.APP_ENV.lower() == "development"
    
    @property
    def database_config(self) -> dict:
        """Retorna configuración de base de datos para SQLAlchemy"""
        return {
            "url": self.DATABASE_URL,
            "pool_size": self.DB_POOL_SIZE,
            "pool_timeout": self.DB_TIMEOUT,
            "pool_pre_ping": True,  # Verificar conexiones antes de usar
            "echo": self.is_development,  # Log SQL en desarrollo
        }
    
    @property
    def wireguard_enabled(self) -> bool:
        """Verifica si WireGuard está configurado"""
        return bool(
            self.WG_SERVER_PUBKEY 
            and self.WG_SERVER_PRIVKEY 
            and self.WG_ENDPOINT
        )
    
    @property
    def outline_enabled(self) -> bool:
        """Verifica si Outline está configurado"""
        return bool(self.OUTLINE_API_URL)
    
    def get_vpn_protocols(self) -> List[str]:
        """Retorna lista de protocolos VPN disponibles"""
        protocols = []
        if self.wireguard_enabled:
            protocols.append("wireguard")
        if self.outline_enabled:
            protocols.append("outline")
        return protocols
    
    def model_dump_safe(self) -> dict:
        """Retorna configuración sin exponer secretos"""
        data = self.model_dump()
        sensitive_keys = [
            "SECRET_KEY",
            "TELEGRAM_TOKEN",
            "WG_SERVER_PRIVKEY",
            "SUPABASE_SERVICE_KEY",
            "SUPABASE_SECRET_KEY",
            "SUPABASE_JWT_SECRET",
            "DATABASE_URL",
            "OUTLINE_API_URL",
            "SENTRY_DSN"
        ]
        for key in sensitive_keys:
            if key in data:
                data[key] = "***HIDDEN***"
        return data


# =========================================================================
# INSTANCIA GLOBAL (SINGLETON)
# =========================================================================

def get_settings() -> Settings:
    """
    Factory function para obtener la configuración.
    Útil para inyección de dependencias en FastAPI.
    """
    return settings


try:
    settings = Settings()

    # Import logger after settings are created to avoid circular import
    from utils.logger import logger

    # Apply full logger configuration now that settings exists
    try:
        logger.configure_from_settings(settings)
    except Exception:
        # If logger configuration fails, continue with the minimal logger
        pass

    # Log de inicio solo con información no sensible
    logger.info(f"✅ Configuración cargada correctamente")
    logger.info(f"📦 Proyecto: {settings.PROJECT_NAME}")
    logger.info(f"🌍 Entorno: {settings.APP_ENV}")
    logger.info(f"🔌 API: {settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"🛡️ Protocolos VPN disponibles: {', '.join(settings.get_vpn_protocols())}")

    if settings.is_production:
        logger.info("🔒 Modo PRODUCCIÓN activado")
    else:
        logger.warning("⚠️ Modo DESARROLLO - No usar en producción")

except Exception as e:
    # Import logger for error logging
    from utils.logger import logger
    logger.critical(f"❌ Error crítico de configuración:")
    logger.critical(f"   {str(e)}")
    logger.critical("   Revisa tu archivo .env y compara con example.env")
    exit(1)

