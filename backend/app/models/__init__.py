"""ORM-модели. Импорт здесь регистрирует их в метаданных Base —
это нужно и приложению, и Alembic для автогенерации миграций.
"""
from app.models.booking import Booking
from app.models.event import Event
from app.models.hold import Hold
from app.models.seat import Seat
from app.models.ticket import Ticket
from app.models.tour import Tour
from app.models.zone import Zone

__all__ = ["Tour", "Event", "Zone", "Seat", "Hold", "Booking", "Ticket"]
