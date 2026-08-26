#!/usr/bin/env python3
"""Положить свежую запись в audio/ под тем именем, которое ждёт плеер.

ElevenLabs отдаёт файл с именем вроде
    ElevenLabs_2026-08-25T20_44_40_JM - Husky & Engaging (…)_v3.mp3
Плееру нужно другое: язык, урок двумя цифрами, день и буква вопроса.

    python3 tools/audio-add.py ~/Downloads/ElevenLabs_*.mp3 de-09-1b
    python3 tools/audio-add.py --check de 9      что уже лежит и нет ли дыр

Скрипт ничего не выкладывает: он только кладёт файл на место и говорит, что
получилось. Публикация — обычные git add/commit/push, как в audio/README.md.
"""
import argparse, pathlib, re, shutil, sys

ROOT  = pathlib.Path(__file__).resolve().parent.parent
AUDIO = ROOT / "audio"
NAME  = re.compile(r"^(de|en|ru)-(\d{2})-(0|[1-7][a-h])$")
DAYS  = ["воскресенье","понедельник","вторник","среда","четверг","пятница","суббота"]


def parts(lang, no):
    """Что лежит для этого урока и где обрыв."""
    pre = f"{lang}-{int(no):02d}-"
    have = sorted(p.stem[len(pre):] for p in AUDIO.glob(pre + "*.mp3"))
    lines, gaps = [], []
    if "0" in have:
        lines.append("  0   вступление")
    else:
        gaps.append("нет вступления — плеера не будет вовсе")
    for d in range(1, 8):
        got = sorted(h[1:] for h in have if h[:1] == str(d) and len(h) == 2)
        if not got:
            continue
        run = ""
        for i, letter in enumerate(got):
            if letter != chr(97 + i):
                gaps.append(f"день {d}: после «{run[-1] if run else '—'}» пропуск, "
                            f"«{letter}» плеер уже не увидит")
                break
            run += letter
        lines.append(f"  {d}{'':2}{DAYS[d-1]:<13}{' '.join(got)}")
    return lines, gaps


def report(lang, no):
    lines, gaps = parts(lang, no)
    print(f"\n{lang}, урок {int(no):02d}:")
    print("\n".join(lines) if lines else "  пусто")
    for g in gaps:
        print("  ⚠ " + g)
    if not gaps and lines:
        print("  дыр нет — плеер соберёт всё подряд")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", nargs="?", help="что скачалось из ElevenLabs")
    p.add_argument("name", nargs="?", help="как назвать: de-09-1b")
    p.add_argument("--check", nargs=2, metavar=("ЯЗЫК", "УРОК"), help="только показать, что есть")
    p.add_argument("--keep", action="store_true", help="копировать, а не переносить")
    p.add_argument("--force", action="store_true", help="переписать, если такой уже лежит")
    a = p.parse_args()

    if a.check:
        report(a.check[0], a.check[1]); return 0
    if not (a.file and a.name):
        p.error("нужен файл и имя, либо --check ЯЗЫК УРОК")

    m = NAME.match(a.name.replace(".mp3", ""))
    if not m:
        raise SystemExit(f"«{a.name}» не то имя. Нужно вроде de-09-0, de-09-1b, ru-12-4c")
    src = pathlib.Path(a.file).expanduser()
    if not src.is_file():
        raise SystemExit(f"нет такого файла: {src}")
    dst = AUDIO / (a.name.replace(".mp3", "") + ".mp3")
    if dst.exists() and not a.force:
        raise SystemExit(f"{dst.name} уже лежит. Переписать — с --force")

    AUDIO.mkdir(exist_ok=True)
    (shutil.copy2 if a.keep else shutil.move)(str(src), str(dst))
    print(f"{'скопирован' if a.keep else 'перенесён'} → audio/{dst.name}  "
          f"({dst.stat().st_size // 1024} КБ)")
    report(m.group(1), m.group(2))
    print("\nвыложить:  git add audio && git commit -m \"audio\" && git push")
    return 0


if __name__ == "__main__":
    sys.exit(main())
