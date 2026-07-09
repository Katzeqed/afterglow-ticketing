"""Наполнение БД данными тура MARLOWE — Afterglow.

Идемпотентно: повторный запуск ничего не дублирует.
Запуск:  python -m app.data.seed   (внутри контейнера backend)
"""
from __future__ import annotations

import random
import string
from datetime import datetime, timedelta, timezone

from app.database import SessionLocal
from app.models import Event, Seat, Tour, Zone

# Геометрия зон на SVG-холсте (сцена сверху). Балконы — слева и справа.
# cols/rows — сетка; start_x/start_y — левый-верхний угол; dx/dy — шаг.
ZONES = [
    {"name": "VIP", "price_cents": 12000, "color": "#C0603B",
     "rows": 4, "cols": 20, "start_x": 253, "start_y": 110, "dx": 26, "dy": 30},
    {"name": "Floor", "price_cents": 8500, "color": "#6E8B74",
     "rows": 10, "cols": 24, "start_x": 201, "start_y": 250, "dx": 26, "dy": 28},
    {"name": "Balcony Left", "price_cents": 5500, "color": "#C99A4C",
     "rows": 16, "cols": 4, "start_x": 60, "start_y": 150, "dx": 24, "dy": 26},
    {"name": "Balcony Right", "price_cents": 5500, "color": "#C99A4C",
     "rows": 16, "cols": 4, "start_x": 862, "start_y": 150, "dx": 24, "dy": 26},
]

EVENTS = [
    {"city": "Berlin", "venue": "Velodrom", "in_days": 30},
    {"city": "Amsterdam", "venue": "Paradiso", "in_days": 37},
    {"city": "London", "venue": "Roundhouse", "in_days": 44},
]

FILL_RATIO = 0.5  # доля уже проданных мест (для реалистичной карты)


def _build_seats(event: Event, zone: Zone, cfg: dict) -> list[Seat]:
    """Раскладывает места зоны сеткой и считает координаты x/y для карты."""
    seats: list[Seat] = []
    for r in range(cfg["rows"]):
        row_label = string.ascii_uppercase[r]
        for c in range(cfg["cols"]):
            seats.append(
                Seat(
                    event=event,
                    zone=zone,
                    row=row_label,
                    number=c + 1,
                    x=int(cfg["start_x"] + c * cfg["dx"]),
                    y=int(cfg["start_y"] + r * cfg["dy"]),
                )
            )
    return seats


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(Tour).filter_by(artist="MARLOWE").first():
            print("seed: данные уже есть — пропускаю")
            return

        tour = Tour(
            artist="MARLOWE",
            title="Afterglow",
            description="MARLOWE returns with Afterglow - an intimate live tour across Europe.",
        )
        db.add(tour)
        db.flush()

        now = datetime.now(timezone.utc)
        total_seats = 0
        total_sold = 0

        for ev in EVENTS:
            starts_at = (now + timedelta(days=ev["in_days"])).replace(
                hour=19, minute=30, second=0, microsecond=0
            )
            event = Event(
                tour=tour,
                city=ev["city"],
                venue=ev["venue"],
                starts_at=starts_at,
                status="on_sale",
            )
            db.add(event)
            db.flush()

            event_seats: list[Seat] = []
            for order, cfg in enumerate(ZONES):
                zone = Zone(
                    event=event,
                    name=cfg["name"],
                    price_cents=cfg["price_cents"],
                    color=cfg["color"],
                    display_order=order,
                )
                db.add(zone)
                db.flush()

                seats = _build_seats(event, zone, cfg)
                db.add_all(seats)
                event_seats.extend(seats)

            # Помечаем ~50% мест как проданные, чтобы карта выглядела живой.
            sold = random.sample(event_seats, k=int(len(event_seats) * FILL_RATIO))
            for seat in sold:
                seat.status = "booked"

            total_seats += len(event_seats)
            total_sold += len(sold)

        db.commit()
        print(
            f"seed: создан тур MARLOWE — Afterglow, {len(EVENTS)} события, "
            f"{total_seats} мест ({total_sold} проданы)"
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed()
