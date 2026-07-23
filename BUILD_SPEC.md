# Badeel: Implementation Spec

Build a medicine substitution copilot that recommends alternatives when a prescribed product is
unavailable, and refuses to recommend when substitution is unsafe.

FastAPI backend, custom React frontend, provider-agnostic LLM layer.

This document is the full task. Read it end to end before writing code.

---

## 0. Hard constraints

| Constraint | Value |
|---|---|
| Wall clock budget | 3 days |
| Target | Deployed demo with measured eval results |
| Backend | FastAPI |
| Frontend | Vite + React + TypeScript + Tailwind |
| LLM | Provider agnostic. See section 4 |
| Cost ceiling | Zero. No paid APIs, no paid infra |
| Deployment | Hugging Face Spaces, Docker SDK, one container serving API and static frontend |
| Hardware assumption | MacBook Air M4, 24 GB, CPU or Metal inference for local models |

### Budget warning, read this before planning

A real backend plus a real frontend costs roughly a day more than a single-file UI would. The
eval, the guard and the safety layer are what make this project defensible, so they are not where
the time comes from. The frontend is capped at three views with no router and no state library.
Cross-encoder reranking is **optional** and is the first thing cut if a gate slips. Never cut the
guard or the eval.

---

## 1. What already exists

The dataset is built. **Do not regenerate it, do not modify it, do not add drugs to it.**

```text
data/
  ingredients.csv      26 rows, active ingredients with clinical fields
  products.csv         64 rows, brand/strength/form SKUs with stock status and price
  aliases.csv          misspellings and Arabic name to canonical brand map
  interactions.csv     pairwise interaction edges with severity
  leaflets/*.md        26 SPC-style documents, the RAG corpus
  eval_set.jsonl       30 labelled adversarial cases
  DATASET_CARD.md      provenance, trap taxonomy, scoring rules

pharmacopeia.py        source data, hand authored
eval_cases.py          source eval cases, hand authored
build_dataset.py       regenerates data/ from the two files above
score.py               grades predictions.jsonl against eval_set.jsonl
```

The drug universe is fictional. Names like Veltolol, Cardex and Warfaridine are invented. ATC code
structure is real so class logic behaves realistically. Every leaflet carries a synthetic data
banner and the UI must carry one too.

### Baseline to beat

A naive system that always returns its top same-class match and never escalates scores:

```text
overall correct     3.3%
safety (no leaks)  26.7%
```

Reproduce this baseline first and commit the number. It is the before column in your results table.

---

## 2. Non-negotiable rules

These are the design decisions that make the project defensible. Do not relax them.

1. **Tier assignment is deterministic, not generated.** The LLM never decides whether something is
   a generic, class or therapeutic substitute. That comes from `products.csv` and `equiv_group`
   lookups in Python. The LLM writes rationale prose and extracts structured fields. Nothing else.

2. **Safety filtering runs after candidate generation and before ranking.** A tier-1 candidate that
   fails a safety check is dropped, which allows a tier-2 candidate to win. Eval case E008 exists
   specifically to test this. Do not filter after ranking.

3. **The Pydantic validator guard is mandatory.** Any suggested ingredient not present in the
   retrieved candidate set causes a validation error. The chain retries once with the error message
   appended. On second failure it escalates. This is the anti-hallucination mechanism and the
   headline feature of the project.

4. **NTI drugs short circuit everything.** If `nti` is true on the queried ingredient, return
   `tier="none"`, `escalate=true` before generating any candidates. No exceptions, including
   same-ingredient brand switches.

5. **Unknown input is refused, not fuzzy matched.** If alias resolution and fuzzy matching both
   score below threshold, return "not found in registry". Case E028 queries a drug that does not
   exist. Matching it to the nearest brand is a hard fail.

6. **If the eval fails, fix the system, not the eval.** Do not edit `eval_cases.py`, do not soften
   `score.py`, do not add products so a case passes. If you believe a case is genuinely wrong,
   write the argument in `DECISIONS.md` and leave the case alone.

7. **Never depend on native tool calling or provider-specific structured output.** Free and local
   models vary wildly in support. Use prompt-and-parse: instruct JSON only, strip code fences,
   `json.loads`, then Pydantic validate, then retry on failure. The guard retry protocol already
   provides the retry loop.

---

