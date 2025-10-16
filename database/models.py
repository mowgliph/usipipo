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
PAYMENT_STATUSES = ("pending", "paid", "failed")
IP_TYPES = ("wireguard_trial", "outline_trial", "wireguard_paid", "outline_paid") # Añadido para IPManager


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid_str)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(256), nullable=True, index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superadmin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.utc_timestamp(), nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    settings: Mapped[List["UserSetting"]] = relationship("UserSetting", back_populates="user", cascade="all, delete-orphan")
    vpnconfigs: Mapped[List["VPNConfig"]] = relationship("VPNConfig", back_populates="user", cascade="all, delete-orphan")
    roles: Mapped[List["UserRole"]] = relationship("UserRole", back_populates="user", cascade="all, delete-orphan", foreign_keys="[UserRole.user_id]")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    assigned_ips: Mapped[List["IPManager"]] = relationship("IPManager", back_populates="user", cascade="all, delete-orphan", foreign_keys="[IPManager.assigned_to_user_id]") # Relación con IPManager


Index("ix_users_email", User.email)


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
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    vpn_type: Mapped[str] = mapped_column(String(16), nullable=False)
    months: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_usd: Mapped[float] = mapped_column(Float, nullable=False)
    amount_stars: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    amount_ton: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.utc_timestamp(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="payments")

    __table_args__ = (
        CheckConstraint(f"vpn_type IN {VPN_TYPES}", name="ck_payments_vpn_type"),
        CheckConstraint(f"status IN {PAYMENT_STATUSES}", name="ck_payments_status"),
    )


__all__ = [
    "User",
    "UserSetting",
    "AuditLog",
    "VPNConfig",
    "IPManager", # Añadido a __all__
    "Role",
    "UserRole",
    "Payment",
]