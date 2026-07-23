"""CSV loading, alias resolution and fuzzy brand matching.

Pure and deterministic. No LLM, no network. The public entry point is
`Registry.resolve(text)`, which returns a `DrugQuery`.

Resolution order (spec section 8, step 1):
    1. exact alias table (misspellings + Arabic names)
    2. exact brand match
    3. surface-form substring scan (handles "Atorex 20 mg is short")
    4. rapidfuzz over brand + Arabic surface forms, threshold 88
    5. below threshold -> unresolved (spec rule 2.5, never fuzzy-match unknowns)
"""

from __future__ import annotations

import csv
import re
from functools import lru_cache

from rapidfuzz import fuzz, process

from .config import ALIASES_CSV, FUZZY_THRESHOLD, INGREDIENTS_CSV, PRODUCTS_CSV
from .schemas import DrugQuery

# Word tokens including Arabic script.
_WORD = re.compile(r"[\w؀-ۿ]+", re.UNICODE)


class Registry:
    def __init__(self, products, ingredients, aliases):
        self.products = products                     # list[dict]
        self.ingredients = {i["ingredient_id"]: i for i in ingredients}

        # First SKU seen per brand is enough for brand-level identity.
        self.by_brand: dict[str, dict] = {}
        for p in products:
            self.by_brand.setdefault(p["brand"], p)

        # Canonical brand set, lowercased index.
        self.brands = sorted(self.by_brand)
        self._brand_lower = {b.lower(): b for b in self.brands}

        # alias (lowercased) -> canonical brand. Covers misspellings and Arabic.
        self.alias_map: dict[str, str] = {}
        for a in aliases:
            self.alias_map[a["alias"].strip().lower()] = a["canonical_brand"]

        # Every surface form we are willing to match against, mapped to its
        # canonical brand. Used for the substring scan and fuzzy step.
        self.surface_to_brand: dict[str, str] = {}
        for b in self.brands:
            self.surface_to_brand[b] = b
            ar = self.by_brand[b].get("brand_ar")
            if ar:
                self.surface_to_brand[ar] = b
        self._surface_lower = {s.lower(): b for s, b in self.surface_to_brand.items()}

    # ---- construction -------------------------------------------------

    @classmethod
    def load(cls) -> "Registry":
        return cls(
            products=_read_csv(PRODUCTS_CSV),
            ingredients=_read_csv(INGREDIENTS_CSV),
            aliases=_read_csv(ALIASES_CSV),
        )

    # ---- resolution ---------------------------------------------------

    def resolve(self, text: str) -> DrugQuery:
        raw = text or ""
        norm = raw.strip()
        low = norm.lower()

        brand, score = self._match(norm, low)
        if brand is None:
            return DrugQuery(raw_text=raw, unresolved=True, resolution_score=score)

        prod = self.by_brand[brand]
        return DrugQuery(
            raw_text=raw,
            resolved_brand=brand,
            ingredient=prod["ingredient"],
            resolution_score=score,
            unresolved=False,
        )

    def _match(self, norm: str, low: str) -> tuple[str | None, float]:
        # 1. exact alias
        if low in self.alias_map:
            return self.alias_map[low], 100.0
        # 2. exact brand
        if low in self._brand_lower:
            return self._brand_lower[low], 100.0
        # 3. substring scan over all surface forms + alias keys, longest wins.
        #    A whole-string query already fell through 1/2, so this catches
        #    brands embedded in a sentence ("No Atorex 20 mg anywhere").
        candidates = {**self._surface_lower,
                      **{a: b for a, b in self.alias_map.items()}}
        hits = [(surface, brand) for surface, brand in candidates.items()
                if _contains_word(low, surface)]
        if hits:
            surface, brand = max(hits, key=lambda sb: len(sb[0]))
            return brand, 100.0
        # 4. fuzzy over surface forms only (brands + Arabic names).
        match = process.extractOne(
            norm, list(self.surface_to_brand.keys()), scorer=fuzz.WRatio)
        if match and match[1] >= FUZZY_THRESHOLD:
            return self.surface_to_brand[match[0]], float(match[1])
        # 5. unresolved
        best = float(match[1]) if match else 0.0
        return None, best


def _contains_word(text: str, surface: str) -> bool:
    """True if surface appears as a whole token (or token run) inside text."""
    if surface not in text:
        return False
    # require token boundaries so "carvex" does not match inside "carvexil"
    pattern = r"(?<![\w؀-ۿ])" + re.escape(surface) + r"(?![\w؀-ۿ])"
    return re.search(pattern, text) is not None


def _read_csv(path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


@lru_cache(maxsize=1)
def get_registry() -> Registry:
    """Process-wide singleton so CSVs load once."""
    return Registry.load()
