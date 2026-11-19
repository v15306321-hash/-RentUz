const TG='https://t.me/Arenda_UZB_bot'; /* Связь с сайтом — только через бота (там есть техподдержка) */
const OWNER_BOT='https://t.me/Arenda_UZB_bot'; /* Бот для автоматического добавления недвижимости */
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const bind=r=>r.querySelectorAll('[data-tg]').forEach(a=>{a.href=TG;a.target='_blank';a.rel='noopener'});bind(document);
/* ↓ Категории: p — кадр обложки из фото */
const CAT=[
{k:'flat',t:'Квартиры',d:'Студии и квартиры в новостройках — на сутки и на длительный срок.',s:['Студии и 1–3 комнаты','С мебелью и без','Посуточно и надолго'],p:'88% 26%'},
{k:'house',t:'Дома и дачи',d:'Частные дома с двором и дачи для семьи или отдыха.',s:['Дома с участком','Дачи с садом','Сезонно и круглый год'],p:'4% 75%'},
{k:'office',t:'Офисы',d:'Кабинеты и open space в бизнес-центрах и новых зданиях.',s:['От 20 м²','Open space','С парковкой'],p:'65% 40%'},
{k:'shop',t:'Магазины и склады',d:'Торговые помещения на первой линии, под кафе и склады.',s:['Первая линия','Под кафе и услуги','Склады с пандусом'],p:'54% 100%'}];
if(window.LANG==='uz')CAT.forEach(c=>Object.assign(c,I18N_CAT_UZ[c.k]));
const T0=document.title;
const ASSET_DEFAULTS={
  home_desktop:'assets/img/7a7fc5e5.jpg',home_mobile:'assets/img/6416a0d7.jpg',
  category_flat:'assets/img/2ebe49ee.jpg',category_house:'assets/img/2bfb3551.jpg',
  category_office:'assets/img/749b4895.jpg',category_shop:'assets/img/9e927aa2.jpg',
  city_tashkent_desktop:'assets/img/city-tashkent-desktop.jpg',city_tashkent_mobile:'assets/img/city-tashkent-mobile.jpg',
  city_samarkand_desktop:'assets/img/city-samarkand-desktop.jpg',city_samarkand_mobile:'assets/img/city-samarkand-mobile.jpg',
  city_andijan_desktop:'assets/img/city-andijan-desktop.jpg',city_andijan_mobile:'assets/img/city-andijan-mobile.jpg',
  city_namangan_desktop:'assets/img/city-namangan-desktop.jpg',city_namangan_mobile:'assets/img/city-namangan-mobile.jpg',
  city_nukus_desktop:'assets/img/city-nukus-desktop.jpg',city_nukus_mobile:'assets/img/city-nukus-mobile.jpg',
  social_preview:'assets/img/2ebe49ee.jpg'
};
let SITE_ASSETS={...ASSET_DEFAULTS,...(window.RENT_SITE_ASSETS||{})};
try{SITE_ASSETS={...SITE_ASSETS,...JSON.parse(localStorage.getItem('rent_site_assets_v1')||'{}')}}catch(_){}
/* Абсолютный адрес: относительный путь внутри CSS-переменной браузер считает от папки css/ — из-за этого не грузились фото обложки и направлений. */
const absUrl=u=>{if(!u)return'';try{return new URL(u,document.baseURI).href}catch(_){return u}};
const siteAsset=k=>absUrl(SITE_ASSETS[k]||ASSET_DEFAULTS[k]||'');
function applyAdBanner(){
  const banner=$('#adBanner'),image=$('#adImage'),placeholder=$('#adPlaceholder');
  if(!banner||!image||!placeholder)return;
  const source=siteAsset('ad_image');
  if(source){
    image.src=new URL(source,document.baseURI).href;
    image.hidden=false;
    placeholder.hidden=true;
    banner.classList.add('has-image');
  }else{
    image.hidden=true;
    image.removeAttribute('src');
    placeholder.hidden=false;
    banner.classList.remove('has-image');
  }
  /* Пустой блок «Здесь могла быть ваша реклама» ведёт в бота, в раздел рекламы */
  let href=OWNER_BOT+'?start=ad';
  const configured=source?String(SITE_ASSETS.ad_link||'').trim():'';
  if(configured){
    try{
      const parsed=new URL(configured,document.baseURI);
      if(parsed.protocol==='http:'||parsed.protocol==='https:')href=parsed.href;
    }catch(_){/* Use the default Telegram contact if the configured URL is invalid. */}
  }
  banner.href=href;
  banner.target='_blank';
  banner.rel='noopener noreferrer';
}
applyAdBanner();
document.documentElement.style.setProperty('--ph',`url("${siteAsset('home_desktop')}")`);
document.documentElement.style.setProperty('--phm',`url("${siteAsset('home_mobile')}")`);
const IMG={flat:siteAsset('category_flat'),house:siteAsset('category_house'),office:siteAsset('category_office'),shop:siteAsset('category_shop')};
const HERO_CONFIG={
  'Алмалык':['city_almalyk_desktop','city_almalyk_mobile'],
  'Ташкент':['city_tashkent_desktop','city_tashkent_mobile'],
  'Самарканд':['city_samarkand_desktop','city_samarkand_mobile'],
  'Андижан':['city_andijan_desktop','city_andijan_mobile'],
  'Наманган':['city_namangan_desktop','city_namangan_mobile'],
  'Нукус':['city_nukus_desktop','city_nukus_mobile'],
  'Фергана':['city_fergana_desktop','city_fergana_mobile'],
  'Карши':['city_karshi_desktop','city_karshi_mobile'],
  'Бухара':['city_bukhara_desktop','city_bukhara_mobile'],
  'Коканд':['city_kokand_desktop','city_kokand_mobile']
};
const HERO=Object.fromEntries(Object.entries(HERO_CONFIG).map(([city,keys])=>[city,keys.map(siteAsset)]));
const API_ENABLED=window.RENT_API_ENABLED===true;
const API_BASE=String(window.RENT_API_BASE||'').replace(/\/+$/,'');
const cityHero=$('#cityHero'),cityHeroMobile=$('#cityHeroMobile'),cityHeroImage=$('#cityHeroImage');
cityHeroImage.onerror=()=>{cityHero.hidden=true};
/* ↓ Города: p — "в городе", f — коэффициент цен, d — районы/микрорайоны (замените на свои) */
const CT={'Алмалык':{p:'в Алмалыке',f:1,d:['Радуга','Ойдин','Телеграф','ГорГаз','5/1','5/2','5/3','Нижняя Терраса','67-квартал','Чехово','Гагарино','Старый базар','Космос','Шанхай','Навруз','Намуна (Депо)','Интернат','ДСК','Хим.городок']},
'Ташкент':{p:'в Ташкенте',f:1.8,d:['Юнусабад','Мирзо-Улугбек','Чиланзар','Яккасарай','Шайхантахур','Сергели','Мирабад','Яшнабад','Учтепа','Алмазар','Бектемир','Янгихаят']},
'Самарканд':{p:'в Самарканде',f:1,d:['Центр','Сиаб','Дагбит','Регистан','Университетский бульвар','Западный']},
'Андижан':{p:'в Андижане',f:.8,d:[]},
'Наманган':{p:'в Намангане',f:.8,d:[]},
'Нукус':{p:'в Нукусе',f:.7,d:[]},
'Фергана':{p:'в Фергане',f:1,d:[]},
'Карши':{p:'в Карши',f:1,d:[]},
'Бухара':{p:'в Бухаре',f:1,d:['Сайфиддин Бохарзий','Кўкалдош','Жўйбор','Дилкушо','Шергирон','Чорбоқхосса','Шайхул Олам','Турки Жанди','Гулчорбоғ','Ҳавзинав','Ширбудин','Отбозор']},
'Коканд':{p:'в Коканде',f:1,d:['Гиштли Масжид','Вакф Чорсу','Тугонбоши','Янги Чорсу','Каландархона','Ёр Бозори','Чархини Куприги','Исфара Гузари','Каймокли Гузар','Мисгарлик','Дегрезлик','Нонвойлик Гузари','Шайхон','Гишткуприк','Галчасой','Темирйули','Чорчинор','Исломабад','Кушчинор','Алишер Навои','Ок Олтин','Нурафшон','Навбахор','Истиклол','Навруз','Дустлик','Бунёдкор','Олтин Водий','Мукимий']}};
/* ↓ Контакты владельца по умолчанию; для отдельного объекта можно добавить 13-й элемент {n:'Имя',ph:'+998…',tg:'https://t.me/…'} */
const OWN={n:'Владелец объекта',ph:''};
const NEAR={flat:['Школа','Детский сад','Больница','Магазин','Рынок'],house:['Школа','Детский сад','Больница','Магазин','Рынок'],office:['Банки и кафе','Остановка транспорта','Парковка','Магазины','Бизнес-центры'],shop:['Высокая проходимость','Остановка транспорта','Парковка','Рынок','Банк рядом']};
if(window.LANG==='uz')Object.assign(NEAR,I18N_NEAR_UZ);
const SLOTS={flat:['Гостиная','Спальня','Кухня','Санузел','Балкон','Вид из окна'],house:['Гостиная','Спальня','Кухня','Санузел','Двор','Терраса'],office:['Рабочая зона','Переговорная','Кухня','Санузел','Вход','Парковка'],shop:['Торговый зал','Витрина','Подсобка','Санузел','Вход','Парковка']};
/* ===== v2: данные, поиск, избранное, статусы, галерея ===== */
const ST={free:t('st_free'),rented:t('st_rented')},stl=o=>ST[o.status]||ST.free;
/* Объявления: data/listings.js + Telegram-бот (API). Черновики из админки видны только в браузере администратора. */
const LS='arenda_listings_v1';let A=null;try{A=JSON.parse(localStorage.getItem(LS))}catch(_){}
if(!Array.isArray(A))A=window.LISTINGS||[];
/* Normalize legacy/unknown statuses: only free and rented are supported. */
let statusMigration=false;A=A.map(o=>{const status=o.status==='rented'?'rented':'free';if(status!==o.status)statusMigration=true;return status===o.status?o:{...o,status}});
if(statusMigration){try{localStorage.setItem(LS,JSON.stringify(A))}catch(_){}}
let FAV=[];try{FAV=JSON.parse(localStorage.getItem('fav'))||[]}catch(_){}
const saveFav=()=>{try{localStorage.setItem('fav',JSON.stringify(FAV))}catch(_){}};
const fmt=n=>Number(n||0).toLocaleString('ru-RU'),cat=k=>CAT.find(c=>c.k===k),tel=p=>p?'tel:'+String(p).replace(/[^+\d]/g,''):'';
/* Перевод полей объявления для показа: тип сделки, единица цены, этаж, название объявлений из бота */
const TERM_KEY={'Посуточно':'term_daily','На месяц':'term_month','Продажа':'term_sale'},UNIT_KEY={'мес':'unit_month','сутки':'unit_day'};
const termOf=o=>TERM_KEY[o.term]?t(TERM_KEY[o.term]):o.term;
const unitOf=o=>o.unit?(UNIT_KEY[o.unit]?t(UNIT_KEY[o.unit]):o.unit):'';
const priceUnit=o=>`${t('sum')}${unitOf(o)?' / '+unitOf(o):''}`;
const floorOf=o=>o.floor_num!=null&&o.floor_num!==''?t('floor_n',{n:o.floor_num}):(o.floor||'—');
const titleOf=o=>{if(o.source!=='telegram_bot'||!o.kind)return o.title;const n=+o.rooms||0;
  if(o.kind==='apartment')return n?t('t_apartment_n',{n}):t('t_apartment');if(o.kind==='house')return n?t('t_house_n',{n}):t('t_house');
  return t('t_'+o.kind)||o.title};
