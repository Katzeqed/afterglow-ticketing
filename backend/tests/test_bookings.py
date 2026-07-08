"""Оформление брони: успех, идемпотентность, отказ карты, истёкший холд."""
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select, update

from app.models import Booking, Hold
from app.schemas.booking import BookingCreate, PaymentInput
from app.services import booking_service, hold_service
from app.services.booking_service import HoldNotActive
from app.services.payment_service import PaymentDeclined

GOOD_CARD = "4242424242424242"
DECLINE_CARD = "4000000000000002"


def _payment(number: str = GOOD_CARD) -> PaymentInput:
    return PaymentInput(number=number, expiry="12/30", cvv="123", holder="Test Fan")


def test_booking_success(SessionFactory, seeded):
    db = SessionFactory()
    try:
        hold = hold_service.create_hold(
            db, seeded["event_id"], seeded["seat_ids"][:2], "sess-book-0001"
        )
        resp = booking_service.create_booking(
            db,
            BookingCreate(
                hold_id=hold.id,
                email="fan@example.com",
                payment=_payment(),
                idempotency_key="idem-key-success-0001",
            ),
        )
        assert resp.status == "confirmed"
        assert len(resp.tickets) == 2
        assert resp.total_cents == 2000
        assert resp.reference.startswith("AG-")

        # Гостевой просмотр по reference.
        again = booking_service.get_booking_by_reference(db, resp.reference)
        assert again is not None
        assert again.reference == resp.reference
    finally:
        db.close()


def test_idempotent_replay_returns_same_booking(SessionFactory, seeded):
    db = SessionFactory()
    try:
        hold = hold_service.create_hold(
            db, seeded["event_id"], seeded["seat_ids"][:1], "sess-book-0002"
        )
        data = BookingCreate(
            hold_id=hold.id,
            email="fan@example.com",
            payment=_payment(),
            idempotency_key="idem-key-replay-000002",
        )
        first = booking_service.create_booking(db, data)
        second = booking_service.create_booking(db, data)  # тот же ключ

        assert first.reference == second.reference
        count = db.execute(select(func.count()).select_from(Booking)).scalar()
        assert count == 1  # вторая бронь не создалась
    finally:
        db.close()


def test_declined_card_keeps_hold_active(SessionFactory, seeded):
    db = SessionFactory()
    try:
        hold = hold_service.create_hold(
            db, seeded["event_id"], seeded["seat_ids"][:1], "sess-book-0003"
        )
        with pytest.raises(PaymentDeclined):
            booking_service.create_booking(
                db,
                BookingCreate(
                    hold_id=hold.id,
                    email="fan@example.com",
                    payment=_payment(DECLINE_CARD),
                    idempotency_key="idem-key-declined-0003",
                ),
            )
        # Холд жив — повтор с хорошей картой проходит.
        ok = booking_service.create_booking(
            db,
            BookingCreate(
                hold_id=hold.id,
                email="fan@example.com",
                payment=_payment(GOOD_CARD),
                idempotency_key="idem-key-retry-000003",
            ),
        )
        assert ok.status == "confirmed"
    finally:
        db.close()


def test_expired_hold_rejected(SessionFactory, seeded):
    db = SessionFactory()
    try:
        hold = hold_service.create_hold(
            db, seeded["event_id"], seeded["seat_ids"][:1], "sess-book-0004"
        )
        # Искусственно «состариваем» холд.
        db.execute(
            update(Hold)
            .where(Hold.id == hold.id)
            .values(expires_at=datetime.now(timezone.utc) - timedelta(minutes=1))
        )
        db.commit()

        with pytest.raises(HoldNotActive):
            booking_service.create_booking(
                db,
                BookingCreate(
                    hold_id=hold.id,
                    email="fan@example.com",
                    payment=_payment(),
                    idempotency_key="idem-key-expired-0004",
                ),
            )
    finally:
        db.close()
