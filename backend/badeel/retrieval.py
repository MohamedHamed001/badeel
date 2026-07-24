"""Leaflet retrieval: Chroma dense search + BM25 lexical + reciprocal rank
fusion (spec section 8).

Leaflets are chunked by markdown H2 section — the section is the semantic unit
and carries the label the safety chain needs — and each chunk stores `leaflet`,
`section` and `ingredient` metadata so Citations populate without reparsing.

Embeddings are local (BAAI/bge-small-en-v1.5) regardless of the LLM provider.
"""

from __future__ import annotations

import re
from functools import lru_cache

from . import config
from .config import CHROMA_DIR, LEAFLETS_DIR

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
COLLECTION = "leaflets"

# Size of the fused pool handed to the reranker. Wider than k so the cross
# encoder has room to reorder; ignored when reranking is off.
RERANK_POOL = 20


def _chunks():
    """Yield (id, text, metadata) for every H2 section of every leaflet."""
    for path in sorted(LEAFLETS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        m = re.match(r"#\s+(.+)", text)
        ingredient = m.group(1).strip() if m else path.stem
        for section, body in _sections(text):
            body = body.strip()
            if not body:
                continue
            yield (f"{path.stem}::{section}",
                   f"{section}\n{body}",
                   {"leaflet": path.name, "section": section,
                    "ingredient": ingredient})


def _sections(text: str):
    parts = re.split(r"^##\s+(.+)$", text, flags=re.MULTILINE)
    # parts[0] is the preamble; then (header, body) pairs
    for i in range(1, len(parts), 2):
        yield parts[i].strip(), parts[i + 1]


class Retriever:
    def __init__(self, collection, chunk_ids, chunk_texts, chunk_meta, bm25):
        self._col = collection
        self._ids = chunk_ids
        self._texts = chunk_texts
        self._meta = chunk_meta
        self._bm25 = bm25
        self._ce = None   # cross-encoder, loaded lazily on first rerank

    @classmethod
    def load(cls) -> "Retriever":
        import chromadb
        from chromadb.utils import embedding_functions
        from rank_bm25 import BM25Okapi

        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL)
        col = client.get_or_create_collection(COLLECTION, embedding_function=ef)

        ids, texts, metas = [], [], []
        for cid, text, meta in _chunks():
            ids.append(cid)
            texts.append(text)
            metas.append(meta)

        if col.count() == 0:
            col.add(ids=ids, documents=texts, metadatas=metas)

        bm25 = BM25Okapi([_tok(t) for t in texts])
        return cls(col, ids, texts, metas, bm25)

    @property
    def doc_count(self) -> int:
        return self._col.count()

    def search(self, query: str, scope: list[str] | None = None, k: int = 5,
               rerank: bool | None = None):
        """Hybrid dense+BM25 with RRF. `scope` restricts to these ingredients.

        `rerank` layers a cross-encoder on top of the fused ranking: the RRF
        order picks a wide pool, the reranker reorders it by direct
        query-passage relevance, and the top `k` are returned. Defaults to
        `config.RERANK`; pass an explicit bool to compare modes in one process.
        This only changes which leaflet passages ground the LLM prose — never
        the deterministic decision.
        """
        if rerank is None:
            rerank = config.RERANK
        where = {"ingredient": {"$in": scope}} if scope else None

        dense = self._col.query(query_texts=[query], n_results=RERANK_POOL, where=where)
        dense_ids = dense["ids"][0] if dense["ids"] else []

        scored = self._bm25.get_scores(_tok(query))
        order = sorted(range(len(scored)), key=lambda i: scored[i], reverse=True)
        allowed = set(scope) if scope else None
        lex_ids = []
        for i in order:
            if allowed and self._meta[i]["ingredient"] not in allowed:
                continue
            lex_ids.append(self._ids[i])
            if len(lex_ids) >= RERANK_POOL:
                break

        idx = {cid: i for i, cid in enumerate(self._ids)}
        fused = [cid for cid in _rrf(dense_ids, lex_ids) if cid in idx]

        if rerank and fused:
            pool = fused[:RERANK_POOL]
            pairs = [(query, self._texts[idx[cid]]) for cid in pool]
            scores = self._reranker().predict(pairs)
            pool = [cid for _, cid in sorted(zip(scores, pool),
                                             key=lambda z: z[0], reverse=True)]
            ordered = pool[:k]
        else:
            ordered = fused[:k]

        return [
            {"leaflet": self._meta[idx[cid]]["leaflet"],
             "section": self._meta[idx[cid]]["section"],
             "ingredient": self._meta[idx[cid]]["ingredient"],
             "text": self._texts[idx[cid]]}
            for cid in ordered
        ]

    def _reranker(self):
        """Lazy cross-encoder — loaded once, only when reranking is used, so the
        ~1 GB model never touches the default path, the --no-llm eval, or CI."""
        if self._ce is None:
            from sentence_transformers import CrossEncoder
            self._ce = CrossEncoder(config.RERANK_MODEL)
        return self._ce


def _rrf(*ranked_lists, kconst: int = 60) -> list[str]:
    """Reciprocal rank fusion over id lists."""
    score: dict[str, float] = {}
    for lst in ranked_lists:
        for rank, cid in enumerate(lst):
            score[cid] = score.get(cid, 0.0) + 1.0 / (kconst + rank + 1)
    return sorted(score, key=lambda c: score[c], reverse=True)


def _tok(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


@lru_cache(maxsize=1)
def get_retriever() -> Retriever:
    return Retriever.load()
