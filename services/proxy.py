# services/proxy.py

from __future__ import annotations
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging
import asyncio
import subprocess
import os

from database import models
from database.crud import proxy as crud_proxy, logs as crud_logs
from utils.helpers import log_and_notify

logger = logging.getLogger(__name__)


async def create_free_proxy_for_user(session: AsyncSession, user_id: str, commit: bool = False) -> Optional[models.MTProtoProxy]:
    """
    Crea un proxy MTProto gratuito para el usuario.
    Utiliza el script mtproto-install.sh para generar la configuración.
    Retorna el proxy creado o None si falla.
    """
    try:
        # Verificar si el usuario ya tiene un proxy activo
        existing = await crud_proxy.get_active_proxy_for_user(session, user_id)
        if existing:
            logger.info("Usuario ya tiene proxy activo", extra={"user_id": user_id, "proxy_id": existing.id})
            raise ValueError("user_has_active_proxy")

        # Ejecutar el script de instalación para generar configuración
        config = await _generate_mtproto_config()
        if not config:
            logger.error("No se pudo generar configuración MTProto", extra={"user_id": user_id})
            await crud_logs.create_audit_log(
                session=session,
                user_id=user_id,
                action="proxy_creation_failed",
                payload={"reason": "Config generation failed"},
                commit=False,
            )
            return None

        # Crear el proxy en la base de datos
        proxy = await crud_proxy.create_free_proxy(
            session,
            user_id=user_id,
            host=config["host"],
            port=config["port"],
            secret=config["secret"],
            tag=config.get("tag"),
            duration_days=30,  # Proxy gratuito por 30 días
            extra_data={"source": "free_proxy", "config_method": "script"},
            commit=commit,
        )

        logger.info("✅ Proxy MTProto gratuito creado para usuario", extra={"user_id": user_id, "proxy_id": proxy.id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="free_proxy_created",
            payload={"proxy_id": proxy.id, "host": proxy.host, "port": proxy.port},
            commit=False,
        )
        return proxy

    except ValueError:
        raise
    except (SQLAlchemyError, Exception) as e:
        logger.exception(f"❌ Error creando proxy gratuito para user {user_id}: {e}", extra={"user_id": user_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=user_id,
            action="proxy_creation_error",
            payload={"error": str(e)},
            commit=False,
        )
        raise


async def _generate_mtproto_config() -> Optional[Dict[str, Any]]:
    """
    Obtiene configuración MTProto desde variables de entorno cargadas por config.py.
    Las variables son pobladas ejecutando mtproto-install.sh que genera .env variables.
    Retorna dict con host, port, secret, tag opcional o None si falla.
    """
    try:
        from config import config

        # Verificar que las variables críticas estén definidas
        if not config.MTPROXY_HOST:
            logger.error("MTPROXY_HOST no está definido en configuración")
            return None
        if not config.MTPROXY_PORT:
            logger.error("MTPROXY_PORT no está definido en configuración")
            return None
        if not config.MTPROXY_SECRET:
            logger.error("MTPROXY_SECRET no está definido en configuración")
            return None

        # Convertir puerto a int para validación
        try:
            port = int(config.MTPROXY_PORT)
        except ValueError:
            logger.error(f"MTPROXY_PORT inválido: {config.MTPROXY_PORT}")
            return None

        # Retornar configuración compartida (misma para todos los usuarios)
        config_dict = {
            "host": config.MTPROXY_HOST,
            "port": port,
            "secret": config.MTPROXY_SECRET,
            "tag": config.MTPROXY_TAG,  # Opcional, puede ser None
        }

        logger.info("Configuración MTProto obtenida desde variables de entorno", extra={
            "host": config_dict["host"],
            "port": config_dict["port"],
            "has_tag": config_dict["tag"] is not None
        })
        return config_dict

    except Exception as e:
        logger.exception(f"Error obteniendo configuración MTProto: {e}")
        return None


async def list_user_proxies(session: AsyncSession, user_id: str) -> list[models.MTProtoProxy]:
    """Lista todos los proxies MTProto de un usuario."""
    try:
        proxies = await crud_proxy.get_proxies_for_user(session, user_id)
        return proxies
    except SQLAlchemyError as e:
        logger.exception(f"Error listando proxies para user {user_id}", extra={"user_id": user_id})
        raise


async def revoke_proxy(session: AsyncSession, proxy_id: str, reason: str = "user_request") -> Optional[models.MTProtoProxy]:
    """
    Revoca un proxy MTProto existente.
    Retorna el proxy actualizado o None si no se encuentra.
    """
    try:
        proxy = await crud_proxy.revoke_proxy(session, proxy_id, reason, commit=False)
        if proxy:
            logger.info(f"🧹 Proxy MTProto revocado (ID: {proxy_id})", extra={"user_id": proxy.user_id, "proxy_id": proxy_id})
            await crud_logs.create_audit_log(
                session=session,
                user_id=proxy.user_id,
                action="proxy_revoked",
                payload={"proxy_id": proxy_id, "reason": reason},
                commit=False,
            )
        else:
            logger.error(f"❌ No se encontró proxy MTProto ID {proxy_id}", extra={"user_id": None, "proxy_id": proxy_id})
            await crud_logs.create_audit_log(
                session=session,
                user_id=None,
                action="proxy_revoke_failed",
                payload={"proxy_id": proxy_id, "reason": "proxy not found"},
                commit=False,
            )
        return proxy
    except (SQLAlchemyError, Exception) as e:
        logger.exception(f"❌ Error revocando proxy ({proxy_id}): {e}", extra={"user_id": None, "proxy_id": proxy_id})
        await crud_logs.create_audit_log(
            session=session,
            user_id=None,
            action="proxy_revoke_error",
            payload={"proxy_id": proxy_id, "error": str(e)},
            commit=False,
        )
        raise


async def get_proxy_connection_string(proxy: models.MTProtoProxy) -> str:
    """
    Genera la cadena de conexión tg:// para el proxy.
    """
    return f"tg://proxy?server={proxy.host}&port={proxy.port}&secret={proxy.secret}"


async def get_proxy_info(proxy: models.MTProtoProxy) -> Dict[str, Any]:
    """
    Retorna información detallada del proxy para mostrar al usuario.
    """
    return {
        "id": proxy.id,
        "host": proxy.host,
        "port": proxy.port,
        "secret": proxy.secret,
        "tag": proxy.tag,
        "status": proxy.status,
        "created_at": proxy.created_at.isoformat() if proxy.created_at else None,
        "expires_at": proxy.expires_at.isoformat() if proxy.expires_at else None,
        "connection_string": await get_proxy_connection_string(proxy),
    }