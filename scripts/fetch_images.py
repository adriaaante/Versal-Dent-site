#!/usr/bin/env python3
"""Скачивает изображения по манифесту scripts/images.json
({ "<target-path>": "<url>", ... }) и сохраняет каждое в указанный путь
в формате webp (обрезка под 16:10, лёгкое осветление). Запускается в
GitHub Actions (в dev-контейнере CDN недоступен сетевой политикой).
"""
import json, os, io, urllib.request
from PIL import Image, ImageOps, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(ROOT, "scripts", "images.json")))

def norm(im, w=1200, h=750):
    im = ImageOps.exif_transpose(im).convert("RGB")
    sw, sh = im.size; tr = w / h; sr = sw / sh
    if sr > tr:
        nw = int(sh * tr); im = im.crop(((sw - nw) // 2, 0, (sw - nw) // 2 + nw, sh))
    else:
        nh = int(sw / tr); im = im.crop((0, (sh - nh) // 2, sw, (sh - nh) // 2 + nh))
    return im.resize((w, h), Image.LANCZOS)

for rel, url in data.items():
    dst = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=90).read()
    im = norm(Image.open(io.BytesIO(raw)))
    im = ImageEnhance.Brightness(im).enhance(1.03)
    im = ImageEnhance.Color(im).enhance(1.04)
    im.save(dst, "WEBP", quality=85, method=6)
    print("saved", rel, len(raw) // 1024, "KB")
print("done")
