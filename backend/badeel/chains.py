"""Extraction and rationale chains (spec section 3).

Prompt-and-parse only (spec rule 2.7): instruct JSON, strip fences, json.loads,
then Pydantic-validate via the guard. No native tool calling, no provider
structured-output — free and local models vary too much to depend on it.
"""

from __future__ import annotations

from pathlib import Path

from .guard import extract_json, run_guarded

_LEAK_RETRY = 1

PROMPTS = Path(__file__).resolve().parent.parent / "prompts"


def _load(name: str) -> str:
    return (PROMPTS / name).read_text(encoding="utf-8")


def extract_fields(llm, query: str) -> dict:
    """Best-effort structured extraction. Not guarded (no allowlist to enforce);
    on any parse failure we simply fall back to whatever the request supplied."""
    prompt = _load("extraction.v1.md").replace("{query}", query)
    try:
        raw = llm.invoke(prompt)
        text = getattr(raw, "content", raw)
        data = extract_json(text if isinstance(text, str) else str(text))
        return {
            "strength": data.get("strength"),
            "form": data.get("form"),
            "patient_flags": [s.lower() for s in data.get("patient_flags") or []],
            "concurrent_meds": data.get("concurrent_meds") or [],
        }
    except Exception:
        return {}


_ARABIC = ("\n\nWrite the \"rationale\" and every \"counselling_flags\" entry in "
           "ARABIC (Modern Standard Arabic suitable for a pharmacist). Keep the "
           "JSON keys and the \"ingredient\" value in English exactly as given; "
           "only the human-readable text is Arabic.")


def narrate_substitute(llm, *, brand, ingredient, queried_brand, tier, flags,
                       evidence, allowed_ingredients, forbidden_named, meta,
                       brand_only=False, lang="en"):
    """Write a grounded rationale for one already-chosen substitute, through the
    validator guard. Returns (GuardedSuggestion | None, trips)."""
    ev_text = "\n".join(
        f"[{c['leaflet']} / {c['section']}] {c['text'][:300]}" for c in evidence
    ) or "None."
    prompt = (_load("rationale.v1.md")
              .replace("{brand}", brand)
              .replace("{ingredient}", ingredient)
              .replace("{queried_brand}", queried_brand or "the queried product")
              .replace("{tier}", tier)
              .replace("{flags}", "; ".join(flags) or "none")
              .replace("{evidence}", ev_text))
    if brand_only:
        prompt += ("\n\nIMPORTANT: This is a fixed dose combination. In the "
                   f"rationale and counselling, refer to it ONLY as '{brand}'. "
                   "Never write any active-ingredient name. Call it a 'fixed "
                   "dose combination' and note that it provides both components "
                   "of the original product, rather than listing them. "
                   f'The JSON "ingredient" field must still be exactly "{ingredient}".')
    if lang == "ar":
        prompt += _ARABIC
    return run_guarded(
        llm, [("user", prompt)],
        allowed_ingredients=allowed_ingredients,
        forbidden_named=forbidden_named,
        meta=meta)


def stream_rationale(llm, *, brand, ingredient, queried_brand, tier, flags,
                     evidence, lang="en", brand_only=False):
    """Yield the rationale as plain-text chunks for live streaming. The caller
    accumulates the text and runs the leak check once the stream completes."""
    ev_text = "\n".join(
        f"[{c['leaflet']} / {c['section']}] {c['text'][:300]}" for c in evidence
    ) or "None."
    prompt = (_load("rationale_stream.v1.md")
              .replace("{brand}", brand)
              .replace("{ingredient}", ingredient)
              .replace("{queried_brand}", queried_brand or "the queried product")
              .replace("{tier}", tier)
              .replace("{flags}", "; ".join(flags) or "none")
              .replace("{evidence}", ev_text))
    if brand_only:
        prompt += (f"\n\nThis is a fixed dose combination: refer to it only as "
                   f"'{brand}', never write any active-ingredient name.")
    if lang == "ar":
        prompt += ("\n\nWrite the sentences in ARABIC (Modern Standard Arabic "
                   "suitable for a pharmacist).")
    for chunk in llm.stream([("user", prompt)]):
        text = getattr(chunk, "content", "")
        if text:
            yield text


def narrate_refusal(llm, *, brand, reason_kind, reason, evidence,
                    forbidden_named, lang="en"):
    """Write a grounded refusal rationale for an escalation, naming no drug.

    Returns (rationale, counselling_flags). Falls back to the deterministic
    reason if the model leaks a drug name or fails to parse — so a refusal is
    never blocked and never leaks a forbidden ingredient through prose."""
    ev_text = "\n".join(
        f"[{c['leaflet']} / {c['section']}] {c['text'][:300]}" for c in evidence
    ) or "None."
    prompt = (_load("refusal.v1.md")
              .replace("{brand}", brand or "the queried product")
              .replace("{reason_kind}", reason_kind)
              .replace("{reason}", reason)
              .replace("{evidence}", ev_text))
    if lang == "ar":
        prompt += _ARABIC

    for _ in range(_LEAK_RETRY + 1):
        try:
            raw = llm.invoke([("user", prompt)])
            text = getattr(raw, "content", raw)
            data = extract_json(text if isinstance(text, str) else str(text))
            rationale = (data.get("rationale") or "").strip()
            flags = data.get("counselling_flags") or []
            low = rationale.lower()
            if rationale and not any(d.lower() in low for d in forbidden_named):
                return rationale, [f for f in flags if isinstance(f, str)]
        except Exception:
            pass
    return "", []
