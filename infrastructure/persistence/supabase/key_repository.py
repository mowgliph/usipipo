"""
Repositorio de llaves VPN con SQLAlchemy Async.

Author: uSipipo Team
Version: 2.0.0
"""

from typing import List, Optional
from datetime import datetime, timezone, timedelta
import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import logger

from domain.entities.vpn_key import VpnKey, KeyType
from domain.interfaces.ikey_repository import IKeyRepository
from .models import VpnKeyModel
from .base_repository import BaseSupabaseRepository


def _normalize_datetime(dt: Optional[datetime]) -> Optional[datetime]:
    """
    Normaliza un datetime a aware (con timezone UTC) para comparaciones consistentes.
    Si es None, retorna None.
    Si es naive (sin timezone), asume UTC.
    Si ya tiene timezone, lo convierte a UTC.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Si es naive, asumir UTC
        return dt.replace(tzinfo=timezone.utc)
    # Si ya tiene timezone, convertir a UTC
    return dt.astimezone(timezone.utc)


class SupabaseKeyRepository(BaseSupabaseRepository, IKeyRepository):
    """
    Implementación del repositorio de llaves VPN usando SQLAlchemy Async.
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el repositorio con una sesión de base de datos.

        Args:
            session: Sesión async de SQLAlchemy.
        """
        super().__init__(session)

    def _model_to_entity(self, model: VpnKeyModel) -> VpnKey:
        """Convierte un modelo SQLAlchemy a entidad de dominio."""
        return VpnKey(
            id=model.id,
            user_id=model.user_id,
            key_type=KeyType(model.key_type) if model.key_type else KeyType.OUTLINE,
            name=model.name,
            key_data=model.key_data,
            external_id=model.external_id,
            created_at=_normalize_datetime(model.created_at) or datetime.now(timezone.utc),
            is_active=model.is_active,
            used_bytes=model.used_bytes or 0,
            last_seen_at=_normalize_datetime(model.last_seen_at),
            data_limit_bytes=model.data_limit_bytes or 10 * 1024**3,
            billing_reset_at=_normalize_datetime(model.billing_reset_at) or datetime.now(timezone.utc)
        )

    def _entity_to_model(self, entity: VpnKey) -> VpnKeyModel:
        """Convierte una entidad de dominio a modelo SQLAlchemy."""
        return VpnKeyModel(
            id=entity.id if entity.id else uuid.uuid4(),
            user_id=entity.user_id,
            key_type=entity.key_type.value if isinstance(entity.key_type, KeyType) else entity.key_type,
            name=entity.name,
            key_data=entity.key_data,
            external_id=entity.external_id,
            is_active=entity.is_active,
            used_bytes=entity.used_bytes,
            last_seen_at=entity.last_seen_at,
            data_limit_bytes=entity.data_limit_bytes,
            billing_reset_at=entity.billing_reset_at
        )

    async def save(self, key: VpnKey, current_user_id: int) -> VpnKey:
        """Guarda una nueva llave o actualiza una existente."""
        await self._set_current_user(current_user_id)
        try:
            if key.id:
                existing = await self.session.get(VpnKeyModel, key.id)

                if existing:
                    # Actualizar
                    existing.name = key.name
                    existing.key_data = key.key_data
                    existing.external_id = key.external_id
                    existing.is_active = key.is_active
                    existing.used_bytes = key.used_bytes
                    existing.last_seen_at = key.last_seen_at
                    existing.data_limit_bytes = key.data_limit_bytes
                    existing.billing_reset_at = key.billing_reset_at
                else:
                    model = self._entity_to_model(key)
                    self.session.add(model)
            else:
                key.id = uuid.uuid4()
                model = self._entity_to_model(key)
                self.session.add(model)

            await self.session.commit()
            logger.debug(f"💾 Llave {key.id} guardada correctamente.")
            return key

        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error al guardar llave: {e}")
            raise

    async def get_by_user_id(self, telegram_id: int, current_user_id: int) -> List[VpnKey]:
        """Recupera todas las llaves activas de un usuario."""
        await self._set_current_user(current_user_id)
        try:
            query = (
                select(VpnKeyModel)
                .where(VpnKeyModel.user_id == telegram_id)
                .where(VpnKeyModel.is_active == True)
            )
            result = await self.session.execute(query)
            models = result.scalars().all()

            return [self._model_to_entity(m) for m in models]

        except Exception as e:
            logger.error(f"❌ Error al listar llaves del usuario {telegram_id}: {e}")
            return []

    async def get_by_user(self, telegram_id: int, current_user_id: int) -> List[VpnKey]:
        """Alias de get_by_user_id para compatibilidad."""
        return await self.get_by_user_id(telegram_id, current_user_id)

    async def get_all_active(self, current_user_id: int) -> List[VpnKey]:
        """Obtiene todas las llaves activas del sistema."""
        await self._set_current_user(current_user_id)
        try:
            query = select(VpnKeyModel).where(VpnKeyModel.is_active == True)
            result = await self.session.execute(query)
            models = result.scalars().all()

            return [self._model_to_entity(m) for m in models]

        except Exception as e:
            logger.error(f"❌ Error al obtener llaves activas: {e}")
            return []

    async def get_all_keys(self, current_user_id: int) -> List[VpnKey]:
        """Obtiene todas las llaves del sistema (activas e inactivas)."""
        await self._set_current_user(current_user_id)
        try:
            query = select(VpnKeyModel)
            result = await self.session.execute(query)
            models = result.scalars().all()

            return [self._model_to_entity(m) for m in models]

        except Exception as e:
            logger.error(f"❌ Error al obtener todas las llaves: {e}")
            return []

    async def get_by_id(self, key_id: uuid.UUID, current_user_id: int) -> Optional[VpnKey]:
        """Busca una llave por su ID."""
        await self._set_current_user(current_user_id)
        try:
            model = await self.session.get(VpnKeyModel, key_id)

            if model is None:
                return None

            return self._model_to_entity(model)

        except Exception as e:
            logger.error(f"❌ Error al obtener llave {key_id}: {e}")
            return None

    async def delete(self, key_id: uuid.UUID, current_user_id: int) -> bool:
        """Marca una llave como inactiva (soft delete)."""
        await self._set_current_user(current_user_id)
        try:
            query = (
                update(VpnKeyModel)
                .where(VpnKeyModel.id == key_id)
                .values(is_active=False)
            )
            await self.session.execute(query)
            await self.session.commit()
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error al eliminar llave {key_id}: {e}")
            return False

    async def update_usage(self, key_id: uuid.UUID, used_bytes: int, current_user_id: int) -> bool:
        """Actualiza el uso de datos de una llave."""
        await self._set_current_user(current_user_id)
        try:
            query = (
                update(VpnKeyModel)
                .where(VpnKeyModel.id == key_id)
                .values(used_bytes=used_bytes, last_seen_at=datetime.now(timezone.utc))
            )
            await self.session.execute(query)
            await self.session.commit()
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error al actualizar uso de llave {key_id}: {e}")
            return False

    async def update_data_limit(self, key_id: uuid.UUID, data_limit_bytes: int, current_user_id: int) -> bool:
        """Actualiza el límite de datos de una llave."""
        await self._set_current_user(current_user_id)
        try:
            query = (
                update(VpnKeyModel)
                .where(VpnKeyModel.id == key_id)
                .values(data_limit_bytes=data_limit_bytes)
            )
            await self.session.execute(query)
            await self.session.commit()
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error al actualizar límite de datos: {e}")
            return False

    async def reset_data_usage(self, key_id: uuid.UUID, current_user_id: int) -> bool:
        """Resetea el uso de datos de una llave."""
        await self._set_current_user(current_user_id)
        try:
            query = (
                update(VpnKeyModel)
                .where(VpnKeyModel.id == key_id)
                .values(
                    used_bytes=0,
                    billing_reset_at=datetime.now(timezone.utc)
                )
            )
            await self.session.execute(query)
            await self.session.commit()
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error al resetear uso de datos: {e}")
            return False

    async def get_keys_needing_reset(self, current_user_id: int) -> List[VpnKey]:
        """Obtiene llaves que necesitan reset de ciclo de facturación."""
        await self._set_current_user(current_user_id)
        try:
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

            query = (
                select(VpnKeyModel)
                .where(VpnKeyModel.billing_reset_at < thirty_days_ago)
                .where(VpnKeyModel.is_active == True)
            )
            result = await self.session.execute(query)
            models = result.scalars().all()

            return [self._model_to_entity(m) for m in models]

        except Exception as e:
            logger.error(f"❌ Error al obtener llaves para reset: {e}")
            return []
