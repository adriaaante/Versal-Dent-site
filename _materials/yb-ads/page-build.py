# -*- coding: utf-8 -*-
"""
Страница-шпаргалка для кабинета Яндекс.Бизнеса — «Версаль», раздел
«Свои объявления». Собирает `Объявления-Версаль.html`: превью картинки с
постоянной ссылкой, заголовок, описание, цена, ссылка; клик по полю
копирует текст в буфер.

⚠️ Поле «Цена товара или услуги» принимает **только число** — «от» туда
не вписать (проверено владельцем 13.08.2026).
⚠️ **Цену не дублируем в заголовке** (владелец, 13.08.2026): если она
стоит в поле цены, в заголовке её быть не должно — освободившееся место
работает на выгоду («за один визит», «как свой зуб», гео).
Где цена может ввести в заблуждение (пародонтология — 800 ₽ это за один
зуб), поле цены оставляем пустым: оно опциональное.

Ссылки на картинки — постоянные, из хранилища Higgsfield: залить
`media_upload` → curl PUT → `media_confirm`, полученные URL положить в
`_uploads.json` (формат: [[ключ, media_id, код, url], …]).

Запуск: python3 page-build.py
"""
import json, html, os

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://versal-dent.ru'
OUT = os.path.join(HERE, 'Объявления-Версаль.html')

# ключ, заголовок (≤56), описание (≤81), цена (только число или ''), ссылка
CARDS = [
    ('kariés'         , 'Лечение кариеса в Реутове за один визит',
     'Пломба за визит, анестезия без боли. Цены фиксируем в договоре.',
     '5 500 ₽', '/services/terapiya.html'),
    ('kanaly'         , 'Лечение каналов — сохраняем зуб, а не удаляем',
     'Пульпит и периодонтит под контролем КТ. Реутов, у м. Новокосино.',
     '7 000 ₽', '/services/terapiya.html'),
    ('bol'            , 'Болит зуб? Примем сегодня, без выходных',
     'Ежедневно 10:00–20:00, 10 минут от м. Новокосино. Снимем боль сразу.',
     '', '/contacts.html'),
    ('mudrosti'       , 'Удаление зуба мудрости в Реутове',
     'Даже сложное: по КТ, с анестезией и планом восстановления.',
     '9 500 ₽', '/services/hirurgiya.html'),
    ('kt'             , 'КТ и письменный план лечения со сметой',
     'Вместо 7 500 ₽. Увидите свою ситуацию и точные цены до лечения.',
     '4 200 ₽', '/promotions.html'),
    ('cirkon'         , 'Циркониевая коронка — как свой зуб',
     'Прочная, не отличить от родного. Цифровой слепок без массы во рту.',
     '22 000 ₽', '/services/protezirovanie.html'),
    ('implant'        , 'Имплант с коронкой под ключ, Реутов',
     'Фиксированная цена: имплант, абатмент и коронка. Osstem, Dentium.',
     '45 000 ₽', '/services/implantaciya.html'),
    ('allon4'         , 'Все зубы на 4 имплантах — за один этап',
     'Несъёмный протез вместо съёмного. Вернём жевание и улыбку.',
     '120 000 ₽', '/services/implantaciya.html'),
    ('protez'         , 'Съёмный протез в Реутове, у Новокосино',
     'Акрил, нейлон или бюгель. Подберём тот, что удобно носить.',
     '28 000 ₽', '/services/protezirovanie.html'),
    ('brekety'        , 'Брекеты взрослым — ровные зубы в любом возрасте',
     'И в 30, и в 45. Консультация ортодонта с ТРГ — бесплатно.',
     '35 000 ₽', '/services/ortodontiya.html'),
    ('elaynery'       , 'Элайнеры — выравнивание без брекетов',
     'Прозрачные капы, незаметны на работе и на встречах.',
     '120 000 ₽', '/services/ortodontiya.html'),
    ('otbelivanie'    , 'Отбеливание Amazing White за один визит',
     'Вместо 25 000 ₽. До 6–8 тонов, обе челюсти, с защитой эмали.',
     '17 500 ₽', '/services/gigiena.html'),
    ('desny'          , 'Кровоточат дёсны? Лечим пародонтит',
     'Чистка карманов, Vector-терапия, шинирование. Остановим подвижность.',
     '', '/services/parodontologiya.html'),
    ('restavraciya'   , 'Скол переднего зуба — реставрация за визит',
     'Восстановим форму и цвет. Незаметно даже вблизи.',
     '8 000 ₽', '/services/terapiya.html'),
]

