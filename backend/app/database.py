"""Слой доступа к БД: движок, фабрика сессий, базовый класс моделей.

`get_db` — зависимость FastAPI: выдаёт сессию на время запроса и
гарантированно закрывает её в конце (даже при ошибке).
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# pool_pre_ping проверяет живость соединения перед выдачей из пула —
# спасает от «протухших» коннектов после простоя БД.
engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Базовый класс всех ORM-моделей."""


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
