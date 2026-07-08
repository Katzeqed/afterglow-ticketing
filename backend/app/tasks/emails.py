"""Отправка письма-подтверждения (мок: пишем в лог воркера)."""
import logging

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Booking

logger = logging.getLogger("afterglow.email")


@celery_app.task(name="app.tasks.emails.send_confirmation_email")
def send_confirmation_email(booking_id: int) -> None:
    db = SessionLocal()
    try:
        booking = db.get(Booking, booking_id)
        if booking is None:
            return
        # Мок: в реальном проекте — SMTP/провайдер рассылок.
        print(
            f"[email] confirmation sent to {booking.email} "
            f"for booking {booking.reference}"
        )
    finally:
        db.close()
