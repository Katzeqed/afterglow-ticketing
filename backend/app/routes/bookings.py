"""Роуты оформления и просмотра брони."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.booking import BookingCreate, BookingResponse
from app.services import booking_service
from app.services.booking_service import HoldNotActive, HoldNotFound
from app.services.payment_service import PaymentDeclined

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(data: BookingCreate, db: Session = Depends(get_db)) -> BookingResponse:
    """Оформить бронь по холду. Идемпотентно по `idempotency_key`."""
    try:
        return booking_service.create_booking(db, data)
    except HoldNotFound:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail={"error": "hold_not_found"}
        )
    except HoldNotActive:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail={"error": "hold_expired"}
        )
    except PaymentDeclined as exc:
        raise HTTPException(
            status.HTTP_402_PAYMENT_REQUIRED,
            detail={"error": "payment_declined", "reason": exc.reason},
        )


@router.get("/{reference}", response_model=BookingResponse)
def get_booking(reference: str, db: Session = Depends(get_db)) -> BookingResponse:
    booking = booking_service.get_booking_by_reference(db, reference)
    if booking is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return booking


@router.get("/{reference}/tickets/{code}")
def download_ticket(
    reference: str, code: str, db: Session = Depends(get_db)
) -> FileResponse:
    """Скачать PDF-билета. 404, если билета нет или PDF ещё генерится."""
    path = booking_service.get_ticket_pdf_path(db, reference, code)
    if path is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="Ticket PDF not found or not ready yet"
        )
    return FileResponse(
        path, media_type="application/pdf", filename=f"ticket-{code}.pdf"
    )
