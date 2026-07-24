"""Paths and thresholds. No logic lives here."""

import os
from pathlib import Path

# Repo root is two levels up from this file: backend/badeel/config.py -> root
ROOT = Path(__file__).resolve().parents[2]

# Dataset selection. "synthetic" (default) is the graded/eval build; "real" is
# the demo dataset of real ingredients + real Egyptian brand names in
# data/real/. Chosen at process start via BADEEL_DATASET.
DATASET = os.getenv("BADEEL_DATASET", "synthetic").lower()
_REAL = DATASET == "real"

DATA = ROOT / "data" / "real" if _REAL else ROOT / "data"

INGREDIENTS_CSV = DATA / "ingredients.csv"
PRODUCTS_CSV = DATA / "products.csv"
ALIASES_CSV = DATA / "aliases.csv"
INTERACTIONS_CSV = DATA / "interactions.csv"
LEAFLETS_DIR = DATA / "leaflets"

# Persisted Chroma index (per dataset) and the latest eval report at the root.
CHROMA_DIR = ROOT / ("chroma_real" if _REAL else "chroma")
EVAL_REPORT = ROOT / "eval_report.json"

# The evaluation is defined on the synthetic dataset only (its ground truth is
# true by construction). The eval routes read it regardless of the active
# dataset, so the Eval browser works even in real-drug demo mode.
EVAL_SET = ROOT / "data" / "eval_set.jsonl"

# LLM identity for /api/health, read from the environment (see .env.example).
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:7b-instruct")

# Frontend dev origin allowed by CORS. Production serves the built frontend from
# the same origin, so no CORS entry is needed there.
DEV_ORIGIN = os.getenv("DEV_ORIGIN", "http://localhost:5173")

# Fuzzy brand-match acceptance threshold (rapidfuzz WRatio, 0-100).
# Tuned so that Carvex resolves to Carvex, never to the near-neighbour Cardex,
# and a non-existent brand (Zeroxan) stays unresolved. See tests/test_registry.py.
FUZZY_THRESHOLD = float(os.getenv("FUZZY_THRESHOLD", "88"))

# Optional cross-encoder reranker over the hybrid-retrieval results. Off by
# default: it only sharpens the leaflet evidence fed to the LLM narration, never
# the deterministic decision, and it pulls a ~1 GB model on first use. Turn on
# with BADEEL_RERANK=1 to demo/measure the retrieval-quality improvement.
RERANK = os.getenv("BADEEL_RERANK", "0") == "1"
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")
