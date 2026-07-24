"""Retriever fusion + optional reranker, proven without network or model loads.

The reranker (spec section 8, phase 6) reorders the fused pool by direct
query-passage relevance. We construct a Retriever with fake internals — a stub
Chroma collection, a stub BM25 and a pre-seeded stub cross-encoder — so the
reordering logic is provable offline, exactly as the guard tests use a fake LLM.
"""

from badeel.retrieval import Retriever

IDS = ["leaf::Contraindications", "leaf::Storage",
       "leaf::Drug Interactions", "leaf::Adverse Reactions"]
TEXTS = ["contra text", "storage text", "interactions text", "adverse text"]
META = [
    {"leaflet": "leaf.md", "section": "Contraindications", "ingredient": "Drug"},
    {"leaflet": "leaf.md", "section": "Storage", "ingredient": "Drug"},
    {"leaflet": "leaf.md", "section": "Drug Interactions", "ingredient": "Drug"},
    {"leaflet": "leaf.md", "section": "Adverse Reactions", "ingredient": "Drug"},
]


class FakeCollection:
    """Returns a fixed dense ranking; ignores the actual embedding."""
    def __init__(self, dense_order):
        self._order = dense_order

    def query(self, query_texts, n_results, where=None):
        return {"ids": [self._order[:n_results]]}

    def count(self):
        return len(IDS)


class FakeBM25:
    def __init__(self, scores):
        self._scores = scores

    def get_scores(self, toks):
        return self._scores


class FakeCrossEncoder:
    """Scores each (query, passage) pair by a passage->score lookup."""
    def __init__(self, by_text):
        self._by_text = by_text

    def predict(self, pairs):
        return [self._by_text[text] for _query, text in pairs]


def _retriever(dense_order, bm25_scores):
    # both signals favour the Storage chunk, so the fused top-1 is Storage
    return Retriever(FakeCollection(dense_order), IDS, TEXTS, META, FakeBM25(bm25_scores))


def test_no_rerank_returns_fused_order_with_expected_keys():
    r = _retriever(dense_order=list(IDS), bm25_scores=[0.1, 9.0, 0.2, 0.0])
    out = r.search("q", k=3, rerank=False)
    assert len(out) == 3
    assert set(out[0]) == {"leaflet", "section", "ingredient", "text"}
    # Storage wins the fusion (top of both dense-ish and BM25)
    assert out[0]["section"] == "Storage"


def test_rerank_reorders_to_cross_encoder_ranking():
    r = _retriever(dense_order=list(IDS), bm25_scores=[0.1, 9.0, 0.2, 0.0])
    # pre-seed the stub cross-encoder so _reranker() never imports/loads a model;
    # make it prefer the clinically useful Contraindications passage
    r._ce = FakeCrossEncoder({
        "contra text": 5.0, "storage text": 0.1,
        "interactions text": 4.0, "adverse text": 0.2,
    })
    out = r.search("q", k=3, rerank=True)
    assert out[0]["section"] == "Contraindications"   # reranker overrides fusion
    assert out[1]["section"] == "Drug Interactions"
    # and it genuinely changed the order vs no-rerank (which led with Storage)
    assert out[0]["section"] != r.search("q", k=3, rerank=False)[0]["section"]
