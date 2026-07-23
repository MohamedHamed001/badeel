#!/usr/bin/env python3
"""Build the REAL-drug demo dataset into ./data/real (same schema as ./data).

    python build_real.py

Reuses the leaflet renderer from build_dataset.py; sources data from
pharmacopeia_real.py (real ingredients + real Egyptian brands). No eval set —
the graded evaluation stays on the synthetic dataset.
"""

import csv
import os

from pharmacopeia_real import INGREDIENTS, BRANDS, ALIASES
from build_dataset import leaflet, BANNER

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "real")
LEAFLETS = os.path.join(OUT, "leaflets")


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

    with open(f"{OUT}/products.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(products[0].keys()))
        w.writeheader()
        w.writerows(products)

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

    with open(f"{OUT}/interactions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ingredient_a", "ingredient_b", "severity", "effect"])
        for i in INGREDIENTS:
            for other, sev, eff in i["interactions"]:
                w.writerow([i["name"], other, sev, eff])

    for i in INGREDIENTS:
        prods = [p for p in products if p["ingredient_id"] == i["id"]]
        slug = i["name"].lower().replace(" + ", "_").replace(" ", "_")
        with open(f"{LEAFLETS}/{slug}.md", "w", encoding="utf-8") as f:
            f.write(leaflet(i, prods))

    card = f"""# Badeel Real-Drug Demo Dataset

{BANNER}
## What this is

A demonstration dataset of **real active ingredients** with **real Egyptian
brand names**. Ingredient-level clinical facts (contraindications, interactions,
ATC codes, narrow-therapeutic-index status) are standard reference pharmacology.
EGP prices are **illustrative** and stock status is assigned for demonstration.

This dataset powers the demo only. The graded evaluation and the 100% safety
result are measured on the separate synthetic dataset, whose ground truth is
true by construction.

## Not for clinical use

Simplified reference knowledge for a software demo, not a validated drug
database. Always verify against an authoritative source and clinical judgement.

## Contents

| File | Rows |
|---|---|
| `ingredients.csv` | {len(INGREDIENTS)} |
| `products.csv` | {len(products)} |
| `aliases.csv` | {len(ALIASES)} misspellings plus Arabic names |
| `interactions.csv` | {sum(len(i['interactions']) for i in INGREDIENTS)} |
| `leaflets/*.md` | {len(INGREDIENTS)} documents |
"""
    with open(f"{OUT}/DATASET_CARD.md", "w", encoding="utf-8") as f:
        f.write(card)

    print(f"ingredients   {len(INGREDIENTS)}")
    print(f"products      {len(products)}")
    print(f"leaflets      {len(INGREDIENTS)}")
    print(f"interactions  {sum(len(i['interactions']) for i in INGREDIENTS)}")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
