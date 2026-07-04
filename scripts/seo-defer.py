#!/usr/bin/env python3
"""Идемпотентно добавляет defer к <script src=".../{main,cookies,portfolio}.js">
во всех HTML (INP/FID — скрипты не блокируют рендер). Все они defer-safe
(IIFE + DOMContentLoaded). Запуск из корня репо: python3 scripts/seo-defer.py"""
import re, pathlib
ROOT=pathlib.Path(__file__).resolve().parent.parent
rx=re.compile(r'(<script src="[^"]*(?:main|cookies|portfolio)\.js")>(</script>)')
n=0
for f in ROOT.rglob("*.html"):
    if ".git" in f.parts: continue
    s=f.read_text(encoding="utf-8")
    s2=rx.sub(lambda m: m.group(1)+" defer>"+m.group(2), s)
    if s2!=s: f.write_text(s2,encoding="utf-8"); n+=1
print("defer добавлен в",n,"HTML-файлов")
