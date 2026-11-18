"""Автопостинг одобренных объявлений в городские Telegram-каналы.

Бот должен быть администратором каждого канала с правом «Публикация сообщений»
и «Редактирование сообщений» (чтобы помечать пост как неактуальный).
Проверка: команда /channels в боте (только для администратора)."""
from __future__ import annotations

import html
import logging
import os

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import BOT_USERNAME, OWNER_CHAT_ID, SITE_URL
from database.db import get_order_photos, update_order
from keyboards import city_entry, district_entry, label_for, money

log = logging.getLogger(__name__)

CHANNELS = {
    "tashkent": "@rent_toshkent",
    "almalyk": "@rent_Olmaliq",
    "samarkand": "@rent_samarkandd",
    "andijan": "@rent_andijan",
    "namangan": "@rent_Namangan",
    "nukus": "@rent_nukus",
    "fergana": "@rent_fergana",
    "karshi": "@rent_karshi",
    "bukhara": "@rent_buxoro",
    "kokand": "@rent_kakand",
}
ENABLED = os.getenv("CHANNEL_POSTING", "on").strip().lower() not in {"off", "0", "false", "no"}

PROPERTY_RU = {"apartment": "🏢 Квартира", "house": "🏡 Дом / участок", "office": "💼 Офис",
               "shop": "🏬 Магазин / помещение", "warehouse": "🏭 Склад / производство"}
PROPERTY_UZ = {"apartment": "Kvartira", "house": "Hovli / uchastka", "office": "Ofis",
               "shop": "Do'kon / joy", "warehouse": "Ombor"}
INACTIVE_MARK = "❌ <b>НЕАКТУАЛЬНО</b> · <b>DOLZARB EMAS</b>"


def site_link(order: dict) -> str:
    return f"{SITE_URL}/#obj-{100000 + int(order['id'])}"


def _tag(text: str) -> str:
    return "#" + "".join(ch for ch in text if ch.isalnum() or ch == "_")


def build_caption(order: dict) -> str:
    is_sale = order.get("purpose") == "sale"
    city = city_entry(order.get("city_key"))
    district = district_entry(order.get("city_key"), order.get("district"))
    city_ru = order.get("city") or (label_for(city["name"], "ru") if city else "")
    city_uz = label_for(city["name"], "uz") if city else city_ru
    place_ru = ", ".join(x for x in (city_ru, order.get("microdistrict") or order.get("district")) if x)
    district_uz = label_for(district["name"], "uz") if district else (order.get("district") or "")
    micro_uz = order.get("microdistrict")
    if micro_uz and district:
        found = next((m for m in district.get("microdistricts", []) if label_for(m, "ru") == micro_uz), None)
        micro_uz = label_for(found, "uz") if found else micro_uz
    place_uz = ", ".join(x for x in (city_uz, micro_uz or district_uz) if x)

    specs = [f"{float(order['area']):g} м²"] if order.get("area") else []
    if order.get("rooms"):
        specs.append(f"{order['rooms']} комн.")
    if order.get("property_floor") is not None:
        specs.append(f"{order['property_floor']} этаж")
    price = money(order.get("price_uzs") or 0)
    deal_ru = "Продажа" if is_sale else "Аренда"
    deal_uz = "Sotuv" if is_sale else "Ijara"
    unit_ru = "" if is_sale else " / мес"
    unit_uz = "" if is_sale else " / oy"
    usd = f" (≈ ${order['price_usd']:,.0f})".replace(",", " ") if is_sale and order.get("price_usd") else ""

    lines = [
        f"<b>{PROPERTY_RU.get(order.get('property_type'), 'Объект')} — {deal_ru}</b>",
        f"📍 {html.escape(place_ru)}",
    ]
    if specs:
        lines.append("📐 " + " · ".join(specs))
    lines.append(f"💰 <b>{price} сум{unit_ru}</b>{usd}")
    if order.get("description"):
        desc = order["description"].strip()
        lines.append("")
        lines.append("📝 " + html.escape(desc[:450] + ("…" if len(desc) > 450 else "")))
    lines += [
        "",
        f"📞 {html.escape(order.get('phone') or '—')}",
        "",
        f"🇺🇿 {deal_uz} · {PROPERTY_UZ.get(order.get('property_type'), '')} · {html.escape(place_uz)} · {price} so'm{unit_uz}",
        "",
        " ".join([_tag(city_ru), "#аренда" if not is_sale else "#продажа", "#" + order["order_number"].replace("-", "")]),
    ]
    caption = "\n".join(lines)
    return caption[:1024]


