"""Роут лендинга: тур артиста + все даты."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.tour import TourResponse
from app.services import catalog_service

router = APIRouter(prefix="/api", tags=["tour"])


@router.get("/tour", response_model=TourResponse)
def get_tour(db: Session = Depends(get_db)) -> TourResponse:
    tour = catalog_service.get_tour(db)
    if tour is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tour not found")
    return tour
