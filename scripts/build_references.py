#!/usr/bin/env python3
"""Генерирует справочники навыка из данных базы и архива улик.

  references/laws-registry.md      — 72 нормы из applaw/taxonomy/norms.yml, по доменам
  references/evidence-registry.md  — 15 актов из evidence/enforcement (meta.yml + quotes.md + реестр исходов)
  references/captures-registry.md  — серии экранов из evidence/captures

Справочники — производные: правьте данные, не их. Запуск:
    python3 -B scripts/build_references.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

import yaml

SKILL = Path(__file__).resolve().parents[1]
KB = SKILL / "applaw"
EV = SKILL / "evidence"
REFS = SKILL / "references"
sys.path.insert(0, str(KB / "scripts"))
from _kb import parse_outcome_registry  # noqa: E402

DOMAINS = [
    ("Чекаут и потребительский договор (ЗоЗПП, ГК, 54-ФЗ, 289-ФЗ)", {
        "ru-zozpp-10", "ru-zozpp-12", "ru-zozpp-16", "ru-zozpp-16-1", "ru-zozpp-26-1", "ru-zozpp-32",
        "ru-gk-426", "ru-gk-oferta", "ru-54fz-receipt", "ru-289fz-platform", "ru-135fz-style-imitation",
        "ru-fap-82-air-addons", "ru-zozpp-16-1-digital-ruble", "ru-zozpp-16-1-installment-price"}),
    ("Реклама и промо (38-ФЗ, 162-ФЗ)", {
        "ru-38fz-5-3", "ru-38fz-18", "ru-38fz-18-1", "ru-38fz-9", "ru-38fz-6-child-ads", "ru-162fz-26",
        "ru-religious-symbols-promo", "ru-vpn-promotion-ban"}),
    ("Персональные данные и согласия (152-ФЗ, ФСТЭК)", {
        "ru-152fz-9", "ru-152fz-15", "ru-152fz-18-1", "ru-152fz-withdrawal", "ru-152fz-16",
        "ru-152fz-11-biometric", "ru-fstek-ui-measures"}),
    ("Информационное право (149-ФЗ, 236-ФЗ, СМИ)", {
        "ru-149fz-10-2", "ru-149fz-10-auth", "ru-149fz-10-2-2", "ru-social-network-duties",
        "ru-236fz-landing", "ru-media-imprint", "ru-interface-language"}),
    ("Контент и символика (госсимволы, запрещённая информация, иноагенты, карты)", {
        "ru-state-symbols", "ru-victory-symbols", "ru-extremist-symbols", "ru-banned-orgs-presence",
        "ru-lgbt-symbolism", "ru-territorial-maps", "ru-foreign-agent-labeling", "ru-drug-symbols",
        "ru-undesirable-orgs"}),
    ("Дети (436-ФЗ)", {"ru-age-marking", "ru-child-access-barriers", "ru-436fz-child-sections"}),
    ("Финансы (353-ФЗ, 259-ФЗ, антифрод)", {
        "ru-353fz-psk-frame", "ru-353fz-7-addons-cooling", "ru-259fz-no-crypto", "ru-antifraud-foreign-messengers", "ru-cbr-3854u-cooling"}),
    ("Госсектор, доступность, ИИ, изображение (ПП 236/102, ГОСТ, 181-ФЗ, ГК 152.1)", {
        "ru-pp-236-eforms", "ru-pp-102-a11y", "ru-gost-52872", "ru-181fz-15-captions",
        "ru-ai-generation-rights", "ru-gk-152-1-likeness"}),
]


def md_escape(text: object) -> str:
    return " ".join(str(text if text is not None else "").split()).replace("|", "\\|")


def short(text: object, limit: int = 220) -> str:
    s = md_escape(text)
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def build_laws() -> str:
    norms = yaml.safe_load((KB / "taxonomy" / "norms.yml").read_text(encoding="utf-8"))
    routes = yaml.safe_load((KB / "taxonomy" / "jurisdiction_routes.yml").read_text(encoding="utf-8"))
    patterns = yaml.safe_load((KB / "taxonomy" / "patterns.yml").read_text(encoding="utf-8"))
    by_id = {n["id"]: n for n in norms}
    routes_by_norm: dict[str, list[str]] = defaultdict(list)
    for r in routes:
        for nid in r.get("candidate_norms") or []:
            routes_by_norm[nid].append(r["id"])
    patterns_by_norm: dict[str, list[str]] = defaultdict(list)
    for p in patterns:
        for nid in p.get("maps_to_norms") or []:
            patterns_by_norm[nid].append(p["id"])
    companions: dict[str, list[str]] = defaultdict(list)
    for n in norms:
        for mid in n.get("companion_to_material_norm_ids") or []:
            companions[mid].append(n["id"])

    material = [n for n in norms if n["type"] == "material"]
    procedural = [n for n in norms if n["type"] == "procedural"]
    out = [
        "# Реестр российских норм навыка AppLaw-RU",
        "",
        f"Производный справочник (`scripts/build_references.py`) по `applaw/taxonomy/norms.yml`: "
        f"{len(norms)} записей — {len(material)} материальных обязанностей интерфейса и {len(procedural)} процедурных составов КоАП.",
        "",
        "Источник всех записей — обзорный PDF «Правовая база РФ для проектирования интерфейсов» (капсула `src-0116437c998bcd82`, редакция 2026-09-29) "
        "плюс точечная сверка с pravo.gov.ru (отражена в `verified_as_of` и `citation`). Это вторичный источник: `availability: partial` у каждой нормы, "
        "перед выпуском сверять редакцию по КонсультантПлюс/Гарант/pravo.gov.ru. Суммы штрафов в базе не хранятся намеренно — только статьи.",
        "",
        "Обозначения: **Маршруты** — id из `jurisdiction_routes.yml`, через которые норма достигает отчёта; **Паттерны** — id детекторов из `patterns.yml` с `maps_to_norms`; "
        "**Компаньон** — процедурный состав, который может сопровождать находку, но никогда не является её первичной нормой; «проверить» — метка самого обзора.",
        "",
    ]
    seen: set[str] = set()
    for title, ids in DOMAINS:
        out += [f"## {title}", ""]
        out += ["| id | Норма и редакция | В силе / сверка | Орган | Маршруты | Паттерны | Компаньоны КоАП | Условности |", "|---|---|---|---|---|---|---|---|"]
        for n in material:
            if n["id"] not in ids:
                continue
            seen.add(n["id"])
            flags = []
            text_all = " ".join(str(n.get(k, "")) for k in ("citation", "instrument", "penalty_basis", "limitations", "enforcer"))
            if "проверить" in text_all or "сверить" in text_all:
                flags.append("метка «проверить»")
            if "Не установлено" in str(n.get("enforcer", "")):
                flags.append("орган не установлен")
            if n.get("eligible_outcome_ids"):
                flags.append("есть пригодный исход: " + ", ".join(n["eligible_outcome_ids"]))
            out.append("| `{id}` | {inst} | {cit} | {enf} | {routes} | {pats} | {comp} | {flags} |".format(
                id=n["id"], inst=short(n.get("instrument"), 200), cit=short(n.get("citation_detail") or n.get("citation"), 200),
                enf=short(n.get("enforcer"), 90),
                routes=", ".join(f"`{r}`" for r in routes_by_norm.get(n["id"], [])) or "—",
                pats=", ".join(f"`{p}`" for p in patterns_by_norm.get(n["id"], [])) or "—",
                comp=", ".join(f"`{c}`" for c in companions.get(n["id"], [])) or "—",
                flags="; ".join(flags) or "—",
            ))
        out.append("")
    missing = [n["id"] for n in material if n["id"] not in seen]
    if missing:
        out += ["## Прочие материальные нормы", "", "| id | Норма |", "|---|---|"]
        out += [f"| `{m}` | {short(by_id[m].get('instrument'))} |" for m in missing] + [""]

    out += ["## Процедурные составы КоАП (компаньоны)", "", "| id | Состав | Компаньон к | Суммы (только если называет сам PDF) |", "|---|---|---|---|"]
    for n in procedural:
        out.append("| `{id}` | {inst} | {to} | {pen} |".format(
            id=n["id"], inst=short(n.get("instrument"), 160),
            to=", ".join(f"`{m}`" for m in n.get("companion_to_material_norm_ids") or []) or "—",
            pen=short(n.get("penalty_basis"), 200)))
    out.append("")

    out += ["## Ключевые даты вступления в силу (для effective-date-гейтов)", "",
            "| Дата | Что | Нормы |", "|---|---|---|",
            "| 01.09.2022 | ст. 16 ЗоЗПП в ред. 135-ФЗ (недопустимые условия, лишние ПДн) | `ru-zozpp-16` |",
            "| 01.10.2023 | 149-ФЗ ст. 10.2-2 — плашка о рекомендательных технологиях (408-ФЗ) | `ru-149fz-10-2-2` |",
            "| 01.12.2023 | 149-ФЗ ст. 10 — авторизация только российскими способами (406-ФЗ) | `ru-149fz-10-auth` |",
            "| 01.03.2024 | 149-ФЗ ст. 15.8 — запрет популяризации средств обхода блокировок | `ru-vpn-promotion-ban` |",
            "| 01.03.2025 | самозапрет на кредиты (31-ФЗ) | `ru-353fz-7-addons-cooling` |",
            "| 01.09.2025 | п. 3.1 ст. 16 ЗоЗПП (69-ФЗ): запрет автоматических отметок о согласии, возврат за навязанное — 3 дня; 156-ФЗ: согласие на ПДн отдельно от договора | `ru-zozpp-16`, `ru-152fz-9` |",
            "| 01.03.2026 | ст. 16.1 ЗоЗПП (376-ФЗ): электронный отказ от сохранённых реквизитов и автопродления; 168-ФЗ: русский язык потребительского интерфейса; ПП 102: доступность госсайтов; правила религиозных символов | `ru-zozpp-16-1`, `ru-interface-language`, `ru-pp-102-a11y`, `ru-religious-symbols-promo` |",
            "| лето 2026 («проверить») | составы КоАП 13.55 (авторизация) и 13.56 (рекомендательные технологии) — закон подписан 26.06.2026 | `ru-koap-13-55`, `ru-koap-13-56` |",
            "| 01.09.2026 («проверить реквизиты») | закон об ИИ: права на сгенерированный результат, кнопка пометки ИИ-контента | `ru-ai-generation-rights` |",
            "| 01.10.2026 | 289-ФЗ — платформенная экономика (реестр ПЦП) | `ru-289fz-platform` (ждёт паттерн P-04) |",
            ""]
    return "\n".join(out)


def read_meta(path: Path) -> dict:
    meta: dict = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith((" ", "\t", "#")):
            continue
        key, sep, rest = raw.partition(":")
        if not sep:
            continue
        value = re.split(r"\s{2,}#", rest, maxsplit=1)[0].strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        meta[key.strip()] = value
    # norms_cited: список
    text = path.read_text(encoding="utf-8")
    m = re.search(r"(?ms)^norms_cited:.*?\n(?=\S)", text + "\nEND")
    norms = re.findall(r'^\s+- "([^"]+)"', m.group(0), re.M) if m else []
    meta["norms_cited_list"] = norms
    notes = re.search(r"(?ms)^notes: >-\n(.*?)(?=^\S|\Z)", text)
    meta["notes_text"] = " ".join(l.strip() for l in notes.group(1).splitlines()) if notes else ""
    return meta


def build_evidence() -> str:
    _, outcomes = parse_outcome_registry(KB / "taxonomy" / "enforcement_outcomes.yml")
    by_folder = {o["evidence_folder"].split("/")[-1]: o for o in outcomes}
    capsules = json.loads((KB / "sources" / "source_capsules.json").read_text(encoding="utf-8"))["sources"]
    caps_by_folder = {c.get("evidence_folder", "").split("/")[-1]: c for c in capsules if c.get("evidence_kind") == "enforcement_act"}

    folders = sorted(p for p in (EV / "enforcement").iterdir() if p.is_dir())
    out = [
        "# Реестр улик: судебные акты и решения ФАС/Роспотребнадзора",
        "",
        f"{len(folders)} первичных документов в `evidence/enforcement/<id>/` (source.pdf с текстовым слоем, source.sha256, source.url.txt, meta.yml, quotes.md). "
        "Каждый вшит в базу как капсула источника (`applaw/sources/source_capsules.json`, постраничный текст + якоря-цитаты) и запись реестра исходов "
        "(`applaw/taxonomy/enforcement_outcomes.yml`). Производный справочник — `scripts/build_references.py`.",
        "",
        "Роли сторон — процессуальные, как в документе: в арбитражных делах об оспаривании штрафа «заявитель» — компания, «ответчик» — управление Роспотребнадзора. "
        "Дисциплина: поля заполнены только из текста самого акта; «Не установлено по приложенным источникам» — честный пропуск. Наводки без текста акта лежат отдельно в `evidence/leads/` и источником полей не являются.",
        "",
        "## Сводная таблица",
        "",
        "| id (папка) | Сценарий | Орган, дата | Ответчик / сайт | Суть по акту | Исход | Финальность | Ориентир (benchmark) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for f in folders:
        meta = read_meta(f / "meta.yml"); o = by_folder.get(f.name, {})
        out.append("| `{id}` | {sc} | {auth}, {date} | {resp} / {site} | {matter} | {sanction} | {fin} | `{elig}` |".format(
            id=f.name, sc=o.get("scenario", meta.get("scenario", "")), auth=short(meta.get("authority"), 70), date=meta.get("decision_date", ""),
            resp=short(meta.get("respondent"), 60), site=short(meta.get("site_or_app"), 40),
            matter=short(o.get("matter_name", ""), 140), sanction=short(meta.get("sanction"), 160),
            fin=short(o.get("finality", ""), 120), elig=o.get("benchmark_eligibility", "")))
    out += ["", "Пригодные ориентиры (`eligible_*`) — только те, чья финальность подтверждена приложенным актом и где нарушение установлено. "
            "`ineligible_no_finding` — итоговые акты, где нарушения НЕ нашли (контрпримеры для ловушек ложных срабатываний). "
            "`ineligible_non_final` — финальность не следует из приложенного текста, акт отменён или промежуточный: поднять до eligible можно только приложив акт вышестоящей инстанции или карточку о вступлении в силу (см. gaps.md).", ""]

    out += ["## Карточки актов", ""]
    for f in folders:
        meta = read_meta(f / "meta.yml"); o = by_folder.get(f.name, {}); c = caps_by_folder.get(f.name, {})
        quotes = (f / "quotes.md").read_text(encoding="utf-8").splitlines()
        qlines = [l.strip() for l in quotes if l.strip().startswith("**стр.")]
        out += [f"### `{f.name}`", "",
                f"- **Сценарий:** {o.get('scenario', '')} · **Тип акта:** {meta.get('act_type', '')} · **Орган:** {meta.get('authority', '')} · **Дата:** {meta.get('decision_date', '')} · **Дело:** {meta.get('case_number', '')}",
                f"- **Ответчик:** {meta.get('respondent', '')} · **Заявитель/истец:** {meta.get('applicant', '')} · **Сайт:** {meta.get('site_or_app', '')}",
                f"- **Нормы, названные в акте:** {'; '.join(meta.get('norms_cited_list') or []) or '—'}",
                f"- **Нормы базы:** {', '.join(f'`{n}`' for n in (o.get('linked_norm_ids') or []))} · **Паттерны (предварительно, подтверждает Виталий):** {', '.join(f'`{p}`' for p in (o.get('linked_patterns_or_practices') or []))}",
                f"- **Исход по акту:** {meta.get('sanction', '')}",
                f"- **Посадка в реестре:** {o.get('posture', '')} · **Финальность:** {o.get('finality', '')} · **Ориентир:** `{o.get('benchmark_eligibility', '')}`",
                f"- **Сопоставимость:** {o.get('comparability_notes', '')}",
                f"- **Ограничения:** {o.get('limitations', '')}",
                f"- **Капсула:** `{c.get('source_id', '')}` · страниц: {c.get('original_document', {}).get('pages', '')} · якорей-цитат: {len(c.get('anchors', []))} · sha256: `{c.get('original_document', {}).get('sha256', '')[:16]}…`",
                f"- **Источник:** {meta.get('source_url', '')}",
                f"- **Примечания из meta.yml:** {meta.get('notes_text', '') or '—'}",
                "- **Цитаты (дословно, со страницей):**"]
        out += [f"  - {q}" for q in qlines]
        out.append("")
    return "\n".join(out)


def build_captures() -> str:
    series = sorted(p for p in (EV / "captures").iterdir() if p.is_dir())
    out = ["# Реестр серий экранов (captures)", "",
           f"{len(series)} серий в `evidence/captures/<сценарий>-<домен>-<дата>/`: PNG каждого шага, PDF/DOM ключевых экранов, capture-log.json (URL, UTC, sha256, заметка без оценок), manifest-draft.md (разметка Виталия), SHA256SUMS.txt.",
           "", "| Серия | Акт-основание | Шагов | PDF | Где закончилась | pattern_visible | Класс (разметка) |", "|---|---|---|---|---|---|---|"]
    details = []
    for s in series:
        log = json.loads((s / "capture-log.json").read_text(encoding="utf-8"))
        manifest = (s / "manifest-draft.md").read_text(encoding="utf-8")
        cls = re.search(r"Класс \(gold / clean\): (.+)", manifest)
        pdfs = sum(1 for st in log["steps"] if st["files"].get("pdf"))
        last = log["steps"][-1]
        out.append("| `{n}` | `{ref}` | {steps} | {pdfs} | {last} | {pv} | {cls} |".format(
            n=s.name, ref=log.get("enforcement_ref", ""), steps=len(log["steps"]), pdfs=pdfs,
            last=short(f"{last['n']:02d} {last['label']} — {'; '.join(log.get('stops') or []) or 'экран перед оплатой'}", 160),
            pv=log.get("pattern_visible", ""), cls=short(cls.group(1) if cls else "", 60)))
        details += [f"### `{s.name}`", "", f"- viewport: {log.get('viewport')} · locale: {log.get('locale')} · начало: {log.get('started_utc')}",
                    f"- стопы: {'; '.join(log.get('stops') or []) or '—'}", f"- заметки: {log.get('notes', '')}", "", "| № | Экран | URL | Файлы | Заметка агента |", "|---|---|---|---|---|"]
        for st in log["steps"]:
            files = ", ".join(v for v in (st["files"].get("png"), st["files"].get("pdf")) if v)
            details.append(f"| {st['n']:02d} | {md_escape(st['label'])} | {md_escape(st['url'])[:90]} | {md_escape(files)} | {short(st.get('agent_note'), 260)} |")
        details.append("")
    out += ["", "Единственная полная серия — uralairlines.ru (15 кадров, 5 PDF с текстовым слоем): паттерн акта 2023 года на экране не наблюдался, все допуслуги подключаются кнопкой «Добавить»/«Да», страховка — явными переключателями «Да, мне нужна защита» / «Нет, спасибо»; Виталий разметил серию как **clean** (2026-10-04). Серии pobeda.aero и iraero.ru прерваны блокировкой по IP / сбоем движка Websky и в gold/clean не годятся.", ""]
    return "\n".join(out + details)


def main() -> None:
    REFS.mkdir(exist_ok=True)
    (REFS / "laws-registry.md").write_text(build_laws() + "\n", encoding="utf-8")
    (REFS / "evidence-registry.md").write_text(build_evidence() + "\n", encoding="utf-8")
    (REFS / "captures-registry.md").write_text(build_captures() + "\n", encoding="utf-8")
    for name in ("laws-registry.md", "evidence-registry.md", "captures-registry.md"):
        print(name, (REFS / name).stat().st_size, "bytes")


if __name__ == "__main__":
    main()
