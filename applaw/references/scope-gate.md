# Scope Gate (A0)

Run this before A1 Intake, on every supplied screenshot. The gate decides which
pattern families apply — it never decides whether the legal analysis runs.
Every screen, checkout or not, goes through the full A1-A8 flow against the
registered Russian norms.

## Classify

- `checkout_or_pricing`: the screen shows a specific price tied to a plan or item, a payment control (pay now, place order, an express-pay button, a card-entry field), a plan/subscription selector, or a negative-option consent step (a checkbox or toggle that adds a recurring charge).
- `non_checkout`: any other screen — a landing, feed, catalog, article, settings, admin, sign-in, map, form, or marketing page with no price, payment control, plan selector, or negative-option step anywhere on the page.

A page that only names a "Pricing" nav link without showing a price is `non_checkout`. A page with a visible price table plus a "cancel anytime" or "no subscription" line is `checkout_or_pricing`, even without a payment form, because it is still a plan-selection or pricing step in the funnel.

## What the classification changes

The label switches the checkout-family specialists on or off — nothing else:

- `checkout_or_pricing`: run the full A1-A8 flow with every family — disclosure, consent, pressure, upsell, cancellation, and content.
- `non_checkout`: run the same full A1-A8 flow; the content, consent, disclosure, and access duties apply exactly as on any screen (symbols, banned-organization assets, maps, labels, interface language, cookie and data-consent elements, authorization methods, recommender notices). Only the checkout-family specialists stand down: never manufacture a checkout finding — a hidden fee, a preselected add-on, a renewal trap — from marketing copy, a logo strip, or a testimonial alone merely because the page is persuasive. A logo strip or testimonial without a platform-review attribution stays in `Mitigating and Low-Risk Elements` or `Missing Context`, per `references/evaluation-workflow.md`.

Never skip the legal analysis for a `non_checkout` screen, and never auto-stamp its risk: the verdict comes from the rubric over the actual findings — a clean marketing page scores low because nothing was found, not because of its page type. The absence of a transactional step is an ordinary `Missing Context` note, not a reason to demand a checkout screen before analyzing what was supplied.

A `non_checkout` classification does not by itself raise a review-authenticity question. Ask that question only when an unresolved social/review-platform module is actually visible, per `references/report-contract.md`.

## If checkout_or_pricing

Continue the ordinary A1-A8 flow in `references/evaluation-workflow.md`. A visible price or plan table without a final payment form is still in scope; treat the absent payment step as an ordinary `Missing Context` limitation, not a reason to skip the pattern specialists.

## Ambiguous Cases

If a screen mixes both, for example a pricing table embedded inside a longer marketing page, classify as `checkout_or_pricing` and run the full flow, scoped to the pricing or plan module for the checkout-family specialists while the content and consent duties cover the whole page.
