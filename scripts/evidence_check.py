#!/usr/bin/env python3
"""Проверка целостности архива улик и его связи с базой.

  * sha256 каждого evidence/enforcement/<id>/source.pdf совпадает с source.sha256
    и с original_document.sha256 капсулы в applaw/sources/source_capsules.json;
  * у каждого акта есть meta.yml, quotes.md, source.url.txt и текстовый слой (pdffonts);
  * каждая запись enforcement_outcomes.yml указывает на существующую папку и капсулу;
  * SHA256SUMS.txt каждой серии captures/ сходится с файлами;
  * evidence/practice: sha256 исходной таблицы и снимков карточек (card.pdf) сходятся.

    python3 -B scripts/evidence_check.py          # отчёт, код 1 при расхождениях
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
KB = SKILL / "applaw"
EV = SKILL / "evidence"
sys.path.insert(0, str(KB / "scripts"))
from _kb import parse_outcome_registry  # noqa: E402


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def has_text_layer(pdf: Path) -> bool:
    try:
        out = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return False
    return len(out.strip().splitlines()) > 2


def main() -> int:
    issues: list[str] = []
    capsules = {
        c.get("evidence_folder", "").split("/")[-1]: c
        for c in json.loads((KB / "sources" / "source_capsules.json").read_text(encoding="utf-8"))["sources"]
        if c.get("evidence_kind") == "enforcement_act"
    }
    folders = sorted(p for p in (EV / "enforcement").iterdir() if p.is_dir())
    for folder in folders:
        for name in ("meta.yml", "quotes.md", "source.url.txt", "source.sha256", "source.pdf"):
            if not (folder / name).is_file():
                issues.append(f"{folder.name}: нет {name}")
        pdf = folder / "source.pdf"
        if pdf.is_file():
            digest = sha256_file(pdf)
            if digest not in (folder / "source.sha256").read_text(encoding="utf-8"):
                issues.append(f"{folder.name}: sha256 source.pdf не совпадает с source.sha256")
            capsule = capsules.get(folder.name)
            if not capsule:
                issues.append(f"{folder.name}: нет капсулы в source_capsules.json (запустите build_evidence_capsules.py)")
            elif capsule["original_document"]["sha256"] != digest:
                issues.append(f"{folder.name}: sha256 капсулы устарел")
            if not has_text_layer(pdf):
                issues.append(f"{folder.name}: у source.pdf нет текстового слоя")
    _, outcomes = parse_outcome_registry(KB / "taxonomy" / "enforcement_outcomes.yml")
    for rec in outcomes:
        folder = EV / str(rec.get("evidence_folder", "")).removeprefix("evidence/")
        if not folder.is_dir():
            issues.append(f"{rec.get('id')}: папка {rec.get('evidence_folder')} не найдена")
        if str(rec.get("source_capsule_id", "")) not in {c["source_id"] for c in capsules.values()}:
            issues.append(f"{rec.get('id')}: капсула {rec.get('source_capsule_id')} не найдена")
    law_dirs = sorted(p for p in (EV / "law").iterdir() if p.is_dir()) if (EV / "law").is_dir() else []
    for d in law_dirs:
        pdf = d / "source.pdf"
        if not pdf.is_file():
            issues.append(f"law/{d.name}: нет source.pdf"); continue
        if not (d / "meta.yml").is_file() or (d / "meta.yml").stat().st_size == 0:
            issues.append(f"law/{d.name}: пустой meta.yml")
        sha = (d / "source.sha256").read_text(encoding="utf-8").split()[0] if (d / "source.sha256").is_file() else ""
        if sha != sha256_file(pdf):
            issues.append(f"law/{d.name}: sha256 не совпадает")
    series = sorted(p for p in (EV / "captures").iterdir() if p.is_dir())
    for s in series:
        sums = s / "SHA256SUMS.txt"
        if not sums.is_file():
            issues.append(f"{s.name}: нет SHA256SUMS.txt")
            continue
        for line in sums.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            digest, _, name = line.partition("  ")
            target = s / name.strip()
            if not target.is_file():
                issues.append(f"{s.name}: файл {name.strip()} из SHA256SUMS отсутствует")
            elif sha256_file(target) != digest.strip():
                issues.append(f"{s.name}: sha256 {name.strip()} не совпадает")
    practice = EV / "practice"
    practice_cards = 0
    if practice.is_dir():
        src = practice / "source" / "sudebnaya-praktika-2026-10-13.xlsx"
        sha = (practice / "source" / "source.sha256").read_text(encoding="utf-8").split()[0] if (practice / "source" / "source.sha256").is_file() else ""
        if not src.is_file() or sha != sha256_file(src):
            issues.append("practice/source: xlsx отсутствует или sha256 не совпадает")
        for d in sorted(p for p in (practice / "cards").iterdir() if p.is_dir()) if (practice / "cards").is_dir() else []:
            practice_cards += 1
            for name in ("card.html", "card.pdf", "card.sha256", "card.url.txt"):
                if not (d / name).is_file():
                    issues.append(f"practice/cards/{d.name}: нет {name}")
            if (d / "card.pdf").is_file() and (d / "card.sha256").is_file():
                if sha256_file(d / "card.pdf") not in (d / "card.sha256").read_text(encoding="utf-8"):
                    issues.append(f"practice/cards/{d.name}: sha256 card.pdf не совпадает")
    print(f"актов: {len(folders)}; капсул актов: {len(capsules)}; записей исходов: {len(outcomes)}; серий экранов: {len(series)}; текстов законов: {len(law_dirs)}; карточек практики: {practice_cards}")
    if issues:
        print("РАСХОЖДЕНИЯ:")
        for item in issues:
            print(" -", item)
        return 1
    print("целостность улик: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
