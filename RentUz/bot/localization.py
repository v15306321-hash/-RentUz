# localization.py
LANGUAGES = {
    "ru": "Русский язык 🇷🇺",
    "uz": "O'zbek tili 🇺🇿",
}

LANGUAGE_PROMPT = (
    "👋 Добро пожаловать в RENT UZBEKISTAN! 🇷🇺\n"
    "Пожалуйста, выберите удобный для вас язык.\n\n"
    "👋 RENT UZBEKISTAN'ga xush kelibsiz! 🇺🇿\n"
    "Iltimos, o'zingizga qulay tilni tanlang."
)

TRANSLATIONS = {
    "ru": {
        # --- главное меню
        "menu_list": "📝 Подать объявление",
        "menu_search": "🔍 Найти недвижимость",
        "menu_ad": "📢 Реклама",
        "menu_referral": "🎁 Скидки -20%",
        "menu_language": "🇺🇿 O'zbek tili",
        "menu_support": "⚙️ Поддержка",
        "menu_fee": "💰 Тарифы",
        "main_title": "🏠 Главное меню. Выберите нужное действие:",
        "home": "🏠 Главное меню",
        "back": "◀️ Назад",
        "continue": "▶️ Продолжить",
        "restart": "🔄 Начать заново",
        "skip": "⏭ Пропустить",
        "language_prompt": LANGUAGE_PROMPT,
        "language_saved": "✅ Язык бота изменён на русский.",
        "error_generic": "⚠️ Что-то пошло не так. Попробуйте ещё раз или нажмите /start.",

        # --- анкета объявления
        "city_prompt": "Выберите город:",
        "district_prompt": "Выберите район в городе {city}:",
        "custom_district_prompt": "Введите название района вручную:",
        "other_district": "Другой район",
        "microdistrict_prompt": "Выберите микрорайон / массив:",
        "custom_microdistrict_prompt": "Введите название микрорайона / массива вручную:",
        "other_microdistrict": "Другой микрорайон",
        "property_prompt": "Выберите тип недвижимости:",
        "property_apartment": "🏢 Квартира",
        "property_house": "🏡 Дом / Участок",
        "property_office": "💼 Офис",
        "property_shop": "🏬 Магазин / Помещение",
        "property_warehouse": "🏭 Склад / Производство",
        "deal_prompt": "Выберите тип сделки:",
        "deal_rent": "🔑 Аренда",
        "deal_sale": "💰 Продажа",
        "area_prompt": "Введите площадь (в м²):",
        "rooms_prompt": "Сколько комнат?",
        "rooms_5plus": "5+",
        "floor_prompt": "Выберите этаж кнопкой ниже или напишите его числом:",
        "floor_label": "Этаж",
        "floor_page": "Выберите этаж (стр. {start}-{end}):",
        "price_prompt_rent": "Введите цену аренды в месяц (в сумах).\nМинимальная цена аренды — 1 000 000 сум.",
        "price_prompt_sale": "Введите цену продажи в сумах или в долларах (например: 70000$).\nМинимальная цена объекта — 5 000 $.",
        "min_rent_price": "❗ Минимальная цена аренды для размещения — 1 000 000 сум. Введите другую цену.",
        "min_sale_price": "❗ Минимальная цена объекта для размещения — 5 000 $ (≈ {min_uzs} сум по текущему курсу). Введите другую цену.",
        "description_prompt": "Напишите краткое описание объекта (ремонт, мебель, что рядом и т.п.) — до 800 символов.\nИли нажмите «Пропустить».",
        "description_too_long": "Описание слишком длинное ({length} символов). Сократите до 800 символов.",
        "phone_prompt": "Укажите номер телефона для связи:",
        "share_phone": "📱 Поделиться контактом",
        "manual_phone": "⌨️ Ввести вручную",
        "manual_phone_prompt": "Напишите номер телефона, например: +998 90 123 45 67",
        "photos_prompt": "Отправьте фотографии объекта (от 1 до 10). Когда закончите — нажмите «Готово».",
        "photos_done": "✅ Готово (сохранить)",
        "photos_required": "Пожалуйста, отправьте хотя бы одну фотографию!",
        "photo_added": "Фото добавлено! Всего: {count} из 10. Можете отправить еще или нажать «Готово».",
        "photo_limit": "Можно загрузить не больше 10 фотографий. Нажмите «Готово».",

        # --- итог заявки
        "listing_saved": "🎉 Данные объявления сохранены!",
        "order_no": "Заявка №{number}",
        "lbl_city": "Город",
        "lbl_district": "Район",
        "lbl_microdistrict": "Микрорайон",
        "lbl_property": "Тип",
        "lbl_area": "Площадь",
        "lbl_rooms": "Комнат",
        "lbl_deal": "Сделка",
        "lbl_description": "Описание",
        "lbl_phone": "Телефон",
        "rent_price": "Цена аренды",
        "sale_price": "Цена продажи",
        "per_month": "/ мес",
        "currency": "сум",
        "exchange_rate": "Курс валют",
        "service_fee": "Сервисный сбор",
        "discount_line": "🎁 Скидка за друзей: −{percent}%",
        "fee_to_pay": "К оплате",
        "period_warning": "Объявление будет опубликовано на сайте после оплаты и проверки.",

        # --- ошибки
        "rate_error": "Ошибка получения курса валют. Попробуйте позже.",
        "not_found": "Данные не найдены. Возврат в главное меню.",
        "invalid_choice": "Неверный выбор. Пожалуйста, используйте кнопки ниже.",
        "invalid_number": "Неверный формат числа. Попробуйте еще раз.",
        "invalid_phone": "Неверный формат телефона. Попробуйте еще раз.",
        "back_unavailable": "Возврат назад на этом этапе недоступен.",
        "draft_found": "У вас есть незавершенная заявка. Хотите продолжить или начать заново?",

        # --- тарифы
        "fee_info": (
            "💰 Тарифы размещения\n\n"
            "🔑 Аренда — 1% от цены аренды в месяц.\n"
            "   Минимальная цена аренды — 1 000 000 сум.\n\n"
            "💰 Продажа — 0,1% от цены объекта.\n"
            "   Минимальная цена объекта — 5 000 $.\n\n"
            "📢 Реклама на сайте:\n{ad_tariffs}\n\n"
            "🎁 Приглашайте друзей: −10% за каждого друга, который выставил объявление (до −30%)."
        ),

        # --- поддержка
        "support_intro": "Напишите ваше сообщение в поддержку, и мы свяжемся с вами:",
        "support_sent": "✅ Ваше сообщение отправлено в поддержку. Скоро ответим!",
        "support_unavailable": "Не удалось отправить сообщение. Попробуйте позже.",

        # --- поиск
        "search_city_prompt": "🔍 Выберите город для поиска недвижимости:",
        "search_deal_prompt": "🔑 Выберите тип сделки:",
        "search_site_info": (
            "🏡 Отличный выбор! Все актуальные объявления {deal} в городе {city} собраны "
            "на нашем сайте RENT UZBEKISTAN.\n\n"
            "На сайте вы сможете:\n"
            "🔎 удобно подобрать объект по району, цене, площади и количеству комнат;\n"
            "📸 посмотреть фотографии и подробное описание;\n"
            "📞 напрямую связаться с владельцем;\n"
            "❤️ сохранить понравившиеся варианты в избранное.\n\n"
            "Нажмите кнопку ниже, чтобы перейти в каталог. Желаем найти именно то, что вы ищете! ✨"
        ),
        "search_deal_rent": "об аренде",
        "search_deal_sale": "о продаже",
        "site_button": "🏡 Перейти на сайт",
        "search_empty": "По вашему запросу в городе {city} пока ничего не найдено.",
        "search_found": "🔍 Найдено объявлений: {count}. Показываю последние:",
        "search_more_site": "Все объявления с фото и фильтрами — на сайте: {url}",

        # --- оплата
        "payment_method_prompt": "Выберите способ оплаты:",
        "payment_summary": "💳 Оплата размещения {number}\n\n{lines}\n\nВыберите способ оплаты:",
        "pay_card_text": "💳 Оплата через {method}\n\nПолучатель: {recipient}\nНомер карты: {card}\nСумма: {amount} сум",
        "receipt_prompt": "После перевода отправьте сюда фотографию или PDF-файл чека. Оплата будет подтверждена администратором вручную.",
        "receipt_sent": "✅ Чек отправлен администратору. Ожидайте проверки. Скриншот сам по себе не означает, что оплата подтверждена.",
        "receipt_pdf_only": "Поддерживаются только фото или PDF-файл чека.",
        "crypto_creating": "⏳ Создаю счёт Crypto Pay…",
        "crypto_min": "Сумма слишком мала для оплаты через Crypto Pay. Выберите другой способ.",
        "crypto_create_failed": "Не удалось создать счёт Crypto Pay. Попробуйте позже или выберите другой способ.",
        "crypto_invoice": "💎 Счёт Crypto Pay создан.\n\nЗаказ: {number}\nСумма: {amount:.2f} USDT\n\nОплатите счёт, затем нажмите «Проверить оплату». Счёт действует 1 час.",
        "crypto_pay_btn": "Оплатить в USDT",
        "crypto_check_btn": "Проверить оплату",
        "crypto_wait": "Для проверки оплаты нажмите кнопку «Проверить оплату» под сообщением со счётом Crypto Pay.",
        "payment_approved": "✅ Оплата подтверждена!",
        "payment_rejected": "❌ Чек не принят администратором. Откройте «📝 Подать объявление» → «Продолжить», чтобы оплатить снова, или напишите в поддержку.",
        "payment_already_confirmed": "Оплата уже подтверждена.",
        "payment_check_error": "Не удалось проверить оплату. Попробуйте через минуту.",
        "payment_pending": "Оплата ещё не поступила.",
        "invoice_expired": "Срок действия счёта истёк. Выберите способ оплаты заново.",
        "invoice_not_found": "Счёт не найден.",
        "invalid_payment_order": "Заявка не найдена.",
        "listing_moderation": "✅ Оплата получена! Объявление {number} отправлено на проверку — после неё оно появится на сайте.",
        "listing_published": "🎉 Ваше объявление {number} опубликовано на сайте!",
        "listing_declined": "❌ Объявление {number} не прошло проверку. Администратор свяжется с вами по поводу возврата оплаты.",
        "listing_unpublished": "ℹ️ Объявление {number} снято с публикации.",

        # --- реклама
        "ad_tariff_prompt": "Выберите тариф для рекламы на сайте:",
        "ad_tariff_label": "{days} — {price} сум",
        "ad_banner_prompt": "Отправьте баннер картинкой в формате 16:9 (например 1600×900).\nВ подписи к картинке можно указать ссылку или @username — по ней будут переходить с сайта.",
        "ad_banner_invalid_ratio": "Баннер должен быть горизонтальным, в пропорции 16:9 (например 1600×900). Отправьте другую картинку.",
        "ad_banner_received": "✅ Баннер получен.",
        "ad_payment_prompt": "Сумма к оплате: {amount} сум. Выберите способ оплаты:",
        "ad_receipt_sent": "✅ Чек отправлен администратору. После проверки оплаты баннер пройдёт модерацию.",
        "ad_payment_approved": "✅ Оплата рекламы подтверждена. Баннер отправлен на модерацию.",
        "ad_payment_rejected": "❌ Чек за рекламу не принят. Нажмите кнопку ниже, чтобы оплатить снова.",
        "ad_retry_payment": "Оплатить снова",
        "ad_content_approved": "🎉 Ваш баннер опубликован на сайте до {until}.",
        "ad_content_rejected": "❌ Баннер не прошёл модерацию. Администратор свяжется с вами по поводу возврата оплаты.",
        "ad_crypto_invoice": "💎 Счёт Crypto Pay на {amount:.2f} USDT создан. Оплатите и нажмите «Проверить оплату».",

        # --- рефералы
        "referral_info": (
            "🎁 Скидки до −30% за друзей\n\n"
            "Пригласите друга, который хочет сдать или продать недвижимость. "
            "Когда он опубликует объявление, вы получите скидку на комиссию за ваше следующее объявление:\n"
            "• 1 друг — −10%\n• 2 друга — −20%\n• 3 друга — −30%\n\n"
            "Засчитываются только друзья, которые перешли по вашей ссылке и опубликовали объявление. "
            "Скидка действует на одно объявление, после этого друзья, за которых она дана, сгорают.\n\n"
            "Ваша ссылка:\n{link}\n\n"
            "Приглашено: {invited}\nОпубликовали объявление: {qualified}\n"
            "Доступная скидка сейчас: −{discount}%"
        ),
        "referral_share_btn": "📤 Поделиться ссылкой",
        "referral_share_text": "Сдаёшь или продаёшь недвижимость? Размести объявление через этого бота:",
        "referral_qualified": "🎉 Ваш друг опубликовал объявление! Ваша скидка на следующее объявление: −{discount}%.",
    },
    "uz": {
        "menu_list": "📝 E'lon berish",
        "menu_search": "🔍 Ko'chmas mulk qidirish",
        "menu_ad": "📢 Reklama",
        "menu_referral": "🎁 Chegirmalar -20%",
        "menu_language": "🇷🇺 Русский язык",
        "menu_support": "⚙️ Qo'llab-quvvatlash",
        "menu_fee": "💰 Tariflar",
        "main_title": "🏠 Asosiy menyu. Kerakli amalni tanlang:",
        "home": "🏠 Asosiy menyu",
        "back": "◀️ Orqaga",
        "continue": "▶️ Davom etish",
        "restart": "🔄 Qaytadan boshlash",
        "skip": "⏭ O'tkazib yuborish",
        "language_prompt": LANGUAGE_PROMPT,
        "language_saved": "✅ Bot tili o'zbek tiliga o'zgartirildi.",
        "error_generic": "⚠️ Nimadir xato ketdi. Qaytadan urinib ko'ring yoki /start ni bosing.",

        "city_prompt": "Shaharni tanlang:",
        "district_prompt": "{city} shahrida tumanni tanlang:",
        "custom_district_prompt": "Tuman nomini qo'lda kiriting:",
        "other_district": "Boshqa tuman",
        "microdistrict_prompt": "Dahani / massivni tanlang:",
        "custom_microdistrict_prompt": "Daha / massiv nomini qo'lda kiriting:",
        "other_microdistrict": "Boshqa daha",
        "property_prompt": "Ko'chmas mulk turini tanlang:",
        "property_apartment": "🏢 Kvartira",
        "property_house": "🏡 Hovli / Uchastka",
        "property_office": "💼 Ofis",
        "property_shop": "🏬 Do'kon / Joy",
        "property_warehouse": "🏭 Ombor / Ishlab chiqarish",
        "deal_prompt": "Bitim turini tanlang:",
        "deal_rent": "🔑 Ijara",
        "deal_sale": "💰 Sotish",
        "area_prompt": "Maydonni kiriting (m² da):",
        "rooms_prompt": "Nechta xona?",
        "rooms_5plus": "5+",
        "floor_prompt": "Qavatni quyidagi tugma orqali tanlang yoki raqam bilan yozing:",
        "floor_label": "Qavat",
        "floor_page": "Qavatni tanlang ({start}-{end}):",
        "price_prompt_rent": "Oylik ijara narxini kiriting (so'mda).\nEng kam ijara narxi — 1 000 000 so'm.",
        "price_prompt_sale": "Sotish narxini so'mda yoki dollarda kiriting (masalan: 70000$).\nObyektning eng kam narxi — 5 000 $.",
        "min_rent_price": "❗ Joylashtirish uchun eng kam ijara narxi — 1 000 000 so'm. Boshqa narx kiriting.",
        "min_sale_price": "❗ Joylashtirish uchun obyektning eng kam narxi — 5 000 $ (joriy kurs bo'yicha ≈ {min_uzs} so'm). Boshqa narx kiriting.",
        "description_prompt": "Obyekt haqida qisqacha yozing (ta'mir, mebel, yaqin atrofda nima bor va h.k.) — 800 belgigacha.\nYoki «O'tkazib yuborish»ni bosing.",
        "description_too_long": "Tavsif juda uzun ({length} belgi). 800 belgigacha qisqartiring.",
        "phone_prompt": "Aloqa uchun telefon raqamingizni kiriting:",
        "share_phone": "📱 Kontaktni ulashish",
        "manual_phone": "⌨️ Qo'lda kiritish",
        "manual_phone_prompt": "Telefon raqamini yozing, masalan: +998 90 123 45 67",
        "photos_prompt": "Obyekt rasmlarini yuboring (1 tadan 10 tagacha). Tugatgach «Tayyor»ni bosing.",
        "photos_done": "✅ Tayyor (saqlash)",
        "photos_required": "Iltimos, kamida bitta rasm yuboring!",
        "photo_added": "Rasm qo'shildi! Jami: {count} / 10. Yana yuborishingiz yoki «Tayyor»ni bosishingiz mumkin.",
        "photo_limit": "10 tadan ortiq rasm yuklab bo'lmaydi. «Tayyor»ni bosing.",

        "listing_saved": "🎉 E'lon ma'lumotlari saqlandi!",
        "order_no": "Buyurtma №{number}",
        "lbl_city": "Shahar",
        "lbl_district": "Tuman",
        "lbl_microdistrict": "Daha",
        "lbl_property": "Turi",
        "lbl_area": "Maydon",
        "lbl_rooms": "Xonalar",
        "lbl_deal": "Bitim",
        "lbl_description": "Tavsif",
        "lbl_phone": "Telefon",
        "rent_price": "Ijara narxi",
        "sale_price": "Sotish narxi",
        "per_month": "/ oy",
        "currency": "so'm",
        "exchange_rate": "Valyuta kursi",
        "service_fee": "Xizmat haqi",
        "discount_line": "🎁 Do'stlar uchun chegirma: −{percent}%",
        "fee_to_pay": "To'lov summasi",
        "period_warning": "E'lon to'lov va tekshiruvdan so'ng saytda e'lon qilinadi.",

        "rate_error": "Valyuta kursini olishda xatolik. Keyinroq urinib ko'ring.",
        "not_found": "Ma'lumot topilmadi. Asosiy menyuga qaytish.",
        "invalid_choice": "Noto'g'ri tanlov. Iltimos, quyidagi tugmalardan foydalaning.",
        "invalid_number": "Raqam formati noto'g'ri. Qaytadan urinib ko'ring.",
        "invalid_phone": "Telefon raqami formati noto'g'ri. Qaytadan urinib ko'ring.",
        "back_unavailable": "Bu bosqichda orqaga qaytish imkonsiz.",
        "draft_found": "Sizda tugallanmagan ariza bor. Davom etasizmi yoki boshqatdan boshlaysizmi?",

        "fee_info": (
            "💰 Joylashtirish tariflari\n\n"
            "🔑 Ijara — oylik ijara narxining 1%.\n"
            "   Eng kam ijara narxi — 1 000 000 so'm.\n\n"
            "💰 Sotish — obyekt narxining 0,1%.\n"
            "   Obyektning eng kam narxi — 5 000 $.\n\n"
            "📢 Saytda reklama:\n{ad_tariffs}\n\n"
            "🎁 Do'stlaringizni taklif qiling: e'lon joylagan har bir do'st uchun −10% (−30% gacha)."
        ),

        "support_intro": "Qo'llab-quvvatlash xizmatiga xabaringizni yozing, biz tez orada bog'lanamiz:",
        "support_sent": "✅ Xabaringiz yuborildi. Tez orada javob beramiz!",
        "support_unavailable": "Xabarni yuborib bo'lmadi. Keyinroq urinib ko'ring.",

        "search_city_prompt": "🔍 Ko'chmas mulk qidirish uchun shaharni tanlang:",
        "search_deal_prompt": "🔑 Bitim turini tanlang:",
        "search_site_info": (
            "🏡 Ajoyib tanlov! {city} shahridagi barcha dolzarb {deal} e'lonlari "
            "RENT UZBEKISTAN saytimizda jamlangan.\n\n"
            "Saytda siz:\n"
            "🔎 obyektni tuman, narx, maydon va xonalar soni bo'yicha qulay tanlashingiz;\n"
            "📸 rasmlar va batafsil tavsifni ko'rishingiz;\n"
            "📞 egasi bilan bevosita bog'lanishingiz;\n"
            "❤️ yoqqan variantlarni sevimlilarga saqlashingiz mumkin.\n\n"
            "Katalogga o'tish uchun quyidagi tugmani bosing. Aynan izlaganingizni topishingizni tilaymiz! ✨"
        ),
        "search_deal_rent": "ijara",
        "search_deal_sale": "sotuv",
        "site_button": "🏡 Saytga o'tish",
        "search_empty": "{city} shahrida so'rovingiz bo'yicha hozircha hech narsa topilmadi.",
        "search_found": "🔍 Topilgan e'lonlar: {count}. Oxirgilari:",
        "search_more_site": "Barcha e'lonlar rasm va filtrlar bilan — saytda: {url}",

        "payment_method_prompt": "To'lov usulini tanlang:",
        "payment_summary": "💳 {number} joylashtirish uchun to'lov\n\n{lines}\n\nTo'lov usulini tanlang:",
        "pay_card_text": "💳 {method} orqali to'lov\n\nQabul qiluvchi: {recipient}\nKarta raqami: {card}\nSumma: {amount} so'm",
        "receipt_prompt": "To'lovdan so'ng chek rasmini yoki PDF faylini shu yerga yuboring. To'lov administrator tomonidan qo'lda tekshiriladi.",
        "receipt_sent": "✅ Chek administratorga yuborildi. Tekshiruvni kuting. Skrinshotning o'zi to'lov tasdiqlanganini anglatmaydi.",
        "receipt_pdf_only": "Faqat chek rasmi yoki PDF fayl qabul qilinadi.",
        "crypto_creating": "⏳ Crypto Pay hisobi yaratilmoqda…",
        "crypto_min": "Crypto Pay orqali to'lash uchun summa juda kichik. Boshqa usulni tanlang.",
        "crypto_create_failed": "Crypto Pay hisobini yaratib bo'lmadi. Keyinroq urinib ko'ring yoki boshqa usulni tanlang.",
        "crypto_invoice": "💎 Crypto Pay hisobi yaratildi.\n\nBuyurtma: {number}\nSumma: {amount:.2f} USDT\n\nHisobni to'lang, so'ng «To'lovni tekshirish» tugmasini bosing. Hisob 1 soat amal qiladi.",
        "crypto_pay_btn": "USDT da to'lash",
        "crypto_check_btn": "To'lovni tekshirish",
        "crypto_wait": "To'lovni tekshirish uchun Crypto Pay hisobi ostidagi «To'lovni tekshirish» tugmasini bosing.",
        "payment_approved": "✅ To'lov tasdiqlandi!",
        "payment_rejected": "❌ Chek administrator tomonidan qabul qilinmadi. Qayta to'lash uchun «📝 E'lon berish» → «Davom etish»ni bosing yoki qo'llab-quvvatlashga yozing.",
        "payment_already_confirmed": "To'lov allaqachon tasdiqlangan.",
        "payment_check_error": "To'lovni tekshirib bo'lmadi. Bir daqiqadan so'ng urinib ko'ring.",
        "payment_pending": "To'lov hali tushmadi.",
        "invoice_expired": "Hisobning amal qilish muddati tugadi. To'lov usulini qaytadan tanlang.",
        "invoice_not_found": "Hisob topilmadi.",
        "invalid_payment_order": "Ariza topilmadi.",
        "listing_moderation": "✅ To'lov qabul qilindi! {number} e'loni tekshiruvga yuborildi — shundan so'ng u saytda paydo bo'ladi.",
        "listing_published": "🎉 {number} e'loningiz saytda e'lon qilindi!",
        "listing_declined": "❌ {number} e'loni tekshiruvdan o'tmadi. To'lovni qaytarish bo'yicha administrator siz bilan bog'lanadi.",
        "listing_unpublished": "ℹ️ {number} e'loni saytdan olib tashlandi.",

        "ad_tariff_prompt": "Saytda reklama uchun tarifni tanlang:",
        "ad_tariff_label": "{days} — {price} so'm",
        "ad_banner_prompt": "Bannerni 16:9 formatdagi rasm sifatida yuboring (masalan 1600×900).\nRasm izohida havola yoki @username ko'rsatishingiz mumkin — saytdan shu manzilga o'tiladi.",
        "ad_banner_invalid_ratio": "Banner gorizontal, 16:9 nisbatda bo'lishi kerak (masalan 1600×900). Boshqa rasm yuboring.",
        "ad_banner_received": "✅ Banner qabul qilindi.",
        "ad_payment_prompt": "To'lov summasi: {amount} so'm. To'lov usulini tanlang:",
        "ad_receipt_sent": "✅ Chek administratorga yuborildi. To'lov tekshirilgach, banner moderatsiyadan o'tadi.",
        "ad_payment_approved": "✅ Reklama uchun to'lov tasdiqlandi. Banner moderatsiyaga yuborildi.",
        "ad_payment_rejected": "❌ Reklama uchun chek qabul qilinmadi. Qayta to'lash uchun quyidagi tugmani bosing.",
        "ad_retry_payment": "Qayta to'lash",
        "ad_content_approved": "🎉 Banneringiz saytda {until} gacha joylashtirildi.",
        "ad_content_rejected": "❌ Banner moderatsiyadan o'tmadi. To'lovni qaytarish bo'yicha administrator siz bilan bog'lanadi.",
        "ad_crypto_invoice": "💎 {amount:.2f} USDT lik Crypto Pay hisobi yaratildi. To'lang va «To'lovni tekshirish»ni bosing.",

        "referral_info": (
            "🎁 Do'stlar uchun −30% gacha chegirma\n\n"
            "Ko'chmas mulkini ijaraga bermoqchi yoki sotmoqchi bo'lgan do'stingizni taklif qiling. "
            "U e'lon joylaganda, keyingi e'loningiz komissiyasiga chegirma olasiz:\n"
            "• 1 do'st — −10%\n• 2 do'st — −20%\n• 3 do'st — −30%\n\n"
            "Faqat havolangiz orqali kelib, e'lon joylagan do'stlar hisobga olinadi. "
            "Chegirma bitta e'longa amal qiladi, shundan so'ng hisobga olingan do'stlar kuyadi.\n\n"
            "Sizning havolangiz:\n{link}\n\n"
            "Taklif qilinganlar: {invited}\nE'lon joylaganlar: {qualified}\n"
            "Hozirgi chegirma: −{discount}%"
        ),
        "referral_share_btn": "📤 Havolani ulashish",
        "referral_share_text": "Ko'chmas mulk ijaraga berasizmi yoki sotasizmi? Shu bot orqali e'lon joylang:",
        "referral_qualified": "🎉 Do'stingiz e'lon joyladi! Keyingi e'loningiz uchun chegirma: −{discount}%.",
    },
}


def normalize_language(language: str | None) -> str:
    return language if language in TRANSLATIONS else "ru"


def tr(language: str | None, key: str, **kwargs) -> str:
    lang_dict = TRANSLATIONS.get(normalize_language(language))
    text = lang_dict.get(key) or TRANSLATIONS["ru"].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return text
    return text


def all_variants(key: str) -> list[str]:
    return sorted({d[key] for d in TRANSLATIONS.values() if key in d})
