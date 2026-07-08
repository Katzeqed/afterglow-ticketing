"""Оформление брони: холд + mock-оплата -> подтверждённая бронь с билетами.

Идемпотентность и защита от гонок строятся на блокировке строки холда
(`FOR UPDATE`) и уникальном ограничении на `idempotency_key`.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Booking, Event, Hold, Seat, Ticket
from app.schemas.booking import BookingCreate, BookingResponse, TicketOut
from app.services import codes, payment_service


class BookingError(Exception):
    pass


class HoldNotFound(BookingError):
    pass


class HoldNotActive(BookingError):
    """Холд истёк, отменён или уже оплачен."""


def _build_response(db: Session, booking: Booking) -> BookingResponse:
    event = db.get(Event, booking.event_id)
    tickets = (
        db.execute(select(Ticket).where(Ticket.booking_id == booking.id).order_by(Ticket.id))
        .scalars()
        .all()
    )
    return BookingResponse(
        reference=booking.reference,
        status=booking.status,
        email=booking.email,
        event_id=event.id,
        city=event.city,
        venue=event.venue,
        starts_at=event.starts_at,
        total_cents=booking.total_cents,
        tickets=[
            TicketOut(
                code=t.code,
                seat_id=t.seat.id,
                row=t.seat.row,
                number=t.seat.number,
                zone_name=t.seat.zone.name,
                price_cents=t.seat.zone.price_cents,
            )
            for t in tickets
        ],
    )


def get_booking_by_reference(db: Session, reference: str) -> BookingResponse | None:
    booking = (
        db.execute(select(Booking).where(Booking.reference == reference)).scalars().first()
    )
    if booking is None:
        return None
    return _build_response(db, booking)


def _find_by_idempotency(db: Session, key: str) -> Booking | None:
    return db.execute(select(Booking).where(Booking.idempotency_key == key)).scalars().first()


def create_booking(db: Session, data: BookingCreate) -> BookingResponse:
    now = datetime.now(timezone.utc)

    # Блокируем холд — конкурентные запросы по этому холду сериализуются.
    hold = (
        db.execute(select(Hold).where(Hold.id == data.hold_id).with_for_update())
        .scalars()
        .first()
    )
    if hold is None:
        raise HoldNotFound()

    # Идемпотентность: тот же ключ -> та же бронь (без повторного «списания»).
    existing = _find_by_idempotency(db, data.idempotency_key)
    if existing is not None:
        db.rollback()
        return _build_response(db, existing)

    if hold.status != "active" or hold.expires_at < now:
        raise HoldNotActive()

    seats = (
        db.execute(
            select(Seat).where(Seat.hold_id == hold.id).order_by(Seat.id).with_for_update()
        )
        .scalars()
        .all()
    )
    if not seats or any(s.status != "held" or s.hold_id != hold.id for s in seats):
        raise HoldNotActive()

    total = sum(s.zone.price_cents for s in seats)

    # Оплата. При отказе — откат (холд остаётся активным, можно повторить).
    try:
        brand, last4 = payment_service.charge(
            total,
            data.payment.number,
            data.payment.expiry,
            data.payment.cvv,
            data.payment.holder,
        )
    except payment_service.PaymentDeclined:
        db.rollback()
        raise

    booking = Booking(
        reference=codes.booking_reference(),
        event_id=hold.event_id,
        email=data.email,
        total_cents=total,
        status="confirmed",
        payment_brand=brand,
        payment_last4=last4,
        idempotency_key=data.idempotency_key,
    )
    db.add(booking)
    db.flush()

    for s in seats:
        db.add(Ticket(booking_id=booking.id, seat_id=s.id, code=codes.ticket_code()))
        s.status = "booked"
        s.hold_id = None
        s.held_until = None
    hold.status = "converted"

    try:
        db.commit()
    except IntegrityError:
        # Гонка одинаковых запросов: уникальный ключ уже занят — вернём готовую бронь.
        db.rollback()
        existing = _find_by_idempotency(db, data.idempotency_key)
        if existing is not None:
            return _build_response(db, existing)
        raise

    return _build_response(db, booking)
