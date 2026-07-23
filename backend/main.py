"""Badeel FastAPI app: routes, CORS, static mount (spec section 7).

Thin by design — every route delegates to the deterministic pipeline. Narration
is still stubbed in phase 3; the LLM chains arrive in phase 4. An escalation or
refusal is a normal 200 response, never a 4xx.
"""

from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from badeel import config
from badeel.pipeline import answer
from badeel.registry import get_registry
from badeel.safety import FLAG_KEYWORDS
from badeel.schemas import SubstitutionAnswer, SubstituteRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_registry()   # load CSVs once at boot, not on first request
    yield


app = FastAPI(title="Badeel", version="0.3.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.DEV_ORIGIN],   # never "*": production is same-origin
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- API routes --------------------------------------------------------

# Narration (LLM rationale) is opt-in: it needs a reachable provider and loads
# the embedding/vector stack. Off by default so the app is fast and boots with
# no model (spec §13 degraded mode). Set BADEEL_NARRATE=1 with a provider in the
# environment to enable grounded prose in the browser.
NARRATE = os.getenv("BADEEL_NARRATE", "0") == "1"


@app.post("/api/substitute", response_model=SubstitutionAnswer)
def substitute(req: SubstituteRequest) -> SubstitutionAnswer:
    return answer(req.text, req.patient_flags, req.concurrent_meds,
                  get_registry(), narrate=NARRATE)


@app.get("/api/registry/products")
def registry_products():
    reg = get_registry()
    return [
        {"sku": p["sku"], "brand": p["brand"], "brand_ar": p["brand_ar"],
         "ingredient": p["ingredient"], "strength": p["strength"],
         "form": p["form"], "status": p["status"],
         "price_egp": float(p["price_egp"])}
        for p in reg.products
    ]


@app.get("/api/registry/options")
def registry_options():
    """Multiselect vocabularies derived from the data, not hardcoded in the UI.
    patient_flags is the controlled set the safety layer actually understands;
    concurrent_meds are ingredient names the patient might already be taking."""
    reg = get_registry()
    return {
        "patient_flags": sorted(FLAG_KEYWORDS.keys()),
        "ingredients": sorted(reg.ing_by_name.keys()),
    }


@app.get("/api/eval/cases")
def eval_cases():
    lines = (config.DATA / "eval_set.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(l) for l in lines if l.strip()]


@app.get("/api/eval/results")
def eval_results():
    if config.EVAL_REPORT.exists():
        return json.loads(config.EVAL_REPORT.read_text(encoding="utf-8"))
    return {"available": False, "rows": []}


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "provider": config.LLM_PROVIDER,
        "model": config.LLM_MODEL,
        "chroma_docs": _doc_count(),
        "narration": "enabled" if NARRATE else "stubbed",
        "dataset": config.DATASET,
    }


# ---- helpers -----------------------------------------------------------

def _doc_count() -> int:
    """Documents available to the RAG layer. Before the Chroma index exists
    (phase 4), report the number of leaflet H2 sections that will be indexed."""
    total = 0
    for path in config.LEAFLETS_DIR.glob("*.md"):
        total += sum(1 for line in path.read_text(encoding="utf-8").splitlines()
                     if line.startswith("## "))
    return total


# ---- static frontend (mounted last, only if built) ---------------------

def _mount_frontend() -> None:
    for candidate in (Path(__file__).parent / "dist",
                      Path(__file__).parent.parent / "frontend" / "dist"):
        if candidate.is_dir():
            app.mount("/", StaticFiles(directory=str(candidate), html=True),
                      name="frontend")
            return


_mount_frontend()
