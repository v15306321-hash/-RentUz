"""Реклама на сайте: тариф → баннер 16:9 → оплата → проверка чека → модерация →
баннер показывается на сайте до окончания срока (сайт берёт его через API бота)."""
from __future__ import annotations

import logging
import re
from decimal import Decimal
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import OWNER_CHAT_ID, PAYMENT_CARDS, PAYMENT_RECIPIENT
from database.db import (
    activate_ad,
    create_advertising_request,
    get_advertising_request,
    transition_ad,
    update_advertising_request,
)
from keyboards import AD_TARIFFS, ad_tariff_from_text, ad_tariff_keyboard, main_menu_keyboard, money, nav_rows, payment_keyboard
from localization import normalize_language, tr
from services.crypto_pay import create_crypto_invoice, get_crypto_invoice_status
from services.exchange_rate import get_usd_uzs_rate
from services.pricing import service_fee_usdt
from .states import AdvertisingForm

router = Router()
TASHKENT = ZoneInfo("Asia/Tashkent")
log = logging.getLogger(__name__)

PAYABLE = ("awaiting_payment", "awaiting_receipt", "awaiting_crypto_payment")
METHOD_LABELS = {"click": "Click", "humo": "Humo", "uzum_bank": "Uzum Bank", "crypto_pay": "Crypto Pay"}
_LINK_RE = re.compile(r"(https?://\S+|t\.me/\S+|@[A-Za-z0-9_]{5,32})")


def _extract_link(caption: str | None) -> str | None:
    match = _LINK_RE.search(caption or "")
    if not match:
        return None
    value = match.group(1).rstrip(".,;)")
    if value.startswith("@"):
        return f"https://t.me/{value[1:]}"
    if value.startswith("t.me/"):
        return "https://" + value
    return value


def _admin_text(ad: dict, title: str) -> str:
    username = f"@{ad['username']}" if ad.get("username") else "—"
    return (
        f"{title}\n\n"
        f"Заявка: AD-{ad['id']:06d}\n"
        f"Пользователь: {ad.get('full_name') or '—'} ({username}, ID {ad['user_id']})\n"
        f"Тариф: {ad['duration_days']} дн. — {money(ad['amount_uzs'])} сум\n"
        f"Оплата: {METHOD_LABELS.get(ad.get('payment_method') or '', '—')}\n"
        f"Ссылка: {ad.get('link') or '—'}\n"
        f"Подпись: {ad.get('caption') or '—'}"
    )


async def show_ad_payment(message: Message, state: FSMContext, ad_id, language: str) -> None:
    ad = await get_advertising_request(ad_id)
    if not ad or ad["user_id"] != message.chat.id or ad["status"] not in PAYABLE:
        await message.answer(tr(language, "not_found"), reply_markup=main_menu_keyboard(language))
        await state.set_state(None)
        return
    await update_advertising_request(ad["id"], status="awaiting_payment")
    await state.update_data(ad_request_id=ad["id"], language=language)
    await state.set_state(AdvertisingForm.choosing_payment_method)
    await message.answer(tr(language, "ad_payment_prompt", amount=money(ad["amount_uzs"])),
                         reply_markup=payment_keyboard(language))


@router.message(AdvertisingForm.choosing_tariff, F.text)
async def advertising_tariff(message: Message, state: FSMContext):
    language = normalize_language((await state.get_data()).get("language"))
    days = ad_tariff_from_text(message.text)
    if not days:
        await message.answer(tr(language, "invalid_choice"), reply_markup=ad_tariff_keyboard(language))
        return
    await state.update_data(ad_days=days, ad_price=AD_TARIFFS[days], ad_request_id=None)
    await state.set_state(AdvertisingForm.banner)
    await message.answer(tr(language, "ad_banner_prompt"), reply_markup=nav_rows([], language))


