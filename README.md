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
| 4  | Retrieval + chains + validator guard | ⏳ |
| 5  | Frontend | ⏳ |
| 6  | Reranker, model comparison, deploy | ⏳ |

## Results

| System | correct | safe | tier | escalation |
|---|---|---|---|---|
| Ungrounded-LLM floor (spec §1) | 3.3% | 26.7% | — | — |
| Deterministic naive baseline (`scripts/baseline.py`) | 0.0% | 83.3% | 23% | 43% |
| **Phase 2 deterministic pipeline (no LLM)** | 6.7% | **100%** | 70% | 80% |
| Badeel (target, phase 4 with narration) | ≥ 60% | ≥ 90% | — | — |

The Phase 2 pipeline is deterministic and does no narration, so `correct` and
the `must_flag` clinical phrases stay low until the LLM lands in phase 4 — but
**safety is already 100%**: it never suggests a forbidden ingredient. That is
the whole argument of the project: the deterministic layer carries safety, the
model only writes prose. See [DECISIONS.md](DECISIONS.md).

Reproduce:

```bash
python backend/scripts/run_eval.py --no-llm   # writes predictions.jsonl
python score.py predictions.jsonl
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
