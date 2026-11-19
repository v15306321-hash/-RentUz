/* ===== Язык сайта: русский / узбекский =====
   Язык выбирается кнопкой RU | UZ в шапке, запоминается в браузере, можно открыть ссылкой ?lang=uz */
(function(){
  const q=new URLSearchParams(location.search).get('lang');
  let saved=null;try{saved=localStorage.getItem('lang')}catch(_){}
  window.LANG=(q==='uz'||q==='ru')?q:(saved==='uz'?'uz':'ru');
  try{if(q==='uz'||q==='ru')localStorage.setItem('lang',q)}catch(_){}
  document.documentElement.lang=window.LANG==='uz'?'uz':'ru';
})();

const I18N={
ru:{
  page_title:'RENT UZBEKISTAN — аренда и продажа недвижимости',
  page_desc:'RENT UZBEKISTAN — квартиры, дома, офисы, магазины и склады в аренду и на продажу в городах Узбекистана.',
  nav_aria:'Основное меню',nav_dir:'Направления',nav_cat:'Каталог',nav_owner:'Выставить объект',nav_contacts:'Контакты',nav_contact_btn:'Связаться',
  city_aria:'Выберите город',menu_aria:'Меню',lang_aria:'Язык сайта',
  hero_title:'Аренда и продажа<br>квартир, домов<br>и помещений',
  hero_text:'Квартиры, дома, офисы и магазины <span class="cl"></span> — объявления от владельцев с фотографиями, ценами и прямыми контактами.',
  hero_btn_list:'Разместить объявление',hero_btn_cat:'Смотреть каталог',hero_alt:'Городской пейзаж',
  dir_title:'Четыре направления',dir_text:'Жильё для семьи или помещение для дела — выберите, что ищете, и посмотрите подходящие объекты.',
  cat_title:'Каталог объектов',cat_text:'Нажмите на объект, чтобы открыть страницу с фотографиями, описанием и контактами владельца.',
  flt_aria:'Поиск объектов',flt_toggle:'Фильтры',f_search:'Поиск',f_search_ph:'Название или описание',f_dist:'Район',f_pmin:'Цена от, сум',f_pmax:'Цена до, сум',
  f_amin:'Площадь от, м²',f_amax:'Площадь до, м²',f_rooms:'Комнаты',f_any_rooms:'Любые',f_rooms4:'4 и больше',f_status:'Статус',f_any:'Любой',
  f_sort:'Сортировка',f_sort_def:'По умолчанию',f_sort_p:'Сначала дешевле',f_sort_d:'Сначала дороже',f_sort_a:'Сначала просторнее',f_fav:'Избранное',f_reset:'Сбросить',
  all_districts:'Все районы',found:'Найдено: {n}',
  cat_note:'Список обновляется каждый день. Не нашли подходящее — загляните позже или напишите нам в Telegram.',
  no_match:'По этим фильтрам объектов нет. Измените условия поиска.',
  empty_title:'{city}: объявлений пока нет',
  empty_text:'Каталог только запускается — первые объекты появятся совсем скоро. Сдаёте или продаёте недвижимость? Разместите объявление через нашего бота, и его первыми увидят клиенты.',
  empty_btn:'Разместить объявление',
  ad_aria:'Рекламный блок RENT UZBEKISTAN',ad_alt:'Рекламный баннер',ad_title:'Здесь могла быть ваша реклама',ad_link:'выставить свою рекламу сюда',ad_tag:'Реклама',
  own_title:'Выставить свою недвижимость',
  own_text:'Хотите сдать или продать квартиру, дом, офис или склад <span class="cl"></span>? Заполните анкету в нашем Telegram-боте — он автоматически соберёт информацию об объекте. Не нужно ждать ответа менеджера.',
  own_card_title:'Добавьте объект через автоматизированного бота',own_card_text:'Бот последовательно запросит необходимые параметры недвижимости и передаст заявку на обработку.',
  own_btn:'Перейти в Telegram-бот',own_hint:'Откроется Telegram. Нажмите «Запустить» и следуйте инструкциям бота.',
  st1_t:'1. Перейдите в бота',st1_d:'Откройте @Arenda_UZB_bot в Telegram и нажмите «Запустить».',
  st2_t:'2. Заполните анкету',st2_d:'Укажите город и район, параметры недвижимости, стоимость, телефон и загрузите фотографии.',
  st3_t:'3. Оплатите размещение',st3_d:'Бот рассчитает комиссию и предложит удобный способ оплаты.',
  st3_promo:'🎁 Первое объявление — бесплатно до {date}',
  st4_t:'4. Автоматическая публикация',st4_d:'После проверки объявление появится на сайте и в Telegram-канале вашего города.',
  safe_title:'Важная информация',safe_text:'Пожалуйста, ознакомьтесь с рекомендациями по безопасности до того, как договариваться о сделке.',
  safe_note:'<b>В целях безопасности</b> сообщаем: сайт носит информационный характер, не имеет отношения к продавцам и арендодателям и не является стороной сделок между ними и клиентами.',
  safe1_t:'Проверяйте документы',safe1_d:'Перед покупкой или арендой обязательно сверьте полный перечень документов на объект.',
  safe2_t:'Не вносите деньги заранее',safe2_d:'Не передавайте денежные средства до личной встречи с владельцем или получения ключей от арендуемого объекта.',
  foot_title:'Остались вопросы?',foot_text:'Напишите нам в Telegram — подскажем, как разместить объявление или найти подходящий объект.',
  foot_btn:'Написать в Telegram',foot_safety:'Безопасность',country:'УЗБЕКИСТАН',
  view_objects:'Смотреть объекты ({n})',all:'Все',
  st_free:'Свободно',st_rented:'Занято',sum:'сум',unit_month:'мес',unit_day:'сутки',term_daily:'Посуточно',term_month:'На месяц',term_sale:'Продажа',
  tab_daily:'Посуточно',tab_month:'На месяц',tab_sale:'Приобрести',
  photos_n:'{n} фото',call:'Позвонить',rooms_n:'{n} комн.',floor_n:'{n} этаж',m2:'м²',
  see_photos:'Смотреть фото: {t}',add_fav:'Добавить в избранное: {t}',
  back_catalog:'← Назад к каталогу',carousel:'карусель',photos_of:'Фотографии: {t}',photo_n:'{t} — фото {n}',prev_photo:'Предыдущее фото',next_photo:'Следующее фото',scroll_photos:'Листать фотографии',close:'Закрыть',
  desc:'Описание',features:'Преимущества',near:'Рядом есть',city:'Город',district:'Район',area:'Площадь',floor:'Этаж / участок',rooms:'Комнат',
  already:'Объект уже {s}. Посмотрите похожие варианты в каталоге.',owner_contacts:'Контакты владельца',owner_default:'Владелец объекта',call_owner:'Позвонить владельцу',write_tg:'Написать в Telegram',fav:'♥ Избранное',
  tg_msg:'Здравствуйте! Меня заинтересовало ваше предложение на {site}. Интересует объект «{t}» ({place}).',
  loc_me:'📍 Узнать расстояние от меня',loc_note:'Местоположение приблизительное. Точный адрес сообщит владелец.',loc_map:'Открыть на карте',
  loc_near:'Совсем рядом с вами',loc_km:'В {n} км от вас',loc_fail:'Не удалось определить ваше местоположение',loc_wait:'Определяем…',
  t_apartment:'Квартира',t_apartment_n:'{n}-комнатная квартира',t_house:'Дом / участок',t_house_n:'Дом, {n} комн.',t_office:'Офис',t_shop:'Магазин / помещение',t_warehouse:'Склад / производство',t_object:'Объект'
},
uz:{
  page_title:'RENT UZBEKISTAN — ko‘chmas mulk ijarasi va savdosi',
  page_desc:'RENT UZBEKISTAN — O‘zbekiston shaharlarida kvartiralar, hovlilar, ofislar, do‘konlar va omborlar ijarasi va savdosi.',
  nav_aria:'Asosiy menyu',nav_dir:'Yo‘nalishlar',nav_cat:'Katalog',nav_owner:'E’lon joylash',nav_contacts:'Aloqa',nav_contact_btn:'Bog‘lanish',
  city_aria:'Shaharni tanlang',menu_aria:'Menyu',lang_aria:'Sayt tili',
  hero_title:'Kvartira, hovli<br>va binolar<br>ijarasi va savdosi',
  hero_text:'<span class="cl"></span> kvartiralar, hovlilar, ofislar va do‘konlar — egalaridan rasmlar, narxlar va to‘g‘ridan-to‘g‘ri aloqa bilan e’lonlar.',
  hero_btn_list:'E’lon joylash',hero_btn_cat:'Katalogni ko‘rish',hero_alt:'Shahar manzarasi',
  dir_title:'To‘rt yo‘nalish',dir_text:'Oila uchun uy yoki biznes uchun joy — nima izlayotganingizni tanlang va mos obyektlarni ko‘ring.',
  cat_title:'Obyektlar katalogi',cat_text:'Rasmlar, tavsif va egasining kontaktlarini ko‘rish uchun obyektni bosing.',
  flt_aria:'Obyektlarni qidirish',flt_toggle:'Filtrlar',f_search:'Qidiruv',f_search_ph:'Nomi yoki tavsifi',f_dist:'Tuman',f_pmin:'Narx (dan), so‘m',f_pmax:'Narx (gacha), so‘m',
  f_amin:'Maydon (dan), m²',f_amax:'Maydon (gacha), m²',f_rooms:'Xonalar',f_any_rooms:'Har qanday',f_rooms4:'4 va undan ko‘p',f_status:'Holati',f_any:'Har qanday',
  f_sort:'Saralash',f_sort_def:'Standart',f_sort_p:'Avval arzonlari',f_sort_d:'Avval qimmatlari',f_sort_a:'Avval kengroqlari',f_fav:'Sevimlilar',f_reset:'Tozalash',
  all_districts:'Barcha tumanlar',found:'Topildi: {n}',
  cat_note:'Ro‘yxat har kuni yangilanadi. Mosini topmadingizmi — keyinroq qarang yoki bizga Telegram orqali yozing.',
  no_match:'Bu filtrlar bo‘yicha obyektlar yo‘q. Qidiruv shartlarini o‘zgartiring.',
  empty_title:'{city}: hozircha e’lonlar yo‘q',
  empty_text:'Katalog endigina ishga tushmoqda — birinchi obyektlar tez orada paydo bo‘ladi. Ko‘chmas mulkni ijaraga berasizmi yoki sotasizmi? Botimiz orqali e’lon joylang — uni mijozlar birinchi bo‘lib ko‘radi.',
  empty_btn:'E’lon joylash',
  ad_aria:'RENT UZBEKISTAN reklama bloki',ad_alt:'Reklama banneri',ad_title:'Bu yerda sizning reklamangiz bo‘lishi mumkin',ad_link:'reklamangizni shu yerga joylang',ad_tag:'Reklama',
  own_title:'Ko‘chmas mulkingizni joylang',
  own_text:'<span class="cl"></span> kvartira, hovli, ofis yoki omborni ijaraga bermoqchi yoki sotmoqchimisiz? Telegram-botimizdagi anketani to‘ldiring — u obyekt haqidagi ma’lumotlarni avtomatik yig‘adi. Menejer javobini kutish shart emas.',
  own_card_title:'Obyektni avtomatlashtirilgan bot orqali qo‘shing',own_card_text:'Bot ko‘chmas mulkning kerakli parametrlarini ketma-ket so‘raydi va arizani ko‘rib chiqishga yuboradi.',
  own_btn:'Telegram-botga o‘tish',own_hint:'Telegram ochiladi. «Start» tugmasini bosing va bot ko‘rsatmalariga amal qiling.',
  st1_t:'1. Botga o‘ting',st1_d:'Telegram’da @Arenda_UZB_bot ni oching va «Start» tugmasini bosing.',
  st2_t:'2. Anketani to‘ldiring',st2_d:'Shahar va tumanni, obyekt parametrlarini, narxini, telefoningizni kiriting va rasmlarni yuklang.',
  st3_t:'3. Joylashtirish uchun to‘lang',st3_d:'Bot komissiyani hisoblaydi va qulay to‘lov usulini taklif qiladi.',
  st3_promo:'🎁 Birinchi e’lon — {date} gacha bepul',
  st4_t:'4. Avtomatik e’lon qilish',st4_d:'Tekshiruvdan so‘ng e’lon saytda va shahringiz Telegram-kanalida paydo bo‘ladi.',
  safe_title:'Muhim ma’lumot',safe_text:'Iltimos, bitim haqida kelishishdan oldin xavfsizlik bo‘yicha tavsiyalar bilan tanishib chiqing.',
  safe_note:'<b>Xavfsizlik maqsadida</b> ma’lum qilamiz: sayt axborot xarakteriga ega, sotuvchilar va ijaraga beruvchilarga aloqasi yo‘q va ular bilan mijozlar o‘rtasidagi bitimlar tarafi hisoblanmaydi.',
  safe1_t:'Hujjatlarni tekshiring',safe1_d:'Sotib olish yoki ijaraga olishdan oldin obyekt hujjatlarining to‘liq ro‘yxatini albatta tekshiring.',
  safe2_t:'Oldindan pul bermang',safe2_d:'Egasi bilan shaxsan uchrashmaguncha yoki ijaraga olinadigan obyekt kalitlarini olmaguncha pul bermang.',
  foot_title:'Savollaringiz bormi?',foot_text:'Bizga Telegram’da yozing — e’lon joylash yoki mos obyektni topishda yordam beramiz.',
  foot_btn:'Telegram’da yozish',foot_safety:'Xavfsizlik',country:'O‘ZBEKISTON',
  view_objects:'Obyektlarni ko‘rish ({n})',all:'Barchasi',
  st_free:'Bo‘sh',st_rented:'Band',sum:'so‘m',unit_month:'oy',unit_day:'sutka',term_daily:'Kunlik',term_month:'Oylik',term_sale:'Sotuv',
  tab_daily:'Kunlik',tab_month:'Oylik',tab_sale:'Sotib olish',
  photos_n:'{n} ta rasm',call:'Qo‘ng‘iroq',rooms_n:'{n} xona',floor_n:'{n}-qavat',m2:'m²',
  see_photos:'Rasmlarni ko‘rish: {t}',add_fav:'Sevimlilarga qo‘shish: {t}',
  back_catalog:'← Katalogga qaytish',carousel:'karusel',photos_of:'Rasmlar: {t}',photo_n:'{t} — {n}-rasm',prev_photo:'Oldingi rasm',next_photo:'Keyingi rasm',scroll_photos:'Rasmlarni varaqlash',close:'Yopish',
  desc:'Tavsif',features:'Afzalliklari',near:'Yaqin atrofda',city:'Shahar',district:'Tuman',area:'Maydon',floor:'Qavat / uchastka',rooms:'Xonalar',
  already:'Obyekt allaqachon {s}. Katalogdagi o‘xshash variantlarni ko‘ring.',owner_contacts:'Egasining kontaktlari',owner_default:'Obyekt egasi',call_owner:'Egasiga qo‘ng‘iroq qilish',write_tg:'Telegram’da yozish',fav:'♥ Sevimlilar',
  tg_msg:'Assalomu alaykum! {site} saytidagi taklifingiz meni qiziqtirdi. «{t}» obyekti ({place}) bo‘yicha yozyapman.',
  loc_me:'📍 Mendan qancha uzoqda?',loc_note:'Joylashuv taxminiy. Aniq manzilni egasi aytadi.',loc_map:'Xaritada ochish',
  loc_near:'Sizga juda yaqin',loc_km:'Sizdan {n} km uzoqlikda',loc_fail:'Joylashuvingizni aniqlab bo‘lmadi',loc_wait:'Aniqlanmoqda…',
  t_apartment:'Kvartira',t_apartment_n:'{n} xonali kvartira',t_house:'Hovli / uchastka',t_house_n:'Hovli, {n} xona',t_office:'Ofis',t_shop:'Do‘kon / joy',t_warehouse:'Ombor / ishlab chiqarish',t_object:'Obyekt'
}};

