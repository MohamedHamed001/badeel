"""All Pydantic models. Shared by the pipeline and the API layer.

Field names are a contract: the eval harness and the frontend both depend on
them. Mirrored in frontend/src/types.ts. Verbatim from BUILD_SPEC.md section 6.
"""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

Tier = Literal["generic", "class", "therapeutic", "none"]
Severity = Literal["minor", "moderate", "major"]


class SubstituteRequest(BaseModel):
    """Body of POST /api/substitute. patient_flags and concurrent_meds, when
    given, override anything the pipeline would infer from `text`."""
    text: str
    patient_flags: list[str] = Field(default_factory=list)
    concurrent_meds: list[str] = Field(default_factory=list)


class DrugQuery(BaseModel):
    raw_text: str
    resolved_brand: str | None = None
    ingredient: str | None = None
    strength: str | None = None
    form: str | None = None
    patient_flags: list[str] = Field(default_factory=list)
    concurrent_meds: list[str] = Field(default_factory=list)
    resolution_score: float = 0.0
    unresolved: bool = False


class Citation(BaseModel):
    leaflet: str          # filename, e.g. "carvedanol.md"
    section: str          # e.g. "Contraindications"
    snippet: str          # under 200 chars


class SafetyFlag(BaseModel):
    kind: Literal["contraindication", "interaction", "form", "strength",
                  "combination", "nti", "potency", "class_block"]
    severity: Severity
    message: str
    evidence: list[Citation] = Field(default_factory=list)


class BlockedCandidate(BaseModel):
    """A candidate that was generated then rejected. Surfaced in the UI."""
    ingredient: str
    brand: str | None = None
    tier: Tier
    reason: str
    flag: SafetyFlag


class Substitute(BaseModel):
    brand: str
    ingredient: str
    strength: str
    form: str
    tier: Tier
    price_egp: float
    price_delta_pct: float
    rationale: str
    counselling_flags: list[str] = Field(default_factory=list)
    evidence: list[Citation] = Field(default_factory=list)


class TierStat(BaseModel):
    """Per-tier candidate accounting, for the frontend tier rail. Additive to
    section 6: it carries no decision, only makes the algorithm visible."""
    tier: Tier
    generated: int
    survived: int
    blocked_reason: str | None = None


class TraceStep(BaseModel):
    """One step of the deterministic algorithm, for the audit trail. Additive:
    a human-readable replay of what the pipeline already did."""
    step: int
    name: str
    status: Literal["ok", "escalate", "block", "info", "skip"]
    detail: str
    items: list[str] = Field(default_factory=list)


class SubstitutionAnswer(BaseModel):
    query: DrugQuery
    tier: Tier
    escalate: bool
    escalation_reason: str | None = None
    substitutes: list[Substitute] = Field(default_factory=list)
    safety_flags: list[SafetyFlag] = Field(default_factory=list)
    blocked_candidates: list[BlockedCandidate] = Field(default_factory=list)
    tier_summary: list[TierStat] = Field(default_factory=list)
    trace: list[TraceStep] = Field(default_factory=list)
    confidence: float = 0.0
    guard_trips: int = 0
    latency_ms: int = 0
    model_used: str = ""

    @model_validator(mode="after")
    def escalation_implies_no_substitutes(self):
        if self.escalate and self.substitutes:
            raise ValueError("escalate=True must not be accompanied by substitutes")
        if self.tier == "none" and self.substitutes:
            raise ValueError('tier="none" must not be accompanied by substitutes')
        return self
