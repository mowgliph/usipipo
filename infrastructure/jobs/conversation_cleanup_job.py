"""
Job para limpieza de conversaciones inactivas del asistente IA Sip.

Author: uSipipo Team
Version: 1.0.0
"""

from utils.logger import logger


async def cleanup_stale_conversations_job(context):
    """
    Job periódico para limpiar conversaciones inactivas de Sip.
    
    Args:
        context: Contexto del job de Telegram
    """
    try:
        ai_support_service = context.job.data.get('ai_support_service')
        
        if not ai_support_service:
            logger.error("❌ Job de limpieza: ai_support_service no proporcionado")
            return
        
        deleted_count = await ai_support_service.cleanup_stale_conversations(hours=24)
        
        if deleted_count > 0:
            logger.info(f"🌊 Job de limpieza: {deleted_count} conversaciones eliminadas")
        else:
            logger.debug("🌊 Job de limpieza: No hay conversaciones para eliminar")
            
    except Exception as e:
        logger.error(f"❌ Error en job de limpieza de conversaciones: {e}")