def _keyboard(order: dict, active: bool) -> InlineKeyboardMarkup:
    rows = []
    if active:
        rows.append([InlineKeyboardButton(text="🏡 Подробнее на сайте · Saytda", url=site_link(order))])
    rows.append([InlineKeyboardButton(text="📝 Разместить своё · E'lon berish",
                                      url=f"https://t.me/{BOT_USERNAME}?start=list")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _notify_owner(bot: Bot, text: str) -> None:
    try:
        await bot.send_message(OWNER_CHAT_ID, text)
    except Exception:
        pass


async def post_listing(bot: Bot, order: dict) -> None:
    """Публикует объявление в канал его города. Ошибки не мешают публикации на сайте."""
    channel = CHANNELS.get(order.get("city_key") or "")
    if not ENABLED or not channel:
        return
    caption = build_caption(order)
    try:
        photos = await get_order_photos(order["id"])
        if photos:
            msg = await bot.send_photo(channel, photos[0]["file_id"], caption=caption, parse_mode="HTML",
                                       reply_markup=_keyboard(order, True))
        else:
            msg = await bot.send_message(channel, caption, parse_mode="HTML", reply_markup=_keyboard(order, True),
                                         disable_web_page_preview=True)
        await update_order(order["id"], channel_chat=channel, channel_message_id=msg.message_id)
    except Exception as exc:
        log.warning("Channel post failed for %s in %s: %s", order.get("order_number"), channel, exc)
        await _notify_owner(bot, f"⚠️ Не удалось опубликовать {order.get('order_number')} в канале {channel}:\n{exc}\n\n"
                                 "Проверьте, что бот — администратор канала с правом публикации. Команда /channels.")


async def mark_inactive(bot: Bot, order: dict) -> None:
    """Помечает пост в канале как неактуальный (объект сдан, продан или снят)."""
    if not order.get("channel_chat") or not order.get("channel_message_id"):
        return
    text = f"{INACTIVE_MARK}\n\n{build_caption(order)}"[:1024]
    chat, message_id = order["channel_chat"], int(order["channel_message_id"])
    try:
        photos = await get_order_photos(order["id"])
        if photos:
            await bot.edit_message_caption(chat_id=chat, message_id=message_id, caption=text, parse_mode="HTML",
                                           reply_markup=_keyboard(order, False))
        else:
            await bot.edit_message_text(text=text, chat_id=chat, message_id=message_id, parse_mode="HTML",
                                        reply_markup=_keyboard(order, False), disable_web_page_preview=True)
    except Exception as exc:
        log.warning("Could not mark channel post %s/%s inactive: %s", chat, message_id, exc)


async def check_channels(bot: Bot) -> list[str]:
    me = await bot.get_me()
    report = []
    for city_key, channel in CHANNELS.items():
        city = label_for((city_entry(city_key) or {}).get("name", {}), "ru") or city_key
        try:
            member = await bot.get_chat_member(channel, me.id)
            can_post = getattr(member, "can_post_messages", None)
            can_edit = getattr(member, "can_edit_messages", None)
            if member.status == "administrator" and can_post and can_edit:
                report.append(f"✅ {city} — {channel}")
            elif member.status == "administrator":
                missing = [n for n, ok in (("публикация", can_post), ("редактирование", can_edit)) if not ok]
                report.append(f"⚠️ {city} — {channel}: нет права «{', '.join(missing)}»")
            else:
                report.append(f"❌ {city} — {channel}: бот не администратор")
        except Exception as exc:
            report.append(f"❌ {city} — {channel}: {exc}")
    return report
