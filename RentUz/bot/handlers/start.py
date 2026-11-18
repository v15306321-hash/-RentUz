"""Главное меню, анкета объявления, поиск, поддержка, язык и реферальная программа.

Порядок обработчиков важен: сначала команды и кнопки меню (работают из любого
шага), затем обработчики конкретных шагов анкеты."""
from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from urllib.parse import quote, urlencode

from config import BOT_USERNAME, OWNER_CHAT_ID, SITE_URL
from database.db import (
    abandon_draft_order,
    add_photo_to_order,
    create_draft_order,
    finalize_draft_order,
    get_draft_order,
    get_order,
    get_order_photos,
    get_user,
    referral_stats,
    register_referral,
    update_draft_progress,
    update_order,
    update_user,
    upsert_user,
    DRAFT_STATUSES,
)
from keyboards import (
    city_entry,
    city_keyboard,
    city_options,
    deal_keyboard,
    district_entries,
    district_entry,
    district_keyboard,
    floor_keyboard,
    label_for,
    language_keyboard,
    main_menu_keyboard,
    microdistrict_keyboard,
    money,
    nav_rows,
    phone_keyboard,
    photos_keyboard,
    property_keyboard,
    rooms_keyboard,
    skip_keyboard,
    AD_TARIFFS,
    ad_tariff_label,
    ad_tariff_keyboard,
)
from localization import LANGUAGES, all_variants, normalize_language, tr
from services.exchange_rate import get_usd_uzs_rate
from services.listing_rules import (
    MAX_DESCRIPTION,
    MAX_PHOTOS,
    normalize_phone,
    parse_number,
    parse_price,
    property_requires_floor,
    property_requires_rooms,
)
from services.pricing import MIN_SALE_PRICE_USD, calculate_listing_cost, discount_percent, price_error
from .states import AdvertisingForm, ListingForm, MenuForm, Onboarding, PaymentForm, PhotoForm, SearchForm, SupportForm

router = Router()
log = logging.getLogger(__name__)

PROPERTY_CHOICES = {
    "apartment": "property_apartment",
    "house": "property_house",
    "office": "property_office",
    "shop": "property_shop",
    "warehouse": "property_warehouse",
}

STEP_STATES = {
    "city": ListingForm.city,
    "district": ListingForm.district,
    "custom_district": ListingForm.custom_district,
    "microdistrict": ListingForm.microdistrict,
    "custom_microdistrict": ListingForm.custom_microdistrict,
    "property_type": ListingForm.property_type,
    "deal": ListingForm.deal,
    "area": ListingForm.area,
    "rooms": ListingForm.rooms,
    "floor": ListingForm.floor,
    "price": ListingForm.price,
    "description": ListingForm.description,
    "phone": ListingForm.phone,
}
STEP_ORDER = list(STEP_STATES)
CUSTOM_STEPS = {"custom_district", "custom_microdistrict"}


# ------------------------------------------------------------------ helpers

def _has_microdistricts(data: dict) -> bool:
    if data.get("district_custom"):
        return False
    entry = district_entry(data.get("city_key"), data.get("district"))
    return bool((entry or {}).get("microdistricts"))


def _step_needed(step: str, data: dict) -> bool:
    if step == "custom_district":
        return bool(data.get("district_custom"))
    if step == "microdistrict":
        return _has_microdistricts(data)
    if step == "custom_microdistrict":
        return bool(data.get("micro_custom"))
    if step == "rooms":
        return property_requires_rooms(data.get("property_type"))
    if step == "floor":
        return property_requires_floor(data.get("property_type"))
    return True


def _next_step(current: str, data: dict) -> str:
    for step in STEP_ORDER[STEP_ORDER.index(current) + 1:]:
        if step not in CUSTOM_STEPS and _step_needed(step, data):
            return step
    return "phone"


def _prev_step(current: str, data: dict) -> str | None:
    for step in reversed(STEP_ORDER[:STEP_ORDER.index(current)]):
        if _step_needed(step, data):
            return step
    return None


async def _language(message_or_cb, state: FSMContext) -> str:
    data = await state.get_data()
    if data.get("language") in LANGUAGES:
        return data["language"]
    user = await get_user(message_or_cb.from_user.id)
    return normalize_language((user or {}).get("language"))


def _matches(text: str | None, key: str) -> bool:
    return bool(text) and text in all_variants(key)


def _referral_link(user_id: int) -> str:
    return f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"


