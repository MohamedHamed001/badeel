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

# Fuzzy brand-match acceptance threshold (rapidfuzz WRatio, 0-100).
# Tuned so that Carvex resolves to Carvex, never to the near-neighbour Cardex,
# and a non-existent brand (Zeroxan) stays unresolved. See tests/test_registry.py.
FUZZY_THRESHOLD = float(os.getenv("FUZZY_THRESHOLD", "88"))
