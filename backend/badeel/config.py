"""Paths and thresholds. No logic lives here."""

import os
from pathlib import Path

# Repo root is two levels up from this file: backend/badeel/config.py -> root
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"

INGREDIENTS_CSV = DATA / "ingredients.csv"
PRODUCTS_CSV = DATA / "products.csv"
ALIASES_CSV = DATA / "aliases.csv"
INTERACTIONS_CSV = DATA / "interactions.csv"
LEAFLETS_DIR = DATA / "leaflets"

# Persisted Chroma index (built in phase 4) and the latest eval report written
# by score.py at the repo root.
CHROMA_DIR = ROOT / "chroma"
EVAL_REPORT = ROOT / "eval_report.json"

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
