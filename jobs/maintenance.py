# jobs/maintenance.py

from __future__ import annotations
from telegram.ext import ContextTypes
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
import logging

from database.db import AsyncSessionLocal as get_session
from database.crud import logs as crud_logs, vpn as crud_vpn, users as crud_users
from services import wireguard as wireguard_service, outline as outline_service
from utils.helpers import notify_admins

logger = logging.getLogger(__name__)

async def maintenance_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Job de mantenimiento (async):
    - Limpia logs antiguos (>30 días).
    - Revoca trials vencidos.
    - Notifica a admins/superadmins SOLO si hubo cambios.
    - Siempre registra traza en audit_logs.
    """
    deleted_logs = 0
    revoked_trials = 0

    async with get_session() as session:
        try:
            # 1. Eliminar logs antiguos
            cutoff = datetime.now(tz=timezone.utc) - timedelta(days=30)
            deleted_logs = await crud_logs.delete_old_logs(session, cutoff)
            logger.info(f"[Maintenance] Logs eliminados: {deleted_logs}", extra={"user_id": None})

            # 2. Revocar trials vencidos
            expired_trials = await crud_vpn.get_expired_trials(session)
            for vpn in expired_trials:
                try:
                    if vpn.vpn_type == "wireguard":
                        await wireguard_service.revoke_peer(session, vpn.id, commit=False)
                    elif vpn.vpn_type == "outline":
                        await outline_service.revoke_access(session, vpn.id)
                    else:
                        logger.error(f"Tipo VPN no soportado: {vpn.vpn_type}", extra={"user_id": vpn.user_id, "vpn_id": vpn.id})
                        continue

                    await crud_logs.create_audit_log(
                        session=session,
                        user_id=vpn.user_id,
                        action="trial_revoked",
                        payload={"details": f"Trial {vpn.id} expirado y revocado", "vpn_id": vpn.id, "vpn_type": vpn.vpn_type},
                        commit=False,
                    )
                    revoked_trials += 1
                    logger.info(f"[Maintenance] Trial revocado: {vpn.id}", extra={"user_id": vpn.user_id, "vpn_id": vpn.id})

                except Exception as e:
                    await crud_logs.create_audit_log(
                        session=session,
                        user_id=vpn.user_id,
                        action="trial_revoke_failed",
                        payload={"details": f"Error al revocar trial {vpn.id}: {str(e)}", "vpn_id": vpn.id, "vpn_type": vpn.vpn_type},
                        commit=False,
                    )
                    logger.error(f"[Maintenance] Error revocando trial {vpn.id}: {e}", extra={"user_id": vpn.user_id, "vpn_id": vpn.id})

            # Commit de todas las operaciones
            await session.commit()

            # 3. Notificar a admins/superadmins SOLO si hubo cambios
            if deleted_logs > 0 or revoked_trials > 0:
                summary = (
                    f"🧹 <b>Mantenimiento completado</b>\n\n"
                    f"🗑️ Logs eliminados: <b>{deleted_logs}</b>\n"
                    f"❌ Trials revocados: <b>{revoked_trials}</b>\n"
                    f"⏱️ Fecha: <code>{datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</code>"
                )
                await notify_admins(
                    session=session,
                    bot=context.bot,
                    message=summary,
                    action="maintenance_completed",
                    details=f"Logs eliminados: {deleted_logs}, Trials revocados: {revoked_trials}",
                )
            else:
                # 4. Registrar traza de que no hubo cambios
                await crud_logs.create_audit_log(
                    session=session,
                    user_id=None,
                    action="maintenance_no_changes",
                    payload={"details": "No se eliminaron logs ni se revocaron trials"},
                    commit=False,
                )
                logger.info("[Maintenance] No hubo cambios en esta ejecución.", extra={"user_id": None})

        except Exception as e:
            logger.error(f"[Maintenance] Error general: {e}", extra={"user_id": None})
            await crud_logs.create_audit_log(
                session=session,
                user_id=None,
                action="maintenance_error",
                payload={"details": f"Error general en mantenimiento: {str(e)}"},
                commit=False,
            )
            await session.rollback()