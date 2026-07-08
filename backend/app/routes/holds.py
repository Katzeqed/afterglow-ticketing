"""Роуты удержания мест."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.hold import HoldCreate, HoldResponse
from app.services import hold_service
from app.services.hold_service import SeatsNotFound, SeatsUnavailable

router = APIRouter(prefix="/api/holds", tags=["holds"])


@router.post("", response_model=HoldResponse, status_code=status.HTTP_201_CREATED)
def create_hold(data: HoldCreate, db: Session = Depends(get_db)) -> HoldResponse:
    """Удержать места на TTL минут. 409 — если хоть одно уже занято."""
    try:
        return hold_service.create_hold(
            db, data.event_id, data.seat_ids, data.session_token
        )
    except SeatsNotFound as exc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail={"error": "seats_not_found", "seat_ids": exc.seat_ids},
        )
    except SeatsUnavailable as exc:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail={"error": "seats_unavailable", "seat_ids": exc.seat_ids},
        )


@router.get("/{hold_id}", response_model=HoldResponse)
def get_hold(hold_id: int, db: Session = Depends(get_db)) -> HoldResponse:
    hold = hold_service.get_hold(db, hold_id)
    if hold is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Hold not found")
    return hold


@router.delete("/{hold_id}", status_code=status.HTTP_204_NO_CONTENT)
def release_hold(hold_id: int, db: Session = Depends(get_db)) -> Response:
    hold_service.release_hold(db, hold_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
