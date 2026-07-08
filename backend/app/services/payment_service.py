"""Мок-платёж: тот же контракт, что у настоящего провайдера, но без списаний.

Чтобы «подключить Stripe», меняется только этот файл — роуты и логика брони
остаются прежними.
"""
from datetime import datetime, timezone

# Тестовая карта, которую «банк» всегда отклоняет (для демонстрации пути ошибки).
DECLINE_CARD = "4000000000000002"


class PaymentError(Exception):
    pass


class PaymentDeclined(PaymentError):
    def __init__(self, reason: str):
        self.reason = reason


def _luhn_ok(number: str) -> bool:
    """Проверка контрольной суммы номера карты (алгоритм Луна)."""
    digits = [int(d) for d in number]
    parity = len(digits) % 2
    total = 0
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def _brand(number: str) -> str:
    if number.startswith("4"):
        return "Visa"
    if number.startswith("5"):
        return "Mastercard"
    if number[:2] in {"34", "37"}:
        return "Amex"
    return "Card"


def charge(total_cents: int, number: str, expiry: str, cvv: str, holder: str) -> tuple[str, str]:
    """«Проводит» оплату. Возвращает (бренд, last4) или бросает PaymentDeclined.

    Полный номер карты нигде не сохраняется.
    """
    if not _luhn_ok(number):
        raise PaymentDeclined("invalid_card_number")

    month_str, year_str = expiry.split("/")
    month, year = int(month_str), 2000 + int(year_str)
    now = datetime.now(timezone.utc)
    if not (1 <= month <= 12) or (year, month) < (now.year, now.month):
        raise PaymentDeclined("card_expired")

    if number == DECLINE_CARD:
        raise PaymentDeclined("card_declined")

    return _brand(number), number[-4:]
