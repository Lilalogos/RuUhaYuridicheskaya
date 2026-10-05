---
id: scope-gate-non-checkout
category: scope_gate
expected_handling: full_pipeline_checkout_families_off
expected_risk_effect: rubric_driven
expected_report_location: material_findings_or_missing_context
prohibited_behavior: short_circuit_or_skip_legal_analysis_on_non_checkout
---

# Evidence

The screenshot is a marketing or informational page: a hero headline, a feature grid, a "trusted by" logo strip, blog or article cards, or an FAQ, with no visible price, payment control, plan selector, or negative-option consent step anywhere on the page.

# Expected Behavior

Classify as `non_checkout` at A0 and still run the full A1-A8 flow against the registered Russian norms: the content, consent, disclosure, and access duties (symbols, banned-organization assets, maps, labels, interface language, cookie and data-consent elements, authorization methods, recommender notices) apply to this screen exactly as to any other. Stand down only the checkout-family specialists: do not manufacture a hidden-fee, preselected-add-on, or renewal finding from marketing copy alone. The verdict comes from the rubric over the actual findings — never auto-stamp the risk from the page type, and never print the private numeric score. Note the absent transactional step as ordinary `Missing Context` without demanding a checkout screen as a precondition of the analysis.
