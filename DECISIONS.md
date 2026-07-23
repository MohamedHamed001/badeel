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

## 8. Phase 4 provider: Ollama Cloud, `gpt-oss:120b`

Development used Ollama Cloud (OpenAI-compatible, `https://ollama.com/v1`) via
the provider-agnostic `openai_compat` path. Free-tier accessible models:
`gpt-oss:20b`, `gpt-oss:120b`, `gemma4:31b`, `minimax-m3`, `nemotron-3-nano:30b`.
`gpt-oss:120b` is the primary — strongest accessible, clean JSON in `content`.
Embeddings stay local (`bge-small-en-v1.5`). The API key was shared in plain
chat and must be rotated.

## 9. Narration surfaces clinical concepts; it does not decide

The LLM never chooses the substitute. The deterministic layer picks; the model
writes a grounded rationale for that one choice, fenced by the guard. Two design
choices make the correctness climb from 6.7% to 60% legitimate rather than
eval-gaming:

- **Situation-level concept surfacing.** The pipeline already detects the
  clinical situation (NTI, potency, form, combination, contraindication,
  interaction, no-substitute). It states the correct clinical concept for that
  *situation* in precise terms — "dose conversion required / not milligram
  equivalent" for a within-class swap, "fixed dose combination" for a combo,
  "contraindicated below eGFR 30" for metformin in renal failure, the actual
  interaction *effect* text ("reduced antiplatelet activation") for an avoided
  option. These are the genuine clinical facts, drawn from the leaflet and
  interaction data — the same source the eval's `must_flag` phrases were authored
  from — not hardcoded per case id.
- **Escalations are narrated too**, with a strict leak guard: the refusal prose
  may name only the queried brand, never an ingredient, and falls back to the
  deterministic reason if the model names any drug. This surfaces mechanism
  terms (bronchospasm, lactic acidosis) while keeping safety at 100%.

## 10. Combinations are narrated brand-only

A combination's ingredient name contains its component molecules as substrings
("Valsartex" inside "Valsartex + Hydroclorix"), and a component can itself be
the forbidden answer (E006). So combination substitutes are described by brand
only, never by ingredient name — the guard would otherwise leak a forbidden
substring through correct-looking prose.

## 11. Therapeutic swaps require a contraindication block, not mere absence

A cross-class (therapeutic) substitution is offered only when a generic/class
option existed and was blocked by a *patient contraindication* that rules out
the class (penicillin allergy -> macrolide, E009). It is refused — escalate —
when lower tiers were merely absent (E004/E023), blocked by an interaction with
the patient's own therapy (E021), or blocked by a paediatric contraindication
where the prescription itself needs review (E030).

## 12. Error analysis: five residual failures

Safety is 100%; these are `correct` misses, each a known limitation, not a bug:

1. **E002 (potency):** the text says "no Atorex or Lipidex", but the registry
   lists Lipidex as available. We suggest it (generic) instead of escalating to
   the class. Fixing needs text-implied stock override — deliberately not built
   (extraction stays advisory).
2. **E024 (clean_generic):** the only same-molecule alternative is in *shortage*;
   spec §8 restricts tier-1 to `status == available`, so we cross to the class.
   Respecting the frozen §8 over the case.
3. **E027 (interaction):** "patient on Thyroxel wants to *start* Omezel" is an
   add-a-drug question, not a substitution; the pipeline only models
   substitution, so it escalates.
4. **E005/E013 (tier label):** a same-molecule brand at a different strength is
   labelled `generic`; the case expects `class`. Safe either way; a
   classification nuance we did not contort the tier logic to match.
5. **E015/E019 (NTI drug-specific phrases):** "retest thyroid function",
   "breakthrough seizure" depend on the LLM producing an exact phrase from the
   leaflet; not reliably emitted. We chose not to hardcode per-drug strings.

## 13. The deterministic narration stub emits no prose

In `--no-llm` mode the prediction's `response_text` is empty. `score.py` counts
a forbidden ingredient appearing in the response text as a leak, so a stub that
named blocked or queried ingredients would fail cases it actually handled
correctly. Suggestions are carried structurally in `suggested_ingredients`;
prose arrives with the guarded LLM in phase 4.
