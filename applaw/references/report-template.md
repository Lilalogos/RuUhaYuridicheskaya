# Interface Risk Assessment: <Продукт или поток>

Используйте в значениях простой разговорный язык. Формальные юридические формулировки держите только внутри прямых цитат или точных строк контракта. Заголовки и метки полей — фиксированные английские токены схемы; правила языка и полей см. в `output-style.md`.

Начинайте с этого заголовка и не добавляйте вводной прозы. Сохраняйте каждую секцию второго уровня. Если ни одна находка уровня Medium/High не поддерживается, замените примерные блоки F и L литералом `None.` в соответствующих секциях. Провалидируйте полный итоговый текст с помощью `validate_live_report.py`, исправьте все ошибки и верните его без изменений.

По умолчанию опускайте строку `Evidence integrity:`. Только когда начальный промпт оператора явно требует раскрытия, добавьте ровно одну строку не более 30 слов сразу после `Verdict` и провалидируйте с `--evidence-integrity-requested`. Рассчитайте унаследованный балл приватно и никогда его не раскрывайте.

Assessment date: YYYY-MM-DD
Jurisdictions assessed: <Явный целевой охват и материальные ограничения, или Not established; no jurisdiction-specific legal conclusion was made.>

## Assessment Summary

RISK: <very low|low|medium|high|very high>
Verdict: <Максимум 80 слов>

## Material Findings

### F1 - <Заголовок находки>

Severity: <Medium|High>
Observed evidence: <Что видимо на экране>
Pattern: <Человекочитаемые имена паттернов>
Risk explanation: <Что может пойти не так для покупателя, простым языком>
Applicable norm: <Прямая цитата нормы, за которой следует объяснение простым языком>
Comparable KB authority: <Дело или источник права и процессуальная позиция>
Linked liability blocks: <L1>
Confidence and limitations: <High|Medium> - <Материальные ограничения>
Recommended correction: <Конкретное изменение продукта, UX, чекаута или процесса>

## Liability and Consequences

### L1 - <Юрисдикция и категория экспозиции>

Linked findings: <F1>
Liability trigger: <Простым языком: что заставит правило применяться>
Consumer or contract remedies: <Простым языком: какая помощь может быть доступна, или none identified>
Public enforcement: <Кто может действовать и что может сделать, простым языком>
Private exposure: <Простым языком: какие ещё требования могут существовать, или почему ничего не выявлено>
Monetary exposure: Statutory ceiling - not an expected outcome: <Формула, предикат, единица и дата>
Observed enforcement benchmark: <Допустимый финальный исход, описанный просто, с процессуальной позицией и ограничениями, или None identified.>
Non-monetary orders: <Описание допустимых предписаний простым языком, или None identified>
Authority citations: <Краткие прямые цитаты>
Estimate status and limitations: Estimate status: Not estimable from the supplied interface and business data. <Прочие ограничения>

## Mitigating and Low-Risk Elements

- <Компактный смягчающий факт, изложенный просто>

## Observed Without a Mapped Norm

- <Имя паттерна простым языком>: <что на экране>. Сопоставленная норма или пример правоприменения для этого в предоставленном материале не найдены.

## Missing Context

- <Факт простым языком, который мог бы материально изменить результат>

## Priority Actions

- <Конкретное действие по продукту или процессу>
- <Второе конкретное действие>
- <Третье конкретное действие>

## Disclaimer

This report is a risk assessment based on the supplied interface and available context. It is not legal advice.