CSS = '''
:root{--gold:#C2A14E;--ivory:#FCFAF6;--espresso:#2C2620;--line:#E7DFCF}
*{box-sizing:border-box}
body{margin:0;background:var(--ivory);color:var(--espresso);font:16px/1.55 Manrope,system-ui,sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:38px 20px 80px}
h1{font:600 34px/1.2 'Playfair Display',Georgia,serif;margin:0 0 8px}
.sub{color:#6b6055;margin:0 0 26px}
.note{background:#fff;border:1px solid var(--line);border-left:4px solid var(--gold);
  padding:16px 18px;border-radius:10px;margin:0 0 30px}
.ad{display:grid;grid-template-columns:190px 1fr;gap:20px;background:#fff;border:1px solid var(--line);
  border-radius:14px;padding:18px;margin:0 0 16px;position:relative}
.ad__num{position:absolute;left:-11px;top:18px;width:26px;height:26px;border-radius:50%;
  background:var(--gold);color:#fff;font-weight:700;font-size:13px;display:grid;place-items:center}
.ad__pic{display:block;text-decoration:none}
.ad__pic img{width:190px;height:190px;object-fit:cover;border-radius:10px;display:block}
@media(max-width:720px){.ad__dl{width:100%}}
.ad__dl{display:block;width:190px;margin-top:8px;padding:8px 10px;border:1px solid var(--gold);
  border-radius:8px;background:#fff;color:var(--gold);font:600 12.5px/1.2 Manrope,sans-serif;
  cursor:pointer;transition:.15s}
.ad__dl:hover{background:var(--gold);color:#fff}
.ad__dl:disabled{opacity:.6;cursor:default}
.f{margin:0 0 11px}
.f__k{display:block;font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:#8d8175;margin-bottom:4px}
.f__k em{font-style:normal;color:#b3a793}
.f__v{background:#FBF8F2;border:1px solid var(--line);border-radius:8px;padding:9px 12px;cursor:pointer;
  transition:.15s;font-size:15px}
.f__v:hover{border-color:var(--gold);background:#fff}
.f__v.copied{border-color:var(--gold);background:#F6EFDD}
.f__v i{color:#a89c8c}
.f2{display:grid;grid-template-columns:150px 1fr;gap:14px;margin-bottom:0}
footer{margin-top:34px;color:#8d8175;font-size:14px;border-top:1px solid var(--line);padding-top:18px}
@media(max-width:720px){.ad{grid-template-columns:1fr}.ad__pic img{width:100%;height:auto}
  .f2{grid-template-columns:1fr}}
'''


def build():
    up = {k: url for k, mid, code, url in json.load(open(os.path.join(HERE, '_uploads.json')))}
    rows = []
    for i, (k, h, d, price, link) in enumerate(CARDS, 1):
        img = up[k]
        price_html = html.escape(price) if price else '<i>оставить пустым</i>'
        rows.append(f'''
<article class="ad">
  <div class="ad__num">{i}</div>
  <div class="ad__pic">
    <img src="{img}" alt="" loading="lazy">
    <button class="ad__dl" data-dl="{img}" data-name="versal-{k}.jpg">Скачать картинку</button>
  </div>
  <div class="ad__body">
    <div class="f"><span class="f__k">Заголовок <em>{len(h)}/56</em></span>
      <div class="f__v" data-copy>{html.escape(h)}</div></div>
    <div class="f"><span class="f__k">Описание <em>{len(d)}/81</em></span>
      <div class="f__v" data-copy>{html.escape(d)}</div></div>
    <div class="f2">
      <div class="f"><span class="f__k">Цена</span>
        <div class="f__v" data-copy>{price_html}</div></div>
      <div class="f"><span class="f__k">Ссылка</span>
        <div class="f__v" data-copy>{SITE}{link}</div></div>
    </div>
  </div>
</article>''')

    doc = f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Объявления Яндекс.Бизнеса — Версаль</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Manrope:wght@400;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><div class="wrap">
<h1>Свои объявления Яндекс.Бизнеса — «Версаль»</h1>
<p class="sub">14 объявлений: заголовок, описание, цена, ссылка и картинка.
Клик по полю копирует текст, клик по картинке — скачивает.</p>
<div class="note">
  <b>Заливать снизу вверх</b> — с №14 к №1. Свежие объявления показываются первыми,
  поэтому самые сильные офферы (боль, КТ + план, имплант) должны попасть в кабинет последними.<br>
  <b>В поле «Цена» — только число.</b> «От» кабинет не принимает, а в заголовке цену
  не дублируем — она и так видна в карточке. Где цена может ввести в заблуждение
  (пародонтология: 800 ₽ — это за один зуб), поле оставляем пустым.<br>
  <b>Срок размещения не ставить</b> — объявления вечные, переделывать их не придётся.
</div>
{''.join(rows)}
<footer>Цены сверены с сайтом versal-dent.ru («Цены» и «Акции»). Изменилась цена на сайте —
поменяйте её в объявлении. Строка «Имеются противопоказания…» на картинках обязательна по
ч. 7 ст. 24 ФЗ «О рекламе» — не обрезайте нижнюю полосу.</footer>
</div>
<script>
// Скачивание по кнопке: атрибут download на чужой домен браузер игнорирует,
// поэтому тянем файл через fetch (CDN отдаёт Access-Control-Allow-Origin: *)
// и сохраняем blob под понятным именем. Если сеть/CORS подвели — открываем
// картинку в новой вкладке, чтобы кнопка не оказалась мёртвой.
document.querySelectorAll('[data-dl]').forEach(function(btn){{
  btn.addEventListener('click', function(){{
    var url = btn.dataset.dl, name = btn.dataset.name, txt = btn.textContent;
    btn.disabled = true; btn.textContent = 'Скачиваю…';
    fetch(url).then(function(r){{ return r.blob(); }}).then(function(b){{
      var u = URL.createObjectURL(b), a = document.createElement('a');
      a.href = u; a.download = name; document.body.appendChild(a); a.click();
      a.remove(); setTimeout(function(){{ URL.revokeObjectURL(u); }}, 4000);
      btn.textContent = 'Готово ✓';
      setTimeout(function(){{ btn.textContent = txt; btn.disabled = false; }}, 1400);
    }}).catch(function(){{
      window.open(url, '_blank');
      btn.textContent = txt; btn.disabled = false;
    }});
  }});
}});
document.querySelectorAll('[data-copy]').forEach(function(el){{
  el.addEventListener('click', function(){{
    navigator.clipboard.writeText(el.innerText.trim()).then(function(){{
      el.classList.add('copied');
      setTimeout(function(){{ el.classList.remove('copied'); }}, 900);
    }});
  }});
}});
</script>
</body></html>'''
    open(OUT, 'w', encoding='utf-8').write(doc)
    print('готово:', OUT)


if __name__ == '__main__':
    build()
