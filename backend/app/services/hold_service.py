"""Логика удержания мест — ядро защиты от двойного бронирования.

Взятие холда идёт в одной транзакции с блокировкой строк мест
(`SELECT ... FOR UPDATE`). Конкурентные запросы за одно место
сериализуются: первый выигрывает, остальные видят место занятым.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Hold, Seat
from app.schemas.hold import HeldSeat, HoldResponse
from app.services.availability import is_available


# --- Доменные ошибки (роут переводит их в HTTP-коды) ---------------------
class HoldError(Exception):
    pass


class SeatsNotFound(HoldError):
    """Каких-то мест нет у этого события."""

    def __init__(self, seat_ids: list[int]):
        self.seat_ids = seat_ids


class SeatsUnavailable(HoldError):
    """Места уже заняты/удержаны кем-то другим."""

    def __init__(self, seat_ids: list[int]):
        self.seat_ids = seat_ids


def _seconds_remaining(expires_at: datetime, now: datetime) -> int:
    return max(0, int((expires_at - now).total_seconds()))


def _to_response(hold: Hold, seats: list[Seat], now: datetime) -> HoldResponse:
    held_seats = [
        HeldSeat(
            id=s.id,
            row=s.row,
            number=s.number,
            zone_name=s.zone.name,
            price_cents=s.zone.price_cents,
        )
        for s in seats
    ]
    return HoldResponse(
        id=hold.id,
        event_id=hold.event_id,
        status=hold.status,
        expires_at=hold.expires_at,
        seconds_remaining=_seconds_remaining(hold.expires_at, now),
        total_cents=sum(s.zone.price_cents for s in seats),
        seats=held_seats,
    )


def create_hold(
    db: Session, event_id: int, seat_ids: list[int], session_token: str
) -> HoldResponse:
    now = datetime.now(timezone.utc)
    # Убираем дубли и сортируем — блокируем строки в одном порядке (анти-дедлок).
    ids = sorted(set(seat_ids))

    # Блокируем нужные места до конца транзакции.
    seats = (
        db.execute(
            select(Seat)
            .where(Seat.id.in_(ids), Seat.event_id == event_id)
            .order_by(Seat.id)
            .with_for_update()
        )
        .scalars()
        .all()
    )

    if len(seats) != len(ids):
        found = {s.id for s in seats}
        raise SeatsNotFound([i for i in ids if i not in found])

    unavailable = [s.id for s in seats if not is_available(s, now)]
    if unavailable:
        raise SeatsUnavailable(unavailable)

    expires_at = now + timedelta(minutes=settings.hold_ttl_minutes)
    hold = Hold(
        event_id=event_id,
        session_token=session_token,
        status="active",
        expires_at=expires_at,
    )
    db.add(hold)
    db.flush()  # получаем hold.id

    for s in seats:
        s.status = "held"
        s.held_until = expires_at
        s.hold_id = hold.id

    response = _to_response(hold, seats, now)  # собираем до commit (объекты «свежие»)
    db.commit()
    return response


def get_hold(db: Session, hold_id: int) -> HoldResponse | None:
    hold = db.get(Hold, hold_id)
    if hold is None:
        return None

    now = datetime.now(timezone.utc)
    seats = (
        db.execute(select(Seat).where(Seat.hold_id == hold_id).order_by(Seat.id))
        .scalars()
        .all()
    )

    # Активный, но просроченный холд показываем как expired.
    status = hold.status
    if status == "active" and hold.expires_at < now:
        status = "expired"

    return HoldResponse(
        id=hold.id,
        event_id=hold.event_id,
        status=status,
        expires_at=hold.expires_at,
        seconds_remaining=_seconds_remaining(hold.expires_at, now),
        total_cents=sum(s.zone.price_cents for s in seats),
        seats=[
            HeldSeat(
                id=s.id,
                row=s.row,
                number=s.number,
                zone_name=s.zone.name,
                price_cents=s.zone.price_cents,
            )
            for s in seats
        ],
    )


def release_hold(db: Session, hold_id: int) -> None:
    """Досрочно отпустить холд и освободить его места (идемпотентно)."""
    hold = db.get(Hold, hold_id)
    if hold is None or hold.status != "active":
        return

    seats = (
        db.execute(
            select(Seat).where(Seat.hold_id == hold_id).with_for_update()
        )
        .scalars()
        .all()
    )
    for s in seats:
        if s.status == "held":
            s.status = "available"
            s.held_until = None
            s.hold_id = None
    hold.status = "released"
    db.commit()
