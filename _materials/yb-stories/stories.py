# -*- coding: utf-8 -*-
"""
Истории Яндекс.Бизнеса «Версаль» — перенос готовой линейки v1 на страницу-хаб.

Слайды собраны 19–20.07.2026 и хранились только на Google Диске; здесь они
перезалиты в постоянное хранилище (`from-drive/_uploads.json`) и описаны
так, как их заливать в кабинет: название истории ≤15 символов, текст
кнопки ≤15, ссылка кнопки на профильную страницу сайта.

⚠️ Порядок заливки: самая свежая история показывается ПЕРВОЙ, поэтому
сильнейшую тему заливаем последней.

Запуск: python3 stories.py  → stories.json
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://versal-dent.ru'

# префикс файлов, название истории (≤15), кнопка (≤15), ссылка, о чём
STORIES = [
    ('ist1', 'Не страшно', 'Записаться', '/contacts.html',
     'Про страх боли: анестезия, спокойный приём, можно остановиться в любой момент.'),
    ('ist2', 'Цены честно', 'Смотреть цены', '/ceny.html',
     'Смета до начала лечения, цены фиксируются в договоре и не растут по ходу.'),
    ('ist3', 'Технологии', 'Подробнее', '/tehnologii.html',
     'КТ, цифровое сканирование, DSD, стерилизация класса B.'),
    ('ist4', 'Наши врачи', 'Врачи', '/doctors/',
     'Реальные врачи клиники — единственная история, где показываем настоящие лица.'),
    ('ist5', 'Первый визит', 'Записаться', '/etapy.html',
     'Как проходит первый приём: осмотр, снимок, план и смета.'),
]


def export():
    up = {k: url for k, mid, code, url in
          json.load(open(os.path.join(HERE, 'from-drive', '_uploads.json')))}
    items = []
    for pref, name, btn, link, about in STORIES:
        imgs = [up[k] for k in sorted(up) if k.startswith(pref + '-')]
        items.append({'key': pref, 'title': name, 'btn': btn, 'link': SITE + link,
                      'about': about, 'imgs': imgs})
    json.dump({'title': 'Истории (сторис)', 'items': items},
              open(os.path.join(HERE, 'stories.json'), 'w'), ensure_ascii=False, indent=1)
    for it in items:
        print(f"{it['key']}  {it['title']:14s} слайдов {len(it['imgs'])}")


if __name__ == '__main__':
    export()
