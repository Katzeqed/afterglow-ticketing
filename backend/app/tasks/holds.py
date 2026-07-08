"""Периодическая уборка истёкших холдов: освобождает места обратно в продажу."""
from datetime import datetime, timezone

from sqlalchemy import select

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Hold, Seat


@celery_app.task(name="app.tasks.holds.expire_holds")
def expire_holds() -> dict:
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        # skip_locked: не ждём холды, которые прямо сейчас оплачиваются.
        holds = (
            db.execute(
                select(Hold)
                .where(Hold.status == "active", Hold.expires_at < now)
                .with_for_update(skip_locked=True)
            )
            .scalars()
            .all()
        )
        released = 0
        for hold in holds:
            seats = (
                db.execute(
                    select(Seat).where(Seat.hold_id == hold.id).with_for_update()
                )
                .scalars()
                .all()
            )
            for seat in seats:
                if seat.status == "held":
                    seat.status = "available"
                    seat.held_until = None
                    seat.hold_id = None
                    released += 1
            hold.status = "expired"
        db.commit()
        return {"expired_holds": len(holds), "released_seats": released}
    finally:
        db.close()
