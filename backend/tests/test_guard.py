"""The validator guard (spec section 9). Fully offline — no network, no model.

Proves the headline anti-hallucination behaviour:
 - a grounded suggestion passes
 - an ingredient outside the candidate set trips validation, and the retry
   (fed the error) can recover
 - two failures escalate to (None) rather than invoking a third time
 - a text-level leak in the rationale also trips
"""

from dataclasses import dataclass

from badeel.guard import GuardedSuggestion, extract_json, run_guarded


@dataclass
class _Msg:
    content: str


class ScriptedLLM:
    """Returns queued responses in order; records how many times it was called."""
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = 0

    def invoke(self, _messages):
        self.calls += 1
        return _Msg(self.responses.pop(0))


ALLOWED = {"Pantoprazine", "Omeprazine"}


def test_extract_json_strips_code_fences():
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json('sure, here:\n{"ingredient": "X"}\nthanks')["ingredient"] == "X"


def test_grounded_suggestion_passes_first_try():
    llm = ScriptedLLM('{"ingredient": "Pantoprazine", "rationale": "Same class.", '
                      '"counselling_flags": []}')
    result, trips = run_guarded(llm, [("user", "go")], allowed_ingredients=ALLOWED)
    assert trips == 0
    assert llm.calls == 1
    assert result.ingredient == "Pantoprazine"


def test_hallucinated_ingredient_trips_then_retry_recovers():
    llm = ScriptedLLM(
        '{"ingredient": "Rosuvastin", "rationale": "x", "counselling_flags": []}',   # not allowed
        '{"ingredient": "Pantoprazine", "rationale": "corrected", "counselling_flags": []}')
    result, trips = run_guarded(llm, [("user", "go")], allowed_ingredients=ALLOWED)
    assert trips == 1
    assert llm.calls == 2
    assert result.ingredient == "Pantoprazine"


def test_two_failures_escalate_without_a_third_call():
    llm = ScriptedLLM(
        '{"ingredient": "Rosuvastin", "rationale": "x", "counselling_flags": []}',
        '{"ingredient": "Atorvastin", "rationale": "still wrong", "counselling_flags": []}')
    result, trips = run_guarded(llm, [("user", "go")], allowed_ingredients=ALLOWED)
    assert result is None
    assert trips == 2
    assert llm.calls == 2          # never a third invocation


def test_rationale_text_leak_is_caught():
    # ingredient is allowed, but the prose names a non-permitted drug.
    llm = ScriptedLLM(
        '{"ingredient": "Pantoprazine", "rationale": "Better than Omeprazine '
        'which interacts.", "counselling_flags": []}',
        '{"ingredient": "Pantoprazine", "rationale": "Same class PPI.", '
        '"counselling_flags": []}')
    result, trips = run_guarded(
        llm, [("user", "go")], allowed_ingredients={"Pantoprazine"},
        forbidden_named=["Omeprazine"])
    assert trips == 1
    assert result.ingredient == "Pantoprazine"
    assert "omeprazine" not in result.rationale.lower()


def test_missing_allowlist_is_a_configuration_error():
    obj = {"ingredient": "X", "rationale": "y", "counselling_flags": []}
    try:
        GuardedSuggestion.model_validate(obj, context={})
        assert False, "should have raised"
    except Exception as e:
        assert "misconfigured" in str(e)
