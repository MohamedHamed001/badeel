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
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from badeel import config
from badeel.pipeline import answer
from badeel.registry import get_registry
from badeel.safety import FLAG_KEYWORDS
from badeel.schemas import SubstitutionAnswer, SubstituteRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_registry()   # load CSVs once at boot, not on first request
    if os.getenv("BADEEL_NARRATE", "0") == "1":
        # Warm the embedding/vector stack at startup so the FIRST narration
        # request doesn't pay the torch cold-start (several seconds).
        try:
            from badeel.retrieval import get_retriever
            get_retriever()
        except Exception:
            pass
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
                  get_registry(), narrate=NARRATE, lang=req.lang)


def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/api/substitute/stream")
def substitute_stream(req: SubstituteRequest):
    """Deterministic answer first (instant), then the LLM rationale streamed
    token-by-token for the top substitute. The prose leak-guard runs once the
    stream completes: if the streamed text names a non-permitted drug it is
    dropped. Falls back cleanly to a deterministic-only stream if no model is
    reachable or narration is off."""
    reg = get_registry()

    def gen():
        ans = answer(req.text, req.patient_flags, req.concurrent_meds, reg,
                     narrate=False, lang=req.lang)
        yield _sse("answer", ans.model_dump())

        if not (NARRATE and ans.substitutes and not ans.escalate):
            yield _sse("end", {})
            return

        sub = ans.substitutes[0]
        q = ans.query
        # tell the client prose is coming, so it can show a 'generating'
        # indicator during the model's (silent) reasoning gap
        yield _sse("narrating", {"i": 0})
        try:
            from badeel.chains import stream_rationale
            from badeel.llm import get_llm
            from badeel.retrieval import get_retriever
            from badeel.schemas import Citation

            evidence = get_retriever().search(
                f"{q.resolved_brand} {sub.ingredient} substitution",
                scope=[sub.ingredient, q.ingredient], k=4)
            # prose may name the substitute, the queried drug, the patient's own
            # concurrent meds (clinically correct to reference), and combo
            # components; anything else is a hallucination and drops the prose.
            permitted = ({sub.ingredient, q.ingredient} | set(q.concurrent_meds)
                         | reg.components(sub.ingredient) | reg.components(q.ingredient))
            forbidden = sorted(set(reg.ing_by_name) - permitted)

            acc = ""
            for chunk in stream_rationale(
                    get_llm(), brand=sub.brand, ingredient=sub.ingredient,
                    queried_brand=q.resolved_brand, tier=sub.tier,
                    flags=sub.counselling_flags, evidence=evidence, lang=req.lang,
                    brand_only=reg.is_combination(sub.ingredient)):
                acc += chunk
                yield _sse("delta", {"i": 0, "text": chunk})

            low = acc.lower()
            leaked = any(d.lower() in low for d in forbidden)
            if not acc.strip() or leaked:
                yield _sse("done", {"i": 0, "rationale": "", "guard_trip": True})
            else:
                cites = [Citation(leaflet=c["leaflet"], section=c["section"],
                                  snippet=c["text"][:190]).model_dump()
                         for c in evidence]
                yield _sse("done", {"i": 0, "rationale": acc.strip(),
                                    "evidence": cites, "guard_trip": False,
                                    "model": os.getenv("LLM_MODEL", "unknown")})
        except Exception:
            yield _sse("done", {"i": 0, "rationale": "", "error": True})
        yield _sse("end", {})

    return StreamingResponse(
        gen(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no",
                 "Connection": "keep-alive"})


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
    # Always the synthetic eval set — it is the graded/labelled set, independent
    # of whichever dataset the pipeline is currently serving.
    lines = config.EVAL_SET.read_text(encoding="utf-8").splitlines()
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
