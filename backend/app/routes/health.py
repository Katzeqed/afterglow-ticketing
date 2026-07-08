"""Health-check: подтверждает, что приложение живо и видит БД."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    # Пингуем БД простым запросом — если соединения нет, вернётся 500.
    db.execute(text("SELECT 1"))
    return {"status": "ok", "service": "afterglow-api", "database": "up"}
