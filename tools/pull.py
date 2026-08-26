#!/usr/bin/env python3
"""Забрать урок с app.sdarm.org и положить рядом с сайтом, в data/.

Издатель иногда правит уже вышедший квартал. Пока квартал идёт, правки нужны:
это исправленные опечатки. Когда квартал кончился, они не нужны — текст, под
который записана озвучка, не должен меняться сам. Поэтому:

    текущий квартал  — проверяется, и изменения забираются
    прошедший        — заморожен, сеть к нему больше не трогают

Проверка стоит ноль байт: HEAD и заголовок Last-Modified. Совпал с прошлым
разом — файл не качается вовсе. Что забрано и когда, записано в data/index.json.

    python3 tools/pull.py                 текущий квартал, три языка
    python3 tools/pull.py --quarter 2026-2
    python3 tools/pull.py --all           весь архив, 2020-1 … сегодня
    python3 tools/pull.py --force         не верить отметкам, забрать заново
"""
import argparse, datetime, json, pathlib, sys, urllib.error, urllib.request

SRC   = "https://app.sdarm.org/sbl/data/{lang}/{lang}-{year}-{q}.json"
LANGS = ("de", "en", "ru")
FIRST = (2020, 1)          # раньше издатель ничего не отдаёт: 2019 — 404
GRACE = 14                 # дней после конца квартала, пока ещё проверяем
UA    = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " \
        "(KHTML, like Gecko) Chrome/120 Safari/537.36"   # без него сервер отвечает 406

ROOT  = pathlib.Path(__file__).resolve().parent.parent
DATA  = ROOT / "data"
INDEX = DATA / "index.json"


def quarter_of(d):
    return (d.year, (d.month - 1) // 3 + 1)


def quarter_end(year, q):
    m = q * 3
    last = 31 if m in (1, 3, 5, 7, 8, 10, 12) else 30 if m != 2 else 29 if (
        year % 4 == 0 and (year % 100 or year % 400 == 0)) else 28
    return datetime.date(year, m, last)


def every_quarter(today):
    y, q = FIRST
    while (y, q) <= quarter_of(today):
        yield y, q
        q += 1
        if q == 5:
            y, q = y + 1, 1


def ask(url, method):
    r = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
    return urllib.request.urlopen(r, timeout=30)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--quarter", help="год-квартал, например 2026-2")
    p.add_argument("--lang", action="append", choices=LANGS)
    p.add_argument("--all", action="store_true", help="весь архив с 2020-1")
    p.add_argument("--force", action="store_true", help="забрать, не глядя на отметки")
    a = p.parse_args()

    today = datetime.date.today()
    langs = a.lang or list(LANGS)
    if a.all:
        targets = list(every_quarter(today))
    elif a.quarter:
        y, q = a.quarter.split("-")
        targets = [(int(y), int(q))]
    else:
        targets = [quarter_of(today)]

    index = json.loads(INDEX.read_text("utf-8")) if INDEX.exists() else {}
    fresh, frozen, same, gone = [], [], [], []

    for year, q in targets:
        # квартал кончился и отлежался — его копия окончательная
        cold = (today - quarter_end(year, q)).days > GRACE
        for lang in langs:
            key  = f"{lang}-{year}-{q}"
            file = DATA / lang / f"{key}.json"
            rec  = index.get(key, {})
            url  = SRC.format(lang=lang, year=year, q=q)

            if cold and file.exists() and not (a.force or a.all):
                frozen.append(key)
                continue
            try:
                head = ask(url, "HEAD")
                stamp = head.headers.get("Last-Modified", "")
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    gone.append(key)
                    continue
                raise
            if file.exists() and stamp and stamp == rec.get("lastModified") and not a.force:
                same.append(key)
                continue
            body = ask(url, "GET").read()
            doc  = json.loads(body)                 # мусор в data/ не попадёт
            if not doc.get("lessons"):
                raise SystemExit(f"{key}: в ответе нет lessons — не пишу")
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(body)
            index[key] = {"lastModified": stamp,
                          "updated": doc.get("updated"),
                          "lessons": len(doc["lessons"]),
                          "bytes": len(body),
                          "pulled": datetime.datetime.now(datetime.timezone.utc)
                                    .strftime("%Y-%m-%dT%H:%M:%SZ"),
                          "frozen": cold}
            fresh.append(key)

    if fresh:
        DATA.mkdir(exist_ok=True)
        INDEX.write_text(json.dumps(dict(sorted(index.items())),
                                    ensure_ascii=False, indent=1) + "\n", "utf-8")

    for name, items in (("забрано", fresh), ("не изменилось", same),
                        ("заморожено", frozen), ("нет у издателя", gone)):
        if items:
            print(f"{name}: {len(items)}" + (" — " + ", ".join(items) if items is fresh else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
