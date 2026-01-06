from application.services.vpn_service import VpnService
from telegram.ext import ContextTypes
from utils.logger import logger

async def sync_vpn_usage_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Consulta el consumo de datos en los servidores VPN 
    y actualiza la base de datos local cada 30 minutos.
    """
    # CORRECCIÓN: Usar context.job.data en lugar de context.job.context
    vpn_service: VpnService = context.job.data['vpn_service']
    
    try:
        logger.info("📊 Iniciando sincronización de consumo de datos...")
        
        # Obtenemos las llaves activas
        keys = await vpn_service.get_all_active_keys()
        
        if not keys:
            logger.info("ℹ️ No hay llaves activas para sincronizar.")
            return
        
        synced_count = 0
        error_count = 0
        
        for key in keys:
            try:
                # Consultar uso real (ya sea Outline o WireGuard)
                current_usage = await vpn_service.fetch_real_usage(key)
                
                # Actualizar en Supabase
                await vpn_service.update_key_usage(key.id, current_usage)
                synced_count += 1
                
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Error sincronizando llave {key.id}: {e}")
        
        logger.info(
            f"✅ Sincronización completada. "
            f"Exitosas: {synced_count}, Errores: {error_count}"
        )
        
    except Exception as e:
        logger.error(f"❌ Error crítico en sync_vpn_usage_job: {e}")