@router.message(AdvertisingForm.banner, F.photo)
async def advertising_banner(message: Message, state: FSMContext):
    data = await state.get_data()
    language = normalize_language(data.get("language"))
    photo = message.photo[-1]
    ratio = photo.width / photo.height if photo.height else 0
    if not 1.70 <= ratio <= 1.85:
        await message.answer(tr(language, "ad_banner_invalid_ratio"), reply_markup=nav_rows([], language))
        return

    caption = (message.caption or "").strip() or None
    link = _extract_link(caption)
    existing = await get_advertising_request(data.get("ad_request_id"))
    if existing and existing["user_id"] == message.from_user.id and existing["status"] in PAYABLE:
        await update_advertising_request(existing["id"], duration_days=int(data["ad_days"]),
                                         amount_uzs=int(data["ad_price"]), banner_file_id=photo.file_id,
                                         caption=caption, link=link, status="awaiting_payment")
        ad = await get_advertising_request(existing["id"])
    else:
        ad = await create_advertising_request(
            user_id=message.from_user.id, username=message.from_user.username,
            full_name=message.from_user.full_name, language=language,
            duration_days=int(data["ad_days"]), amount_uzs=int(data["ad_price"]),
            banner_file_id=photo.file_id, caption=caption, link=link,
        )
    await message.answer(tr(language, "ad_banner_received"))
    await show_ad_payment(message, state, ad["id"], language)


@router.message(AdvertisingForm.banner)
async def advertising_banner_wrong_format(message: Message, state: FSMContext):
    language = normalize_language((await state.get_data()).get("language"))
    await message.answer(tr(language, "ad_banner_prompt"), reply_markup=nav_rows([], language))


@router.message(AdvertisingForm.choosing_payment_method, F.text)
async def advertising_payment_method(message: Message, state: FSMContext):
    data = await state.get_data()
    language = normalize_language(data.get("language"))
    ad = await get_advertising_request(data.get("ad_request_id"))
    if not ad or ad["user_id"] != message.from_user.id or ad["status"] not in PAYABLE:
        await message.answer(tr(language, "not_found"), reply_markup=main_menu_keyboard(language))
        await state.set_state(None)
        return

    if message.text == "Crypto Pay":
        await message.answer(tr(language, "crypto_creating"))
        try:
            rate = Decimal(str(await get_usd_uzs_rate()))
            amount_usdt = service_fee_usdt(ad["amount_uzs"], rate)
            invoice = await create_crypto_invoice(float(amount_usdt), f"Advertising AD-{ad['id']:06d}", int(ad["id"]))
            invoice_id, invoice_url = invoice.get("invoice_id"), invoice.get("bot_invoice_url")
            if not invoice_id or not invoice_url:
                raise RuntimeError("Crypto Pay did not return invoice ID or URL")
        except Exception:
            log.exception("Crypto Pay invoice for ad failed")
            await message.answer(tr(language, "crypto_create_failed"), reply_markup=payment_keyboard(language))
            return
        await update_advertising_request(ad["id"], payment_method="crypto_pay", payment_status="pending",
                                         crypto_invoice_id=str(invoice_id), crypto_invoice_url=invoice_url,
                                         exchange_rate=float(rate), status="awaiting_crypto_payment")
        await state.set_state(AdvertisingForm.waiting_crypto)
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=tr(language, "crypto_pay_btn"), url=invoice_url)],
            [InlineKeyboardButton(text=tr(language, "crypto_check_btn"), callback_data=f"check_ad_crypto:{ad['id']}")],
        ])
        await message.answer(tr(language, "ad_crypto_invoice", amount=float(amount_usdt)), reply_markup=markup)
        await message.answer(tr(language, "crypto_wait"), reply_markup=nav_rows([], language))
        return

    if message.text not in PAYMENT_CARDS:
        await message.answer(tr(language, "ad_payment_prompt", amount=money(ad["amount_uzs"])),
                             reply_markup=payment_keyboard(language))
        return

    method, card_number = PAYMENT_CARDS[message.text]
    await update_advertising_request(ad["id"], payment_method=method, payment_status="awaiting_receipt",
                                     status="awaiting_receipt")
    await state.set_state(AdvertisingForm.waiting_receipt)
    text = tr(language, "pay_card_text", method=message.text, recipient=PAYMENT_RECIPIENT,
              card=card_number, amount=money(ad["amount_uzs"]))
    await message.answer(f"{text}\n\n{tr(language, 'receipt_prompt')}", reply_markup=nav_rows([], language))


