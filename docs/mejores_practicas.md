# 📋 Mejores Prácticas y Guías de Desarrollo

## Descripción General

Este documento establece las mejores prácticas para el desarrollo, mantenimiento y operación de uSipipo, asegurando código de calidad, seguridad y escalabilidad.

## 🏗️ Arquitectura y Diseño

### Principios SOLID

#### 1. Single Responsibility Principle (SRP)
**Cada clase/función debe tener una única responsabilidad.**

✅ **Correcto:**
```python
class VPNConfigService:
    """Gestiona configuraciones VPN - UNA responsabilidad"""

    def create_wireguard_config(self, user_id: str) -> dict:
        # Solo lógica de creación de config
        pass

    def validate_config(self, config: dict) -> bool:
        # Solo validación
        pass

class VPNConfigRepository:
    """Acceso a datos de VPN configs - UNA responsabilidad"""

    def save(self, config: VPNConfig) -> None:
        # Solo persistencia
        pass
```

❌ **Incorrecto:**
```python
class VPNManager:
    """Hace TODO - múltiples responsabilidades"""

    def create_config(self, user_id: str) -> dict:
        # Crea config Y valida Y guarda Y envía notificación
        pass
```

#### 2. Open/Closed Principle (OCP)
**Las clases deben estar abiertas para extensión pero cerradas para modificación.**

✅ **Correcto:**
```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        pass

class StarsPaymentProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        # Lógica específica de Stars
        pass

class QvaPayPaymentProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        # Lógica específica de QvaPay
        pass
```

#### 3. Liskov Substitution Principle (LSP)
**Los objetos de una subclase deben ser sustituibles por objetos de la clase base.**

✅ **Correcto:**
```python
def process_payment(processor: PaymentProcessor, amount: float) -> bool:
    return processor.process_payment(amount)

# Ambas implementaciones funcionan igual
stars_processor = StarsPaymentProcessor()
qvapay_processor = QvaPayPaymentProcessor()

process_payment(stars_processor, 5.0)  # ✅
process_payment(qvapay_processor, 5.0)  # ✅
```

### Patrón Repository

**Centralizar el acceso a datos:**

```python
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user_data: dict) -> User:
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        return user
```

### Inyección de Dependencias

**No crear dependencias dentro de las clases:**

✅ **Correcto:**
```python
class UserService:
    def __init__(self, user_repo: UserRepository, audit_service: AuditService):
        self.user_repo = user_repo
        self.audit_service = audit_service

# En el contenedor de dependencias
def create_user_service(session: AsyncSession) -> UserService:
    user_repo = UserRepository(session)
    audit_service = AuditService(session)
    return UserService(user_repo, audit_service)
```

❌ **Incorrecto:**
```python
class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)  # Creando dependencia aquí
        self.audit_service = AuditService(session)  # Creando dependencia aquí
```

## 🔒 Seguridad

### Validación de Entrada

**Siempre validar datos de entrada:**

```python
from pydantic import BaseModel, validator
from typing import Optional

class CreateVPNRequest(BaseModel):
    user_id: str
    vpn_type: str
    config_name: Optional[str] = None

    @validator('vpn_type')
    def validate_vpn_type(cls, v):
        if v not in ['wireguard', 'outline']:
            raise ValueError('Tipo VPN inválido')
        return v

    @validator('config_name')
    def validate_config_name(cls, v):
        if v and len(v) > 128:
            raise ValueError('Nombre demasiado largo')
        return v
```

### Sanitización de Datos

**Prevenir inyección SQL y XSS:**

```python
import bleach

def sanitize_html(text: str) -> str:
    """Sanitiza HTML para prevenir XSS"""
    allowed_tags = ['b', 'i', 'u', 'code', 'pre']
    return bleach.clean(text, tags=allowed_tags, strip=True)

def sanitize_sql_input(value: str) -> str:
    """Sanitiza entrada para prevenir inyección SQL"""
    # Usar parámetros preparados en SQLAlchemy
    # NO concatenar strings en queries
    return value.strip()
```

### Gestión de Secrets

**Nunca hardcodear secrets:**

```python
# .env
TELEGRAM_BOT_TOKEN=sk-1234567890abcdef
DATABASE_URL=mysql+pymysql://user:pass@localhost/db
SECRET_KEY=mi_clave_super_secreta_de_32_caracteres

# config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    telegram_bot_token: str
    database_url: str
    secret_key: str

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### Rate Limiting

**Proteger contra abuso:**

```python
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        self.requests[key] = [req_time for req_time in self.requests[key]
                             if now - req_time < self.window_seconds]

        if len(self.requests[key]) >= self.max_requests:
            return False

        self.requests[key].append(now)
        return True

# Uso en handlers
rate_limiter = RateLimiter(max_requests=5, window_seconds=60)

async def vpn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not rate_limiter.is_allowed(f"vpn_command_{user_id}"):
        await update.message.reply_text("Demasiadas solicitudes. Intenta más tarde.")
        return

    # Procesar comando
    pass
