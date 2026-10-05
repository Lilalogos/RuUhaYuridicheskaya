#!/usr/bin/env python3
"""Тексты актов с КонсультантПлюс → evidence/law/<slug>/source.pdf (+ url, sha256, meta.yml).

Список — evidence/law/SOURCES.tsv (slug \t url \t title). Для записей, помеченных
в EXPAND, корневая страница документа на consultant.ru отдаёт только оглавление —
скрипт читает оглавление и добавляет постатейные страницы (slug_NN-<article>).
Печать — scripts/print_pdf.sh. Повторный запуск докачивает только отсутствующее.
"""

from __future__ import annotations

import hashlib
import html as htmlmod
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SK = Path(__file__).resolve().parents[1]
LAW = SK / "evidence" / "law"
PR = SK / "scripts" / "print_pdf.sh"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# slug корня -> фильтр заголовков подстраниц (regex) или None = все
EXPAND = {
    "fz-69-2025-04-07": None,
    "fz-376-2025-10-15": None,
    "fz-248-2025-07-23": None,
    "fz-9-2025-02-13": None,
    "fz-41-2025-04-01": None,
    "fz-72-2025-04-07": None,
    "fz-156-2025-06-24": None,
    "fz-168-2025-06-24": None,
    "fz-420-2024-11-30": None,
    "plenum-vs-17-2012": None,
    "plenum-vs-49-2018": None,
    "pp-2463-2020": r"Правила продажи товаров по договору розничной|^II\.|^I\.|дистанцион",
    "fap-82-2007_root": r"Бронирован|Оплат|Общие положения|провозной|XXII|Прекращение договора",
    "fz-199-2026-06-26": None,
    "fz-332-2025-07-31": None,
    "fz-505-2023-10-19": None,
    "fz-284-2025-07-31": None,
    "fz-561-2025-12-29": None,
    "fz-406-2023-07-31": None,
}


def curl(url: str) -> str:
    return subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", "60", url], capture_output=True, check=True).stdout.decode("utf-8", "ignore")


def toc_links(root_url: str) -> list[tuple[str, str]]:
    m = re.search(r"cons_doc_LAW_(\d+)", root_url)
    doc = m.group(1)
    page = curl(root_url)
    out = []
    seen = set()
    for href, name in re.findall(rf'href="(/document/cons_doc_LAW_{doc}/[0-9a-f]{{40}}/)"[^>]*>([^<]{{2,200}})', page):
        name = htmlmod.unescape(name).strip()
        if href in seen or not name:
            continue
        seen.add(href)
        out.append(("https://www.consultant.ru" + href, name))
    return out


def slugify(name: str, n: int) -> str:
    s = re.sub(r"[^\w]+", "-", name.lower()).strip("-")
    s = re.sub(r"-+", "-", s)[:40].strip("-")
    return f"{n:02d}-{s or 'razdel'}"


def read_sources() -> list[tuple[str, str, str]]:
    rows = []
    for line in (LAW / "SOURCES.tsv").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        slug, url, title = line.split("\t", 2)
        rows.append((slug, url, title))
    return rows


def fetch_one(slug: str, url: str, title: str, parent: str | None = None) -> None:
    d = LAW / slug
    d.mkdir(parents=True, exist_ok=True)
    pdf = d / "source.pdf"
    if not pdf.is_file() or pdf.stat().st_size == 0 or not (d / "meta.yml").is_file() or (d / "meta.yml").stat().st_size == 0:
        if not pdf.is_file() or pdf.stat().st_size == 0:
            r = subprocess.run([str(PR), url, str(pdf), "60"], capture_output=True, text=True)
            print(r.stdout.strip() or r.stderr.strip()[-200:])
            if not pdf.is_file() or pdf.stat().st_size == 0:
                print("FAIL", slug)
                return
        utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        (d / "source.url.txt").write_text(f"{url}\n  «Печать→PDF» (Chrome headless) страницы КонсультантПлюс, UTC {utc}\n", encoding="utf-8")
        sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
        (d / "source.sha256").write_text(f"{sha}  source.pdf\n", encoding="utf-8")
        text = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
        red = re.search(r"\(ред\. от [0-9.]+[^)]*\)|\(последняя редакция\)|с изм\. и доп\., вступ\. в силу с [0-9.]+|Документ не вступил в силу", text)
        pages = re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout)
        first = next((l.strip() for l in text.splitlines() if l.strip()), "")
        toc_only = bool(re.search(r"^• Статья \d", text, re.M)) and len(text.split()) < 300
        meta = "\n".join([
            f"id: {slug}",
            "kind: law_text",
            f'title: "{title.replace(chr(34), chr(39))}"',
            f"parent: {parent}" if parent else "parent: null",
            "source: КонсультантПлюс (www.consultant.ru), сохранённая страница",
            f'redaction_marker: "{(red.group(0) if red else "").replace(chr(34), chr(39))}"',
            f'first_line: "{first[:160].replace(chr(34), chr(39))}"',
            f"toc_only: {'true' if toc_only else 'false'}",
            f"source_url: {url}",
            f"captured_utc: {utc}",
            "text_layer: true",
            f"pages: {pages.group(1) if pages else 0}",
            f"sha256: {sha}",
            'notes: "Вторичный правовой справочник, который сам обзорный PDF называет местом сверки; официальное опубликование — publication.pravo.gov.ru (с этой машины недоступен: соединение не устанавливается)."',
            "",
        ])
        (d / "meta.yml").write_text(meta, encoding="utf-8")
        print("meta", slug)


def main() -> int:
    rows = read_sources()
    only = set(sys.argv[1:])
    for slug, url, title in rows:
        if only and slug not in only:
            continue
        fetch_one(slug, url, title)
        if slug in EXPAND:
            flt = EXPAND[slug]
            for n, (sub_url, name) in enumerate(toc_links(url), 1):
                if flt and not re.search(flt, name):
                    continue
                fetch_one(f"{slug}_{slugify(name, n)}", sub_url, f"{title} — {name}", parent=slug)
    # индекс
    lines = ["# Индекс текстов актов (evidence/law)", "", "| slug | акт | редакция | стр. | только оглавление |", "|---|---|---|---|---|"]
    for d in sorted(p for p in LAW.iterdir() if p.is_dir()):
        m = (d / "meta.yml")
        if not m.is_file():
            continue
        meta = m.read_text(encoding="utf-8")
        g = lambda k: (re.search(rf"^{k}: \"?(.*?)\"?$", meta, re.M) or [None, ""])[1]
        lines.append(f"| `{d.name}` | {g('title')} | {g('redaction_marker')} | {g('pages')} | {g('toc_only')} |")
    (LAW / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("INDEX.md:", len(lines) - 4, "записей")
    return 0


if __name__ == "__main__":
    sys.exit(main())
