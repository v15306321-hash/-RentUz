"""Курс USD→UZS: сначала официальный курс ЦБ Узбекистана, запасной источник —
open.er-api.com. Курс кэшируется на час, чтобы не дёргать API на каждый шаг."""
from __future__ import annotations

import logging
import time

import aiohttp

CBU_URL = "https://cbu.uz/ru/arkhiv-kursov-valyut/json/USD/"
FALLBACK_URL = "https://open.er-api.com/v6/latest/USD"
CACHE_SECONDS = 3600

_cache: tuple[float, float] | None = None  # (rate, timestamp)
log = logging.getLogger(__name__)


def _check(rate: float) -> float:
    if not (1000 <= rate <= 100000):
        raise ValueError("Exchange-rate response is outside the expected range")
    return rate


async def _from_cbu(session: aiohttp.ClientSession) -> float:
    async with session.get(CBU_URL) as response:
        response.raise_for_status()
        payload = await response.json(content_type=None)
    return _check(float(str(payload[0]["Rate"]).replace(",", ".")))


async def _from_fallback(session: aiohttp.ClientSession) -> float:
    async with session.get(FALLBACK_URL) as response:
        response.raise_for_status()
        payload = await response.json(content_type=None)
    if payload.get("result") != "success":
        raise RuntimeError("Exchange-rate provider did not return success")
    return _check(float(payload["rates"]["UZS"]))


async def get_usd_uzs_rate() -> float:
    global _cache
    if _cache and time.time() - _cache[1] < CACHE_SECONDS:
        return _cache[0]
    timeout = aiohttp.ClientTimeout(total=8)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for source in (_from_cbu, _from_fallback):
            try:
                rate = await source(session)
                _cache = (rate, time.time())
                return rate
            except Exception as exc:  # пробуем следующий источник
                log.warning("Exchange rate source %s failed: %s", source.__name__, exc)
    if _cache:  # лучше вчерашний курс, чем никакого
        return _cache[0]
    raise RuntimeError("No exchange-rate source is available")
