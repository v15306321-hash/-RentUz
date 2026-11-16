const TG='https://t.me/Resell_Tashkent'; /* Telegram для связи и подбора объектов */
const OWNER_BOT='https://t.me/Arenda_UZB_bot'; /* Бот для автоматического добавления недвижимости */
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const bind=r=>r.querySelectorAll('[data-tg]').forEach(a=>{a.href=TG;a.target='_blank';a.rel='noopener'});bind(document);
/* ↓ Категории: p — кадр обложки из фото */
const CAT=[
{k:'flat',t:'Квартиры',d:'Студии и квартиры в новостройках — на сутки и на длительный срок.',s:['Студии и 1–3 комнаты','С мебелью и без','Посуточно и надолго'],p:'88% 26%'},
{k:'house',t:'Дома и дачи',d:'Частные дома с двором и дачи для семьи или отдыха.',s:['Дома с участком','Дачи с садом','Сезонно и круглый год'],p:'4% 75%'},
{k:'office',t:'Офисы',d:'Кабинеты и open space в бизнес-центрах и новых зданиях.',s:['От 20 м²','Open space','С парковкой'],p:'65% 40%'},
{k:'shop',t:'Магазины и склады',d:'Торговые помещения на первой линии, под кафе и склады.',s:['Первая линия','Под кафе и услуги','Склады с пандусом'],p:'54% 100%'}];
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
const siteAsset=k=>SITE_ASSETS[k]||ASSET_DEFAULTS[k]||'';
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
  let href=TG;
  const configured=String(SITE_ASSETS.ad_link||'').trim();
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
const OWN={n:'Владелец объекта',ph:'+998 90 000 00 00'};
const NEAR={flat:['Школа','Детский сад','Больница','Магазин','Рынок'],house:['Школа','Детский сад','Больница','Магазин','Рынок'],office:['Банки и кафе','Остановка транспорта','Парковка','Магазины','Бизнес-центры'],shop:['Высокая проходимость','Остановка транспорта','Парковка','Рынок','Банк рядом']};
const SLOTS={flat:['Гостиная','Спальня','Кухня','Санузел','Балкон','Вид из окна'],house:['Гостиная','Спальня','Кухня','Санузел','Двор','Терраса'],office:['Рабочая зона','Переговорная','Кухня','Санузел','Вход','Парковка'],shop:['Торговый зал','Витрина','Подсобка','Санузел','Вход','Парковка']};
/* ===== v2: данные, поиск, избранное, статусы, галерея ===== */
const ST={free:'Свободно',rented:'Занято'},stl=o=>ST[o.status]||ST.free;
const LS='arenda_listings_v1';let A=null;try{A=JSON.parse(localStorage.getItem(LS))}catch(_){}
if(!Array.isArray(A))A=window.LISTINGS||[];
/* Normalize legacy/unknown statuses: only free and rented are supported. */
let statusMigration=false;A=A.map(o=>{const status=o.status==='rented'?'rented':'free';if(status!==o.status)statusMigration=true;return status===o.status?o:{...o,status}});
if(statusMigration){try{localStorage.setItem(LS,JSON.stringify(A))}catch(_){}}
let FAV=[];try{FAV=JSON.parse(localStorage.getItem('fav'))||[]}catch(_){}
const saveFav=()=>{try{localStorage.setItem('fav',JSON.stringify(FAV))}catch(_){}};
const fmt=n=>n.toLocaleString('ru-RU'),cat=k=>CAT.find(c=>c.k===k),tel=p=>'tel:'+(p||OWN.ph).replace(/[^+\d]/g,'');
const F0=()=>({q:'',dist:'',pmin:'',pmax:'',amin:'',amax:'',rooms:'',st:'',sort:'',fav:false});
let city='Алмалык',cur='all',dl='',sy=null,F=F0();
const drawDirs=()=>{$('#dirs').innerHTML=CAT.map(c=>{const n=A.filter(x=>x.cat===c.k&&x.city===city).length;return`<div class="dc" data-go="${c.k}" tabindex="0" role="button" style="--im:url(${IMG[c.k]})"><h3>${c.t}</h3><p>${c.d}</p><ul>${c.s.map(x=>`<li>${x}</li>`).join('')}</ul><span>Смотреть объекты (${n})</span></div>`}).join('')};
const DL=['Посуточно','На месяц','Приобрести'],DM={'Посуточно':'Посуточно','На месяц':'На месяц','Приобрести':'Продажа'};
const rows=()=>{const q=F.q.trim().toLowerCase();return A.filter(o=>o.city===city&&(cur==='all'||o.cat===cur)&&(!dl||o.term===DM[dl])&&(!F.dist||o.district===F.dist)&&(!F.pmin||o.price>=+F.pmin)&&(!F.pmax||o.price<=+F.pmax)&&(!F.amin||o.area>=+F.amin)&&(!F.amax||o.area<=+F.amax)&&(!F.rooms||(F.rooms==='4'?o.rooms>=4:o.rooms===+F.rooms))&&(!F.st||o.status===F.st)&&(!F.fav||FAV.includes(o.id))&&(!q||`${o.title} ${o.district} ${o.desc}`.toLowerCase().includes(q)))};
const card=o=>{const f=FAV.includes(o.id),s=o.status||'free';return`<article class="lc s-${s}" data-i="${o.id}"><div class="pw"><button type="button" class="ph" data-g="${o.id}" aria-label="Смотреть фото: ${o.title}" style="background-image:url('${o.photos[0]||IMG[o.cat]}')"></button><span class="bd st-${s}">${stl(o)}</span><span class="cn2">${o.photos.length||1} фото</span><button type="button" class="hr${f?' on':''}" data-f="${o.id}" aria-label="Добавить в избранное: ${o.title}">♥</button></div><div class="cb"><div class="ch"><em>${cat(o.cat).t}</em><em>${o.term}</em></div><h3>${o.title}</h3><div class="dd">${o.district}</div><div class="pc">${fmt(o.price)} <small>сум${o.unit?' / '+o.unit:''}</small></div><div class="sp"><span>${o.area} м²</span><span>${o.rooms?o.rooms+' комн.':o.floor}</span></div>${s==='rented'?'':`<a class="cl2" href="${tel(o.phone)}">Позвонить</a>`}</div></article>`};
function draw(){$('#dtabs').innerHTML=DL.map(d=>`<button data-d="${d}" class="${d===dl?'on':''}">${d}</button>`).join('');$('#tabs').innerHTML=[['all','Все'],...CAT.map(c=>[c.k,c.t])].map(([k,t])=>`<button data-k="${k}" class="${k===cur?'on':''}">${t}</button>`).join('');
const r=rows(),s=F.sort;if(s)r.sort((a,b)=>s==='p'?a.price-b.price:s==='d'?b.price-a.price:b.area-a.area);
$('#fn').textContent=FAV.length;$('#fv').classList.toggle('on',F.fav);$('#fc').textContent='Найдено: '+r.length;
$('#gal').innerHTML=r.map(card).join('')||'<p class="note">По этим фильтрам объектов нет. Измените условия или напишите нам — подберём вариант.</p>'}
const sel=k=>{cur=k;draw()};
const fillDist=()=>{const available=[...new Set([...CT[city].d,...A.filter(x=>x.city===city).map(x=>x.district).filter(Boolean)])];$('#flt [name=dist]').innerHTML='<option value="">Все районы</option>'+available.map(x=>`<option>${x}</option>`).join('');F.dist=''};
$('#flt').oninput=e=>{if(e.target.name){F[e.target.name]=e.target.value;draw()}};
$('#flt').onsubmit=e=>e.preventDefault();
$('#flt').onreset=()=>setTimeout(()=>{F=F0();draw()});
$('#fv').onclick=()=>{F.fav=!F.fav;draw()};
/* галерея */
const lb=document.createElement('dialog');lb.id='lb';lb.innerHTML='<button class="x" aria-label="Закрыть">×</button><button class="pv" aria-label="Предыдущее фото">‹</button><img alt=""><button class="nx" aria-label="Следующее фото">›</button><p></p>';document.body.append(lb);
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
const pageHTML=o=>{const ph=o.photos.length?o.photos:[IMG[o.cat]],t=tel(o.phone),done=o.status==='rented',msg=encodeURIComponent(`Здравствуйте! Интересует объект «${o.title}» (${o.city}, ${o.district}).`);
return`<a class="bk" href="#catalog" onclick="if(sy!=null){history.back();return false}">← Назад к каталогу</a><div class="ob"><div><div class="gm" data-g="${o.id}" data-gi="0" tabindex="0" role="button" aria-label="Открыть галерею: ${o.title}" style="background-image:url('${ph[0]}')"><span class="cn2">${ph.length} фото</span></div><div class="gs">${ph.slice(1).map((s,j)=>`<img class="sl" loading="lazy" data-g="${o.id}" data-gi="${j+1}" src="${s}" alt="${o.title} — фото ${j+2}">`).join('')}</div>
<div class="tx"><h3>Описание</h3><p>${o.desc}</p><h3>Преимущества</h3><ul class="pl">${o.features.map(y=>`<li>${y}</li>`).join('')}</ul><h3>Рядом есть</h3><ul class="pl">${NEAR[o.cat].map(y=>`<li>${y}</li>`).join('')}</ul></div></div>
<aside class="sd"><div class="ch"><em>${cat(o.cat).t}</em><em>${o.term}</em><em class="st-${o.status||'free'}">${stl(o)}</em></div><h2>${o.title}</h2><div class="pc">${fmt(o.price)} <small>сум${o.unit?' / '+o.unit:''}</small></div><div class="sg"><div><b>Город</b>${o.city}</div><div><b>Район</b>${o.district}</div><div><b>Площадь</b>${o.area} м²</div><div><b>Этаж / участок</b>${o.floor}</div>${o.rooms?`<div><b>Комнат</b>${o.rooms}</div>`:''}</div>
${done?`<p class="note">Объект уже ${stl(o).toLowerCase()}. Напишите нам — подберём похожий вариант.</p>`:`<div class="own"><small>Контакты владельца</small><b>${o.owner||OWN.n}</b><a href="${t}">${o.phone||OWN.ph}</a></div><a class="btn" href="${t}">Позвонить владельцу</a>`}<a class="btn w" href="${o.tg||TG}?text=${msg}" target="_blank" rel="noopener">Написать в Telegram</a><button type="button" class="btn w${FAV.includes(o.id)?' on':''}" data-f="${o.id}">♥ Избранное</button></aside></div>${done?'':`<a class="fcall" href="${t}">Позвонить владельцу</a>`}`};
const MD=document.querySelector('meta[name=description]'),D0=MD.content;const OG=document.querySelector('meta[property="og:image"]');if(OG)OG.content=new URL(siteAsset('social_preview'),document.baseURI).href;
function ld(o){let s=$('#ldo');if(!s){s=document.createElement('script');s.id='ldo';s.type='application/ld+json';document.head.append(s)}s.textContent=o?JSON.stringify({'@context':'https://schema.org','@type':'Product',name:o.title,description:o.desc,image:o.photos[0]||IMG[o.cat],offers:{'@type':'Offer',priceCurrency:'UZS',price:o.price,availability:o.status==='free'?'https://schema.org/InStock':'https://schema.org/SoldOut'}}):''}
function route(){const m=/^#obj-(\d+)$/.exec(location.hash),o=m&&A.find(x=>x.id===+m[1]),b=document.body;
if(o){$('#obj').innerHTML=pageHTML(o);bind($('#obj'));b.classList.add('pg');scrollTo({top:0,behavior:'instant'});document.title=`${o.title}, ${o.district}, ${o.city} — ${fmt(o.price)} сум`;MD.content=o.desc;ld(o)}
else if(b.classList.contains('pg')){b.classList.remove('pg');document.title=T0;MD.content=D0;ld();sy!=null?scrollTo({top:sy,behavior:'instant'}):$('#catalog').scrollIntoView()}}
function setCity(c){city=c;try{localStorage.setItem('city',c)}catch(_){}
const configured=HERO[c]||[];const h=configured.some(Boolean)?configured:null;
if(h){
  /* Resolve asset paths against the actual page URL, including installations in subfolders. */
  cityHeroMobile.srcset=new URL(h[1]||h[0],document.baseURI).href;
  cityHeroImage.src=new URL(h[0]||h[1],document.baseURI).href;
  cityHeroImage.alt='Городской пейзаж — '+c;
  cityHero.hidden=false;
}else{
  cityHero.hidden=true;
  cityHeroMobile.removeAttribute('srcset');
  cityHeroImage.removeAttribute('src');
}
$('#cv').textContent=c;$$('#cu button').forEach(b=>b.classList.toggle('on',b.dataset.c===c));$$('.cl').forEach(e=>e.textContent=CT[c].p);$$('.cn').forEach(e=>e.textContent=c);
fillDist();drawDirs();draw()}
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
async function loadBotListings(){
  if(!API_ENABLED)return;
  try{
    const response=await fetch(`${API_BASE}/api/listings`,{cache:'no-store'});
    if(!response.ok)throw new Error(`API HTTP ${response.status}`);
    const payload=await response.json();
    const remote=Array.isArray(payload.items)?payload.items:[];
    A=[...A.filter(item=>item.source!=='telegram_bot'),...remote];
    fillDist();drawDirs();draw();
  }catch(error){console.warn('RENT UZBEKISTAN API is unavailable; the static catalogue remains active.',error)}
}

let sv=null;try{sv=localStorage.getItem('city')}catch(_){}
setCity(CT[sv]?sv:'Алмалык');route();
loadBotListings();
