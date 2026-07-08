"""Схемы карты мест: места вложены в зоны."""
from pydantic import BaseModel


class SeatOut(BaseModel):
    id: int
    row: str
    number: int
    x: int
    y: int
    status: str  # эффективный статус: available / held / booked


class ZoneWithSeats(BaseModel):
    id: int
    name: str
    price_cents: int
    color: str
    display_order: int
    seats: list[SeatOut]


class SeatMapResponse(BaseModel):
    event_id: int
    currency: str = "EUR"
    zones: list[ZoneWithSeats]
