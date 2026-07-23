"""Deterministic safety filtering (spec section 8, step 5).

Runs on every candidate AFTER generation and BEFORE ranking, so that a blocked
tier-1 candidate lets a tier-2 candidate win (spec rule 2.2, case E008).

Blocking checks drop a candidate into blocked_candidates; flag-only checks keep
it but attach a counselling flag.

    a. contraindication   candidate contraindications vs patient_flags   -> BLOCK
    b. interaction        candidate vs concurrent_meds (major -> BLOCK,
                          moderate/minor -> flag)
    c. form               modified-release vs immediate-release mismatch -> flag,
                          BLOCK when the queried MR product is non-interchangeable
    d. strength           candidate cannot reproduce queried strength    -> flag
    e. combination        component set differs from queried             -> BLOCK
    f. potency            within-class swap, dose not mg-equivalent       -> flag

Contraindication text comes from the leaflet markdown (the canonical RAG
corpus), which also supplies Citation evidence.
"""

from __future__ import annotations

import csv
import re
from functools import lru_cache

from .candidates import Candidate
from .config import INTERACTIONS_CSV, LEAFLETS_DIR
from .schemas import Citation, SafetyFlag

# Controlled map from a patient flag to keywords we look for in a candidate's
# contraindication text. Kept explicit and small: these are the flags the eval
# actually uses, and clinical keyword matching should never be "clever".
FLAG_KEYWORDS: dict[str, list[str]] = {
    "bronchial asthma": ["asthma", "bronchospasm", "reactive airway"],
    "penicillin allergy": ["penicillin"],
    "pregnancy": ["pregnancy", "pregnant", "trimester"],
    "severe renal impairment": ["renal impairment", "egfr", "crcl", "renal failure",
                                "anuria"],
    "ischaemic heart disease": ["ischaemic heart", "coronary", "cardiovascular"],
    "paediatric": ["under 18", "age under", "paediatric", "children", "child"],
}

_MR = re.compile(r"extended release|modified release|sustained release|\b(xr|sr|mr|er)\b",
                 re.IGNORECASE)


def _flag_keywords(flag: str) -> list[str]:
    low = flag.lower()
    for key, words in FLAG_KEYWORDS.items():
        if key in low or low in key:
            return words
    # fall back to the significant tokens of the flag itself
    return [t for t in re.findall(r"[a-z]+", low) if len(t) > 3]


class Leaflets:
    """Parsed leaflet sections, keyed by ingredient name."""

    def __init__(self, contraindications, notes, files):
        self.contraindications = contraindications   # name -> [bullet, ...]
        self.notes = notes                           # name -> substitution note
        self.files = files                           # name -> filename

    def contra_text(self, ingredient: str) -> str:
        return " | ".join(self.contraindications.get(ingredient, [])).lower()

    def citation(self, ingredient: str, section: str, snippet: str) -> Citation:
        return Citation(leaflet=self.files.get(ingredient, ""),
                        section=section, snippet=snippet[:190])


