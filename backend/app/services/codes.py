"""Генерация человекочитаемых кодов: номер брони и код билета.

Алфавит без неоднозначных символов (нет 0/O, 1/I). `secrets` —
криптостойкий источник случайности.
"""
import secrets

_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _block(n: int) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(n))


def booking_reference() -> str:
    """Напр. AG-7K2F-9QX4 — по нему гость находит бронь."""
    return f"AG-{_block(4)}-{_block(4)}"


def ticket_code() -> str:
    """Напр. TK-7K2F9QX4H3 — полезная нагрузка QR билета."""
    return f"TK-{_block(10)}"