async def _show_main(message: Message, state: FSMContext, language: str) -> None:
    await state.set_state(None)
    await state.set_data({"language": language})
    await message.answer(tr(language, "main_title"), reply_markup=main_menu_keyboard(language))


async def _persist_draft_step(state: FSMContext, step: str) -> None:
    data = await state.get_data()
    order_id = data.get("order_id")
    if order_id:
        await update_draft_progress(int(order_id), step, data)


async def _set_listing_step(message: Message, state: FSMContext, step: str) -> None:
    data = await state.get_data()
    language = data.get("language", "ru")
    await state.set_state(STEP_STATES[step])
    await _persist_draft_step(state, step)

    if step == "city":
        await message.answer(tr(language, "city_prompt"), reply_markup=city_keyboard(language, back=False))
    elif step == "district":
        city_name = label_for((city_entry(data.get("city_key")) or {}).get("name", {}), language)
        await message.answer(tr(language, "district_prompt", city=city_name),
                             reply_markup=district_keyboard(data.get("city_key"), language))
    elif step == "custom_district":
        await message.answer(tr(language, "custom_district_prompt"), reply_markup=nav_rows([], language))
    elif step == "microdistrict":
        await message.answer(tr(language, "microdistrict_prompt"),
                             reply_markup=microdistrict_keyboard(data.get("city_key"), data.get("district", ""), language))
    elif step == "custom_microdistrict":
        await message.answer(tr(language, "custom_microdistrict_prompt"), reply_markup=nav_rows([], language))
    elif step == "property_type":
        await message.answer(tr(language, "property_prompt"), reply_markup=property_keyboard(language))
    elif step == "deal":
        await message.answer(tr(language, "deal_prompt"), reply_markup=deal_keyboard(language))
    elif step == "area":
        await message.answer(tr(language, "area_prompt"), reply_markup=nav_rows([], language))
    elif step == "rooms":
        await message.answer(tr(language, "rooms_prompt"), reply_markup=rooms_keyboard(language))
    elif step == "floor":
        await message.answer(tr(language, "floor_prompt"), reply_markup=nav_rows([], language))
        await message.answer(tr(language, "floor_page", start=1, end=10), reply_markup=floor_keyboard(0, language))
    elif step == "price":
        key = "price_prompt_sale" if data.get("purpose") == "sale" else "price_prompt_rent"
        await message.answer(tr(language, key), reply_markup=nav_rows([], language))
    elif step == "description":
        await message.answer(tr(language, "description_prompt"), reply_markup=skip_keyboard(language))
    elif step == "phone":
        await message.answer(tr(language, "phone_prompt"), reply_markup=phone_keyboard(language))


async def _go_next(message: Message, state: FSMContext, current: str) -> None:
    await _set_listing_step(message, state, _next_step(current, await state.get_data()))


async def _start_new_listing(message: Message, state: FSMContext, language: str, user_id: int) -> None:
    order = await create_draft_order(user_id, language)
    await state.set_data({"language": language, "order_id": order["id"]})
    await _set_listing_step(message, state, "city")


async def _begin_listing(message: Message, state: FSMContext, language: str, user_id: int) -> None:
    existing = await get_draft_order(user_id)
    if existing:
        await state.set_data({"language": language, "pending_order_id": existing["id"]})
        await state.set_state(MenuForm.draft_choice)
        await message.answer(tr(language, "draft_found"), reply_markup=nav_rows(
            [[tr(language, "continue")], [tr(language, "restart")]], language, back=False
        ))
        return
    await _start_new_listing(message, state, language, user_id)


async def _resume_order(message: Message, state: FSMContext, language: str, user_id: int) -> None:
    order = await get_draft_order(user_id)
    if not order:
        await _start_new_listing(message, state, language, user_id)
        return
    data = dict(order.get("draft_data") or {})
    data.update({"order_id": order["id"], "language": language})
    await state.set_data(data)

    if order["status"] == "awaiting_photos":
        await state.set_state(PhotoForm.waiting_photos)
        await message.answer(tr(language, "photos_prompt"), reply_markup=photos_keyboard(language))
        return
    if order["status"] in {"awaiting_payment", "awaiting_receipt", "awaiting_crypto_payment"}:
        from handlers.payment import show_listing_payment
        await show_listing_payment(message, state, order["id"], language)
        return

    step = order.get("draft_step") or "city"
    await _set_listing_step(message, state, step if step in STEP_STATES else "city")


