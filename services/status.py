# services/status.py
from typing import Dict, Any
import logging
import subprocess
import tempfile
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.crud import status as crud_status
from services.audit import audit_service
from config.runtime import BOT_START_TIME

logger = logging.getLogger("usipipo.status")

async def format_uptime(seconds: float) -> str:
    """Convierte segundos en formato legible (días, horas, minutos)."""
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)

async def get_status_metrics(session: AsyncSession) -> Dict[str, Any]:
    """
    Obtiene métricas globales del sistema para el comando /status.
    Registra la acción en AuditLog.
    """
    try:
        # Obtener métricas
        total_users = await crud_status.count_users(session)
        total_wireguard = await crud_status.count_vpn_configs_by_type(session, "wireguard")
        total_outline = await crud_status.count_vpn_configs_by_type(session, "outline")
        total_bandwidth = await crud_status.total_bandwidth_gb(session)

        # Calcular uptime
        uptime_seconds = datetime.now(timezone.utc).timestamp() - BOT_START_TIME
        uptime_str = await format_uptime(uptime_seconds)

        # Verificar estado de la conexión
        db_status = "✅ Conectada" if (await session.execute(select(1))).scalar() else "❌ Error de conexión"

        metrics = {
            "total_users": total_users,
            "total_wireguard": total_wireguard,
            "total_outline": total_outline,
            "total_bandwidth": total_bandwidth,
            "uptime": uptime_str,
            "db_status": db_status,
        }

        # Registrar en AuditLog
        await audit_service.log_action(
            user_id=None,  # Sistema, no usuario específico
            action="command_status",
            payload={"metrics": metrics}
        )

        return metrics
    except Exception as e:
        logger.exception("Error en get_status_metrics", extra={"user_id": None})
        raise

async def get_server_status() -> Dict[str, Any]:
    """
    Obtiene el estado de los servidores VPN (Outline y WireGuard) ejecutando los scripts de status.
    Esta función ejecuta los scripts bash para obtener información detallada del estado del servidor.
    """
    server_status = {
        "outline": {"status": "unknown", "details": ""},
        "wireguard": {"status": "unknown", "details": ""}
    }
    
    # Scripts base path
    base_path = "/home/mowgliph/usipipo"
    
    try:
        # Ejecutar status de Outline
        try:
            outline_script = f"{base_path}/scripts/outline-install.sh"
            result = subprocess.run(
                ["bash", outline_script, "--status"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=base_path
            )
            
            if result.returncode == 0:
                # Verificar si el servidor está operativo
                if "OUTLINE SERVER: OPERATIVO" in result.stdout:
                    server_status["outline"]["status"] = "operativo"
                elif "OUTLINE SERVER: NO OPERATIVO" in result.stdout:
                    server_status["outline"]["status"] = "no_operativo"
                else:
                    server_status["outline"]["status"] = "instalado"
                
                # Guardar detalles (primeros 500 caracteres para no saturar el mensaje)
                details = result.stdout.strip()
                if len(details) > 500:
                    details = details[:500] + "... (más información disponible)"
                server_status["outline"]["details"] = details
            else:
                server_status["outline"]["status"] = "no_instalado"
                server_status["outline"]["details"] = f"Error: {result.stderr[:200]}"
                
        except subprocess.TimeoutExpired:
            server_status["outline"]["status"] = "timeout"
            server_status["outline"]["details"] = "Timeout ejecutando script de Outline"
        except Exception as e:
            server_status["outline"]["status"] = "error"
            server_status["outline"]["details"] = f"Error ejecutando script: {str(e)}"
            
    except Exception as e:
        logger.exception("Error obteniendo status de Outline: %s", str(e))
        server_status["outline"]["status"] = "error"
        server_status["outline"]["details"] = f"Error interno: {str(e)}"
    
    try:
        # Ejecutar status de WireGuard
        try:
            wireguard_script = f"{base_path}/scripts/wireguard-install.sh"
            result = subprocess.run(
                ["bash", wireguard_script, "--status"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=base_path
            )
            
            if result.returncode == 0:
                # Verificar si el servidor está operativo
                if "WIREGUARD SERVER: OPERATIVO" in result.stdout:
                    server_status["wireguard"]["status"] = "operativo"
                elif "WIREGUARD SERVER: NO OPERATIVO" in result.stdout:
                    server_status["wireguard"]["status"] = "no_operativo"
                else:
                    server_status["wireguard"]["status"] = "instalado"
                
                # Guardar detalles (primeros 500 caracteres para no saturar el mensaje)
                details = result.stdout.strip()
                if len(details) > 500:
                    details = details[:500] + "... (más información disponible)"
                server_status["wireguard"]["details"] = details
            else:
                server_status["wireguard"]["status"] = "no_instalado"
                server_status["wireguard"]["details"] = f"Error: {result.stderr[:200]}"
                
        except subprocess.TimeoutExpired:
            server_status["wireguard"]["status"] = "timeout"
            server_status["wireguard"]["details"] = "Timeout ejecutando script de WireGuard"
        except Exception as e:
            server_status["wireguard"]["status"] = "error"
            server_status["wireguard"]["details"] = f"Error ejecutando script: {str(e)}"
            
    except Exception as e:
        logger.exception("Error obteniendo status de WireGuard: %s", str(e))
        server_status["wireguard"]["status"] = "error"
        server_status["wireguard"]["details"] = f"Error interno: {str(e)}"
    
    return server_status

def format_server_status_for_telegram(server_status: Dict[str, Any]) -> str:
    """
    Formatea el estado de los servidores para mostrar en Telegram.
    """
    status_text = "<b>🖥️ Estado de Servidores VPN</b>\n\n"
    
    # Estado de Outline
    outline = server_status.get("outline", {})
    outline_emoji = {
        "operativo": "✅",
        "no_operativo": "❌",
        "instalado": "⚠️",
        "no_instalado": "❌",
        "timeout": "⏰",
        "error": "💥"
    }.get(outline.get("status", "unknown"), "❓")
    
    status_text += f"{outline_emoji} <b>Outline Server:</b> {outline.get('status', 'desconocido').replace('_', ' ').title()}\n"
    
    # Estado de WireGuard
    wireguard = server_status.get("wireguard", {})
    wireguard_emoji = {
        "operativo": "✅",
        "no_operativo": "❌",
        "instalado": "⚠️",
        "no_instalado": "❌",
        "timeout": "⏰",
        "error": "💥"
    }.get(wireguard.get("status", "unknown"), "❓")
    
    status_text += f"{wireguard_emoji} <b>WireGuard Server:</b> {wireguard.get('status', 'desconocido').replace('_', ' ').title()}\n\n"
    
    # Agregar información de servidores operativos
    active_servers = []
    if outline.get("status") == "operativo":
        active_servers.append("Outline")
    if wireguard.get("status") == "operativo":
        active_servers.append("WireGuard")
    
    if active_servers:
        status_text += f"🚀 <b>Servidores Activos:</b> {', '.join(active_servers)}\n"
    else:
        status_text += "⚠️ <b>Ningún servidor VPN está operativo actualmente</b>\n"
    
    status_text += "\n📝 <i>Para detalles completos, ejecuta los scripts directamente:</i>\n"
    status_text += "<code>./scripts/outline-install.sh --status</code>\n"
    status_text += "<code>./scripts/wireguard-install.sh --status</code>"
    
    return status_text