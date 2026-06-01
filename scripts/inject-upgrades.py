#!/usr/bin/env python3
"""
Apply UX/SEO upgrades to every HTML page in the project:

- Replace OG/Twitter image (logo.png) with the generated CDN banner.
- Add <link rel=preconnect> for Higgsfield CDN + Yandex.
- Insert the scroll-progress bar right after <body>.
- Insert the floating contact widget (FAB) right before the main <script>.

Idempotent: re-running won't duplicate blocks. Run from project root.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Higgsfield CDN — generated branded social banner (1200x630-ish, 16:9 2K).
# Replace these URLs after running scripts/sync-higgsfield-images.sh
# to switch to local /assets/img/generated/ paths.
OG_BANNER_URL = (
    "https://d8j0ntlcm91z4.cloudfront.net/user_3Di09CVa1BatdZIdE0tir1KKUxw/"
    "hf_20260518_141253_d2cb86d1-e4f8-4193-998c-8f65003b9127.png"
)
CDN_HOST = "https://d8j0ntlcm91z4.cloudfront.net"

PRECONNECT_MARK = "<!-- ad-preconnect-block -->"
PRECONNECT_BLOCK = f"""{PRECONNECT_MARK}
<link rel="preconnect" href="{CDN_HOST}" crossorigin>
<link rel="preconnect" href="https://yandex.ru">
<link rel="dns-prefetch" href="https://mc.yandex.ru">"""

PROGRESS_MARK = "<!-- ad-scroll-progress -->"
PROGRESS_BLOCK = f"""{PROGRESS_MARK}
<div class="scroll-progress"><span class="scroll-progress__bar" data-scroll-progress></span></div>"""

FAB_MARK = "<!-- ad-fab-widget -->"
FAB_BLOCK = f"""{FAB_MARK}
<div class="fab" data-fab aria-label="Связаться с клиникой">
  <div class="fab__menu" role="menu">
    <a href="https://wa.me/70000000000?text=Здравствуйте!%20Хочу%20записаться%20в%20Версаль-Дент" target="_blank" rel="noopener" class="fab__item" role="menuitem">
      <span class="fab__item-icon fab__item-icon--wa"><svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M.057 24l1.687-6.163a11.867 11.867 0 0 1-1.587-5.946C.16 5.335 5.495 0 12.05 0a11.817 11.817 0 0 1 8.413 3.488 11.824 11.824 0 0 1 3.48 8.414c-.003 6.557-5.338 11.892-11.893 11.892a11.9 11.9 0 0 1-5.688-1.448L.057 24zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884a9.86 9.86 0 0 0 1.51 5.26l.6.953-1 3.648 3.74-.98z"/></svg></span>
      WhatsApp
    </a>
    <a href="https://t.me/versaldent" target="_blank" rel="noopener" class="fab__item" role="menuitem">
      <span class="fab__item-icon fab__item-icon--tg"><svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.961 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg></span>
      Telegram
    </a>
    <a href="tel:+70000000000" class="fab__item" role="menuitem">
      <span class="fab__item-icon fab__item-icon--phone"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg></span>
      Позвонить
    </a>
  </div>
  <button type="button" class="fab__toggle" data-fab-toggle aria-label="Открыть меню связи" aria-expanded="false" aria-haspopup="true">
    <svg class="fab__icon-open" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
    <svg class="fab__icon-close" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
  </button>
</div>"""


def discover_html() -> list[Path]:
    """Return all HTML pages excluding 404 and partials."""
    files = []
    for p in ROOT.rglob("*.html"):
        if any(part.startswith(".") for part in p.parts):
            continue
        files.append(p)
    return files


def replace_og_image(html: str) -> str:
    """Swap logo.png OG/Twitter images for the branded social banner."""
    patterns = [
        (r'(<meta property="og:image" content=")[^"]*assets/img/logo\.png(")', rf'\1{OG_BANNER_URL}\2'),
        (r'(<meta name="twitter:image" content=")[^"]*assets/img/logo\.png(")', rf'\1{OG_BANNER_URL}\2'),
    ]
    for pat, repl in patterns:
        html = re.sub(pat, repl, html)
    return html


def ensure_preconnect(html: str) -> str:
    """Insert preconnect block once, right before the styles.css link."""
    if PRECONNECT_MARK in html:
        return html
    return re.sub(
        r'(<link rel="stylesheet" href="[^"]*styles\.css">)',
        f'{PRECONNECT_BLOCK}\n\\1',
        html,
        count=1,
    )


def ensure_progress(html: str) -> str:
    """Insert scroll progress bar once, right after <body>."""
    if PROGRESS_MARK in html:
        return html
    return re.sub(
        r'(<body[^>]*>)',
        rf'\1\n\n{PROGRESS_BLOCK}',
        html,
        count=1,
    )


def ensure_fab(html: str) -> str:
    """Insert FAB once, right before the closing </body> tag."""
    if FAB_MARK in html:
        return html
    if '</body>' not in html:
        return html
    return html.replace('</body>', f'\n{FAB_BLOCK}\n</body>', 1)


def apply(html: str) -> str:
    html = replace_og_image(html)
    html = ensure_preconnect(html)
    html = ensure_progress(html)
    html = ensure_fab(html)
    return html


def main() -> None:
    files = discover_html()
    changed = 0
    for f in files:
        original = f.read_text(encoding="utf-8")
        updated = apply(original)
        if updated != original:
            f.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"  updated {f.relative_to(ROOT)}")
    print(f"\nDone. {changed} / {len(files)} files updated.")


if __name__ == "__main__":
    main()
