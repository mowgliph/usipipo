# database/models.py
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, Dict, List

from sqlalchemy import (
    String,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
    func,
    Index,
    CheckConstraint,
    Float,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.mysql import CHAR, JSON as MYSQL_JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base


def gen_uuid_str() -> str:
    return str(uuid.uuid4())


# Allowed literal values for columns enforced via CheckConstraint at DB level and validated in services
VPN_TYPES = ("outline", "wireguard", "none")
VPN_STATUSES = ("active", "revoked", "expired", "pending")
PAYMENT_STATUSES = ("pending", "completed", "failed", "refunded")
IP_TYPES = ("wireguard_trial", "outline_trial", "wireguard_paid", "outline_paid") # Añadido para IPManager
PROXY_STATUSES = ("active", "revoked", "expired")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid_str)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superadmin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.utc_timestamp(), nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    qvapay_user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    qvapay_app_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    qvapay_linked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    qvapay_last_balance_check: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    settings: Mapped[List["UserSetting"]] = relationship("UserSetting", back_populates="user", cascade="all, delete-orphan")
    vpnconfigs: Mapped[List["VPNConfig"]] = relationship("VPNConfig", back_populates="user", cascade="all, delete-orphan")
    roles: Mapped[List["UserRole"]] = relationship("UserRole", back_populates="user", cascade="all, delete-orphan", foreign_keys="[UserRole.user_id]")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    assigned_ips: Mapped[List["IPManager"]] = relationship("IPManager", back_populates="user", cascade="all, delete-orphan", foreign_keys="[IPManager.assigned_to_user_id]") # Relación con IPManager
    mtproto_proxies: Mapped[List["MTProtoProxy"]] = relationship("MTProtoProxy", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_users_qvapay_user_id", "qvapay_user_id"),
    )




class UserSetting(Base):
    __tablename__ = "user_settings"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    setting_key: Mapped[str] = mapped_column(String(64), nullable=False)
    setting_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.utc_timestamp(), onupdate=func.utc_timestamp(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="settings")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid_str)
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[Optional[Dict]] = mapped_column(MYSQL_JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.utc_timestamp(), nullable=False)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="logs")


class VPNConfig(Base):
    __tablename__ = "vpn_configs"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    vpn_type: Mapped[str] = mapped_column(String(16), nullable=False)
    config_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    config_data: Mapped[Optional[Dict]] = mapped_column(MYSQL_JSON, nullable=True)
    bandwidth_used_mb: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.utc_timestamp(), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    extra_data: Mapped[Optional[Dict]] = mapped_column(MYSQL_JSON, nullable=True)
    is_trial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="vpnconfigs")

    __table_args__ = (
        CheckConstraint(f"vpn_type IN {VPN_TYPES}", name="ck_vpnconfigs_vpn_type"),
        CheckConstraint(f"status IN {VPN_STATUSES}", name="ck_vpnconfigs_status"),
    )


class IPManager(Base):
    """
    Gestiona IPs disponibles/ocupadas para VPNs (trial y pago)
    """
    __tablename__ = "ip_manager"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid_str)
    ip_address: Mapped[str] = mapped_column(String(45), unique=True, nullable=False)  # IPv4 o IPv6
    ip_type: Mapped[str] = mapped_column(String(20), nullable=False)  # wireguard_trial, outline_trial, etc.
    assigned_to_user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    extra_data: Mapped[Optional[Dict]] = mapped_column(MYSQL_JSON, nullable=True)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="assigned_ips")

    __table_args__ = (
        CheckConstraint(f"ip_type IN {IP_TYPES}", name="ck_ip_manager_ip_type"),
        Index("ix_ip_manager_type_available", "ip_type", "is_available"),
    )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid_str)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.utc_timestamp(), nullable=False)

    users: Mapped[List["UserRole"]] = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")


class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    granted_by: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    granted_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.utc_timestamp(), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="roles", foreign_keys=[user_id])
    granted_by_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[granted_by])
    role: Mapped["Role"] = relationship("Role", back_populates="users")


class Payment(Base):
    """
    Modelo para pagos con estrellas de Telegram.
    Maneja transacciones de pago para servicios como VPN trial, VPN premium, etc.
    """
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid_str)
    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    telegram_payment_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    amount_usd: Mapped[float] = mapped_column(Float, nullable=False)
    amount_stars: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default='XTR')
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    vpn_type: Mapped[str] = mapped_column(String(16), nullable=False)
    months: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_method: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)  # stars o qvapay
    service_type: Mapped[str] = mapped_column(String(32), nullable=False, default="vpn")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.utc_timestamp(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.utc_timestamp(), onupdate=func.utc_timestamp(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="payments")

    __table_args__ = (
        CheckConstraint(f"status IN {PAYMENT_STATUSES}", name="ck_payments_status"),
        Index("ix_payments_user_id", "user_id"),
        Index("ix_payments_status", "status"),
    )


class MTProtoProxy(Base):
    """
    Gestiona proxies MTProto para Telegram.
    """
    __tablename__ = "mtproto_proxies"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    host: Mapped[str] = mapped_column(String(45), nullable=False)  # IPv4 o IPv6
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    secret: Mapped[str] = mapped_column(String(64), nullable=False)
    tag: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # Para registro con @MTProxybot
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.utc_timestamp(), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    extra_data: Mapped[Optional[Dict]] = mapped_column(MYSQL_JSON, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="mtproto_proxies")

    __table_args__ = (
        CheckConstraint(f"status IN {PROXY_STATUSES}", name="ck_mtproto_proxies_status"),
        Index("ix_mtproto_proxies_user_status", "user_id", "status"),
    )

class ShadowmereProxy(Base):
    """
    Gestiona proxies detectados por Shadowmere.
    Almacena información sobre proxies SOCKS5, SOCKS4, HTTP y HTTPS detectados.
    """
    __tablename__ = "shadowmere_proxies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    proxy_address: Mapped[str] = mapped_column(String(45), unique=True, nullable=False)  # IP:puerto
    proxy_type: Mapped[str] = mapped_column(String(16), nullable=False)  # SOCKS5, SOCKS4, HTTP, HTTPS
    country: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_working: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_checked: Mapped[datetime] = mapped_column(DateTime, server_default=func.utc_timestamp(), nullable=False)
    response_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # en ms
    detection_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.utc_timestamp(), nullable=False)
    detection_source: Mapped[str] = mapped_column(String(32), default="shadowmere", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.utc_timestamp(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.utc_timestamp(), onupdate=func.utc_timestamp(), nullable=False)

    __table_args__ = (
        Index("ix_shadowmere_proxies_proxy_address", "proxy_address"),
        Index("ix_shadowmere_proxies_is_working", "is_working"),
        Index("ix_shadowmere_proxies_last_checked", "last_checked"),
    )

    def __repr__(self) -> str:
        return f"<ShadowmereProxy(id={self.id}, proxy_address={self.proxy_address}, proxy_type={self.proxy_type}, is_working={self.is_working})>"



__all__ = [
    "User",
    "UserSetting",
    "AuditLog",
    "VPNConfig",
    "IPManager", # Añadido a __all__
    "Role",
    "UserRole",
    "Payment",
    "MTProtoProxy",
]


