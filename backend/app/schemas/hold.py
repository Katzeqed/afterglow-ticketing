"""Схемы удержания мест (hold)."""
from datetime import datetime

from pydantic import BaseModel, Field


class HoldCreate(BaseModel):
    event_id: int
    # 1..8 мест за раз (лимит совпадает с settings.max_seats_per_hold).
    seat_ids: list[int] = Field(min_length=1, max_length=8)
    # Анонимный идентификатор клиента (генерит фронт).
    session_token: str = Field(min_length=8, max_length=64)


class HeldSeat(BaseModel):
    id: int
    row: str
    number: int
    zone_name: str
    price_cents: int


class HoldResponse(BaseModel):
    id: int
    event_id: int
    status: str
    expires_at: datetime
    seconds_remaining: int
    total_cents: int
    currency: str = "EUR"
    seats: list[HeldSeat]
