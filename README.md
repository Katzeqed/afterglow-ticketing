# Afterglow — MARLOWE Tour Ticketing

Concurrency-safe event ticketing for a single fictional artist tour (**MARLOWE — *Afterglow***). A full-stack portfolio project centered on the hard part of ticketing: **seat holds, protection against double-booking, and background jobs** — with a warm editorial React front end on top.

> Fictional artist, venues and event. Built for portfolio / educational purposes.

![FastAPI](https://img.shields.io/badge/FastAPI-0.1x-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![Celery](https://img.shields.io/badge/Celery-RabbitMQ-37814A)
![React](https://img.shields.io/badge/React-19-149ECA)

## What it demonstrates

- **Row-level locking** (`SELECT … FOR UPDATE`) to prevent two buyers getting the same seat — with a concurrency test proving exactly one winner under 20 parallel requests.
- **Temporary holds** with a TTL and a Celery **beat** sweeper that releases expired seats (`SKIP LOCKED` so it never blocks an in-flight payment).
- **Idempotent** booking (safe against double-submit / retries).
- **Background jobs** (Celery + RabbitMQ): PDF ticket generation with QR, confirmation email.
- Mock payment with the same contract as a real provider (Luhn/expiry checks; full card number never stored).
- Layered architecture (routes → services → models), Alembic migrations, pytest.

## Tech Stack

**Backend:** FastAPI · PostgreSQL · SQLAlchemy 2.0 · Alembic · Celery + RabbitMQ · Redis · reportlab
**Frontend:** React 19 · Vite · TypeScript · Tailwind v4 · TanStack Query · Zustand · Framer Motion (SVG seat map with zoom/pan)
**Infra:** Docker Compose · pytest

## Run

**Backend + infrastructure** (Postgres, RabbitMQ, Redis, API, worker, beat):

```bash
docker compose up --build
docker compose exec backend alembic upgrade head   # create tables
docker compose exec backend python -m app.data.seed  # MARLOWE tour data
```

- API: http://localhost:8000 · docs: http://localhost:8000/docs
- RabbitMQ panel: http://localhost:15672 (guest/guest)

**Frontend** (Vite dev server, proxies `/api` to the backend):

```bash
cd frontend
npm install
npm run dev            # http://localhost:5173
```

**Tests:**

```bash
docker compose exec backend pip install -r requirements-dev.txt
docker compose exec backend pytest
```

## User flow

Landing (tour dates) → **seat map** (zoom/pan, pick seats) → *Continue* creates a
10-minute hold → **checkout** (countdown + mock card) → **confirmation** with tickets
and downloadable PDFs.

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/tour` | Artist + all tour dates |
| GET | `/api/events/{id}` | Event detail + per-zone availability |
| GET | `/api/events/{id}/seats` | Seat map (zones with nested seats) |
| POST | `/api/holds` | Hold seats (row-locked, all-or-nothing) |
| GET | `/api/holds/{id}` | Hold status + time left |
| DELETE | `/api/holds/{id}` | Release a hold |
| POST | `/api/bookings` | Book a hold (mock payment, idempotent) |
| GET | `/api/bookings/{reference}` | Guest booking lookup |
| GET | `/api/bookings/{reference}/tickets/{code}` | Download PDF ticket |

## Project structure

```
├── backend/
│   ├── app/
│   │   ├── main.py · config.py · database.py · celery_app.py · limiter…
│   │   ├── models/     # Tour → Event → Zone → Seat, Hold, Booking, Ticket
│   │   ├── schemas/    # Pydantic
│   │   ├── routes/     # tour, events, holds, bookings, health
│   │   ├── services/   # catalog, hold, booking, payment, availability, pdf
│   │   ├── tasks/      # Celery: expire_holds, ticket PDF, email
│   │   └── data/seed.py
│   ├── alembic/  · tests/  · Dockerfile
├── frontend/           # React + Vite SPA (pages, components, api, store)
├── design-system/      # design tokens & rules
└── docker-compose.yml  # db · rabbitmq · redis · backend · worker · beat
```

## Notes

- Prices are stored in cents (integers) to avoid floating-point errors.
- The schema is owned by Alembic migrations, not `create_all`.
- Design direction and tokens: see [`design-system/MASTER.md`](design-system/MASTER.md).
