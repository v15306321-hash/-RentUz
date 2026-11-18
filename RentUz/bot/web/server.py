"""HTTP-сервер бота на Render:

* POST /webhook          — обновления от Telegram (секретный заголовок);
* GET  /health           — проверка, что сервис жив (Render, UptimeRobot);
* GET  /api/listings     — опубликованные объявления в формате сайта;
* GET  /api/ads          — активные рекламные баннеры;
* GET  /api/photo/{id}   — фото объявления (скачивается из Telegram, токен не раскрывается);
* GET  /api/ad-banner/{id} — картинка баннера.
"""
from __future__ import annotations

import logging
import time
from collections import OrderedDict

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

from database import db

log = logging.getLogger(__name__)

CATEGORY = {"apartment": "flat", "house": "house", "office": "office", "shop": "shop", "warehouse": "shop"}
SITE_ID_OFFSET = 100000  # id объявлений из бота на сайте: 100000 + номер заявки (не пересекаются с демо)
LIST_CACHE_SECONDS = 60
PHOTO_CACHE_ITEMS = 300

_photo_cache: OrderedDict[str, tuple[bytes, str]] = OrderedDict()
_json_cache: dict[str, tuple[float, list]] = {}


def _title(order: dict) -> str:
    rooms = order.get("rooms")
    kind = order.get("property_type")
    if kind == "apartment":
        return f"{rooms}-комнатная квартира" if rooms else "Квартира"
    if kind == "house":
        return f"Дом, {rooms} комн." if rooms else "Дом / участок"
    return {"office": "Офис", "shop": "Магазин / помещение", "warehouse": "Склад / производство"}.get(kind, "Объект")


def _number(value):
    if value is None:
        return 0
    return int(value) if float(value).is_integer() else round(float(value), 1)


def to_site_listing(order: dict, base_url: str) -> dict:
    is_sale = order.get("purpose") == "sale"
    floor = order.get("property_floor")
    username = order.get("contact_username")
    return {
        "id": SITE_ID_OFFSET + int(order["id"]),
        "source": "bot",
        "number": order.get("order_number"),
        "cat": CATEGORY.get(order.get("property_type"), "flat"),
        "title": _title(order),
        "city": order.get("city") or "",
        "district": order.get("microdistrict") or order.get("district") or "",
        "area": _number(order.get("area")),
        "rooms": int(order.get("rooms") or 0),
        "floor": f"{floor} этаж" if floor is not None else "—",
        "price": int(order.get("price_uzs") or 0),
        "unit": "" if is_sale else "мес",
        "term": "Продажа" if is_sale else "На месяц",
        "status": "free",
        "desc": order.get("description") or f"{_title(order)}, {_number(order.get('area'))} м². Подробности уточняйте у владельца.",
        "features": [],
        "photos": [f"{base_url}/api/photo/{pid}" for pid in (order.get("photo_ids") or [])],
        "phone": order.get("phone") or "",
        "owner": order.get("contact_name") or "",
        "tg": f"https://t.me/{username}" if username else "",
        "published": order["published_at"].isoformat() if order.get("published_at") else None,
    }


def _cors(response: web.StreamResponse) -> web.StreamResponse:
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    return response


def build_app(bot: Bot, dp: Dispatcher, *, public_url: str, webhook_secret: str | None) -> web.Application:
    app = web.Application()

    def base_url(request: web.Request) -> str:
        return public_url or f"{request.scheme}://{request.host}"

    async def cached(name: str, loader):
        hit = _json_cache.get(name)
        if hit and time.time() - hit[0] < LIST_CACHE_SECONDS:
            return hit[1]
        value = await loader()
        _json_cache[name] = (time.time(), value)
        return value

    async def health(_request: web.Request) -> web.Response:
        return web.Response(text="ok")

    async def listings(request: web.Request) -> web.Response:
        base = base_url(request)

        async def load():
            return [to_site_listing(o, base) for o in await db.published_listings_with_photos()]

        data = await cached("listings", load)
        response = web.json_response(data, headers={"Cache-Control": f"public, max-age={LIST_CACHE_SECONDS}"})
        return _cors(response)

    async def ads(request: web.Request) -> web.Response:
        base = base_url(request)

        async def load():
            return [
                {"id": ad["id"], "image": f"{base}/api/ad-banner/{ad['id']}", "link": ad.get("link") or "",
                 "until": ad["ends_at"].isoformat()}
                for ad in await db.active_ads()
            ]

        data = await cached("ads", load)
        return _cors(web.json_response(data, headers={"Cache-Control": f"public, max-age={LIST_CACHE_SECONDS}"}))

    async def _telegram_file(file_id: str) -> web.Response:
        hit = _photo_cache.get(file_id)
        if hit:
            _photo_cache.move_to_end(file_id)
            content, ctype = hit
        else:
            tg_file = await bot.get_file(file_id)
            buffer = await bot.download_file(tg_file.file_path)
            content = buffer.read()
            ctype = "image/png" if (tg_file.file_path or "").endswith(".png") else "image/jpeg"
            _photo_cache[file_id] = (content, ctype)
            while len(_photo_cache) > PHOTO_CACHE_ITEMS:
                _photo_cache.popitem(last=False)
        response = web.Response(body=content, content_type=ctype,
                                headers={"Cache-Control": "public, max-age=604800, immutable"})
        return _cors(response)

    async def photo(request: web.Request) -> web.Response:
        try:
            photo_id = int(request.match_info["photo_id"])
        except ValueError:
            raise web.HTTPNotFound()
        row = await db.get_photo(photo_id)
        if not row or row["order_status"] != "published":
            raise web.HTTPNotFound()
        return await _telegram_file(row["file_id"])

    async def ad_banner(request: web.Request) -> web.Response:
        try:
            ad = await db.get_advertising_request(int(request.match_info["ad_id"]))
        except ValueError:
            raise web.HTTPNotFound()
        if not ad or ad["status"] != "active":
            raise web.HTTPNotFound()
        return await _telegram_file(ad["banner_file_id"])

    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    app.router.add_get("/api/listings", listings)
    app.router.add_get("/api/ads", ads)
    app.router.add_get(r"/api/photo/{photo_id}", photo)
    app.router.add_get(r"/api/ad-banner/{ad_id}", ad_banner)

    if webhook_secret is not None:
        SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=webhook_secret).register(app, path="/webhook")
    return app
