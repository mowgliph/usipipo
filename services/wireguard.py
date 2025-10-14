# services/wireguard.py

from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import os
import asyncio
import logging
import tempfile

import aiofiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import models
from database.crud import vpn as crud_vpn

logger = logging.getLogger("usipipo")

# Configuración desde entorno
WG_INTERFACE = os.getenv("WG_INTERFACE")
WG_CONFIG_DIR = os.getenv("WG_CONFIG_DIR")
SERVER_PUBLIC_KEY = os.getenv("SERVER_PUBLIC_KEY")
SERVER_ENDPOINT = os.getenv("SERVER_ENDPOINT")
WG_SUBNET_PREFIX = os.getenv("WG_SUBNET_PREFIX")
IP_RANGE_START = int(os.getenv("WG_IP_START", "2"))
IP_RANGE_END = int(os.getenv("WG_IP_END", "254"))

# Validar variables críticas al importar el módulo
_required = [WG_INTERFACE, WG_CONFIG_DIR, SERVER_PUBLIC_KEY, SERVER_ENDPOINT, WG_SUBNET_PREFIX]
if not all(_required):
    logger.error(
        "WireGuard service not configured correctly. Required envs: WG_INTERFACE, WG_CONFIG_DIR, "
        "SERVER_PUBLIC_KEY, SERVER_ENDPOINT, WG_SUBNET_PREFIX"
    )
    raise RuntimeError(
        "WireGuard service not configured: check WG_INTERFACE, WG_CONFIG_DIR, SERVER_PUBLIC_KEY, SERVER_ENDPOINT, WG_SUBNET_PREFIX"
    )


async def _run_cmd_capture(cmd: List[str], input_data: Optional[bytes] = None) -> bytes:
    """
    Ejecuta un comando externo de forma asíncrona y devuelve stdout.
    Lanza RuntimeError en fallo.
    """
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE if input_data is not None else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate(input=input_data)
    if proc.returncode != 0:
        err = stderr.decode(errors="ignore").strip()
        logger.error("Command failed: %s | stderr: %s", cmd, err)
        raise RuntimeError(f"Command {cmd} failed: {err}")
    return stdout


async def generate_keys() -> Tuple[str, str]:
    """
    Genera par de claves WireGuard (privada, pública) usando wg genkey | wg pubkey.
    Retorna (private_key, public_key).
    """
    priv = await _run_cmd_capture(["wg", "genkey"])
    pub = await _run_cmd_capture(["wg", "pubkey"], input_data=priv)
    return priv.decode().strip(), pub.decode().strip()


async def get_next_ip(session: AsyncSession) -> str:
    """
    Asigna la siguiente IP libre en el rango definido.
    Consulta la DB asíncronamente para minimizar race conditions; idealmente debe llamarse
    dentro de una transacción que garantice exclusión si hay alta concurrencia.
    Retorna una IP en formato CIDR (ej. 10.10.0.2/32).
    """
    stmt = select(models.VPNConfig.extra_data).where(models.VPNConfig.vpntype == "wireguard")
    res = await session.execute(stmt)
    used_addresses = []
    for row in res.scalars().all():
        if isinstance(row, dict):
            addr = row.get("address")
            if addr:
                used_addresses.append(addr)

    for i in range(IP_RANGE_START, IP_RANGE_END + 1):
        candidate = f"{WG_SUBNET_PREFIX}.{i}/32"
        if candidate not in used_addresses:
            return candidate

    raise RuntimeError("No available IPs in WireGuard range")


async def _wg_add_peer(public_key: str, address: str) -> None:
    """
    Añade peer al interfaz wg de forma asíncrona.
    Lanza RuntimeError si falla.
    """
    cmd = ["wg", "set", WG_INTERFACE, "peer", public_key, "allowed-ips", address]
    await _run_cmd_capture(cmd)


async def _wg_remove_peer(public_key: str) -> None:
    """
    Elimina peer del interfaz wg de forma asíncrona.
    Lanza RuntimeError si falla.
    """
    cmd = ["wg", "set", WG_INTERFACE, "peer", public_key, "remove"]
    await _run_cmd_capture(cmd)


async def _atomic_write_text(path: str, text: str, encoding: str = "utf-8") -> None:
    """
    Escritura atómica: escribe en archivo temporal y luego replace al destino.
    """
    dirpath = os.path.dirname(path)
    os.makedirs(dirpath, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dirpath)
    os.close(fd)
    try:
        async with aiofiles.open(tmp_path, "w", encoding=encoding) as f:
            await f.write(text)
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                logger.debug("Could not remove tmp file %s", tmp_path)


