"""The validator guard (spec section 9) — the anti-hallucination mechanism.

The LLM output is parsed into GuardedSuggestion. The Pydantic validator rejects
any ingredient not in the retrieved candidate set (carried in validation
context). The chain retries once with the error appended; on a second failure it
escalates. Every trip is logged so the per-model trip rate can be reported.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from pydantic import BaseModel, ValidationError, model_validator

from .config import ROOT

LOG = ROOT / "logs" / "guard_trips.jsonl"


class GuardedSuggestion(BaseModel):
    """LLM output is parsed into this. Validation context carries the allowlist."""
    ingredient: str
    rationale: str
    counselling_flags: list[str] = []

    @model_validator(mode="after")
    def ingredient_must_be_in_candidate_set(self, info):
        ctx = info.context or {}
        allowed = ctx.get("allowed_ingredients")
        if allowed is None:
            raise ValueError("guard misconfigured: no allowlist in validation context")
        if self.ingredient not in allowed:
            raise ValueError(
                f"'{self.ingredient}' is not in the retrieved candidate set "
                f"{sorted(allowed)}. You may only suggest from that set.")
        # Second line of defence: the rationale prose must not smuggle in a
        # different real drug (a text-level hallucination the eval also
        # penalises). Any known ingredient named outside the allowlist trips it.
        forbidden_named = ctx.get("forbidden_named")
        if forbidden_named:
            low = self.rationale.lower()
            leaked = [d for d in forbidden_named if d.lower() in low]
            if leaked:
                raise ValueError(
                    f"rationale names non-permitted drug(s) {leaked}. Only "
                    f"discuss {sorted(allowed)}.")
        return self


def extract_json(text: str) -> dict:
    """Strip code fences and parse the first JSON object. Prompt-and-parse only
    (spec rule 2.7): never rely on native tool calling or structured output."""
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.MULTILINE).strip()
    start = t.find("{")
    end = t.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"no JSON object in model output: {text[:120]!r}")
    return json.loads(t[start:end + 1])


def run_guarded(llm, messages, *, allowed_ingredients, forbidden_named=None,
                meta=None):
    """Invoke the LLM, parse+validate against the allowlist, retry once.

    Returns (GuardedSuggestion, trips) on success, or (None, trips) if the model
    could not produce a grounded suggestion after the retry (caller escalates).
    """
    ctx = {"allowed_ingredients": set(allowed_ingredients),
           "forbidden_named": forbidden_named or []}
    convo = list(messages)
    trips = 0

    for attempt in (1, 2):
        raw = llm.invoke(convo)
        text = getattr(raw, "content", raw)
        try:
            obj = extract_json(text if isinstance(text, str) else str(text))
            return GuardedSuggestion.model_validate(obj, context=ctx), trips
        except (ValidationError, ValueError) as err:
            trips += 1
            _log_trip(meta, attempt, err, allowed_ingredients)
            if attempt == 2:
                return None, trips
            # correction turn: hand the model its own error and try once more
            convo = convo + [
                ("assistant", text if isinstance(text, str) else str(text)),
                ("user", f"That failed validation: {err}. "
                         f"Respond again with corrected JSON only."),
            ]
    return None, trips


def _log_trip(meta, attempt, err, allowed):
    meta = meta or {}
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "case_id": meta.get("case_id"),
            "model": meta.get("model"),
            "attempt": attempt,
            "error": str(err).split("\n")[0][:300],
            "allowed_ingredients": sorted(allowed),
        }, ensure_ascii=False) + "\n")
