#!/usr/bin/env python3
"""Реестр судебной и административной практики из таблицы оператора (evidence/practice).

Входы:
  evidence/practice/cases.tsv       — 190 строк «Все дела» + practice_id, norm_ids, scenario, source_class
  evidence/practice/not-found.tsv   — лист «Практика не найдена»
  evidence/practice/cards/*/card.pdf — снимки карточек судов (snapshot_card.py)
Выходы (производные, руками не править):
  evidence/practice/sections/NN-<slug>.md — дайджест каждого раздела, строки целиком
  evidence/practice/cards/INDEX.md        — реквизиты из текста карточек
  references/practice-registry.md         — сводка: покрытие по разделам и нормам, пробелы, компактные таблицы

Дисциплина: строки таблицы — наводки (leads), не первичка. Поля отчёта из них не заполняются;
в enforcement/ попадает только акт с текстовым слоем (evidence/CLAUDE.md §0.1–0.2).
Запуск: python3 -B scripts/build_practice_registry.py
"""
from __future__ import annotations

import csv
import re
import subprocess
import sys
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
PR = SKILL / "evidence" / "practice"
REFS = SKILL / "references"
KB = SKILL / "applaw"
sys.path.insert(0, str(KB / "scripts"))
from _kb import parse_yaml_items  # noqa: E402

SRC_LABEL = {"act_or_card": "текст акта или карточка суда", "news": "новости или обзор", "search": "только поисковая выдача"}
SCEN_LABEL = {
    "G1": "G1 предвыбранная платная допуслуга", "G2/G3": "G2/G3 обусловливание или обязательный сбор", "G3": "G3 сведения о продавце, товаре и цене до договора", "G4": "G4 подписка без электронного отказа", "G5": "G5 отказ от услуги, отмена", "platform": "platform — ответственность и штрафы площадок (289-ФЗ / 135-ФЗ, до P-04)",
    "G6": "G6 недостоверная реклама, таймеры, «№ 1»", "G7": "G7 рассылки без согласия", "G8": "G8 маркировка интернет-рекламы",
    "content": "content — контент, символика, статусы, модерация", "consent": "consent — согласия и формы ПДн",
    "security": "security — защита данных, утечки (видимые меры)", "вне-охвата:finance": "вне охвата скрин-чекера: подпись и финансы",
    "вне-охвата:ip": "вне охвата: интеллектуальная собственность", "вне-охвата:hr": "вне охвата: кадровый ЭДО и тайна",
    "вне-охвата:gov": "вне охвата: госсектор и приёмка", "вне-охвата:antitrust": "вне охвата: антимонопольные дела",
}


