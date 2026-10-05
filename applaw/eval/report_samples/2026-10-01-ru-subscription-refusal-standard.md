# Interface Risk Assessment: RU Subscription Refusal Fixture

Assessment date: 2026-10-01
Jurisdictions assessed: Russian Federation (survey-based federal analysis; consumer-scope and billing facts require separate confirmation).

## Assessment Summary

RISK: high
Verdict: The checkout foregrounds a low daily price while the materially larger recurring charge sits in weaker text, and the account exposes no electronic way to refuse the saved card or switch off auto-renewal. Under the stated Russian scope, the interface supports a material subscription-refusal concern pending review of the final billing and refusal-path sequence.

## Material Findings

### F1 - Recurring charge is subordinated to daily pricing

Severity: High
Observed evidence: The selected plan highlights a daily amount, while weaker text states a larger recurring charge every four weeks until cancellation.
Pattern: Hidden renewal; daily-price framing; delayed price disclosure
Risk explanation: The primary commercial impression may leave the consumer without equal prominence for the recurring amount and billing cadence before enrollment.
Applicable norm: ст. 16.1 Закона РФ от 07.02.1992 N 2300-1 (в ред. ФЗ от 15.10.2025 N 376-ФЗ, в силе с 01.03.2026) requires pre-subscription disclosure of the charge amount and cadence and an electronic refusal path for saved payment credentials.
Comparable KB authority: No comparable final case authority is recorded in the supplied KB; the statutory posture rests on the survey source alone.
Linked liability blocks: L1
Confidence and limitations: Medium - The pricing hierarchy is visible, but the final billing screen, consent record, saved-card controls, and refusal-path behavior were not supplied.
Recommended correction: Display the total initial charge, recurring charge, cadence, and cancellation method with equal prominence before billing information and again at final authorization.

## Liability and Consequences

### L1 - Russian online subscription-refusal exposure

Linked findings: F1
Liability trigger: A consumer subscription enables recurring charges from saved payment credentials while the product offers no electronic self-service refusal, with consumer status and the post-01.03.2026 contract date established.
Consumer or contract remedies: Charges after an expressed refusal are prohibited; the consumer may also refuse the service at any time paying only the executor's actual costs where that route applies.
Public enforcement: Rospotrebnadzor supervises consumer-rights compliance and may pursue the administrative route under ст. 14.8 КоАП РФ where its predicates are established.
Private exposure: The attached sources do not describe a standalone private action under this article; consumer claims proceed through the material consumer-law routes with separate proof.
Monetary exposure: Statutory ceiling - not an expected outcome: no verified ceiling is selected for this report; the attached survey stores the article rather than a figure because amounts change almost yearly.
Observed enforcement benchmark: None identified.
Non-monetary orders: Working electronic refusal controls, a recorded refusal date and time, corrected disclosures, and cessation of post-refusal charges may be required where authorized.
Authority citations: ст. 16.1 Закона РФ от 07.02.1992 N 2300-1 (в ред. ФЗ от 15.10.2025 N 376-ФЗ, в силе с 01.03.2026); ст. 14.8 КоАП РФ.
Estimate status and limitations: Estimate status: Not estimable from the supplied interface and business data. Final billing, consumers, charges, duration, refusal-path performance, injury, and revenue are unknown.

## Mitigating and Low-Risk Elements

- The page states a recurring amount and cadence rather than omitting renewal entirely.
- The subscription language appears on the captured page rather than only behind a separate terms link.

## Observed Without a Mapped Norm

None.

## Missing Context

- The final payment-review screen and consent record were not supplied.
- The saved-card controls, refusal path, and post-refusal billing behavior were not supplied.
- Consumer scale, charges, duration, injury, and revenue were not supplied.

## Priority Actions

- Put the full initial and recurring economics beside the purchase action before billing information is collected.
- Provide working in-account controls to delete the card and switch off auto-renewal without contacting support.
- Record the refusal date and time and stop charges immediately after an expressed refusal.

## Disclaimer

This report is a risk assessment based on the supplied interface and available context. It is not legal advice.