const F0=()=>({q:'',dist:'',pmin:'',pmax:'',amin:'',amax:'',rooms:'',st:'',sort:'',fav:false});
let city='Алмалык',cur='all',dl='',sy=null,F=F0();
const drawDirs=()=>{$('#dirs').innerHTML=CAT.map(c=>{const n=A.filter(x=>x.cat===c.k&&x.city===city).length;return`<div class="dc" data-go="${c.k}" tabindex="0" role="button" style="--im:url(${IMG[c.k]})"><h3>${c.t}</h3><p>${c.d}</p><ul>${c.s.map(x=>`<li>${x}</li>`).join('')}</ul><span>${t('view_objects',{n})}</span></div>`}).join('')};
const DL=['Посуточно','На месяц','Приобрести'],DLK={'Посуточно':'tab_daily','На месяц':'tab_month','Приобрести':'tab_sale'},DM={'Посуточно':'Посуточно','На месяц':'На месяц','Приобрести':'Продажа'};
const rows=()=>{const q=F.q.trim().toLowerCase();return A.filter(o=>o.city===city&&(cur==='all'||o.cat===cur)&&(!dl||o.term===DM[dl])&&(!F.dist||o.district===F.dist)&&(!F.pmin||o.price>=+F.pmin)&&(!F.pmax||o.price<=+F.pmax)&&(!F.amin||o.area>=+F.amin)&&(!F.amax||o.area<=+F.amax)&&(!F.rooms||(F.rooms==='4'?o.rooms>=4:o.rooms===+F.rooms))&&(!F.st||o.status===F.st)&&(!F.fav||FAV.includes(o.id))&&(!q||`${o.title} ${titleOf(o)} ${o.district} ${o.desc}`.toLowerCase().includes(q)))};
const card=o=>{const f=FAV.includes(o.id),s=o.status||'free';return`<article class="lc s-${s}" data-i="${o.id}"><div class="pw"><button type="button" class="ph" data-g="${o.id}" aria-label="${t('see_photos',{t:titleOf(o)})}" style="background-image:url('${o.photos[0]||IMG[o.cat]}')"></button><span class="bd st-${s}">${stl(o)}</span><span class="cn2">${t('photos_n',{n:o.photos.length||1})}</span><button type="button" class="hr${f?' on':''}" data-f="${o.id}" aria-label="${t('add_fav',{t:titleOf(o)})}">♥</button></div><div class="cb"><div class="ch"><em>${cat(o.cat).t}</em><em>${termOf(o)}</em></div><h3>${titleOf(o)}</h3><div class="dd">${o.district}</div><div class="pc">${fmt(o.price)} <small>${priceUnit(o)}</small></div><div class="sp"><span>${o.area} ${t('m2')}</span><span>${o.rooms?t('rooms_n',{n:o.rooms}):floorOf(o)}</span></div>${s==='rented'||!o.phone?'':`<a class="cl2" href="${tel(o.phone)}">${t('call')}</a>`}</div></article>`};
function draw(){$('#dtabs').innerHTML=DL.map(d=>`<button data-d="${d}" class="${d===dl?'on':''}">${t(DLK[d])}</button>`).join('');$('#tabs').innerHTML=[['all',t('all')],...CAT.map(c=>[c.k,c.t])].map(([k,t])=>`<button data-k="${k}" class="${k===cur?'on':''}">${t}</button>`).join('');
const r=rows(),s=F.sort;if(s)r.sort((a,b)=>s==='p'?a.price-b.price:s==='d'?b.price-a.price:b.area-a.area);
$('#fn').textContent=FAV.length;$('#fv').classList.toggle('on',F.fav);$('#fc').textContent=t('found',{n:r.length});updFltCount();
$('#gal').innerHTML=r.map(card).join('')||(A.some(o=>o.city===city)?`<p class="note">${t('no_match')}</p>`:`<div class="empty"><b>${t('empty_title',{city:cityName(city)})}</b><p>${t('empty_text')}</p><a class="btn" href="${OWNER_BOT}?start=list" target="_blank" rel="noopener">${t('empty_btn')}</a></div>`)}
const sel=k=>{cur=k;draw()};
const fillDist=()=>{const available=[...new Set([...CT[city].d,...A.filter(x=>x.city===city).map(x=>x.district).filter(Boolean)])];$('#flt [name=dist]').innerHTML=`<option value="">${t('all_districts')}</option>`+available.map(x=>`<option>${x}</option>`).join('');F.dist=''};
$('#flt').oninput=e=>{if(e.target.name){F[e.target.name]=e.target.value;draw()}};
$('#flt').onsubmit=e=>e.preventDefault();
$('#flt').onreset=()=>setTimeout(()=>{F=F0();draw()});
$('#fv').onclick=()=>{F.fav=!F.fav;draw()};
/* Фильтры на телефоне спрятаны под кнопку «Фильтры» (на компьютере всегда открыты) */
const fltT=$('#fltToggle'),fltF=$('#flt');
if(fltT)fltT.onclick=()=>{const o=!fltF.classList.contains('open');fltF.classList.toggle('open',o);fltT.setAttribute('aria-expanded',String(o))};
function updFltCount(){const b=$('#fltN');if(!b)return;const n=['q','dist','pmin','pmax','amin','amax','rooms','st','sort'].filter(k=>F[k]).length+(F.fav?1:0);b.hidden=!n;b.textContent=n}
/* Акция в блоке «Выставить свою недвижимость»: дата из js/config.js, после окончания строка скрывается сама */
(()=>{const el=$('#promoLine'),v=window.RENT_PROMO_UNTIL;if(!el||!v)return;const d=new Date(v+'T23:59:59+05:00');if(isNaN(d)||d<new Date())return;
  const m=window.LANG==='uz'?['yanvar','fevral','mart','aprel','may','iyun','iyul','avgust','sentabr','oktabr','noyabr','dekabr']:['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря'];
  const day=+v.slice(8,10),mon=m[+v.slice(5,7)-1];el.textContent=t('st3_promo',{date:window.LANG==='uz'?`${day}-${mon}`:`${day} ${mon}`});el.hidden=false})();
