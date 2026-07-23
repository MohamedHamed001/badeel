"""Deterministic tier generation (spec section 8, step 4).

Pure Python. No LLM, no safety knowledge — this module only enumerates what
*could* substitute for the queried product by tier. Safety filtering happens
afterwards in safety.py, which is what lets a blocked tier-1 candidate cede to
a tier-2 one (spec rule 2.2, case E008).

    tier 1 generic      same ingredient, different SKU, available
    tier 2 class        same equiv_group, different ingredient, available
    tier 3 therapeutic  same ATC 3-char subgroup, different equiv_group, available

Combination products only ever match candidates with an identical component set;
adding or dropping an active ingredient is left for safety.py to block.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .schemas import Tier


@dataclass
class Candidate:
    product: dict                 # the products.csv row
    tier: Tier
    counselling_flags: list[str] = field(default_factory=list)

    @property
    def ingredient(self) -> str:
        return self.product["ingredient"]

    @property
    def brand(self) -> str:
        return self.product["brand"]


def generate(query, reg) -> list[Candidate]:
    """Return every candidate SKU, tagged with its tier. Not yet filtered."""
    qprod = reg.by_brand[query.resolved_brand]
    q_ing = qprod["ingredient"]
    q_group = qprod["equiv_group"]
    q_atc3 = qprod["atc"][:3]
    already_taking = set(query.concurrent_meds)

    out: list[Candidate] = []
    for p in reg.products:
        if p["status"] != "available":
            continue
        # never re-offer the exact queried brand+strength+form SKU
        if p["sku"] == qprod["sku"]:
            continue

        ing = p["ingredient"]
        # never "substitute" with a drug the patient already takes (E021)
        if ing in already_taking:
            continue
        if ing == q_ing:
            tier: Tier = "generic"
        elif p["equiv_group"] == q_group:
            tier = "class"
        elif p["atc"][:3] == q_atc3 and p["equiv_group"] != q_group:
            tier = "therapeutic"
        else:
            continue

        out.append(Candidate(product=p, tier=tier))
    return out
