"""Tier generation is deterministic (spec section 8 step 4)."""

import pytest

from badeel.candidates import generate
from badeel.registry import get_registry


@pytest.fixture(scope="module")
def reg():
    return get_registry()


def _tiers(cands):
    return {c.ingredient: c.tier for c in cands}


def test_generic_is_same_ingredient_different_sku(reg):
    q = reg.resolve("Atorex")            # Atorvastin, in shortage
    tiers = _tiers(generate(q, reg))
    # Lipidex (Atorvastin) is another available SKU -> generic
    assert tiers.get("Atorvastin") == "generic"


def test_class_is_same_equiv_group_other_molecule(reg):
    q = reg.resolve("Atorex")            # statin
    tiers = _tiers(generate(q, reg))
    assert tiers.get("Rosuvastin") == "class"


def test_only_available_products_are_candidates(reg):
    q = reg.resolve("Atorex")
    for c in generate(q, reg):
        assert c.product["status"] == "available"


def test_queried_sku_is_not_a_candidate(reg):
    q = reg.resolve("Lipidex")           # Atorvastin, available
    qsku = reg.by_brand["Lipidex"]["sku"]
    assert all(c.product["sku"] != qsku for c in generate(q, reg))


def test_concurrent_med_is_never_a_candidate(reg):
    # Patient already on Ciproflaxen; it must not be offered as a substitute.
    q = reg.resolve("Azitrex")
    q.concurrent_meds = ["Ciproflaxen"]
    assert "Ciproflaxen" not in _tiers(generate(q, reg))


def test_therapeutic_shares_atc_subgroup_not_equiv_group(reg):
    # Amoxicillex (penicillin) -> Azithromycex (macrolide) is same J01 subgroup.
    q = reg.resolve("Penamox")
    tiers = _tiers(generate(q, reg))
    assert tiers.get("Azithromycex") == "therapeutic"
