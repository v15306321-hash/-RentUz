"""Команды администратора. Роутер подключается ПЕРВЫМ, поэтому команды работают
на любом шаге диалога (раньше /channels мог перехватываться анкетой или поиском)."""
from __future__ import annotations

from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import OWNER_CHAT_ID
from database.db import get_order_by_number, pool
from handlers.payment import _unpublish
from services.channels import check_channels
from services.pricing import TASHKENT, promo_active, promo_end_label

router = Router()
ADMIN_COMMANDS = {"channels", "unpublish", "stats"}


def _is_owner(message: Message) -> bool:
    return message.from_user.id == OWNER_CHAT_ID


@router.message(Command("myid"))
async def my_id(message: Message):
    await message.answer(f"Ваш Telegram ID: <code>{message.from_user.id}</code>", parse_mode="HTML")


@router.message(Command(*ADMIN_COMMANDS), F.func(lambda m: m.from_user.id != OWNER_CHAT_ID))
async def not_owner(message: Message):
    await message.answer(
        "⛔ Эта команда доступна только администратору.\n"
        f"Ваш Telegram ID: <code>{message.from_user.id}</code>\n"
        "Если администратор — вы, укажите этот ID в Render → Environment → OWNER_CHAT_ID.",
        parse_mode="HTML",
    )


@router.message(Command("channels"))
async def channels_command(message: Message, state: FSMContext):
    """/channels — проверить, может ли бот публиковать в городские каналы."""
    await message.answer("⏳ Проверяю каналы…")
    report = await check_channels(message.bot)
    await message.answer(
        "📡 Каналы для автопостинга:\n\n" + "\n".join(report) +
        "\n\nЕсли ❌ — добавьте бота в канал администратором с правами "
        "«Публикация сообщений» и «Редактирование сообщений», затем повторите /channels.",
        disable_web_page_preview=True,
    )


@router.message(Command("unpublish"))
async def unpublish_command(message: Message, command: CommandObject):
    """/unpublish R-12 — снять объявление с сайта."""
    order = await get_order_by_number((command.args or "").strip()) if command.args else None
    if not order:
        await message.answer("Использование: /unpublish R-12")
        return
    if await _unpublish(message.bot, order["id"]):
        await message.answer(f"🗑 {order['order_number']} снято с сайта, пост в канале помечен как неактуальный.")
    else:
        await message.answer(f"{order['order_number']} сейчас не опубликовано (статус: {order['status']}).")


PAID_LISTING = "status IN ('published', 'rented', 'unpublished') AND published_at >= $1"
PERIODS = [("📅 Сегодня", "today"), ("🗓 7 дней", 7), ("🗓 30 дней", 30), ("🗓 60 дней", 60), ("♾ Всё время", None)]


def _since(period) -> datetime:
    now = datetime.now(TASHKENT)
    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period is None:
        return datetime(2000, 1, 1, tzinfo=TASHKENT)
    return now - timedelta(days=period)


def _money(v) -> str:
    return f"{int(v or 0):,}".replace(",", " ")


@router.message(Command("stats"))
async def stats_command(message: Message):
    """/stats — доход и количество объявлений: сегодня, 7, 30, 60 дней и за всё время."""
    blocks = []
    for title, period in PERIODS:
        since = _since(period)
        row = await pool().fetchrow(
            f"""
            SELECT
              (SELECT count(*) FROM orders WHERE {PAID_LISTING}) AS listings,
              (SELECT count(*) FROM orders WHERE {PAID_LISTING} AND payment_method = 'promo') AS free_listings,
              (SELECT coalesce(sum(service_fee), 0) FROM orders WHERE {PAID_LISTING}) AS listing_income,
              (SELECT count(*) FROM ads WHERE starts_at >= $1) AS ads,
              (SELECT coalesce(sum(amount_uzs), 0) FROM ads WHERE starts_at >= $1) AS ads_income,
              (SELECT count(*) FROM users WHERE created_at >= $1) AS new_users
            """,
            since,
        )
        total = int(row["listing_income"]) + int(row["ads_income"])
        blocks.append(
            f"<b>{title}</b>\n"
            f"🏠 Выложено объявлений: <b>{row['listings']}</b>"
            + (f" (из них бесплатно по акции: {row['free_listings']})" if row["free_listings"] else "") + "\n"
            f"💰 Доход с объявлений: <b>{_money(row['listing_income'])} сум</b>\n"
            f"📢 Реклама: {row['ads']} шт. — {_money(row['ads_income'])} сум\n"
            f"💵 Итого: <b>{_money(total)} сум</b>\n"
            f"👥 Новых пользователей: {row['new_users']}"
        )
    now = await pool().fetchrow(
        """
        SELECT (SELECT count(*) FROM orders WHERE status = 'published') AS live,
               (SELECT count(*) FROM orders WHERE status IN ('payment_review', 'moderation')) AS waiting,
               (SELECT count(*) FROM ads WHERE status = 'active' AND ends_at > now()) AS ads_live,
               (SELECT count(*) FROM users) AS users
        """
    )
    promo = f"🎁 Акция «первое бесплатно»: до {promo_end_label('ru')}" if promo_active() else "🎁 Акция: выключена"
    await message.answer(
        "📊 <b>Статистика RENT UZBEKISTAN</b>\n\n" + "\n\n".join(blocks) +
        f"\n\n<b>Сейчас</b>\n🟢 На сайте: {now['live']} · ⏳ Ждут проверки: {now['waiting']} · "
        f"📢 Реклама: {now['ads_live']} · 👥 Всего пользователей: {now['users']}\n{promo}\n\n"
        "<i>Доход — сумма комиссий и рекламы по подтверждённым оплатам, без учёта ваших расходов и возвратов.</i>",
        parse_mode="HTML",
    )
