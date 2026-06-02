#!/usr/bin/env python3
"""Скачивает сгенерированные изображения услуг (Higgsfield CDN) и кладёт
их в assets/img/services/<svc>.webp. Запускается в GitHub Actions, где
есть доступ в интернет (из dev-контейнера CDN закрыт сетевой политикой).

Манифест: scripts/service-images.json  ({ "<svc>": "<url>", ... }).
"""
import json, os, io, urllib.request
from PIL import Image, ImageOps, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(ROOT, "scripts", "service-images.json")))
out = os.path.join(ROOT, "assets", "img", "services")
os.makedirs(out, exist_ok=True)

def norm(im, w=1200, h=750):
    im = ImageOps.exif_transpose(im).convert("RGB")
    sw, sh = im.size; tr = w / h; sr = sw / sh
    if sr > tr:
        nw = int(sh * tr); im = im.crop(((sw - nw) // 2, 0, (sw - nw) // 2 + nw, sh))
    else:
        nh = int(sw / tr); im = im.crop((0, (sh - nh) // 2, sw, (sh - nh) // 2 + nh))
    return im.resize((w, h), Image.LANCZOS)

for svc, url in data.items():
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=90).read()
    im = norm(Image.open(io.BytesIO(raw)))
    im = ImageEnhance.Brightness(im).enhance(1.03)
    im = ImageEnhance.Color(im).enhance(1.04)
    im.save(os.path.join(out, f"{svc}.webp"), "WEBP", quality=85, method=6)
    print("saved", svc, len(raw) // 1024, "KB")
print("done")