def _place_labels(order: dict, language: str) -> tuple[str, str, str | None]:
    """Город/район/микрорайон хранятся по-русски (для сайта); показываем на языке пользователя."""
    city = city_entry(order.get("city_key"))
    city_label = label_for(city["name"], language) if city else (order.get("city") or "—")
    district = district_entry(order.get("city_key"), order.get("district"))
    district_label = label_for(district["name"], language) if district else (order.get("district") or "—")
    micro = order.get("microdistrict")
    if micro and district:
        found = next((m for m in district.get("microdistricts", []) if label_for(m, "ru") == micro), None)
        micro = label_for(found, language) if found else micro
    return city_label, district_label, micro


def listing_summary_lines(order: dict, language: str) -> list[str]:
    """Описание объявления для пользователя и администратора."""
    city_label, district_label, micro = _place_labels(order, language)
    lines = [
        f"{tr(language, 'lbl_city')}: {city_label}",
        f"{tr(language, 'lbl_district')}: {district_label}",
    ]
    if micro:
        lines.append(f"{tr(language, 'lbl_microdistrict')}: {micro}")
    lines.append(f"{tr(language, 'lbl_property')}: {tr(language, PROPERTY_CHOICES.get(order.get('property_type'), 'property_apartment'))}")
    lines.append(f"{tr(language, 'lbl_deal')}: {tr(language, 'deal_sale' if order.get('purpose') == 'sale' else 'deal_rent')}")
    if order.get("area") is not None:
        lines.append(f"{tr(language, 'lbl_area')}: {Decimal(str(order['area'])).normalize():f} m²")
    if order.get("rooms"):
        lines.append(f"{tr(language, 'lbl_rooms')}: {order['rooms']}")
    if order.get("property_floor") is not None:
        lines.append(f"{tr(language, 'floor_label')}: {order['property_floor']}")
    if order.get("price_uzs"):
        is_sale = order.get("purpose") == "sale"
        label = tr(language, "sale_price" if is_sale else "rent_price")
        suffix = "" if is_sale else f" {tr(language, 'per_month')}"
        usd = f" (≈ ${order['price_usd']:,.0f})".replace(",", " ") if order.get("price_usd") else ""
        lines.append(f"{label}: {money(order['price_uzs'])} {tr(language, 'currency')}{suffix}{usd}")
    if order.get("description"):
        lines.append(f"{tr(language, 'lbl_description')}: {order['description']}")
    if order.get("phone"):
        lines.append(f"{tr(language, 'lbl_phone')}: {order['phone']}")
    return lines


async def _finish_listing(message: Message, state: FSMContext, phone: str) -> None:
    data = await state.get_data()
    language = data.get("language", "ru")
    order_id = data.get("order_id")
    await state.update_data(phone=phone)
    await update_user(message.from_user.id, phone=phone)
    await _persist_draft_step(state, "phone")

    try:
        rate = Decimal(str(await get_usd_uzs_rate()))
    except Exception:
        await message.answer(tr(language, "rate_error"), reply_markup=phone_keyboard(language))
        return

    purpose = data.get("purpose")
    price = int(data["price_uzs"])
    base_fee, price_usd = calculate_listing_cost(price, rate, purpose)
    city = city_entry(data.get("city_key")) or {}
    fields = {
        "language": language,
        "city": label_for(city.get("name", {}), "ru") or data.get("city"),
        "city_key": data.get("city_key"),
        "district": data.get("district"),
        "microdistrict": data.get("microdistrict"),
        "property_type": data.get("property_type"),
        "purpose": purpose,
        "area": float(data["area"]),
        "rooms": data.get("rooms") if property_requires_rooms(data.get("property_type")) else None,
        "property_floor": data.get("property_floor") if property_requires_floor(data.get("property_type")) else None,
        "description": data.get("description"),
        "price_uzs": price,
        "price_usd": float(price_usd),
        "exchange_rate": float(rate),
        "commission_rate": float(Decimal("0.001") if purpose == "sale" else Decimal("0.01")),
        "base_fee": base_fee,
        "service_fee": base_fee,
        "discount_percent": 0,
        "phone": phone,
        "contact_name": message.from_user.full_name,
        "contact_username": message.from_user.username,
    }
    order = await finalize_draft_order(int(order_id), fields)
    if not order:
        await message.answer(tr(language, "not_found"), reply_markup=main_menu_keyboard(language))
        await _show_main(message, state, language)
        return

    summary = [tr(language, "listing_saved"), tr(language, "order_no", number=order["order_number"]), ""]
    summary += listing_summary_lines(order, language)
    summary += [
        f"{tr(language, 'exchange_rate')}: 1 USD = {Decimal(str(rate)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,.2f} UZS".replace(",", " "),
        f"{tr(language, 'service_fee')}: {money(base_fee)} {tr(language, 'currency')}",
        "",
        tr(language, "period_warning"),
    ]
    await state.set_state(PhotoForm.waiting_photos)
    await message.answer("\n".join(summary))
    await message.answer(tr(language, "photos_prompt"), reply_markup=photos_keyboard(language))