```

## 🧪 Testing

### Estructura de Tests

```
test/
├── unit/           # Tests unitarios
├── integration/    # Tests de integración
├── e2e/           # Tests end-to-end
├── fixtures/      # Datos de prueba
└── conftest.py    # Configuración de pytest
```

### Test Unitario Ejemplo

```python
import pytest
from unittest.mock import Mock, AsyncMock
from services.vpn import VPNService

@pytest.fixture
def mock_repo():
    repo = Mock()
    repo.get_user_vpn_configs = AsyncMock(return_value=[])
    return repo

@pytest.fixture
def vpn_service(mock_repo):
    return VPNService(mock_repo)

@pytest.mark.asyncio
async def test_create_trial_config_success(vpn_service, mock_repo):
    # Arrange
    user_id = "user-123"
    mock_repo.create_vpn_config = AsyncMock(return_value=Mock(id="config-123"))

    # Act
    result = await vpn_service.create_trial_config(user_id, "wireguard")

    # Assert
    assert result is not None
    mock_repo.create_vpn_config.assert_called_once()
```

### Test de Integración

```python
@pytest.mark.asyncio
async def test_full_vpn_creation_flow(db_session):
    # Crear usuario
    user = User(telegram_id=123456, username="testuser")
    db_session.add(user)
    await db_session.commit()

    # Crear config VPN
    vpn_service = VPNService(db_session)
    config = await vpn_service.create_trial_config(str(user.id), "wireguard")

    # Verificar en BD
    saved_config = await db_session.get(VPNConfig, config.id)
    assert saved_config is not None
    assert saved_config.is_trial is True
```

## 📊 Logging y Monitoreo

### Niveles de Logging

```python
import logging

# Configuración centralizada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Logger específico por módulo
logger = logging.getLogger(__name__)

class UserService:
    async def create_user(self, telegram_id: int):
        logger.info("Creating user", extra={"telegram_id": telegram_id})

        try:
            # Lógica de creación
            logger.info("User created successfully", extra={"user_id": "new-id"})
        except Exception as e:
            logger.error("Failed to create user", extra={
                "telegram_id": telegram_id,
                "error": str(e)
            })
            raise
```

### Helpers de Logging Estandarizados

```python
# utils/logging_helpers.py
from typing import Optional
import logging

def log_user_action(user_id: Optional[str], action: str, details: Optional[dict] = None):
    """Log estandarizado para acciones de usuario"""
    extra = {"user_id": user_id or "SYSTEM"}
    if details:
        extra.update(details)

    logging.info(f"User action: {action}", extra=extra)

def log_error(context: str, error: Exception, user_id: Optional[str] = None):
    """Log estandarizado para errores"""
    logging.error(f"Error in {context}", extra={
        "user_id": user_id or "SYSTEM",
        "error": str(error),
        "error_type": type(error).__name__
    })
```

### Métricas y Monitoreo

```python
# services/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Contadores
VPN_CONFIGS_CREATED = Counter('vpn_configs_created_total', 'Total VPN configs created', ['vpn_type'])
PAYMENTS_PROCESSED = Counter('payments_processed_total', 'Total payments processed', ['method'])

# Histogramas
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration', ['endpoint'])

# Gauges
ACTIVE_USERS = Gauge('active_users', 'Number of active users')
SYSTEM_CPU = Gauge('system_cpu_usage', 'CPU usage percentage')

class MetricsService:
    @staticmethod
    def increment_vpn_configs_created(vpn_type: str):
        VPN_CONFIGS_CREATED.labels(vpn_type=vpn_type).inc()

    @staticmethod
    def time_request(endpoint: str):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    return await func(*args, **kwargs)
                finally:
                    duration = time.time() - start_time
                    REQUEST_DURATION.labels(endpoint=endpoint).observe(duration)
            return wrapper
        return decorator
```

## 🚀 Rendimiento

### Optimización de Base de Datos

#### Índices Estratégicos

```sql
-- Índices para búsquedas frecuentes
CREATE INDEX CONCURRENTLY idx_users_telegram_id_active ON users (telegram_id) WHERE is_active = true;
CREATE INDEX CONCURRENTLY idx_vpn_configs_user_status_created ON vpn_configs (user_id, status, created_at DESC);
CREATE INDEX CONCURRENTLY idx_payments_user_created ON payments (user_id, created_at DESC);

-- Índices parciales para estados específicos
CREATE INDEX CONCURRENTLY idx_audit_logs_recent ON audit_logs (created_at DESC) WHERE created_at > NOW() - INTERVAL '30 days';
```

#### Consultas Optimizadas

```python
# ✅ Bueno: Usar selectinload para relaciones
async def get_user_with_configs(user_id: str) -> User:
    stmt = select(User).options(
        selectinload(User.vpnconfigs),
        selectinload(User.payments)
    ).where(User.id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one()

# ❌ Malo: N+1 queries
async def get_users_with_configs_bad():
    users = await session.execute(select(User))
    for user in users:
        configs = await session.execute(
            select(VPNConfig).where(VPNConfig.user_id == user.id)
        )  # Query por cada usuario
```

### Cache Estratégico

```python
# services/cache.py
import redis.asyncio as redis
from typing import Optional, Any
import json

class CacheService:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url)

    async def get(self, key: str) -> Optional[Any]:
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value: Any, ttl: int = 300):
        await self.redis.set(key, json.dumps(value), ex=ttl)

    async def invalidate_pattern(self, pattern: str):
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

