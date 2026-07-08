"""Рендер PDF-билета с QR-кодом (reportlab + qrcode).

Файлы пишутся в generated/ (вне /static) — доступ только через API-роут.
"""
import io
import os
from datetime import datetime

import qrcode
from reportlab.lib.pagesizes import A6
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

OUTPUT_DIR = "generated/tickets"


def render_ticket_pdf(
    *,
    code: str,
    artist: str,
    title: str,
    city: str,
    venue: str,
    starts_at: datetime,
    zone_name: str,
    row: str,
    number: int,
    price_cents: int,
    reference: str,
) -> str:
    """Рисует билет A6 и возвращает путь к файлу."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"{code}.pdf")

    width, height = A6
    c = canvas.Canvas(path, pagesize=A6)
    left = 12 * mm
    y = height - 16 * mm

    c.setFillColorRGB(0.13, 0.12, 0.10)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(left, y, artist)
    y -= 8 * mm
    c.setFont("Helvetica-Oblique", 13)
    c.drawString(left, y, title)

    y -= 6 * mm
    c.setLineWidth(0.6)
    c.line(left, y, width - left, y)

    def field(label: str, value: str, y_pos: float) -> float:
        c.setFont("Helvetica-Bold", 8)
        c.setFillColorRGB(0.5, 0.45, 0.4)
        c.drawString(left, y_pos, label)
        c.setFont("Helvetica", 11)
        c.setFillColorRGB(0.13, 0.12, 0.10)
        c.drawString(left, y_pos - 5 * mm, value)
        return y_pos - 12 * mm

    y -= 8 * mm
    y = field("EVENT", f"{city} - {venue}", y)
    y = field("DATE", starts_at.strftime("%d %b %Y  %H:%M"), y)
    y = field("SEAT", f"{zone_name} - Row {row}, Seat {number}", y)
    y = field("PRICE", f"EUR {price_cents / 100:.2f}", y)
    y = field("BOOKING", reference, y)

    # QR-код с кодом билета.
    qr_img = qrcode.make(code)
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    buf.seek(0)
    qr_size = 30 * mm
    c.drawImage(ImageReader(buf), width - left - qr_size, 12 * mm, qr_size, qr_size)
    c.setFont("Helvetica", 7)
    c.setFillColorRGB(0.5, 0.45, 0.4)
    c.drawRightString(width - left, 9 * mm, code)

    c.showPage()
    c.save()
    return path
