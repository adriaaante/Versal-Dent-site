#!/usr/bin/env python3
"""Prepare a doctor portrait for the Angel-Dent site.

Steps:
  1. Remove the background:
       * if the source already has transparent pixels (alpha channel
         contains values < 250), reuse them — no need to re-run rembg;
       * otherwise call rembg (u2net model);
       * if rembg is not importable, fall back to a simple luminance
         chroma-key (pixels brighter than 235 in all channels become
         transparent).
  2. Crop to the subject's bounding box (with light padding) and frame
     it as a square anchored near the top so the face stays centred.
  3. Produce two PNGs: 600x600 (hero on /doctors/<slug>.html) and
     320x320 (thumbnail used on card grids).

Usage:
    python scripts/prepare-doctor-photo.py <source> <slug>

Examples:
    python scripts/prepare-doctor-photo.py /tmp/raw/geworkyan.webp geworkyan
    python scripts/prepare-doctor-photo.py /tmp/raw/smolyakova.png smolyakova
    python scripts/prepare-doctor-photo.py ~/Downloads/drobkova.jpg drobkova

Output files (relative to repo root):
    assets/img/doctors/<slug>.png        (600x600, hero)
    assets/img/doctors/<slug>-thumb.png  (320x320, card thumb)
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "assets" / "img" / "doctors"

SIZE_FULL = 600
SIZE_THUMB = 320


def remove_background(im: Image.Image) -> Image.Image:
    """Return an RGBA image with a transparent background.

    Uses birefnet-portrait — the most accurate model for portrait
    photos (handles dark uniforms against complex backgrounds well).
    Falls back to u2net and finally a chroma-key if rembg is missing.
    """
    im = im.convert("RGBA")
    # Heuristic: source counts as "already cut out" only if a substantial
    # share of pixels is transparent (not just a thin antialiased border).
    alpha = im.split()[-1]
    transparent_share = sum(1 for v in alpha.getdata() if v < 10) / (im.width * im.height)
    if transparent_share > 0.05:
        return im

    try:
        from rembg import remove, new_session  # type: ignore
        import io
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        try:
            session = new_session("birefnet-portrait")
        except Exception:
            session = new_session("isnet-general-use")
        out_bytes = remove(buf.getvalue(), session=session)
        return Image.open(io.BytesIO(out_bytes)).convert("RGBA")
    except Exception as exc:
        print(f"[warn] rembg unavailable ({exc}); using chroma-key fallback",
              file=sys.stderr)
        return _chroma_key_fallback(im)


def _chroma_key_fallback(im: Image.Image, threshold: int = 235) -> Image.Image:
    im = im.convert("RGBA")
    pixels = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, _ = pixels[x, y]
            if r >= threshold and g >= threshold and b >= threshold:
                pixels[x, y] = (r, g, b, 0)
    return im


def crop_square_face(im: Image.Image) -> Image.Image:
    """Crop to a square framed around the subject (face-centred at the top)."""
    alpha = im.split()[-1]
    bbox = alpha.getbbox()
    if bbox is None:
        raise SystemExit("background removal produced an empty alpha channel")

    subject = im.crop(bbox)
    w, h = subject.size

    side_pad = int(0.06 * w)
    square = max(w + 2 * side_pad, int(h * 0.72))
    crop_h = min(h, square)

    canvas = Image.new("RGBA", (square, square), (0, 0, 0, 0))
    paste_x = (square - w) // 2
    top_pad = int(0.02 * square)
    head = subject.crop((0, 0, w, crop_h))
    canvas.paste(head, (paste_x, top_pad), head)
    return canvas


def prepare(src_path: Path, slug: str) -> None:
    raw = Image.open(src_path)
    print(f"[1/4] open: {src_path} {raw.size} {raw.mode}")

    print("[2/4] remove background")
    cut = remove_background(raw)

    print("[3/4] crop to square (face-centred)")
    canvas = crop_square_face(cut)
    print(f"        canvas={canvas.size}")

    print("[4/4] resize and save")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    big = canvas.resize((SIZE_FULL, SIZE_FULL), Image.LANCZOS)
    small = canvas.resize((SIZE_THUMB, SIZE_THUMB), Image.LANCZOS)
    big_path = OUT_DIR / f"{slug}.png"
    small_path = OUT_DIR / f"{slug}-thumb.png"
    big.save(big_path, optimize=True)
    small.save(small_path, optimize=True)
    print(f"        wrote {big_path}")
    print(f"        wrote {small_path}")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 1
    prepare(Path(argv[1]).expanduser(), argv[2].strip().lower())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
