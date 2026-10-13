#!/usr/bin/env python3
"""Карточки наводок (evidence/leads) из реестра практики evidence/practice/cases.tsv.

Одна строка таблицы → один файл `evidence/leads/<папка сценария>/<ГГГГММДД>-<домен>-P-NNN.md`
(дата — дата акта по таблице, если она полная; иначе 00000000). Формат — как у ручных карточек
(evidence/CLAUDE.md §3): что, где, дата, первичка. Текст описания и итога — пересказ составителя
таблицы, цитируется «по таблице»; агент не классифицирует (§0.5). Ручные карточки (без суффикса
`-P-NNN`) не трогаются; если для practice_id уже есть ручная карточка с пометкой `P-NNN` в теле,
автогенерация этой строки пропускается.
Запуск: python3 -B scripts/build_practice_leads.py  [--clean]  (--clean удаляет ранее сгенерированные `*-P-NNN.md`)
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

SKILL = Path(__file__).resolve().parents[1]
PR = SKILL / "evidence" / "practice"
LEADS = SKILL / "evidence" / "leads"
FOLDER = {"G1": "G1", "G2/G3": "G2", "G3": "G3", "G4": "G4", "G5": "G5", "G6": "G6", "G7": "G7", "G8": "G8",
          "content": "content", "consent": "consent", "security": "security", "platform": "platform",
          "вне-охвата:finance": "finance", "вне-охвата:ip": "ip", "вне-охвата:hr": "hr", "вне-охвата:gov": "gov",
          "вне-охвата:antitrust": "antitrust"}
SRC = {"act_or_card": "текст акта или карточка суда (открывал составитель таблицы)", "news": "новости или обзор (пересказ)", "search": "только поисковая выдача (страница не проверялась)"}
ARCHIVED = {
    "P-079": "по описанию совпадает с актом в архиве `enforcement/2024-mosgorsud-33-35439` (Мосгорсуд, 22.08.2024, «Победа»); сверить",
    "P-081": "в архиве семь актов по делу А40-284009/21 (`enforcement/2022-asmsk-A40-284009-21-20220318` … `2023-asmo-F05-19574-2022-20230531`), итог — нарушения нет",
    "P-082": "в архиве: `enforcement/2022-asmsk-A40-284009-21-20221212` (новое рассмотрение, 12.12.2022) и последующие инстанции",
    "P-109": "вероятно совпадает с `enforcement/2025-vologda-ufas-035-05-5-1030-2025` (Вологодское УФАС, 23.12.2025, реклама VPN); сверить",
}
CARDS = {"P-001": "taganskij-05-3666-2024", "P-002": "taganskij-05-2135-2024", "P-003": "taganskij-05-7212-2023", "P-004": "taganskij-05-7400-2023",
         "P-005": "taganskij-05-6990-2023", "P-006": "taganskij-05-0876-2024", "P-007": "taganskij-05-0317-2026", "P-010": "taganskij-search-koap-13-50"}


def where_to_search(auth: str, case: str, url: str) -> str:
    a = auth.lower()
    hints = []
    if "уфас" in a or "фас" in a or "антимонопол" in a:
        hints.append("База решений ФАС br.fas.gov.ru (поиск по ответчику и номеру) и сайт регионального УФАС")
    if re.search(r"а\d{2}-\d+", case.lower()) or "арбитраж" in a or "аас" in a:
        hints.append("Картотека арбитражных дел kad.arbitr.ru (капча — СТОП, нужен Виталий)")
    if "верховн" in a or re.search(r"\bвс\b", a) or "-кг" in case.lower() or "-эс" in case.lower():
        hints.append("vsrf.ru — тексты определений ВС РФ по номеру дела")
    if "мирово" in a:
        hints.append("портал мировых судей региона / mos-gorsud.ru (участки Москвы)")
    if any(k in a for k in ("районн", "городск", "областн", "краев", "мосгорсуд", "суд общей", "кассационн", "апелляционн")) and "арбитраж" not in a:
        hints.append("ГАС «Правосудие» sudrf.ru / mos-gorsud.ru — карточка дела и вкладка «Судебные акты»")
    if "роскомнадзор" in a:
        hints.append("rkn.gov.ru (пресс-релизы — наводки) и суд, выносивший постановление")
    if "роспотребнадзор" in a:
        hints.append("ГИС ЗПП zpp.rospotrebnadzor.ru, раздел судебной практики")
    if not hints:
        hints.append("по реквизитам из ссылки; орган в таблице не позволяет выбрать портал")
    return "; ".join(hints)


def main() -> None:
    clean = "--clean" in sys.argv
    if clean:
        for p in LEADS.rglob("*-P-[0-9][0-9][0-9].md"):
            p.unlink()
    manual_marks = set()
    for p in LEADS.rglob("*.md"):
        if p.name.lower() == "readme.md" or re.search(r"-P-\d{3}\.md$", p.name):
            continue  # README и сгенерированные карточки не считаются ручными пометками
        manual_marks |= set(re.findall(r"\bP-\d{3}\b", p.read_text(encoding="utf-8")))
    with (PR / "cases.tsv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    written = skipped = 0
    for r in rows:
        pid = r["practice_id"]
        if pid in manual_marks:
            skipped += 1
            continue
        folder = LEADS / FOLDER.get(r["scenario"], "other")
        folder.mkdir(parents=True, exist_ok=True)
        m = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", r["authority_date"] or "")
        date = f"{m.group(3)}{m.group(2)}{m.group(1)}" if m else "00000000"
        host = urlparse(r["url"] or "").netloc.removeprefix("www.") or "no-url"
        name = f"{date}-{host}-{pid}.md"
        norms = ", ".join(f"`{i}`" for i in r["norm_ids"].split(";") if i) or "в базе не заведены"
        lines = [
            f"# Наводка: {r['ui_aspect']} — {r['parties'] or 'стороны не указаны'} ({FOLDER.get(r['scenario'], r['scenario'])})",
            f"- Что (по таблице практики {pid}, пересказ составителя): {r['violation']} Итог по таблице: {r['outcome']}",
            f"- Норма (по таблице): {r['norm_text']}; нормы базы: {norms}",
            f"- Дело: {r['case']} · {r['authority_date']}",
            f"- Стороны: {r['parties'] or 'не указаны'}",
            f"- Где: {r['url'] or 'ссылка в таблице отсутствует'}",
            f"- Дата: {'дата акта по таблице ' + m.group(0) if m else 'полная дата в таблице не указана'}; дата публикации источника не проверялась",
            f"- Класс источника по таблице: {SRC.get(r['source_class'], r['source_class'])}",
        ]
        if pid in CARDS:
            lines.append(f"- Снимок карточки суда: `evidence/practice/cards/{CARDS[pid]}/` (реквизиты и стадия; текста постановления нет)")
        if pid in ARCHIVED:
            lines.append(f"- Пересечение с архивом: {ARCHIVED[pid]}")
        else:
            lines.append(f"- Первичка: не приложена; искать — {where_to_search(r['authority_date'] or '', r['case'] or '', r['url'] or '')}")
        lines.append(f"- Раздел таблицы: {r['section']} · сценарий: {r['scenario']} · источник карточки: `evidence/practice/cases.tsv` (сгенерировано `scripts/build_practice_leads.py`)")
        (folder / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
        written += 1
    total = sum(1 for _ in LEADS.rglob("*.md"))
    print(f"карточек создано: {written}; пропущено (есть ручная карточка): {skipped}; всего в leads/: {total}")


if __name__ == "__main__":
    main()