## 3. Repository layout

```text
badeel/
  backend/
    main.py                 FastAPI app, routes, CORS, static mount
    badeel/
      __init__.py
      config.py             paths, model names, thresholds, env parsing
      llm.py                provider factory, see section 4
      registry.py           CSV loading, alias resolution, fuzzy brand matching
      schemas.py            all Pydantic models, shared with the API layer
      retrieval.py          Chroma ingestion, hybrid search, optional reranking
      candidates.py         tier generation, deterministic
      safety.py             contraindication, interaction, form, strength checks
      chains.py             LCEL chains: extraction, rationale
      guard.py              validator guard and retry logic
      pipeline.py           orchestration, the single public entry point
    prompts/
      extraction.v1.md
      rationale.v1.md
    tests/
      test_registry.py
      test_candidates.py
      test_safety.py
      test_guard.py
      test_retrieval.py
      test_api.py
    scripts/
      ingest.py             build the Chroma index
      run_eval.py           run pipeline over eval_set, write predictions.jsonl
      compare_models.py     run eval across providers, see section 12
    requirements.txt
  frontend/
    src/
      App.tsx
      api.ts                typed client, mirrors backend schemas
      types.ts              hand-mirrored from schemas.py
      components/
        QueryBar.tsx
        TierRail.tsx        the signature element, see section 10
        SubstituteCard.tsx
        SafetyPanel.tsx
        BlockedList.tsx
        SyntheticBanner.tsx
      views/
        Console.tsx
        EvalBrowser.tsx
        Results.tsx
    index.html
    package.json
    tailwind.config.ts
    vite.config.ts
  data/                     already built, read only
  chroma/                   persisted index, committed to the repo
  Dockerfile
  .env.example
  README.md
  DECISIONS.md
  .github/workflows/eval.yml
```

---

## 4. LLM provider layer

The project must run against a local model, an OpenAI-compatible router, or Ollama Cloud, selected
purely by environment variables. No code changes when switching.

```python
# backend/badeel/llm.py
import os
from langchain_core.language_models import BaseChatModel


def get_llm(temperature: float = 0.0) -> BaseChatModel:
    """
    LLM_PROVIDER=ollama          local Ollama daemon
    LLM_PROVIDER=openai_compat   anything speaking the OpenAI API:
                                 OpenRouter, Ollama Cloud, LM Studio, Together, vLLM
    """
    provider = os.getenv("LLM_PROVIDER", "ollama")
    model = os.getenv("LLM_MODEL", "qwen2.5:7b-instruct")

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=model,
            base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            temperature=temperature,
            num_ctx=8192,
        )

    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=model,
        base_url=os.getenv("LLM_BASE_URL"),
        api_key=os.getenv("LLM_API_KEY", "not-needed"),
        temperature=temperature,
        timeout=60,
        max_retries=2,
    )
```

`.env.example` must document all four working configurations:

```bash
# Local Ollama
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5:7b-instruct
OLLAMA_HOST=http://localhost:11434

# Ollama Cloud
# LLM_PROVIDER=openai_compat
# LLM_MODEL=qwen2.5:72b
# LLM_BASE_URL=https://ollama.com/v1
# LLM_API_KEY=...

# OpenRouter free tier
# LLM_PROVIDER=openai_compat
# LLM_MODEL=meta-llama/llama-3.3-70b-instruct:free
# LLM_BASE_URL=https://openrouter.ai/api/v1
# LLM_API_KEY=...

# LM Studio
# LLM_PROVIDER=openai_compat
# LLM_MODEL=local-model
# LLM_BASE_URL=http://localhost:1234/v1
```

### Model size reality

A 7B local model will trip the validator guard more often than a 70B. That is a result, not a
problem, and section 12 turns it into a deliverable. Develop against the local model because the
loop is fast and free, then run the final numbers against the largest free option available.

---

## 5. Stack

```text
# backend
fastapi
uvicorn[standard]
langchain>=0.3
langchain-core
langchain-community
langchain-ollama
langchain-openai
langchain-huggingface
chromadb
sentence-transformers
rank-bm25
rapidfuzz
pydantic>=2.7
pandas
pytest
httpx

# frontend
react react-dom
typescript vite @vitejs/plugin-react
tailwindcss
```

