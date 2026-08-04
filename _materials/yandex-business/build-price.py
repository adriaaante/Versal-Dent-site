#!/usr/bin/env python3
# Генератор прайса для Яндекс.Бизнеса (раздел «Товары и услуги»).
#
# ВАЖНО: источник цен — САЙТ (services/*.html, promotions.html). Этот файл
# синхронизируется ОТ сайта, не наоборот. Перед пересборкой свериться с
# актуальными ценами в прайс-таблицах services/*.html и акциями в
# promotions.html (см. README.md рядом).
#
# Запуск (из любой папки):  python3 _materials/yandex-business/build-price.py
# Результат:  _materials/yandex-business/versal-dent-yandex-business-price.xlsx
#
# Колонки под загрузку «Загрузить XLS/YML»: Название | Цена | Категория | Описание.
# Правила оформления:
#  - цену НЕ дублировать в названии (только в колонке «Цена»);
#  - «от …» и «вместо …» — в описании;
#  - бесплатное/подарочное — цена 0 (НЕ хак «1 ₽»);
#  - никаких просроченных дат акций.

import os, zipfile, html

# (Название, Цена(число или ""), Категория, Описание) — цены сверены с сайтом.
rows = [
 ("Имплант Osstem (Корея)",28000,"Имплантация","Установка импланта Osstem (Южная Корея) «под ключ». Опытный хирург-имплантолог. Гарантия 10 лет. Цена «от»."),
 ("Имплант Dentium (Корея)",32000,"Имплантация","Установка импланта Dentium (Южная Корея). КТ и план лечения бесплатно при заключении договора. Цена «от»."),
 ("Имплант Straumann (Швейцария)",55000,"Имплантация","Премиум-имплант Straumann (Швейцария). Гарантия 10 лет. Цена «от»."),
 ("Имплант + коронка металлокерамика «под ключ»",45000,"Имплантация","Имплантация с металлокерамической коронкой под ключ. Цена «от»."),
 ("Имплант + коронка цирконий «под ключ»",65000,"Имплантация","Имплантация с циркониевой коронкой под ключ. Цена «от»."),
 ("All-on-4 — несъёмный протез на 4 имплантах",120000,"Имплантация","Несъёмный протез всей челюсти на 4 имплантах. Цена «от», за одну челюсть."),
 ("All-on-6 — несъёмный протез на 6 имплантах",180000,"Имплантация","Несъёмный протез всей челюсти на 6 имплантах. Цена «от», за одну челюсть."),

 ("Брекеты под ключ",35000,"Ортодонтия","Металлические, керамические или сапфировые брекеты под ключ. Стаж ортодонта 15 лет. Цена «от»."),
 ("Элайнеры — полный курс",120000,"Ортодонтия","Прозрачные элайнеры, полный курс исправления прикуса. Цена «от»."),
 ("Бесплатная консультация ортодонта",0,"Ортодонтия","Первичная консультация ортодонта с расчётом ТРГ — бесплатно. Подберём брекеты или элайнеры."),

 ("Лечение кариеса",5500,"Лечение зубов","Лечение кариеса за одно посещение, анестезия включена. Цена «от»."),
 ("Лечение пульпита (1 канал)",7000,"Лечение зубов","Лечение пульпита одноканального зуба. Цена «от»."),
 ("Лечение каналов под микроскопом",12000,"Лечение зубов","Эндодонтическое лечение каналов под микроскопом. Цена «от»."),
 ("Художественная реставрация зуба",8000,"Лечение зубов","Эстетическая реставрация переднего зуба. Цена «от»."),

 ("Удаление зуба для взрослого",4500,"Хирургия","Удаление зуба для взрослого (простое и сложное), под анестезией. Цена «от»."),
 ("Удаление зуба мудрости (ретинированного)",9500,"Хирургия","Удаление ретинированного зуба мудрости опытным хирургом. Цена «от»."),
 ("Костная пластика (1 единица)",10000,"Хирургия","Наращивание костной ткани. Цена «от»."),
 ("Синус-лифтинг закрытый",18000,"Хирургия","Закрытый синус-лифтинг для имплантации на верхней челюсти. Цена «от»."),

 ("Коронка металлокерамика",12000,"Протезирование","Металлокерамическая коронка. Цена «от»."),
 ("Коронка цирконий монолит",22000,"Протезирование","Монолитная циркониевая коронка. Цена «от»."),
 ("Коронка E-max",28000,"Протезирование","Коронка из дисиликата лития E-max (эстетика). Цена «от»."),
 ("Съёмный протез акрил (1 челюсть)",28000,"Протезирование","Полный съёмный акриловый протез на одну челюсть. Цена «от»."),
 ("Бюгельный протез с замками",65000,"Протезирование","Бюгельный протез на замках. Цена «от»."),

 ("Винир керамический E-max",22000,"Виниры","Керамический винир E-max. Голливудская улыбка за 2 визита. Цена «от»."),
 ("Люминир Cerinate",38000,"Виниры","Ультратонкий люминир Cerinate без обточки. Цена «от»."),
 ("Композитный винир",7500,"Виниры","Композитный винир (прямая реставрация). Цена «от»."),
 ("Голливудская улыбка под ключ (10 виниров)",220000,"Виниры","Комплекс из 10 виниров E-max под ключ. Цена «от»."),

 ("Комплексная гигиена (ультразвук + Air Flow + полировка)",5000,"Гигиена","Профессиональная чистка зубов: ультразвук, Air Flow, полировка."),
 ("Комплексная гигиена с брекетами",7000,"Гигиена","Профессиональная чистка при установленной брекет-системе: ультразвук, Air Flow, полировка."),
 ("Комплексная гигиена с ретейнерами",6000,"Гигиена","Профессиональная чистка при установленных ретейнерах: ультразвук, Air Flow, полировка."),
 ("Чистка Air Flow",2500,"Гигиена","Чистка Air Flow — удаление налёта и пигмента."),
 ("Ультразвуковая гигиена",2500,"Гигиена","Снятие зубного камня ультразвуком."),
 ("Гигиена + чистка десневых карманов 3–4 мм (кюретаж)",7500,"Гигиена","Комплексная гигиена с глубоким кюретажем пародонтальных карманов 3–4 мм."),
 ("Гигиена + чистка десневых карманов от 5 мм (кюретаж)",9500,"Гигиена","Комплексная гигиена с глубоким кюретажем пародонтальных карманов от 5 мм."),
 ("Глубокое фторирование",1200,"Гигиена","Укрепление эмали всех зубов: фторирующий гель в каппах."),

 ("Лечение дёсен Vector (1 челюсть)",8500,"Лечение дёсен","Vector-терапия при пародонтите, 1 челюсть. Цена «от»."),
 ("Plasmolifting (1 пробирка)",4500,"Лечение дёсен","Плазмолифтинг дёсен, 1 пробирка. Цена «от»."),

 ("Лечение молочного зуба",1500,"Детская стоматология","Лечение кариеса молочного зуба у детей с 2 лет, в игровой форме. Цена «от»."),
 ("Цветная пломба Twinky Star",2800,"Детская стоматология","Лечение молочного зуба с цветной пломбой Twinky Star. Цена «от»."),
 ("Удаление молочного зуба",1650,"Детская стоматология","Удаление молочного зуба у детей, бережно и без стресса. Цена «от»."),
 ("Консультация детского стоматолога",1000,"Детская стоматология","Осмотр и план лечения у детского стоматолога."),

 ("Акция: КТ + план лечения",4200,"Акции","Вместо 7 500 ₽. КТ двух челюстей, осмотр главврача, письменный план с фиксированными ценами на 30 дней. При договоре на лечение — бесплатно."),
 ("Акция: отбеливание Amazing White",17500,"Акции","Вместо 25 000 ₽. Кабинетное отбеливание до 6–8 тонов за визит. Защита дёсен и реминерализация включены."),
 ("Акция: каждый 3-й имплант в подарок",0,"Акции","При установке нескольких имплантов каждый третий — бесплатно. Гарантия 10 лет."),
 ("Акция: чистка в подарок при имплантации или брекетах",0,"Акции","Профгигиена (Air Flow + ультразвук + полировка) в подарок при договоре на имплантацию или брекеты. Экономия 5 000 ₽."),
 ("Скидка 10% пенсионерам, многодетным и военнослужащим",0,"Акции","Скидка 10% на лечение, протезирование и гигиену по удостоверению. Действует постоянно."),
 ("Семейная программа — скидка 3–10%",0,"Акции","Скидка от 3% до 10% всем членам семьи при лечении 3 и более человек."),
]

