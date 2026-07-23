# Decisions

Tradeoffs made under the 3-day budget. One entry per decision.

## 1. Development LLM provider: local Ollama, `qwen2.5:7b-instruct`

Per spec §4. Local Ollama is free, fast to iterate against, and needs no
network on the hot path. Final numbers will additionally be run against the
largest free option available (§12). Embeddings stay local (`bge-small-en-v1.5`)
regardless of provider.

## 2. Repository layout: source scripts at root, `data/` is generated output

`pharmacopeia.py`, `eval_cases.py`, `build_dataset.py`, `score.py` live at the
repo root; `data/` holds only generated artefacts. This matches spec §3 and is
required for the scripts to work: `build_dataset.py` writes to `<root>/data`,
and `score.py` reads `data/eval_set.jsonl` relative to the working directory.
`data/` is treated as read-only from here on (§1).

## 3. Baseline definition and the 3.3% / 26.7% figure

Spec §1 cites a naive floor of **3.3% correct, 26.7% safe**. That figure comes
from an *ungrounded LLM* baseline — a model free to name any drug in prose,
which leaks forbidden ingredients on most adversarial cases.

`scripts/baseline.py` is a *deterministic* naive baseline: resolve the queried
brand, surface every same-equivalence-group molecule, never apply a safety
filter, never escalate. Measured on `eval_set.jsonl`:

| | correct | safe |
|---|---|---|
| Spec's ungrounded-LLM floor (§1) | 3.3% | 26.7% |
| Our deterministic class-swap baseline | 0.0% | 83.3% |

The deterministic baseline is *safer* than the LLM floor, and that is itself
the finding: on this eval the forbidden traps are mostly same-ingredient
generics, narrow-therapeutic-index alternatives, and cross-class drugs — not
class-mates — so a class-only swap rarely names them. It still scores **0%
correct**, because it gets tier wrong (always "class"), never escalates on the
17 escalation cases, and never surfaces the correct same-ingredient generic.

Both numbers make the same argument: without the deterministic tier logic,
safety filter, NTI gate and escalation, the system is either unsafe (LLM) or
unhelpful (naive). We report both honestly rather than reverse-engineer the
original ungrounded baseline's undocumented prompt. Per the dataset card, "a
negative result honestly reported beats a fabricated positive one."

## 4. Contraindication data comes from the leaflets, not a CSV

`build_dataset.py` exports only a subset of the ingredient fields to
`ingredients.csv` — there is no contraindication column. Rather than modify the
frozen dataset (spec §1), the safety filter parses the `## Contraindications`
section of each leaflet markdown. This keeps `data/` the single source of
truth and gives `Citation` evidence for free. Patient flags map to
contraindication text through a small explicit keyword table in `safety.py`
(the six flags the eval uses); clinical keyword matching is kept deliberately
literal, never "clever".

## 5. Interaction blocking is severity-driven

`major` interactions block a candidate; `moderate`/`minor` only attach a
counselling flag. This is what makes E008 (Omeprazine × Clopidogrex, major)
drop the tier-1 generic so a tier-2 Pantoprazine wins, while E027 (Levothyral ×
Omeprazine, moderate) still allows the PPI with a flag.

## 6. Two rules the eval forced, both safe and defensible

- **Resolve the earliest-mentioned brand.** "Profex is out, can I give
  Panadex?" names the out-of-stock drug first and the proposed alternative
  second. Longest-substring matching grabbed the wrong one (Panadex), leaking a
  forbidden ingredient. Resolving by earliest position (then longest at that
  position) fixes E013 and E029 and still keeps "Cardex Plus" over "Cardex".
- **A therapeutic (cross-class) swap is only offered when a closer
  generic/class option existed but was safety-blocked** (e.g. penicillin
  allergy forces a macrolide, E009). If no generic/class candidate ever existed,
  the drug is genuinely unsubstitutable and we escalate rather than cross drug
  classes — an antiplatelet must never silently become an anticoagulant (E004,
  E023).

## 7. The deterministic narration stub emits no prose

In `--no-llm` mode the prediction's `response_text` is empty. `score.py` counts
a forbidden ingredient appearing in the response text as a leak, so a stub that
named blocked or queried ingredients would fail cases it actually handled
correctly. Suggestions are carried structurally in `suggested_ingredients`;
prose arrives with the guarded LLM in phase 4.