# ------------------------------------------------------------------ commands

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    created = await upsert_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    payload = (command.args or "").strip()

    # Реферальная ссылка засчитывается только для новых пользователей.
    if payload.startswith("ref_") and created:
        try:
            await register_referral(int(payload[4:]), message.from_user.id)
        except ValueError:
            pass

    user = await get_user(message.from_user.id)
    language = normalize_language((user or {}).get("language"))
    await state.clear()
    if created:
        await state.update_data(change_language=False, start_payload=payload)
        await state.set_state(Onboarding.language)
        await message.answer(tr(language, "language_prompt"), reply_markup=language_keyboard())
        return
    await _after_start(message, state, language, payload)


async def _after_start(message: Message, state: FSMContext, language: str, payload: str) -> None:
    """Глубокие ссылки с сайта: ?start=list и ?start=ad."""
    if payload == "list":
        await _show_main(message, state, language)
        await _begin_listing(message, state, language, message.from_user.id)
    elif payload == "ad":
        await _show_main(message, state, language)
        await _open_ads(message, state, language)
    else:
        await _show_main(message, state, language)


@router.message(Command("myid"))
async def my_id(message: Message):
    await message.answer(f"Your Telegram ID: {message.from_user.id}")


# ------------------------------------------------------------------ navigation (из любого шага)

@router.message(F.text.in_(all_variants("home")))
async def go_home(message: Message, state: FSMContext):
    await _show_main(message, state, await _language(message, state))


@router.message(F.text.in_(all_variants("back")))
async def go_back(message: Message, state: FSMContext):
    current = await state.get_state()
    data = await state.get_data()
    language = await _language(message, state)

    step = current.split(":", 1)[1] if current and current.startswith("ListingForm:") else None
    if step:
        target = _prev_step(step, data)
        if target:
            await _set_listing_step(message, state, target)
            return
        await _show_main(message, state, language)
        return

    if current == PhotoForm.waiting_photos.state:
        await _set_listing_step(message, state, "phone")
    elif current in {PaymentForm.choosing_method.state, PaymentForm.waiting_receipt.state, PaymentForm.waiting_crypto.state}:
        if current == PaymentForm.choosing_method.state:
            await update_order(int(data["order_id"]), status="awaiting_photos")
            await state.set_state(PhotoForm.waiting_photos)
            await message.answer(tr(language, "photos_prompt"), reply_markup=photos_keyboard(language))
        else:
            from handlers.payment import show_listing_payment
            await show_listing_payment(message, state, data["order_id"], language)
    elif current == SearchForm.deal.state:
        await state.set_state(SearchForm.city)
        await message.answer(tr(language, "search_city_prompt"), reply_markup=city_keyboard(language, back=True))
    elif current in {AdvertisingForm.banner.state}:
        await _open_ads(message, state, language)
    elif current in {AdvertisingForm.choosing_payment_method.state}:
        await state.set_state(AdvertisingForm.banner)
        await message.answer(tr(language, "ad_banner_prompt"), reply_markup=nav_rows([], language))
    elif current in {AdvertisingForm.waiting_receipt.state, AdvertisingForm.waiting_crypto.state}:
        from handlers.advertising import show_ad_payment
        await show_ad_payment(message, state, data.get("ad_request_id"), language)
    else:
        await _show_main(message, state, language)


# ------------------------------------------------------------------ main menu

@router.message(F.text.in_(all_variants("menu_list")))
async def menu_list(message: Message, state: FSMContext):
    language = await _language(message, state)
    await update_user(message.from_user.id, intent="listing")
    await _begin_listing(message, state, language, message.from_user.id)


