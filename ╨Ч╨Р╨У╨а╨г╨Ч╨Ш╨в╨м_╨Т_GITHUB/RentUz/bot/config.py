"""Настройки бота. Все секреты берутся ТОЛЬКО из переменных окружения
(Render → Environment). Для запуска на своём компьютере скопируйте
.env.example в .env и заполните значения."""
from __future__ import annotations

import os
from pathlib import Path

# Локальный запуск: подхватываем .env, если он есть (на Render его нет).
_env_file = Path(__file__).resolve().parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _key, _value = _line.split("=", 1)
            os.environ.setdefault(_key.strip(), _value.strip().strip('"').strip("'"))


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Не задана переменная окружения {name}. См. .env.example")
    return value


# --- Обязательные ---
BOT_TOKEN = _required("BOT_TOKEN")
DATABASE_URL = _required("DATABASE_URL")          # строка подключения Neon
OWNER_CHAT_ID = int(_required("OWNER_CHAT_ID"))   # Telegram ID администратора

# --- Необязательные ---
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN", "").strip()
BOT_USERNAME = os.getenv("BOT_USERNAME", "Arenda_UZB_bot").lstrip("@")
SITE_URL = (os.getenv("SITE_URL") or "https://rentuz-1.onrender.com").strip().rstrip("/")  # адрес сайта

# Webhook: Render сам задаёт RENDER_EXTERNAL_URL для Web Service.
# Если адреса нет (запуск на ноутбуке) — бот работает через polling.
WEBHOOK_BASE_URL = (os.getenv("WEBHOOK_BASE_URL") or os.getenv("RENDER_EXTERNAL_URL") or "").rstrip("/")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()
PORT = int(os.getenv("PORT", "8080"))

# Реквизиты для ручной оплаты (можно переопределить в Render).
PAYMENT_RECIPIENT = os.getenv("PAYMENT_RECIPIENT", "Burtilev V.")
PAYMENT_CARDS = {
    "Click": ("click", os.getenv("CARD_CLICK", "8802 6112 4007 3151")),
    "Humo": ("humo", os.getenv("CARD_HUMO", "9860 0101 4036 3283")),
    "Uzum Bank": ("uzum_bank", os.getenv("CARD_UZUM", "4916 9903 1742 4379")),
}

# Акция «первое объявление бесплатно». Дата включительно (по Ташкенту), формат ГГГГ-ММ-ДД.
# Чтобы продлить — поменяйте дату в Render → Environment; чтобы выключить — PROMO_FREE_FIRST_UNTIL=off
PROMO_FREE_FIRST_UNTIL = os.getenv("PROMO_FREE_FIRST_UNTIL", "2026-12-19").strip()
