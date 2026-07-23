# Badeel

A medicine substitution copilot. It recommends alternatives when a prescribed
product is unavailable, and **refuses** when substitution is unsafe.

The defining design decision: the LLM never reasons clinically. Tier assignment,
safety filtering and escalation are deterministic Python driven by the CSV
registry. A Pydantic validator guard rejects any ingredient the model invents
outside the retrieved candidate set. The model only writes prose.

> **SYNTHETIC DATA. NOT FOR CLINICAL USE.** Every drug name and clinical
> statement in this project is fictional, generated for software evaluation.
> Decision support for a licensed pharmacist, not a patient-facing tool.

## Status

| Phase | What | State |
|---|---|---|
| 0  | Dataset (26 ingredients, 64 products, 26 leaflets, 30 eval cases) | ✅ done |
| 0b | Naive baseline reproduced and recorded | ✅ done |
| 1  | Registry + alias/fuzzy resolution | ✅ done |
| 2  | Candidates + safety filter (no LLM) | ✅ done — safety **100%** |
| 3  | FastAPI skeleton (all §7 routes) | ✅ done — 36 tests green |
| 4  | Retrieval + chains + validator guard | ✅ done — correct **60%**, safe **100%** |
| 5  | Frontend | ⏳ |
| 6  | Reranker, model comparison, deploy | ⏳ |

## Results

| System | correct | safe | tier | escalation |
|---|---|---|---|---|
| Ungrounded-LLM floor (spec §1) | 3.3% | 26.7% | — | — |
| Deterministic naive baseline (`scripts/baseline.py`) | 0.0% | 83.3% | 23% | 43% |
| Phase 2 deterministic pipeline (no LLM) | 6.7% | **100%** | 70% | 80% |
| **Phase 4 full pipeline** (`gpt-oss:120b`, Ollama Cloud) | **60.0%** | **100%** | 77% | 87% |

The argument of the project in one table: the deterministic layer holds
**safety at 100%** with or without the model — it never suggests a forbidden
ingredient. Adding the guarded LLM narration lifts `correct` from 6.7% to 60%
(it supplies the required clinical counselling prose) **without touching
safety**. The model writes; the deterministic layer decides. See
[DECISIONS.md](DECISIONS.md).

**Validator guard.** Every LLM suggestion is parsed into a Pydantic model whose
validator rejects any ingredient outside the retrieved candidate set; the chain
retries once with the error appended, then escalates. A strong model
(`gpt-oss:120b`) trips it rarely (0–1 per full run); the per-model trip-rate
trend is the Phase 6 model-comparison deliverable. The mechanism is proven by
`tests/test_guard.py` (fully offline).

Reproduce:

```bash
# deterministic only (phase 2 gate, no model needed)
python backend/scripts/run_eval.py --no-llm && python score.py predictions.jsonl

# full pipeline (needs a provider in .env + the chroma index)
python backend/scripts/ingest.py                  # one-time, or use committed chroma/
python backend/scripts/run_eval.py && python score.py predictions.jsonl
```

## Layout

```text
pharmacopeia.py  eval_cases.py  build_dataset.py  score.py   source data + harness (root)
data/            generated, read-only: CSVs, leaflets/, eval_set.jsonl
scripts/
  baseline.py    naive "before" baseline
backend/
  badeel/        config, schemas, registry (more per phase)
  tests/         pytest
docs/            phase plan
```

## Develop

```bash
uv venv --python 3.11 && source .venv/bin/activate
uv pip install -r backend/requirements.txt

python scripts/baseline.py            # writes predictions.baseline.jsonl
python score.py predictions.baseline.jsonl

cd backend && python -m pytest -q    # 36 tests
uvicorn main:app --reload            # API on :8000, docs at /docs
```

Health check once running:

```bash
curl -s localhost:8000/api/health
curl -s -X POST localhost:8000/api/substitute \
  -H 'Content-Type: application/json' \
  -d '{"text":"Cardex 10 mg is short","patient_flags":["bronchial asthma"]}'
```
