import httpx
from urllib.parse import quote
from utils.logger import logger
from config import settings

class OutlineClient:
    """
    Cliente de infraestructura para la API de Outline (Shadowbox).
    Portado y optimizado desde la implementación estable en JS.
    """

    def __init__(self):
        self.api_url = settings.OUTLINE_API_URL
        # Outline utiliza certificados autofirmados por defecto
        self.client = httpx.AsyncClient(
            verify=False, 
            timeout=15.0
        )
        self.brand = "uSipipo VPN"

    @staticmethod
    def apply_branding(access_url: str, brand_name: str) -> str:
        """Añade el tag de branding al final de la URL ss://"""
        tag = quote(brand_name)
        return f"{access_url}#{tag}"

    async def get_server_info(self) -> dict:
        """Obtiene estado de salud y estadísticas básicas del servidor."""
        try:
            server_res = await self.client.get(f"{self.api_url}/server")
            keys_res = await self.client.get(f"{self.api_url}/access-keys")
            
            server_res.raise_for_status()
            
            data = server_res.json()
            keys_data = keys_res.json()
            
            return {
                "name": data.get("name", "Outline Server"),
                "serverId": data.get("serverId"),
                "version": data.get("version"),
                "total_keys": len(keys_data.get("accessKeys", [])),
                "is_healthy": True
            }
        except Exception as e:
            logger.error(f"Error en getServerInfo: {e}")
            return {
                "is_healthy": False,
                "error": str(e)
            }

    async def create_key(self, name: str = "Usuario") -> dict:
        """Crea una llave, la renombra y aplica branding."""
        try:
            # 1. Crear la llave
            res = await self.client.post(f"{self.api_url}/access-keys")
            res.raise_for_status()
            key_data = res.json()
            
            key_id = key_data["id"]

            # 2. Renombrar la llave
            await self.client.put(
                f"{self.api_url}/access-keys/{key_id}/name", 
                data={"name": name}
            )

            # 3. Formatear respuesta con branding
            return {
                "id": key_id,
                "name": name,
                "access_url": self.apply_branding(key_data["accessUrl"], self.brand),
                "port": key_data.get("port"),
                "method": key_data.get("method")
            }
        except Exception as e:
            logger.error(f"Error en createKey: {e}")
            raise Exception("Error al generar acceso en el servidor VPN.")

    async def delete_key(self, key_id: str) -> bool:
        """Elimina una llave. Retorna True incluso si ya no existe (404)."""
        try:
            res = await self.client.delete(f"{self.api_url}/access-keys/{key_id}")
            if res.status_code == 404:
                logger.warning(f"Intento de borrar key inexistente: {key_id}")
                return True
            return res.status_code == 204
        except Exception as e:
            logger.error(f"Error en deleteKey({key_id}): {e}")
            return False

    async def get_metrics(self) -> dict:
        """
        Obtiene el mapa completo de consumo de datos del servidor.
        Requerido por vpn_service.fetch_real_usage.
        """
        try:
            res = await self.client.get(f"{self.api_url}/metrics/transfer")
            # Devuelve un diccionario { "id_usuario": bytes_usados }
            return res.json().get("bytesTransferredByUserId", {})
        except Exception as e:
            logger.error(f"Error obteniendo métricas globales Outline: {e}")
            return {}

    async def get_key_usage(self, key_id: str) -> dict:
        """Obtiene consumo de datos. No rompe el flujo si falla."""
        try:
            res = await self.client.get(f"{self.api_url}/metrics/transfer")
            usage_map = res.json().get("bytesTransferredByUserId", {})
            
            bytes_used = usage_map.get(key_id, 0)
            
            return {
                "keyId": key_id,
                "bytesUsed": bytes_used,
                "mbUsed": round(bytes_used / (1024 * 1024), 2),
                "error": False
            }
        except Exception as e:
            logger.error(f"Error en getKeyUsage para {key_id}: {e}")
            return {
                "keyId": key_id, 
                "bytesUsed": 0, 
                "mbUsed": 0, 
                "error": True
            }

    async def close(self):
        """Cierra la sesión del cliente HTTP."""
        await self.client.aclose()
