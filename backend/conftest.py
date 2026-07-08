"""Общие фикстуры pytest.

Тесты идут на настоящем Postgres (отдельная БД `afterglow_test`), потому что
конкурентный тест опирается на блокировки строк (`SELECT ... FOR UPDATE`),
которых нет в SQLite.
"""
import os
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Event, Seat, Tour, Zone

# Подключение к служебной БД (для CREATE DATABASE) и к тестовой БД.
ADMIN_URL = os.environ.get(
    "TEST_ADMIN_URL", "postgresql+psycopg://afterglow:afterglow@db:5432/postgres"
)
TEST_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://afterglow:afterglow@db:5432/afterglow_test",
)

_TABLES = ["tickets", "holds", "seats", "zones", "events", "tours", "bookings"]


@pytest.fixture(scope="session")
def engine():
    # Создаём тестовую БД, если её ещё нет.
    admin = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'afterglow_test'")
        ).scalar()
        if not exists:
            conn.execute(text("CREATE DATABASE afterglow_test"))
    admin.dispose()

    eng = create_engine(TEST_URL)
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def SessionFactory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def seeded(SessionFactory):
    """Чистая БД + минимальный набор: событие, зона, 5 мест. Возвращает id."""
    db = SessionFactory()
    try:
        db.execute(text("TRUNCATE " + ", ".join(_TABLES) + " RESTART IDENTITY CASCADE"))
        db.commit()

        tour = Tour(artist="TEST", title="T", description="")
        db.add(tour)
        db.flush()
        event = Event(
            tour_id=tour.id,
            city="X",
            venue="Y",
            starts_at=datetime.now(timezone.utc) + timedelta(days=10),
            status="on_sale",
        )
        db.add(event)
        db.flush()
        zone = Zone(
            event_id=event.id, name="Z", price_cents=1000, color="#000000", display_order=0
        )
        db.add(zone)
        db.flush()

        seat_ids = []
        for i in range(1, 6):
            seat = Seat(event_id=event.id, zone_id=zone.id, row="A", number=i, x=i, y=0)
            db.add(seat)
            db.flush()
            seat_ids.append(seat.id)
        db.commit()

        return {"event_id": event.id, "zone_id": zone.id, "seat_ids": seat_ids}
    finally:
        db.close()