/* галерея */
const lb=document.createElement('dialog');lb.id='lb';lb.innerHTML=`<button class="x" aria-label="${t('close')}">×</button><button class="pv" aria-label="${t('prev_photo')}">‹</button><img alt=""><button class="nx" aria-label="${t('next_photo')}">›</button><p></p>`;document.body.append(lb);
let gp=[],gi=0,tx=0;const show=()=>{lb.querySelector('img').src=gp[gi];lb.querySelector('p').textContent=`${gi+1} / ${gp.length}`},step=n=>{gi=(gi+n+gp.length)%gp.length;show()};
function openGal(id,i){const o=A.find(x=>x.id===id);if(!o)return;gp=o.photos.length?o.photos:[IMG[o.cat]];gi=i||0;show();lb.showModal()}
lb.onclick=e=>{const b=e.target.closest('button');if(b&&b.classList.contains('x')||e.target===lb)lb.close();else if(b)step(b.classList.contains('nx')?1:-1)};
lb.ontouchstart=e=>{tx=e.touches[0].clientX};lb.ontouchend=e=>{const d=e.changedTouches[0].clientX-tx;if(Math.abs(d)>40)step(d<0?1:-1)};
addEventListener('keydown',e=>{if(lb.open&&(e.key==='ArrowRight'||e.key==='ArrowLeft'))step(e.key==='ArrowRight'?1:-1)});
/* клики */
document.addEventListener('click',e=>{const T=e.target,f=T.closest('[data-f]'),g=T.closest('[data-g]'),dc=T.closest('.dc'),b=T.closest('#tabs button'),d=T.closest('#dtabs button'),l=T.closest('.lc');
if(f){const id=+f.dataset.f,i=FAV.indexOf(id);i<0?FAV.push(id):FAV.splice(i,1);saveFav();if(F.fav)draw();else{$$(`[data-f="${id}"]`).forEach(x=>x.classList.toggle('on',i<0));$('#fn').textContent=FAV.length}}
else if(g)openGal(+g.dataset.g,+g.dataset.gi||0);
else if(dc){sel(dc.dataset.go);$('#catalog').scrollIntoView()}else if(b)sel(b.dataset.k);else if(d){dl=dl===d.dataset.d?'':d.dataset.d;draw()}
else if(l&&!T.closest('a')){sy=scrollY;location.hash='obj-'+l.dataset.i}});
document.addEventListener('keydown',e=>{if((e.key==='Enter'||e.key===' ')&&e.target.matches('.dc,.gm')){e.preventDefault();e.target.click()}});
/* страница объекта */
const unesc=v=>{const d=document.createElement('textarea');d.innerHTML=String(v??'');return d.value};
/* Кнопка «Написать в Telegram»: админ может заменить ссылку или убрать кнопку (SITE_ASSETS.tg_overrides, ключ — id или bot:id; пустая строка — кнопки нет). */
const tgUrl=o=>{const ov=SITE_ASSETS.tg_overrides||{},key=(o.source==='telegram_bot'?'bot:':'')+o.id;const v=Object.prototype.hasOwnProperty.call(ov,key)?ov[key]:o.tg;
  try{const u=new URL(String(v||'').trim());return['http:','https:'].includes(u.protocol)?u:null}catch(_){return null}};
