#!/usr/bin/env python3
"""Generates favicons / apple-touch-icon from assets/img/logo.png.

Apple-touch-icon (180×180) — белый лого на фирменном синем #1e5fb3
(= `--c-primary` и `<meta name="theme-color">`): на айфоне в Home Screen
это выглядит как полноценная иконка приложения, а не PNG с прозрачным
фоном (иначе iOS подкладывает белый и обрезает).

Остальные favicon (16/32/48/192/512 + .ico) — синий лого на светлом
фирменном фоне #eaf2fc (= `--c-primary-50`): хорошо читается во вкладке
браузера, на закладках и в результатах поиска.

Лого асимметричное (зуб слева + крыло справа), bbox-центрирование
даёт перекос — поэтому маска квадратно обрезается вокруг центроида
(центра массы непрозрачных пикселей), чтобы зуб ровно стоял в центре.

Запуск из корня репо: `python3 scripts/build-favicons.py`.
"""
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "img" / "logo.png"
OUT_DIR = ROOT / "assets" / "img"

PRIMARY = (194, 161, 78, 255)    # #C2A14E — золото (заливка лого)
PRIMARY_50 = (74, 63, 53, 255)   # #4A3F35 — эспрессо (фон иконки)
WHITE = (255, 255, 255, 255)

LOGO_RATIO = 1.0  # доля канваса, занимаемая центроид-маской

# (filename, size, background, fill) — генерируем только то, на что
# реально ссылаются HTML-страницы. 48px остаётся внутри favicon.ico.
TARGETS = [
    ("favicon-16.png",  16,  PRIMARY_50, PRIMARY),
    ("favicon-32.png",  32,  PRIMARY_50, PRIMARY),
    ("favicon-180.png", 180, PRIMARY_50, PRIMARY),   # apple-touch-icon
]


def load_logo_mask() -> Image.Image:
    """Квадратная alpha-маска с центроидом лого в центре квадрата.
    Прозрачные поля добавляются с «лёгкого» края, чтобы при заливке на
    весь канвас визуальный центр массы попал в центр иконки."""
    logo = Image.open(SRC).convert("RGBA")
    alpha = logo.split()[-1]
    bbox = alpha.getbbox()
    if not bbox:
        return alpha
    x0, y0, x1, y1 = bbox
    px = alpha.load()
    total = sx = sy = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            v = px[x, y]
            if v > 30:
                sx += x * v
                sy += y * v
                total += v
    cx, cy = sx / total, sy / total
    r = int(max(cx - x0, x1 - cx, cy - y0, y1 - cy)) + 1
    canvas = Image.new("L", (2 * r, 2 * r), 0)
    src = (int(cx - r), int(cy - r), int(cx + r), int(cy + r))
    sx0, sy0 = max(src[0], 0), max(src[1], 0)
    sx1, sy1 = min(src[2], alpha.width), min(src[3], alpha.height)
    crop = alpha.crop((sx0, sy0, sx1, sy1))
    canvas.paste(crop, (sx0 - src[0], sy0 - src[1]))
    return canvas


def render(size: int, mask_src: Image.Image, bg, fill) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), bg)
    target = int(size * LOGO_RATIO)
    mask = ImageOps.contain(mask_src, (target, target), Image.LANCZOS)
    fg = Image.new("RGBA", mask.size, fill)
    fg.putalpha(mask)
    pos = ((size - mask.width) // 2, (size - mask.height) // 2)
    canvas.alpha_composite(fg, pos)
    return canvas


def main() -> None:
    mask = load_logo_mask()
    for name, size, bg, fill in TARGETS:
        img = render(size, mask, bg, fill)
        img.save(OUT_DIR / name, "PNG", optimize=True)
        print(f"  {name}  {size}x{size}")

    ico_sizes = [16, 32, 48]
    ico_imgs = [render(s, mask, PRIMARY_50, PRIMARY).convert("RGBA")
                for s in ico_sizes]
    ico_imgs[0].save(
        OUT_DIR / "favicon.ico",
        format="ICO",
        sizes=[(s, s) for s in ico_sizes],
        append_images=ico_imgs[1:],
    )
    print("  favicon.ico  16/32/48")


if __name__ == "__main__":
    main()