@router.message(AdvertisingForm.waiting_receipt, F.photo | F.document)
async def advertising_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    language = normalize_language(data.get("language"))
    ad = await get_advertising_request(data.get("ad_request_id"))
    if not ad or ad["user_id"] != message.from_user.id:
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

    ad = await transition_ad(ad["id"], ("awaiting_receipt",), "payment_review",
                             receipt_file_id=file_id, payment_status="manual_review")
    if not ad:
        await message.answer(tr(language, "ad_receipt_sent"), reply_markup=main_menu_keyboard(language))
        await state.set_state(None)
        return
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оплата получена", callback_data=f"adpay_approve:{ad['id']}")],
        [InlineKeyboardButton(text="❌ Отклонить чек", callback_data=f"adpay_reject:{ad['id']}")],
    ])
    try:
        await message.bot.send_photo(OWNER_CHAT_ID, ad["banner_file_id"], caption=f"Баннер AD-{ad['id']:06d}")
        if is_photo:
            await message.bot.send_photo(OWNER_CHAT_ID, file_id, caption=f"🧾 Чек AD-{ad['id']:06d}")
        else:
            await message.bot.send_document(OWNER_CHAT_ID, file_id, caption=f"🧾 Чек AD-{ad['id']:06d}")
        await message.bot.send_message(OWNER_CHAT_ID, _admin_text(ad, "🧾 ЧЕК ЗА РЕКЛАМУ — ПРОВЕРКА ОПЛАТЫ"),
                                       reply_markup=markup)
    except Exception:
        log.exception("Failed to deliver ad receipt to owner")
        await update_advertising_request(ad["id"], receipt_file_id=None, payment_status="pending", status="awaiting_receipt")
        await message.answer(tr(language, "support_unavailable"), reply_markup=nav_rows([], language))
        return
    await message.answer(tr(language, "ad_receipt_sent"), reply_markup=main_menu_keyboard(language))
    await state.set_state(None)
    await state.set_data({"language": language})


@router.message(AdvertisingForm.waiting_receipt)
async def advertising_receipt_wrong_format(message: Message, state: FSMContext):
    language = normalize_language((await state.get_data()).get("language"))
    await message.answer(tr(language, "receipt_prompt"), reply_markup=nav_rows([], language))


@router.message(AdvertisingForm.waiting_crypto)
async def advertising_waiting_crypto(message: Message, state: FSMContext):
    language = normalize_language((await state.get_data()).get("language"))
    await message.answer(tr(language, "crypto_wait"), reply_markup=nav_rows([], language))


async def _send_for_moderation(bot, ad: dict) -> None:
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опубликовать баннер", callback_data=f"adcontent_approve:{ad['id']}")],
        [InlineKeyboardButton(text="❌ Отклонить (возврат)", callback_data=f"adcontent_reject:{ad['id']}")],
    ])
    await bot.send_photo(OWNER_CHAT_ID, ad["banner_file_id"],
                         caption=_admin_text(ad, "📣 БАННЕР ОПЛАЧЕН — ОЖИДАЕТ МОДЕРАЦИИ")[:1024], reply_markup=markup)


def _is_owner(callback: CallbackQuery) -> bool:
    return callback.from_user.id == OWNER_CHAT_ID


def _cb_id(callback: CallbackQuery) -> int | None:
    try:
        return int(callback.data.split(":", 1)[1])
    except (ValueError, IndexError):
        return None


@router.callback_query(F.data.startswith("adpay_approve:"))
async def approve_ad_payment(callback: CallbackQuery):
    if not _is_owner(callback):
        await callback.answer("Только для администратора", show_alert=True)
        return
    ad = await transition_ad(_cb_id(callback) or 0, ("payment_review",), "paid_pending_moderation", payment_status="paid")
    if not ad:
        await callback.answer("Заявка уже обработана", show_alert=True)
        return
    language = normalize_language(ad.get("language"))
    try:
        await callback.bot.send_message(ad["user_id"], tr(language, "ad_payment_approved"))
    except Exception:
        pass
    await callback.message.edit_reply_markup(reply_markup=None)
    await _send_for_moderation(callback.bot, ad)
    await callback.answer("Оплата подтверждена")


@router.callback_query(F.data.startswith("adpay_reject:"))
async def reject_ad_payment(callback: CallbackQuery):
    if not _is_owner(callback):
        await callback.answer("Только для администратора", show_alert=True)
        return
    ad = await transition_ad(_cb_id(callback) or 0, ("payment_review",), "awaiting_payment", payment_status="rejected")
    if not ad:
        await callback.answer("Заявка уже обработана", show_alert=True)
        return
    language = normalize_language(ad.get("language"))
    retry = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=tr(language, "ad_retry_payment"), callback_data=f"ad_retry:{ad['id']}")
    ]])
    try:
        await callback.bot.send_message(ad["user_id"], tr(language, "ad_payment_rejected"), reply_markup=retry)
    except Exception:
        pass
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"❌ AD-{ad['id']:06d}: чек отклонён.")
    await callback.answer("Отклонено")