const tgHref=(o,msg)=>{const u=tgUrl(o);if(!u)return'';if(/^(t\.me|telegram\.me)$/i.test(u.hostname)&&!u.searchParams.has('text'))u.searchParams.set('text',decodeURIComponent(msg));return u.href};
const pageHTML=o=>{const ph=o.photos.length?o.photos:[IMG[o.cat]],t_=tel(o.phone),done=o.status==='rented',place=[cityName(o.city),o.district].filter(Boolean).join(', '),msg=encodeURIComponent(unesc(t('tg_msg',{site:location.hostname,t:titleOf(o),place})));const T=titleOf(o);
return`<a class="bk" href="#catalog" onclick="if(sy!=null){history.back();return false}">${t('back_catalog')}</a><div class="ob"><div><div class="c3${ph.length>1?'':' one'}" tabindex="0" role="region" aria-roledescription="${t('carousel')}" aria-label="${t('photos_of',{t:T})}" data-c3="${o.id}"><div class="c3-stage">${ph.map((s,j)=>`<figure class="c3-it" data-i="${j}"><img src="${s}" alt="${t('photo_n',{t:T,n:j+1})}" draggable="false" ${j>2&&j<ph.length-2?'loading="lazy"':''}></figure>`).join('')}</div>${ph.length>1?`<button type="button" class="c3-nav c3-prev" aria-label="${t('prev_photo')}">‹</button><button type="button" class="c3-nav c3-next" aria-label="${t('next_photo')}">›</button>`:''}<span class="cn2 c3-count">1 / ${ph.length}</span></div>${ph.length>1?`<input type="range" class="c3-bar" min="0" max="${ph.length-1}" step="1" value="0" aria-label="${t('scroll_photos')}">`:''}
<div class="tx"><h3>${t('desc')}</h3><p>${o.desc}</p>${o.features&&o.features.length?`<h3>${t('features')}</h3><ul class="pl">${o.features.map(y=>`<li>${y}</li>`).join('')}</ul>`:''}<h3>${t('near')}</h3><ul class="pl">${NEAR[o.cat].map(y=>`<li>${y}</li>`).join('')}</ul>${locHTML(o)}</div></div>
<aside class="sd"><div class="ch"><em>${cat(o.cat).t}</em><em>${termOf(o)}</em><em class="st-${o.status||'free'}">${stl(o)}</em></div><h2>${T}</h2><div class="pc">${fmt(o.price)} <small>${priceUnit(o)}</small></div><div class="sg"><div><b>${t('city')}</b>${cityName(o.city)}</div><div><b>${t('district')}</b>${o.district}</div><div><b>${t('area')}</b>${o.area} ${t('m2')}</div><div><b>${t('floor')}</b>${floorOf(o)}</div>${o.rooms?`<div><b>${t('rooms')}</b>${o.rooms}</div>`:''}</div>
${done?`<p class="note">${t('already',{s:stl(o).toLowerCase()})}</p>`:`<div class="own"><small>${t('owner_contacts')}</small><b>${o.owner||t('owner_default')}</b>${t_?`<a href="${t_}">${o.phone}</a>`:''}</div>${t_?`<a class="btn" href="${t_}">${t('call_owner')}</a>`:''}`}${tgHref(o,msg)&&!done?`<a class="btn w" href="${escHTML(tgHref(o,msg))}" target="_blank" rel="noopener">${t('write_tg')}</a>`:''}<button type="button" class="btn w${FAV.includes(o.id)?' on':''}" data-f="${o.id}">${t('fav')}</button></aside></div>${done||!t_?'':`<a class="fcall" href="${t_}">${t('call_owner')}</a>`}`};
const MD=document.querySelector('meta[name=description]'),D0=MD.content;const OG=document.querySelector('meta[property="og:image"]');if(OG)OG.content=new URL(siteAsset('social_preview'),document.baseURI).href;
function ld(o){let s=$('#ldo');if(!s){s=document.createElement('script');s.id='ldo';s.type='application/ld+json';document.head.append(s)}s.textContent=o?JSON.stringify({'@context':'https://schema.org','@type':'Product',name:o.title,description:o.desc,image:o.photos[0]||IMG[o.cat],offers:{'@type':'Offer',priceCurrency:'UZS',price:o.price,availability:o.status==='free'?'https://schema.org/InStock':'https://schema.org/SoldOut'}}):''}
/* ===== 3D-карусель фото на странице объекта: свайп/перетаскивание, стрелки, ползунок, по кругу ===== */
function initC3(root,id){
  if(!root)return;
  const items=[...root.querySelectorAll('.c3-it')],n=items.length,bar=root.parentElement.querySelector('.c3-bar'),count=root.querySelector('.c3-count');
  let pos=0,drag=null;
  const wrap=v=>((v%n)+n)%n;
  const rel=(i,p)=>{let d=i-p;if(n>1){d=((d%n)+n)%n;if(d>n/2)d-=n}return d};
  const paint=(animate=true)=>{
    root.classList.toggle('dragging',!animate);
    items.forEach((el,i)=>{
      const d=rel(i,pos),a=Math.abs(d),c=Math.min(a,3);
      el.style.transform=`translateX(${d*58}%) translateZ(${-c*140}px) rotateY(${Math.max(-1,Math.min(1,d))*-38}deg) scale(${1-Math.min(a,2)*.08})`;
      el.style.zIndex=String(100-Math.round(a*10));
      el.style.opacity=a>2.4?'0':a>1.4?'.55':'1';
      el.style.pointerEvents=a>1.5?'none':'auto';
      el.classList.toggle('on',a<.5);
    });
    const cur=wrap(Math.round(pos));
    if(count)count.textContent=`${cur+1} / ${n}`;
    if(bar&&!bar.matches(':active'))bar.value=cur;
  };
  const go=t=>{pos=Math.round(t);paint();};
  root.querySelector('.c3-prev')?.addEventListener('click',e=>{e.stopPropagation();go(pos-1)});
  root.querySelector('.c3-next')?.addEventListener('click',e=>{e.stopPropagation();go(pos+1)});
  bar?.addEventListener('input',()=>{const target=+bar.value,cur=wrap(Math.round(pos));pos=Math.round(pos)+rel(target,cur);paint()});
  root.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'){e.preventDefault();go(pos-1)}else if(e.key==='ArrowRight'){e.preventDefault();go(pos+1)}else if(e.key==='Enter')openGal(id,wrap(Math.round(pos)))});
  const stage=root.querySelector('.c3-stage');
  stage.addEventListener('pointerdown',e=>{if(e.button>0)return;drag={x:e.clientX,p:pos,moved:false,id:e.pointerId}});
  stage.addEventListener('pointermove',e=>{if(!drag||n<2)return;const dx=e.clientX-drag.x;if(Math.abs(dx)>6&&!drag.moved){drag.moved=true;stage.setPointerCapture?.(drag.id)}
    if(drag.moved){const w=stage.clientWidth*.58||1;pos=drag.p-dx/w;paint(false)}});
  const end=e=>{if(!drag)return;const d=drag;drag=null;
    if(d.moved){const v=pos-d.p;go(Math.abs(v)<.2&&Math.abs(v)>.02?d.p+Math.sign(v):pos);return}
    paint();const it=e.target.closest&&e.target.closest('.c3-it');if(!it)return;const i=+it.dataset.i,d2=rel(i,pos);
    if(Math.abs(d2)<.5)openGal(id,i);else go(pos+d2)};
  stage.addEventListener('pointerup',end);stage.addEventListener('pointercancel',()=>{if(drag){drag=null;go(pos)}});
  stage.addEventListener('dragstart',e=>e.preventDefault());
  paint();
}
/* ===== Приблизительное местоположение объекта (без точного адреса) ===== */
const GEO={'Алмалык':[40.8447,69.5983,'Ташкентская область'],'Ташкент':[41.3111,69.2797,'город Ташкент'],'Самарканд':[39.6542,66.9597,'Самаркандская область'],
'Андижан':[40.7821,72.3442,'Андижанская область'],'Наманган':[40.9983,71.6726,'Наманганская область'],'Нукус':[42.4600,59.6100,'Республика Каракалпакстан'],
'Фергана':[40.3864,71.7864,'Ферганская область'],'Карши':[38.8606,65.7891,'Кашкадарьинская область'],'Бухара':[39.7747,64.4286,'Бухарская область'],'Коканд':[40.5286,70.9425,'Ферганская область']};
const PIN='<svg viewBox="0 0 24 24" width="30" height="30" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.6" fill="none" stroke="currentColor" stroke-width="2"/></svg>';
function locHTML(o){const g=GEO[o.city];if(!g)return'';const place=o.district&&o.district!==o.city?`${o.district}, ${cityName(o.city)}`:cityName(o.city);
  return`<div class="loc" data-lat="${g[0]}" data-lon="${g[1]}"><div class="loc-tx"><i>${PIN}</i><div><b>${place}</b><span>${regionName(g[2])}</span><em class="loc-dist"><button type="button" class="loc-me">${t('loc_me')}</button></em><small>${t('loc_note')}</small></div></div>
  <a class="loc-map" href="https://yandex.uz/maps/?ll=${g[1]},${g[0]}&z=13&pt=${g[1]},${g[0]}" target="_blank" rel="noopener" aria-label="${t('loc_map')}"><span class="loc-ring"></span></a></div>`}