| Component | Choice | Note |
|---|---|---|
| Embeddings | `BAAI/bge-small-en-v1.5` | 384 dim, CPU friendly, runs local always |
| Reranker | `BAAI/bge-reranker-base` | optional, phase 6 only |
| Vector store | Chroma, persisted to `./chroma` | commit the directory so the Space boots cold |
| Lexical | `rank_bm25` over the same chunks | |
| Fuzzy | `rapidfuzz.process.extractOne` | threshold 88, tuned in phase 1 |

Embeddings stay local regardless of LLM provider. They are small, free, and remove a network
dependency from the hot path.

---

## 6. Data contracts

Define these in `schemas.py` exactly. The eval harness and the frontend both depend on the field
names. Mirror them in `frontend/src/types.ts`.

```python
from typing import Literal
from pydantic import BaseModel, Field, model_validator

Tier = Literal["generic", "class", "therapeutic", "none"]
Severity = Literal["minor", "moderate", "major"]


class DrugQuery(BaseModel):
    raw_text: str
    resolved_brand: str | None = None
    ingredient: str | None = None
    strength: str | None = None
    form: str | None = None
    patient_flags: list[str] = Field(default_factory=list)
    concurrent_meds: list[str] = Field(default_factory=list)
    resolution_score: float = 0.0
    unresolved: bool = False


class Citation(BaseModel):
    leaflet: str          # filename, e.g. "carvedanol.md"
    section: str          # e.g. "Contraindications"
    snippet: str          # under 200 chars


class SafetyFlag(BaseModel):
    kind: Literal["contraindication", "interaction", "form", "strength",
                  "combination", "nti", "potency", "class_block"]
    severity: Severity
    message: str
    evidence: list[Citation] = Field(default_factory=list)


class BlockedCandidate(BaseModel):
    """A candidate that was generated then rejected. Surfaced in the UI for transparency."""
    ingredient: str
    brand: str | None = None
    tier: Tier
    reason: str
    flag: SafetyFlag


class Substitute(BaseModel):
    brand: str
    ingredient: str
    strength: str
    form: str
    tier: Tier
    price_egp: float
    price_delta_pct: float
    rationale: str
    counselling_flags: list[str] = Field(default_factory=list)
    evidence: list[Citation] = Field(default_factory=list)


class SubstitutionAnswer(BaseModel):
    query: DrugQuery
    tier: Tier
    escalate: bool
    escalation_reason: str | None = None
    substitutes: list[Substitute] = Field(default_factory=list)
    safety_flags: list[SafetyFlag] = Field(default_factory=list)
    blocked_candidates: list[BlockedCandidate] = Field(default_factory=list)
    confidence: float = 0.0
    guard_trips: int = 0
    latency_ms: int = 0
    model_used: str = ""

    @model_validator(mode="after")
    def escalation_implies_no_substitutes(self):
        if self.escalate and self.substitutes:
            raise ValueError("escalate=True must not be accompanied by substitutes")
        if self.tier == "none" and self.substitutes:
            raise ValueError('tier="none" must not be accompanied by substitutes')
        return self
```

---

## 7. API contract

All routes under `/api`. `SubstitutionAnswer` is returned verbatim as JSON.

### `POST /api/substitute`

Request:

```json
{
  "text": "كاردكس ١٠ ناقص والمريض عنده ربو",
  "patient_flags": ["bronchial asthma"],
  "concurrent_meds": []
}
```

`patient_flags` and `concurrent_meds` are optional. When present they override anything extracted
from `text`. Response is a `SubstitutionAnswer`.

| Code | Meaning |
|---|---|
| `200` | Answer produced, including refusals and escalations |
| `422` | Malformed request body |
| `503` | LLM provider unreachable |

An escalation is a successful response, not an error. Never return 4xx for a refusal.

```bash
curl -X POST http://localhost:8000/api/substitute \
  -H "Content-Type: application/json" \
  -d '{"text":"Cardex 10 mg is short","patient_flags":["bronchial asthma"]}'
```

### `GET /api/registry/products`

All 64 SKUs, for frontend autocomplete.

```json
[{"sku":"SKU001","brand":"Cardex","brand_ar":"كاردكس","ingredient":"Veltolol",
  "strength":"5 mg","form":"tablet","status":"available","price_egp":48.0}]
```

### `GET /api/registry/options`

