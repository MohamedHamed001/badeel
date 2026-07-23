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
from .i18n import t
from .registry import Registry, get_registry
from .safety import contraindication_flag, load_leaflets
from .schemas import (BlockedCandidate, DrugQuery, SafetyFlag, Substitute,
                      SubstitutionAnswer, TraceStep)

TIER_ORDER = {"generic": 0, "class": 1, "therapeutic": 2, "none": 3}


def answer(text: str,
           patient_flags: list[str] | None = None,
           concurrent_meds: list[str] | None = None,
           reg: Registry | None = None,
           narrate: bool = False,
           meta: dict | None = None,
           lang: str = "en") -> SubstitutionAnswer:
    reg = reg or get_registry()
    started = time.perf_counter()
    meta = meta or {}
    trace: list[TraceStep] = []

    # 1. RESOLVE
    query = reg.resolve(text)
    # explicit request fields override anything the text implied
    if patient_flags is not None:
        query.patient_flags = patient_flags
    if concurrent_meds is not None:
        query.concurrent_meds = concurrent_meds

    def finish(ans: SubstitutionAnswer) -> SubstitutionAnswer:
        ans.trace = trace
        ans.latency_ms = int((time.perf_counter() - started) * 1000)
        return ans

    if query.unresolved:
        trace.append(TraceStep(
            step=1, name=t(lang, "trace.resolve"), status="escalate",
            detail=t(lang, "trace.resolve.fail", text=text)))
        return finish(_escalate(query, t(lang, "esc.unresolved")))

    qprod = reg.by_brand[query.resolved_brand]
    query.strength = qprod["strength"]
    query.form = qprod["form"]
    trace.append(TraceStep(
        step=1, name=t(lang, "trace.resolve"), status="ok",
        detail=t(lang, "trace.resolve.ok", text=text, brand=query.resolved_brand,
                 ingredient=query.ingredient, strength=qprod["strength"],
                 form=qprod["form"], score=f"{query.resolution_score:.0f}")))

    # 2. NTI GATE — short-circuit everything, even a same-molecule brand switch
    if reg.is_nti(query.ingredient):
        trace.append(TraceStep(
            step=2, name=t(lang, "trace.nti"), status="escalate",
            detail=t(lang, "trace.nti.escalate", ingredient=query.ingredient)))
        splitting = any(w in text.lower() for w in ("halve", "split", "cut", "quarter"))
        reason = t(lang, "esc.nti") + (t(lang, "esc.nti_split") if splitting else "")
        ans = _escalate(
            query, reason,
            flags=[SafetyFlag(kind="nti", severity="major", message=t(lang, "flag.nti"))])
        if narrate:
            _narrate_refusal(ans, query, "narrow therapeutic index", reg, meta, lang)
        return finish(ans)

    trace.append(TraceStep(
        step=2, name=t(lang, "trace.nti"), status="skip",
        detail=t(lang, "trace.nti.skip", ingredient=query.ingredient)))

    # 3. UPSTREAM — is the original prescription itself contraindicated?
    leaflets = load_leaflets()
    upstream = contraindication_flag(query.ingredient, query.patient_flags, leaflets, lang)
    if query.patient_flags:
        trace.append(TraceStep(
            step=3, name=t(lang, "trace.upstream"), status="block" if upstream else "ok",
            detail=(t(lang, "trace.upstream.block", ingredient=query.ingredient)
                    if upstream else
                    t(lang, "trace.upstream.ok", ingredient=query.ingredient,
                      flags=", ".join(query.patient_flags)))))

    # 4. CANDIDATES
    cands = candidates_mod.generate(query, reg)
    trace.append(TraceStep(
        step=4, name=t(lang, "trace.candidates"), status="info",
        detail=t(lang, "trace.candidates.detail", n=len(cands)),
        items=[f"{c.brand} ({c.ingredient}) — {c.tier}" for c in cands]))

    # 5. SAFETY (after generation, before ranking)
    survivors, blocked = safety_mod.screen(query, cands, reg, lang)

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

    tier_summary = _tier_summary(cands, survivors, blocked)

    trace.append(TraceStep(
        step=5, name=t(lang, "trace.safety"), status="ok",
        detail=t(lang, "trace.safety.detail", surv=len(survivors), blk=len(blocked)),
        items=[f"{c.brand} ✓" for c in survivors]
              + [f"{c.brand} ✗ {flag.message}" for c, flag in blocked]))

    # 6. DECIDE
    if not survivors:
        reason = _no_survivor_reason(upstream, blocked, lang)
        trace.append(TraceStep(
            step=6, name=t(lang, "trace.decide"), status="escalate",
            detail=t(lang, "trace.decide.escalate")))
        ans = _escalate(query, reason,
                        flags=[upstream] if upstream else [],
                        blocked=blocked_out)
        ans.tier_summary = tier_summary
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
            _narrate_refusal(ans, query, kind, reg, meta, lang)
        return finish(ans)

    # 7. RANK, then keep only the lowest surviving tier (never surface a
    #    higher tier alongside a closer match — that is how forbidden class
    #    swaps would leak past a valid generic, e.g. E001).
    best_tier = min(survivors, key=lambda c: TIER_ORDER[c.tier]).tier
    winners = [c for c in survivors if c.tier == best_tier]
    winners.sort(key=lambda c: _rank_key(c, qprod))

    trace.append(TraceStep(
        step=6, name=t(lang, "trace.decide"), status="ok",
        detail=t(lang, "trace.decide.ok", tier=best_tier)))
    trace.append(TraceStep(
        step=7, name=t(lang, "trace.rank"), status="info",
        detail=t(lang, "trace.rank.detail"),
        items=[f"{c.brand} ({c.ingredient}) · {c.product['strength']} · "
               f"EGP {float(c.product['price_egp']):.0f}" for c in winners[:3]]))

    subs = [_to_substitute(c, qprod) for c in winners[:3]]

    # situation-level counselling the pipeline can state deterministically
    if best_tier == "therapeutic" and any(
            "penicillin" in f.lower() for f in query.patient_flags):
        for s in subs:
            s.counselling_flags.append(t(lang, "couns.penicillin"))

    # A combination substitute is a combination product covering both actives.
    for s in subs:
        if reg.is_combination(s.ingredient):
            s.counselling_flags.append(t(lang, "couns.combo"))

    # If a closer same-class option was set aside for an interaction, tell the
    # pharmacist the mechanism (drug-name-free effect text) — e.g. E008.
    inter_effects = [flag.message.split(": ", 1)[1].rstrip(".")
                     for c, flag in blocked
                     if flag.kind == "interaction" and ": " in flag.message]
    for eff in dict.fromkeys(inter_effects):
        for s in subs:
            s.counselling_flags.append(t(lang, "couns.avoided", effect=eff))

    guard_trips = 0
    model_used = "deterministic"

    # 8. NARRATE — ground a rationale for each substitute through the guard.
    if narrate:
        subs, guard_trips, model_used = _narrate(query, subs, reg, meta, lang)
        if not subs:
            # every candidate failed the guard twice (spec 9.3) -> escalate
            ans = _escalate(query, t(lang, "esc.guard_fail"), blocked=blocked_out)
            ans.guard_trips = guard_trips
            ans.model_used = model_used
            return finish(ans)

    trace.append(TraceStep(
        step=8, name=t(lang, "trace.narrate"), status="info",
        detail=(t(lang, "trace.narrate.model", model=model_used, trips=guard_trips)
                if model_used != "deterministic"
                else t(lang, "trace.narrate.stub"))))

    ans = SubstitutionAnswer(
        query=query, tier=best_tier, escalate=False,
        substitutes=subs,
        safety_flags=[upstream] if upstream else [],
        blocked_candidates=blocked_out,
        tier_summary=tier_summary,
        confidence=1.0, guard_trips=guard_trips, model_used=model_used)
    return finish(ans)


