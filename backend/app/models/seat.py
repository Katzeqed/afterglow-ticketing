"""Место события.

`status` + `held_until` + `hold_id` живут прямо на месте — это позволяет
блокировать конкретную строку (`SELECT ... FOR UPDATE`) при взятии холда
и наглядно защищает от двойного бронирования.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import utcnow


class Seat(Base):
    __tablename__ = "seats"
    # В пределах зоны место однозначно определяется рядом и номером.
    __table_args__ = (
        UniqueConstraint("zone_id", "row", "number", name="uq_seat_zone_row_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # event_id денормализован (выводим из зоны), но нужен для быстрых
    # запросов и блокировок в рамках события.
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    zone_id: Mapped[int] = mapped_column(
        ForeignKey("zones.id", ondelete="CASCADE"), nullable=False, index=True
    )
    row: Mapped[str] = mapped_column(String(8), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    x: Mapped[int] = mapped_column(Integer, nullable=False)  # координаты для SVG-карты
    y: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[str] = mapped_column(String(16), default="available", nullable=False)
    held_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    hold_id: Mapped[int | None] = mapped_column(
        ForeignKey("holds.id", ondelete="SET NULL"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    event: Mapped["Event"] = relationship(back_populates="seats")
    zone: Mapped["Zone"] = relationship(back_populates="seats")
    hold: Mapped["Hold | None"] = relationship(back_populates="seats")
