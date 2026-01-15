"""
Repositorio de usuarios con SQLAlchemy Async.

Author: uSipipo Team
Version: 2.0.0
"""

from typing import Optional, List
from datetime import datetime, timezone
import secrets

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import logger

from domain.entities.user import User, UserStatus
from domain.interfaces.iuser_repository import IUserRepository
from .models import UserModel
from .base_repository import BaseSupabaseRepository


class SupabaseUserRepository(BaseSupabaseRepository, IUserRepository):
    """
    Implementación del repositorio de usuarios usando SQLAlchemy Async.
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el repositorio con una sesión de base de datos.

        Args:
            session: Sesión async de SQLAlchemy.
        """
        super().__init__(session)

    def _model_to_entity(self, model: UserModel) -> User:
        """Convierte un modelo SQLAlchemy a entidad de dominio."""
        # Normalizar vip_expires_at: si es naive, asumir UTC
        vip_expires = model.vip_expires_at
        if vip_expires is not None and vip_expires.tzinfo is None:
            vip_expires = vip_expires.replace(tzinfo=timezone.utc)

        return User(
            telegram_id=model.telegram_id,
            username=model.username,
            full_name=model.full_name,
            status=UserStatus(model.status) if model.status else UserStatus.ACTIVE,
            max_keys=model.max_keys or 2,
            balance_stars=model.balance_stars or 0,
            total_deposited=model.total_deposited or 0,
            referral_code=model.referral_code,
            referred_by=model.referred_by,
            total_referral_earnings=model.total_referral_earnings or 0,
            is_vip=model.is_vip or False,
            vip_expires_at=vip_expires
        )
    def _entity_to_model(self, entity: User) -> UserModel:
        """Convierte una entidad de dominio a modelo SQLAlchemy."""
        return UserModel(
            telegram_id=entity.telegram_id,
            username=entity.username,
            full_name=entity.full_name,
            status=entity.status.value if isinstance(entity.status, UserStatus) else entity.status,
            max_keys=entity.max_keys,
            balance_stars=entity.balance_stars,
            total_deposited=entity.total_deposited,
            referral_code=entity.referral_code,
            referred_by=entity.referred_by,
            total_referral_earnings=entity.total_referral_earnings,
            is_vip=entity.is_vip,
            vip_expires_at=entity.vip_expires_at
        )

    async def get_by_id(self, telegram_id: int, current_user_id: int) -> Optional[User]:
        """Busca un usuario por su ID de Telegram."""
        await self._set_current_user(current_user_id)
        try:
            query = select(UserModel).where(UserModel.telegram_id == telegram_id)
            result = await self.session.execute(query)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._model_to_entity(model)

        except Exception as e:
            logger.error(f"❌ Error al obtener usuario {telegram_id}: {e}")
            return None

    async def get_user(self, telegram_id: int, current_user_id: int) -> Optional[User]:
        """Alias de get_by_id para compatibilidad."""
        return await self.get_by_id(telegram_id, current_user_id)

    async def save(self, user: User, current_user_id: int) -> User:
        """Guarda o actualiza los datos del usuario."""
        await self._set_current_user(current_user_id)
        try:
            # Verificar si existe
            existing = await self.session.get(UserModel, user.telegram_id)

            if existing:
                # Actualizar campos
                existing.username = user.username
                existing.full_name = user.full_name
                existing.status = user.status.value if isinstance(user.status, UserStatus) else user.status
                existing.max_keys = user.max_keys
                existing.balance_stars = user.balance_stars
                existing.total_deposited = user.total_deposited
                existing.referral_code = user.referral_code
                existing.referred_by = user.referred_by
                existing.total_referral_earnings = user.total_referral_earnings
                existing.is_vip = user.is_vip
                # Asegurar que vip_expires_at sea aware (UTC) antes de guardar
                if user.vip_expires_at is None:
                    existing.vip_expires_at = None
                elif user.vip_expires_at.tzinfo is None:
                    existing.vip_expires_at = user.vip_expires_at.replace(tzinfo=timezone.utc)
                else:
                    existing.vip_expires_at = user.vip_expires_at.astimezone(timezone.utc)
            else:
                # Crear nuevo
                model = self._entity_to_model(user)
                self.session.add(model)

            await self.session.commit()
            logger.info(f"💾 Usuario {user.telegram_id} guardado correctamente.")
            return user

        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error al guardar usuario: {e}")
            raise

    async def create_user(
        self,
        user_id: int,
        username: str = None,
        full_name: str = None,
        referral_code: str = None,
        referred_by: int = None,
        current_user_id: int = None
    ) -> User:
        """Crea un nuevo usuario."""
        if referral_code is None:
            referral_code = secrets.token_hex(4).upper()

        user = User(
            telegram_id=user_id,
            username=username,
            full_name=full_name,
            referral_code=referral_code,
            referred_by=referred_by
        )

        # For user creation, if no current_user_id provided, use the new user's ID
        if current_user_id is None:
            current_user_id = user_id

        return await self.save(user, current_user_id)

    async def exists(self, telegram_id: int, current_user_id: int) -> bool:
        """Verifica si el usuario ya está registrado."""
        await self._set_current_user(current_user_id)
        try:
            query = select(UserModel.telegram_id).where(
                UserModel.telegram_id == telegram_id
            )
            result = await self.session.execute(query)
            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(f"❌ Error verificando existencia de usuario: {e}")
            return False

    async def get_by_referral_code(self, referral_code: str, current_user_id: int) -> Optional[User]:
        """Busca un usuario por su código de referido."""
        await self._set_current_user(current_user_id)
        try:
            query = select(UserModel).where(
                UserModel.referral_code == referral_code
            )
            result = await self.session.execute(query)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._model_to_entity(model)

        except Exception as e:
            logger.error(f"❌ Error al buscar por referral_code {referral_code}: {e}")
            return None

    async def update_balance(self, telegram_id: int, new_balance: int, current_user_id: int) -> bool:
        """Actualiza el balance de estrellas del usuario."""
        await self._set_current_user(current_user_id)
        try:
            query = (
                update(UserModel)
                .where(UserModel.telegram_id == telegram_id)
                .values(balance_stars=new_balance)
            )
            await self.session.execute(query)
            await self.session.commit()
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error al actualizar balance: {e}")
            return False

    async def get_referrals(self, referrer_id: int, current_user_id: int) -> List[dict]:
        """Obtiene todos los usuarios referidos (como diccionarios)."""
        await self._set_current_user(current_user_id)
        try:
            query = select(UserModel).where(
                UserModel.referred_by == referrer_id
            )
            result = await self.session.execute(query)
            models = result.scalars().all()

            return [
                {
                    "telegram_id": m.telegram_id,
                    "username": m.username,
                    "full_name": m.full_name,
                    "created_at": m.created_at
                }
                for m in models
            ]

        except Exception as e:
            logger.error(f"❌ Error al obtener referidos: {e}")
            return []

    async def get_referrals_by_user(self, telegram_id: int, current_user_id: int) -> List[User]:
        """Obtiene la lista de usuarios referidos como entidades."""
        await self._set_current_user(current_user_id)
        try:
            query = select(UserModel).where(
                UserModel.referred_by == telegram_id
            )
            result = await self.session.execute(query)
            models = result.scalars().all()

            return [self._model_to_entity(m) for m in models]

        except Exception as e:
            logger.error(f"❌ Error al obtener referidos por usuario {telegram_id}: {e}")
            return []

    async def get_all_users(self, current_user_id: int) -> List[User]:
        """Obtiene todos los usuarios registrados."""
        await self._set_current_user(current_user_id)
        try:
            query = select(UserModel)
            result = await self.session.execute(query)
            models = result.scalars().all()

            return [self._model_to_entity(m) for m in models]

        except Exception as e:
            logger.error(f"❌ Error al obtener todos los usuarios: {e}")
            return []

