"""Генерация PDF-билета в фоне."""
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Booking, Event, Ticket
from app.services.pdf import render_ticket_pdf


@celery_app.task(name="app.tasks.tickets.generate_ticket_pdf")
def generate_ticket_pdf(ticket_id: int) -> str | None:
    db = SessionLocal()
    try:
        ticket = db.get(Ticket, ticket_id)
        if ticket is None:
            return None

        seat = ticket.seat
        zone = seat.zone
        event = db.get(Event, seat.event_id)
        tour = event.tour
        booking = db.get(Booking, ticket.booking_id)

        path = render_ticket_pdf(
            code=ticket.code,
            artist=tour.artist,
            title=tour.title,
            city=event.city,
            venue=event.venue,
            starts_at=event.starts_at,
            zone_name=zone.name,
            row=seat.row,
            number=seat.number,
            price_cents=zone.price_cents,
            reference=booking.reference,
        )
        ticket.pdf_path = path
        db.commit()
        return path
    finally:
        db.close()