function loadLeaflet(){if(window.L)return Promise.resolve();if(loadLeaflet.p)return loadLeaflet.p;
  const css=document.createElement('link');css.rel='stylesheet';css.href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';document.head.append(css);
  return loadLeaflet.p=new Promise((ok,no)=>{const sc=document.createElement('script');sc.src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';sc.onload=ok;sc.onerror=no;document.head.append(sc)})}
function km(a,b,c,d){const r=x=>x*Math.PI/180,R=6371,dl=r(c-a),dn=r(d-b),h=Math.sin(dl/2)**2+Math.cos(r(a))*Math.cos(r(c))*Math.sin(dn/2)**2;return Math.round(2*R*Math.asin(Math.sqrt(h)))}
function initLoc(box){if(!box)return;const lat=+box.dataset.lat,lon=+box.dataset.lon,map=box.querySelector('.loc-map'),dist=box.querySelector('.loc-dist');
  loadLeaflet().then(()=>{const m=L.map(map,{center:[lat,lon],zoom:13,zoomControl:false,attributionControl:true,dragging:false,scrollWheelZoom:false,doubleClickZoom:false,boxZoom:false,keyboard:false,touchZoom:false,tap:false});
    m.attributionControl.setPrefix(false);L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:18,attribution:'© OpenStreetMap'}).addTo(m);
    L.circle([lat,lon],{radius:450,color:'#3b6cf6',weight:8,fillColor:'#7d9cf8',fillOpacity:.45}).addTo(m);map.classList.add('ready')}).catch(()=>{});
  const showDist=()=>navigator.geolocation.getCurrentPosition(p=>{const k=km(p.coords.latitude,p.coords.longitude,lat,lon);dist.textContent=k<1?t('loc_near'):t('loc_km',{n:k.toLocaleString('ru-RU')})},()=>{dist.textContent=t('loc_fail')},{maximumAge:600000,timeout:10000});
  if(!navigator.geolocation){dist.remove();return}
  dist.querySelector('.loc-me').onclick=e=>{e.stopPropagation();dist.textContent=t('loc_wait');showDist()};
  navigator.permissions?.query({name:'geolocation'}).then(r=>{if(r.state==='granted')showDist()}).catch(()=>{})}
function route(){const m=/^#obj-(\d+)$/.exec(location.hash),o=m&&A.find(x=>x.id===+m[1]),b=document.body;
if(o){$('#obj').innerHTML=pageHTML(o);initC3($('#obj .c3'),o.id);initLoc($('#obj .loc'));bind($('#obj'));b.classList.add('pg');scrollTo({top:0,behavior:'instant'});document.title=unesc(`${titleOf(o)}, ${o.district}, ${cityName(o.city)} — ${fmt(o.price)} ${t('sum')}`);MD.content=o.desc;ld(o)}
else if(b.classList.contains('pg')){b.classList.remove('pg');document.title=T0;MD.content=D0;ld();sy!=null?scrollTo({top:sy,behavior:'instant'}):$('#catalog').scrollIntoView()}}
function setCity(c){city=c;try{localStorage.setItem('city',c)}catch(_){}
const configured=HERO[c]||[];const h=configured.some(Boolean)?configured:null;
if(h){
  /* Resolve asset paths against the actual page URL, including installations in subfolders. */
  cityHeroMobile.srcset=new URL(h[1]||h[0],document.baseURI).href;
  cityHeroImage.src=new URL(h[0]||h[1],document.baseURI).href;
  cityHeroImage.alt=t('hero_alt')+' — '+cityName(c);
  cityHero.hidden=false;
}else{
  cityHero.hidden=true;
  cityHeroMobile.removeAttribute('srcset');
  cityHeroImage.removeAttribute('src');
}
$('#cv').textContent=cityName(c);$$('#cu button').forEach(b=>b.classList.toggle('on',b.dataset.c===c));$$('.cl').forEach(e=>e.textContent=window.LANG==='uz'?cityIn(c):CT[c].p);$$('.cn').forEach(e=>e.textContent=cityName(c));
fillDist();drawDirs();draw()}
$$('#cu button').forEach(b=>{b.textContent=cityName(b.dataset.c)});
const cs=$('#cs'),cbn=$('#cb'),cu=$('#cu'),cls=()=>{cu.hidden=true;cs.classList.remove('open');cbn.setAttribute('aria-expanded','false')};
cbn.onclick=()=>{const o=cu.hidden;cu.hidden=!o;cs.classList.toggle('open',o);cbn.setAttribute('aria-expanded',String(o))};
cu.onclick=e=>{const b=e.target.closest('button');if(b){setCity(b.dataset.c);cls()}};
document.addEventListener('click',e=>{if(!cs.contains(e.target))cls()});addEventListener('keydown',e=>{if(e.key==='Escape')cls()});addEventListener('hashchange',route);
/* header, burger, scroll-spy */
const hd=$('#hd'),bgr=$('#bgr');
new IntersectionObserver(([e])=>hd.classList.toggle('on',!e.isIntersecting),{rootMargin:'-80px 0px 0px 0px'}).observe($('#home'));
bgr.onclick=()=>bgr.setAttribute('aria-expanded',hd.classList.toggle('open'));$('#lk').onclick=e=>{if(e.target.closest('a')){hd.classList.remove('open');bgr.setAttribute('aria-expanded','false')}};
const nav=$$('#lk a:not(.btn)');
const so=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)nav.forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#'+e.target.id))}),{rootMargin:'-40% 0px -55% 0px'});
['directions','catalog','owner','contacts'].forEach(id=>so.observe(document.getElementById(id)));
$('#yr').textContent=new Date().getFullYear();
/* ===== Объявления и реклама из Telegram-бота (API на Render) ===== */
const escHTML=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const httpsUrl=u=>/^https:\/\//.test(String(u||''))?String(u):'';
const fromBot=o=>({...o,id:+o.id,source:'telegram_bot',title:escHTML(o.title),city:escHTML(o.city),district:escHTML(o.district),desc:escHTML(o.desc),
  owner:escHTML(o.owner),phone:escHTML(o.phone),floor:escHTML(o.floor),term:escHTML(o.term),unit:escHTML(o.unit),features:(o.features||[]).map(escHTML),
  photos:(o.photos||[]).map(httpsUrl).filter(Boolean),tg:httpsUrl(o.tg),status:o.status==='rented'?'rented':'free',area:+o.area||0,rooms:+o.rooms||0,price:+o.price||0});
