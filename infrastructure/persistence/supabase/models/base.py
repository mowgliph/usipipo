from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, Integer, DateTime, ForeignKey, Boolean, text
from sqlalchemy.sql import func
from typing import List, Optional
import uuid

class Base(DeclarativeBase):
    """Clase base para todos los modelos de SQLAlchemy"""
    pass

class UserModel(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, server_default="active")
    max_keys: Mapped[int] = mapped_column(Integer, server_default="2")
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    balance_stars: Mapped[int] = mapped_column(Integer, server_default="0")
    total_deposited: Mapped[int] = mapped_column(Integer, server_default="0")
    
    referral_code: Mapped[str] = mapped_column(
        String(12), unique=True, nullable=True
    )
    referred_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="SET NULL"), nullable=True
    )
    total_referral_earnings: Mapped[int] = mapped_column(Integer, server_default="0")
    
    is_vip: Mapped[bool] = mapped_column(Boolean, server_default="false")
    vip_expires_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    keys: Mapped[List["VpnKeyModel"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    
    tickets: Mapped[List["TicketModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    
    transactions: Mapped[List["TransactionModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    
    referrals: Mapped[List["UserModel"]] = relationship(
        "UserModel",
        backref="referrer",
        remote_side=[telegram_id],
        foreign_keys=[referred_by]
    )

class VpnKeyModel(Base):
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
    external_id: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    used_bytes: Mapped[int] = mapped_column(BigInteger, server_default="0")
    last_seen_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    
    data_limit_bytes: Mapped[int] = mapped_column(
        BigInteger, server_default="10737418240"
    )
    billing_reset_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    owner: Mapped["UserModel"] = relationship(back_populates="keys")

class TicketModel(Base):
    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE")
    )
    user_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, server_default="open")
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_message_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["UserModel"] = relationship(back_populates="tickets")

class TransactionModel(Base):
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
    
    reference_id: Mapped[str | None] = mapped_column(String, nullable=True)
    
    description: Mapped[str] = mapped_column(String, nullable=False)
    
    telegram_payment_id: Mapped[str | None] = mapped_column(String, nullable=True)
    
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["UserModel"] = relationship(back_populates="transactions")
