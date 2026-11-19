"""Crypto Pay API (@CryptoBot) — прямые запросы без сторонней библиотеки.

Документация: https://help.crypt.bot/crypto-pay-api
Токен: @CryptoBot → Crypto Pay → My Apps → приложение → API Token.
Если токен создан в тестовом боте @CryptoTestnetBot — задайте CRYPTO_PAY_NETWORK=test."""
from __future__ import annotations

import logging
import os

import aiohttp

from config import CRYPTO_PAY_TOKEN

log = logging.getLogger(__name__)

NETWORK = os.getenv("CRYPTO_PAY_NETWORK", "main").strip().lower()
API_URL = "https://testnet-pay.crypt.bot/api" if NETWORK == "test" else "https://pay.crypt.bot/api"
INVOICE_LIFETIME_SECONDS = 3600


class CryptoPayError(RuntimeError):
    pass


async def _call(method: str, params: dict) -> dict:
    if not CRYPTO_PAY_TOKEN:
        raise CryptoPayError("CRYPTO_PAY_TOKEN is not set in Render → Environment")
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(
            f"{API_URL}/{method}",
            json=params,
            headers={"Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN},
        ) as response:
            payload = await response.json(content_type=None)
    if not payload.get("ok"):
        error = payload.get("error") or {}
        raise CryptoPayError(f"Crypto Pay {method} failed: {error.get('name') or error} (HTTP {response.status})")
    return payload["result"]


async def create_crypto_invoice(amount_usdt: float, description: str, order_id: int) -> dict:
    result = await _call("createInvoice", {
        "currency_type": "crypto",
        "asset": "USDT",
        "amount": f"{amount_usdt:.2f}",
        "description": description[:1024],
        "payload": str(order_id),
        "expires_in": INVOICE_LIFETIME_SECONDS,
    })
    url = result.get("bot_invoice_url") or result.get("pay_url") or result.get("mini_app_invoice_url")
    return {"invoice_id": result.get("invoice_id"), "bot_invoice_url": url}


async def get_crypto_invoice_status(invoice_id: str | int) -> str:
    result = await _call("getInvoices", {"invoice_ids": str(invoice_id)})
    items = result.get("items", []) if isinstance(result, dict) else result
    if not items:
        return "not_found"
    return str(items[0].get("status", "unknown"))


async def check_token() -> str:
    """Проверка токена при запуске: возвращает имя приложения или текст ошибки."""
    try:
        me = await _call("getMe", {})
        return f"OK ({me.get('name')}, {NETWORK} net)"
    except Exception as exc:
        return f"ERROR: {exc}"