@router.callback_query(F.data.startswith("ad_retry:"))
async def retry_ad_payment(callback: CallbackQuery, state: FSMContext):
    ad = await get_advertising_request(_cb_id(callback))
    if not ad or ad["user_id"] != callback.from_user.id or ad["status"] not in PAYABLE:
        await callback.answer(tr("ru", "invalid_payment_order"), show_alert=True)
        return
    await callback.answer()
    await show_ad_payment(callback.message, state, ad["id"], normalize_language(ad.get("language")))


@router.callback_query(F.data.startswith("check_ad_crypto:"))
async def check_ad_crypto(callback: CallbackQuery, state: FSMContext):
    ad = await get_advertising_request(_cb_id(callback))
    if not ad or ad["user_id"] != callback.from_user.id:
        await callback.answer(tr("ru", "invalid_payment_order"), show_alert=True)
        return
    language = normalize_language(ad.get("language"))
    if ad["status"] in {"paid_pending_moderation", "active"}:
        await callback.answer(tr(language, "payment_already_confirmed"))
        return
    if ad["status"] != "awaiting_crypto_payment" or not ad.get("crypto_invoice_id"):
        await callback.answer(tr(language, "invoice_not_found"), show_alert=True)
        return
    try:
        status = await get_crypto_invoice_status(ad["crypto_invoice_id"])
    except Exception:
        await callback.answer(tr(language, "payment_check_error"), show_alert=True)
        return
    if status == "paid":
        ad = await transition_ad(ad["id"], ("awaiting_crypto_payment",), "paid_pending_moderation", payment_status="paid")
        if not ad:
            await callback.answer(tr(language, "payment_already_confirmed"))
            return
        await callback.answer(tr(language, "payment_approved"))
        await callback.message.answer(tr(language, "ad_payment_approved"), reply_markup=main_menu_keyboard(language))
        await state.set_state(None)
        await state.set_data({"language": language})
        try:
            await _send_for_moderation(callback.bot, ad)
        except Exception:
            log.exception("Failed to send ad for moderation")
    elif status == "expired":
        await update_advertising_request(ad["id"], payment_status="expired", status="awaiting_payment")
        await callback.answer(tr(language, "invoice_expired"), show_alert=True)
        await show_ad_payment(callback.message, state, ad["id"], language)
    else:
        await callback.answer(tr(language, "payment_pending"), show_alert=True)


@router.callback_query(F.data.startswith("adcontent_approve:"))
async def approve_ad_content(callback: CallbackQuery):
    if not _is_owner(callback):
        await callback.answer("Только для администратора", show_alert=True)
        return
    ad = await activate_ad(_cb_id(callback) or 0)
    if not ad:
        await callback.answer("Баннер уже обработан", show_alert=True)
        return
    language = normalize_language(ad.get("language"))
    until = ad["ends_at"].astimezone(TASHKENT).strftime("%d.%m.%Y %H:%M")
    try:
        await callback.bot.send_message(ad["user_id"], tr(language, "ad_content_approved", until=until),
                                        reply_markup=main_menu_keyboard(language))
    except Exception:
        pass
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"✅ AD-{ad['id']:06d}: баннер на сайте до {until}.")
    await callback.answer("Опубликовано")


@router.callback_query(F.data.startswith("adcontent_reject:"))
async def reject_ad_content(callback: CallbackQuery):
    if not _is_owner(callback):
        await callback.answer("Только для администратора", show_alert=True)
        return
    ad = await transition_ad(_cb_id(callback) or 0, ("paid_pending_moderation",), "rejected")
    if not ad:
        await callback.answer("Баннер уже обработан", show_alert=True)
        return
    language = normalize_language(ad.get("language"))
    try:
        await callback.bot.send_message(ad["user_id"], tr(language, "ad_content_rejected"),
                                        reply_markup=main_menu_keyboard(language))
    except Exception:
        pass
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"❌ AD-{ad['id']:06d}: баннер отклонён. Не забудьте вернуть оплату.")
    await callback.answer("Отклонено")
