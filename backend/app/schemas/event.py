"""Схемы деталей события (с краткой сводкой по зонам)."""
from datetime import datetime

from pydantic import BaseModel


class ZoneSummary(BaseModel):
    id: int
    name: str
    price_cents: int
    color: str
    display_order: int
    total_seats: int
    available_seats: int


class EventDetail(BaseModel):
    id: int
    city: str
    venue: str
    starts_at: datetime
    status: str
    currency: str = "EUR"
    zones: list[ZoneSummary]
