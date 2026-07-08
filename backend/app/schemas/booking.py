"""Схемы оформления брони и оплаты."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class PaymentInput(BaseModel):
    """Данные карты. Формат проверяем здесь; бизнес-правила — в payment_service."""

    number: str
    expiry: str = Field(pattern=r"^\d{2}/\d{2}$")  # MM/YY
    cvv: str = Field(pattern=r"^\d{3,4}$")
    holder: str = Field(min_length=2, max_length=100)

    @field_validator("number")
    @classmethod
    def _normalize_number(cls, v: str) -> str:
        digits = v.replace(" ", "")
        if not (13 <= len(digits) <= 19 and digits.isdigit()):
            raise ValueError("card number must be 13-19 digits")
        return digits


class BookingCreate(BaseModel):
    hold_id: int
    email: EmailStr
    payment: PaymentInput
    idempotency_key: str = Field(min_length=16, max_length=64)


class TicketOut(BaseModel):
    code: str
    seat_id: int
    row: str
    number: int
    zone_name: str
    price_cents: int


class BookingResponse(BaseModel):
    reference: str
    status: str
    email: str
    event_id: int
    city: str
    venue: str
    starts_at: datetime
    total_cents: int
    currency: str = "EUR"
    tickets: list[TicketOut]