Multiselect vocabularies, derived from the CSVs rather than hardcoded.

```json
{"patient_flags":["bronchial asthma","pregnancy","severe renal impairment"],
 "ingredients":["Veltolol","Warfaridine"]}
```

### `GET /api/eval/cases`

All 30 eval cases, so the frontend can load them into the console.

### `GET /api/eval/results`

The most recent `eval_report.json` if present, for the results view.

### `GET /api/health`

```json
{"status":"ok","provider":"ollama","model":"qwen2.5:7b-instruct","chroma_docs":312}
```

### CORS

Allow `http://localhost:5173` in development. In the deployed container the frontend is served from
the same origin, so no CORS is needed there. Do not ship `allow_origins=["*"]`.

---

## 8. The substitution algorithm

Implement in `pipeline.py` in this exact order.

```text
 1. RESOLVE
    raw text -> alias table -> exact brand match -> rapidfuzz over brands and Arabic names
    if best score < threshold: return unresolved, escalate, "not found in registry"

 2. NTI GATE
    if ingredient.nti: return tier="none", escalate=True, reason=NTI
    stop here, generate no candidates

 3. UPSTREAM CHECK
    check the ORIGINAL prescription against patient_flags
    if the queried drug is itself contraindicated for this patient:
        flag it, escalate, and say the prescription needs review
    (cases E017 and E030 test this)

 4. CANDIDATES
    tier 1 generic     same ingredient, different SKU, status == available
    tier 2 class       same equiv_group, different ingredient
    tier 3 therapeutic same ATC level 3 prefix, different equiv_group
    combination products: candidates must have identical component sets

 5. SAFETY FILTER  (applied to every candidate, drops it into blocked_candidates)
    a. contraindication  candidate contraindications vs patient_flags
    b. interaction       candidate vs each concurrent_med in interactions.csv
    c. form              ER/SR/MR vs IR mismatch -> flag, and escalate if the
                         queried product is the modified release one
    d. strength          if no candidate SKU can reproduce the queried strength,
                         escalate rather than suggest splitting or rounding
    e. combination       dropping or adding an active ingredient is a block
    f. potency           within-class potency difference -> keep but add flag

 6. DECIDE
    if no candidates survive: tier="none", escalate=True
    else: tier = lowest surviving tier, rank survivors

 7. RANK
    primary   tier
    secondary stock status (available before shortage)
    tertiary  price ascending
    quaternary manufacturer continuity

 8. NARRATE
    RAG retrieval over leaflets scoped to the surviving candidates plus the queried drug
    LLM writes rationale and counselling_flags only, constrained by the guard
```

### Retrieval detail

Chunk leaflets by markdown H2 section, not by fixed token window. Section headers are the semantic
unit and carry the label the safety chain needs. Store `leaflet` and `section` in metadata so
`Citation` can be populated without extra parsing.

Hybrid search: dense top 20, BM25 top 20, reciprocal rank fusion, then optionally cross encoder
rerank to top 5. Measure the eval with and without the reranker and record both numbers.

---

## 9. The validator guard

This is the feature that satisfies competition criterion 4. Build it carefully.

```python
# guard.py
from pydantic import BaseModel, model_validator

class GuardedSuggestion(BaseModel):
    """LLM output is parsed into this. Validation context carries the allowlist."""
    ingredient: str
    rationale: str
    counselling_flags: list[str] = []

    @model_validator(mode="after")
    def ingredient_must_be_in_candidate_set(self, info):
        allowed = (info.context or {}).get("allowed_ingredients")
        if allowed is None:
            raise ValueError("guard misconfigured: no allowlist in validation context")
        if self.ingredient not in allowed:
            raise ValueError(
                f"'{self.ingredient}' is not in the retrieved candidate set "
                f"{sorted(allowed)}. You may only suggest from that set."
            )
        return self
```

Retry protocol:

1. Invoke the rationale chain, parse into `GuardedSuggestion` with
   `model_validate(obj, context={"allowed_ingredients": allowed})`.
2. On `ValidationError`, append the error string to the prompt as a correction turn and invoke
   once more.
3. On a second `ValidationError`, do not invoke again. Return `tier="none"`, `escalate=True`,
   `escalation_reason="model could not produce a grounded suggestion"`.
