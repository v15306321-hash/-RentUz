from __future__ import annotations

import json
from pathlib import Path

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from localization import LANGUAGES, tr


_LOCATION_PATH = Path(__file__).resolve().parent / "data" / "locations.json"
with _LOCATION_PATH.open("r", encoding="utf-8") as _file:
    LOCATIONS = json.load(_file)


def label_for(entry: dict, language: str) -> str:
    if isinstance(entry, dict):
        return entry.get(language) or entry.get("ru") or ""
    return str(entry)


def city_options(language: str) -> list[tuple[str, str]]:
    return [(key, label_for(value["name"], language)) for key, value in LOCATIONS.items()]


def city_entry(city_key: str) -> dict | None:
    return LOCATIONS.get(city_key)


def district_entries(city_key: str) -> list[dict]:
    entry = city_entry(city_key) or {}
    return entry.get("districts", [])


def nav_rows(rows: list[list[str]], language: str, *, back: bool = True, home: bool = True) -> ReplyKeyboardMarkup:
    result = [[KeyboardButton(text=text) for text in row] for row in rows]
    nav = []
    if home:
        nav.append(KeyboardButton(text=tr(language, "home")))
    if back:
        nav.append(KeyboardButton(text=tr(language, "back")))
    if nav:
        result.append(nav)
    return ReplyKeyboardMarkup(keyboard=result, resize_keyboard=True, is_persistent=True)


def language_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=value) for value in LANGUAGES.values()]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def main_menu_keyboard(language: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            # A dedicated full-width row gives the long first action the same
            # visual treatment on Telegram clients as the other menu buttons.
            [KeyboardButton(text=tr(language, "menu_list"))],
            [KeyboardButton(text=tr(language, "menu_search"))],
            [KeyboardButton(text=tr(language, "menu_my")), KeyboardButton(text=tr(language, "menu_referral"))],
            [KeyboardButton(text=tr(language, "menu_ad")), KeyboardButton(text=tr(language, "menu_fee"))],
            [KeyboardButton(text=tr(language, "menu_support")), KeyboardButton(text=tr(language, "menu_language"))],
        ],
        resize_keyboard=True,
        is_persistent=False,
    )


def draft_choice_keyboard(language: str) -> ReplyKeyboardMarkup:
    return nav_rows(
        [[tr(language, "continue")], [tr(language, "restart")]],
        language,
        back=False,
    )


def city_keyboard(language: str, *, back: bool = True) -> ReplyKeyboardMarkup:
    options = [label for _, label in city_options(language)]
    rows = [options[i:i + 2] for i in range(0, len(options), 2)]
    return nav_rows(rows, language, back=back)


def district_keyboard(city_key: str, language: str) -> ReplyKeyboardMarkup:
    options = [label_for(item["name"], language) for item in district_entries(city_key)]
    options.append(tr(language, "other_district"))
    rows = [options[i:i + 2] for i in range(0, len(options), 2)]
    return nav_rows(rows, language)


def district_entry(city_key: str, district_ru: str | None) -> dict | None:
    return next(
        (item for item in district_entries(city_key) if label_for(item["name"], "ru") == district_ru),
        None,
    )


def microdistrict_keyboard(city_key: str, district_ru: str, language: str) -> ReplyKeyboardMarkup:
    district = district_entry(city_key, district_ru)
    options = [label_for(item, language) for item in (district or {}).get("microdistricts", [])]
    options.append(tr(language, "other_microdistrict"))
    rows = [options[i:i + 2] for i in range(0, len(options), 2)]
    return nav_rows(rows, language)


def property_keyboard(language: str) -> ReplyKeyboardMarkup:
    options = [
        tr(language, "property_apartment"), tr(language, "property_house"),
        tr(language, "property_office"), tr(language, "property_shop"),
        tr(language, "property_warehouse"),
    ]
    return nav_rows([[options[0], options[1]], [options[2], options[3]], [options[4]]], language)


def deal_keyboard(language: str) -> ReplyKeyboardMarkup:
    return nav_rows([[tr(language, "deal_rent"), tr(language, "deal_sale")]], language)


def phone_keyboard(language: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=tr(language, "share_phone"), request_contact=True)],
            [KeyboardButton(text=tr(language, "manual_phone"))],
            [KeyboardButton(text=tr(language, "home")), KeyboardButton(text=tr(language, "back"))],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def photos_keyboard(language: str) -> ReplyKeyboardMarkup:
    return nav_rows([[tr(language, "photos_done")]], language)


PAYMENT_LABELS = ["Click", "Humo", "Uzum Bank", "Crypto Pay"]


def payment_keyboard(language: str) -> ReplyKeyboardMarkup:
    labels = PAYMENT_LABELS
    return nav_rows([[labels[0], labels[1]], [labels[2], labels[3]]], language)


def rooms_keyboard(language: str) -> ReplyKeyboardMarkup:
    return nav_rows([["1", "2", "3"], ["4", tr(language, "rooms_5plus")]], language)


def skip_keyboard(language: str) -> ReplyKeyboardMarkup:
    return nav_rows([[tr(language, "skip")]], language)


def floor_keyboard(page: int, language: str) -> InlineKeyboardMarkup:
    page = max(0, min(5, page))
    start = page * 10 + 1
    end = start + 9
    rows = []
    values = list(range(start, end + 1))
    for index in range(0, len(values), 5):
        rows.append([
            InlineKeyboardButton(text=str(value), callback_data=f"floor:{value}")
            for value in values[index:index + 5]
        ])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"floorpage:{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"{page + 1}/6", callback_data="floor:noop"))
    if page < 5:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"floorpage:{page + 1}"))
    rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=rows)


AD_TARIFFS = {  # дней: цена в сумах
    1: 25000,
    3: 63000,
    7: 119000,
    30: 390000,
    90: 900000,
}

_DAY_WORDS = {
    "ru": {1: "1 день", 3: "3 дня", 7: "7 дней", 30: "30 дней", 90: "90 дней"},
    "uz": {1: "1 kun", 3: "3 kun", 7: "7 kun", 30: "30 kun", 90: "90 kun"},
}


def money(value) -> str:
    return f"{int(value):,}".replace(",", " ")


def ad_tariff_label(days: int, language: str) -> str:
    words = _DAY_WORDS.get(language, _DAY_WORDS["ru"])
    return tr(language, "ad_tariff_label", days=words[days], price=money(AD_TARIFFS[days]))


def ad_tariff_from_text(text: str) -> int | None:
    """Находит тариф по тексту кнопки на любом языке."""
    for days in AD_TARIFFS:
        for language in LANGUAGES:
            if text == ad_tariff_label(days, language):
                return days
    return None


def ad_tariff_keyboard(language: str) -> ReplyKeyboardMarkup:
    return nav_rows([[ad_tariff_label(days, language)] for days in AD_TARIFFS], language)