/* Бесплатный Render «засыпает»: первый ответ может идти до минуты — ждём до 70 секунд. */
async function apiGet(path){
  const ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),70000);
  try{const r=await fetch(`${API_BASE}${path}`,{cache:'no-store',signal:ctrl.signal});if(!r.ok)throw new Error(`API HTTP ${r.status}`);return await r.json()}
  finally{clearTimeout(timer)}
}
async function loadBotListings(){
  if(!API_ENABLED)return;
  try{
    const payload=await apiGet('/api/listings');
    const remote=(Array.isArray(payload)?payload:Array.isArray(payload.items)?payload.items:[]).map(fromBot);
    A=[...remote,...A.filter(item=>item.source!=='telegram_bot'&&item.source!=='bot')];
    const d=F.dist;fillDist();if(d){F.dist=d;$('#flt [name=dist]').value=d}
    drawDirs();draw();route();
  }catch(error){console.warn('RENT UZBEKISTAN API is unavailable; the static catalogue remains active.',error)}
}
async function loadBotAds(){
  if(!API_ENABLED)return;
  try{
    const ads=(await apiGet('/api/ads')).filter(ad=>httpsUrl(ad.image));
    if(!ads.length)return;
    let i=0;
    const show=()=>{const ad=ads[i++%ads.length];SITE_ASSETS.ad_image=httpsUrl(ad.image);SITE_ASSETS.ad_link=httpsUrl(ad.link)||OWNER_BOT+'?start=ad';applyAdBanner()};
    show();if(ads.length>1)setInterval(show,8000);
  }catch(error){console.warn('Ads API is unavailable.',error)}
}

let sv=null;try{sv=localStorage.getItem('city')}catch(_){}
/* Ссылка из бота: ?city=Ташкент&deal=sale — открыть сразу нужный город и тип сделки. */
const QS=new URLSearchParams(location.search),qCity=QS.get('city');if(QS.get('deal')==='sale')dl='Приобрести';else if(QS.get('deal')==='daily')dl='Посуточно';
setCity(CT[qCity]?qCity:CT[sv]?sv:'Алмалык');route();
loadBotListings();loadBotAds();
