import asyncio
import logging
import sys
from os import getenv
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

# Загружаем локальные переменные из .env файла (если он есть при локальном запуске)
load_dotenv()

# Получаем токен бота из окружения Render
TOKEN = getenv("BOT_TOKEN")

# Инициализируем диспетчер и бота
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Этот хэндлер срабатывает на команду /start
    """
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! Бот успешно запущен и работает на Render 🚀")

async def main() -> None:
    # Проверяем, задан ли токен
    if not TOKEN:
        raise ValueError("Не найден BOT_TOKEN в переменных окружения!")

    # Инициализируем бота с настройками по умолчанию (HTML-разметка)
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Запускаем polling (бот начинает слушать сообщения)
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Настраиваем логирование, чтобы все ошибки и события были видны в панели Render
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен!")
      
