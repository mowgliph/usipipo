# services/register.py
from __future__ import annotations
from typing import Optional, Callable, Dict, Any
from datetime import datetime, timezone, timedelta

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from database.crud import users as crud_users
from database.crud import vpn as crud_vpn
from database.crud import logs as crud_logs
from config.config import TRIAL_DURATION_DAYS

logger = logging.getLogger("usipipo.services.register")

Notifier = Callable[[str, Dict[str, Any]], None]  # signature: notify(channel, payload) or custom


class RegistrationError(RuntimeError):
    """Errores genéricos del flow de registro."""


async def register_user(
    session: AsyncSession,
    tg_payload: Dict[str, Any],
    *,
    create_trial: bool = True,
    trial_days: Optional[int] = None,
    notify: Optional[Notifier] = None,
) -> Dict[str, Any]:
    """
    Flujo de registro / onboarding.

    - Asegura existencia de User (create/update) usando crud_users.ensure_user.
    - Si create_trial=True intentará crear un trial (una sola vez por usuario).
    - Crea un AuditLog con la acción 'user_registered' o 'user_login_existing' según el caso.
    - Notifica a admins vía `notify` si se crea un usuario nuevo (notify puede ser None).
    - Devuelve dict con keys: user, created_user (bool), trial (VPNConfig|None).

    Transacciones y commits:
    - Esta función coordina la transacción: hace commit si hay cambios (usuario creado o trial creado).
    - Usa rollback en errores y re-raise con RegistrationError cuando procede.
    """
    telegram_id = int(tg_payload["id"])
    user = None
    created_user = False
    trial = None

    try:
        # 1) Asegurar user (no commitea en CRUD por defecto)
        user = await crud_users.ensure_user(session, tg_payload, commit=False)

        # Determinar si es usuario nuevo (created_at reciente)
        now = datetime.now(timezone.utc)
        created_recent = False
        try:
            created_at = getattr(user, "created_at", None)
            if created_at:
                created_recent = (now - created_at) <= timedelta(seconds=5)
        except Exception:
            created_recent = False

        created_user = created_recent

        # 2) Si solicitamos trial, comprobar y crear
        if create_trial:
            # Usar duración por defecto de config si no se especifica
            actual_trial_days = trial_days or TRIAL_DURATION_DAYS

            # Verificamos si ya existe trial activo
            has_trial = await crud_vpn.has_trial(session, user.id)
            if not has_trial:
                try:
                    trial = await crud_vpn.create_trial_vpn(
                        session,
                        user_id=user.id,
                        vpn_type="wireguard",  # elección razonable por defecto; cambiar en caller si hace falta
                        config_name="trial",
                        config_data={"notes": f"trial created on register ({actual_trial_days} days)"},
                        duration_days=actual_trial_days,
                        commit=False,
                    )
                except ValueError:
                    # ValueError lanzado por create_trial_vpn cuando ya tiene trial activo
                    trial = None
                    logger.debug("Usuario ya tiene trial activo, no se crea nuevo", extra={"user_id": user.id})
                except SQLAlchemyError:
                    logger.exception("Error creando trial durante registro", extra={"user_id": user.id})
                    raise RegistrationError("create_trial_failed")

        # 3) Commitar todos los cambios hechos (user created/updated, trial)
        # Solo commit si algo cambió: nuevo usuario o trial fue creado
        if created_user or trial is not None:
            try:
                await session.commit()
                # refresh objects to populate DB-generated fields
                await session.refresh(user)
                if trial is not None:
                    await session.refresh(trial)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Fallo al commitear cambios de registro", extra={"user_id": user.id})
                raise RegistrationError("db_commit_failed")

        # 4) Crear audit log (no commiteamos otra vez; ya commitado arriba if needed)
        action = "user_registered" if created_user else "user_login_existing"
        payload = {
            "telegram_id": telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "created_user": created_user,
            "trial_created": trial is not None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        try:
            # create_audit_log by default does not commit; we don't need to commit it if we already committed above.
            await crud_logs.create_audit_log(session, user_id=user.id, action=action, details=None, payload=payload, commit=False)
            # Commit del audit log por separado si no se commiteó arriba
            if not (created_user or trial is not None):
                await session.commit()
        except SQLAlchemyError:
            # If audit log fails, log but do not block the registration success
            logger.exception("Fallo creando audit log de registro", extra={"user_id": user.id})

        # 5) Notificar admins si es un nuevo usuario
        if created_user and notify:
            try:
                notify_payload = {
                    "user_id": user.id,
                    "telegram_id": telegram_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "trial_created": trial is not None,
                    "registered_at": datetime.now(timezone.utc).isoformat(),
                }
                notify("admin_new_user", notify_payload)
            except Exception:
                logger.exception("Fallo notificar admins de nuevo usuario", extra={"user_id": user.id})

        result = {"user": user, "created_user": created_user, "trial": trial}
        logger.info("Registro finalizado", extra={"user_id": user.id})
        return result

    except RegistrationError:
        raise
    except Exception as exc:
        # Rollback safe and re-raise controlled RegistrationError
        try:
            await session.rollback()
        except Exception:
            logger.exception("Fallo al rollback tras error de registro", extra={"user_id": telegram_id})
        logger.exception("Error en register_user", extra={"user_id": telegram_id})
        raise RegistrationError("register_failed") from exc