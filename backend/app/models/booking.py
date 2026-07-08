"""Бронь — подтверждённая после оплаты покупка мест.

Данные карты не храним — только бренд и последние 4 цифры.
Снаружи адресуется по `reference` (а не по числовому id), чтобы
нельзя было перебирать чужие брони.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import utcnow


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False
    )
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    # pending -> confirmed | failed
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)

    payment_brand: Mapped[str | None] = mapped_column(String(20))
    payment_last4: Mapped[str | None] = mapped_column(String(4))

    # Идемпотентность: повторный POST с тем же ключом вернёт ту же бронь.
    idempotency_key: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="booking", cascade="all, delete-orphan"
    )
