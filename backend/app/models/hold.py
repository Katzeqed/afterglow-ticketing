"""Холд — временное удержание мест за анонимным клиентом до оплаты."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import utcnow


class Hold(Base):
    __tablename__ = "holds"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Анонимный идентификатор клиента (генерит фронт, хранит у себя).
    session_token: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    # active -> converted (оплачен) | expired (истёк) | released (отменён)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    seats: Mapped[list["Seat"]] = relationship(back_populates="hold")