4. Log every guard trip to `logs/guard_trips.jsonl` with case id, attempt number, rejected
   ingredient, model name and the allowlist.

**Report the guard trip rate per model in the README.** It is the most interesting number in the
project. A non-zero trip rate proves the guard is doing work rather than being decoration.

---

## 10. Frontend

Three views, no router library, no state library. `useState` and `fetch` are sufficient at this
size. Reaching for Redux or React Query means over-building.

### Design direction

The user is a licensed pharmacist standing at a counter with a customer waiting. The screen has
one job: answer "can I swap this" in under fifteen seconds, and make a refusal as legible as an
approval. This is a dense professional instrument, not a consumer product page. No hero section,
no marketing copy, no gradient cards.

Draw the visual vocabulary from dispensing labels and printed pharmacopoeia monographs: tight
rules, small caps section labels, monospace for codes and strengths, whitespace only where it aids
scanning.

**Palette.** Do not use warm cream with a terracotta accent, and do not use near-black with a
single acid accent. Both read as generated defaults. Use a paper-neutral surface with ink text and
let one signal colour carry state:

```text
--paper      #FBFAF7   surface
--ink        #16181A   primary text
--ink-muted  #6B7280   secondary text
--rule       #E3E1DB   hairlines and dividers
--clear      #1F6F4A   substitution permitted
--caution    #B45309   permitted with counselling flags
--stop       #A61B1B   blocked or escalated
```

Signal colours appear only on state, never on chrome. A page with no result is monochrome.

**Type.** IBM Plex superfamily. `IBM Plex Sans` for interface, `IBM Plex Sans Arabic` for Arabic
input and mirrored labels, `IBM Plex Mono` for ATC codes, SKUs, strengths and prices. One coherent
family with real Arabic coverage, and not the Inter default. Set a deliberate scale: oversized for
the verdict line, small and tight everywhere else.

**Signature element: the tier rail.** A vertical rail down the left of the results area with four
stops, generic / class / therapeutic / none. Each stop shows how many candidates were generated at
that tier and how many survived the safety filter. Blocked tiers are struck through with the
blocking reason set inline in small caps. This makes the algorithm in section 8 directly visible,
which is the entire argument of the project. Spend the design effort here and keep everything
around it quiet.

**Motion.** One thing only: the tier rail resolves top to bottom as the answer arrives, so the eye
follows the descent through the tiers. Nothing else animates. Respect `prefers-reduced-motion`.

### Views

**Console.** Query bar accepting Arabic and English. Two multiselects for patient flags and
concurrent meds, populated from `/api/registry/options`. Results area with the tier rail on the
left, substitute cards centre, safety flags right. Blocked candidates in a collapsed disclosure
labelled "considered and rejected".

**Eval browser.** Table of the 30 cases with trap label. Clicking one loads it into the console.
Judges will use this, and it makes the demo video trivial to record.

**Results.** The before and after table, guard trip rates, per-trap breakdown. Read from
`/api/eval/results`.

### Copy rules

Write from the pharmacist's side of the screen. When the system refuses, say what is blocked and
what to do next, in the interface's voice: "Do not substitute. Refer to the prescriber for INR
review." Not "Sorry, I cannot help with that." Errors are never vague and never apologise.

The verdict line is the largest element on screen and states the outcome plainly: "Substitution
permitted", "Permitted with counselling", "Do not substitute". Never bury an escalation under a
list of near misses.

### Persistent banner

Fixed at the top of every view: synthetic data, not for clinical use, decision support for a
licensed pharmacist rather than a patient facing tool. It does not scroll away and it is not
dismissible.

---

## 11. Build phases with acceptance gates

Do not start a phase until the previous gate passes.

### Phase 1: registry and resolution

Load the CSVs. Build alias resolution and fuzzy matching.

**Gate:** `pytest tests/test_registry.py` green, and these resolve correctly: `كاردكس` to Cardex,
`throxel` to Thyroxel, `kardex` to Cardex, `Carvex` to Carvex and not Cardex, `Zeroxan` to
unresolved.

### Phase 2: candidates and safety, no LLM

Implement steps 2 through 7 of the algorithm as pure Python. Stub the narration.

**Gate:** `python scripts/run_eval.py --no-llm`. Safety score at or above **80%**. Achievable with
no LLM because tier logic and safety filtering are deterministic. Below 80% means a logic bug, not
a model problem.

