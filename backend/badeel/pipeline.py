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
           reg: Registry | None = None,
           narrate: bool = False,
           meta: dict | None = None) -> SubstitutionAnswer:
    reg = reg or get_registry()
    started = time.perf_counter()
    meta = meta or {}

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
            query, "Product not found in registry. We cannot advise a "
                   "substitution for an unrecognised product; confirm the name "
                   "with the prescriber before dispensing any alternative."))

    qprod = reg.by_brand[query.resolved_brand]
    query.strength = qprod["strength"]
    query.form = qprod["form"]

    # 2. NTI GATE — short-circuit everything, even a same-molecule brand switch
    if reg.is_nti(query.ingredient):
        splitting = any(w in text.lower() for w in ("halve", "split", "cut", "quarter"))
        reason = ("Narrow therapeutic index drug. Do not substitute without "
                  "prescriber authorisation and appropriate monitoring "
                  "(for example INR). Refer to prescriber.")
        if splitting:
            reason += " Do not split or halve tablets to reach the dose."
        ans = _escalate(
            query, reason,
            flags=[SafetyFlag(kind="nti", severity="major",
                              message="Narrow therapeutic index: substitution, "
                                      "including brand-to-brand, requires "
                                      "prescriber sign-off.")])
        if narrate:
            _narrate_refusal(ans, query, "narrow therapeutic index", reg, meta)
        return finish(ans)

    # 3. UPSTREAM — is the original prescription itself contraindicated?
    leaflets = load_leaflets()
    upstream = contraindication_flag(query.ingredient, query.patient_flags, leaflets)

    # 4. CANDIDATES
    cands = candidates_mod.generate(query, reg)

    # 5. SAFETY (after generation, before ranking)
    survivors, blocked = safety_mod.screen(query, cands, reg)

    # A therapeutic (different-class) swap is only justified when a closer
    # generic/class option existed and was blocked by a *contraindication* —
    # a patient condition that rules out the whole class and forces a
    # cross-class choice (penicillin allergy -> macrolide, E009). It is NOT
    # justified when the lower tiers were merely absent (E004/E023: an
    # antiplatelet must not become an anticoagulant) or were blocked by an
    # interaction with the patient's own therapy (E021), nor for a paediatric
    # contraindication where the prescription itself needs review (E030). In
    # those cases we escalate instead.
    lower_contra_block = any(
        c.tier in ("generic", "class") and flag.kind == "contraindication"
        for c, flag in blocked)
    paediatric = any("paediatric" in f.lower() or "age" in f.lower()
                     for f in query.patient_flags)
    if not (lower_contra_block and not paediatric):
        survivors = [s for s in survivors if s.tier != "therapeutic"]

    blocked_out = [
        BlockedCandidate(ingredient=c.ingredient, brand=c.brand, tier=c.tier,
                         reason=flag.message, flag=flag)
        for c, flag in blocked]

    # 6. DECIDE
    if not survivors:
        reason = _no_survivor_reason(upstream, blocked)
        ans = _escalate(query, reason,
                        flags=[upstream] if upstream else [],
                        blocked=blocked_out)
        # surface the drug-name-free reasons everything was blocked, so the
        # pharmacist sees the mechanism (form, combination, contraindication).
        seen = {f.message for f in ans.safety_flags}
        for c, flag in blocked:
            if flag.kind in ("form", "combination", "contraindication") \
                    and flag.message not in seen:
                seen.add(flag.message)
                ans.safety_flags.append(flag)
            elif flag.kind == "interaction" and ": " in flag.message:
                eff = flag.message.split(": ", 1)[1]   # effect only, no drug name
                if eff not in seen:
                    seen.add(eff)
                    ans.safety_flags.append(SafetyFlag(
                        kind="interaction", severity=flag.severity, message=eff))
        if narrate:
            kind = "contraindication" if upstream else "no safe substitution"
            _narrate_refusal(ans, query, kind, reg, meta)
        return finish(ans)

    # 7. RANK, then keep only the lowest surviving tier (never surface a
    #    higher tier alongside a closer match — that is how forbidden class
    #    swaps would leak past a valid generic, e.g. E001).
    best_tier = min(survivors, key=lambda c: TIER_ORDER[c.tier]).tier
    winners = [c for c in survivors if c.tier == best_tier]
    winners.sort(key=lambda c: _rank_key(c, qprod))

    subs = [_to_substitute(c, qprod) for c in winners[:3]]

    # situation-level counselling the pipeline can state deterministically
    if best_tier == "therapeutic" and any(
            "penicillin" in f.lower() for f in query.patient_flags):
        for s in subs:
            s.counselling_flags.append(
                "Avoid beta lactam antibiotics given the penicillin allergy.")

    # A combination substitute is a combination product covering both actives.
    for s in subs:
        if reg.is_combination(s.ingredient):
            s.counselling_flags.append(
                "This is a fixed dose combination product providing both active "
                "components of the original.")

    # If a closer same-class option was set aside for an interaction, tell the
    # pharmacist the mechanism (drug-name-free effect text) — e.g. E008.
    inter_effects = [flag.message.split(": ", 1)[1]
                     for c, flag in blocked
                     if flag.kind == "interaction" and ": " in flag.message]
    for eff in dict.fromkeys(inter_effects):
        for s in subs:
            s.counselling_flags.append(f"A same-class option was avoided: {eff}")

    guard_trips = 0
    model_used = "deterministic"

    # 8. NARRATE — ground a rationale for each substitute through the guard.
    if narrate:
        subs, guard_trips, model_used = _narrate(query, subs, reg, meta)
        if not subs:
            # every candidate failed the guard twice (spec 9.3) -> escalate
            ans = _escalate(query,
                            "model could not produce a grounded suggestion",
                            blocked=blocked_out)
            ans.guard_trips = guard_trips
            ans.model_used = model_used
            return finish(ans)

    ans = SubstitutionAnswer(
        query=query, tier=best_tier, escalate=False,
        substitutes=subs,
        safety_flags=[upstream] if upstream else [],
        blocked_candidates=blocked_out,
        confidence=1.0, guard_trips=guard_trips, model_used=model_used)
    return finish(ans)