# Uso en servicios
class UserService:
    def __init__(self, cache: CacheService, repo: UserRepository):
        self.cache = cache
        self.repo = repo

    async def get_user(self, user_id: str) -> Optional[User]:
        cache_key = f"user:{user_id}"

        # Intentar cache primero
        cached = await self.cache.get(cache_key)
        if cached:
            return User(**cached)

        # Fallback a BD
        user = await self.repo.get_by_id(user_id)
        if user:
            await self.cache.set(cache_key, user.__dict__)

        return user
```

## 🔄 Manejo de Errores

### Excepciones Personalizadas

```python
# exceptions.py
class USipipoException(Exception):
    """Base exception for uSipipo"""
    pass

class ValidationError(USipipoException):
    """Invalid input data"""
    pass

class PaymentError(USipipoException):
    """Payment processing failed"""
    pass

class VPNConfigError(USipipoException):
    """VPN configuration error"""
    pass

class InsufficientPermissionsError(USipipoException):
    """User doesn't have required permissions"""
    pass
```

### Middleware de Error Handling

```python
# middleware/error_handler.py
from telegram.ext import CallbackContext
from exceptions import USipipoException
import logging

async def error_handler(update: Update, context: CallbackContext):
    """Global error handler for Telegram bot"""

    error = context.error
    user_id = update.effective_user.id if update and update.effective_user else None

    if isinstance(error, USipipoException):
        # Errores de negocio - mostrar mensaje amigable
        await update.message.reply_text(f"Error: {str(error)}")
        logging.warning(f"Business error: {error}", extra={"user_id": user_id})

    elif isinstance(error, Exception):
        # Errores técnicos - log detallado, mensaje genérico
        logging.error(f"Unexpected error: {error}", extra={
            "user_id": user_id,
            "error_type": type(error).__name__,
            "traceback": traceback.format_exc()
        })
        await update.message.reply_text("Ha ocurrido un error interno. Intenta más tarde.")

        # Notificar a admins
        await notify_admins(f"Error crítico: {error}")
```

## 📝 Documentación

### Docstrings Estandarizados

```python
def create_vpn_config(
    self,
    user_id: str,
    vpn_type: str,
    is_trial: bool = False,
    months: int = 1
) -> VPNConfig:
    """
    Create a new VPN configuration for a user.

    Args:
        user_id: UUID of the user
        vpn_type: Type of VPN ('wireguard' or 'outline')
        is_trial: Whether this is a trial configuration
        months: Number of months for paid configs

    Returns:
        The created VPNConfig object

    Raises:
        ValidationError: If input data is invalid
        VPNConfigError: If config creation fails

    Example:
        config = await vpn_service.create_vpn_config(
            user_id="user-123",
            vpn_type="wireguard",
            is_trial=True
        )
    """
```

### README por Módulo

Cada módulo debe tener documentación:

```
services/
├── vpn.py          # Servicio VPN
├── vpn.md          # Documentación del servicio VPN
├── payments.py     # Servicio de pagos
├── payments.md     # Documentación del servicio de pagos
```

## 🔧 Code Quality

### Linting y Formateo

```bash
# requirements-dev.txt
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.5.0

# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
```

### Type Hints Obligatorios

```python
from typing import Optional, List, Dict, Any
from datetime import datetime

def process_payment(
    self,
    user_id: str,
    amount: float,
    currency: str = "USD"
) -> Dict[str, Any]:
    """
    Process a payment transaction.

    Returns:
        Dict with payment details and status
    """
    pass

async def get_user_configs(
    self,
    user_id: str,
    status: Optional[str] = None
) -> List[VPNConfig]:
    """Get VPN configurations for a user."""
    pass
```

## 🚀 Deployment

### CI/CD Básico

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run tests
        run: pytest

      - name: Run linters
        run: |
          black --check .
          isort --check-only .
          flake8 .
          mypy .
```

### Health Checks

```python
# routes/health.py
from fastapi import APIRouter
from sqlalchemy import text
import redis.asyncio as redis

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "timestamp": datetime.utcnow().isoformat()
    }

    # Check database
    try:
        # db check logic
        health_status["database"] = "healthy"
    except Exception as e:
        health_status["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check Redis
    try:
        # redis check logic
        health_status["redis"] = "healthy"
    except Exception as e:
        health_status["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    return health_status
```

## 📚 Conclusión

Seguir estas mejores prácticas asegura que uSipipo mantenga:

- **Mantenibilidad**: Código fácil de entender y modificar
- **Escalabilidad**: Arquitectura que soporta crecimiento
- **Seguridad**: Protección contra vulnerabilidades comunes
- **Rendimiento**: Optimización para alto throughput
- **Confiabilidad**: Manejo robusto de errores y edge cases

La implementación consistente de estos patrones desde el inicio previene problemas futuros y facilita la incorporación de nuevos desarrolladores al proyecto.

---

**Última actualización: Octubre 2025**