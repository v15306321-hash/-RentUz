# bot.py
"""Точка входа.

На Render (есть RENDER_EXTERNAL_URL) бот работает через webhook и сам открывает
порт $PORT — так Render не считает сервис «упавшим». На своём компьютере (адреса
нет) бот работает через polling, а API для сайта доступно на http://localhost:8080."""
import asyncio
import hashlib
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent
from aiohttp import web

from config import BOT_TOKEN, PORT, WEBHOOK_BASE_URL, WEBHOOK_SECRET
from database.db import close_db, init_db
from database.fsm_storage import PostgresStorage
from handlers import admin, advertising, fallback, my_listings, payment, start
from localization import tr
from web.server import build_app

log = logging.getLogger("bot")


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=PostgresStorage())
    # Порядок важен: в start — команды и кнопки главного меню (работают с любого шага).
    dp.include_router(admin.router)  # команды администратора — первыми, работают с любого шага
    dp.include_router(start.router)
    dp.include_router(payment.router)
    dp.include_router(advertising.router)
    dp.include_router(my_listings.router)
    dp.include_router(fallback.router)  # всегда последним

    @dp.errors()
    async def on_error(event: ErrorEvent) -> bool:
        log.exception("Update handling failed: %s", event.exception, exc_info=event.exception)
        update = event.update
        target = update.message or (update.callback_query.message if update.callback_query else None)
        try:
            if update.callback_query:
                await update.callback_query.answer()
            if target:
                await target.answer(tr("ru", "error_generic"))
        except Exception:
            pass
        return True

    return dp


async def reminders_loop(bot: Bot) -> None:
    """Раз в 30 минут: напоминания владельцам «Объявление ещё актуально?» (через 25 дней)."""
    from handlers.my_listings import send_due_reminders
    while True:
        try:
            sent = await send_due_reminders(bot)
            if sent:
                log.info("Sent %s listing reminders", sent)
        except Exception:
            log.exception("Reminder loop failed")
        await asyncio.sleep(1800)


async def set_commands(bot: Bot) -> None:
    """Кнопка «Меню» слева от поля ввода: /start для всех, админ-команды только владельцу."""
    from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault
    from config import OWNER_CHAT_ID
    base = [BotCommand(command="start", description="Главное меню / Asosiy menyu")]
    try:
        await bot.set_my_commands(base, scope=BotCommandScopeDefault())
        await bot.set_my_commands(base + [
            BotCommand(command="stats", description="📊 Статистика"),
            BotCommand(command="channels", description="📡 Проверить каналы"),
            BotCommand(command="unpublish", description="🗑 Снять объявление: /unpublish R-12"),
            BotCommand(command="myid", description="Мой Telegram ID"),
        ], scope=BotCommandScopeChat(chat_id=OWNER_CHAT_ID))
    except Exception as exc:
        log.warning("Could not set bot commands: %s", exc)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    await init_db()
    from services.crypto_pay import check_token
    log.info("Crypto Pay token check: %s", await check_token())

    bot = Bot(token=BOT_TOKEN)
    dp = create_dispatcher()
    secret = WEBHOOK_SECRET or hashlib.sha256(BOT_TOKEN.encode()).hexdigest()[:48]
    use_webhook = bool(WEBHOOK_BASE_URL)

    app = build_app(bot, dp, public_url=WEBHOOK_BASE_URL, webhook_secret=secret if use_webhook else None)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, host="0.0.0.0", port=PORT).start()
    log.info("HTTP server listening on port %s", PORT)

    await set_commands(bot)
    reminders = asyncio.create_task(reminders_loop(bot))

    try:
        if use_webhook:
            await bot.set_webhook(
                f"{WEBHOOK_BASE_URL}/webhook",
                secret_token=secret,
                allowed_updates=dp.resolve_used_update_types(),
            )
            log.info("Webhook mode: %s/webhook", WEBHOOK_BASE_URL)
            await asyncio.Event().wait()
        else:
            await bot.delete_webhook(drop_pending_updates=False)
            log.info("Polling mode (local run)")
            await dp.start_polling(bot)
    finally:
        reminders.cancel()
        await runner.cleanup()
        await bot.session.close()
        await close_db()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен.")