async def create_peer(
    session: AsyncSession,
    user_id: int,
    duration_months: int = 1,
    dns: str = "1.1.1.1",
    config_name: Optional[str] = None,
    commit: bool = False,
) -> Dict[str, Any]:
    """
    Crea un peer WireGuard y su registro DB.
    Flujo seguro:
      1. Generar claves y reservar IP (no muta el servidor aún)
      2. Escribir archivo .conf de forma atómica
      3. Crear registro VPNConfig con status='creating' (commit opcional)
      4. Añadir peer al servidor wg
      5. Actualizar registro a status='active' y retornar vpn

    Parámetros:
      - session: AsyncSession
      - commit: si True hace commit al crear/actualizar el registro DB
    Retorna dict con keys: config_data, extra_data, vpn (models.VPNConfig)
    Nota: el llamador puede elegir cuándo confirmar la transacción si commit=False.
    """
    if config_name is None:
        config_name = f"user_{user_id}_{int(datetime.utcnow().timestamp())}"

    # 1. Generar claves y reservar IP
    private_key, public_key = await generate_keys()
    address = await get_next_ip(session)
    expires_at = datetime.utcnow() + timedelta(days=30 * max(1, int(duration_months)))

    config_data = (
        f"[Interface]\n"
        f"PrivateKey = {private_key}\n"
        f"Address = {address}\n"
        f"DNS = {dns}\n\n"
        f"[Peer]\n"
        f"PublicKey = {SERVER_PUBLIC_KEY}\n"
        f"Endpoint = {SERVER_ENDPOINT}\n"
        f"AllowedIPs = 0.0.0.0/0, ::/0\n"
        f"PersistentKeepalive = 25\n"
    )

    # 2. Escribir archivo .conf de forma atómica (si falla no hemos tocado el servidor ni la DB)
    conf_path = os.path.join(WG_CONFIG_DIR, f"{config_name}.conf")
    try:
        await _atomic_write_text(conf_path, config_data)
    except Exception as e:
        logger.exception("failed_write_wg_conf", extra={"user_id": user_id})
        raise RuntimeError(f"Unable to write WireGuard config file: {e}")

    extra = {
        "public_key": public_key,
        "address": address,
        "dns": dns,
        "conf_path": conf_path,
    }

    # 3. Crear registro DB inicial con status 'creating'
    vpn_obj = await crud_vpn.create_vpn_config(
        session=session,
        user_id=user_id,
        vpn_type="wireguard",
        config_name=config_name,
        config_data=config_data,
        expires_at=expires_at,
        extra_data=extra,
        is_trial=False,
        status="creating",
        commit=commit,
    )

    # 4. Añadir peer al servidor; si falla, marcamos DB como 'error' para intervención
    try:
        await _wg_add_peer(public_key, address)
    except Exception as e:
        logger.exception("failed_add_wg_peer", extra={"user_id": user_id})
        try:
            # Intento de marcar DB como inconsistent/error (no commit automatico si commit=False)
            await crud_vpn.update_vpn_status(session, getattr(vpn_obj, "id", None), "error", commit=commit)
        except Exception:
            logger.exception("failed_mark_vpn_error", extra={"user_id": user_id})
        raise RuntimeError(f"Failed to add peer to WireGuard interface: {e}")

    # 5. Actualizar registro a 'active'
    try:
        updated = await crud_vpn.update_vpn_status(session, getattr(vpn_obj, "id", None), "active", commit=commit)
    except Exception:
        logger.exception("failed_update_status_active", extra={"user_id": user_id})
        # No propagamos aquí, pero devolvemos vpn_obj tal como esté
        updated = vpn_obj

    # Dependiendo del commit flag, el caller debe refrescar la entidad si requiere atributos actualizados.
    return {"config_data": config_data, "extra_data": extra, "vpn": updated}


async def revoke_peer(session: AsyncSession, vpn_id: int, commit: bool = False) -> Optional[models.VPNConfig]:
    """
    Revoca un peer: remueve del servidor y actualiza estado en DB.
    - Si no existe o no es wireguard devuelve None.
    - commit controla si se hace commit al actualizar la DB.
    """
    vpn_entry = await crud_vpn.get_vpn_config(session, vpn_id)
    if not vpn_entry or getattr(vpn_entry, "vpntype", None) != "wireguard":
        return None

    public_key = (getattr(vpn_entry, "extra_data", {}) or {}).get("public_key")
    if public_key:
        try:
            await _wg_remove_peer(public_key)
        except Exception as e:
            logger.exception("failed_remove_wg_peer", extra={"vpn_id": vpn_id})
            raise RuntimeError(f"Error removing peer from server: {e}")

    updated = await crud_vpn.update_vpn_status(session, vpn_id, "revoked", commit=commit)
    return updated


async def list_user_peers(session: AsyncSession, user_id: int) -> List[models.VPNConfig]:
    """
    Lista todos los peers activos de un usuario consultando el CRUD asíncrono.
    """
    all_configs = await crud_vpn.get_vpn_configs(session, user_id)
    return [v for v in all_configs if getattr(v, "status", None) == "active" and getattr(v, "vpntype", None) == "wireguard"]


async def generate_qr(config_data: str) -> bytes:
    """
    Genera QR usando qrencode de forma asíncrona.
    Devuelve bytes PNG.
    """
    if not isinstance(config_data, (str, bytes)):
        raise TypeError("config_data must be str or bytes")
    input_bytes = config_data.encode("utf-8") if isinstance(config_data, str) else config_data
    out = await _run_cmd_capture(["qrencode", "-t", "PNG", "-o", "-"], input_data=input_bytes)
    return out
