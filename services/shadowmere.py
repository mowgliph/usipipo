# services/shadowmere.py
"""
Servicio de integración con Shadowmere para gestionar proxies detectados.
Sincroniza proxies desde la API de Shadowmere con la base de datos.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
import logging
import asyncio
import time

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from database import models
from database.crud import shadowmere as crud_shadowmere

logger = logging.getLogger("usipipo.services.shadowmere")


class ShadowmereService:
    """
    Servicio para gestionar la integración con Shadowmere.
    Proporciona métodos para sincronizar, validar y gestionar proxies detectados.
    """

    def __init__(self, shadowmere_api_url: str, shadowmere_port: int) -> None:
        """
        Inicializa el servicio de Shadowmere.

        Args:
            shadowmere_api_url: URL base de la API de Shadowmere (ej: http://localhost)
            shadowmere_port: Puerto de la API de Shadowmere (ej: 8080)

        Raises:
            ValueError: Si los parámetros están vacíos o son inválidos
        """
        if not shadowmere_api_url or not shadowmere_api_url.strip():
            raise ValueError("shadowmere_api_url no puede estar vacío")
        if not isinstance(shadowmere_port, int) or shadowmere_port <= 0 or shadowmere_port > 65535:
            raise ValueError("shadowmere_port debe ser un entero entre 1 y 65535")

        self.shadowmere_api_url = shadowmere_api_url.rstrip("/")
        self.shadowmere_port = shadowmere_port
        self.api_endpoint = f"{self.shadowmere_api_url}:{self.shadowmere_port}/api/proxies"
        self.timeout = aiohttp.ClientTimeout(total=30)

        logger.info(
            "ShadowmereService inicializado",
            extra={"api_endpoint": self.api_endpoint}
        )

    async def fetch_proxies_from_api(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de proxies desde la API de Shadowmere.

        Returns:
            Lista de diccionarios con información de proxies.
            Estructura esperada: [{"proxy": "IP:puerto", "type": "SOCKS5", "country": "US"}, ...]

        Raises:
            RuntimeError: Si hay error de conexión o respuesta inválida
            asyncio.TimeoutError: Si la solicitud excede el timeout
        """
        try:
            logger.debug("Obteniendo proxies desde API de Shadowmere", extra={"endpoint": self.api_endpoint})

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(self.api_endpoint) as resp:
                    if resp.status != 200:
                        logger.error(
                            "Error en respuesta de Shadowmere API",
                            extra={"status": resp.status, "endpoint": self.api_endpoint}
                        )
                        raise RuntimeError(f"Shadowmere API retornó status {resp.status}")

                    data = await resp.json()

                    # Validar que sea una lista
                    if not isinstance(data, list):
                        logger.error(
                            "Respuesta de Shadowmere API no es una lista",
                            extra={"type": type(data).__name__}
                        )
                        raise RuntimeError("Respuesta de API debe ser una lista de proxies")

                    logger.info(
                        "Proxies obtenidos desde Shadowmere API",
                        extra={"count": len(data)}
                    )
                    return data

        except asyncio.TimeoutError:
            logger.error(
                "Timeout conectando a Shadowmere API",
                extra={"endpoint": self.api_endpoint, "timeout": self.timeout.total}
            )
            raise RuntimeError(f"Timeout conectando a {self.api_endpoint}")

        except aiohttp.ClientError as e:
            logger.error(
                "Error de conexión con Shadowmere API",
                extra={"endpoint": self.api_endpoint, "error": str(e)}
            )
            raise RuntimeError(f"Error conectando a Shadowmere: {e}") from e

        except Exception as e:
            logger.exception(
                "Error inesperado obteniendo proxies de Shadowmere",
                extra={"endpoint": self.api_endpoint}
            )
            raise RuntimeError(f"Error inesperado: {e}") from e

    async def sync_proxies_to_db(self, session: AsyncSession) -> Dict[str, int]:
        """
        Sincroniza los proxies obtenidos de Shadowmere con la base de datos.
        Crea nuevos registros y actualiza los existentes.

        Args:
            session: Sesión async de SQLAlchemy

        Returns:
            Diccionario con estadísticas de sincronización:
            {
                "created": int,
                "updated": int,
                "failed": int,
                "total": int
            }

        Raises:
            RuntimeError: Si hay error obteniendo proxies de la API
            SQLAlchemyError: Si hay error en la base de datos
        """
        stats = {"created": 0, "updated": 0, "failed": 0, "total": 0}

        try:
            # Obtener proxies desde la API
            proxies_data = await self.fetch_proxies_from_api()
            stats["total"] = len(proxies_data)

            logger.info(
                "Iniciando sincronización de proxies",
                extra={"total": stats["total"]}
            )

            for proxy_data in proxies_data:
                try:
                    # Validar estructura mínima
                    if not isinstance(proxy_data, dict):
                        logger.warning("Proxy data no es un diccionario", extra={"data": proxy_data})
                        stats["failed"] += 1
                        continue

                    proxy_address = proxy_data.get("proxy", "").strip()
                    proxy_type = proxy_data.get("type", "UNKNOWN").strip().upper()
                    country = proxy_data.get("country", "").strip() or None

                    if not proxy_address:
                        logger.warning("Proxy sin dirección", extra={"data": proxy_data})
                        stats["failed"] += 1
                        continue

                    # Verificar si el proxy ya existe
                    existing_proxy = await crud_shadowmere.get_proxy_by_address(session, proxy_address)

                    if existing_proxy:
                        # Actualizar proxy existente
                        existing_proxy.proxy_type = proxy_type
                        if country:
                            existing_proxy.country = country
                        existing_proxy.is_working = True
                        existing_proxy.updated_at = datetime.now(timezone.utc)
                        session.add(existing_proxy)
                        stats["updated"] += 1
                        logger.debug("Proxy actualizado", extra={"proxy_address": proxy_address})
                    else:
                        # Crear nuevo proxy
                        await crud_shadowmere.create_proxy(
                            session,
                            proxy_address=proxy_address,
                            proxy_type=proxy_type,
                            country=country,
                            commit=False
                        )
                        stats["created"] += 1
                        logger.debug("Proxy creado", extra={"proxy_address": proxy_address})

                except Exception as e:
                    logger.warning(
                        "Error procesando proxy individual",
                        extra={"data": proxy_data, "error": str(e)}
                    )
                    stats["failed"] += 1
                    continue

            # Commit de todos los cambios
            try:
                await session.commit()
                logger.info(
                    "Sincronización completada",
                    extra=stats
                )
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error commiteando sincronización de proxies")
                raise

            return stats

        except RuntimeError:
            raise
        except SQLAlchemyError:
            logger.exception("Error en base de datos durante sincronización")
            raise
        except Exception as e:
            logger.exception("Error inesperado durante sincronización")
            raise RuntimeError(f"Error sincronizando proxies: {e}") from e

    async def validate_proxy(self, proxy_address: str, timeout: int = 10) -> bool:
        """
        Valida si un proxy funciona intentando conectar a través de él.
        Mide el tiempo de respuesta.

        Args:
            proxy_address: Dirección del proxy (IP:puerto)
            timeout: Timeout en segundos para la validación

        Returns:
            True si el proxy responde correctamente, False en caso contrario
        """
        if not proxy_address or not proxy_address.strip():
            logger.warning("proxy_address vacío para validación")
            return False

        try:
            # Parsear dirección
            parts = proxy_address.strip().split(":")
            if len(parts) != 2:
                logger.warning("Formato de proxy inválido", extra={"proxy_address": proxy_address})
                return False

            host, port_str = parts
            try:
                port = int(port_str)
            except ValueError:
                logger.warning("Puerto inválido", extra={"proxy_address": proxy_address})
                return False

            # Intentar conexión simple (TCP handshake)
            start_time = time.time()
            timeout_obj = aiohttp.ClientTimeout(total=timeout)

            try:
                async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                    # Intentar GET a un sitio simple a través del proxy
                    proxy_url = f"http://{proxy_address}"
                    async with session.get("http://httpbin.org/ip", proxy=proxy_url, timeout=timeout) as resp:
                        response_time = (time.time() - start_time) * 1000  # en ms
                        is_working = resp.status == 200
                        logger.debug(
                            "Proxy validado",
                            extra={
                                "proxy_address": proxy_address,
                                "is_working": is_working,
                                "response_time_ms": response_time
                            }
                        )
                        return is_working
            except asyncio.TimeoutError:
                logger.debug("Timeout validando proxy", extra={"proxy_address": proxy_address})
                return False
            except aiohttp.ClientError as e:
                logger.debug(
                    "Error de conexión validando proxy",
                    extra={"proxy_address": proxy_address, "error": str(e)}
                )
                return False

        except Exception as e:
            logger.warning(
                "Error inesperado validando proxy",
                extra={"proxy_address": proxy_address, "error": str(e)}
            )
            return False

    async def get_top_working_proxies(
        self,
        session: AsyncSession,
        limit: int = 10
    ) -> List[models.ShadowmereProxy]:
        """
        Obtiene los mejores proxies que están funcionando.
        Ordenados por tiempo de respuesta más rápido.

        Args:
            session: Sesión async de SQLAlchemy
            limit: Número máximo de proxies a retornar (default: 10)

        Returns:
            Lista de proxies funcionando ordenados por velocidad

        Raises:
            ValueError: Si limit es inválido
            SQLAlchemyError: Si hay error en la base de datos
        """
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit debe ser un entero positivo")

        try:
            logger.debug("Obteniendo top proxies funcionando", extra={"limit": limit})
            proxies = await crud_shadowmere.get_all_working_proxies(session, limit=limit)
            logger.info(
                "Top proxies obtenidos",
                extra={"count": len(proxies), "limit": limit}
            )
            return proxies
        except SQLAlchemyError:
            logger.exception("Error obteniendo top proxies")
            raise

    async def cleanup_old_proxies(
        self,
        session: AsyncSession,
        days: int = 30
    ) -> int:
        """
        Limpia (elimina) proxies más antiguos que el número de días especificado.
        Útil para mantener la base de datos limpia.

        Args:
            session: Sesión async de SQLAlchemy
            days: Número de días (default: 30)

        Returns:
            Número de proxies eliminados

        Raises:
            ValueError: Si days es inválido
            SQLAlchemyError: Si hay error en la base de datos
        """
        if not isinstance(days, int) or days <= 0:
            raise ValueError("days debe ser un entero positivo")

        try:
            logger.info("Iniciando limpieza de proxies antiguos", extra={"days": days})
            count = await crud_shadowmere.delete_old_proxies(session, days=days, commit=True)
            logger.info("Limpieza completada", extra={"deleted_count": count, "days": days})
            return count
        except SQLAlchemyError:
            logger.exception("Error limpiando proxies antiguos")
            raise

    async def get_proxy_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """
        Obtiene estadísticas completas sobre los proxies almacenados.

        Args:
            session: Sesión async de SQLAlchemy

        Returns:
            Diccionario con estadísticas:
            {
                "total": int,
                "working": int,
                "not_working": int,
                "by_type": {"SOCKS5": int, ...},
                "by_country": {"US": int, ...}
            }

        Raises:
            SQLAlchemyError: Si hay error en la base de datos
        """
        try:
            logger.debug("Obteniendo estadísticas de proxies")
            stats = await crud_shadowmere.get_proxy_stats(session)
            logger.info("Estadísticas obtenidas", extra={"stats": stats})
            return stats
        except SQLAlchemyError:
            logger.exception("Error obteniendo estadísticas de proxies")
            raise

    async def validate_and_update_proxies(
        self,
        session: AsyncSession,
        proxy_addresses: Optional[List[str]] = None,
        batch_size: int = 5
    ) -> Dict[str, int]:
        """
        Valida un conjunto de proxies y actualiza su estado en la BD.
        Ejecuta validaciones en paralelo por lotes.

        Args:
            session: Sesión async de SQLAlchemy
            proxy_addresses: Lista de direcciones de proxy a validar. Si es None, valida todos.
            batch_size: Número de proxies a validar en paralelo (default: 5)

        Returns:
            Diccionario con estadísticas:
            {
                "validated": int,
                "working": int,
                "not_working": int
            }

        Raises:
            SQLAlchemyError: Si hay error en la base de datos
        """
        stats = {"validated": 0, "working": 0, "not_working": 0}

        try:
            # Si no se especifican proxies, obtener todos
            if proxy_addresses is None:
                logger.debug("Obteniendo todos los proxies para validación")
                proxies = await crud_shadowmere.get_all_working_proxies(session, limit=1000)
                proxy_addresses = [p.proxy_address for p in proxies]

            if not proxy_addresses:
                logger.info("No hay proxies para validar")
                return stats

            logger.info(
                "Iniciando validación de proxies",
                extra={"total": len(proxy_addresses), "batch_size": batch_size}
            )

            # Procesar en lotes
            for i in range(0, len(proxy_addresses), batch_size):
                batch = proxy_addresses[i : i + batch_size]
                tasks = [self.validate_proxy(addr) for addr in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for proxy_address, result in zip(batch, results):
                    try:
                        is_working = result if isinstance(result, bool) else False

                        # Actualizar en BD
                        await crud_shadowmere.update_proxy_status(
                            session,
                            proxy_address=proxy_address,
                            is_working=is_working,
                            commit=False
                        )

                        stats["validated"] += 1
                        if is_working:
                            stats["working"] += 1
                        else:
                            stats["not_working"] += 1

                    except Exception as e:
                        logger.warning(
                            "Error actualizando proxy después de validación",
                            extra={"proxy_address": proxy_address, "error": str(e)}
                        )

            # Commit final
            try:
                await session.commit()
                logger.info("Validación completada", extra=stats)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception("Error commiteando validación de proxies")
                raise

            return stats

        except SQLAlchemyError:
            logger.exception("Error en base de datos durante validación")
            raise
        except Exception as e:
            logger.exception("Error inesperado durante validación de proxies")
            raise RuntimeError(f"Error validando proxies: {e}") from e


__all__ = [
    "ShadowmereService",
]
