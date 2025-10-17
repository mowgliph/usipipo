# services/outline.py
from typing import Optional, Dict, Any, List
import os
import ssl
import socket
import hashlib
import urllib.parse
import logging
import asyncio

import aiohttp
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from database import models
from database.crud import vpn as crud_vpn

logger = logging.getLogger("usipipo")

OUTLINE_API_URL = os.getenv("OUTLINE_API_URL")
OUTLINE_CERT_SHA256 = os.getenv("OUTLINE_CERT_SHA256")
DEFAULT_DURATION_MONTHS = int(os.getenv("OUTLINE_DEFAULT_MONTHS", "1"))


# ---- Utility: blocking fingerprint check run in executor ----
def _fetch_remote_cert_sha256(host: str, port: int) -> str:
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            der_cert = ssock.getpeercert(binary_form=True)
            if der_cert is None:
                raise RuntimeError("No se pudo obtener el certificado remoto")
            return hashlib.sha256(der_cert).hexdigest().upper()


async def _verify_outline_cert() -> bool:
    """Verifica el fingerprint SHA256 del certificado TLS de Outline (ejecuta socket en executor)."""
    if not OUTLINE_API_URL:
        logger.error("OUTLINE_API_URL no está configurado.")
        return False
    parsed = urllib.parse.urlparse(OUTLINE_API_URL)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    if not host:
        logger.error("No se pudo extraer el host de OUTLINE_API_URL.")
        return False
    loop = asyncio.get_running_loop()
    try:
        sha256 = await loop.run_in_executor(None, _fetch_remote_cert_sha256, host, port)
        ok = bool(sha256 and OUTLINE_CERT_SHA256 and sha256.upper() == OUTLINE_CERT_SHA256.upper())
        if not ok:
            logger.error("outline cert mismatch: remote=%s expected=%s", sha256, OUTLINE_CERT_SHA256)
        return ok
    except Exception:
        logger.exception("failed_verify_outline_cert")
        return False


# ---- HTTP helper using aiohttp ----
async def _outline_request(method: str, path: str, *, json: Optional[Dict[str, Any]] = None, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    Realiza una petición a la API de Outline.
    Primero verifica el certificado TLS; tras ello realiza la petición con verify disabled
    para evitar doble verificación (ya validamos el fingerprint manualmente).
    """
    if not await _verify_outline_cert():
        raise RuntimeError("Certificado TLS de Outline no coincide con el esperado")

    if not OUTLINE_API_URL:
        raise RuntimeError("OUTLINE_API_URL no está configurado.")
    url = f"{OUTLINE_API_URL.rstrip('/')}{path}"
    try:
        # No verification on aiohttp side since we validated fingerprint manually
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.request(method.upper(), url, json=json, ssl=False) as resp:
                resp.raise_for_status()
                if resp.content_type and "application/json" in resp.content_type:
                    return await resp.json()
                # If no JSON body, return None
                text = await resp.text()
                return None if text == "" else {"text": text}
    except aiohttp.ClientError as e:
        logger.exception("outline_http_error")
        raise RuntimeError(f"Error comunicándose con Outline: {e}") from e


# ---- Public API: create_access / revoke_access / list_user_accesses ----
async def create_access(
    session: AsyncSession,
    user_id: str,
    duration_months: int = DEFAULT_DURATION_MONTHS,
    commit: bool = False,
) -> Dict[str, Any]:
    """
    Crea un access key en Outline y registra el record en la DB (sin commit).
    Retorna dict con keys: config_data (accessUrl), extra_data (raw API response), vpn_obj (created DB object).
    """
    expires_at = datetime.utcnow() + timedelta(days=30 * max(1, duration_months))

    # Call Outline API
    api_resp = await _outline_request("POST", "/access-keys")
    if not api_resp or "accessUrl" not in api_resp:
        raise RuntimeError("Respuesta inesperada de Outline al crear access key")

    access_url = api_resp["accessUrl"]
    config_name = f"outline_{user_id}_{int(datetime.utcnow().timestamp())}"

    extra = dict(api_resp)  # store full response for auditing: id, method, password, port, etc.

    # Create DB record without committing; caller controls the transaction
    vpn_obj = await crud_vpn.create_vpn_config(
        session=session,
        user_id=user_id,
        vpn_type="outline",
        config_name=config_name,
        config_data=access_url,
        expires_at=expires_at,
        extra_data=extra,
        is_trial=False,
        commit=commit,
    )

    return {"config_data": access_url, "extra_data": extra, "vpn_obj": vpn_obj}


async def revoke_access(session: AsyncSession, vpn_id: str, commit: bool = False) -> Optional[models.VPNConfig]:
    """
    Revoca un access key en Outline (si existe) y marca el registro como revoked (commit controlado por caller).
    """
    vpn_entry = await crud_vpn.get_vpn_config(session, vpn_id)
    if not vpn_entry or vpn_entry.vpn_type != "outline":
        return None

    access_id = (vpn_entry.extra_data or {}).get("id")
    if access_id:
        try:
            await _outline_request("DELETE", f"/access-keys/{access_id}")
        except Exception as e:
            logger.exception("failed_revoke_outline_remote", extra={"user_id": getattr(vpn_entry, "user_id", None)})
            raise RuntimeError(f"No se pudo revocar el acceso en Outline: {e}") from e

    updated = await crud_vpn.update_vpn_status(session, vpn_id, "revoked", commit=commit)
    return updated


async def list_user_accesses(session: AsyncSession, user_id: str) -> List[models.VPNConfig]:
    """
    Lista accesos Outline de un usuario consultando CRUD asíncrono.
    """
    all_configs = await crud_vpn.get_vpn_configs_for_user(session, user_id)
    return [v for v in all_configs if v.vpn_type == "outline"]
