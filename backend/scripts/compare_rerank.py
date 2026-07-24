#!/usr/bin/env python3
"""Measure retrieval quality with vs without the cross-encoder reranker.

    python backend/scripts/compare_rerank.py
    BADEEL_DATASET=real python backend/scripts/compare_rerank.py

The reranker only reorders the leaflet passages that ground the LLM narration —
it never touches the deterministic decision — so this measures *retrieval*, not
the graded eval. With no gold relevance labels we use a label-free proxy: within
the scoped drug, does the top passage land on a clinically high-value section
(Contraindications / Interactions / Substitution Notes / Composition) rather than
boilerplate (Storage / Adverse Reactions)?

First `--on` run downloads BAAI/bge-reranker-base (~1 GB), then caches it.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from badeel.registry import get_registry      # noqa: E402
from badeel.retrieval import get_retriever     # noqa: E402

HIGH_VALUE = {"Contraindications", "Drug Interactions",
              "Substitution Notes", "Composition and Available Forms"}
K = 4
N_PROBES = 8


def build_probes(reg):
    """Narration-style queries, one per ingredient that has a brand + leaflet,
    mirroring how pipeline.py phrases the retrieval query."""
    probes = []
    for name in reg.ing_by_name:
        brand = next((p["brand"] for p in reg.products if p["ingredient"] == name), None)
        if not brand:
            continue
        probes.append((f"{brand} {name} substitution", name))
        if len(probes) >= N_PROBES:
            break
    return probes


def first_hv_rank(records):
    for i, r in enumerate(records, start=1):
        if r["section"] in HIGH_VALUE:
            return i
    return None


def run(retriever, probes, rerank):
    top1_hits, ranks, rows = 0, [], []
    for query, ing in probes:
        recs = retriever.search(query, scope=[ing], k=K, rerank=rerank)
        secs = [r["section"] for r in recs]
        if recs and recs[0]["section"] in HIGH_VALUE:
            top1_hits += 1
        ranks.append(first_hv_rank(recs) or (K + 1))
        rows.append((ing, secs))
    return top1_hits, ranks, rows


def main():
    reg = get_registry()
    retriever = get_retriever()
    probes = build_probes(reg)
    n = len(probes)
    print(f"\nProbes: {n}   k={K}   high-value sections: {sorted(HIGH_VALUE)}\n")

    off_hits, off_ranks, off_rows = run(retriever, probes, rerank=False)
    print("Loading reranker (first run downloads ~1 GB)...")
    on_hits, on_ranks, on_rows = run(retriever, probes, rerank=True)

    print("\nper-probe top-1 section  (RRF  ->  reranked):")
    for (ing, off_secs), (_, on_secs) in zip(off_rows, on_rows):
        mark = "  *" if off_secs[:1] != on_secs[:1] else ""
        print(f"  {ing:16s} {off_secs[0]:26s} -> {on_secs[0]}{mark}")

    def pct(h): return 100.0 * h / n if n else 0.0
    def mean(xs): return sum(xs) / len(xs) if xs else 0.0

    print("\n" + "=" * 52)
    print(f"{'metric':32s}{'RRF':>9s}{'rerank':>9s}")
    print("-" * 52)
    print(f"{'top-1 high-value hit-rate':32s}{pct(off_hits):8.1f}%{pct(on_hits):8.1f}%")
    print(f"{'mean rank of first high-value':32s}{mean(off_ranks):9.2f}{mean(on_ranks):9.2f}")
    print("=" * 52)
    print("\nNote: safety/tier/escalation are unaffected either way — retrieval only\n"
          "grounds the narration. Run run_eval.py with BADEEL_RERANK=0 then =1 to\n"
          "confirm the graded numbers are identical.\n")


if __name__ == "__main__":
    main()
