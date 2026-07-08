"""Наполнение БД данными тура MARLOWE — Afterglow.

Идемпотентно: повторный запуск ничего не дублирует.
Запуск:  python -m app.data.seed   (внутри контейнера backend)
"""
from __future__ import annotations

import string
from datetime import datetime, timedelta, timezone

from app.database import SessionLocal
from app.models import Event, Seat, Tour, Zone

# Ценовые зоны (одинаковая раскладка на каждом событии).
# start_y — вертикальное смещение блока на SVG-холсте (сцена сверху).
ZONES = [
    {"name": "VIP", "price_cents": 12000, "color": "#C0603B", "rows": 4, "cols": 20, "start_y": 90},
    {"name": "Floor", "price_cents": 8500, "color": "#6E8B74", "rows": 10, "cols": 24, "start_y": 250},
    {"name": "Balcony", "price_cents": 5500, "color": "#C99A4C", "rows": 6, "cols": 30, "start_y": 590},
]

# Даты тура: город, площадка, через сколько дней от «сегодня».
EVENTS = [
    {"city": "Berlin", "venue": "Velodrom", "in_days": 30},
    {"city": "Amsterdam", "venue": "Paradiso", "in_days": 37},
    {"city": "London", "venue": "Roundhouse", "in_days": 44},
]

CANVAS_CX = 500   # центр холста по горизонтали
SEAT_DX = 26      # шаг между местами в ряду
SEAT_DY = 30      # шаг между рядами


def _build_seats(event: Event, zone: Zone, cfg: dict) -> list[Seat]:
    """Раскладывает места зоны сеткой и считает координаты x/y для карты."""
    seats: list[Seat] = []
    block_width = cfg["cols"] * SEAT_DX
    start_x = CANVAS_CX - block_width / 2 + SEAT_DX / 2
    for r in range(cfg["rows"]):
        row_label = string.ascii_uppercase[r]
        for c in range(cfg["cols"]):
            seats.append(
                Seat(
                    event=event,
                    zone=zone,
                    row=row_label,
                    number=c + 1,
                    x=int(start_x + c * SEAT_DX),
                    y=int(cfg["start_y"] + r * SEAT_DY),
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
                total_seats += len(seats)

        db.commit()
        print(
            f"seed: создан тур MARLOWE — Afterglow, "
            f"{len(EVENTS)} события, {total_seats} мест"
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed()