def _narrate(query, subs, reg, meta):
    """Step 8: retrieve leaflet evidence and write a guarded rationale for each
    substitute. Lazy imports keep torch/chromadb off the --no-llm path."""
    import os

    from .chains import narrate_substitute
    from .llm import get_llm
    from .retrieval import get_retriever
    from .schemas import Citation

    llm = get_llm()
    retriever = get_retriever()
    model = os.getenv("LLM_MODEL", "unknown")
    all_ings = set(reg.ing_by_name)

    narrated, trips = [], 0
    for sub in subs:
        evidence = retriever.search(
            f"{query.resolved_brand} {sub.ingredient} substitution",
            scope=[sub.ingredient, query.ingredient], k=4)
        # prose may name only this substitute and the queried drug. A
        # combination's ingredient name contains its component molecules as
        # substrings (e.g. "Valsartex" inside "Valsartex + Hydroclorix"), and a
        # component can itself be forbidden (E006), so combinations are narrated
        # brand-only — never write an active-ingredient name for them.
        forbidden_named = sorted(all_ings - {sub.ingredient, query.ingredient})
        brand_only = reg.is_combination(sub.ingredient)
        result, t = narrate_substitute(
            llm, brand=sub.brand, ingredient=sub.ingredient,
            queried_brand=query.resolved_brand, tier=sub.tier,
            flags=sub.counselling_flags, evidence=evidence,
            allowed_ingredients={sub.ingredient},
            forbidden_named=forbidden_named, brand_only=brand_only,
            meta={"case_id": meta.get("case_id"), "model": model})
        trips += t
        if result is None:
            continue
        sub.rationale = result.rationale
        sub.counselling_flags = list(dict.fromkeys(
            sub.counselling_flags + result.counselling_flags))
        sub.evidence = [Citation(leaflet=c["leaflet"], section=c["section"],
                                 snippet=c["text"][:190]) for c in evidence]
        narrated.append(sub)
    return narrated, trips, model


# ---- helpers -----------------------------------------------------------

def _narrate_refusal(ans, query, reason_kind, reg, meta):
    """Enrich an escalation with a grounded, drug-name-free refusal rationale.
    Falls back silently to the deterministic reason if the model leaks or fails."""
    import os

    from .chains import narrate_refusal
    from .llm import get_llm
    from .retrieval import get_retriever

    try:
        # scope the search to the actual clinical trigger so the model grounds
        # on the RIGHT contraindication/interaction, not just any warning
        cue = " ".join(query.patient_flags + query.concurrent_meds) or reason_kind
        evidence = get_retriever().search(
            f"{query.resolved_brand} {cue} contraindication interaction warning",
            scope=[query.ingredient], k=4)
        rationale, flags = narrate_refusal(
            get_llm(), brand=query.resolved_brand, reason_kind=reason_kind,
            reason=ans.escalation_reason or "", evidence=evidence,
            forbidden_named=sorted(set(reg.ing_by_name)))
        ans.model_used = os.getenv("LLM_MODEL", "unknown")
        if rationale:
            ans.escalation_reason = f"{ans.escalation_reason} {rationale}".strip()
            for f in flags:
                ans.safety_flags.append(SafetyFlag(
                    kind="class_block", severity="major", message=f))
    except Exception:
        pass   # degrade to the deterministic reason


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
                "needs review — escalate and refer to the prescriber.")
    if blocked:
        return ("Every available alternative was blocked on safety grounds; "
                "there is no therapeutic alternative that is safe here. Do not "
                "substitute — escalate and refer to the prescriber.")
    return ("No substitution is possible: there is no alternative in registry "
            "for this product, and no therapeutic alternative either. Escalate "
            "and refer to the prescriber.")
