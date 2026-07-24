"""Step 0: the LLM comprehension layer (reads → Python verifies → Python decides).

The model reads a free-text request into structured fields; this module then
re-validates every field before any of it can influence a decision:

  * drug           -> resolved through the registry (the LLM cannot invent one)
  * patient_flags  -> intersected with the controlled safety vocabulary
  * concurrent_meds-> resolved to known ingredients only

The LLM never assigns a tier, screens safety, or picks a substitute. Every
validated value can only *add* caution downstream, never remove it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .safety import FLAG_KEYWORDS


@dataclass
class ComprehendResult:
    intent: str = "substitution"          # substitution | not_a_shortage | unclear
    drug: str | None = None               # LLM-read drug string (still resolved by registry)
    flags: list[str] = field(default_factory=list)   # canonical, validated
    meds: list[str] = field(default_factory=list)    # known ingredients, validated
    strength: str | None = None
    form: str | None = None


def normalize_flags(raw: list[str]) -> list[str]:
    """Map free-text conditions to the controlled patient-flag vocabulary the
    safety layer understands ('asthma' -> 'bronchial asthma'). Anything that does
    not match a known flag is dropped, so the LLM can only surface flags the
    deterministic checks already act on — never inject an unknown one."""
    out: list[str] = []
    for item in raw:
        low = str(item).strip().lower()
        if not low:
            continue
        for key, keywords in FLAG_KEYWORDS.items():
            if key in low or low in key or any(kw in low for kw in keywords):
                if key not in out:
                    out.append(key)
                break
    return out


def resolve_meds(raw: list[str], reg) -> list[str]:
    """Keep only concurrent meds that resolve to a known ingredient — by brand
    (via the registry) or by ingredient name. Unknown strings are dropped."""
    lower_ing = {name.lower(): name for name in reg.ing_by_name}
    out: list[str] = []
    for item in raw:
        s = str(item).strip()
        if not s:
            continue
        ingredient = None
        if s.lower() in lower_ing:
            ingredient = lower_ing[s.lower()]
        else:
            q = reg.resolve(s)
            if not q.unresolved and q.ingredient:
                ingredient = q.ingredient
        if ingredient and ingredient not in out:
            out.append(ingredient)
    return out


def comprehend_request(llm, text: str, reg) -> ComprehendResult | None:
    """Run the comprehension chain and validate its output. Returns None on any
    model/parse failure so the caller degrades to the deterministic path."""
    from .chains import comprehend

    data = comprehend(llm, text)
    if not data:
        return None
    return ComprehendResult(
        intent=data.get("intent", "substitution"),
        drug=data.get("drug"),
        flags=normalize_flags(data.get("patient_flags") or []),
        meds=resolve_meds(data.get("concurrent_meds") or [], reg),
        strength=data.get("strength"),
        form=data.get("form"),
    )
