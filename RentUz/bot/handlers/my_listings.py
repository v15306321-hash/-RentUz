"""«📋 Мои объявления»: владелец видит свои объявления и сам отмечает «Сдано / Продано»
или снимает объявление с публикации."""
from __future__ import annotations

import html
import logging
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from database.db import due_reminders, get_order, transition_order, update_order, user_orders
from localization import normalize_language, tr
from services.channels import mark_inactive, site_link

router = Router()
log = logging.getLogger(__name__)

REVIEW = {"payment_review", "moderation"}
DRAFT = {"draft", "awaiting_photos", "awaiting_payment", "awaiting_receipt", "awaiting_crypto_payment"}


def _kind(order: dict) -> str:
    return "sale" if order.get("purpose") == "sale" else "rent"


def _status(order: dict, language: str) -> str:
    status = order["status"]
    if status == "published":
        return tr(language, "my_status_published")
    if status == "rented":
        return tr(language, f"my_status_rented_{_kind(order)}")
    if status in REVIEW:
        return tr(language, "my_status_review")
    if status in DRAFT:
        return tr(language, "my_status_draft")
    if status == "rejected":
        return tr(language, "my_status_rejected")
    return tr(language, "my_status_unpublished")


def _card(order: dict, language: str) -> str:
    from handlers.start import listing_summary_lines
    lines = [line for line in listing_summary_lines(order, language) if not line.startswith(tr(language, "lbl_phone"))]
    return f"<b>{html.escape(order['order_number'])}</b> · {html.escape(_status(order, language))}\n\n" + html.escape("\n".join(lines))


def _buttons(order: dict, language: str) -> InlineKeyboardMarkup | None:
    rows = []
    if order["status"] == "published":
        rows.append([
            InlineKeyboardButton(text=tr(language, f"my_btn_done_{_kind(order)}"), callback_data=f"my_ask:done:{order['id']}"),
            InlineKeyboardButton(text=tr(language, "my_btn_remove"), callback_data=f"my_ask:remove:{order['id']}"),
        ])
    if order["status"] in {"published", "rented"}:
        rows.append([InlineKeyboardButton(text=tr(language, "my_btn_site"), url=site_link(order))])
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None


async def show_my_listings(message: Message, language: str) -> None:
    orders = await user_orders(message.chat.id)
    if not orders:
        await message.answer(tr(language, "my_empty"))
        return
    await message.answer(tr(language, "my_title", count=len(orders)))
    for order in orders:
        await message.answer(_card(order, language), parse_mode="HTML", reply_markup=_buttons(order, language),
                             disable_web_page_preview=True)


def _parse(data: str) -> tuple[str, int] | None:
    try:
        _, action, order_id = data.split(":", 2)
        return action, int(order_id)
    except ValueError:
        return None


async def _own_order(callback: CallbackQuery) -> tuple[str, dict] | None:
    parsed = _parse(callback.data)
    order = await get_order(parsed[1]) if parsed else None
    if not order or order["user_id"] != callback.from_user.id or parsed[0] not in {"done", "remove"}:
        await callback.answer(tr("ru", "invalid_payment_order"), show_alert=True)
        return None
    return parsed[0], order


@router.callback_query(F.data.startswith("my_ask:"))
async def ask_confirm(callback: CallbackQuery):
    found = await _own_order(callback)
    if not found:
        return
    action, order = found
    language = normalize_language(order.get("language"))
    if order["status"] != "published":
        await callback.answer(tr(language, "my_not_allowed"), show_alert=True)
        return
    key = f"my_confirm_done_{_kind(order)}" if action == "done" else "my_confirm_remove"
    await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=tr(language, "my_yes"), callback_data=f"my_do:{action}:{order['id']}"),
        InlineKeyboardButton(text=tr(language, "my_no"), callback_data=f"my_no:{action}:{order['id']}"),
    ]]))
    await callback.answer(tr(language, key, number=order["order_number"]), show_alert=True)


@router.callback_query(F.data.startswith("my_no:"))
async def cancel(callback: CallbackQuery):
    found = await _own_order(callback)
    if not found:
        return
    _, order = found
    language = normalize_language(order.get("language"))
    await callback.message.edit_reply_markup(reply_markup=_buttons(order, language))
    await callback.answer()


@router.callback_query(F.data.startswith("my_do:"))
async def do_action(callback: CallbackQuery):
    found = await _own_order(callback)
    if not found:
        return
    action, order = found
    language = normalize_language(order.get("language"))
    if action == "done":
        updated = await transition_order(order["id"], ("published",), "rented", rented_at=datetime.now(timezone.utc))
    else:
        updated = await transition_order(order["id"], ("published",), "unpublished")
    if not updated:
        await callback.answer(tr(language, "my_not_allowed"), show_alert=True)
        return
    await mark_inactive(callback.bot, updated)
    try:
        await callback.message.edit_text(_card(updated, language), parse_mode="HTML",
                                         reply_markup=_buttons(updated, language), disable_web_page_preview=True)
    except Exception:
        pass
    await callback.answer(tr(language, "my_done_ok" if action == "done" else "my_remove_ok"), show_alert=True)
    log.info("Owner %s set %s to %s", callback.from_user.id, updated["order_number"], updated["status"])


# ------------------------------------------------------------------ напоминание «Объявление ещё актуально?»

def _title(order: dict, language: str) -> str:
    from handlers.start import PROPERTY_CHOICES
    kind = tr(language, PROPERTY_CHOICES.get(order.get("property_type"), "property_apartment"))
    return f"{kind}, {order.get('microdistrict') or order.get('district') or order.get('city') or ''}".strip(", ")


async def send_due_reminders(bot) -> int:
    """Вызывается фоновой задачей раз в 30 минут. Возвращает число отправленных напоминаний."""
    sent = 0
    for order in await due_reminders():
        language = normalize_language(order.get("language"))
        kind = _kind(order)
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text=tr(language, "remind_yes"), callback_data=f"rem_yes:{order['id']}"),
            InlineKeyboardButton(text=tr(language, f"my_btn_done_{kind}"), callback_data=f"my_do:done:{order['id']}"),
        ]])
        try:
            await bot.send_message(order["user_id"], tr(language, "remind_text", number=order["order_number"],
                                                        title=_title(order, language),
                                                        done_word=tr(language, f"remind_done_word_{kind}")),
                                   reply_markup=markup)
            sent += 1
        except Exception as exc:  # пользователь заблокировал бота и т.п. — не повторяем бесконечно
            log.warning("Reminder for %s not delivered: %s", order["order_number"], exc)
        await update_order(order["id"], reminded_at=datetime.now(timezone.utc))
    return sent


@router.callback_query(F.data.startswith("rem_yes:"))
async def reminder_yes(callback: CallbackQuery):
    try:
        order = await get_order(int(callback.data.split(":", 1)[1]))
    except ValueError:
        order = None
    if not order or order["user_id"] != callback.from_user.id:
        await callback.answer(tr("ru", "invalid_payment_order"), show_alert=True)
        return
    language = normalize_language(order.get("language"))
    if order["status"] != "published":
        await callback.answer(tr(language, "my_not_allowed"), show_alert=True)
        return
    await update_order(order["id"], confirmed_at=datetime.now(timezone.utc))
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(tr(language, "remind_yes_ok"))
    await callback.answer()
