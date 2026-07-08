"""Единое правило доступности места.

Место со статусом `held`, у которого истёк срок удержания, считается
свободным — не дожидаясь фонового воркера-уборщика.
"""
from datetime import datetime

from app.models import Seat


def effective_status(seat: Seat, now: datetime) -> str:
    if seat.status == "held" and seat.held_until is not None and seat.held_until < now:
        return "available"
    return seat.status


def is_available(seat: Seat, now: datetime) -> bool:
    return effective_status(seat, now) == "available"