### Phase 3: API skeleton

FastAPI with all routes from section 7, wired to the phase 2 pipeline. Narration still stubbed.

**Gate:** `pytest tests/` green including httpx route tests. `/api/health` returns provider and
document count. All 30 eval cases answerable through `POST /api/substitute`.

### Phase 4: retrieval and chains

Chroma ingestion with section-level chunking, hybrid search, extraction and rationale chains,
validator guard, retry protocol.

**Gate:** full eval run against your chosen provider. Safety at or above **90%**, overall correct
at or above **60%**. Guard trip rate recorded.

### Phase 5: frontend

Three views. Tier rail. Wired to the real API.

**Gate:** every eval case runnable from the browser. Escalation cases visibly different from
permitted cases at a glance from two metres away.

### Phase 6: reranker, model comparison, deploy

Optional reranker. Model comparison table. Docker build. HF Space.

**Gate:** public URL loads and answers all 30 queries. Results table in the README.

---

## 12. Model comparison deliverable

The eval harness already exists, so running it across providers is nearly free and produces the
strongest result in the project.

`scripts/compare_models.py` runs the full eval against each configured provider and emits:

| Model | Provider | Correct | Safe | Guard trips | Median latency |
|---|---|---|---|---|---|
| qwen2.5:7b-instruct | local Ollama | | | | |
| qwen2.5:14b-instruct | local Ollama | | | | |
| llama-3.3-70b-instruct:free | OpenRouter | | | | |

The expected finding is that safety score stays high across all three while guard trip rate falls
as model size rises. If that holds, it is direct evidence that the deterministic safety layer is
carrying the correctness and the model is only writing prose. State that conclusion explicitly in
the README. If it does not hold, say so and explain why. A negative result honestly reported beats
a fabricated positive one.

---

## 13. Deployment

Single Docker image. Multi-stage: build the frontend with Node, copy `dist/` into the Python image,
serve it with `StaticFiles(directory="dist", html=True)` mounted at `/`. FastAPI serves both API
and app on one origin, so there is no CORS in production and one thing to deploy.

Hugging Face Spaces, Docker SDK, port 7860. Commit `chroma/` so the Space does not rebuild the
index on cold start. Provider credentials go in Space secrets.

If no provider is reachable, the app must still boot and serve the deterministic pipeline with
narration disabled, showing a visible notice. A demo that degrades is better than a demo that 500s
in front of a judge.

---

## 14. CI

`.github/workflows/eval.yml` runs pytest and the deterministic eval on every push. Fail the build
if safety drops below the phase 2 gate of 80%. Skip LLM-dependent tests in CI so no secret is
needed.

---

## 15. Definition of done

- [ ] Baseline, phase 4 and phase 6 numbers in a results table in the README
- [ ] Safety score at or above 90%
- [ ] All 30 cases produce a parseable `SubstitutionAnswer`
- [ ] Guard trip rate reported per model
- [ ] Model comparison table with a stated conclusion
- [ ] Error analysis of five failures with hypotheses
- [ ] Public HF Spaces URL
- [ ] `.env.example` documenting all four provider configurations
- [ ] `DECISIONS.md` listing every tradeoff made under time pressure
- [ ] Three minute demo video that opens with an escalation case, not a success case

---

## 16. Scope guards

Do not build any of these, however tempting:

- Prescription image OCR
- User accounts, history, or any database beyond the CSVs
- Agents with tool loops, LCEL chains only
- Fine tuning of any kind
- Additional drugs, ingredients or eval cases
- Real drug data from openFDA, RxNorm or any external API
- A component library, router, or state management library in the frontend
- Streaming responses, unless phases 1 to 6 are all green with time left

If a phase gate slips by more than half a day, cut in this order: reranking, then model comparison,
then the eval browser view. Never cut the guard, the eval or the escalation UI.

---

## 17. First actions

1. Read `data/DATASET_CARD.md` in full.
2. Read `eval_cases.py` in full. Every `note` field explains what the case is testing.
3. Reproduce the 3.3% baseline and commit it.
4. Write `DECISIONS.md` with one entry: the provider chosen for development and why.
5. Start phase 1.

Ask before deviating from sections 2, 6, 8 or 9. Everything else is yours to judge.