@router.message(F.text.in_(all_variants("menu_search")))
async def menu_search(message: Message, state: FSMContext):
    language = await _language(message, state)
    await update_user(message.from_user.id, intent="search")
    await state.set_data({"language": language})
    await state.set_state(SearchForm.city)
    await message.answer(tr(language, "search_city_prompt"), reply_markup=city_keyboard(language, back=True))


async def _open_ads(message: Message, state: FSMContext, language: str) -> None:
    await state.set_data({"language": language})
    await state.set_state(AdvertisingForm.choosing_tariff)
    await message.answer(tr(language, "ad_tariff_prompt"), reply_markup=ad_tariff_keyboard(language))


@router.message(F.text.in_(all_variants("menu_ad")))
async def menu_ad(message: Message, state: FSMContext):
    await _open_ads(message, state, await _language(message, state))


@router.message(F.text.in_(all_variants("menu_language")))
async def menu_language(message: Message, state: FSMContext):
    """Кнопка подписана на другом языке и сразу переключает на него."""
    current = await _language(message, state)
    language = "uz" if current == "ru" else "ru"
    await update_user(message.from_user.id, language=language)
    await state.set_state(None)
    await state.set_data({"language": language})
    await message.answer(tr(language, "language_saved"), reply_markup=main_menu_keyboard(language))


@router.message(F.text.in_(all_variants("menu_my")))
async def menu_my(message: Message, state: FSMContext):
    language = await _language(message, state)
    await _show_main_silent(state, language)
    from handlers.my_listings import show_my_listings
    await show_my_listings(message, language)


@router.message(F.text.in_(all_variants("menu_fee")))
async def menu_fee(message: Message, state: FSMContext):
    language = await _language(message, state)
    ad_lines = "\n".join(f"   • {ad_tariff_label(days, language)}" for days in AD_TARIFFS)
    await message.answer(tr(language, "fee_info", ad_tariffs=ad_lines), reply_markup=main_menu_keyboard(language))


@router.message(F.text.in_(all_variants("menu_referral")))
async def menu_referral(message: Message, state: FSMContext):
    language = await _language(message, state)
    stats = await referral_stats(message.from_user.id)
    link = _referral_link(message.from_user.id)
    share_url = f"https://t.me/share/url?url={quote(link)}&text={quote(tr(language, 'referral_share_text'))}"
    await message.answer(
        tr(language, "referral_info", link=link, invited=stats["invited"], qualified=stats["qualified"],
           discount=discount_percent(stats["available"])),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text=tr(language, "referral_share_btn"), url=share_url)
        ]]),
        disable_web_page_preview=True,
    )


@router.message(F.text.in_(all_variants("menu_support")))
async def menu_support(message: Message, state: FSMContext):
    language = await _language(message, state)
    await state.set_data({"language": language})
    await state.set_state(SupportForm.message)
    await message.answer(tr(language, "support_intro"), reply_markup=nav_rows([], language, back=False))


# ------------------------------------------------------------------ language

def _language_from_text(text: str | None) -> str | None:
    value = (text or "").lower()
    if "рус" in value or "🇷🇺" in value:
        return "ru"
    if "zbek" in value or "o‘zbek" in value or "🇺🇿" in value:
        return "uz"
    return None


@router.message(Onboarding.language, F.text)
async def choose_language(message: Message, state: FSMContext):
    language = _language_from_text(message.text)
    if not language:
        await message.answer(tr("ru", "language_prompt"), reply_markup=language_keyboard())
        return
    data = await state.get_data()
    await update_user(message.from_user.id, language=language)
    if data.get("change_language"):
        await _show_main(message, state, language)
        await message.answer(tr(language, "language_saved"))
    else:
        await _after_start(message, state, language, data.get("start_payload") or "")


# ------------------------------------------------------------------ draft choice

@router.message(MenuForm.draft_choice, F.text)
async def draft_choice(message: Message, state: FSMContext):
    language = await _language(message, state)
    if _matches(message.text, "continue"):
        await _resume_order(message, state, language, message.from_user.id)
    elif _matches(message.text, "restart"):
        existing = await get_draft_order(message.from_user.id)
        if existing:
            await abandon_draft_order(existing["id"])
        await _start_new_listing(message, state, language, message.from_user.id)
    else:
        await message.answer(tr(language, "draft_found"), reply_markup=nav_rows(
            [[tr(language, "continue")], [tr(language, "restart")]], language, back=False
        ))


# ------------------------------------------------------------------ search

