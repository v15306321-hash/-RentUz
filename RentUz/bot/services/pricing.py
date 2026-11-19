"""Комиссии за размещение объявлений и реферальные скидки.

Правила:
* Аренда  — 1% от цены аренды; цена аренды не меньше 1 000 000 сум.
* Продажа — 0,1% от цены объекта; цена объекта не меньше 5 000 $.
* Посуточно — 10% от цены одних суток; цена не меньше 100 000 сум за сутки.
* Реферальная скидка — 10% за каждого приглашённого друга, который
  опубликовал объявление; максимум 30% на одно объявление.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

RENT_COMMISSION = Decimal("0.01")
DAILY_COMMISSION = Decimal("0.10")   # посуточно: 10% от цены одних суток
MIN_DAILY_PRICE_UZS = 100_000
SALE_COMMISSION = Decimal("0.001")
MIN_RENT_PRICE_UZS = 1_000_000
MIN_SALE_PRICE_USD = 5_000
DISCOUNT_PER_FRIEND = 10
MAX_DISCOUNT_FRIENDS = 3

# Совместимость со старым кодом.
COMMISSION_RATE = RENT_COMMISSION


def commission_rate(purpose: str | None) -> Decimal:
    if purpose == "sale":
        return SALE_COMMISSION
    if purpose == "daily":
        return DAILY_COMMISSION
    return RENT_COMMISSION


def price_error(purpose: str | None, price_uzs: int | Decimal, exchange_rate: int | float | Decimal | None) -> str | None:
    """Ключ текста ошибки, если цена ниже минимальной, иначе None."""
    price = Decimal(str(price_uzs))
    if price <= 0:
        return "invalid_number"
    if purpose == "sale":
        rate = Decimal(str(exchange_rate or 0))
        if rate <= 0:
            return "rate_error"
        if price / rate < MIN_SALE_PRICE_USD:
            return "min_sale_price"
    elif purpose == "daily":
        if price < MIN_DAILY_PRICE_UZS:
            return "min_daily_price"
    elif price < MIN_RENT_PRICE_UZS:
        return "min_rent_price"
    return None


def calculate_listing_cost(price_uzs, exchange_rate, purpose: str | None = "rent") -> tuple[int, Decimal]:
    """(комиссия в сумах, цена объекта в $)."""
    price = Decimal(str(price_uzs))
    rate = Decimal(str(exchange_rate))
    if price <= 0:
        raise ValueError("Property price must be positive")
    if rate <= 0:
        raise ValueError("Exchange rate must be positive")
    fee = (price * commission_rate(purpose)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    price_usd = (price / rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(fee), price_usd


def discount_percent(friends: int) -> int:
    return DISCOUNT_PER_FRIEND * max(0, min(MAX_DISCOUNT_FRIENDS, friends))


def apply_discount(fee_uzs: int, percent: int) -> int:
    fee = Decimal(int(fee_uzs))
    result = fee * (Decimal(100 - percent) / Decimal(100))
    return int(result.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def service_fee_usdt(service_fee_uzs, exchange_rate) -> Decimal:
    fee = Decimal(str(service_fee_uzs))
    rate = Decimal(str(exchange_rate))
    if fee < 0 or rate <= 0:
        raise ValueError("Invalid service fee or exchange rate")
    return (fee / rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


TASHKENT = ZoneInfo("Asia/Tashkent")


def promo_end() -> date | None:
    """Последний день акции «первое объявление бесплатно» или None, если акция выключена."""
    from config import PROMO_FREE_FIRST_UNTIL
    try:
        return date.fromisoformat(PROMO_FREE_FIRST_UNTIL)
    except ValueError:
        return None


def promo_active(now: datetime | None = None) -> bool:
    end = promo_end()
    today = (now or datetime.now(TASHKENT)).astimezone(TASHKENT).date()
    return end is not None and today <= end


def promo_end_label(language: str) -> str:
    end = promo_end()
    if not end:
        return ""
    months = {
        "ru": ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"],
        "uz": ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"],
    }
    names = months.get(language, months["ru"])
    return f"{end.day} {names[end.month - 1]}" if language != "uz" else f"{end.day}-{names[end.month - 1]}"
