# Afterglow — MARLOWE Tour Ticketing

Concurrency-safe event ticketing for a single fictional artist tour (**MARLOWE — Afterglow**). A backend-focused portfolio project: seat selection with hold/reservation logic, protection against double-booking, and background jobs.

> Fictional artist and event. Built for portfolio/educational purposes.

## Tech Stack

**Backend:** FastAPI · PostgreSQL · SQLAlchemy 2.0 · Alembic · Celery + RabbitMQ · Redis
**Frontend:** React · Vite · Tailwind · Framer Motion (SVG seat map)
**Infra:** Docker Compose · pytest

## Run (Phase 1)

```bash
docker compose up --build
```

- API: http://localhost:8000 · docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health
- RabbitMQ panel: http://localhost:15672 (guest/guest)

## Status

Phase 1 — project scaffold, Docker Compose (Postgres, RabbitMQ, Redis), health check. ✅