@router.message(SearchForm.city, F.text)
async def search_city_handler(message: Message, state: FSMContext):
    language = await _language(message, state)
    selected = next(((key, label) for key, label in city_options(language) if label == message.text), None)
    if not selected:
        await message.answer(tr(language, "invalid_choice"), reply_markup=city_keyboard(language, back=True))
        return
    await state.update_data(city_key=selected[0], city=selected[1])
    await state.set_state(SearchForm.deal)
    await message.answer(tr(language, "search_deal_prompt"), reply_markup=deal_keyboard(language))


@router.message(SearchForm.deal, F.text)
async def search_deal_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    language = await _language(message, state)
    if _matches(message.text, "deal_rent"):
        purpose = "rent"
    elif _matches(message.text, "deal_sale"):
        purpose = "sale"
    else:
        await message.answer(tr(language, "invalid_choice"), reply_markup=deal_keyboard(language))
        return

    city = label_for((city_entry(data.get("city_key")) or {}).get("name", {}), language) or data.get("city")
    await _show_main_silent(state, language)
    deal = tr(language, "search_deal_sale" if purpose == "sale" else "search_deal_rent")
    await message.answer(
        tr(language, "search_site_info", city=city, deal=deal),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text=tr(language, "site_button"), url=_site_search_url(data.get("city_key"), purpose))
        ]]),
    )
    await message.answer(tr(language, "main_title"), reply_markup=main_menu_keyboard(language))

def _site_search_url(city_key: str | None, purpose: str) -> str:
    city_ru = label_for((city_entry(city_key) or {}).get("name", {}), "ru")
    params = {"city": city_ru} if city_ru else {}
    if purpose == "sale":
        params["deal"] = "sale"
    query = f"?{urlencode(params)}" if params else ""
    return f"{SITE_URL}/{query}#catalog"


async def _show_main_silent(state: FSMContext, language: str) -> None:
    await state.set_state(None)
    await state.set_data({"language": language})


# ------------------------------------------------------------------ support

@router.message(SupportForm.message)
async def support_message(message: Message, state: FSMContext):
    language = await _language(message, state)
    username = f"@{message.from_user.username}" if message.from_user.username else "—"
    header = (
        "🆘 ОБРАЩЕНИЕ В ПОДДЕРЖКУ\n"
        f"Telegram ID: {message.from_user.id}\n"
        f"Имя: {message.from_user.full_name}\n"
        f"Username: {username}"
    )
    try:
        await message.bot.send_message(OWNER_CHAT_ID, header)
        await message.copy_to(OWNER_CHAT_ID)  # пересылаем как есть: текст, фото, файл
    except Exception:
        log.exception("Support message delivery failed")
        await message.answer(tr(language, "support_unavailable"), reply_markup=main_menu_keyboard(language))
        await _show_main_silent(state, language)
        return
    await _show_main_silent(state, language)
    await message.answer(tr(language, "support_sent"), reply_markup=main_menu_keyboard(language))


# ------------------------------------------------------------------ listing form

@router.message(ListingForm.city, F.text)
async def listing_city(message: Message, state: FSMContext):
    language = await _language(message, state)
    selected = next(((key, label) for key, label in city_options(language) if label == message.text), None)
    if not selected:
        await message.answer(tr(language, "invalid_choice"), reply_markup=city_keyboard(language, back=False))
        return
    await state.update_data(city_key=selected[0], city=selected[1], district=None, microdistrict=None,
                            district_custom=False, micro_custom=False)
    await _go_next(message, state, "city")