HEADER = ["Название", "Цена", "Категория", "Описание"]

# Картинки для YML-фида: по одной сгенерированной фотографии на категорию,
# лежат в assets/img/yb/yb-<slug>.jpg (деплоятся вместе с сайтом). XLS-импорт
# YB колонку с фото НЕ поддерживает — картинки подключаются только через
# YML-фид (тег <picture>), см. README.md.
IMG_BASE = "https://versal-dent.ru/assets/img/yb/"
CAT_IMG = {
    "Имплантация": "yb-implantaciya",
    "Ортодонтия": "yb-ortodontiya",
    "Лечение зубов": "yb-terapiya",
    "Хирургия": "yb-hirurgiya",
    "Протезирование": "yb-protezirovanie",
    "Виниры": "yb-viniry",
    "Гигиена": "yb-gigiena",
    "Лечение дёсен": "yb-parodontologiya",
    "Детская стоматология": "yb-detskaya",
    "Акции": "yb-akcii",
}


def img_for(category):
    return IMG_BASE + CAT_IMG.get(category, "yb-akcii") + ".jpg"


# Ссылка на страницу товара (раздел сайта) — делает карточку кликабельной в
# Картах. С UTM, чтобы клики считались в Метрике (см. CLAUDE.md, цели Директа).
SITE = "https://versal-dent.ru/"
UTM = "?utm_source=yandex_business&utm_medium=tovary&utm_campaign=catalog"
CAT_URL = {
    "Имплантация": "services/implantaciya.html",
    "Ортодонтия": "services/ortodontiya.html",
    "Лечение зубов": "services/terapiya.html",
    "Хирургия": "services/hirurgiya.html",
    "Протезирование": "services/protezirovanie.html",
    "Виниры": "services/viniry.html",
    "Гигиена": "services/gigiena.html",
    "Лечение дёсен": "services/parodontologiya.html",
    "Детская стоматология": "services/detskaya.html",
    "Акции": "promotions.html",
}


