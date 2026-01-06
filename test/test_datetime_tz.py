from datetime import datetime, timezone, timedelta
from domain.entities.user import User


def test_is_vip_active_with_aware_expiry():
    u = User(telegram_id=1, is_vip=True, vip_expires_at=datetime.now(timezone.utc) + timedelta(days=1))
    assert u.is_vip_active() is True


def test_is_vip_inactive_with_aware_expiry_past():
    u = User(telegram_id=2, is_vip=True, vip_expires_at=datetime.now(timezone.utc) - timedelta(days=1))
    assert u.is_vip_active() is False


def test_is_vip_active_with_naive_expiry():
    future_naive = (datetime.now(timezone.utc) + timedelta(days=1)).replace(tzinfo=None)
    u = User(telegram_id=3, is_vip=True, vip_expires_at=future_naive)
    assert u.is_vip_active() is True


def test_is_vip_inactive_with_naive_expiry_past():
    past_naive = (datetime.now(timezone.utc) - timedelta(days=1)).replace(tzinfo=None)
    u = User(telegram_id=4, is_vip=True, vip_expires_at=past_naive)
    assert u.is_vip_active() is False
