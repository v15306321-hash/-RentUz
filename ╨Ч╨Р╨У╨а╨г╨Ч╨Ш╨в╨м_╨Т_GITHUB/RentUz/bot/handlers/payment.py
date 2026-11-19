"""Оплата размещения объявления, проверка администратором и публикация на сайте.

Публикация = статус 'published' в базе. Сайт сам забирает опубликованные
объявления через API бота (web/server.py), поэтому ничего «не теряется в пути»."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Message

from config import OWNER_CHAT_ID, PAYMENT_CARDS, PAYMENT_RECIPIENT, SITE_URL
from database.db import (
    has_previous_listing,
    get_order,
    get_order_photos,
    qualify_referral,
    referral_stats,
    release_referral_credits,
    reserve_referral_credits,
    transition_order,
    update_order,
)
from keyboards import main_menu_keyboard, money, nav_rows, payment_keyboard
from localization import normalize_language, tr
from services.channels import mark_inactive, post_listing
from services.crypto_pay import create_crypto_invoice, get_crypto_invoice_status
from services.pricing import MAX_DISCOUNT_FRIENDS, apply_discount, discount_percent, promo_active, service_fee_usdt
from .states import PaymentForm

router = Router()
log = logging.getLogger(__name__)

PAYABLE_STATUSES = ("awaiting_photos", "awaiting_payment", "awaiting_receipt", "awaiting_crypto_payment")
METHODS = PAYMENT_CARDS  # совместимость: {"Click": ("click", "8802 …"), …}
METHOD_LABELS = {"click": "Click", "humo": "Humo", "uzum_bank": "Uzum Bank", "crypto_pay": "Crypto Pay",
                 "promo": "🎁 Акция — бесплатно"}


def _admin_card(order: dict) -> str:
    from handlers.start import listing_summary_lines
    lines = [f"Заявка: {order['order_number']}"] + listing_summary_lines(order, "ru")
    username = f"@{order['contact_username']}" if order.get("contact_username") else "—"
    lines += [
        "",
        f"Пользователь: {order.get('contact_name') or '—'} ({username}, ID {order['user_id']})",
        f"Комиссия: {money(order.get('base_fee') or 0)} сум, скидка −{order.get('discount_percent') or 0}% "
        f"→ к оплате {money(order.get('service_fee') or 0)} сум",
        f"Способ оплаты: {METHOD_LABELS.get(order.get('payment_method') or '', '—')}",
    ]
    return "\n".join(lines)


async def _send_photos_to_owner(bot, order_id: int) -> None:
    photos = await get_order_photos(order_id)
    if photos:
        await bot.send_media_group(OWNER_CHAT_ID, [InputMediaPhoto(media=p["file_id"]) for p in photos[:10]])


async def send_for_moderation(bot, order: dict, title: str) -> None:
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опубликовать", callback_data=f"publish_order:{order['id']}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline_order:{order['id']}")],
    ])
    try:
        await _send_photos_to_owner(bot, order["id"])
        await bot.send_message(OWNER_CHAT_ID, f"{title}\n\n" + _admin_card(order), reply_markup=markup)
    except Exception:
        log.exception("Failed to send %s for moderation", order.get("order_number"))


async def _free_by_promo(message: Message, state: FSMContext, order: dict, language: str) -> bool:
    """Акция «первое объявление бесплатно»: без оплаты сразу на проверку администратору."""
    if not promo_active() or await has_previous_listing(order["user_id"], order["id"]):
        return False
    await release_referral_credits(order["id"])  # скидка за друзей сохранится на следующее объявление
    updated = await transition_order(order["id"], PAYABLE_STATUSES, "moderation", discount_percent=0, service_fee=0,
                                     payment_method="promo", payment_status="free")
    if not updated:
        return False
    await state.set_state(None)
    await state.set_data({"language": language})
    await message.answer(tr(language, "promo_free_sent", number=updated["order_number"]),
                         reply_markup=main_menu_keyboard(language))
    await send_for_moderation(message.bot, updated, "🎁 АКЦИЯ: ПЕРВОЕ ОБЪЯВЛЕНИЕ БЕСПЛАТНО — ПРОВЕРЬТЕ")
    return True


async def show_listing_payment(message: Message, state: FSMContext, order_id: int | str, language: str) -> None:
    """Экран оплаты: считает комиссию со скидкой за друзей и показывает способы оплаты."""
    order = await get_order(order_id)
    if not order or order["user_id"] != message.chat.id or order["status"] not in PAYABLE_STATUSES:
        await message.answer(tr(language, "not_found"), reply_markup=main_menu_keyboard(language))
        await state.set_state(None)
        return
    if await _free_by_promo(message, state, order, language):
        return

    friends = await reserve_referral_credits(order["user_id"], order["id"], MAX_DISCOUNT_FRIENDS)
    percent = discount_percent(friends)
    fee = apply_discount(int(order["base_fee"]), percent)
    await update_order(order["id"], status="awaiting_payment", discount_percent=percent, service_fee=fee)

    cur = tr(language, "currency")
    lines = [f"{tr(language, 'service_fee')}: {money(order['base_fee'])} {cur}"]
    if percent:
        lines.append(tr(language, "discount_line", percent=percent))
    lines.append(f"{tr(language, 'fee_to_pay')}: {money(fee)} {cur}")

    await state.update_data(order_id=order["id"], language=language)
    await state.set_state(PaymentForm.choosing_method)
    await message.answer(
        tr(language, "payment_summary", number=order["order_number"], lines="\n".join(lines)),
        reply_markup=payment_keyboard(language),
    )


@router.message(PaymentForm.choosing_method, F.text)
async def payment_method_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    language = normalize_language(data.get("language"))
    order = await get_order(data["order_id"]) if data.get("order_id") else None
    if not order or order["user_id"] != message.from_user.id or order["status"] not in PAYABLE_STATUSES:
        await message.answer(tr(language, "not_found"), reply_markup=main_menu_keyboard(language))
        await state.set_state(None)
        return

    if message.text == "Crypto Pay":
        await create_crypto_payment(message, state, order, language)
        return
    if message.text not in METHODS:
        await message.answer(tr(language, "payment_method_prompt"), reply_markup=payment_keyboard(language))
        return

    method, card_number = METHODS[message.text]
    await update_order(order["id"], payment_method=method, payment_status="awaiting_receipt", status="awaiting_receipt")
    await state.set_state(PaymentForm.waiting_receipt)
    text = tr(language, "pay_card_text", method=message.text, recipient=PAYMENT_RECIPIENT,
              card=card_number, amount=money(order["service_fee"]))
    await message.answer(f"{text}\n\n{tr(language, 'receipt_prompt')}", reply_markup=nav_rows([], language))


async def create_crypto_payment(message: Message, state: FSMContext, order: dict, language: str) -> None:
    rate = Decimal(str(order.get("exchange_rate") or 0))
    if rate <= 0:
        await message.answer(tr(language, "rate_error"), reply_markup=payment_keyboard(language))
        return
    amount_usdt = service_fee_usdt(order["service_fee"], rate)
    if amount_usdt < Decimal("0.01"):
        await message.answer(tr(language, "crypto_min"), reply_markup=payment_keyboard(language))
        return

    await message.answer(tr(language, "crypto_creating"))
    try:
        invoice = await create_crypto_invoice(float(amount_usdt), f"Listing fee {order['order_number']}", int(order["id"]))
        invoice_id, invoice_url = invoice.get("invoice_id"), invoice.get("bot_invoice_url")
        if not invoice_id or not invoice_url:
            raise RuntimeError("Crypto Pay did not return an invoice ID and URL")
    except Exception:
        log.exception("Crypto Pay invoice creation failed")
        await message.answer(tr(language, "crypto_create_failed"), reply_markup=payment_keyboard(language))
        return

    await update_order(order["id"], payment_method="crypto_pay", payment_status="pending",
                       crypto_invoice_id=str(invoice_id), crypto_invoice_url=invoice_url,
                       status="awaiting_crypto_payment")
    await state.set_state(PaymentForm.waiting_crypto)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=tr(language, "crypto_pay_btn"), url=invoice_url)],
        [InlineKeyboardButton(text=tr(language, "crypto_check_btn"), callback_data=f"check_crypto:{order['id']}")],
    ])
    await message.answer(tr(language, "crypto_invoice", number=order["order_number"], amount=float(amount_usdt)),
                         reply_markup=keyboard)
    await message.answer(tr(language, "crypto_wait"), reply_markup=nav_rows([], language))


@router.message(PaymentForm.waiting_receipt, F.photo | F.document)
async def receive_payment_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    language = normalize_language(data.get("language"))
    order = await get_order(data["order_id"]) if data.get("order_id") else None
    if not order or order["user_id"] != message.from_user.id:
        await message.answer(tr(language, "not_found"), reply_markup=main_menu_keyboard(language))
        await state.set_state(None)
        return

    if message.photo:
        file_id, is_photo = message.photo[-1].file_id, True
    else:
        if (message.document.mime_type or "").lower() != "application/pdf":
            await message.answer(tr(language, "receipt_pdf_only"))
            return
        file_id, is_photo = message.document.file_id, False

    order = await transition_order(order["id"], ("awaiting_receipt",), "payment_review",
                                   receipt_file_id=file_id, payment_status="manual_review")
    if not order:  # чек уже отправлен (двойное сообщение)
        await message.answer(tr(language, "receipt_sent"), reply_markup=main_menu_keyboard(language))
        await state.set_state(None)
        return

    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оплата получена — опубликовать", callback_data=f"approve_order:{order['id']}")],
        [InlineKeyboardButton(text="❌ Отклонить чек", callback_data=f"reject_order:{order['id']}")],
    ])
    try:
        await _send_photos_to_owner(message.bot, order["id"])
        if is_photo:
            await message.bot.send_photo(OWNER_CHAT_ID, file_id, caption=f"🧾 Чек по заявке {order['order_number']}")
        else:
            await message.bot.send_document(OWNER_CHAT_ID, file_id, caption=f"🧾 Чек по заявке {order['order_number']}")
        await message.bot.send_message(OWNER_CHAT_ID, "🧾 ПРОВЕРКА ОПЛАТЫ ОБЪЯВЛЕНИЯ\n\n" + _admin_card(order),
                                       reply_markup=admin_keyboard)
    except Exception:
        log.exception("Failed to deliver receipt to owner")
        await update_order(order["id"], receipt_file_id=None, payment_status="pending", status="awaiting_receipt")
        await message.answer(tr(language, "support_unavailable"), reply_markup=nav_rows([], language))
        return

    await message.answer(tr(language, "receipt_sent"), reply_markup=main_menu_keyboard(language))
    await state.set_state(None)
    await state.set_data({"language": language})


@router.message(PaymentForm.waiting_receipt)
async def wrong_receipt_input(message: Message, state: FSMContext):
    language = normalize_language((await state.get_data()).get("language"))
    await message.answer(tr(language, "receipt_prompt"), reply_markup=nav_rows([], language))


@router.message(PaymentForm.waiting_crypto)
async def waiting_crypto_message(message: Message, state: FSMContext):
    language = normalize_language((await state.get_data()).get("language"))
    await message.answer(tr(language, "crypto_wait"), reply_markup=nav_rows([], language))


@router.callback_query(F.data.startswith("check_crypto:"))
async def check_crypto_payment(callback: CallbackQuery, state: FSMContext):
    try:
        order_id = int(callback.data.split(":", 1)[1])
    except (ValueError, IndexError):
        await callback.answer()
        return
    order = await get_order(order_id)
    if not order or order["user_id"] != callback.from_user.id:
        await callback.answer(tr("ru", "invalid_payment_order"), show_alert=True)
        return
    language = normalize_language(order.get("language"))
    if order["status"] in {"moderation", "published"}:
        await callback.answer(tr(language, "payment_already_confirmed"))
        return
    if order["status"] != "awaiting_crypto_payment" or not order.get("crypto_invoice_id"):
        await callback.answer(tr(language, "invoice_not_found"), show_alert=True)
        return
    try:
        status = await get_crypto_invoice_status(order["crypto_invoice_id"])
    except Exception:
        log.exception("Crypto Pay status check failed")
        await callback.answer(tr(language, "payment_check_error"), show_alert=True)
        return

    if status == "paid":
        order = await transition_order(order_id, ("awaiting_crypto_payment",), "moderation", payment_status="paid")
        if not order:
            await callback.answer(tr(language, "payment_already_confirmed"))
            return
        await callback.answer(tr(language, "payment_approved"))
        await callback.message.answer(tr(language, "listing_moderation", number=order["order_number"]),
                                      reply_markup=main_menu_keyboard(language))
        await state.set_state(None)
        await state.set_data({"language": language})
        await send_for_moderation(callback.bot, order, "💎 ОПЛАЧЕНО CRYPTO PAY — ПРОВЕРЬТЕ ОБЪЯВЛЕНИЕ")
    elif status == "expired":
        await update_order(order_id, payment_status="expired", status="awaiting_payment")
        await callback.answer(tr(language, "invoice_expired"), show_alert=True)
        await show_listing_payment(callback.message, state, order_id, language)
    else:
        await callback.answer(tr(language, "payment_pending"), show_alert=True)


# ------------------------------------------------------------------ администратор

def _is_owner(callback: CallbackQuery | Message) -> bool:
    return callback.from_user.id == OWNER_CHAT_ID


def _callback_id(callback: CallbackQuery) -> int | None:
    try:
        return int(callback.data.split(":", 1)[1])
    except (ValueError, IndexError):
        return None


async def _publish(bot, order: dict) -> None:
    """Действия после публикации: уведомить автора и засчитать приглашение."""
    language = normalize_language(order.get("language"))
    text = tr(language, "listing_published", number=order["order_number"])
    if SITE_URL:
        text += f"\n{SITE_URL}/#obj-{100000 + int(order['id'])}"
    try:
        await bot.send_message(order["user_id"], text, reply_markup=main_menu_keyboard(language))
    except Exception:
        log.warning("Could not notify user %s about publication", order["user_id"])

    await post_listing(bot, order)

    referrer_id = await qualify_referral(order["user_id"], order["id"])
    if referrer_id:
        stats = await referral_stats(referrer_id)
        from database.db import get_user
        referrer = await get_user(referrer_id)
        ref_lang = normalize_language((referrer or {}).get("language"))
        try:
            await bot.send_message(referrer_id, tr(ref_lang, "referral_qualified",
                                                   discount=discount_percent(stats["available"])))
        except Exception:
            log.warning("Could not notify referrer %s", referrer_id)


def _unpublish_markup(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🗑 Снять с сайта", callback_data=f"unpublish_order:{order_id}")
    ]])


@router.callback_query(F.data.startswith("approve_order:") | F.data.startswith("publish_order:"))
async def approve_order(callback: CallbackQuery):
    if not _is_owner(callback):
        await callback.answer("Только для администратора", show_alert=True)
        return
    order_id = _callback_id(callback)
    from_status = "payment_review" if callback.data.startswith("approve_order:") else "moderation"
    order = await transition_order(order_id, (from_status,), "published", payment_status="paid",
                                   published_at=datetime.now(timezone.utc)) if order_id else None
    if not order:
        await callback.answer("Заявка уже обработана", show_alert=True)
        return
    await _publish(callback.bot, order)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"✅ {order['order_number']} опубликовано на сайте.", reply_markup=_unpublish_markup(order_id))
    await callback.answer("Опубликовано")


@router.callback_query(F.data.startswith("reject_order:"))
async def reject_order(callback: CallbackQuery):
    if not _is_owner(callback):
        await callback.answer("Только для администратора", show_alert=True)
        return
    order_id = _callback_id(callback)
    order = await transition_order(order_id, ("payment_review",), "awaiting_payment", payment_status="rejected") if order_id else None
    if not order:
        await callback.answer("Заявка уже обработана", show_alert=True)
        return
    language = normalize_language(order.get("language"))
    try:
        await callback.bot.send_message(order["user_id"], tr(language, "payment_rejected"))
    except Exception:
        log.warning("Could not notify user %s", order["user_id"])
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"❌ {order['order_number']}: чек отклонён, пользователь может оплатить снова.")
    await callback.answer("Отклонено")


@router.callback_query(F.data.startswith("decline_order:"))
async def decline_order(callback: CallbackQuery):
    if not _is_owner(callback):
        await callback.answer("Только для администратора", show_alert=True)
        return
    order_id = _callback_id(callback)
    order = await transition_order(order_id, ("moderation",), "rejected") if order_id else None
    if not order:
        await callback.answer("Заявка уже обработана", show_alert=True)
        return
    await release_referral_credits(order_id)
    language = normalize_language(order.get("language"))
    try:
        await callback.bot.send_message(order["user_id"], tr(language, "listing_declined", number=order["order_number"]))
    except Exception:
        log.warning("Could not notify user %s", order["user_id"])
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"❌ {order['order_number']} отклонено. Не забудьте вернуть оплату.")
    await callback.answer("Отклонено")


async def _unpublish(bot, order_id: int) -> dict | None:
    order = await transition_order(order_id, ("published",), "unpublished")
    if order:
        await mark_inactive(bot, order)
        language = normalize_language(order.get("language"))
        try:
            await bot.send_message(order["user_id"], tr(language, "listing_unpublished", number=order["order_number"]))
        except Exception:
            pass
    return order


@router.callback_query(F.data.startswith("unpublish_order:"))
async def unpublish_order_cb(callback: CallbackQuery):
    if not _is_owner(callback):
        await callback.answer("Только для администратора", show_alert=True)
        return
    order = await _unpublish(callback.bot, _callback_id(callback) or 0)
    if not order:
        await callback.answer("Объявление уже снято", show_alert=True)
        return
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"🗑 {order['order_number']} снято с сайта.")
    await callback.answer()