@router.message(ListingForm.district, F.text)
async def listing_district(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")
    if _matches(message.text, "other_district"):
        await state.update_data(district_custom=True, micro_custom=False, microdistrict=None)
        await _set_listing_step(message, state, "custom_district")
        return
    entry = next((item for item in district_entries(data.get("city_key"))
                  if label_for(item["name"], language) == message.text), None)
    if not entry:
        await message.answer(tr(language, "invalid_choice"), reply_markup=district_keyboard(data.get("city_key"), language))
        return
    await state.update_data(district=label_for(entry["name"], "ru"), microdistrict=None,
                            district_custom=False, micro_custom=False)
    await _go_next(message, state, "district")


@router.message(ListingForm.custom_district, F.text)
async def listing_custom_district(message: Message, state: FSMContext):
    value = (message.text or "").strip()
    language = await _language(message, state)
    if not value or len(value) > 100:
        await message.answer(tr(language, "custom_district_prompt"), reply_markup=nav_rows([], language))
        return
    await state.update_data(district=value, microdistrict=None)
    await _go_next(message, state, "custom_district")


@router.message(ListingForm.microdistrict, F.text)
async def listing_microdistrict(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")
    if _matches(message.text, "other_microdistrict"):
        await state.update_data(micro_custom=True)
        await _set_listing_step(message, state, "custom_microdistrict")
        return
    entry = district_entry(data.get("city_key"), data.get("district"))
    selected = next((item for item in (entry or {}).get("microdistricts", [])
                     if label_for(item, language) == message.text), None)
    if not selected:
        await message.answer(tr(language, "invalid_choice"),
                             reply_markup=microdistrict_keyboard(data.get("city_key"), data.get("district", ""), language))
        return
    await state.update_data(microdistrict=label_for(selected, "ru"), micro_custom=False)
    await _go_next(message, state, "microdistrict")


@router.message(ListingForm.custom_microdistrict, F.text)
async def listing_custom_microdistrict(message: Message, state: FSMContext):
    value = (message.text or "").strip()
    language = await _language(message, state)
    if not value or len(value) > 100:
        await message.answer(tr(language, "custom_microdistrict_prompt"), reply_markup=nav_rows([], language))
        return
    await state.update_data(microdistrict=value)
    await _go_next(message, state, "custom_microdistrict")


@router.message(ListingForm.property_type, F.text)
async def listing_property_type(message: Message, state: FSMContext):
    language = await _language(message, state)
    selected = next((code for code, key in PROPERTY_CHOICES.items() if _matches(message.text, key)), None)
    if not selected:
        await message.answer(tr(language, "invalid_choice"), reply_markup=property_keyboard(language))
        return
    await state.update_data(property_type=selected, property_floor=None, rooms=None)
    await _go_next(message, state, "property_type")


@router.message(ListingForm.deal, F.text)
async def listing_deal(message: Message, state: FSMContext):
    language = await _language(message, state)
    if _matches(message.text, "deal_rent"):
        purpose = "rent"
    elif _matches(message.text, "deal_sale"):
        purpose = "sale"
    else:
        await message.answer(tr(language, "invalid_choice"), reply_markup=deal_keyboard(language))
        return
    await state.update_data(purpose=purpose)
    await _go_next(message, state, "deal")


@router.message(ListingForm.area, F.text)
async def listing_area(message: Message, state: FSMContext):
    language = await _language(message, state)
    value = parse_number(message.text)
    if value is None or value <= 0 or value > 100000:
        await message.answer(tr(language, "invalid_number"), reply_markup=nav_rows([], language))
        return
    await state.update_data(area=float(value))
    await _go_next(message, state, "area")


@router.message(ListingForm.rooms, F.text)
async def listing_rooms(message: Message, state: FSMContext):
    language = await _language(message, state)
    text = (message.text or "").strip().rstrip("+")
    if not text.isdigit() or not 1 <= int(text) <= 50:
        await message.answer(tr(language, "invalid_number"), reply_markup=rooms_keyboard(language))
        return
    await state.update_data(rooms=int(text))
    await _go_next(message, state, "rooms")


@router.callback_query(ListingForm.floor, F.data.startswith("floorpage:"))
async def floor_page(callback: CallbackQuery, state: FSMContext):
    try:
        page = max(0, min(5, int(callback.data.split(":", 1)[1])))
    except (ValueError, IndexError):
        await callback.answer()
        return
    language = await _language(callback, state)
    await callback.message.edit_text(
        tr(language, "floor_page", start=page * 10 + 1, end=page * 10 + 10),
        reply_markup=floor_keyboard(page, language),
    )
    await callback.answer()


@router.callback_query(ListingForm.floor, F.data.startswith("floor:"))
async def floor_select(callback: CallbackQuery, state: FSMContext):
    value = callback.data.split(":", 1)[1]
    if not value.lstrip("-").isdigit():
        await callback.answer()
        return
    await state.update_data(property_floor=int(value))
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await _go_next(callback.message, state, "floor")


@router.callback_query(F.data.startswith("floor"))
async def floor_outdated(callback: CallbackQuery):
    """Нажатие на старую клавиатуру этажей вне шага «этаж» — просто убираем часики."""
    await callback.answer()


@router.message(ListingForm.floor, F.text)
async def listing_floor_text(message: Message, state: FSMContext):
    language = await _language(message, state)
    text = (message.text or "").strip()
    if not text.lstrip("-").isdigit() or not -5 <= int(text) <= 150:
        await message.answer(tr(language, "invalid_number"))
        return
    await state.update_data(property_floor=int(text))
    await _go_next(message, state, "floor")


@router.message(ListingForm.price, F.text)
async def listing_price(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")
    parsed = parse_price(message.text)
    if not parsed or parsed[0] > Decimal("1e15"):
        await message.answer(tr(language, "invalid_number"), reply_markup=nav_rows([], language))
        return
    amount, currency = parsed
    purpose = data.get("purpose")
    rate = None
    if purpose == "sale" or currency == "USD":
        try:
            rate = Decimal(str(await get_usd_uzs_rate()))
        except Exception:
            await message.answer(tr(language, "rate_error"), reply_markup=nav_rows([], language))
            return
    price_uzs = int((amount * rate if currency == "USD" else amount).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    error = price_error(purpose, price_uzs, rate)
    if error:
        min_uzs = money(Decimal(MIN_SALE_PRICE_USD) * rate) if rate else "—"
        await message.answer(tr(language, error, min_uzs=min_uzs), reply_markup=nav_rows([], language))
        return
    await state.update_data(price_uzs=price_uzs)
    await _go_next(message, state, "price")


@router.message(ListingForm.description, F.text)
async def listing_description(message: Message, state: FSMContext):
    language = await _language(message, state)
    if _matches(message.text, "skip"):
        await state.update_data(description=None)
    else:
        text = message.text.strip()
        if len(text) > MAX_DESCRIPTION:
            await message.answer(tr(language, "description_too_long", length=len(text)), reply_markup=skip_keyboard(language))
            return
        await state.update_data(description=text)
    await _go_next(message, state, "description")


@router.message(ListingForm.phone, F.contact)
async def listing_phone_contact(message: Message, state: FSMContext):
    language = await _language(message, state)
    phone = normalize_phone(message.contact.phone_number if message.contact else "")
    if not phone:
        await message.answer(tr(language, "invalid_phone"), reply_markup=phone_keyboard(language))
        return
    await _finish_listing(message, state, phone)


@router.message(ListingForm.phone, F.text)
async def listing_phone_text(message: Message, state: FSMContext):
    language = await _language(message, state)
    if _matches(message.text, "manual_phone"):
        await message.answer(tr(language, "manual_phone_prompt"), reply_markup=phone_keyboard(language))
        return
    phone = normalize_phone(message.text)
    if not phone:
        await message.answer(tr(language, "invalid_phone"), reply_markup=phone_keyboard(language))
        return
    await _finish_listing(message, state, phone)


# ------------------------------------------------------------------ photos

@router.message(PhotoForm.waiting_photos, F.photo)
async def photo_received(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")
    order_id = data.get("order_id")
    if not order_id:
        await message.answer(tr(language, "not_found"), reply_markup=main_menu_keyboard(language))
        await _show_main_silent(state, language)
        return
    photo = message.photo[-1]
    added, count = await add_photo_to_order(int(order_id), photo.file_id, photo.file_unique_id, MAX_PHOTOS)
    if not added and count >= MAX_PHOTOS:
        await message.answer(tr(language, "photo_limit"), reply_markup=photos_keyboard(language))
        return
    await message.answer(tr(language, "photo_added", count=count), reply_markup=photos_keyboard(language))


@router.message(PhotoForm.waiting_photos, F.text.in_(all_variants("photos_done")))
async def photos_done(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "ru")
    order_id = data.get("order_id")
    order = await get_order(order_id) if order_id else None
    if not order or order["user_id"] != message.from_user.id or order["status"] not in DRAFT_STATUSES:
        await message.answer(tr(language, "not_found"), reply_markup=main_menu_keyboard(language))
        await _show_main_silent(state, language)
        return
    if not await get_order_photos(int(order_id)):
        await message.answer(tr(language, "photos_required"), reply_markup=photos_keyboard(language))
        return
    from handlers.payment import show_listing_payment
    await show_listing_payment(message, state, int(order_id), language)


@router.message(PhotoForm.waiting_photos)
async def photos_wrong_input(message: Message, state: FSMContext):
    language = await _language(message, state)
    await message.answer(tr(language, "photos_prompt"), reply_markup=photos_keyboard(language))
