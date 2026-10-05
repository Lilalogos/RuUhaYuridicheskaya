#!/usr/bin/env python3
"""Сверка quotes.md с текстовым слоем source.pdf (постранично, нормализация пробелов).

    verify_quotes.py [folder ...]      # по умолчанию — все evidence/enforcement/*
Выход: OK/BAD по каждой цитате; код 1, если есть BAD.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

E = Path(__file__).resolve().parents[1] / "evidence" / "enforcement"


def norm(s: str) -> str:
    s = s.replace("­", "").replace("­", "")
    s = re.sub(r"[«»\"“”]", '"', s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def page_text(pdf: Path, page: int) -> str:
    return subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"], capture_output=True, text=True).stdout


def main() -> int:
    folders = [Path(a) if Path(a).is_dir() else E / a for a in sys.argv[1:]] or sorted(p for p in E.iterdir() if p.is_dir())
    bad = 0
    total = 0
    for folder in folders:
        q = folder / "quotes.md"
        pdf = folder / "source.pdf"
        if not q.is_file() or not pdf.is_file():
            continue
        cache: dict[int, str] = {}
        for line in q.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\*\*стр\. (\d+)(?:/(\d+))?\*\* — «(.+)»\s*(\(.*\))?\s*$", line.strip())
            if not m:
                continue
            total += 1
            pages = [int(m.group(1))] + ([int(m.group(2))] if m.group(2) else [])
            quote = norm(m.group(3))
            text = ""
            for p in pages:
                cache.setdefault(p, norm(page_text(pdf, p)))
                text += " " + cache[p]
            if quote in text:
                continue
            # цитата может быть разнесена на страницу + следующую
            nxt = pages[-1] + 1
            cache.setdefault(nxt, norm(page_text(pdf, nxt)))
            if quote in text + " " + cache[nxt]:
                print(f"WARN {folder.name}: стр. {pages} — цитата переходит на стр. {nxt}: {m.group(3)[:70]}…")
                continue
            bad += 1
            print(f"BAD  {folder.name}: стр. {pages}: {m.group(3)[:90]}…")
    print(f"цитат: {total}, BAD: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
