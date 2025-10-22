# services/vpn_crud.py

from __future__ import annotations
from typing import Optional, List, Dict, Any, Literal
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from database import models
from database.crud import vpn as crud_vpn, users as crud_users, payments as crud_payments, logs as crud_logs
from services import vpn as vpn_service, payments as payments_service
from utils.helpers import log_error_and_notify

logger = logging.getLogger(__name__)


class VPNCrudService:
    """Servicio CRUD para operaciones de VPN con lógica de negocio integrada."""

    @staticmethod
    async def create_vpn(
        session: AsyncSession,
        user_id: str,
        vpn_type: Literal["wireguard", "outline"],
        months: int,
        payment_method: Literal["stars", "qvapay"],
        *,
        is_trial: bool = False,
        commit: bool = True,
    ) -> Optional[models.VPNConfig]:
        """
        Crea una nueva VPN con pago integrado.

        Args:
            session: Sesión de base de datos
            user_id: ID del usuario
            vpn_type: Tipo de VPN
            months: Número de meses
            payment_method: Método de pago
            is_trial: Si es trial
            commit: Si hacer commit de la transacción

        Returns:
            VPNConfig creada o None si falla
        """
        try:
            # Validar parámetros
            if vpn_type not in ("wireguard", "outline"):
                raise ValueError(f"Tipo VPN no soportado: {vpn_type}")

            if months < 1:
                raise ValueError("Número de meses inválido")

            if payment_method not in ("stars", "qvapay"):
                raise ValueError(f"Método de pago no soportado: {payment_method}")

            # Para trials, crear directamente sin pago
            if is_trial:
                # Verificar que no tenga trial activo
                existing_trial = await crud_vpn.get_active_trial_for_user(session, user_id)
                if existing_trial:
                    raise ValueError("Usuario ya tiene un trial activo")

                # Crear VPN trial
                vpn = await crud_vpn.create_trial_vpn(
                    session=session,
                    user_id=user_id,
                    vpn_type=vpn_type,
                    config_name=f"Trial {vpn_type.capitalize()}",
                    config_data={},  # Se llenará en el servicio VPN
                    duration_days=7,
                    commit=False
                )

                # Activar la VPN usando el servicio
                activated_vpn = await vpn_service.activate_vpn_for_user(
                    session, user_id, vpn_type, months
                )

                if activated_vpn and commit:
                    await session.commit()
                    await crud_logs.create_audit_log(
                        session=session,
                        user_id=user_id,
                        action="vpn_trial_created",
                        payload={
                            "vpn_id": activated_vpn.id,
                            "vpn_type": vpn_type,
                            "months": months
                        },
                        commit=False
                    )

                return activated_vpn

            # Para pagos, procesar pago primero
            else:
                # Crear pago
                payment = await payments_service.create_vpn_payment(
                    session, user_id, vpn_type, months
                )
                if not payment:
                    raise ValueError("No se pudo crear el pago")

                # Marcar pago como pagado (para QvaPay se hace inmediatamente)
                if payment_method == "qvapay":
                    payment = await payments_service.mark_as_paid(session, payment.id)
                    if not payment:
                        raise ValueError("No se pudo procesar el pago QvaPay")

                # Activar VPN
                vpn = await vpn_service.activate_vpn_for_user(
                    session, user_id, vpn_type, months
                )
                if not vpn:
                    raise ValueError("No se pudo activar la VPN")

                if commit:
                    await session.commit()
                    await crud_logs.create_audit_log(
                        session=session,
                        user_id=user_id,
                        action="vpn_created",
                        payload={
                            "vpn_id": vpn.id,
                            "vpn_type": vpn_type,
                            "months": months,
                            "payment_method": payment_method,
                            "payment_id": payment.id
                        },
                        commit=False
                    )

                return vpn

        except ValueError as e:
            logger.error(f"Error de validación creando VPN: {e}", extra={"user_id": user_id})
            if commit:
                await session.rollback()
            raise
        except SQLAlchemyError as e:
            logger.exception(f"Error de BD creando VPN: {e}", extra={"user_id": user_id})
            if commit:
                await session.rollback()
            raise
        except Exception as e:
            logger.exception(f"Error inesperado creando VPN: {e}", extra={"user_id": user_id})
            if commit:
                await session.rollback()
            raise

    @staticmethod
    async def list_user_vpns(
        session: AsyncSession,
        user_id: str
    ) -> List[models.VPNConfig]:
        """
        Lista todas las VPNs de un usuario.

        Args:
            session: Sesión de base de datos
            user_id: ID del usuario

        Returns:
            Lista de VPNConfigs
        """
        try:
            vpns = await crud_vpn.get_vpn_configs_for_user(session, user_id)
            logger.info(f"Listadas {len(vpns)} VPNs para usuario {user_id}", extra={"user_id": user_id})
            return vpns
        except SQLAlchemyError as e:
            logger.exception(f"Error listando VPNs para usuario {user_id}: {e}", extra={"user_id": user_id})
            raise

    @staticmethod
    async def get_vpn_by_id(
        session: AsyncSession,
        vpn_id: str
    ) -> Optional[models.VPNConfig]:
        """
        Obtiene una VPN por ID.

        Args:
            session: Sesión de base de datos
            vpn_id: ID de la VPN

        Returns:
            VPNConfig o None
        """
        try:
            vpn = await crud_vpn.get_vpn_config(session, vpn_id)
            return vpn
        except SQLAlchemyError as e:
            logger.exception(f"Error obteniendo VPN {vpn_id}: {e}")
            raise

    @staticmethod
    async def revoke_vpn(
        session: AsyncSession,
        vpn_id: str,
        user_id: str,
        *,
        commit: bool = True,
    ) -> Optional[models.VPNConfig]:
        """
        Revoca una VPN verificando permisos.

        Args:
            session: Sesión de base de datos
            vpn_id: ID de la VPN
            user_id: ID del usuario que solicita la revocación
            commit: Si hacer commit

        Returns:
            VPNConfig revocada o None si no encontrada o sin permisos
        """
        try:
            # Obtener VPN
            vpn = await crud_vpn.get_vpn_config(session, vpn_id)
            if not vpn:
                return None

            # Verificar permisos
            if not await VPNCrudService._check_vpn_ownership_or_admin(session, vpn, user_id):
                return None

            # Revocar usando servicio VPN
            revoked_vpn = await vpn_service.revoke_vpn(session, vpn_id, vpn.vpn_type)
            if not revoked_vpn:
                return None

            if commit:
                await session.commit()
                await crud_logs.create_audit_log(
                    session=session,
                    user_id=user_id,
                    action="vpn_revoked",
                    payload={
                        "vpn_id": vpn_id,
                        "vpn_type": vpn.vpn_type
                    },
                    commit=False
                )

            return revoked_vpn

        except SQLAlchemyError as e:
            logger.exception(f"Error revocando VPN {vpn_id}: {e}", extra={"user_id": user_id})
            if commit:
                await session.rollback()
            raise
        except Exception as e:
            logger.exception(f"Error inesperado revocando VPN {vpn_id}: {e}", extra={"user_id": user_id})
            if commit:
                await session.rollback()
            raise

    @staticmethod
    async def _check_vpn_ownership_or_admin(
        session: AsyncSession,
        vpn: models.VPNConfig,
        user_id: str
    ) -> bool:
        """
        Verifica si el usuario es propietario de la VPN o es admin.

        Args:
            session: Sesión de base de datos
            vpn: VPN a verificar
            user_id: ID del usuario

        Returns:
            True si tiene permisos, False en caso contrario
        """
        try:
            if vpn.user_id == user_id:
                return True
            return await crud_users.is_user_admin(session, user_id)
        except SQLAlchemyError as e:
            logger.exception(f"Error verificando permisos para VPN {vpn.id}: {e}")
            return False

    @staticmethod
    async def calculate_vpn_price(
        months: int,
        payment_method: Literal["stars", "qvapay"] = "stars"
    ) -> Dict[str, Any]:
        """
        Calcula el precio de una VPN.

        Args:
            months: Número de meses
            payment_method: Método de pago

        Returns:
            Diccionario con precios calculados
        """
        try:
            price = await payments_service.calculate_price(months, payment_method)
            return {
                "months": months,
                "usd": price["usd"],
                "stars": price["stars"],
                "payment_method": payment_method,
                "qvapay_balance_needed": price.get("qvapay_balance_needed")
            }
        except Exception as e:
            logger.exception(f"Error calculando precio: {e}")
            raise

    @staticmethod
    async def check_qvapay_balance(
        session: AsyncSession,
        user_id: str,
        required_amount: float
    ) -> Dict[str, Any]:
        """
        Verifica el balance de QvaPay del usuario.

        Args:
            session: Sesión de base de datos
            user_id: ID del usuario
            required_amount: Monto requerido

        Returns:
            Dict con información del balance
        """
        try:
            # Obtener usuario
            db_user = await crud_users.get_user_by_telegram_id(session, int(user_id))
            if not db_user or not db_user.qvapay_app_id or not db_user.qvapay_user_id:
                raise ValueError("Usuario no tiene QvaPay vinculado")

            # Obtener balance
            balance_info = await payments_service.get_user_qvapay_balance(
                db_user.qvapay_app_id, db_user.qvapay_user_id
            )

            usd_balance = balance_info.get("balances", {}).get("USD", 0)
            has_sufficient_balance = usd_balance >= required_amount

            return {
                "has_sufficient_balance": has_sufficient_balance,
                "current_balance": usd_balance,
                "required_amount": required_amount,
                "deficit": max(0, required_amount - usd_balance)
            }

        except Exception as e:
            logger.exception(f"Error verificando balance QvaPay: {e}")
            raise

    @staticmethod
    async def process_qvapay_payment(
        session: AsyncSession,
        user_id: str,
        vpn_type: Literal["wireguard", "outline"],
        months: int,
        *,
        commit: bool = True,
    ) -> Optional[models.VPNConfig]:
        """
        Procesa un pago completo con QvaPay y crea la VPN.

        Args:
            session: Sesión de base de datos
            user_id: ID del usuario
            vpn_type: Tipo de VPN
            months: Número de meses
            commit: Si hacer commit

        Returns:
            VPNConfig creada o None si falla
        """
        try:
            # Obtener usuario
            db_user = await crud_users.get_user_by_telegram_id(session, int(user_id))
            if not db_user:
                raise ValueError("Usuario no encontrado")

            # Calcular precio
            price_info = await VPNCrudService.calculate_vpn_price(months, "qvapay")
            amount_usd = price_info["usd"]

            # Verificar balance
            balance_check = await VPNCrudService.check_qvapay_balance(
                session, user_id, amount_usd
            )
            if not balance_check["has_sufficient_balance"]:
                raise ValueError(
                    f"Balance insuficiente. Tiene ${balance_check['current_balance']:.2f} USD, "
                    f"necesita ${balance_check['required_amount']:.2f} USD"
                )

            # Procesar pago
            payment_result = await payments_service.process_qvapay_payment(
                db_user.qvapay_app_id, db_user.qvapay_user_id, amount_usd
            )

            # Validar pago
            if not await payments_service.validate_qvapay_payment(payment_result):
                raise ValueError("Pago QvaPay inválido")

            # Crear VPN
            vpn = await VPNCrudService.create_vpn(
                session=session,
                user_id=user_id,
                vpn_type=vpn_type,
                months=months,
                payment_method="qvapay",
                is_trial=False,
                commit=commit
            )

            return vpn

        except Exception as e:
            logger.exception(f"Error procesando pago QvaPay: {e}")
            if commit:
                await session.rollback()
            raise