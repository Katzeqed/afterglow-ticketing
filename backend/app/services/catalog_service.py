"""Бизнес-логика чтения каталога: тур, события, карта мест.

Здесь же — правило «эффективного статуса»: место со статусом `held`,
у которого срок удержания истёк, считается свободным (не дожидаясь воркера).
"""
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Event, Seat, Tour, Zone
from app.schemas.event import EventDetail, ZoneSummary
from app.schemas.seat import SeatMapResponse, SeatOut, ZoneWithSeats
from app.schemas.tour import EventSummary, TourResponse
from app.services.availability import effective_status as _effective_status


def get_tour(db: Session) -> TourResponse | None:
    """Тур (единственный) + его события по возрастанию даты."""
    tour = db.execute(select(Tour).order_by(Tour.id)).scalars().first()
    if tour is None:
        return None
    events = (
        db.execute(
            select(Event)
            .where(Event.tour_id == tour.id)
            .order_by(Event.starts_at)
        )
        .scalars()
        .all()
    )
    return TourResponse(
        artist=tour.artist,
        title=tour.title,
        description=tour.description,
        events=[EventSummary.model_validate(e) for e in events],
    )


def get_event_detail(db: Session, event_id: int) -> EventDetail | None:
    """Детали события со сводкой по зонам (всего/свободно мест)."""
    event = db.get(Event, event_id)
    if event is None:
        return None

    zones = (
        db.execute(
            select(Zone).where(Zone.event_id == event_id).order_by(Zone.display_order)
        )
        .scalars()
        .all()
    )
    # Одним запросом берём все места события и группируем по зоне.
    seats = db.execute(select(Seat).where(Seat.event_id == event_id)).scalars().all()
    now = datetime.now(timezone.utc)
    by_zone: dict[int, list[Seat]] = defaultdict(list)
    for s in seats:
        by_zone[s.zone_id].append(s)

    zone_summaries = [
        ZoneSummary(
            id=z.id,
            name=z.name,
            price_cents=z.price_cents,
            color=z.color,
            display_order=z.display_order,
            total_seats=len(by_zone[z.id]),
            available_seats=sum(
                1 for s in by_zone[z.id] if _effective_status(s, now) == "available"
            ),
        )
        for z in zones
    ]

    return EventDetail(
        id=event.id,
        city=event.city,
        venue=event.venue,
        starts_at=event.starts_at,
        status=event.status,
        zones=zone_summaries,
    )


def get_seat_map(db: Session, event_id: int) -> SeatMapResponse | None:
    """Карта мест: зоны с вложенными местами (координаты + статус)."""
    event = db.get(Event, event_id)
    if event is None:
        return None

    zones = (
        db.execute(
            select(Zone).where(Zone.event_id == event_id).order_by(Zone.display_order)
        )
        .scalars()
        .all()
    )
    seats = (
        db.execute(
            select(Seat)
            .where(Seat.event_id == event_id)
            .order_by(Seat.row, Seat.number)
        )
        .scalars()
        .all()
    )
    now = datetime.now(timezone.utc)
    by_zone: dict[int, list[Seat]] = defaultdict(list)
    for s in seats:
        by_zone[s.zone_id].append(s)

    zones_out = [
        ZoneWithSeats(
            id=z.id,
            name=z.name,
            price_cents=z.price_cents,
            color=z.color,
            display_order=z.display_order,
            seats=[
                SeatOut(
                    id=s.id,
                    row=s.row,
                    number=s.number,
                    x=s.x,
                    y=s.y,
                    status=_effective_status(s, now),
                )
                for s in by_zone[z.id]
            ],
        )
        for z in zones
    ]

    return SeatMapResponse(event_id=event.id, zones=zones_out)
