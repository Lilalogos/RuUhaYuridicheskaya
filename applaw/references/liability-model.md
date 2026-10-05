# Liability Model

Read this reference whenever a task adds, reviews, or reports liability, remedies, penalties, redress, damages, enforcement outcomes, or case-specific estimates.

## Public Wording

Keep direct legal citations and required posture labels accurate. Describe the route, limits, uncertainty, and practical consequence in plain language. Do not copy source-file legalese into the report narrative.

## Evidence Chain

Resolve in this order:

1. visible finding;
2. explicitly supplied canonical jurisdiction/country and a supported material norm;
3. actor, transaction, factual-trigger, effective-date, availability, and source-anchor gates;
4. an optional procedural enforcement or remedy companion declared for that material norm;
5. consumer, public, private, monetary, and non-monetary routes;
6. eligible final outcome matching the explicit country scope, if a comparator is useful;
7. estimate gate.

A pattern label is never a liability conclusion. A procedural norm is never the primary duty derived from a visual pattern and cannot support liability without a surviving material norm.

## Three Monetary Layers

### Statutory ceiling

State the exact maximum or formula, unit, legal predicate, and adjustment/effective date. Label it `not an expected outcome`.

### Observed enforcement benchmark

Use only `eligible_monetary` or `eligible_non_monetary` records from `taxonomy/enforcement_outcomes.yml`. State the matter, date, posture, amount type, legal basis, similarity, and non-predictive limits. Do not use complaints, pending matters, proposed orders, no-finding commitments, press-release-only records, or superseded routes.

### Case-specific estimate

Require jurisdiction, actor, relevant turnover, affected consumers, charges, duration, conduct, knowledge, prior orders, injury, redress already paid, defenses, and methodology. If those inputs are insufficient, use exactly:

`Estimate status: Not estimable from the supplied interface and business data.`

## Posture Ladder

- allegation or complaint: theory only;
- pending proceeding: unresolved;
- undertaking or commitment: corrective conduct, usually no finding;
- consent order: final within its terms, not judicial precedent;
- settlement: enforcement outcome, not precedent;
- final administrative notice or decision: final regulator outcome, subject to appeal metadata;
- court order: binding relief within its terms;
- judgment: precedential only to the extent the legal system gives it precedential weight.

## Amount Types

Keep public penalty, consumer redress, refund, damages, settlement payment, suspended judgment, turnover ceiling, per-day amount, and aggregate multi-breach amount separate. Never sum a suspended face judgment with its payable amount. Never allocate an aggregate amount without an official allocation.

## Scope Traps

- КоАП amounts are never stated: the attached survey deliberately stores the article, not a figure, because sums change almost yearly.
- КоАП 14.8 is a procedural companion only; consumer money flows through the material routes (Art. 12; the three-day refund of п. 3.1 Art. 16; actual costs under Art. 32).
- A refund for the unused subscription period is marked by the survey as practice, not the letter of the norm.
- 289-ФЗ reaches only registry-listed intermediary platforms, and registry membership is never visible on a screen.
- There is no dedicated reviews rule in the attached sources; fabricated social proof qualifies only as an untrue advertising assertion under Art. 5 pt. 3.
- The enforcement-outcome registry holds the archived RU acts from `evidence/enforcement` (court and FAS decisions, sha256-verified). Only records marked `eligible_*` may populate `Observed enforcement benchmark`: `eligible_monetary` — НордСтар А33-35161/2019 (решение 29.01.2020, кассация АС ВСО 23.10.2020 не подлежит обжалованию) and А33-536/2022 (решение 24.03.2022, апелляция 14.06.2022): 10 000 ₽ each by ч. 2 ст. 14.8 for a mandatory 550 ₽ booking fee — one matter, one amount, never summed with its appellate/cassation twins (`ineligible_source_only`); `eligible_non_monetary` — the ИрАэро pair (Куйбышевский районный суд г. Иркутска, 24.01.2024; 8КСОЮ, 18.02.2025) and Нордстар (Железнодорожный районный суд г. Красноярска, 26.03.2025; апелляционное определение Красноярского краевого суда 33-10269/2025 от 03.09.2025) under ст. 16 ЗоЗПП — a non-monetary outcome (признание противоправности, публикация решения), never a fine figure. Every other record is `ineligible_non_final` (finality not stated in the attached act, reversed, or pending) or `ineligible_no_finding` (the Delivery Club «сервисный сбор» chain: no violation found — a false-positive counterexample, cite it only as a limit on the mandatory-fee pattern, never as a benchmark). Observed administrative fines (10 000 ₽ by ч. 2 ст. 14.8 in the НордСтар and first-round Delivery Club acts; 4 000 / 100 000 ₽ by ч. 1 ст. 14.3 in the Челябинск «Победа» orders; 400 000 ₽ by ч. 4.1 ст. 14.3 in the Россельхозбанк and Агроторг mailing orders) are recorded as metadata on ineligible records and must not be quoted as expected outcomes.

## Authoring And Validation

- Keep duties and ceilings in `taxonomy/norms.yml`.
- Keep dated outcomes in `taxonomy/enforcement_outcomes.yml`.
- Link eligible records in both directions through norm and outcome ids.
- Store official URLs and pinpoints in the KB; show short citations in public reports.
- Run `validate_enforcement_outcomes.py` and `validate_report.py` after changes.

