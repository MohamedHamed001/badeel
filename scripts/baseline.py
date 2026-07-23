#!/usr/bin/env python3
"""
Naive baseline for Badeel (spec section 1).

A deliberately dumb system: resolve the queried brand, return the top
same-class match (same equivalence group, cheapest available), and NEVER
escalate. This is the "before" column of the results table.

    python scripts/baseline.py            # writes predictions.baseline.jsonl
    python score.py predictions.baseline.jsonl

Expected order of magnitude: overall correct ~3%, safety ~27%. The point is
that a system with no safety layer and no escalation leaks forbidden
ingredients on most adversarial cases.
"""

import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def load_products():
    with open(os.path.join(DATA, "products.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_aliases():
    with open(os.path.join(DATA, "aliases.csv"), encoding="utf-8") as f:
        return {r["alias"].lower(): r["canonical_brand"] for r in csv.DictReader(f)}


def resolve_brand(query_en, brands, aliases):
    """Naive: longest brand substring, else first alias substring. No fuzzy."""
    q = query_en.lower()
    hits = [b for b in brands if b.lower() in q]
    if hits:
        return max(hits, key=len)
    for alias, canon in aliases.items():
        if alias in q:
            return canon
    return None


def main():
    products = load_products()
    aliases = load_aliases()
    brands = sorted({p["brand"] for p in products})
    by_brand = {}
    for p in products:
        by_brand.setdefault(p["brand"], p)  # first SKU per brand is enough

    with open(os.path.join(DATA, "eval_set.jsonl"), encoding="utf-8") as f:
        cases = [json.loads(l) for l in f if l.strip()]

    preds = []
    for c in cases:
        brand = resolve_brand(c["query_en"], brands, aliases)
        suggested, text = [], "No match found."
        if brand and brand in by_brand:
            group = by_brand[brand]["equiv_group"]
            ing = by_brand[brand]["ingredient"]
            # NAIVE: surface every same-class molecule. No safety filter, no
            # NTI gate, no escalation. This is exactly the ungrounded system
            # the real pipeline is built to beat.
            suggested = sorted({p["ingredient"] for p in products
                                if p["equiv_group"] == group
                                and p["ingredient"] != ing})
            if suggested:
                text = "Same-class options: " + ", ".join(suggested) + "."
        preds.append({
            "id": c["id"],
            "tier": "class",        # naive: always claims a class swap
            "escalate": False,      # naive: never escalates
            "suggested_ingredients": suggested,
            "response_text": text,
        })

    out = os.path.join(ROOT, "predictions.baseline.jsonl")
    with open(out, "w", encoding="utf-8") as f:
        for p in preds:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"wrote {out}  ({len(preds)} predictions)")


if __name__ == "__main__":
    main()