def _tier_summary(cands, survivors, blocked):
    """Per-tier generated/survived counts + a representative block reason, so the
    frontend tier rail can render the algorithm's descent through the tiers."""
    from .schemas import TierStat
    survived_ings = {(c.tier, c.ingredient) for c in survivors}
    out = []
    for tier in ("generic", "class", "therapeutic"):
        generated = {c.ingredient for c in cands if c.tier == tier}
        survived = {ing for (tr, ing) in survived_ings if tr == tier}
        reason = None
        if generated and not survived:
            reason = next((f.message for c, f in blocked if c.tier == tier), None)
        out.append(TierStat(tier=tier, generated=len(generated),
                            survived=len(survived), blocked_reason=reason))
    return out


def _narrate(query, subs, reg, meta, lang="en"):
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
        result, tr = narrate_substitute(
            llm, brand=sub.brand, ingredient=sub.ingredient,
            queried_brand=query.resolved_brand, tier=sub.tier,
            flags=sub.counselling_flags, evidence=evidence,
            allowed_ingredients={sub.ingredient},
            forbidden_named=forbidden_named, brand_only=brand_only, lang=lang,
            meta={"case_id": meta.get("case_id"), "model": model})
        trips += tr
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

def _narrate_refusal(ans, query, reason_kind, reg, meta, lang="en"):
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
            forbidden_named=sorted(set(reg.ing_by_name)), lang=lang)
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


def _no_survivor_reason(upstream, blocked, lang="en") -> str:
    if upstream:
        return t(lang, "esc.upstream")
    if blocked:
        return t(lang, "esc.all_blocked")
    return t(lang, "esc.none")
