"""Хранилище состояний диалогов (FSM) в PostgreSQL.

Раньше состояния жили в памяти и терялись при каждом перезапуске Render —
после этого кнопки «не реагировали». Теперь бот помнит шаг пользователя."""
from __future__ import annotations

from typing import Any, Mapping

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey

from database import db


def _key(key: StorageKey) -> str:
    return f"{key.bot_id}:{key.chat_id}:{key.user_id}:{key.thread_id or 0}:{key.destiny}"


class PostgresStorage(BaseStorage):
    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        value = state.state if isinstance(state, State) else state
        await db.fsm_set_state(_key(key), value)

    async def get_state(self, key: StorageKey) -> str | None:
        state, _ = await db.fsm_get(_key(key))
        return state

    async def set_data(self, key: StorageKey, data: Mapping[str, Any]) -> None:
        await db.fsm_set_data(_key(key), dict(data))

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        _, data = await db.fsm_get(_key(key))
        return dict(data)

    async def close(self) -> None:  # пул закрывается в bot.py
        pass
