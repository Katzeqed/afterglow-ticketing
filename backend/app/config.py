"""Настройки приложения.

Значения берутся из переменных окружения (или .env). Имена полей
соответствуют переменным без учёта регистра: DATABASE_URL -> database_url.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Afterglow API"
    debug: bool = True

    # Основная БД. Замена на другой Postgres/облако = смена одной строки.
    database_url: str = (
        "postgresql+psycopg://afterglow:afterglow@localhost:5432/afterglow"
    )

    # RabbitMQ — брокер фоновых задач (Celery). Redis — результаты/кэш.
    # Реально подключаются на фазе 6, но заводим настройки заранее.
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672//"
    redis_url: str = "redis://localhost:6379/0"


settings = Settings()
