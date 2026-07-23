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

The drug universe is **fully synthetic** (fictional brands and ingredients with
realistic ATC-code structure), so the ground truth is true by construction and the
30-case evaluation set can be deliberately adversarial. Not for clinical use.

> For engineering detail, architecture and design tradeoffs, see
> [README_DEV.md](README_DEV.md) and [DECISIONS.md](DECISIONS.md).

---

# ✨ Features

* **Deterministic tier assignment & safety filter** — generic / same-class /
  therapeutic tiers and all safety checks are pure Python, not model output.
* **Validator guard (anti-hallucination)** — every LLM suggestion is validated
  against the retrieved candidate set; on failure the chain retries once with the
  error, then escalates. Guard trips are logged per model.
* **Safety-first behaviour** — the safety filter runs *before* ranking, so a blocked
  first-choice cedes to a safe alternative; narrow-therapeutic-index drugs
  short-circuit to escalation; unknown drugs are refused, not fuzzy-matched.
* **Grounded RAG narration with citations** — hybrid retrieval (dense embeddings +
  BM25 + reciprocal rank fusion) over SPC-style leaflets, chunked by section.
* **Bilingual input** — accepts Arabic and English pharmacist queries, with brand,
  misspelling and transliteration resolution.
* **Provider-agnostic LLM layer** — local Ollama or any OpenAI-compatible endpoint,
  selected purely by environment variables; embeddings always run locally and free.
* **Professional dispensing UI** — three views with a signature "tier rail" that
  makes the decision algorithm visible; refusals are as legible as approvals.
* **Reproducible, graded evaluation** — 30 adversarial cases, a harsh scorer, and a
  CI-friendly deterministic test suite (42 tests).

---

# 🛠️ Technologies Used

**Backend**

* Python 3.11, FastAPI, Uvicorn
* LangChain (LCEL, prompt-and-parse — no native tool calling)
* Pydantic v2 (data contracts + the validator guard)
* Chroma (vector store) · `sentence-transformers` `BAAI/bge-small-en-v1.5` (local embeddings)
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

**Run the API (deterministic, no model needed):**

```bash
cd backend && uvicorn main:app --reload          # http://localhost:8000
```

**Enable LLM narration (optional):**

```bash
BADEEL_NARRATE=1 uvicorn main:app --reload        # needs a provider in .env
```

**Run the frontend (dev):**

```bash
cd frontend && npm run dev                        # http://localhost:5173
```

**Try it** — ask a question in Arabic or English, e.g. `Cardex 10 mg is short and the
patient has asthma` → *Do not substitute* (all beta-blockers contraindicated), or
`Atorex 20 mg is out of stock` → a generic alternative with price and counselling.

**Reproduce the evaluation:**

```bash
python backend/scripts/run_eval.py --no-llm && python score.py predictions.jsonl   # deterministic
python backend/scripts/run_eval.py         && python score.py predictions.jsonl   # full pipeline
pytest backend/tests -q                                                            # 42 tests
```

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

> A public Hugging Face Spaces URL and a 3-minute demo video are added with the
> deployment step. The video opens with a refusal case, not a success case.

---

# 📈 Results

Measured on the 30-case adversarial evaluation set. **Safety** (never suggesting a
forbidden drug) is the primary metric.

| System                                   | Correct | Safe   |
| ---------------------------------------- | ------- | ------ |
| Ungrounded-LLM floor (baseline in spec)  | 3.3%    | 26.7%  |
| Deterministic naive baseline             | 0.0%    | 83.3%  |
| **Badeel — full pipeline (`gpt-oss:120b`)** | **60.0%** | **100.0%** |

Additional metrics for the full pipeline: tier accuracy **76.7%**, escalation
accuracy **86.7%**, recall **86.7%**, safety-flag coverage **66.7%**.

**Key finding:** the deterministic layer holds **safety at 100%** with or without the
model — it never suggests a forbidden ingredient. Adding the guarded LLM narration
lifts overall correctness roughly **9×** over the naive baseline **without touching
safety**. This is the argument of the project: the deterministic layer decides, the
model only writes, and the guard keeps the prose grounded.

---

# 🔮 Future Improvements

* **Cross-encoder reranker** (`bge-reranker-base`) on top of hybrid retrieval, with a
  measured with/without comparison.
* **Multi-model comparison table** (`gpt-oss:20b` → `gemma4:31b` → `gpt-oss:120b`) to
  show the guard-trip rate falling as model size rises.
* **Public deployment** on Hugging Face Spaces (single Docker image serving the API
  and the built frontend from one origin) plus the demo video.

---

# 📚 About the Challenge

This project was developed as part of the [**Tips Hindawi**](https://www.tipshindawi.com/) **Challenge (June–July) 2026**.

[Tips Hindawi](https://www.tipshindawi.com/) is the internships department of [**Edrak for Ai**](https://edrak4ai.com/en), and the challenge encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.

For more information about the challenge, training programs, and upcoming batches, visit the official [Tips Hindawi](https://www.tipshindawi.com/) website.

---

# 📄 License

This project is shared for educational and portfolio purposes.
