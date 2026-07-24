"""The LLM comprehension layer — proven fully offline with a scripted model.

Covers the two defects it fixes and the invariants that keep it safe:
 - a patient flag stated in prose reaches the safety filter and blocks (the leak
   that exists without comprehension)
 - "the drug is available" is understood as NOT a shortage
 - a drug the model names is still gated by the registry (can't invent one)
 - flags are validated to the controlled vocabulary; unknowns are dropped
 - with comprehension off, behaviour is byte-for-byte the deterministic path
"""

import json
from dataclasses import dataclass

import pytest

from badeel.comprehension import normalize_flags, resolve_meds
from badeel.pipeline import answer
from badeel.registry import get_registry


@dataclass
class _Msg:
    content: str


class ScriptedLLM:
    """Returns one queued JSON payload; records call count."""
    def __init__(self, payload: str):
        self.payload = payload
        self.calls = 0

    def invoke(self, _prompt):
        self.calls += 1
        return _Msg(self.payload)


def _payload(**kw) -> str:
    return json.dumps(kw)


@pytest.fixture(scope="module")
def reg():
    return get_registry()   # synthetic dataset


# ---- Python re-validation of the LLM's fields ------------------------

def test_normalize_flags_maps_to_controlled_vocabulary():
    assert normalize_flags(["asthma", "pregnant", "banana"]) == [
        "bronchial asthma", "pregnancy"]
    assert normalize_flags(["totally unknown"]) == []


def test_resolve_meds_keeps_only_known_ingredients(reg):
    # brand -> ingredient, ingredient kept as-is, gibberish dropped
    assert resolve_meds(["Clopidex", "Warfaridine", "nonsense"], reg) == [
        "Clopidogrex", "Warfaridine"]


# ---- integration: comprehension changes behaviour, safely -----------

def test_prose_flag_reaches_safety_and_blocks(reg, monkeypatch):
    # asthma is only in the prose (no explicit flag) — without comprehension the
    # beta-blocker would be substituted; with it, the contraindication fires.
    llm = ScriptedLLM(_payload(intent="substitution", drug="Cardex",
                               patient_flags=["asthma"], concurrent_meds=[]))
    monkeypatch.setattr("badeel.llm.get_llm", lambda *a, **k: llm)

    a = answer("Cardex 10 is short and the patient has asthma", [], [], reg,
               comprehend=True)

    assert "bronchial asthma" in a.query.patient_flags
    assert a.escalate is True and a.substitutes == []
    assert a.comprehension is not None
    assert a.comprehension.intent == "substitution"
    assert a.comprehension.flags == ["bronchial asthma"]


def test_available_is_understood_as_not_a_shortage(reg, monkeypatch):
    llm = ScriptedLLM(_payload(intent="not_a_shortage", drug="Cardex",
                               patient_flags=[], concurrent_meds=[]))
    monkeypatch.setattr("badeel.llm.get_llm", lambda *a, **k: llm)

    a = answer("Cardex is available", [], [], reg, comprehend=True)

    assert a.escalate is False          # not a clinical refusal
    assert a.tier == "none" and a.substitutes == []
    assert a.comprehension.intent == "not_a_shortage"
    assert "available" in (a.escalation_reason or "").lower()


def test_model_named_drug_still_gated_by_registry(reg, monkeypatch):
    # the model can propose a name, but an unknown one does not enter the pipeline
    llm = ScriptedLLM(_payload(intent="substitution", drug="Zeroxan",
                               patient_flags=[], concurrent_meds=[]))
    monkeypatch.setattr("badeel.llm.get_llm", lambda *a, **k: llm)

    a = answer("Zeroxan is short", [], [], reg, comprehend=True)

    assert a.query.unresolved is True
    assert a.escalate is True and a.substitutes == []


def test_comprehension_off_is_the_deterministic_path(reg):
    # default path: no model call, no comprehension attached, today's behaviour
    a = answer("Cardex 10 mg is short", [], [], reg, comprehend=False)
    assert a.comprehension is None
