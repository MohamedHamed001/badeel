#!/usr/bin/env python3
"""Build the persisted Chroma index from the leaflets.

    python backend/scripts/ingest.py

Commit the resulting ./chroma directory so the deployed Space boots cold without
re-embedding (spec section 13).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from badeel.retrieval import get_retriever  # noqa: E402


def main():
    r = get_retriever()
    print(f"indexed {r.doc_count} leaflet sections into {ROOT / 'chroma'}")


if __name__ == "__main__":
    main()
