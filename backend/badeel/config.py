"""Paths and thresholds. No logic lives here."""

import os
from pathlib import Path

# Repo root is two levels up from this file: backend/badeel/config.py -> root
ROOT = Path(__file__).resolve().parents[2]

# Dataset selection. "synthetic" is the graded/eval build (ground truth true by
# construction); "real" is the demo build of real ingredients + real Egyptian
# brand names in data/real/. The two are kept completely separate — never merged
# — so a synthetic eval query can never resolve against a real brand.
#
# BADEEL_DATASET sets the *default*, but each request may pick its own, so the
# demo can run on real drugs while the eval browser still runs on synthetic.
DATASETS = ("synthetic", "real")
DATASET = os.getenv("BADEEL_DATASET", "synthetic").lower()
if DATASET not in DATASETS:
    DATASET = "synthetic"


def data_dir(dataset: str) -> Path:
    """Directory holding one dataset's CSVs and leaflets."""
    return ROOT / "data" / "real" if dataset == "real" else ROOT / "data"


def chroma_dir(dataset: str) -> Path:
    """Persisted vector index, one per dataset."""
    return ROOT / ("chroma_real" if dataset == "real" else "chroma")


# Default-dataset paths, kept for scripts and tests that work on one build.
DATA = data_dir(DATASET)
INGREDIENTS_CSV = DATA / "ingredients.csv"
PRODUCTS_CSV = DATA / "products.csv"
ALIASES_CSV = DATA / "aliases.csv"
INTERACTIONS_CSV = DATA / "interactions.csv"
LEAFLETS_DIR = DATA / "leaflets"

CHROMA_DIR = chroma_dir(DATASET)
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
