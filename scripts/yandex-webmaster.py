#!/usr/bin/env python3
"""Выгрузка SEO-данных Версаль из API Яндекс.Вебмастера и Метрики.

Токен НЕ хранится в репозитории. Скрипт читает его из переменной окружения
YANDEX_WEBMASTER_TOKEN (OAuth-токен с правами webmaster:hostinfo + metrika:read).
Как получить токен и куда его положить — см. scripts/README-yandex-api.md.

Запуск:
    YANDEX_WEBMASTER_TOKEN=xxxx python3 scripts/yandex-webmaster.py

Скрипт не деплоится (scripts/ исключён из rsync).
"""
import os, sys, re, json, time, pathlib, urllib.request, urllib.parse, urllib.error

WM_API = "https://api.webmaster.yandex.net/v4"
MT_API = "https://api-metrika.yandex.net/stat/v1/data"
METRIKA_COUNTER = "109728396"  # счётчик Метрики Версаль
SITE = "https://versal-dent.ru"


def _token():
    # Версаль — отдельный аккаунт Яндекса (свой токен). Приоритет —
    # YANDEX_WEBMASTER_TOKEN_VERSAL, чтобы не путать с токеном Angel.
    t = (os.environ.get("YANDEX_WEBMASTER_TOKEN_VERSAL")
         or os.environ.get("YANDEX_WEBMASTER_TOKEN") or "").strip()
    if not t:
        sys.exit("Нет токена: задайте YANDEX_WEBMASTER_TOKEN_VERSAL (см. scripts/README-yandex-api.md).")
    return t


def _get(url):
    req = urllib.request.Request(url, headers={"Authorization": "OAuth " + _token()})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"_http_error": e.code, "_body": e.read().decode("utf-8", "replace")[:400]}
    except Exception as e:
        return {"_error": str(e)}


