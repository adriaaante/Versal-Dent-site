"""Сторис ЯБ для «Версаль»: 1080×1920, премиум бежево-золотой стиль. v2.
Playfair Display (заголовки) + Manrope (текст). Нижние ~200px — свободные
(кнопка Яндекса). Лого в шапке каждого слайда. Плотная вертикальная
композиция: контент заканчивается ~1700, без пустых «дыр»."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

S = Path(__file__).parent
W, H = 1080, 1920
ML = 72
IVORY = (252, 250, 246); SAND = (245, 238, 226); CREAM = (243, 236, 224)
GOLD = (194, 161, 78); GOLD_D = (168, 134, 58)
ESP = (44, 38, 32); ESP2 = (74, 63, 53); MUT = (124, 115, 103)
BORDER = (231, 221, 203); WHITE = (255, 255, 255)
VD = Path("/home/user/Versal-Dent-site")
LOGO = Image.open(VD / "assets/img/logo-mark.png").convert("RGBA")
GEO = "Реутов, ул. Победы, 22 · м. Новокосино · 10:00–20:00"
DISC = "Имеются противопоказания, необходима консультация специалиста"

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
    d = ImageDraw.Draw(img)
    top, chip = 64, 108
    d.rounded_rectangle([ML, top, ML+chip, top+chip], radius=28, fill=WHITE)
    ls = LOGO.resize((chip-24, chip-24), Image.LANCZOS)
    img.paste(ls, (ML+12, top+12), ls)
    d = ImageDraw.Draw(img)
    tcol = IVORY if dark_bg else ESP
    scol = (222, 210, 188) if dark_bg else MUT
    d.text((ML+chip+30, top+8), "ВЕРСАЛЬ", font=pf(52, 700), fill=tcol)
    d.text((ML+chip+30, top+74), "Семейная стоматология · Реутов", font=mr(30, 600), fill=scol)
    return img

def gold_chip(d, x, y, text, size=42):
    f = mr(size, 800)
    tw = d.textlength(text, font=f); bb = d.textbbox((0, 0), text, font=f)
    h = size + 46
    d.rounded_rectangle([x, y, x+tw+76, y+h], radius=h//2, fill=GOLD)
    d.text((x+38, y+(h-(bb[3]-bb[1]))//2-bb[1]), text, font=f, fill=(30, 24, 12))
    return y + h

def geo_strip(img, y=1596):
    """Нижняя фирменная полоса-якорь: адрес и график."""
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([ML, y, W-ML, y+104], radius=26, fill=SAND)
    f = mr(31, 700)
    tw = d.textlength(GEO, font=f)
    d.ellipse([ML+34, y+42, ML+54, y+62], fill=GOLD)
    d.text((ML+76 + (W-2*ML-110-tw)/2, y+34), GEO, font=f, fill=ESP2)
    return img

def vgrad(img, y0, y1, color, a0, a1):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    for y in range(max(0, y0), min(y1, img.size[1])):
        t = (y - y0) / max(1, (y1 - y0))
        dd.line([(0, y), (img.size[0], y)], fill=color + (int(a0 + (a1 - a0) * t),))
    return Image.alpha_composite(img.convert("RGBA"), ov)

def fit(ph, w, h, focus=0.5, hfocus=0.5):
    """cover-кроп под w×h; focus/hfocus — акцент по вертикали/горизонтали (0..1)."""
    r = max(w / ph.width, h / ph.height)
    ph = ph.resize((int(ph.width * r) + 1, int(ph.height * r) + 1), Image.LANCZOS)
    x = int((ph.width - w) * hfocus)
    y = int((ph.height - h) * focus)
    return ph.crop((x, y, x + w, y + h))

def save(img, out):
    img.convert("RGB").save(S / out, "JPEG", quality=92, optimize=True)
    print("built", out)

def shadow_paste(img, ph, x, y, rad=36):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([x+8, y+14, x+ph.width+8, y+ph.height+14],
                                         radius=rad, fill=(74, 63, 53, 60))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(16)))
    img.paste(ph, (x, y), ph)
    return img

# ---------- слайды ----------

def cover(out, photo, kicker, title_lines, sub_lines=(), title_size=110,
          focus=0.5, hfocus=0.5, chips=()):
    img = fit(photo, W, H, focus, hfocus).convert("RGBA")
    img = vgrad(img, 0, 320, (42, 36, 30), 135, 0)
    img = vgrad(img, H - 1050, H, (42, 36, 30), 0, 240)
    img = header(img, dark_bg=True)
    d = ImageDraw.Draw(img)
    n_sub = len(sub_lines)
    block = 88 + 34 + len(title_lines)*(title_size+16) + (18 + n_sub*58 if n_sub else 0) \
            + (34 + 72 if chips else 0)
    y = 1700 - block
    y = gold_chip(d, ML, y, kicker) + 34
    for t in title_lines:
        d.text((ML, y), t, font=pf(title_size, 800), fill=IVORY); y += title_size + 16
    if sub_lines:
        y += 18
        for t in sub_lines:
            d.text((ML, y), t, font=mr(42, 600), fill=(230, 219, 198)); y += 58
    if chips:
        y += 34
        x = ML
        f = mr(30, 700)
        for c in chips:
            tw = d.textlength(c, font=f)
            d.rounded_rectangle([x, y, x+tw+52, y+64], radius=32,
                                outline=(214, 198, 164), width=3)
            d.text((x+26, y+15), c, font=f, fill=(238, 229, 210))
            x += tw + 52 + 20
    save(img, out)

def content(out, title_lines, cards, photo=None, photo_h=600, focus=0.5,
            card_title=46, card_text=36, disclaimer=False, strip=True):
    img = Image.new("RGBA", (W, H), IVORY)
    img = vgrad(img, 0, 430, SAND, 255, 0)
    img = header(img)
    d = ImageDraw.Draw(img)
    y = 236
    if photo is not None:
        ph = rounded(fit(photo, W - 2*ML, photo_h, focus), 36)
        img = shadow_paste(img, ph, ML, y)
        d = ImageDraw.Draw(img)
        y += photo_h + 54
    else:
        y += 34
    for t in title_lines:
        d.text((ML, y), t, font=pf(80, 800), fill=ESP); y += 98
    d.line([ML, y+14, ML+150, y+14], fill=GOLD, width=6)
    y += 58
    # распределяем карточки так, чтобы блок закончился у гео-полосы
    strip_y = 1596 if strip else 1700
    lines_cnt = [len(cx) if isinstance(cx, (list, tuple)) else 1 for _, cx in cards]
    base_h = [66 + n*(card_text+14) + 28 for n in lines_cnt]
    total = sum(base_h)
    gap = max(24, min(44, (strip_y - 36 - y - total) // max(1, len(cards)-0) ))
    for (ct, cx), chh in zip(cards, base_h):
        lines = cx if isinstance(cx, (list, tuple)) else [cx]
        d.rounded_rectangle([ML, y, W-ML, y+chh], radius=28, fill=WHITE,
                            outline=BORDER, width=2)
        d.ellipse([ML+36, y+36, ML+62, y+62], fill=GOLD)
        d.text((ML+92, y+26), ct, font=mr(card_title, 800), fill=ESP)
        yy = y + 66 + 12
        for ln in lines:
            d.text((ML+92, yy), ln, font=mr(card_text, 600), fill=MUT)
            yy += card_text + 14
        y += chh + gap
    if strip:
        img = geo_strip(img)
        d = ImageDraw.Draw(img)
    if disclaimer:
        f = mr(24, 500); tw = d.textlength(DISC, font=f)
        d.text(((W-tw)/2, 1726), DISC, font=f, fill=(168, 158, 144))
    save(img, out)

def doctors_slide(out, title_lines, docs, note=None):
    img = Image.new("RGBA", (W, H), IVORY)
    img = vgrad(img, 0, 430, SAND, 255, 0)
    img = header(img)
    d = ImageDraw.Draw(img)
    y = 244
    for t in title_lines:
        d.text((ML, y), t, font=pf(84, 800), fill=ESP); y += 102
    d.line([ML, y+14, ML+150, y+14], fill=GOLD, width=6)
    y += 62
    ch = 356
    for slug, name, role, extra in docs:
        d.rounded_rectangle([ML, y, W-ML, y+ch], radius=32, fill=WHITE,
                            outline=BORDER, width=2)
        ph = Image.open(VD / f"assets/img/doctors/{slug}.webp").convert("RGB")
        pw = int((ch-44) * 0.8)
        ph = rounded(fit(ph, pw, ch-44), 24)
        img.paste(ph, (ML+26, y+22), ph)
        d = ImageDraw.Draw(img)
        tx = ML + 26 + pw + 40
        d.text((tx, y+52), name, font=pf(50, 800), fill=ESP)
        d.text((tx, y+130), role, font=mr(35, 700), fill=GOLD_D)
        yy = y + 196
        for ln in extra:
            d.text((tx, yy), ln, font=mr(32, 600), fill=MUT); yy += 46
        y += ch + 30
    if note:
        f = mr(32, 700); tw = d.textlength(note, font=f)
        d.text(((W-tw)/2, y+14), note, font=f, fill=MUT)
    save(img, out)

def steps_slide(out, title_lines, steps, foot=None, disclaimer=False):
    img = Image.new("RGBA", (W, H), IVORY)
    img = vgrad(img, 0, 430, SAND, 255, 0)
    img = header(img)
    d = ImageDraw.Draw(img)
    y = 244
    for t in title_lines:
        d.text((ML, y), t, font=pf(84, 800), fill=ESP); y += 102
    d.line([ML, y+14, ML+150, y+14], fill=GOLD, width=6)
    y += 66
    n = len(steps)
    foot_y = 1560
    row_h = (foot_y - 40 - y) // n
    for i, (st, sx) in enumerate(steps):
        if i < n-1:
            d.line([ML+46, y+50, ML+46, y+row_h+50], fill=(216, 202, 176), width=4)
        d.ellipse([ML+8, y+8, ML+84, y+84], fill=GOLD)
        f_n = mr(42, 800); num = str(i+1)
        bb = d.textbbox((0, 0), num, font=f_n)
        d.text((ML+46-(bb[2]-bb[0])/2-bb[0], y+46-(bb[3]-bb[1])/2-bb[1]), num,
               font=f_n, fill=(30, 24, 12))
        d.text((ML+120, y+4), st, font=mr(47, 800), fill=ESP)
        d.text((ML+120, y+72), sx, font=mr(35, 600), fill=MUT)
        y += row_h
    if foot:
        d.rounded_rectangle([ML, foot_y, W-ML, foot_y+104], radius=26, fill=SAND)
        f = mr(33, 800); tw = d.textlength(foot, font=f)
        d.ellipse([ML+34, foot_y+42, ML+54, foot_y+62], fill=GOLD)
        d.text((ML+76 + (W-2*ML-110-tw)/2, foot_y+32), foot, font=f, fill=ESP2)
    if disclaimer:
        f = mr(24, 500); tw = d.textlength(DISC, font=f)
        d.text(((W-tw)/2, 1700), DISC, font=f, fill=(168, 158, 144))
    save(img, out)

def cta(out, photo, title_lines, sub_lines, btn="Записаться", chips=(),
        focus=0.5, hfocus=0.5, disclaimer=False):
    img = Image.new("RGBA", (W, H), IVORY)
    ph = fit(photo, W, 950, focus, hfocus).convert("RGBA")
    ph = vgrad(ph, 0, 280, (42, 36, 30), 125, 0)
    fade = Image.new("L", (1, 240), 0)
    for i in range(240): fade.putpixel((0, i), int(255*(i/239)))
    fade = fade.resize((W, 240))
    strip = Image.new("RGBA", (W, 240), IVORY); strip.putalpha(fade)
    ph.alpha_composite(strip, (0, 950-240))
    img.paste(ph, (0, 0))
    img = header(img, dark_bg=True)
    d = ImageDraw.Draw(img)
    y = 990
    for t in title_lines:
        d.text((ML, y), t, font=pf(92, 800), fill=ESP); y += 110
    d.line([ML, y+12, ML+150, y+12], fill=GOLD, width=6)
    y += 54
    for t in sub_lines:
        d.text((ML, y), t, font=mr(41, 600), fill=ESP2); y += 58
    if chips:
        y += 22
        x = ML
        f = mr(30, 700)
        for c in chips:
            tw = d.textlength(c, font=f)
            d.rounded_rectangle([x, y, x+tw+52, y+64], radius=32, fill=SAND)
            d.text((x+26, y+15), c, font=f, fill=ESP2)
            x += tw + 52 + 18
    # кнопка
    by = 1500
    f_b = mr(48, 800); tw = d.textlength(btn, font=f_b)
    bw = max(tw + 160, 560)
    bx0 = (W - bw) / 2
    d.rounded_rectangle([bx0, by, bx0+bw, by+116], radius=58, fill=GOLD)
    bb = d.textbbox((0, 0), btn, font=f_b)
    d.text(((W-tw)/2, by+(116-(bb[3]-bb[1]))/2-bb[1]), btn, font=f_b, fill=(30, 24, 12))
    hint = "жмите кнопку ниже ↓"
    f_h = mr(34, 700); hw = d.textlength(hint, font=f_h)
    d.text(((W-hw)/2, by+146), hint, font=f_h, fill=MUT)
    if disclaimer:
        f = mr(24, 500); dw = d.textlength(DISC, font=f)
        d.text(((W-dw)/2, by+206), DISC, font=f, fill=(168, 158, 144))
    save(img, out)