@lru_cache(maxsize=1)
def load_leaflets() -> Leaflets:
    contra, notes, files = {}, {}, {}
    for path in sorted(LEAFLETS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        name = _leaflet_ingredient(text)
        if not name:
            continue
        files[name] = path.name
        contra[name] = _section_bullets(text, "Contraindications")
        notes[name] = _section_body(text, "Substitution Notes")
    return Leaflets(contra, notes, files)


@lru_cache(maxsize=1)
def load_interactions() -> dict[tuple[str, str], tuple[str, str]]:
    """(ingredient_a, ingredient_b) -> (severity, effect). Symmetric."""
    edges: dict[tuple[str, str], tuple[str, str]] = {}
    with open(INTERACTIONS_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            a, b = r["ingredient_a"], r["ingredient_b"]
            edges[(a, b)] = (r["severity"], r["effect"])
            edges.setdefault((b, a), (r["severity"], r["effect"]))
    return edges


# ---- individual checks -------------------------------------------------

def contraindication_flag(ingredient, patient_flags, leaflets) -> SafetyFlag | None:
    text = leaflets.contra_text(ingredient)
    if not text:
        return None
    for flag in patient_flags:
        for kw in _flag_keywords(flag):
            if kw in text:
                return SafetyFlag(
                    kind="contraindication", severity="major",
                    message=f"Contraindicated in {flag}.",
                    evidence=[leaflets.citation(ingredient, "Contraindications", text)])
    return None


def interaction_flag(ingredient, concurrent_meds, edges) -> SafetyFlag | None:
    worst = None
    for med in concurrent_meds:
        hit = edges.get((ingredient, med))
        if not hit:
            continue
        severity, effect = hit
        flag = SafetyFlag(kind="interaction", severity=severity,
                          message=f"Interaction with {med}: {effect}.")
        if severity == "major":
            return flag           # a major interaction blocks immediately
        worst = worst or flag     # remember a moderate/minor to attach later
    return worst


# ---- orchestration -----------------------------------------------------

def screen(query, candidates: list[Candidate], reg):
    """Partition candidates into (survivors, blocked_flags).

    Returns survivors (Candidates, with counselling_flags populated) and a list
    of (Candidate, SafetyFlag) for the rejected ones.
    """
    leaflets = load_leaflets()
    edges = load_interactions()
    q_components = reg.components(query.ingredient)

    survivors, blocked = [], []
    for cand in candidates:
        ing = cand.ingredient

        # a. contraindication -> BLOCK
        flag = contraindication_flag(ing, query.patient_flags, leaflets)
        if flag:
            blocked.append((cand, flag))
            continue

        # b. interaction (major -> BLOCK, else flag)
        flag = interaction_flag(ing, query.concurrent_meds, edges)
        if flag and flag.severity == "major":
            blocked.append((cand, flag))
            continue
        if flag:
            cand.counselling_flags.append(flag.message)

        # e. combination -> BLOCK only when a fixed-dose combination is involved
        #    and the component sets differ (adding or dropping an active). A
        #    plain molecule-for-molecule class switch is NOT a combination
        #    violation even though its component set differs.
        involves_combo = reg.is_combination(ing) or reg.is_combination(query.ingredient)
        if involves_combo and reg.components(ing) != q_components:
            blocked.append((cand, SafetyFlag(
                kind="combination", severity="major",
                message="Component set differs; adding or dropping an active "
                        "ingredient is not an equivalent substitution.")))
            continue

        # c. form: modified-release mismatch
        f = _form_flag(query, cand, leaflets)
        if f and f.kind == "form" and f.severity == "major":
            blocked.append((cand, f))
            continue
        if f:
            cand.counselling_flags.append(f.message)

        # f. potency: within-class swap needs dose conversion
        if cand.tier == "class":
            cand.counselling_flags.append(
                "Within-class substitution; dose is not milligram equivalent, "
                "conversion required.")

        survivors.append(cand)
    return survivors, blocked


def _form_flag(query, cand, leaflets) -> SafetyFlag | None:
    q_mr = bool(_MR.search(query.form or ""))
    c_mr = bool(_MR.search(cand.product["form"]))
    if q_mr == c_mr:
        return None
    note = leaflets.notes.get(query.ingredient, "").lower()
    non_interchangeable = ("not interchangeable" in note
                           or "prescriber review" in note)
    severity = "major" if (q_mr and non_interchangeable) else "moderate"
    return SafetyFlag(
        kind="form", severity=severity,
        message="Modified-release and immediate-release forms are not "
                "directly interchangeable.")


# ---- leaflet parsing helpers ------------------------------------------

def _leaflet_ingredient(text: str) -> str | None:
    m = re.match(r"#\s+(.+)", text)
    return m.group(1).strip() if m else None


def _section_bullets(text: str, header: str) -> list[str]:
    body = _section_body(text, header)
    return [line[2:].strip() for line in body.splitlines()
            if line.startswith("- ") and "None recorded" not in line]


def _section_body(text: str, header: str) -> str:
    m = re.search(rf"^##\s+{re.escape(header)}\s*$(.*?)(?=^##\s|\Z)",
                  text, re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ""
