from application.services.vpn_service import VpnService
from telegram.ext import ContextTypes
from loguru import logger

async def sync_vpn_usage_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Consulta el consumo de datos en los servidores VPN 
    y actualiza la base de datos local cada 10 minutos.
    """
    # El objeto se inyecta desde el contexto del Job (configurado en main.py)
    vpn_service: VpnService = context.job.context['vpn_service']
    
    try:
        logger.info("📊 Iniciando sincronización de consumo de datos...")
        
        # Obtenemos las llaves usando el método que ahora incluiremos en el servicio
        keys = await vpn_service.get_all_active_keys()
        
        for key in keys:
            try:
                # Consultar uso real (ya sea Outline o WireGuard)
                current_usage = await vpn_service.fetch_real_usage(key)
                
                # Actualizar en Supabase
                await vpn_service.update_key_usage(key.id, current_usage)
                
            except Exception as e:
                logger.error(f"Error sincronizando llave {key.id}: {e}")
                
        logger.info("✅ Sincronización de consumo completada.")
        
    except Exception as e:
        logger.error(f"Error crítico en sync_vpn_usage_job: {e}")