/* Названия городов, областей, «в городе», категорий и «рядом есть» на узбекском */
const I18N_CITY_UZ={'Алмалык':'Olmaliq','Ташкент':'Toshkent','Самарканд':'Samarqand','Андижан':'Andijon','Наманган':'Namangan','Нукус':'Nukus','Фергана':'Farg‘ona','Карши':'Qarshi','Бухара':'Buxoro','Коканд':'Qo‘qon'};
const I18N_REGION_UZ={'Ташкентская область':'Toshkent viloyati','город Ташкент':'Toshkent shahri','Самаркандская область':'Samarqand viloyati','Андижанская область':'Andijon viloyati','Наманганская область':'Namangan viloyati','Республика Каракалпакстан':'Qoraqalpog‘iston Respublikasi','Ферганская область':'Farg‘ona viloyati','Кашкадарьинская область':'Qashqadaryo viloyati','Бухарская область':'Buxoro viloyati'};
const I18N_CAT_UZ={
  flat:{t:'Kvartiralar',d:'Yangi binolardagi studiyalar va kvartiralar — kunlik va uzoq muddatga.',s:['Studiya va 1–3 xonali','Mebelli va mebelsiz','Kunlik va uzoq muddatga']},
  house:{t:'Hovli va dachalar',d:'Oila yoki dam olish uchun hovlili xususiy uylar va dachalar.',s:['Uchastkali uylar','Bog‘li dachalar','Mavsumiy va yil bo‘yi']},
  office:{t:'Ofislar',d:'Biznes-markazlar va yangi binolardagi kabinetlar va open space.',s:['20 m² dan','Open space','Avtoturargohli']},
  shop:{t:'Do‘kon va omborlar',d:'Birinchi qatordagi savdo joylari, kafe va omborlar uchun.',s:['Birinchi qator','Kafe va xizmatlar uchun','Pandusli omborlar']}};
