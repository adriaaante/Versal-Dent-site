"""Акции ЯБ Версаля, формат «full-bleed» (процесс Angel, стиль Версаля):
фото на весь холст 1800×960 (мин. ЯБ 900×480), слева эспрессо-градиент,
текст поверх: Playfair (заголовки) + Manrope, выгода золотом, лого-чип.
Исходники фото кладём рядом (photos/*.png, soul_2 16:9, человек справа)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

S = Path(__file__).parent
W, H = 1800, 960
ESPRESSO = (44, 38, 32)          # #2C2620
GOLD = (194, 161, 78)            # #C2A14E
IVORY = (232, 224, 210)
IVORY_DIM = (205, 194, 176)
logo = Image.open(S / "../../assets/img/logo-mark.png").convert("RGBA")


def font_m(size, weight):
    f = ImageFont.truetype(str(S / "fonts/Manrope-var.ttf"), size)
    f.set_variation_by_axes([weight])
    return f


def font_p(size, weight=700):
    f = ImageFont.truetype(str(S / "fonts/PlayfairDisplay-var.ttf"), size)
    f.set_variation_by_axes([weight])
    return f


def make(out, photo_path, badge, title_lines, big, sub_lines,
         old_price=None, grad_end=1140, title_size=86, crop_y=0.4):
    photo = Image.open(S / photo_path).convert("RGB")
    # 2048×1152 -> кроп под 1800×960 (15:8)
    cw, ch = photo.width, int(photo.width * H / W)
    y0 = int((photo.height - ch) * crop_y)
    ph = photo.crop((0, y0, cw, y0 + ch)).resize((W, H), Image.LANCZOS)
    img = ph.convert("RGBA")

    grad = Image.new("L", (W, 1), 0)
    gd = ImageDraw.Draw(grad)
    for x in range(W):
        if x < 600:
            a = int(250 - 30 * (x / 600))
        elif x < grad_end:
            a = int(225 * (1 - (x - 600) / (grad_end - 600)))
        else:
            a = 0
        gd.point((x, 0), fill=a)
    grad = grad.resize((W, H))
    tint = Image.new("RGBA", (W, H), ESPRESSO + (0,))
    tint.putalpha(grad)
    img = Image.alpha_composite(img, tint)
    d = ImageDraw.Draw(img)
    ML = 72

    # лого на белом чипе + бренд-строка
    chip = 96
    d.rounded_rectangle([ML, 52, ML + chip, 52 + chip], radius=26, fill=(255, 255, 255, 255))
    ls = logo.resize((chip - 20, chip - 20), Image.LANCZOS)
    img.paste(ls, (ML + 10, 62), ls)
    d = ImageDraw.Draw(img)
    d.text((ML + chip + 26, 56), "ВЕРСАЛЬ", font=font_m(40, 800), fill=(255, 255, 255))
    d.text((ML + chip + 26, 106), "Стоматология · Реутов", font=font_m(29, 600), fill=IVORY_DIM)

    # бейдж золотом
    f_b = font_m(48, 800)
    bb = d.textbbox((0, 0), badge, font=f_b)
    bw = d.textlength(badge, font=f_b)
    by0, bh = 224, 94
    d.rounded_rectangle([ML, by0, ML + bw + 84, by0 + bh], radius=47, fill=GOLD)
    d.text((ML + 42, by0 + (bh - (bb[3] - bb[1])) // 2 - bb[1]), badge, font=f_b, fill=(38, 30, 12))

    # заголовок — Playfair
    ty = 368
    for t in title_lines:
        d.text((ML, ty), t, font=font_p(title_size, 700), fill=(255, 255, 255))
        ty += title_size + 18

    # выгода крупно золотом + зачёркнутая старая цена
    ty += 22
    f_big = font_m(138, 800)
    d.text((ML, ty), big, font=f_big, fill=GOLD)
    if old_price:
        f_old = font_m(56, 600)
        ow = d.textlength(old_price, font=f_old)
        ox, oy = ML + d.textlength(big, font=f_big) + 42, ty + 74
        d.text((ox, oy), old_price, font=f_old, fill=IVORY_DIM)
        d.line([ox - 5, oy + 38, ox + ow + 5, oy + 38], fill=IVORY_DIM, width=6)
    ty += 196
    for t in sub_lines:
        d.text((ML, ty), t, font=font_m(42, 600), fill=IVORY)
        ty += 58

    d.text((ML, 898), "Имеются противопоказания, необходима консультация специалиста",
           font=font_m(26, 500), fill=(168, 158, 142))
    img.convert("RGB").save(S / out, "JPEG", quality=90, optimize=True)
    print("built", out)


CARDS = {
    "kt": dict(out="yb-akcia-v1-kt-plan.jpg", photo_path="photos/kt.png",
        badge="−44%", title_lines=["КТ + план лечения"], big="4 200 ₽", old_price="7 500 ₽",
        sub_lines=["Томография двух челюстей, осмотр", "и план с фиксированными ценами"]),
    "aw": dict(out="yb-akcia-v2-amazing-white.jpg", photo_path="photos/aw.png",
        badge="−30%", title_lines=["Отбеливание", "Amazing White"], big="17 500 ₽", old_price="25 000 ₽",
        sub_lines=["До 6–8 тонов светлее за один визит,", "обе челюсти «под ключ»"], title_size=80),
    "ortodont": dict(out="yb-akcia-v3-ortodont.jpg", photo_path="photos/ortodont.png",
        badge="Бесплатно", title_lines=["Консультация", "ортодонта"], big="0 ₽", old_price="1 000 ₽",
        sub_lines=["Первичный приём с расчётом ТРГ —", "подберём брекеты или элайнеры"], title_size=80),
    "implant": dict(out="yb-akcia-v4-implant.jpg", photo_path="photos/implant.png",
        badge="Подарок", title_lines=["Каждый 3-й имплант", "в подарок"], big="−1 из 3",
        sub_lines=["При установке нескольких имплантатов.", "Гарантия до 10 лет по договору"], title_size=76),
    "chistka": dict(out="yb-akcia-v5-chistka.jpg", photo_path="photos/chistka.png",
        badge="Подарок", title_lines=["Чистка в подарок"], big="0 ₽", old_price="5 000 ₽",
        sub_lines=["При заключении договора", "на имплантацию или брекеты"]),
    "lgoty": dict(out="yb-akcia-v6-lgoty.jpg", photo_path="photos/lgoty.png",
        badge="−10%", title_lines=["Пенсионерам", "и многодетным"], big="−10%",
        sub_lines=["А также военнослужащим и их семьям —", "на лечение, протезирование и гигиену"], title_size=78),
    "semya": dict(out="yb-akcia-v7-semya.jpg", photo_path="photos/semya.png",
        badge="Семейная", title_lines=["Семейная программа"], big="−3…10%",
        sub_lines=["Скидка всем членам семьи", "при лечении трёх и более человек"], title_size=76),
}

if __name__ == "__main__":
    import sys
    keys = sys.argv[1:] or CARDS.keys()
    for k in keys:
        make(**CARDS[k])
