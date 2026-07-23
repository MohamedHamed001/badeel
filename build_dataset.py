#!/usr/bin/env python3
"""
Build the Badeel synthetic dataset.

    python build_dataset.py

Emits into ./data:
    ingredients.csv      one row per active ingredient
    products.csv         one row per brand/strength/form SKU
    aliases.csv          misspelling and transliteration map
    interactions.csv     pairwise interaction edges
    leaflets/*.md        synthetic SPC-style leaflets for RAG ingestion
    eval_set.jsonl       30 labelled adversarial cases
    DATASET_CARD.md      provenance and warning
"""

import csv
import json
import os
import textwrap

from pharmacopeia import INGREDIENTS, BRANDS, ALIASES
from eval_cases import EVAL_CASES, TRAPS

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
LEAFLETS = os.path.join(OUT, "leaflets")

BANNER = (
    "> **SYNTHETIC DATA. NOT FOR CLINICAL USE.** Every drug name, brand and "
    "clinical statement in this document is fictional and was generated for "
    "software evaluation. It does not describe any real medicine.\n"
)


def bullets(items):
    return "\n".join(f"- {i}" for i in items) if items else "- None recorded."


def leaflet(ing, products):
    forms_lines = []
    for form, strengths in ing["forms"]:
        forms_lines.append(f"- {form.capitalize()}: {', '.join(strengths)}")

    inter_lines = []
    for other, severity, effect in ing["interactions"]:
        inter_lines.append(f"- **{other}** ({severity}): {effect}")

    brand_lines = []
    for b in products:
        status = "" if b["status"] == "available" else f" [{b['status'].upper()}]"
        brand_lines.append(
            f"- {b['brand']} ({b['brand_ar']}), {b['strength']} {b['form']}, "
            f"{b['manufacturer']}, EGP {b['price_egp']}{status}"
        )

    nti_block = ""
    if ing["nti"]:
        nti_block = (
            "\n## Narrow Therapeutic Index Warning\n\n"
            "This product is designated narrow therapeutic index. Small changes "
            "in plasma concentration produce clinically significant changes in "
            "effect or toxicity. Product substitution, including substitution "
            "between brands containing the same active ingredient, must not be "
            "performed without prescriber authorisation and appropriate "
            "monitoring.\n"
        )

    combo_block = ""
    if ing.get("is_combination"):
        combo_block = (
            "\n## Fixed Dose Combination\n\n"
            f"This product contains {' and '.join(ing['components'])} in a fixed "
            "ratio. Substitution with a product containing only one of these "
            "components leaves the other indication untreated and does not "
            "constitute therapeutic equivalence.\n"
        )

    return f"""# {ing['name']}

{BANNER}
**ATC code:** {ing['atc']}
**Pharmacological class:** {ing['drug_class']}
**Equivalence group:** `{ing['equiv_group']}`
**Narrow therapeutic index:** {"YES" if ing['nti'] else "No"}

## Composition and Available Forms

{chr(10).join(forms_lines)}

## Registered Products

{chr(10).join(brand_lines)}

## Indications

{bullets(ing['indications'])}

## Contraindications

{bullets(ing['contraindications'])}
{combo_block}{nti_block}
## Drug Interactions

{chr(10).join(inter_lines) if inter_lines else "- None recorded."}

## Use in Pregnancy and Lactation

{ing['pregnancy']}

## Renal Impairment

{ing['renal']}

## Hepatic Impairment

{ing['hepatic']}

## Adverse Reactions

{bullets(ing['adverse'])}

## Substitution Notes

{textwrap.fill(ing['notes'], 88)}

## Storage

Store below 25 degrees Celsius, protected from light and moisture. Keep out of
the reach of children.
"""


