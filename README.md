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
| 2  | Candidates + safety filter (no LLM) | ⏳ |
| 3  | FastAPI skeleton | ⏳ |
| 4  | Retrieval + chains + validator guard | ⏳ |
| 5  | Frontend | ⏳ |
| 6  | Reranker, model comparison, deploy | ⏳ |

## Results

| System | correct | safe |
|---|---|---|
| Ungrounded-LLM floor (spec §1) | 3.3% | 26.7% |
| Deterministic naive baseline (`scripts/baseline.py`) | 0.0% | 83.3% |
| Badeel (target, phase 4) | ≥ 60% | ≥ 90% |

See [DECISIONS.md](DECISIONS.md) for why the two baseline rows differ.

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

pytest backend/tests -q
```
