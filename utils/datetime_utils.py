"""Utilities for consistent timezone-aware datetime handling."""
from datetime import datetime, timezone
from typing import Optional


def now_utc() -> datetime:
    """Return current time in UTC as timezone-aware datetime."""
    return datetime.now(timezone.utc)


def normalize_datetime(dt: Optional[datetime]) -> Optional[datetime]:
    """Normalize a datetime to timezone-aware UTC.

    - If dt is None -> None
    - If dt is naive -> assume UTC and attach tzinfo
    - If dt is aware -> convert to UTC
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
