from application.services.vpn_service import VpnService
from telegram.ext import ContextTypes
from loguru import logger

async def sync_vpn_usage_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Consulta el consumo de datos en los servidores VPN 
    y actualiza la base de datos local.
    """
    vpn_service: VpnService = context.job.context['vpn_service']
    
    try:
        logger.info("📊 Iniciando sincronización de consumo de datos...")
        
        # 1. Obtener todas las llaves desde el Repositorio a través del Servicio
        # Suponiendo que implementamos un método get_all_active_keys en el servicio
        keys = await vpn_service.get_all_active_keys()
        
        for key in keys:
            try:
                # 2. Consultar uso real a la API correspondiente (Outline o WG)
                # El servicio debe abstraer la llamada al cliente_outline o client_wireguard
                current_usage = await vpn_service.fetch_real_usage(key)
                
                # 3. Guardar en DB
                await vpn_service.update_key_usage(key.id, current_usage)
                
            except Exception as e:
                logger.error(f"Error sincronizando llave {key.id}: {e}")
                
        logger.info("✅ Sincronización de consumo completada.")
        
    except Exception as e:
        logger.error(f"Error crítico en sync_vpn_usage_job: {e}")
