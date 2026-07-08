"""Схемы ответа для лендинга тура."""
from datetime import datetime

from pydantic import BaseModel


class EventSummary(BaseModel):
    id: int
    city: str
    venue: str
    starts_at: datetime
    status: str

    model_config = {"from_attributes": True}


class TourResponse(BaseModel):
    artist: str
    title: str
    description: str
    events: list[EventSummary]

    model_config = {"from_attributes": True}
