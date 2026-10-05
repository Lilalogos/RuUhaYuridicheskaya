# Журнал зачистки иностранного права (RU-форк, 2026-10-01)

## Удалено — 23 проектных документа docs/ об US/EU/UK-праве
applaw-spec-v1.3, applaw-spec-v2, core-decisions-2026-09-03, decisions, design-brief-applaw, design-parity-2026-09-27, factual-gates-2026-09-03, first-live-run-2026-09-03, liability-research-2026-09, norms-added-2026-09-03, norms-shopping-list, perf-architecture-review-2026-08-13, quiz-applaw-v2-2026-09-26, routing-pass-1/2/3-2026-09-03, spec-ai-core-misha-norms, spec-ai-core-vitaly-patterns, spec-kb-gap-analysis, tasks-misha-2026-08-14, tasks-misha-2026-09-03, tasks-vitaliy-2026-08-14, unmapped-norms.
Оставлены: все ru-*.md и чисто операционные (deploy-*, environments, promo-codes-howto, setup-google-oauth-ga4, users-notion-sync, stage-test-invite, mobile-audit, design-corrections-mobile, core-hardening).

## Портировано на русское право (замена, не удаление)
- **Приложение:** components/landing/ScopeSlider.tsx (копирайт скоупа), components/wizard/Wizard.tsx (сообщение о поддерживаемом рынке), lib/checks.ts (SUPPORTED_JURISDICTIONS → "RU,OTHER"; метки рынков), lib/verdict-card.ts (детектор юрисдикции по тексту вердикта → RU-маркеры), config/landing.ts (AUTHORITY_SHORT → ФАС/Роспотребнадзор; MATTER_SHORT пуст — RU-решений в источниках нет; NORM_STRIP, IN/OUT_SCOPE, REPORT_SAMPLE → русские нормы), config/kb-stats.json (пересобран из RU-базы: 7 норм, 6 маршрутов, 0 решений), council/stub/index.ts (стаб-отчёт: ст. 16.1 + 38-ФЗ ст. 5 ч. 3, Роспотребнадзор, RU-блок ответственности).
- **kb/references:** citation-policy (модуль отзывов → маршрут недостоверной рекламы 38-ФЗ 5 ч. 3), cumulative-assessment (переписан целиком под RU-опоры: ст. 8–10 «итог без сюрпризов», 5 ч. 3/7, ст. 16+ГК 438; честно указано, что общей кодификации «overall presentation» в источниках нет), liability-model (Scope Traps → шесть RU-ловушек), kb-schema (примеры нормы и маршрута → ru-записи), report-contract (единственная правка — пример «ещё не вступившего режима» обезличен; обязательные фразы контракта не тронуты).
- **Фикстуры:** adversarial cite-01 (докет-давление → ст. 16.1 + капсула src-0116…), cite-03 (выдумывание иностранного аналога: теперь оператор просит «американский аналог ст. 16.1» — агент обязан отказаться: база держит только RU), output_safety (FTC → Роспотребнадзор), сэмпл longevitycompass (строка про Member State → нейтральная), TODO.placeholders строка 11 → RU-состояние покрытия.

## Оставлено сознательно (и почему)
1. **scripts/validate_report.py — маркеры FTC/CMA/EU/CNIL/ACM и регэксп `(?:us|eu|uk|ru)-`.** Это защита, а не право: упоминание иностранной власти в отчёте без неё в преамбуле — автоматический reject; леак-детектор ловит внутренние id всех четырёх префиксов. Удаление ослабило бы валидатор.
2. **Вектор `country-specific-authority-without-country-reject` (текст про CNIL/French DPA).** Обязательный негативный тест из required-набора: проверяет, что чекер отвергает чужую страновую власть. Это тест-приманка, а не норма базы.
3. **Amazon Prime / Trustpilot / Facebook в policy-fixtures, scoring-rubric, citation-policy, report-contract.** Это бренд-примеры поведенческого social-proof-модуля, дословно зашитые в контракт и parity-валидатор (REFERENCE_REQUIREMENTS, сценарии SP01–SP11), а не право ЕС/США. Русификация этих примеров возможна только согласованной правкой контракта + валидатора одним шагом — предложено отдельным решением оператора.
4. **package-lock.json** — совпадения в именах зависимостей, к праву отношения не имеют.

## Проверки
Полный релизный контур после зачистки: **PASS 15/15** (126 файлов в kb). Правки .ts — строковые литералы; сборка Next-приложения в этой среде не выполнялась (node_modules исключены из форка) — прогоните `npm ci && npm run build` на своей стороне.
