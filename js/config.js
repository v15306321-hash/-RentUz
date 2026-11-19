/* Адрес API Telegram-бота на Render. Оттуда сайт берёт одобренные объявления и рекламу. */
window.RENT_API_ENABLED = true;
window.RENT_API_BASE = 'https://rentuz.onrender.com';

/* Акция «Первое объявление бесплатно»: последний день (как PROMO_FREE_FIRST_UNTIL у бота в Render).
   После этой даты строка про акцию на сайте исчезнет сама. Выключить сейчас — поставьте ''. */
window.RENT_PROMO_UNTIL = '2026-12-19';
