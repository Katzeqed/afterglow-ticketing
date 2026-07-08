"""Общие помощники для моделей."""
from datetime import datetime, timezone


def utcnow() -> datetime:
    """Текущее время в UTC (timezone-aware)."""
    return datetime.now(timezone.utc)
