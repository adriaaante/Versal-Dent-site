"""Витрина ЯБ Версаль: миниатюры 1200×1200 БЕЗ текста, золото-айвори гамма,
водяной знак клиники (32% ширины, правый нижний, op 0.78, тёмный halo)."""
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path

S = Path(__file__).parent
OUT = 1200
WM = Image.open("/home/user/Versal-Dent-site/assets/img/watermark.png").convert("RGBA")
WM_RATIO, WM_MARGIN, WM_OP, SH_OP, SH_BLUR = 0.32, 0.03, 0.78, 0.55, 0.014

def watermark(img):
    tw = int(img.width * WM_RATIO); scale = tw / WM.width; th = int(WM.height * scale)
    wm = WM.resize((tw, th), Image.LANCZOS)
    a = wm.split()[3].point(lambda p: int(p * WM_OP)); wm.putalpha(a)
    m = int(img.width * WM_MARGIN)
    pos = (img.width - tw - m, img.height - th - m)
    br = max(2, int(tw * SH_BLUR)); pad = br * 4
    sa = wm.split()[3].point(lambda p: int(p * SH_OP))
    sh = Image.new("RGBA", (tw + pad*2, th + pad*2), (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", wm.size, (0, 0, 0, 255)), (pad, pad), sa)
    sh = sh.filter(ImageFilter.GaussianBlur(br))
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer.paste(sh, (pos[0]-pad, pos[1]-pad), sh)
    layer.paste(wm, pos, wm)
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def make(out, src, crop=None):
    im = Image.open(S / src).convert("RGB")
    if crop: im = im.crop(crop)
    # квадрат по центру
    side = min(im.size)
    x = (im.width - side)//2; y = (im.height - side)//2
    im = im.crop((x, y, x+side, y+side)).resize((OUT, OUT), Image.LANCZOS)
    watermark(im).save(S / out, "JPEG", quality=90, optimize=True)
    print("built", out)

ITEMS = {
 "vv-01-chistka.jpg":   ("vit-chistka.png", None),
 "vv-02-kt.jpg":        ("vbg-ct.png", (0, 560, 1152, 1712)),      # КТ-томограф, средняя часть
 "vv-03-ortodont.jpg":  ("vit-orto.png", (0, 0, 2048, 1870)),
 "vv-04-detskiy.jpg":   ("vit-kid.png", None),
 "vv-05-karies.jpg":    ("vit-karies.png", None),
 "vv-06-desny.jpg":     ("vit-desny.png", None),
 "vv-07-udalenie.jpg":  ("vit-udalenie.png", None),
 "vv-08-otbelivanie.jpg": ("vbg-smile.png", (0, 300, 1152, 1452)), # белоснежная улыбка
 "vv-09-viniry.jpg":    ("vit-viniry.png", (620, 0, 2048, 1428)),
 "vv-10-koronka.jpg":   ("vit-koronka.png", None),
 "vv-11-implant.jpg":   ("vit-implant.png", None),
 "vv-12-brekety.jpg":   ("vit-brekety.png", None),
}
import sys
keys = sys.argv[1:] or list(ITEMS)
for k in keys:
    src, crop = ITEMS[k]
    make(k, src, crop)
