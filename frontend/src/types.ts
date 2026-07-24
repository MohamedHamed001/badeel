// Hand-mirrored from backend/badeel/schemas.py. Keep field names in sync.

export type Tier = "generic" | "class" | "therapeutic" | "none";
export type Severity = "minor" | "moderate" | "major";

export interface Suggestion {
  brand: string;
  ingredient: string;
  score: number;
}

export interface DrugQuery {
  raw_text: string;
  resolved_brand: string | null;
  ingredient: string | null;
  strength: string | null;
  form: string | null;
  patient_flags: string[];
  concurrent_meds: string[];
  resolution_score: number;
  unresolved: boolean;
  suggestions: Suggestion[];
}

export interface Citation {
  leaflet: string;
  section: string;
  snippet: string;
}

export interface SafetyFlag {
  kind:
    | "contraindication"
    | "interaction"
    | "form"
    | "strength"
    | "combination"
    | "nti"
    | "potency"
    | "class_block";
  severity: Severity;
  message: string;
  evidence: Citation[];
}

export interface BlockedCandidate {
  ingredient: string;
  brand: string | null;
  tier: Tier;
  reason: string;
  flag: SafetyFlag;
}

export interface Substitute {
  brand: string;
  ingredient: string;
  strength: string;
  form: string;
  tier: Tier;
  price_egp: number;
  price_delta_pct: number;
  rationale: string;
  counselling_flags: string[];
  evidence: Citation[];
}

export interface TierStat {
  tier: Tier;
  generated: number;
  survived: number;
  blocked_reason: string | null;
}

export interface TraceStep {
  step: number;
  name: string;
  status: "ok" | "escalate" | "block" | "info" | "skip";
  detail: string;
  items: string[];
}

export interface Comprehension {
  intent: "substitution" | "not_a_shortage" | "unclear";
  drug: string | null;
  flags: string[];
  meds: string[];
}

export interface SubstitutionAnswer {
  query: DrugQuery;
  tier: Tier;
  escalate: boolean;
  escalation_reason: string | null;
  substitutes: Substitute[];
  safety_flags: SafetyFlag[];
  blocked_candidates: BlockedCandidate[];
  tier_summary: TierStat[];
  trace: TraceStep[];
  comprehension: Comprehension | null;
  confidence: number;
  guard_trips: number;
  latency_ms: number;
  model_used: string;
}

export interface RegistryOptions {
  patient_flags: string[];
  ingredients: string[];
}

export interface EvalCase {
  id: string;
  trap: string;
  query_ar: string;
  query_en: string;
  patient_flags: string[];
  concurrent_meds: string[];
  expected_tier: Tier;
  must_escalate: boolean;
  acceptable: string[];
  forbidden: string[];
  must_flag: string[];
  note: string;
}

export interface Health {
  status: string;
  provider: string;
  model: string;
  chroma_docs: number;
  narration: string;
  dataset: string;
}
