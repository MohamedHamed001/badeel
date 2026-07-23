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