const I18N_NEAR_UZ={flat:['Maktab','Bolalar bog‘chasi','Shifoxona','Do‘kon','Bozor'],house:['Maktab','Bolalar bog‘chasi','Shifoxona','Do‘kon','Bozor'],office:['Bank va kafelar','Jamoat transporti bekati','Avtoturargoh','Do‘konlar','Biznes-markazlar'],shop:['Odamlar oqimi yuqori','Jamoat transporti bekati','Avtoturargoh','Bozor','Yaqinda bank']};

function t(key,vars){const d=I18N[window.LANG]||I18N.ru;let s=d[key]??I18N.ru[key]??key;if(vars)for(const k in vars)s=s.split('{'+k+'}').join(vars[k]);return s}
const cityName=c=>window.LANG==='uz'?(I18N_CITY_UZ[c]||c):c;
const regionName=r=>window.LANG==='uz'?(I18N_REGION_UZ[r]||r):r;
const cityIn=c=>window.LANG==='uz'?`${cityName(c)}da`:null; /* «в Алмалыке» на узбекском: «Olmaliqda» */

/* Перевод статичного текста страницы: data-i18n (текст), data-i18n-html (с разметкой), data-i18n-ph (placeholder), data-i18n-aria (aria-label), data-i18n-alt */
function applyI18n(root){
  root=root||document;
  root.querySelectorAll('[data-i18n]').forEach(el=>{el.textContent=t(el.dataset.i18n)});
  root.querySelectorAll('[data-i18n-html]').forEach(el=>{el.innerHTML=t(el.dataset.i18nHtml)});
  root.querySelectorAll('[data-i18n-ph]').forEach(el=>{el.placeholder=t(el.dataset.i18nPh)});
  root.querySelectorAll('[data-i18n-aria]').forEach(el=>{el.setAttribute('aria-label',t(el.dataset.i18nAria))});
  root.querySelectorAll('[data-i18n-alt]').forEach(el=>{el.alt=t(el.dataset.i18nAlt)});
  document.title=t('page_title');
  const md=document.querySelector('meta[name=description]');if(md)md.content=t('page_desc');
  document.querySelectorAll('.lng button').forEach(b=>{const on=b.dataset.lang===window.LANG;b.classList.toggle('on',on);b.setAttribute('aria-pressed',String(on))});
}
function setLang(l){
  if(l===window.LANG)return;
  try{localStorage.setItem('lang',l)}catch(_){}
  const u=new URL(location.href);u.searchParams.delete('lang');
  location.replace(u.pathname+u.search+u.hash); /* перезагрузка — самый надёжный способ перевести всю страницу */
}
document.addEventListener('click',e=>{const b=e.target.closest('.lng button');if(b){e.preventDefault();setLang(b.dataset.lang)}});
applyI18n();
