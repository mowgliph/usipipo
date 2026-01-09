"""
Modelos SQLAlchemy unificados para uSipipo.

Todos los modelos comparten la misma Base declarativa para
asegurar integridad referencial y relaciones correctas.

Author: uSipipo Team
Version: 2.0.0
"""

from datetime import datetime, date
from typing import List, Optional
import uuid

from sqlalchemy import (
    BigInteger,
    String,
    Integer,
    Float,
    DateTime,
    Date,
    ForeignKey,
    Boolean,
    Text,
    text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Clase base única para todos los modelos de SQLAlchemy."""
    pass


# =============================================================================
# MODELO DE USUARIOS
# =============================================================================

class UserModel(Base):
    """Modelo de usuarios del sistema."""
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, server_default="active")
    max_keys: Mapped[int] = mapped_column(Integer, server_default="2")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Sistema de estrellas
    balance_stars: Mapped[int] = mapped_column(Integer, server_default="0")
    total_deposited: Mapped[int] = mapped_column(Integer, server_default="0")
    
    # Sistema de referidos
    referral_code: Mapped[Optional[str]] = mapped_column(
        String(12), unique=True, nullable=True
    )
    referred_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="SET NULL"), nullable=True
    )
    total_referral_earnings: Mapped[int] = mapped_column(Integer, server_default="0")
    
    # Sistema VIP
    is_vip: Mapped[bool] = mapped_column(Boolean, server_default="false")
    vip_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relaciones
    keys: Mapped[List["VpnKeyModel"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    tickets: Mapped[List["TicketModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    transactions: Mapped[List["TransactionModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    stats: Mapped[Optional["UserStatsModel"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    achievements: Mapped[List["UserAchievementModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    tasks: Mapped[List["UserTaskModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    conversations: Mapped[List["ConversationModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    
    # Auto-referencia para referidos
    referrals: Mapped[List["UserModel"]] = relationship(
        "UserModel",
        backref="referrer",
        remote_side=[telegram_id],
        foreign_keys=[referred_by]
    )


# =============================================================================
# MODELO DE LLAVES VPN
# =============================================================================

class VpnKeyModel(Base):
    """Modelo de llaves VPN."""
    __tablename__ = "vpn_keys"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE")
    )
    key_type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    key_data: Mapped[str] = mapped_column(String, nullable=False)
    external_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    used_bytes: Mapped[int] = mapped_column(BigInteger, server_default="0")
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    data_limit_bytes: Mapped[int] = mapped_column(
        BigInteger, server_default="10737418240"  # 10 GB
    )
    billing_reset_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relación
    owner: Mapped["UserModel"] = relationship(back_populates="keys")


# =============================================================================
# MODELO DE TICKETS
# =============================================================================

class TicketModel(Base):
    """Modelo de tickets de soporte."""
    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE")
    )
    user_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, server_default="open")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relación
    user: Mapped["UserModel"] = relationship(back_populates="tickets")


# =============================================================================
# MODELO DE TRANSACCIONES
# =============================================================================

class TransactionModel(Base):
    """Modelo de transacciones financieras."""
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE")
    )
    transaction_type: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    reference_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    telegram_payment_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relación
    user: Mapped["UserModel"] = relationship(back_populates="transactions")


# =============================================================================
# MODELOS DE LOGROS
# =============================================================================

class AchievementModel(Base):
    """Modelo de definiciones de logros."""
    __tablename__ = "achievements"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    tier: Mapped[str] = mapped_column(String, nullable=False)
    requirement_value: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_stars: Mapped[int] = mapped_column(Integer, nullable=False)
    icon: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    # Relación
    user_achievements: Mapped[List["UserAchievementModel"]] = relationship(
        back_populates="achievement"
    )


class UserStatsModel(Base):
    """Modelo de estadísticas de usuarios."""
    __tablename__ = "user_stats"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), primary_key=True
    )
    total_data_consumed_gb: Mapped[float] = mapped_column(Float, server_default="0.0")
    days_active: Mapped[int] = mapped_column(Integer, server_default="0")
    total_referrals: Mapped[int] = mapped_column(Integer, server_default="0")
    total_stars_deposited: Mapped[int] = mapped_column(Integer, server_default="0")
    total_keys_created: Mapped[int] = mapped_column(Integer, server_default="0")
    total_games_won: Mapped[int] = mapped_column(Integer, server_default="0")
    vip_months_purchased: Mapped[int] = mapped_column(Integer, server_default="0")
    last_active_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    
    # Relación
    user: Mapped["UserModel"] = relationship(back_populates="stats")


class UserAchievementModel(Base):
    """Modelo de progreso de logros de usuarios."""
    __tablename__ = "user_achievements"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), primary_key=True
    )
    achievement_id: Mapped[str] = mapped_column(
        String, ForeignKey("achievements.id", ondelete="CASCADE"), primary_key=True
    )
    current_value: Mapped[int] = mapped_column(Integer, server_default="0")
    is_completed: Mapped[bool] = mapped_column(Boolean, server_default="false")
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reward_claimed: Mapped[bool] = mapped_column(Boolean, server_default="false")
    reward_claimed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    
    # Relaciones
    user: Mapped["UserModel"] = relationship(back_populates="achievements")
    achievement: Mapped["AchievementModel"] = relationship(back_populates="user_achievements")


# =============================================================================
# MODELOS DE TAREAS
# =============================================================================

class TaskModel(Base):
    """Modelo de tareas creadas por administradores."""
    __tablename__ = "tasks"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reward_stars: Mapped[int] = mapped_column(Integer, nullable=False)
    guide_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    created_by: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    # Relación
    user_tasks: Mapped[List["UserTaskModel"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )


class UserTaskModel(Base):
    """Modelo de progreso de tareas de usuarios."""
    __tablename__ = "user_tasks"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), primary_key=True
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    )
    is_completed: Mapped[bool] = mapped_column(Boolean, server_default="false")
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reward_claimed: Mapped[bool] = mapped_column(Boolean, server_default="false")
    reward_claimed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    # Relaciones
    user: Mapped["UserModel"] = relationship(back_populates="tasks")
    task: Mapped["TaskModel"] = relationship(back_populates="user_tasks")


# =============================================================================
# MODELO DE CONVERSACIONES IA (SIP)
# =============================================================================

class ConversationModel(Base):
    """Modelo de conversaciones con el asistente IA Sip."""
    __tablename__ = "ai_conversations"
    
    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False
    )
    user_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, server_default="active")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    messages: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Relación
    user: Mapped["UserModel"] = relationship(back_populates="conversations")