def esc(t: object) -> str:
    return str(t if t is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def short(t: object, n: int = 160) -> str:
    s = esc(t)
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def slug(section: str) -> str:
    num, _, name = section.partition(". ")
    tr = {"а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya"}
    s = "".join(tr.get(c, c) for c in name.lower())
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return f"{int(num):02d}-{s}"


def load_rows() -> list[dict]:
    with (PR / "cases.tsv").open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def load_not_found() -> list[dict]:
    with (PR / "not-found.tsv").open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def card_fields(pdf: Path) -> dict:
    text = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    out: dict[str, str] = {}
    m = re.search(r"^URL: (\S+)", text, re.M)
    out["url"] = m.group(1) if m else ""
    m = re.search(r"^UTC: (\S+)", text, re.M)
    out["utc"] = m.group(1) if m else ""
    labels = ["Уникальный идентификатор дела", "Номер дела", "Дата регистрации", "Привлекаемое лицо", "Cудья", "Судья", "Статья КоАП РФ", "Дата рассмотрения дела в первой инстанции", "Дата вступления в силу", "Результат"]
    for i, ln in enumerate(lines):
        if ln in labels and i + 1 < len(lines):
            val = lines[i + 1]
            if val not in labels and not val.startswith("Скопиров"):
                out.setdefault(ln.replace("Cудья", "Судья"), val)
    # «История состояний»: дата, затем «|», затем состояние (вкладка скрыта в HTML, но есть в тексте)
    states: list[tuple[str, str]] = []
    hist = text.split("История состояний", 1)[1] if "История состояний" in text else ""
    hl = [ln.strip() for ln in hist.splitlines() if ln.strip()]
    for i, ln in enumerate(hl):
        if re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", ln):
            j = i + 1
            while j < len(hl) and hl[j] == "|":
                j += 1
            if j < len(hl) and re.match(r"(Зарегистрировано|Рассмотрение|Назначено адм\. наказание|Обжаловано|Вступило в силу|Возвращено|Прекращено|Отменено|Передано)", hl[j]):
                states.append((hl[j], ln))
    if states:
        out["Состояния"] = "; ".join(f"{a} {b}" for a, b in OrderedDict.fromkeys(states))
    return out


def build_cards_index() -> str:
    dirs = sorted(p for p in (PR / "cards").iterdir() if p.is_dir())
    lines = ["# Снимки карточек судов (evidence/practice/cards)", "",
             "Снимок = сохранённая страница сайта суда (card.html + card.pdf с текстовым слоем, card.sha256, card.url.txt), сделан `scripts/snapshot_card.py`. Это подтверждение реквизитов и стадии дела, **не текст акта**: в `enforcement/` такие дела не заводятся, пока не приложен сам акт. Реквизиты ниже извлечены из текста карточки автоматически — сверять по card.pdf.", "",
             "| Папка | Номер дела | Привлекаемое лицо | Статья | Состояния по карточке | Снято (UTC) |", "|---|---|---|---|---|---|"]
    for d in dirs:
        pdf = d / "card.pdf"
        if not pdf.is_file():
            continue
        f = card_fields(pdf)
        lines.append(f"| `{d.name}` | {esc(f.get('Номер дела','—'))} | {esc(f.get('Привлекаемое лицо','—'))} | {esc(f.get('Статья КоАП РФ','—'))} | {esc(f.get('Состояния','—'))} | {esc(f.get('utc',''))} |")
    return "\n".join(lines)


def build_sections(rows: list[dict]) -> list[str]:
    (PR / "sections").mkdir(exist_ok=True)
    by = OrderedDict()
    for r in rows:
        by.setdefault(r["section"], []).append(r)
    names = []
    for section, items in by.items():
        name = slug(section) + ".md"
        names.append(name)
        out = [f"# {section} — практика из таблицы оператора (13.10.2026)", "",
               f"{len(items)} строк. Источник: `evidence/practice/source/sudebnaya-praktika-2026-10-13.xlsx`, лист «Все дела». Строки — наводки; номера дел, даты и суммы перед использованием сверять с текстами актов. Производный файл `scripts/build_practice_registry.py`.", ""]
        for r in items:
            out += [f"## {r['practice_id']} — {esc(r['ui_aspect'])}", "",
                    f"- Норма (по таблице): {esc(r['norm_text'])}",
                    f"- Нормы базы: {', '.join('`'+i+'`' for i in r['norm_ids'].split(';') if i) or 'в базе не заведены'}",
                    f"- Сценарий: {SCEN_LABEL.get(r['scenario'], r['scenario'])}",
                    f"- Дело: {esc(r['case'])} · {esc(r['authority_date'])}",
                    f"- Стороны: {esc(r['parties'])}",
                    f"- Описание (по таблице): {esc(r['violation'])}",
                    f"- Итог (по таблице): {esc(r['outcome'])}",
                    f"- Класс источника: {SRC_LABEL.get(r['source_class'], r['source_class'])}",
                    f"- Ссылка: {esc(r['url'])}", ""]
        (PR / "sections" / name).write_text("\n".join(out) + "\n", encoding="utf-8")
    return names


def build_registry(rows: list[dict], not_found: list[dict], section_files: list[str]) -> str:
    norms = {n["id"]: n for n in parse_yaml_items(KB / "taxonomy" / "norms.yml")}
    by_sec = OrderedDict()
    for r in rows:
        by_sec.setdefault(r["section"], []).append(r)
    L = ["# Реестр практики: судебные и административные дела по нормам для интерфейсов", "",
         f"{len(rows)} строк из таблицы оператора «Судебная практика» (составлена 13.10.2026; архив — `evidence/practice/source/`, sha256 в `source.sha256`). Машиночитаемая версия — `evidence/practice/cases.tsv`; полные дайджесты по разделам — `evidence/practice/sections/`; снимки карточек Таганского суда — `evidence/practice/cards/INDEX.md`. Производный справочник, генерируется `scripts/build_practice_registry.py`.", "",
         "**Статус в терминах базы:** каждая строка — наводка (lead). Она указывает, где искать первичку, но не является источником полей отчёта и не попадает в `enforcement_outcomes.yml`, пока акт не приложен с текстовым слоем и sha256 (evidence/CLAUDE.md §0.1–0.2). Класс источника по таблице: «текст акта или карточка суда» — документ открывался составителем таблицы; «новости или обзор» — пересказ; «только поисковая выдача» — ссылка не проверялась. Перед использованием номера дел, даты и суммы сверять с текстами актов.", "",
         "## Покрытие по разделам", "",
         "| Раздел | Строк | С актом/карточкой | Новости/обзор | Только выдача | Нормы базы, к которым привязано | Дайджест |", "|---|---:|---:|---:|---:|---|---|"]
    for sec, items in by_sec.items():
        c = Counter(r["source_class"] for r in items)
        ids = Counter(i for r in items for i in r["norm_ids"].split(";") if i)
        L.append(f"| {esc(sec)} | {len(items)} | {c.get('act_or_card',0)} | {c.get('news',0)} | {c.get('search',0)} | {', '.join('`'+k+'`' for k,_ in ids.most_common()) or '—'} | `sections/{slug(sec)}.md` |")
    L += ["", "## Покрытие по сценариям сбора улик", "", "| Сценарий | Строк | Из них с актом/карточкой |", "|---|---:|---:|"]
    sc = Counter(r["scenario"] for r in rows)
    sca = Counter(r["scenario"] for r in rows if r["source_class"] == "act_or_card")
    for k, v in sorted(sc.items(), key=lambda kv: (-kv[1], kv[0])):
        L.append(f"| {SCEN_LABEL.get(k,k)} | {v} | {sca.get(k,0)} |")
    L += ["", "## Нормы базы, по которым есть наводки", "", "| Норма базы | Цитата | Строк | Примеры (practice_id) |", "|---|---|---:|---|"]
    per_norm = defaultdict(list)
    for r in rows:
        for i in r["norm_ids"].split(";"):
            if i:
                per_norm[i].append(r["practice_id"])
    for nid, ids in sorted(per_norm.items(), key=lambda kv: -len(kv[1])):
        L.append(f"| `{nid}` | {short(norms.get(nid,{}).get('citation',''),90)} | {len(ids)} | {', '.join(ids[:8])}{'…' if len(ids)>8 else ''} |")
    L += ["", "## Нормы, названные в практике, но не заведённые в базе", "",
          "Строки без привязки к нормам базы (`norm_ids` пусто) — кандидаты в `references/gaps.md`. Заводить норму по строке таблицы нельзя: нужен текст закона (evidence/law) и, для исхода, текст акта.", "",
          "| Норма (по таблице) | Строк | Разделы |", "|---|---:|---|"]
    unm = defaultdict(list)
    for r in rows:
        if not r["norm_ids"]:
            unm[r["norm_text"]].append(r["section"].split(". ")[0])
    for k, v in sorted(unm.items(), key=lambda kv: -len(kv[1])):
        L.append(f"| {esc(k)} | {len(v)} | {', '.join(sorted(set(v), key=int))} |")
    L += ["", "## Лист «Практика не найдена» (по таблице)", "", "| № | Норма | К чему относится | Что известно |", "|---|---|---|---|"]
    for r in not_found:
        L.append(f"| {r['n']} | {esc(r['norm_text'])} | {esc(r['ui_aspect'])} | {esc(r['note'])} |")
    L += ["", "## Пересечения с архивом актов", "",
          "- P-079 «лоукостер», предустановленное согласие на «Полётную страховку», снимается кнопкой «Изменить» (обзор Гарант, 2024): по описанию совпадает с делом «Победы» в архиве — `2024-mosgorsud-33-35439` (Мосгорсуд, 22.08.2024) и наводки `evidence/leads/G1/`.",
          "- P-081, P-082 Delivery Club (сервисный сбор): в архиве семь актов по делу А40-284009/21 (`2022-asmsk-A40-284009-21-20220318` … `2023-asmo-F05-19574-2022-20230531`), итог — нарушения нет (`ineligible_no_finding`).",
          "- Остальные строки в `enforcement/` не представлены; P-022 («Победа», ПДн для рекламы, АС Новосибирской области) — другое дело, не G1.", "",
          "## Все строки (компактно)", ""]
    for sec, items in by_sec.items():
        L += [f"### {esc(sec)}", "", "| id | Норма | Интерфейс | Дело · орган, дата | Стороны | Итог (по таблице) | Источник |", "|---|---|---|---|---|---|---|"]
        for r in items:
            L.append(f"| {r['practice_id']} | {short(r['norm_text'],40)} | {short(r['ui_aspect'],60)} | {short(r['case'],40)} · {short(r['authority_date'],45)} | {short(r['parties'],35)} | {short(r['outcome'],110)} | {SRC_LABEL.get(r['source_class'],r['source_class']).split(' ')[0]} |")
        L.append("")
    return "\n".join(L)


def main() -> None:
    rows = load_rows()
    nf = load_not_found()
    names = build_sections(rows)
    (PR / "cards" / "INDEX.md").write_text(build_cards_index() + "\n", encoding="utf-8")
    (REFS / "practice-registry.md").write_text(build_registry(rows, nf, names) + "\n", encoding="utf-8")
    print(f"practice: {len(rows)} строк, {len(names)} разделов, карточек: {len([p for p in (PR/'cards').iterdir() if p.is_dir()])}; references/practice-registry.md {(REFS/'practice-registry.md').stat().st_size} bytes")


if __name__ == "__main__":
    main()
