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

from rapidfuzz import fuzz, process, utils

from .config import ALIASES_CSV, FUZZY_THRESHOLD, INGREDIENTS_CSV, PRODUCTS_CSV
from .schemas import DrugQuery, Suggestion

# Word tokens including Arabic script.
_WORD = re.compile(r"[\w؀-ۿ]+", re.UNICODE)


class Registry:
    def __init__(self, products, ingredients, aliases):
        self.products = products                     # list[dict]
        self.ingredients = {i["ingredient_id"]: i for i in ingredients}
        self.ing_by_name = {i["name"]: i for i in ingredients}

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

    # ---- metadata accessors ------------------------------------------

    def is_combination(self, ingredient: str) -> bool:
        row = self.ing_by_name.get(ingredient)
        return bool(row and row.get("is_combination") == "1")

    def components(self, ingredient: str) -> frozenset[str]:
        """Active-ingredient component set. A single-molecule drug's set is
        just itself; a fixed-dose combination's is its declared components."""
        row = self.ing_by_name.get(ingredient)
        if row and row.get("components"):
            return frozenset(row["components"].split("|"))
        return frozenset({ingredient})

    def is_nti(self, ingredient: str) -> bool:
        row = self.ing_by_name.get(ingredient)
        return bool(row and row.get("nti") == "1")

    # ---- resolution ---------------------------------------------------

    def resolve(self, text: str) -> DrugQuery:
        raw = text or ""
        norm = raw.strip()
        low = norm.lower()

        brand, score = self._match(norm, low)
        if brand is None:
            return DrugQuery(raw_text=raw, unresolved=True, resolution_score=score,
                             suggestions=self.suggest(norm))

        prod = self.by_brand[brand]
        return DrugQuery(
            raw_text=raw,
            resolved_brand=brand,
            ingredient=prod["ingredient"],
            resolution_score=score,
            unresolved=False,
        )

    def suggest(self, text: str, limit: int = 3, floor: float = 70.0) -> list[Suggestion]:
        """Deterministic "did you mean?" candidates for a query that did not
        resolve. Only ever called on an unresolved query, so anything scoring at
        or above `floor` is worth offering; genuine gibberish scores below it and
        yields nothing, keeping an unknown drug unknown. Python proposes the
        brands — all real registry entries — and the pharmacist confirms.

        Scores the whole phrase *and* each individual word: a misspelled brand
        buried in a sentence ("concer is short") scores poorly against the full
        string but matches cleanly on its own token. Matching is
        case-insensitive, so "concer" and "Concer" behave identically.
        """
        raw = (text or "").strip()
        if not raw:
            return []
        probes = [raw] + [w for w in _WORD.findall(raw)
                          if len(w) >= 4 and not w.isdigit()]
        surfaces = list(self.surface_to_brand.keys())

        best: dict[str, float] = {}
        for probe in probes:
            for surface, score, _ in process.extract(
                    probe, surfaces, scorer=fuzz.WRatio,
                    processor=utils.default_process, limit=limit * 4):
                if score < floor:
                    continue
                brand = self.surface_to_brand[surface]
                if score > best.get(brand, 0.0):
                    best[brand] = float(score)

        ranked = sorted(best.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]
        return [Suggestion(brand=b,
                           ingredient=self.by_brand[b]["ingredient"], score=s)
                for b, s in ranked]

    def _match(self, norm: str, low: str) -> tuple[str | None, float]:
        # 1. exact alias
        if low in self.alias_map:
            return self.alias_map[low], 100.0
        # 2. exact brand
        if low in self._brand_lower:
            return self._brand_lower[low], 100.0
        # 3. substring scan over all surface forms + alias keys. The queried
        #    (out-of-stock) drug is the one mentioned FIRST; a proposed
        #    alternative ("...can I give Panadex?") comes later. So resolve by
        #    earliest position, then longest surface at that position. This is
        #    what keeps "Valtec 160 is out, can I give Valtec Plus" on Valtec,
        #    and "Cardex Plus is out" on the longer Cardex Plus.
        candidates = {**self._surface_lower, **self.alias_map}
        hits = [(low.find(surface), -len(surface), brand)
                for surface, brand in candidates.items()
                if _contains_word(low, surface)]
        if hits:
            _, _, brand = min(hits)
            return brand, 100.0
        # 4. fuzzy over surface forms only (brands + Arabic names). Matching is
        #    case-insensitive: without it "Marevn" scored 92 and resolved while
        #    the same typo in lowercase scored 77 and did not — the outcome must
        #    not depend on how the pharmacist capitalised the word.
        match = process.extractOne(
            norm, list(self.surface_to_brand.keys()), scorer=fuzz.WRatio,
            processor=utils.default_process)
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
