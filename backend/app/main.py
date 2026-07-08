"""Точка входа FastAPI-приложения.

Здесь только сборка: создаём приложение, подключаем middleware и роутеры.
Бизнес-логика живёт в services/, доступ к БД — в models/ и database.py.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import bookings, events, health, holds, tour

app = FastAPI(title=settings.app_name, debug=settings.debug)

# CORS: разрешаем фронтенду (другой origin) обращаться к API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(tour.router)
app.include_router(events.router)
app.include_router(holds.router)
app.include_router(bookings.router)
