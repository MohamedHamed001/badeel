"""Phase 3 gate: all §7 routes wired to the pipeline, 30 cases answerable.

A refusal or escalation is a 200 response, never 4xx.
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from badeel.config import DATA
from main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# ---- health & registry -------------------------------------------------

def test_health_reports_provider_and_doc_count(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["provider"]                       # non-empty
    assert body["model"]
    assert isinstance(body["chroma_docs"], int) and body["chroma_docs"] > 0


def test_products_returns_all_64_skus(client):
    r = client.get("/api/registry/products")
    assert r.status_code == 200
    products = r.json()
    assert len(products) == 64
    assert {"sku", "brand", "brand_ar", "ingredient", "strength", "form",
            "status", "price_egp"} <= products[0].keys()


def test_options_are_derived_from_data(client):
    body = client.get("/api/registry/options").json()
    assert "bronchial asthma" in body["patient_flags"]
    assert len(body["ingredients"]) == 26


def test_eval_cases_returns_all_30(client):
    r = client.get("/api/eval/cases")
    assert r.status_code == 200
    assert len(r.json()) == 30


def test_eval_results_is_safe_when_absent(client):
    # Endpoint must not error even if no report has been generated yet.
    assert client.get("/api/eval/results").status_code == 200


# ---- substitute --------------------------------------------------------

def test_substitute_nti_escalates(client):
    r = client.post("/api/substitute", json={"text": "Coagulex 5 mg is short"})
    assert r.status_code == 200
    body = r.json()
    assert body["tier"] == "none"
    assert body["escalate"] is True
    assert body["substitutes"] == []


def test_substitute_returns_a_grounded_answer(client):
    r = client.post("/api/substitute", json={"text": "Atorex 20 mg is out of stock"})
    assert r.status_code == 200
    body = r.json()
    assert body["escalate"] is False
    assert body["substitutes"], "expected at least one substitute"
    assert body["substitutes"][0]["ingredient"] == "Atorvastin"


def test_escalation_is_200_not_error(client):
    # Unknown drug is refused — still a successful response.
    r = client.post("/api/substitute",
                    json={"text": "Do you have an alternative for Zeroxan?"})
    assert r.status_code == 200
    assert r.json()["escalate"] is True


def test_request_flags_override(client):
    r = client.post("/api/substitute", json={
        "text": "Cardex 10 mg is short",
        "patient_flags": ["bronchial asthma"]})
    assert r.status_code == 200
    # beta-blocker in asthma -> nothing safe -> escalate
    assert r.json()["escalate"] is True


def test_malformed_body_returns_422(client):
    r = client.post("/api/substitute", json={"patient_flags": []})  # no text
    assert r.status_code == 422


def test_all_30_cases_answerable(client):
    cases = [json.loads(l) for l in
             (DATA / "eval_set.jsonl").read_text(encoding="utf-8").splitlines()
             if l.strip()]
    for c in cases:
        r = client.post("/api/substitute", json={
            "text": c["query_en"],
            "patient_flags": c["patient_flags"],
            "concurrent_meds": c["concurrent_meds"]})
        assert r.status_code == 200, c["id"]
        body = r.json()
        assert isinstance(body["escalate"], bool)
        assert body["tier"] in {"generic", "class", "therapeutic", "none"}