def url_for(category):
    return SITE + CAT_URL.get(category, "services/") + UTM


def _esc(s):
    return html.escape(str(s), quote=False)


def _cell(ref, val):
    if isinstance(val, (int, float)):
        return f'<c r="{ref}"><v>{val}</v></c>'
    if val == "":
        return f'<c r="{ref}"/>'
    return f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{_esc(val)}</t></is></c>'


def _row(rn, vals):
    cells = "".join(_cell(f"{chr(ord('A')+i)}{rn}", v) for i, v in enumerate(vals))
    return f'<row r="{rn}">{cells}</row>'


def build(out_path):
    data = []
    for i, r in enumerate(rows, 2):
        name, price, cat, desc = r
        price = "" if price == 0 else price  # YB не принимает 0 как цену
        data.append(_row(i, [name, price, cat, desc]))
    sd = [_row(1, HEADER)] + data
    sheet = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
             '<cols><col min="1" max="1" width="60"/><col min="2" max="2" width="12"/>'
             '<col min="3" max="3" width="22"/><col min="4" max="4" width="75"/>'
             '<col min="5" max="5" width="55"/></cols>'
             '<sheetData>' + "".join(sd) + '</sheetData></worksheet>')
    ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
          '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
    wb = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
          '<sheets><sheet name="Прайс" sheetId="1" r:id="rId1"/></sheets></workbook>')
    wbrels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
              '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("xl/workbook.xml", wb)
        z.writestr("xl/_rels/workbook.xml.rels", wbrels)
        z.writestr("xl/worksheets/sheet1.xml", sheet)
    return len(rows)


def build_yml(out_path):
    """YML-фид для автозагрузки в Яндекс.Бизнес по ссылке (цены + картинки).
    Включаем только позиции с ценой — в YML <price> обязателен. Бесплатные и
    подарочные акции (цена пустая) в фид не идут: их место — раздел «Акции» в YB.
    """
    from datetime import datetime
    cats = list(CAT_IMG.keys())
    cat_id = {c: i + 1 for i, c in enumerate(cats)}
    cats_xml = "".join(
        f'<category id="{cat_id[c]}">{_esc(c)}</category>' for c in cats
    )
    offers = []
    oid = 0
    skipped = 0
    for name, price, cat, desc in rows:
        # YB не принимает 0/пустую цену — бесплатные/подарочные акции в фид не идут
        # (их место — раздел «Акции» карточки YB).
        if price == 0 or price == "" or price is None:
            skipped += 1
            continue
        oid += 1
        offers.append(
            f'<offer id="{oid}" available="true">'
            f'<name>{_esc(name)}</name>'
            f'<url>{_esc(url_for(cat))}</url>'
            f'<price>{price}</price><currencyId>RUB</currencyId>'
            f'<categoryId>{cat_id.get(cat, cat_id["Акции"])}</categoryId>'
            f'<picture>{_esc(img_for(cat))}</picture>'
            f'<description>{_esc(desc)}</description>'
            f'</offer>'
        )
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    yml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<yml_catalog date="{date}">\n<shop>\n'
        '<name>Версаль</name>\n'
        '<company>ООО «Версаль»</company>\n'
        '<url>https://versal-dent.ru/</url>\n'
        '<currencies><currency id="RUB" rate="1"/></currencies>\n'
        f'<categories>{cats_xml}</categories>\n'
        f'<offers>{"".join(offers)}</offers>\n'
        '</shop>\n</yml_catalog>\n'
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(yml)
    return oid, skipped


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(here, "..", ".."))

    out_xlsx = os.path.join(here, "versal-dent-yandex-business-price.xlsx")
    n = build(out_xlsx)
    print(f"XLSX: {out_xlsx} ({n} позиций)")

    out_yml = os.path.join(repo_root, "yandex-business.yml")
    o, sk = build_yml(out_yml)
    print(f"YML:  {out_yml} ({o} офферов с ценой, пропущено без цены: {sk})")
