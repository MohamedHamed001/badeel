"""Orchestration: the single public entry point (spec section 8).

Steps run in this exact order. Phase 2 implements 1-7 as pure Python; step 8
(narration) is stubbed — substitutes carry an empty rationale until the LLM
chains land in phase 4.

    1 RESOLVE      -> registry
    2 NTI GATE     -> escalate before generating candidates
    3 UPSTREAM     -> is the queried drug itself contraindicated?
    4 CANDIDATES   -> candidates.generate
    5 SAFETY       -> safety.screen (after generation, before ranking)
    6 DECIDE       -> lowest surviving tier, or escalate
    7 RANK         -> tier, stock, price, manufacturer continuity
    8 NARRATE      -> stubbed in phase 2
"""

from __future__ import annotations

import time

from . import candidates as candidates_mod
from . import safety as safety_mod
from .registry import Registry, get_registry
from .safety import contraindication_flag, load_leaflets
from .schemas import (BlockedCandidate, DrugQuery, SafetyFlag, Substitute,
                      SubstitutionAnswer)

TIER_ORDER = {"generic": 0, "class": 1, "therapeutic": 2, "none": 3}


def answer(text: str,
           patient_flags: list[str] | None = None,
           concurrent_meds: list[str] | None = None,
           reg: Registry | None = None) -> SubstitutionAnswer:
    reg = reg or get_registry()
    started = time.perf_counter()

    # 1. RESOLVE
    query = reg.resolve(text)
    # explicit request fields override anything the text implied
    if patient_flags is not None:
        query.patient_flags = patient_flags
    if concurrent_meds is not None:
        query.concurrent_meds = concurrent_meds

    def finish(ans: SubstitutionAnswer) -> SubstitutionAnswer:
        ans.latency_ms = int((time.perf_counter() - started) * 1000)
        return ans

    if query.unresolved:
        return finish(_escalate(
            query, "Product not found in registry. Confirm the name with the "
                   "prescriber before dispensing any alternative."))

    qprod = reg.by_brand[query.resolved_brand]
    query.strength = qprod["strength"]
    query.form = qprod["form"]

    # 2. NTI GATE — short-circuit everything, even a same-molecule brand switch
    if reg.is_nti(query.ingredient):
        return finish(_escalate(
            query, "Narrow therapeutic index drug. Do not substitute without "
                   "prescriber authorisation and appropriate monitoring "
                   "(for example INR). Refer to prescriber.",
            flags=[SafetyFlag(kind="nti", severity="major",
                              message="Narrow therapeutic index: substitution, "
                                      "including brand-to-brand, requires "
                                      "prescriber sign-off.")]))

    # 3. UPSTREAM — is the original prescription itself contraindicated?
    leaflets = load_leaflets()
    upstream = contraindication_flag(query.ingredient, query.patient_flags, leaflets)

    # 4. CANDIDATES
    cands = candidates_mod.generate(query, reg)

    # 5. SAFETY (after generation, before ranking)
    survivors, blocked = safety_mod.screen(query, cands, reg)

    # A therapeutic (different-class) swap is only justified when a closer
    # generic/class option existed but was safety-blocked — e.g. an allergy
    # that blocks the whole penicillin class forces a macrolide (E009). If no
    # generic/class candidate ever existed, the drug is genuinely
    # unsubstitutable and we escalate rather than cross drug classes (E004,
    # E023: antiplatelet must not become an anticoagulant).
    had_lower = any(c.tier in ("generic", "class") for c in cands)
    if not had_lower:
        survivors = [s for s in survivors if s.tier != "therapeutic"]

    blocked_out = [
        BlockedCandidate(ingredient=c.ingredient, brand=c.brand, tier=c.tier,
                         reason=flag.message, flag=flag)
        for c, flag in blocked]

    # 6. DECIDE
    if not survivors:
        reason = _no_survivor_reason(upstream, blocked)
        return finish(_escalate(query, reason,
                                flags=[upstream] if upstream else [],
                                blocked=blocked_out))

    # 7. RANK, then keep only the lowest surviving tier (never surface a
    #    higher tier alongside a closer match — that is how forbidden class
    #    swaps would leak past a valid generic, e.g. E001).
    best_tier = min(survivors, key=lambda c: TIER_ORDER[c.tier]).tier
    winners = [c for c in survivors if c.tier == best_tier]
    winners.sort(key=lambda c: _rank_key(c, qprod))

    subs = [_to_substitute(c, qprod) for c in winners[:5]]
    ans = SubstitutionAnswer(
        query=query, tier=best_tier, escalate=False,
        substitutes=subs,
        safety_flags=[upstream] if upstream else [],
        blocked_candidates=blocked_out,
        confidence=1.0, model_used="deterministic")
    return finish(ans)


# ---- helpers -----------------------------------------------------------

def _rank_key(cand, qprod):
    p = cand.product
    return (
        0 if p["status"] == "available" else 1,            # stock
        float(p["price_egp"]),                             # price ascending
        0 if p["manufacturer"] == qprod["manufacturer"] else 1,  # continuity
    )


def _to_substitute(cand, qprod) -> Substitute:
    p = cand.product
    q_price = float(qprod["price_egp"])
    price = float(p["price_egp"])
    delta = round((price - q_price) / q_price * 100, 1) if q_price else 0.0
    return Substitute(
        brand=p["brand"], ingredient=p["ingredient"], strength=p["strength"],
        form=p["form"], tier=cand.tier, price_egp=price, price_delta_pct=delta,
        rationale="",  # narration stubbed until phase 4
        counselling_flags=list(dict.fromkeys(cand.counselling_flags)))


def _escalate(query: DrugQuery, reason: str, flags=None, blocked=None):
    return SubstitutionAnswer(
        query=query, tier="none", escalate=True, escalation_reason=reason,
        substitutes=[], safety_flags=flags or [],
        blocked_candidates=blocked or [], confidence=1.0,
        model_used="deterministic")


def _no_survivor_reason(upstream, blocked) -> str:
    if upstream:
        return ("The prescribed product is itself contraindicated for this "
                "patient and no safe alternative is available. The prescription "
                "needs review — refer to the prescriber.")
    if blocked:
        return ("Every available alternative was blocked on safety grounds. "
                "Do not substitute; refer to the prescriber.")
    return ("No valid substitution exists in the registry. Refer to the "
            "prescriber.")
