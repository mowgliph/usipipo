"""
Modelos SQLAlchemy para el sistema de logros.

Author: uSipipo Team
Version: 1.0.0
"""

from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Date, BigInteger, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class AchievementModel(Base):
    """Modelo de logros."""
    __tablename__ = 'achievements'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)
    tier = Column(String, nullable=False)
    requirement_value = Column(Integer, nullable=False)
    reward_stars = Column(Integer, nullable=False)
    icon = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relaciones
    user_achievements = relationship("UserAchievementModel", back_populates="achievement")

class UserStatsModel(Base):
    """Modelo de estadísticas de usuarios."""
    __tablename__ = 'user_stats'
    
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), primary_key=True)
    total_data_consumed_gb = Column(Float, nullable=False, default=0.0)
    days_active = Column(Integer, nullable=False, default=0)
    total_referrals = Column(Integer, nullable=False, default=0)
    total_stars_deposited = Column(Integer, nullable=False, default=0)
    total_keys_created = Column(Integer, nullable=False, default=0)
    total_games_won = Column(Integer, nullable=False, default=0)
    vip_months_purchased = Column(Integer, nullable=False, default=0)
    last_active_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relaciones
    user = relationship("UserModel", back_populates="stats")

class UserAchievementModel(Base):
    """Modelo de progreso de logros de usuarios."""
    __tablename__ = 'user_achievements'
    
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), primary_key=True)
    achievement_id = Column(String, ForeignKey('achievements.id'), primary_key=True)
    current_value = Column(Integer, nullable=False, default=0)
    is_completed = Column(Boolean, nullable=False, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    reward_claimed = Column(Boolean, nullable=False, default=False)
    reward_claimed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relaciones
    user = relationship("UserModel", back_populates="achievements")
    achievement = relationship("AchievementModel", back_populates="user_achievements")
