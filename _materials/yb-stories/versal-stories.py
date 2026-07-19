"""Сторис ЯБ для «Версаль»: 1080×1920, премиум бежево-золотой стиль.
Playfair Display (заголовки) + Manrope (текст). Нижние ~220px — свободные
(там кнопка Яндекса). Лого в шапке каждого слайда."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import sys

S = Path(__file__).parent
W, H = 1080, 1920
IVORY = (252, 250, 246); SAND = (245, 238, 226); CREAM = (243, 236, 224)
GOLD = (194, 161, 78); GOLD_D = (168, 134, 58)
ESP = (44, 38, 32); ESP2 = (74, 63, 53); MUT = (124, 115, 103)
BORDER = (231, 221, 203); WHITE = (255, 255, 255)
VD = Path("/home/user/Versal-Dent-site")
LOGO = Image.open(VD / "assets/img/logo-mark.png").convert("RGBA")

def pf(size, weight=700):
    f = ImageFont.truetype(str(S / "fonts/PlayfairDisplay-var.ttf"), size)
    f.set_variation_by_axes([weight]); return f

def mr(size, weight=600):
    f = ImageFont.truetype(str(S / "fonts/Manrope-var.ttf"), size)
    f.set_variation_by_axes([weight]); return f

def rounded(img, rad):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, img.size[0]-1, img.size[1]-1], radius=rad, fill=255)
    out = img.convert("RGBA"); out.putalpha(m); return out

def header(img, dark_bg=False):
    """Бренд-шапка: лого на чипе + ВЕРСАЛЬ."""
    d = ImageDraw.Draw(img)
    ML, top, chip = 72, 64, 108
    d.rounded_rectangle([ML, top, ML+chip, top+chip], radius=28,
                        fill=WHITE if not dark_bg else (252, 250, 246))
    ls = LOGO.resize((chip-24, chip-24), Image.LANCZOS)
    img.paste(ls, (ML+12, top+12), ls)
    d = ImageDraw.Draw(img)
    tcol = IVORY if dark_bg else ESP
    scol = (216, 202, 176) if dark_bg else MUT
    d.text((ML+chip+30, top+8), "ВЕРСАЛЬ", font=pf(52, 700), fill=tcol)
    d.text((ML+chip+30, top+74), "Семейная стоматология · Реутов", font=mr(30, 600), fill=scol)
    return img

def gold_chip(d, img, x, y, text, size=40):
    f = mr(size, 800)
    tw = d.textlength(text, font=f); bb = d.textbbox((0, 0), text, font=f)
    h = size + 44
    d.rounded_rectangle([x, y, x+tw+72, y+h], radius=(size+44)//2, fill=GOLD)
    d.text((x+36, y+(h-(bb[3]-bb[1]))//2-bb[1]), text, font=f, fill=(30, 24, 12))
    return y + h

def vgrad(img, y0, y1, color, a0, a1, top_down=True):
    """Вертикальный градиент-плашка color с альфой a0→a1 на [y0,y1]."""
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    for y in range(y0, min(y1, img.size[1])):
        t = (y - y0) / max(1, (y1 - y0))
        dd.line([(0, y), (img.size[0], y)], fill=color + (int(a0 + (a1 - a0) * t),))
    return Image.alpha_composite(img.convert("RGBA"), ov)

def load_photo(path, crop=None):
    ph = Image.open(S / path).convert("RGB")
    if crop: ph = ph.crop(crop)
    return ph

def fit(ph, w, h):
    """cover-кроп по центру под w×h."""
    r = max(w / ph.width, h / ph.height)
    ph = ph.resize((int(ph.width * r) + 1, int(ph.height * r) + 1), Image.LANCZOS)
    x = (ph.width - w) // 2; y = (ph.height - h) // 2
    return ph.crop((x, y, x + w, y + h))

def save(img, out):
    img.convert("RGB").save(S / out, "JPEG", quality=92, optimize=True)
    print("built", out)

# ---------- типы слайдов ----------

def cover(out, photo, kicker, title_lines, sub_lines=(), title_size=104, ty=1280):
    img = fit(photo, W, H).convert("RGBA")
    img = vgrad(img, 0, 300, (42, 36, 30), 130, 0)              # верх под шапку
    img = vgrad(img, H - 1000, H, (42, 36, 30), 0, 235)          # низ под текст
    img = header(img, dark_bg=True)
    d = ImageDraw.Draw(img)
    ML = 72
    y = ty
    y = gold_chip(d, img, ML, y, kicker) + 34
    for t in title_lines:
        d.text((ML, y), t, font=pf(title_size, 800), fill=IVORY); y += title_size + 18
    y += 14
    for t in sub_lines:
        d.text((ML, y), t, font=mr(40, 600), fill=(226, 214, 192)); y += 56
    save(img, out)

def content(out, title_lines, cards, photo=None, photo_h=560, kicker=None,
            card_title_size=44, card_text_size=34):
    """Айвори-фон: опц. фото сверху (скруглённое), заголовок, карточки."""
    img = Image.new("RGBA", (W, H), IVORY)
    # мягкий песочный градиент сверху
    img = vgrad(img, 0, 420, (245, 238, 226), 255, 0)
    img = header(img)
    d = ImageDraw.Draw(img)
    ML = 72; y = 232
    if photo is not None:
        ph = rounded(fit(photo, W - 2 * ML, photo_h), 36)
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([ML+8, y+14, W-ML+8, y+photo_h+14],
                                             radius=36, fill=(74, 63, 53, 60))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(18)))
        img.paste(ph, (ML, y), ph)
        d = ImageDraw.Draw(img)
        y += photo_h + 56
    else:
        y += 40
    if kicker:
        y = gold_chip(d, img, ML, y, kicker) + 30
    for t in title_lines:
        d.text((ML, y), t, font=pf(76, 800), fill=ESP); y += 94
    d.line([ML, y+16, ML+140, y+16], fill=GOLD, width=6)
    y += 56
    for ct, cx in cards:
        lines = cx if isinstance(cx, (list, tuple)) else [cx]
        ch = 62 + len(lines) * (card_text_size + 14) + 30
        d.rounded_rectangle([ML, y, W - ML, y + ch], radius=28, fill=WHITE,
                            outline=BORDER, width=2)
        d.ellipse([ML+34, y+34, ML+58, y+58], fill=GOLD)
        d.text((ML+84, y+24), ct, font=mr(card_title_size, 800), fill=ESP)
        yy = y + 62 + 10
        for ln in lines:
            d.text((ML+84, yy), ln, font=mr(card_text_size, 600), fill=MUT)
            yy += card_text_size + 14
        y += ch + 26
    save(img, out)

def doctors_slide(out, title_lines, docs, note=None):
    """Три карточки врачей с реальными фото (4:5, айвори-градиент)."""
    img = Image.new("RGBA", (W, H), IVORY)
    img = vgrad(img, 0, 420, (245, 238, 226), 255, 0)
    img = header(img)
    d = ImageDraw.Draw(img)
    ML = 72; y = 250
    for t in title_lines:
        d.text((ML, y), t, font=pf(80, 800), fill=ESP); y += 98
    d.line([ML, y+14, ML+140, y+14], fill=GOLD, width=6)
    y += 60
    ch = 320
    for slug, name, role, extra in docs:
        d.rounded_rectangle([ML, y, W - ML, y + ch], radius=32, fill=WHITE,
                            outline=BORDER, width=2)
        ph = Image.open(VD / f"assets/img/doctors/{slug}.webp").convert("RGB")
        pw = int(ch * 0.8)
        ph = rounded(fit(ph, pw, ch - 40), 24)
        img.paste(ph, (ML + 24, y + 20), ph)
        d = ImageDraw.Draw(img)
        tx = ML + 24 + pw + 36
        d.text((tx, y + 44), name, font=pf(46, 800), fill=ESP)
        d.text((tx, y + 116), role, font=mr(33, 700), fill=GOLD_D)
        yy = y + 172
        for ln in extra:
            d.text((tx, yy), ln, font=mr(30, 600), fill=MUT); yy += 42
        y += ch + 28
    if note:
        d.text((ML, y + 6), note, font=mr(30, 600), fill=MUT)
    save(img, out)

def steps_slide(out, title_lines, steps, foot=None):
    img = Image.new("RGBA", (W, H), IVORY)
    img = vgrad(img, 0, 420, (245, 238, 226), 255, 0)
    img = header(img)
    d = ImageDraw.Draw(img)
    ML = 72; y = 252
    for t in title_lines:
        d.text((ML, y), t, font=pf(80, 800), fill=ESP); y += 98
    d.line([ML, y+14, ML+140, y+14], fill=GOLD, width=6)
    y += 64
    n = len(steps)
    for i, (st, sx) in enumerate(steps):
        lines = sx if isinstance(sx, (list, tuple)) else [sx]
        ch = 66 + len(lines) * 46 + 26
        # линия-коннектор
        if i < n - 1:
            d.line([ML+44, y+44, ML+44, y+ch+30+44], fill=(216, 202, 176), width=4)
        d.ellipse([ML+10, y+10, ML+78, y+78], fill=GOLD)
        f_n = mr(40, 800); num = str(i+1)
        bb = d.textbbox((0, 0), num, font=f_n)
        d.text((ML+44-(bb[2]-bb[0])/2-bb[0], y+44-(bb[3]-bb[1])/2-bb[1]), num,
               font=f_n, fill=(30, 24, 12))
        d.text((ML+110, y+8), st, font=mr(44, 800), fill=ESP)
        yy = y + 70
        for ln in lines:
            d.text((ML+110, yy), ln, font=mr(33, 600), fill=MUT); yy += 46
        y += ch + 30
    if foot:
        d.rounded_rectangle([ML, y+10, W-ML, y+10+100], radius=26, fill=SAND)
        d.ellipse([ML+34, y+10+40, ML+54, y+10+60], fill=GOLD)
        d.text((ML+80, y+10+31), foot, font=mr(33, 700), fill=ESP2)
    save(img, out)

def cta(out, photo, title_lines, sub_lines, btn="Записаться", disclaimer=False):
    """CTA: фото сверху, айвори-панель, стрелка к кнопке Яндекса внизу."""
    img = Image.new("RGBA", (W, H), IVORY)
    ph = fit(photo, W, 900).convert("RGBA")
    ph = vgrad(ph, 0, 260, (42, 36, 30), 120, 0)
    # плавный переход фото -> айвори
    fade = Image.new("L", (1, 260), 0)
    for i in range(260): fade.putpixel((0, i), int(255 * (i / 259)))
    fade = fade.resize((W, 260))
    ivory_strip = Image.new("RGBA", (W, 260), IVORY); ivory_strip.putalpha(fade)
    ph.alpha_composite(ivory_strip, (0, 900 - 260))
    img.paste(ph, (0, 0))
    img = header(img, dark_bg=True)
    d = ImageDraw.Draw(img)
    ML = 72; y = 960
    for t in title_lines:
        d.text((ML, y), t, font=pf(88, 800), fill=ESP); y += 106
    d.line([ML, y+14, ML+140, y+14], fill=GOLD, width=6)
    y += 58
    for t in sub_lines:
        d.text((ML, y), t, font=mr(40, 600), fill=ESP2); y += 58
    # кнопка-подсказка
    y = max(y + 40, 1470)
    f_b = mr(46, 800); tw = d.textlength(btn, font=f_b)
    bx0 = (W - (tw + 140)) / 2
    d.rounded_rectangle([bx0, y, bx0 + tw + 140, y + 110], radius=55, fill=GOLD)
    bb = d.textbbox((0, 0), btn, font=f_b)
    d.text((bx0 + 70, y + (110 - (bb[3]-bb[1])) / 2 - bb[1]), btn, font=f_b, fill=(30, 24, 12))
    hint = "жмите кнопку ниже ↓"
    f_h = mr(34, 700); hw = d.textlength(hint, font=f_h)
    d.text(((W - hw) / 2, y + 140), hint, font=f_h, fill=MUT)
    if disclaimer:
        f_d = mr(24, 500)
        dt = "Имеются противопоказания, необходима консультация специалиста"
        dw = d.textlength(dt, font=f_d)
        d.text(((W - dw) / 2, y + 196), dt, font=f_d, fill=(160, 150, 136))
    save(img, out)
