"""Роуты события: детали и карта мест."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.event import EventDetail
from app.schemas.seat import SeatMapResponse
from app.services import catalog_service

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/{event_id}", response_model=EventDetail)
def get_event(event_id: int, db: Session = Depends(get_db)) -> EventDetail:
    event = catalog_service.get_event_detail(db, event_id)
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.get("/{event_id}/seats", response_model=SeatMapResponse)
def get_seat_map(event_id: int, db: Session = Depends(get_db)) -> SeatMapResponse:
    seat_map = catalog_service.get_seat_map(db, event_id)
    if seat_map is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found")
    return seat_map
