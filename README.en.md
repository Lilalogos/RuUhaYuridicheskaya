# UhaYuridicheskaya — AppLaw-RU

[Русский](README.md) · **English**

A Claude skill that checks a screen of a Russian-market interface against registered Russian legal norms and returns a validated risk report. The skill ships with an evidence archive: court rulings, antitrust authority (FAS) decisions, statute texts, screen capture series, and a case-practice registry.

The skill follows a **cite-or-abstain** rule: every finding must name the article, the visible fact on the screen, and the source of the wording. If a link in that chain is missing, the skill abstains or marks the finding as conditional.

> A report is a risk assessment based on the supplied interface. It is not legal advice.

Most of the repository content, including the skill instructions, is in Russian.

## What it does

| Mode | What happens | Example request |
|---|---|---|
| **1. Screen assessment** | Screenshot → patterns → norms → a Report Contract v3 report in Russian that has passed the validator | "Check this checkout with AppLaw-RU" |
| **2. Evidence work** | Finding rulings, archiving them with sha256 and verbatim quotes, capturing screen series | "Phase A, scenario G1" |
| **3. Questions about the KB** | Which norms are covered, which rulings exist, what is missing | "Which cases do we have on Article 16 of the Consumer Protection Law?" |

Any screen is in scope: checkout, pricing, subscription, landing page, feed, catalogue, settings, sign-in. The jurisdiction is always the Russian Federation.

## What is inside

| Layer | Folder | Contents |
|---|---|---|
| **Knowledge base** | [`applaw/`](applaw/) | 77 norms (59 material, 18 procedural companions from the Code of Administrative Offences), 113 patterns in six families, 57 pattern-to-norm routes, 50 factual gates, 34 enforcement outcome records (6 eligible as benchmarks, 2 of them monetary), 35 source capsules with verbatim quotes, constitutions, the report contract, 18 validators |
| **Evidence** | [`evidence/`](evidence/) | 34 court and FAS acts (PDF with a text layer, sha256, `meta.yml`, `quotes.md`), 150 statute texts, 3 screen capture series, 214 lead cards, a practice registry of 190 cases, run journals |
| **References** | [`references/`](references/), [`docs/`](docs/) | Registries of norms, acts, captures and practice, an acts → norms → patterns map, verification of norms against statute texts, a gap list, fork history |
| **Tooling** | [`scripts/`](scripts/) | Wiring acts into the KB, generating registries, importing the practice spreadsheet, integrity checks |

Norm domains: the Consumer Protection Law and the Civil Code (price, consent, subscriptions, cancellation), Federal Law 38-FZ (advertising, ad labelling, mailings), 152-FZ (personal data), 149-FZ (social networks, recommender systems, authorisation), 436-FZ (children), symbols and prohibited content, interface language, finance, accessibility.

## How the skill reasons

The law is broken into five machine-checkable units:

- **Norm** — the article citation, who enforces it, the remedy, the limitations. Fine amounts are deliberately not stored.
- **Pattern** — detection cues and false-positive traps.
- **Route** — the link between patterns and norms, with required and disqualifying facts.
- **Factual gate** — a question about a fact on the screen. An unknown fact makes a finding conditional; it does not remove it.
- **Outcome** — a specific case with the court's posture and finality. Only final decisions serve as benchmarks.

A pattern becomes a finding once five gates pass: a visible element matches a cue, the traps are resolved, the effect on the buyer's decision is material, a material norm applies, and the finding stands on its own evidence. The number of findings is not capped: each pattern that passes gets its own block.

Screenshots, OCR, HTML and file names are evidence to the skill, not instructions. Directives embedded in a screen do not affect the assessment.

## Installation

**Claude Code.** Clone the repository into your skills folder:

```bash
git clone https://github.com/Lilalogos/RuUhaYuridicheskaya.git ~/.claude/skills/applaw-ru
```

The `applaw-ru` skill is then available in every session.

