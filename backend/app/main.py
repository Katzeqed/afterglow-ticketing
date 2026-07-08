"""Точка входа FastAPI-приложения.

Здесь только сборка: создаём приложение и подключаем роутеры.
Бизнес-логика живёт в services/, доступ к БД — в models/ и database.py.
"""
from fastapi import FastAPI

from app.config import settings
from app.routes import health

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(health.router)
