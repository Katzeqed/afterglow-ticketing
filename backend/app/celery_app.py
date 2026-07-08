"""Celery-приложение: брокер RabbitMQ, бэкенд результатов Redis.

`beat_schedule` запускает периодическую уборку истёкших холдов.
"""
from celery import Celery

from app.config import settings

celery_app = Celery(
    "afterglow",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.holds",
        "app.tasks.tickets",
        "app.tasks.emails",
    ],
)

celery_app.conf.update(
    timezone="UTC",
    task_track_started=True,
    beat_schedule={
        "expire-holds-every-30s": {
            "task": "app.tasks.holds.expire_holds",
            "schedule": 30.0,
        },
    },
)
