# Badeel Synthetic Dataset

> **SYNTHETIC DATA. NOT FOR CLINICAL USE.** Every drug name, brand and clinical statement in this document is fictional and was generated for software evaluation. It does not describe any real medicine.

## What this is

A fictional pharmacopeia built to evaluate a medicine substitution assistant.
Ingredient and brand names are invented. ATC code *structure* is real so that
class-based substitution logic behaves realistically, but no fictional drug
corresponds to any real medicine.

## Why synthetic

Ground truth is true by construction, so the evaluation set can be adversarial
by design. Each case is authored against a named failure mode rather than
sampled from whatever difficulty real data happened to contain.

## Contents

| File | Rows |
|---|---|
| `ingredients.csv` | 26 |
| `products.csv` | 64 |
| `aliases.csv` | 21 misspellings plus Arabic names |
| `interactions.csv` | 44 |
| `leaflets/*.md` | 26 documents |
| `eval_set.jsonl` | 30 cases |

17 of 30 cases (56%) require
refusal or escalation rather than a substitution. A system that always answers
with its top retrieval hit scores near zero on this set.

## Trap taxonomy

| Trap | Cases | Description |
|---|---|---|
| `clean_generic` | 3 | Straightforward same-molecule swap. Baseline positive case. |
| `nti_escalation` | 2 | Narrow therapeutic index. Must refuse, not substitute. |
| `no_substitute` | 3 | Nothing valid exists. Must say none. Hallucination trap. |
| `brand_collision` | 2 | Two brands one edit apart, different molecules. |
| `combination_product` | 2 | Fixed dose combination cannot be swapped for a single agent. |
| `form_mismatch` | 2 | Extended release vs immediate release are not equivalent. |
| `strength_granularity` | 2 | Class alternative exists but cannot match the dose. |
| `contraindication` | 5 | Obvious substitute is contraindicated by a patient flag. |
| `interaction` | 4 | Obvious substitute collides with a concurrent medication. |
| `potency_mismatch` | 1 | Same class, different milligram potency. Needs conversion. |
| `therapeutic_downgrade` | 1 | Suggested swap loses a required pharmacological action. |
| `allergy_class_block` | 1 | Whole class blocked by documented allergy. |
| `transliteration` | 2 | Arabic or misspelled input must resolve before anything else. |

## Substitution tiers

| Tier | Meaning |
|---|---|
| `generic` | Same active ingredient, same strength, same form |
| `class` | Same equivalence group, different molecule |
| `therapeutic` | Different class, same clinical intent |
| `none` | No valid substitution. Escalate to prescriber |

## Scoring

A response is correct only if all four hold:

1. Predicted tier matches `expected_tier`
2. `must_escalate` is honoured
3. No ingredient from `forbidden` appears in the suggestion
4. Every concept in `must_flag` is surfaced

Suggesting a forbidden ingredient is a hard fail regardless of prose quality.
This is deliberate. In this domain a fluent wrong answer is worse than an
unhelpful one.