def _post(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Authorization": "OAuth " + _token(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return {"_code": r.status, **(json.load(r) if r.length != 0 else {})}
    except urllib.error.HTTPError as e:
        return {"_http_error": e.code, "_body": e.read().decode("utf-8", "replace")[:400]}
    except Exception as e:
        return {"_error": str(e)}


def user_id():
    d = _get(f"{WM_API}/user/")
    if "user_id" not in d:
        sys.exit(f"Не удалось получить user_id: {d}")
    return str(d["user_id"])


def hosts(uid):
    d = _get(f"{WM_API}/user/{uid}/hosts/")
    return d.get("hosts", []) if isinstance(d, dict) else []


def host_report(uid, host_id):
    q = urllib.parse.quote(host_id, safe="")
    base = f"{WM_API}/user/{uid}/hosts/{q}"
    s = _get(f"{base}/summary/")
    print(f"  ИКС (SQI):            {s.get('sqi', '—')}")
    print(f"  Страниц в поиске:     {s.get('searchable_pages_count', '—')}")
    print(f"  Исключено страниц:    {s.get('excluded_pages_count', '—')}")
    diag = _get(f"{base}/diagnostics/")
    active = [(k, v.get("severity")) for k, v in (diag.get("problems", {}) or {}).items()
              if v.get("state") not in (None, "ABSENT", "NONE")]
    print(f"  Активные проблемы:    {active if active else 'нет'}")
    params = urllib.parse.urlencode({"order_by": "TOTAL_SHOWS",
        "query_indicator": ["TOTAL_SHOWS", "TOTAL_CLICKS", "AVG_SHOW_POSITION"], "limit": 30}, doseq=True)
    d = _get(f"{base}/search-queries/popular/?{params}")
    rows = d.get("queries", []) if isinstance(d, dict) else []
    print(f"\n  ТОП-{len(rows)} запросов (показы / клики / поз.показа):")
    print(f"  {'запрос':<52}{'пок':>6}{'клик':>6}{'поз':>7}")
    for qrow in rows:
        ind = qrow.get("indicators", {})
        sh = int(ind.get("TOTAL_SHOWS") or 0); cl = int(ind.get("TOTAL_CLICKS") or 0)
        ap = ind.get("AVG_SHOW_POSITION"); ap = f"{ap:.1f}" if ap else "—"
        print(f"  {qrow.get('query_text', '')[:51]:<52}{sh:>6}{cl:>6}{ap:>7}")


def metrika():
    def stat(params):
        return _get(MT_API + "?" + urllib.parse.urlencode(params))
    print("\n===== МЕТРИКА (счётчик %s, 30 дней) =====" % METRIKA_COUNTER)
    d = stat({"ids": METRIKA_COUNTER, "metrics": "ym:s:visits,ym:s:bounceRate,ym:s:avgVisitDurationSeconds",
              "dimensions": "ym:s:lastsignTrafficSource", "date1": "30daysAgo", "date2": "today", "limit": 20})
    if "_http_error" in d or "_error" in d:
        print("  Метрика недоступна:", d); return
    print(f"  {'источник':<26}{'визиты':>7}{'отказы':>8}{'ср.время':>10}")
    for r in d.get("data", []):
        m = r["metrics"]
        print(f"  {r['dimensions'][0]['name'][:25]:<26}{int(m[0]):>7}{m[1]:>7.0f}%{m[2]:>8.0f}с")
    print(f"  ИТОГО визитов: {int(d.get('totals', [0])[0])}")
    d2 = stat({"ids": METRIKA_COUNTER, "metrics": "ym:s:visits", "dimensions": "ym:s:startURLPathFull",
               "filters": "ym:s:lastsignTrafficSource=='organic'", "date1": "30daysAgo", "date2": "today", "limit": 12})
    if isinstance(d2, dict) and d2.get("data"):
        print("\n  Топ страниц входа из ПОИСКА:")
        for r in d2["data"]:
            print(f"    {int(r['metrics'][0]):>4}  {r['dimensions'][0]['name'][:64]}")


def sitemap_urls():
    """Канонические URL из корневого sitemap.xml (источник списка для переобхода)."""
    sm = (pathlib.Path(__file__).resolve().parent.parent / "sitemap.xml")
    if not sm.exists():
        return []
    return re.findall(r"<loc>(" + re.escape(SITE) + r"/[^<]*)</loc>", sm.read_text(encoding="utf-8"))


def recrawl(uid, host_id, urls):
    """Отправить страницы на переобход (Webmaster → «Переобход страниц»).

    Квота суточная (см. --quota). На каждый URL — отдельный POST. Полезно
    ПОСЛЕ деплоя, чтобы Яндекс быстрее увидел новые/обновлённые страницы и
    канонические URL вместо старых Tilda-адресов.
    """
    q = urllib.parse.quote(host_id, safe="")
    quota = _get(f"{WM_API}/user/{uid}/hosts/{q}/recrawl/quota/")
    rem = quota.get("quota_remainder")
    print(f"  Квота переобхода: осталось {rem} из {quota.get('daily_quota', '—')} на сутки")
    if isinstance(rem, int) and len(urls) > rem:
        print(f"  ⚠️ URL-ов ({len(urls)}) больше остатка квоты ({rem}) — отправлю первые {rem}.")
        urls = urls[:rem]
    ok = 0
    for u in urls:
        r = _post(f"{WM_API}/user/{uid}/hosts/{q}/recrawl/queue/", {"url": u})
        tid = r.get("task_id")
        if tid:
            ok += 1
            print(f"    ✓ {u}  (task {tid})")
        else:
            print(f"    ✗ {u}  → {r}")
        time.sleep(0.3)  # бережно к рейт-лимиту
    print(f"  Отправлено на переобход: {ok} из {len(urls)}")
    return ok


def main():
    args = sys.argv[1:]
    uid = user_id(); print(f"user_id: {uid}")
    hs = hosts(uid)
    if not hs:
        sys.exit("Хостов не найдено (проверьте права токена).")
    # В аккаунте владельца два сайта (Angel + Версаль) — выбираем именно этот.
    domain = SITE.split("//")[-1]
    host = next((h for h in hs if domain in (h.get("ascii_host_url") or h.get("host_id", ""))), None)
    if host is None:
        avail = ", ".join(h.get("ascii_host_url", "?") for h in hs) or "нет"
        sys.exit(f"Хост {domain} не найден в Вебмастере (доступны: {avail}).\n"
                 f"Добавьте и подтвердите {domain} в Яндекс.Вебмастере под этим аккаунтом,\n"
                 f"иначе данных по сайту нет. Metrika-счётчик {METRIKA_COUNTER} тоже должен быть\n"
                 f"доступен этому токену (иначе 403).")
    host_id = host["host_id"]

    if args and args[0] == "--quota":
        q = urllib.parse.quote(host_id, safe="")
        print(json.dumps(_get(f"{WM_API}/user/{uid}/hosts/{q}/recrawl/quota/"), ensure_ascii=False))
        return 0

    if args and args[0] == "--recrawl":
        urls = args[1:] or sitemap_urls()
        if not urls:
            sys.exit("Нет URL для переобхода (пустой sitemap.xml?).")
        print(f"\n===== ПЕРЕОБХОД ({len(urls)} URL) =====")
        recrawl(uid, host_id, urls)
        return 0

    print("\n===== %s =====" % host.get("ascii_host_url", host_id))
    print(f"  подтверждён: {host.get('verified')}")
    host_report(uid, host_id)
    metrika(); return 0


if __name__ == "__main__":
    raise SystemExit(main())
