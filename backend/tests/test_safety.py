"""Safety filtering and the full-eval safety gate (spec section 11, phase 2).

The headline assertion is `test_eval_safety_gate`: run the deterministic
pipeline over all 30 cases and confirm it never suggests a forbidden
ingredient. The phase 2 gate is >= 80%; we hold 100%.
"""

import json
from pathlib import Path

import pytest

from badeel.candidates import generate
from badeel.config import DATA
from badeel.pipeline import answer
from badeel.registry import get_registry
from badeel.safety import screen


@pytest.fixture(scope="module")
def reg():
    return get_registry()


# ---- individual checks --------------------------------------------------

def test_contraindication_blocks_all_beta_blockers_in_asthma(reg):
    q = reg.resolve("Cardex")            # Veltolol, a beta-blocker
    q.patient_flags = ["bronchial asthma"]
    survivors, blocked = screen(q, generate(q, reg), reg)
    blocked_ings = {c.ingredient for c, _ in blocked}
    assert "Carvedanol" in blocked_ings          # non-selective, forbidden in E007
    assert survivors == []                        # nothing safe -> escalation


def test_major_interaction_blocks_but_moderate_only_flags(reg):
    # E008: Omeprazine interacts MAJOR with Clopidogrex -> blocked;
    #       Pantoprazine (class) survives.
    q = reg.resolve("Gastrolux")         # Omeprazine, in shortage
    q.concurrent_meds = ["Clopidogrex"]
    survivors, blocked = screen(q, generate(q, reg), reg)
    blocked_ings = {c.ingredient for c, _ in blocked}
    survivor_ings = {c.ingredient for c in survivors}
    assert "Omeprazine" in blocked_ings
    assert "Pantoprazine" in survivor_ings


def test_e008_blocked_tier1_lets_tier2_win(reg):
    # The load-bearing ordering case: safety runs before ranking, so a blocked
    # generic cedes to a class candidate.
    ans = answer("Gastrolux is out and the patient takes Clopidex",
                 patient_flags=[], concurrent_meds=["Clopidogrex"], reg=reg)
    assert ans.escalate is False
    assert ans.tier == "class"
    assert [s.ingredient for s in ans.substitutes] == ["Pantoprazine"]


def test_combination_swap_is_blocked(reg):
    # Substituting a single molecule with a fixed-dose combination adds an
    # active ingredient -> blocked.
    q = reg.resolve("Valtec")            # mono Valsartex
    survivors, blocked = screen(q, generate(q, reg), reg)
    reasons = {c.ingredient: f.kind for c, f in blocked}
    assert reasons.get("Valsartex + Hydroclorix") == "combination"


# ---- NTI short-circuit (pipeline, before candidates) --------------------

def test_nti_escalates_before_generating_candidates(reg):
    ans = answer("Coagulex 5 mg is short", reg=reg)   # Warfaridine, NTI
    assert ans.tier == "none"
    assert ans.escalate is True
    assert ans.substitutes == []


def test_unknown_drug_is_refused(reg):
    ans = answer("Do you have an alternative for Zeroxan?", reg=reg)
    assert ans.escalate is True
    assert "not found" in (ans.escalation_reason or "").lower()


# ---- the phase 2 gate ---------------------------------------------------

def _cases():
    text = (DATA / "eval_set.jsonl").read_text(encoding="utf-8")
    return [json.loads(l) for l in text.splitlines() if l.strip()]


def test_eval_safety_gate(reg):
    """No forbidden ingredient is ever suggested, across all 30 cases."""
    leaks = []
    for c in _cases():
        ans = answer(c["query_en"], c["patient_flags"], c["concurrent_meds"], reg)
        suggested = {s.ingredient for s in ans.substitutes}
        leaked = suggested & set(c["forbidden"])
        if leaked:
            leaks.append((c["id"], sorted(leaked)))
    assert leaks == [], f"safety leaks: {leaks}"


def test_every_case_produces_a_valid_answer(reg):
    for c in _cases():
        ans = answer(c["query_en"], c["patient_flags"], c["concurrent_meds"], reg)
        # schema validator already enforces escalate/tier vs substitutes;
        # reaching here means all 30 parsed and validated.
        assert ans.model_used == "deterministic"
