"""Phase 1 gate (spec section 11).

These must resolve correctly:
    كاردكس  -> Cardex      (Arabic alias)
    throxel  -> Thyroxel    (misspelling alias)
    kardex   -> Cardex      (misspelling alias)
    Carvex   -> Carvex      (exact brand, NOT the near-neighbour Cardex)
    Zeroxan  -> unresolved  (unknown, must not fuzzy-match)
"""

import pytest

from badeel.registry import get_registry


@pytest.fixture(scope="module")
def reg():
    return get_registry()


# ---- the five named gate cases -------------------------------------

def test_arabic_alias_resolves_to_cardex(reg):
    q = reg.resolve("كاردكس")
    assert q.resolved_brand == "Cardex"
    assert q.unresolved is False


def test_misspelling_throxel_resolves_to_thyroxel(reg):
    q = reg.resolve("throxel")
    assert q.resolved_brand == "Thyroxel"


def test_misspelling_kardex_resolves_to_cardex(reg):
    q = reg.resolve("kardex")
    assert q.resolved_brand == "Cardex"


def test_carvex_resolves_to_itself_not_cardex(reg):
    q = reg.resolve("Carvex")
    assert q.resolved_brand == "Carvex"
    assert q.resolved_brand != "Cardex"


def test_unknown_brand_is_unresolved_not_fuzzy_matched(reg):
    q = reg.resolve("Zeroxan")
    assert q.unresolved is True
    assert q.resolved_brand is None


# ---- resolution attaches ingredient identity ------------------------

def test_resolution_attaches_ingredient(reg):
    q = reg.resolve("Cardex")
    assert q.ingredient == "Veltolol"


def test_exact_match_scores_full(reg):
    q = reg.resolve("kardex")
    assert q.resolution_score == 100.0


# ---- resolution from a full sentence (Phase 2 will lean on this) ----

def test_resolves_brand_embedded_in_english_sentence(reg):
    q = reg.resolve("Atorex 20 mg is out of stock")
    assert q.resolved_brand == "Atorex"


def test_resolves_brand_embedded_in_arabic_sentence(reg):
    q = reg.resolve("كاردكس ١٠ ناقص والمريض عنده ربو")
    assert q.resolved_brand == "Cardex"


# ---- "did you mean?" suggestions (deterministic, near-miss only) ----

def test_gibberish_yields_no_suggestions(reg):
    # the Zeroxan gate case must stay unknown — no confident guess for gibberish
    assert reg.suggest("Zeroxan") == []
    assert reg.suggest("xqzwp") == []


def test_typo_surfaces_the_right_brand(reg):
    sug = reg.suggest("Thyrox")
    assert sug, "a plausible typo should surface at least one suggestion"
    assert sug[0].brand == "Thyroxel"
    assert sug[0].ingredient  # carries the molecule, for display
    # suggestions live strictly below the acceptance threshold (else they'd resolve)
    assert all(s.score < 88.0 for s in sug)


def test_unresolved_query_carries_suggestions(reg):
    q = reg.resolve("Thyrox")
    assert q.unresolved is True
    assert q.resolved_brand is None
    assert any(s.brand == "Thyroxel" for s in q.suggestions)


# ---- registry loads the full universe -------------------------------

def test_registry_loads_all_products(reg):
    assert len(reg.products) == 64


def test_registry_loads_all_ingredients(reg):
    assert len(reg.ingredients) == 26