def main():
    os.makedirs(LEAFLETS, exist_ok=True)
    by_id = {i["id"]: i for i in INGREDIENTS}

    products = []
    for brand, brand_ar, ing_id, strength, form, mfr, price, status in BRANDS:
        products.append(dict(
            sku=f"SKU{len(products)+1:03d}", brand=brand, brand_ar=brand_ar,
            ingredient_id=ing_id, ingredient=by_id[ing_id]["name"],
            strength=strength, form=form, manufacturer=mfr,
            price_egp=price, status=status,
            atc=by_id[ing_id]["atc"],
            equiv_group=by_id[ing_id]["equiv_group"],
            nti=by_id[ing_id]["nti"],
        ))

    # ingredients.csv
    with open(f"{OUT}/ingredients.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ingredient_id", "name", "atc", "atc_level4", "drug_class",
                    "equiv_group", "nti", "is_combination", "components",
                    "pregnancy", "forms"])
        for i in INGREDIENTS:
            forms = "; ".join(f"{fm}:{'/'.join(st)}" for fm, st in i["forms"])
            w.writerow([i["id"], i["name"], i["atc"], i["atc"][:5], i["drug_class"],
                        i["equiv_group"], int(i["nti"]), int(i.get("is_combination", False)),
                        "|".join(i.get("components", [])), i["pregnancy"], forms])

    # products.csv
    with open(f"{OUT}/products.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(products[0].keys()))
        w.writeheader()
        w.writerows(products)

    # aliases.csv
    with open(f"{OUT}/aliases.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["alias", "canonical_brand", "kind"])
        for alias, canon in ALIASES.items():
            w.writerow([alias, canon, "misspelling"])
        seen = set()
        for p in products:
            key = (p["brand_ar"], p["brand"])
            if key not in seen:
                seen.add(key)
                w.writerow([p["brand_ar"], p["brand"], "arabic"])

    # interactions.csv
    with open(f"{OUT}/interactions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ingredient_a", "ingredient_b", "severity", "effect"])
        for i in INGREDIENTS:
            for other, sev, eff in i["interactions"]:
                w.writerow([i["name"], other, sev, eff])

    # leaflets
    for i in INGREDIENTS:
        prods = [p for p in products if p["ingredient_id"] == i["id"]]
        slug = i["name"].lower().replace(" + ", "_").replace(" ", "_")
        with open(f"{LEAFLETS}/{slug}.md", "w", encoding="utf-8") as f:
            f.write(leaflet(i, prods))

    # eval set
    with open(f"{OUT}/eval_set.jsonl", "w", encoding="utf-8") as f:
        for c in EVAL_CASES:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    # dataset card
    counts = {}
    for c in EVAL_CASES:
        counts[c["trap"]] = counts.get(c["trap"], 0) + 1
    trap_rows = "\n".join(
        f"| `{k}` | {counts.get(k,0)} | {v} |" for k, v in TRAPS.items())

    escalate_n = sum(1 for c in EVAL_CASES if c["must_escalate"])

    card = f"""# Badeel Synthetic Dataset

{BANNER}
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
| `ingredients.csv` | {len(INGREDIENTS)} |
| `products.csv` | {len(products)} |
| `aliases.csv` | {len(ALIASES)} misspellings plus Arabic names |
| `interactions.csv` | {sum(len(i['interactions']) for i in INGREDIENTS)} |
| `leaflets/*.md` | {len(INGREDIENTS)} documents |
| `eval_set.jsonl` | {len(EVAL_CASES)} cases |

{escalate_n} of {len(EVAL_CASES)} cases ({escalate_n*100//len(EVAL_CASES)}%) require
refusal or escalation rather than a substitution. A system that always answers
with its top retrieval hit scores near zero on this set.

## Trap taxonomy

| Trap | Cases | Description |
|---|---|---|
{trap_rows}

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
"""
    with open(f"{OUT}/DATASET_CARD.md", "w", encoding="utf-8") as f:
        f.write(card)

    print(f"ingredients   {len(INGREDIENTS)}")
    print(f"products      {len(products)}")
    print(f"leaflets      {len(INGREDIENTS)}")
    print(f"eval cases    {len(EVAL_CASES)}  ({escalate_n} require escalation)")
    print(f"traps covered {len(counts)}/{len(TRAPS)}")


if __name__ == "__main__":
    main()
