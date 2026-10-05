#!/usr/bin/env python3
"""Снимок карточки дела на сайте суда (sudrf / mos-gorsud): HTML + текстовый PDF.

Карточки sudrf держат вкладки (ДЕЛО / ДВИЖЕНИЕ / ОБЖАЛОВАНИЕ) скрытыми через CSS,
поэтому печать браузером теряет сведения об обжаловании. Снимок берёт весь текст
страницы (включая скрытые вкладки) и кладёт его в PDF с текстовым слоем, а исходный
HTML сохраняет рядом. Это «сохранённая страница» в терминах evidence/CLAUDE.md §0.1,
а не текст акта: в meta.yml ссылаться как на карточку.

    snapshot_card.py <url> <outdir> [basename=card]
"""

from __future__ import annotations

import hashlib
import html as htmlmod
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import fitz  # PyMuPDF

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def fetch(url: str) -> bytes:
    return subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", "60", url], capture_output=True, check=True).stdout


def decode(raw: bytes) -> str:
    head = raw[:4000].lower()
    enc = "cp1251" if b"windows-1251" in head or b"charset=cp1251" in head else "utf-8"
    return raw.decode(enc, errors="ignore")


def to_text(doc: str) -> str:
    t = re.sub(r"<script.*?</script>", "", doc, flags=re.S)
    t = re.sub(r"<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<(br|/p|/div|/tr|/li|/h\d|/table)[^>]*>", "\n", t, flags=re.I)
    t = re.sub(r"<(td|th)[^>]*>", " | ", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = htmlmod.unescape(t)
    t = re.sub(r"[ \t\xa0]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


def main() -> int:
    url, outdir = sys.argv[1], Path(sys.argv[2])
    base = sys.argv[3] if len(sys.argv) > 3 else "card"
    outdir.mkdir(parents=True, exist_ok=True)
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    raw = fetch(url)
    (outdir / f"{base}.html").write_bytes(raw)
    text = to_text(decode(raw))
    header = f"Снимок карточки дела (текст страницы, включая скрытые вкладки)\nURL: {url}\nUTC: {utc}\n{'=' * 80}\n\n"
    pdf = fitz.open()
    page = pdf.new_page(width=595, height=842)
    rect = fitz.Rect(36, 36, 559, 806)
    body = header + text
    fontfile = None
    for cand in ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial Unicode.ttf"):
        if Path(cand).exists():
            fontfile = cand
            break
    kwargs = dict(fontsize=8, fontname="F0", fontfile=fontfile) if fontfile else dict(fontsize=8, fontname="helv")
    while body:
        rc = page.insert_textbox(rect, body, **kwargs)
        if rc >= 0:
            break
        # не влезло: отрежем вставленную часть эмпирически — делим по строкам
        lines = body.split("\n")
        lo, hi = 0, len(lines)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            probe = fitz.open(); pp = probe.new_page(width=595, height=842)
            if pp.insert_textbox(rect, "\n".join(lines[:mid]), **kwargs) >= 0:
                lo = mid
            else:
                hi = mid - 1
            probe.close()
        page.insert_textbox(rect, "\n".join(lines[:max(lo, 1)]), **kwargs)
        body = "\n".join(lines[max(lo, 1):])
        if body:
            page = pdf.new_page(width=595, height=842)
    pdf.subset_fonts()
    pdf.save(outdir / f"{base}.pdf", garbage=4, deflate=True)
    pdf.close()
    sha_pdf = hashlib.sha256((outdir / f"{base}.pdf").read_bytes()).hexdigest()
    sha_html = hashlib.sha256(raw).hexdigest()
    (outdir / f"{base}.sha256").write_text(f"{sha_pdf}  {base}.pdf\n{sha_html}  {base}.html\n", encoding="utf-8")
    (outdir / f"{base}.url.txt").write_text(f"{url}\n  снимок карточки дела: curl → текст страницы → PDF (PyMuPDF), UTC {utc}; исходный HTML рядом ({base}.html)\n", encoding="utf-8")
    pages = fitz.open(outdir / f"{base}.pdf").page_count
    print(f"OK {outdir.name}/{base}.pdf pages={pages} chars={len(text)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
