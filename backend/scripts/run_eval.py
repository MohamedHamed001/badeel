#!/usr/bin/env python3
"""Run the pipeline over eval_set.jsonl and write predictions.jsonl.

    python backend/scripts/run_eval.py --no-llm        # deterministic only
    python score.py predictions.jsonl                  # grade (from repo root)

`--no-llm` runs steps 1-7 with narration stubbed; it is the phase 2 gate. The
prediction's response_text is deliberately empty so the deterministic run can
never leak a forbidden ingredient name through prose — suggestions are carried
structurally in suggested_ingredients.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from badeel.pipeline import answer  # noqa: E402
from badeel.registry import get_registry  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-llm", action="store_true",
                    help="deterministic pipeline, narration stubbed (phase 2 gate)")
    ap.add_argument("--out", default=str(ROOT / "predictions.jsonl"))
    args = ap.parse_args()
    narrate = not args.no_llm

    reg = get_registry()
    cases = [json.loads(l) for l in
             (ROOT / "data" / "eval_set.jsonl").read_text(encoding="utf-8").splitlines()
             if l.strip()]

    preds, total_trips = [], 0
    for c in cases:
        ans = answer(c["query_en"], c["patient_flags"], c["concurrent_meds"], reg,
                     narrate=narrate, meta={"case_id": c["id"]})
        total_trips += ans.guard_trips
        preds.append({
            "id": c["id"],
            "tier": ans.tier,
            "escalate": ans.escalate,
            "suggested_ingredients": list(dict.fromkeys(
                s.ingredient for s in ans.substitutes)),
            "response_text": _response_text(ans, args.no_llm),
            "guard_trips": ans.guard_trips,
        })
        if narrate:
            print(f"  {c['id']}: tier={ans.tier} escalate={ans.escalate} "
                  f"trips={ans.guard_trips}")

    out = Path(args.out)
    with open(out, "w", encoding="utf-8") as f:
        for p in preds:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"\nwrote {out}  ({len(preds)} predictions, "
          f"{sum(p['escalate'] for p in preds)} escalations, "
          f"{total_trips} guard trips)")


def _response_text(ans, no_llm: bool) -> str:
    """Aggregate the prose the grader inspects for required safety concepts.
    In --no-llm mode this is empty so the deterministic stub can never leak a
    forbidden name through prose."""
    if no_llm:
        return ""
    parts = []
    if ans.escalation_reason:
        parts.append(ans.escalation_reason)
    parts += [f.message for f in ans.safety_flags]
    for s in ans.substitutes:
        if s.rationale:
            parts.append(s.rationale)
        parts += s.counselling_flags
    return " ".join(parts)


if __name__ == "__main__":
    main()
