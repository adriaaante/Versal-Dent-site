# -*- coding: utf-8 -*-
"""
Публикации Яндекс.Бизнеса — «Версаль». Картинки к постам.

Правила (общие с Angel, раздел «Публикации Яндекс.Бизнеса» в его CLAUDE.md):
публикация = новость клиники, вечная, только с реальными условиями с сайта;
однотипных баннеров не делаем — баннер-обложка только у офферного поста,
остальные идут «живыми» фото клиники. На всех — водяной знак (в отличие от
объявлений и фото карточки, где он запрещён/не нужен).

Источник кадров — РЕАЛЬНЫЕ фото клиники в репозитории
(`assets/img/clinic/*`, `assets/img/tehnologii/*`), поэтому генерировать
ничего не нужно: пост показывает настоящую клинику, а не сток.

Запуск: python3 versal-posts.py
"""
from PIL import Image, ImageDraw, ImageFont
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
IMG = os.path.join(ROOT, 'assets', 'img')
FONTS = os.path.join(HERE, '..', 'yb-ads', 'fonts')
OUT = os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)

GOLD, ESPRESSO, IVORY = (194, 161, 78), (44, 38, 32), (252, 250, 246)
W, H = 1600, 900                      # 16:9 — как показывает публикацию Яндекс
BANNER = (1800, 960)
WM_FRAC = 0.15

# пост → список исходных кадров
SHOTS = {
    'klinika':    ['clinic/clinic-4.webp', 'clinic/clinic-1.webp', 'clinic/clinic-3.webp'],
    'tehnologii': ['tehnologii/kt-3d.webp', 'tehnologii/skaner-3shape.webp',
                   'tehnologii/sterilizaciya.webp', 'tehnologii/dsd.webp'],
    'gigiena':    ['clinic/clinic-5.webp', 'clinic/clinic-6.webp'],
    'bol':        ['clinic/clinic-2.webp', 'clinic/clinic-7.webp'],
}
# офферный пост — с баннером-обложкой
BANNER_POST = ('ortodont', 'clinic/clinic-8.webp',
               'Консультация ортодонта — бесплатно',
               'Осмотр, расчёт ТРГ и план лечения без обязательств')


def wm(im):
    w = Image.open(os.path.join(IMG, 'watermark.png')).convert('RGBA')
    s = round(min(im.size) * WM_FRAC)
    w = w.resize((s, s), Image.LANCZOS)
    w.putalpha(w.split()[3].point(lambda v: round(v * 0.7)))
    pad = round(min(im.size) * 0.04)
    im.paste(w, (im.width - s - pad, im.height - s - pad), w)
    return im


def cover(path, size):
    im = Image.open(os.path.join(IMG, path)).convert('RGB')
    sc = max(size[0] / im.width, size[1] / im.height)
    im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    x, y = (im.width - size[0]) // 2, round((im.height - size[1]) * 0.4)
    return im.crop((x, y, x + size[0], y + size[1]))


def font(name, size, wght=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    if wght:
        f.set_variation_by_axes([wght])
    return f


def build_banner(key, shot, title, sub):
    """Обложка офферного поста: фото + тёмный градиент слева + текст."""
    im = cover(shot, BANNER)
    # градиент плотный: на светлом интерьере иначе не читается белый текст
    grad = Image.new('L', (BANNER[0], 1))
    for x in range(BANNER[0]):
        grad.putpixel((x, 0), max(0, min(255, int(252 - x / BANNER[0] * 268))))
    veil = Image.new('RGB', BANNER, ESPRESSO)
    im.paste(veil, (0, 0), grad.resize(BANNER))

    d = ImageDraw.Draw(im)
    # лого на белом чипе
    logo = Image.open(os.path.join(IMG, 'logo-mark.png')).convert('RGBA')
    ls = 96
    logo = logo.resize((ls, ls), Image.LANCZOS)
    d.rounded_rectangle([70, 62, 70 + ls + 34, 62 + ls + 22], 18, fill=(255, 255, 255))
    im.paste(logo, (70 + 17, 62 + 11), logo)
    d.text((70 + ls + 56, 78), 'ВЕРСАЛЬ', font=font('Manrope[wght].ttf', 34, 700), fill=IVORY)
    d.text((70 + ls + 56, 122), 'Стоматология · Реутов',
           font=font('Manrope[wght].ttf', 26, 400), fill=(214, 205, 188))

    d.text((70, 372), title, font=font('PlayfairDisplay.ttf', 76), fill=IVORY)
    d.text((70, 486), sub, font=font('Manrope[wght].ttf', 34, 400), fill=(226, 218, 202))
    # ⚠️ в Playfair нет глифа «₽» — цену пишем Manrope, иначе вместо знака квадрат
    d.text((70, 596), '0 ₽', font=font('Manrope[wght].ttf', 122, 700), fill=GOLD)
    d.text((70, 880), 'Имеются противопоказания, необходима консультация специалиста',
           font=font('Manrope[wght].ttf', 21, 400), fill=(190, 182, 168))
    wm(im).save(os.path.join(OUT, f'post-{key}-1.jpg'), quality=93, subsampling=0)


if __name__ == '__main__':
    n = 0
    for key, shots in SHOTS.items():
        for i, s in enumerate(shots, 1):
            wm(cover(s, (W, H))).save(os.path.join(OUT, f'post-{key}-{i}.jpg'),
                                      quality=92, subsampling=0)
            n += 1
    build_banner(*BANNER_POST)
    n += 1
    print(f'готово: {n} картинок в out/')
