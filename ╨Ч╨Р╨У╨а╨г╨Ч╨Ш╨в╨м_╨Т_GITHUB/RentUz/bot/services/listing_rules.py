"""Правила анкеты объявления: какие поля нужны для какого типа, проверка ввода."""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

FLOOR_PROPERTY_TYPES = frozenset({"apartment", "office", "warehouse"})
ROOMS_PROPERTY_TYPES = frozenset({"apartment", "house"})
MAX_PHOTOS = 10
MAX_DESCRIPTION = 800


def property_requires_floor(property_type: str | None) -> bool:
    return property_type in FLOOR_PROPERTY_TYPES


def property_requires_rooms(property_type: str | None) -> bool:
    return property_type in ROOMS_PROPERTY_TYPES


def normalize_phone(value: str) -> str | None:
    """Нормализует телефон; отклоняет буквы и посторонние символы."""
    raw = (value or "").strip()
    if not raw or not re.fullmatch(r"\+?[0-9\s().-]+", raw):
        return None
    digits = re.sub(r"\D", "", raw)
    if not 7 <= len(digits) <= 15:
        return None
    return "+" + digits


def parse_number(value: str) -> Decimal | None:
    raw = (value or "").strip().replace(" ", "").replace(" ", "").replace(",", ".")
    try:
        number = Decimal(raw)
    except InvalidOperation:
        return None
    return number if number.is_finite() else None


def parse_price(value: str) -> tuple[Decimal, str] | None:
    """'5 000 000' → (5000000, 'UZS'); '70000$' / '$70 000' / '70000 usd' → (70000, 'USD')."""
    raw = (value or "").strip().lower()
    currency = "UZS"
    if "$" in raw or "usd" in raw or "долл" in raw or "dollar" in raw:
        currency = "USD"
    cleaned = re.sub(r"(\$|usd|долл\w*|dollar\w*|сум|so[‘'`]?m|uzs)", "", raw)
    number = parse_number(cleaned)
    if number is None or number <= 0:
        return None
    return number, currency
