# -*- coding: utf-8 -*-
"""
Картинки для раздела «Свои объявления» Яндекс.Бизнеса — «Версаль».

Формат кабинета: минимум 650×650, поля «Заголовок» (≤56) и «Описание»
(≤81) — текст пишется В ПОЛЯХ, на картинку его класть НЕ надо (как в
витрине, в отличие от акций и публикаций).

Что делает скрипт: берёт кадры Higgsfield из `bg/`, режет в квадрат
1200×1200 и впечатывает обязательную по ч. 7 ст. 24 ФЗ «О рекламе»
строку о противопоказаниях (реклама медуслуг; закон требует отдать под
неё **не менее 5 % площади** — отсюда высота полосы 5,2 %).

⚠️ Водяного знака здесь НЕТ (решение владельца, 13.08.2026): в
объявлении бренд и так виден по домену в карточке, а знак поверх лица
удешевляет кадр. Знак остаётся в витрине, портфолио и Дзене.

⚠️ Кадры — только «живые», с лицами (решение владельца, 13.08.2026):
предметные макро (инструменты, коронка, модель челюсти с имплантом)
выглядели искусственно и не привлекали внимание. Лицо + естественная
эмоция работают лучше всего.

Тексты объявлений — в `TEXTS.md` (источник цен: сайт, ceny.html).

Запуск: python3 versal-ads.py
"""
from PIL import Image, ImageDraw, ImageFont
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(HERE, 'bg')
OUT = os.path.join(HERE, 'out')
FONTS = os.path.join(HERE, 'fonts')          # фирменный Manrope (Google Fonts)
os.makedirs(OUT, exist_ok=True)

SIDE = 1200
DISCLAIMER = 'Имеются противопоказания, необходима консультация специалиста'

# ключ → (файл фона, вертикальный акцент кропа: 0 — верх, 0.5 — центр)
SHOTS = [
    ('kariés',       '01-kariés.png',       0.42),
    ('kanaly',       '02-kanaly.png',       0.45),
    ('bol',          '03-bol.png',          0.45),
    ('mudrosti',     '04-mudrosti.png',     0.50),
    ('kt',           '05-kt.png',           0.45),
    ('cirkon',       '06-cirkon.png',       0.50),
    ('implant',      '07-implant.png',      0.50),
    ('allon4',       '08-allon4.png',       0.40),
    ('protez',       '09-protez.png',       0.40),
    ('brekety',      '10-brekety.png',      0.40),
    ('elaynery',     '11-elaynery.png',     0.50),
    ('otbelivanie',  '12-otbelivanie.png',  0.40),
    ('desny',        '13-desny.png',        0.45),
    ('restavraciya', '14-restavraciya.png', 0.45),
]


def square(im, focus=0.45):
    """кроп в квадрат с акцентом на верхнюю часть кадра (там лица)"""
    w, h = im.size
    if w > h:
        x = (w - h) // 2
        im = im.crop((x, 0, x + h, h))
    elif h > w:
        y = round((h - w) * focus)
        im = im.crop((0, y, w, y + w))
    return im.resize((SIDE, SIDE), Image.LANCZOS)


def disclaimer(im):
    """мелкая строка по нижнему краю на затемнённой подложке"""
    d = ImageDraw.Draw(im, 'RGBA')
    f = ImageFont.truetype(os.path.join(FONTS, 'Manrope[wght].ttf'), 21)
    f.set_variation_by_axes([450])
    tw = d.textlength(DISCLAIMER, font=f)
    bar = round(SIDE * 0.052)
    d.rectangle([0, SIDE - bar, SIDE, SIDE], fill=(44, 38, 32, 190))
    d.text(((SIDE - tw) / 2, SIDE - bar + (bar - 26) / 2), DISCLAIMER,
           font=f, fill=(252, 250, 246, 235))
    return im


if __name__ == '__main__':
    n = 0
    for key, src, focus in SHOTS:
        p = os.path.join(BG, src)
        if not os.path.exists(p):
            print('нет фона:', src); continue
        im = square(Image.open(p).convert('RGB'), focus)
        im = disclaimer(im)
        im.save(os.path.join(OUT, f'versal-ad-{key}.jpg'), quality=92, subsampling=0)
        n += 1
    print(f'готово: {n} картинок 1200×1200 в out/')
