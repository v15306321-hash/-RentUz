"""Последний роутер: ловит всё, что не обработали остальные.
Бот больше никогда не «молчит» — например, после нажатия на кнопку из старой
версии меню или при отправке стикера вместо ответа."""
from __future__ import annotations

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.db import get_user
from keyboards import main_menu_keyboard
from localization import normalize_language, tr

router = Router()


@router.message()
async def unknown_message(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language") or (await get_user(message.from_user.id) or {}).get("language")
    language = normalize_language(language)
    if await state.get_state() is None:
        await message.answer(tr(language, "main_title"), reply_markup=main_menu_keyboard(language))
    else:
        await message.answer(tr(language, "invalid_choice"))


@router.callback_query()
async def unknown_callback(callback: CallbackQuery):
    await callback.answer()
