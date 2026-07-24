# 🚀 [Tips Hindawi](https://www.tipshindawi.com/) Challenge (June–July) 2026

> 🏆 This repository is my official submission for the [ **Tips Hindawi** ](https://www.tipshindawi.com/) **Challenge (June–July) 2026**.

## 👤 Participant

| Field            | Value                                |
| ---------------- | ------------------------------------ |
| Full Name        | Mohamed Hamed                        |
| Project Name     | Badeel (بديل) — Medicine Substitution Copilot |
| GitHub Username  | [MohamedHamed001](https://github.com/MohamedHamed001) |
| Challenge Batch  | June–July 2026                       |
| Training Program | Large Language Models (LLMs) Program |
| Organization     | [**Edrak for Ai**](https://edrak4ai.com/en)                         |

---

# 📖 Project Overview

**Badeel** ("substitute" in Arabic) is a decision-support copilot for pharmacists.
When a prescribed medicine is out of stock, it recommends a safe alternative — and,
just as importantly, **refuses to recommend one when substitution is unsafe** and
escalates to the prescriber instead.

The core design idea is that **the language model never makes a clinical decision.**
Whether a substitute is a generic, a same-class, or a therapeutic alternative is
decided deterministically in Python from a drug registry; the safety filter
(contraindications, drug interactions, narrow-therapeutic-index drugs, dosage form,
strength and combination-product rules) also runs in Python. The LLM only writes the
counselling prose, and a **Pydantic validator guard** rejects any drug it names that
is not in the retrieved candidate set — the project's anti-hallucination mechanism.

The graded drug universe is **fully synthetic** (fictional brands and ingredients with
realistic ATC-code structure), so the ground truth is true by construction and the
30-case evaluation set can be deliberately adversarial. A second, parallel dataset of
**real molecules and real Egyptian brand names** (Concor, Plavix, Glucophage…) ships
alongside it for demonstration — the pipeline is data-agnostic and runs unchanged on
either. Not for clinical use.

---

# ✨ Features

* **Deterministic tier assignment & safety filter** — generic / same-class /
  therapeutic tiers and all safety checks are pure Python, not model output.
* **LLM comprehension of the request** — the model *reads* the free-text query into
  structured fields (intent, drug, patient conditions, concurrent meds); Python then
  re-validates every field (drug via the registry, conditions against the safety
  vocabulary) before any of it reaches a decision. It understands "available" vs "out
  of stock", and lifts a condition stated in prose ("…and the patient has asthma")
  into the safety filter — while never choosing a drug or a verdict itself.
* **Validator guard (anti-hallucination)** — every LLM suggestion is validated
  against the retrieved candidate set; on failure the chain retries once with the
  error, then escalates. Guard trips are logged per model.
* **Safety-first behaviour** — the safety filter runs *before* ranking, so a blocked
  first-choice cedes to a safe alternative; narrow-therapeutic-index drugs
  short-circuit to escalation; unknown drugs are refused, not fuzzy-matched.
* **Grounded RAG narration with citations** — hybrid retrieval (dense embeddings +
  BM25 + reciprocal rank fusion) over SPC-style leaflets, chunked by section, with an
  optional cross-encoder reranker (`bge-reranker-base`, env-gated).
* **Bilingual input** — accepts Arabic and English pharmacist queries, with brand,
  misspelling and transliteration resolution.
* **"Did you mean?" suggestions** — an unrecognised or mistyped product surfaces the
  fuzzy resolver's near-misses as one-click chips (real registered brands only). The
  LLM never chooses which drug the pipeline runs on — Python proposes, the pharmacist
  confirms.
* **Provider-agnostic LLM layer** — local Ollama or any OpenAI-compatible endpoint,
  selected purely by environment variables; embeddings always run locally and free.
* **Professional dispensing UI** — three views with a signature "tier rail" that
  makes the decision algorithm visible; refusals are as legible as approvals. Full
  **English ⇄ العربية** toggle with real RTL layout, interface and clinical text.
* **Two interchangeable datasets** — the graded synthetic universe, or a real-drug demo
  set (real molecules, real Egyptian brands) selected with one environment variable.
* **Degrades gracefully** — with no model reachable the app still boots and serves the
  complete deterministic pipeline; only the prose and comprehension switch off.
* **Reproducible, graded evaluation** — 30 adversarial cases, a harsh scorer, and a
  CI-friendly deterministic test suite (53 tests, fully offline).

---

# 🛠️ Technologies Used

**Backend**

* Python 3.11, FastAPI, Uvicorn (JSON API + Server-Sent Events streaming)
* LangChain (LCEL, prompt-and-parse — no native tool calling)
* Pydantic v2 (data contracts + the validator guard)
* Chroma (vector store) · `sentence-transformers` `BAAI/bge-small-en-v1.5` (local embeddings)
* `BAAI/bge-reranker-base` cross-encoder (optional reranking)
* `rank_bm25` (lexical search) · `rapidfuzz` (fuzzy brand resolution)
* pandas · pytest

**Frontend**

* Vite + React + TypeScript
* Tailwind CSS v4
* IBM Plex superfamily (bundled locally; Sans / Sans Arabic / Mono)

**LLM providers**

* Ollama Cloud / local Ollama / any OpenAI-compatible endpoint
* Developed & evaluated against `gpt-oss:120b` (Ollama Cloud, free tier)

---

# 🗂️ Repository structure

```
backend/
  main.py                  FastAPI app: routes, CORS, SSE, static mount
  badeel/
    registry.py            CSV load + brand resolution (aliases, fuzzy, suggestions)
    candidates.py          tier generation: generic / same-class / therapeutic
    safety.py              the six safety checks + patient-flag vocabulary
    comprehension.py       LLM reads the query -> Python re-validates every field
    retrieval.py           RAG: Chroma dense + BM25 + RRF (+ optional reranker)
    guard.py               the Pydantic validator guard (anti-hallucination)
    chains.py  llm.py      prompt-and-parse chains, provider factory
    pipeline.py            orchestration — the single entry point, answer()
    schemas.py  config.py  i18n.py
  prompts/*.md             versioned LLM prompt templates
  scripts/                 ingest.py · run_eval.py · compare_rerank.py
  tests/                   53 offline tests
frontend/src/              Vite + React + TS: views, components, i18n, api client
data/                      synthetic dataset (graded) + data/real/ (demo)
pharmacopeia.py            source of truth for the synthetic drug universe
eval_cases.py              the 30 labelled adversarial cases
build_dataset.py           renders the sources into data/
score.py                   the grader (harsh, safety-first)
```

A rule the layout enforces: `candidates.py` never imports `safety.py`, and neither
imports `llm.py` — that separation is what makes "the model never decides" verifiable
rather than aspirational.

---

# ⚙️ Installation

**Requirements:** Python 3.11+, Node 18+.

```bash
# 1. Backend
python -m venv .venv && source .venv/bin/activate     # or: uv venv --python 3.11
pip install -r backend/requirements.txt

# 2. Build the vector index (or use the committed chroma/ directory)
python backend/scripts/ingest.py

# 3. Frontend
cd frontend && npm install && npm run build           # outputs frontend/dist
```

**LLM configuration** — copy `.env.example` to `.env` and fill one provider block
(local Ollama, Ollama Cloud, OpenRouter, or LM Studio). Embeddings run locally and
need no key. The app also boots and serves the full deterministic pipeline with **no
provider at all** (narration simply disabled).

---

# 🚀 Usage

**Run the API (deterministic, no model needed).** Run from `backend/` — that is where
`main.py` lives. Once `frontend/dist` exists it is served from the same origin, so
`http://localhost:8000` gives you the whole app:

```bash
cd backend && uvicorn main:app --reload          # http://localhost:8000
```

**Enable the LLM (narration + query comprehension):**

```bash
cd backend && BADEEL_NARRATE=1 uvicorn main:app --reload    # needs a provider in .env
```

**Run the frontend with hot reload (optional, for development):**

```bash
cd frontend && npm run dev                        # http://localhost:5173
```

**Environment flags** — all optional, all off by default:

| Variable | Default | Effect |
| --- | --- | --- |
| `BADEEL_NARRATE` | `0` | `1` enables LLM narration **and** query comprehension |
| `BADEEL_DATASET` | `synthetic` | `real` switches to the real-drug demo dataset |
| `BADEEL_RERANK` | `0` | `1` adds the cross-encoder reranker (downloads ~1 GB once) |
| `FUZZY_THRESHOLD` | `88` | brand fuzzy-match acceptance (0–100) |

**Try it** — ask in Arabic or English, e.g. `Cardex 10 mg is short and the patient has
asthma` → *Do not substitute* (all beta-blockers contraindicated), or `Atorex 20 mg is
out of stock` → a generic alternative with price and counselling. With `BADEEL_NARRATE=1`,
`Atorex is available` is understood as **not a shortage** rather than a substitution request.

**Reproduce the evaluation:**

```bash
python backend/scripts/run_eval.py --no-llm && python score.py predictions.jsonl   # deterministic
python backend/scripts/run_eval.py         && python score.py predictions.jsonl   # full pipeline
cd backend && pytest tests -q                                                      # 53 tests, offline
```

The evaluation always runs on the synthetic dataset with structured inputs, so the
graded numbers are independent of the demo dataset, the UI language, and the
comprehension layer.

**API examples:**

```bash
curl -X POST http://localhost:8000/api/substitute \
  -H "Content-Type: application/json" \
  -d '{"text":"Cardex 10 mg is short","patient_flags":["bronchial asthma"]}'
```

---

# 📸 Demo

The interface has three views, all under a fixed "synthetic data — not for clinical
use" banner:

* **Console** — a pharmacist query bar (Arabic + English) with patient-flag and
  concurrent-medication selectors. The verdict line is the largest element on screen:
  a green **Substitution permitted**, an amber **Permitted with counselling**, or a
  red **Do not substitute**. The signature **tier rail** on the left shows how many
  candidates were generated and survived at each tier; blocked tiers are struck
  through with the reason, so the algorithm's descent to a decision is visible at a
  glance.
* **Eval browser** — the 30 adversarial cases with their trap labels; one click loads
  a case into the console.
* **Results** — the before/after table and per-trap breakdown.

**Cases worth trying** (start with the refusals — they are the point of the project):

| Query | Outcome |
| --- | --- |
| `Coagulex 5 mg is short` | **Do not substitute** — narrow therapeutic index, refer to prescriber |
| `Cardex 10 mg is short` + *bronchial asthma* | **Do not substitute** — every beta-blocker is contraindicated |
| `Denufex is unavailable` | **Do not substitute** — no alternative exists; the hallucination trap |
| `Atorex 20 mg is out of stock` | Generic alternative, with price delta and counselling |
| `Gastrolux is out, patient takes Clopidex` | A *blocked* first choice cedes to a safe same-class option |
| `Zeroxan is short` | Not in registry — refused, with "did you mean?" suggestions |

Run the demo on real Egyptian brand names with `BADEEL_DATASET=real` (Concor, Plavix,
Risek, Marevan…). The app runs locally; public deployment is listed under future work.

---

# 📈 Results

Measured on the 30-case adversarial evaluation set. **Safety** (never suggesting a
forbidden drug) is the primary metric.

| System                                      | Correct   | Safe       |
| ------------------------------------------- | --------- | ---------- |
| Ungrounded-LLM floor (baseline in spec)     | 3.3%      | 26.7%      |
| Deterministic naive baseline (class swap)   | 0.0%      | 83.3%      |
| Badeel — deterministic only, no model        | 6.7%      | **100.0%** |
| **Badeel — full pipeline (`gpt-oss:120b`)** | **56.7%** | **100.0%** |

Additional metrics for the full pipeline: tier accuracy **76.7%**, escalation
accuracy **86.7%**, recall **86.7%**, safety-flag coverage **63.3%**, with **3 guard
trips** across the 30 cases — the guard is load-bearing, not decorative.

Safety is **100% in every one of the 13 trap categories** — 30/30 cases, no exceptions,
including the hallucination trap (`no_substitute`, where no alternative exists at all),
the narrow-therapeutic-index cases, and the brand-collision pairs.

**Key finding — read the third row against the fourth.** The deterministic layer alone
already holds **safety at 100%**: with no model reachable at all, it never suggests a
forbidden ingredient. What the guarded LLM adds is *helpfulness* — correctness rises
from 6.7% to 56.7% (roughly **8×**) while safety does not move, because the model is
never allowed to touch the decision. That is the whole argument of the project: the
deterministic layer decides, the model only writes, and the guard keeps the prose
grounded.

*On reproducibility:* tier, escalation, recall and safety are deterministic and
reproduce exactly. The two prose-dependent metrics (overall correct, safety-flag
coverage) move by about one case between runs, because the scorer checks whether the
model's wording surfaced specific safety concepts and hosted models are not perfectly
repeatable even at `temperature=0`. Safety is unaffected either way.

(The deterministic row scores low on *correctness* by construction: with narration off
it emits no prose, so it cannot satisfy the scorer's `must_flag` requirement that
specific safety concepts be stated in words. Its tier and escalation decisions are
identical to the full pipeline's.)

### Retrieval reranker (ablation)

The optional cross-encoder reranker (`BADEEL_RERANK=1`) reorders the leaflet passages
that ground the narration. It only touches the *explanation*, never the decision —
retrieval output is consumed by the narration chains alone, so the graded
tier/escalate/safety numbers are identical with it on or off (confirm:
`BADEEL_RERANK=0` then `=1` through `run_eval.py`). Measured on an 8-probe set with a
label-free proxy (does the top passage land on a clinically high-value section?):

| Retrieval | top-1 high-value hit-rate |
| --------- | ------------------------- |
| Hybrid + RRF        | 12.5% |
| **+ cross-encoder** | **25.0%** |

Reproduce with `python backend/scripts/compare_rerank.py`. The gain is real but
modest — retrieval is already scoped to a single drug's ~10 sections — and that is the
point: safety is architecturally decoupled from retrieval, so better retrieval sharpens
the counselling prose while the decision stays provably unaffected.

---

# 🔮 Future Improvements

* **Public deployment** on Hugging Face Spaces (single Docker image serving the API
  and the built frontend from one origin) plus the demo video.
* **LLM-assisted resolution** — let the model *propose* a spelling correction, then
  force it back through the deterministic registry so only a real registered brand is
  ever accepted (the model suggests, Python confirms).

---

# 📚 About the Challenge

This project was developed as part of the [**Tips Hindawi**](https://www.tipshindawi.com/) **Challenge (June–July) 2026**.

[Tips Hindawi](https://www.tipshindawi.com/) is the internships department of [**Edrak for Ai**](https://edrak4ai.com/en), and the challenge encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.

For more information about the challenge, training programs, and upcoming batches, visit the official [Tips Hindawi](https://www.tipshindawi.com/) website.

---

# 📄 License

This project is shared for educational and portfolio purposes.