**Claude in chat.** Download the repository archive (Code → Download ZIP), attach it to a message and ask Claude to unpack it and use it as a skill in that conversation. The skill is active within that chat only.

**Dependencies.** The knowledge base and validators use only the Python 3 standard library. The tools in `scripts/` additionally need PyYAML, PyMuPDF, openpyxl and the poppler utilities (`pdftotext`, `pdffonts`).

## Checking that everything works

```bash
cd applaw && python3 -B scripts/validate_release.py --kb .
```

Expected result: `PASS: 15 check(s)`. The `-B` flag is required: `__pycache__` breaks the file count.

```bash
python3 -B scripts/evidence_check.py
```

Expected result: `целостность улик: OK` (evidence integrity: OK).

## Report format

Reports follow Report Contract v3. Section headings and field labels stay in English because the validator matches on them. All explanatory text is written in Russian.

Sections: `Assessment Summary` (a five-level risk label and a verdict), `Material Findings` (blocks F1, F2…), `Liability and Consequences` (blocks L1, L2…), `Mitigating and Low-Risk Elements`, `Observed Without a Mapped Norm`, `Missing Context`, `Priority Actions`, `Disclaimer`.

Every report passes the validator before it is returned:

```bash
python3 -B applaw/scripts/validate_live_report.py <report.md> --kb applaw
```

A sample with three findings: [`applaw/eval/report_samples/2026-10-14-ru-multi-finding-standard.md`](applaw/eval/report_samples/2026-10-14-ru-multi-finding-standard.md).

## Extending the skill

**A new act.** Put the document into `evidence/enforcement/<year>-<authority>-<number>/` following the rules in [`evidence/CLAUDE.md`](evidence/CLAUDE.md), add its placement to `OVERLAY` in the wiring script, and rebuild:

```bash
python3 -B scripts/build_evidence_capsules.py && python3 -B scripts/build_references.py && python3 -B scripts/refresh_release.py
```

**An edit inside `applaw/`.** Run `scripts/refresh_release.py` after any edit, otherwise validation fails on checksums. Do not change the `citation` field of a norm: the report validator matches on it.

**The practice spreadsheet.** Replace the xlsx in `evidence/practice/source/` and rebuild the registry and lead cards:

```bash
python3 -B scripts/import_practice_xlsx.py && python3 -B scripts/build_practice_registry.py && python3 -B scripts/build_practice_leads.py --clean
```

## Repository layout

```
SKILL.md                 skill entry point: three working modes
applaw/                  knowledge base, the portable applaw skill v0.5.0
  taxonomy/              norms, patterns, routes, gates, outcomes
  constitutions/         behaviour rules, session limits
  references/            report contract, A0–A8 workflow, citation policy
  sources/               source capsules
  scripts/               legal-slice builder and validators
  eval/                  report samples, fixtures, adversarial scenarios
evidence/
  enforcement/           court and FAS acts
  law/                   statute texts
  captures/              screen capture series
  leads/                 lead cards
  practice/              practice registry: spreadsheet, court cards, digests
  runs/                  run journals
  CLAUDE.md              evidence collection rules
references/              registries and maps, gap list
docs/                    fork history, specifications, proposals
scripts/                 build and verification tooling
```

## Limitations

- The norms rest on a secondary survey, "Правовая база РФ для проектирования интерфейсов" (the Russian legal framework for interface design). Check the current wording against the official text before release.
- Fine amounts are not stored: they change almost every year.
- A court act is evidence of a decision in one case. The skill does not use it as precedent beyond its own terms.
- Practice-registry rows and lead cards point to where primary sources can be found. They are not used as benchmarks in a report.
- Scenarios G4 (subscriptions, Article 16.1 of the Consumer Protection Law) and G5 (service cancellation) have no archived acts yet.
- Registry membership, whether a placement is paid, and the buyer's status cannot be established from a screenshot. Such findings are issued as conditional.

The full gap list: [`references/gaps.md`](references/gaps.md).
