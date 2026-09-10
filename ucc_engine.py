#!/usr/bin/env python3
"""
Unrecorded-Cessation Class (UCC) scoring engine
Session: 2026-09-10T13:40:00-04:00
Author: Haley Bird / autonomous research agent

Research-stage classification heuristic. NOT a measurement of nature,
NOT a physical discovery, NOT peer review, NOT a patent.

UCC definition
--------------
A cessation (extinction, hypothesis-death, signal-loss, function-loss)
that cannot mint a ledger event because the entity never held a durable
identifier. Loss can be real; a death record is structurally impossible.

This is the remaining surface AFTER fourteen archived classes
(place, converter, named-cause residual, failed verdict, clock,
join, transfer function, consuming capture, patch).

Gates (all must pass for STRUCTURAL_GAP)
----------------------------------------
G1  Entity never had a durable identifier, OR identifier-lag exceeds
    plausible remaining lifetime.
G2  Cessation is physically or institutionally possible in the current window.
G3  No existing ledger can record the cessation as a named event.
G4  Not Undersampling: the unknown is not merely "we have not looked
    at the living"; it is that the dead never existed on paper.
G5  Not CIC: CIC requires two constructible clocks. UCC's loss-clock
    cannot be built because events have no names.
G6  Not DIC: DIC requires a seen object whose identification consumes it.
    UCC's object may never be seen.
G7  Not PPC: PPC requires a residual already inside an operational
    pipeline. UCC entities never entered the pipeline, so they cannot
    generate residuals for a patch to eat.
G8  Not TAC/NCR/FAC/JAC/IOA/CBR/DBH: archive subtraction.

Scores are classification heuristics, not measurements of nature.
Novelty is capped because the biodiversity instance (Katuš shortfall)
was named by Kew on 2026-09-10; the class is the cross-realm
generalization after archive subtraction, not the coining of Katuš.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any
import json
import math
import sys
from datetime import datetime, timezone


ARCHIVED_CLASSES = [
    "Dark Biosphere Hypothesis",
    "Cosmic-Bio Resonance",
    "Undersampling",
    "Deep-biosphere-as-space-prior",
    "Ritual Nyquist Law",
    "Transducer-Absence Class (TAC)",
    "Cadence Mismatch",
    "Named-Cause Residual (NCR)",
    "Failed-Adjudication Class (FAC)",
    "Clock-Incommensurability Class (CIC)",
    "Join-Absence Class (JAC)",
    "Interscale-Operator Absence Class (IOA)",
    "Destructive-Inquiry Class (DIC)",
    "Patch-Proliferation Class (PPC)",
]

ZEROED_CONTROLS = [
    "nodule dark oxygen",
    "universal dark-fraction",
    "wood-wide web Type I",
    "Hubble tension as object",
    "consciousness hard problem",
    "hadal Animalia incerta sedis",
    "dark dimension DE x DM coupling",
    "K2-18b DMS-as-life",
    "magnetoreceptor cell",
    "Cosmic-Bio Resonance",
    "Dark Biosphere",
]

NOVELTY_CAP = 0.47  # Kew named the plant/fungi instance today; class is the remainder
COHERENCE_PRIOR = 0.76


@dataclass
class UCCInstance:
    id: str
    realm: str
    name: str
    sense: str  # vision, hearing, chemical, time, touch, magnetism, proprioception
    source: str
    source_date: str
    known_fact: str
    gap_statement: str
    identifier_absent: bool
    cessation_possible: bool
    ledger_can_record: bool
    prior_class_overlap: str  # empty or class acronym
    industrial_pressure: float  # 0-1
    freshness: float  # 0-1, 1 = locked today
    uniqueness: float  # 0-1, inverse of literature saturation of THIS framing
    notes: str = ""


def _clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def score_ucc_instance(inst: UCCInstance) -> dict[str, Any]:
    """Score one candidate against UCC gates.

    Inputs: UCCInstance
    Outputs: dict with status, score, failed_gates, reasons

    Edge cases:
    - ZEROED controls always return score 0, status ZEROED
    - Any prior_class_overlap in {DIC, PPC, TAC, FAC, CIC, IOA, JAC, NCR,
      UND, CBR, DBH} with identifier present -> KILLED or PENALIZED
    - ledger_can_record True -> fails G3, cannot be STRUCTURAL_GAP
    """
    reasons: list[str] = []
    failed: list[str] = []

    name_l = (inst.name + " " + inst.id).lower()
    for z in ZEROED_CONTROLS:
        if z.lower() in name_l:
            return {
                "id": inst.id,
                "name": inst.name,
                "realm": inst.realm,
                "sense": inst.sense,
                "status": "ZEROED",
                "score": 0.0,
                "failed_gates": ["ZEROED_CONTROL"],
                "reasons": [f"Archive-zeroed control: {z}"],
                "gates": {},
            }

    g1 = bool(inst.identifier_absent)
    g2 = bool(inst.cessation_possible)
    g3 = not bool(inst.ledger_can_record)
    if not g1:
        failed.append("G1"); reasons.append("Entity has or can mint a durable identifier")
    if not g2:
        failed.append("G2"); reasons.append("Cessation not evidenced as currently possible")
    if not g3:
        failed.append("G3"); reasons.append("A ledger can already record this cessation")

    overlap = (inst.prior_class_overlap or "").upper().strip()
    hard_kill = {
        "DIC": "G6",
        "PPC": "G7",
        "TAC": "G8",
        "CBR": "G8",
        "DBH": "G8",
        "CONSCIOUSNESS": "G8",
    }
    penalize = {"CIC": "G5", "UND": "G4", "UNDERSAMPLING": "G4",
                "FAC": "G8", "NCR": "G8", "JAC": "G8", "IOA": "G8",
                "INSTITUTIONAL": "G2"}

    g4 = overlap not in {"UND", "UNDERSAMPLING"}
    g5 = overlap != "CIC"
    g6 = overlap != "DIC"
    g7 = overlap != "PPC"
    g8 = overlap not in {"TAC", "NCR", "FAC", "JAC", "IOA", "CBR", "DBH", "CONSCIOUSNESS"}

    status = "STRUCTURAL_GAP"
    if overlap in hard_kill:
        failed.append(hard_kill[overlap])
        reasons.append(f"Hard archive overlap: {overlap}")
        status = "KILLED"
    elif overlap in penalize:
        failed.append(penalize[overlap])
        reasons.append(f"Soft archive overlap: {overlap} — penalized, not promoted")
        status = "PENALIZED"

    if status == "STRUCTURAL_GAP" and failed:
        status = "PENALIZED"

    # heuristic score: only STRUCTURAL_GAP gets full product
    base = (
        0.28 * inst.freshness
        + 0.22 * inst.uniqueness
        + 0.20 * inst.industrial_pressure
        + 0.15 * (1.0 if g1 else 0.0)
        + 0.15 * (1.0 if g3 else 0.0)
    )
    if status == "STRUCTURAL_GAP":
        score = 100.0 * _clip(base)
    elif status == "PENALIZED":
        score = 100.0 * _clip(base * 0.45)
    elif status == "KILLED":
        score = 0.0
    else:
        score = 0.0

    return {
        "id": inst.id,
        "name": inst.name,
        "realm": inst.realm,
        "sense": inst.sense,
        "status": status,
        "score": round(score, 2),
        "failed_gates": failed,
        "reasons": reasons,
        "source": inst.source,
        "source_date": inst.source_date,
        "known_fact": inst.known_fact,
        "gap_statement": inst.gap_statement,
        "notes": inst.notes,
        "gates": {"G1": g1, "G2": g2, "G3": g3, "G4": g4,
                  "G5": g5, "G6": g6, "G7": g7, "G8": g8},
        "prior_class_overlap": overlap,
    }


def identifier_lag_window(
    collected_year: int,
    named_year: int | None,
    estimated_remaining_lifetime_years: float | None,
    now_year: int = 2026,
) -> dict[str, Any]:
    """Iterate #1 — Identifier-Lag Window (ILW).

    Even a collected specimen can sit in certificate-absence while a
    name is pending. If the lag exceeds remaining lifetime, UCC holds
    for a *collected* entity, which is stricter than the unnamed-living case.

    Inputs
    ------
    collected_year : year the specimen entered a drawer
    named_year : year of formal description, or None if still unnamed
    estimated_remaining_lifetime_years : wild remaining lifetime, or None
    now_year : evaluation year

    Outputs
    -------
    lag_years, still_unnamed, window_exceeds_lifetime, status
    """
    if collected_year > now_year:
        raise ValueError("collected_year cannot be in the future")
    if named_year is not None and named_year < collected_year:
        raise ValueError("named_year precedes collected_year")
    if estimated_remaining_lifetime_years is not None and estimated_remaining_lifetime_years < 0:
        raise ValueError("lifetime cannot be negative")

    end = named_year if named_year is not None else now_year
    lag = end - collected_year
    still_unnamed = named_year is None
    exceeds = (
        estimated_remaining_lifetime_years is not None
        and lag > estimated_remaining_lifetime_years
    )
    if still_unnamed and exceeds:
        status = "UCC_HOLDS_ON_COLLECTED"
    elif still_unnamed:
        status = "OPEN_LAG"
    elif exceeds:
        status = "NAMED_AFTER_PLAUSIBLE_DEATH"
    else:
        status = "NAMED_INSIDE_WINDOW"
    return {
        "collected_year": collected_year,
        "named_year": named_year,
        "lag_years": lag,
        "still_unnamed": still_unnamed,
        "window_exceeds_lifetime": exceeds,
        "status": status,
    }


def witness_retraction_score(
    cancelled_count: int,
    questions_owned: int,
    replacement_funded: bool,
    institutional: bool = True,
) -> dict[str, Any]:
    """Iterate #2 — Witness-Retraction (institutional dual of UCC).

    When the measurement that would have minted an identifier is itself
    cancelled, the unknown dies as a research object without a negative
    result. This is INSTITUTIONAL UCC, not a law of nature. Always
    penalized relative to natural-kind instances.

    Edge cases: cancelled_count < 0 invalid; questions_owned == 0
    means no owned unknown, score 0.
    """
    if cancelled_count < 0 or questions_owned < 0:
        raise ValueError("counts cannot be negative")
    if questions_owned == 0:
        return {"status": "NO_OWNED_UNKNOWN", "score": 0.0, "promoted": False}
    coverage = min(1.0, cancelled_count / max(1, questions_owned))
    raw = 100.0 * coverage * (0.35 if replacement_funded else 0.80)
    # institutional dual is never promoted to winning class
    return {
        "cancelled_count": cancelled_count,
        "questions_owned": questions_owned,
        "replacement_funded": replacement_funded,
        "institutional": institutional,
        "status": "PENALIZED_INSTITUTIONAL_DUAL",
        "score": round(raw * 0.45, 2),
        "promoted": False,
        "note": "NASA-class cancellation can kill a witness; it does not name a natural kind.",
    }


def build_catalog() -> list[UCCInstance]:
    """Sourced instances for 2026-09-10. Freshness 1.0 reserved for today's lock."""
    return [
        UCCInstance(
            id="KATUS_KEW_2026",
            realm="land",
            name="Katuš shortfall — unrecorded plant/fungal extinction",
            sense="vision",
            source="Kew, State of the World's Plants and Fungi 2026",
            source_date="2026-09-10",
            known_fact=(
                "29,748 plant species and 411 fungal species assessed as threatened; "
                "only 18% of plants and 0.6% of fungi have been assessed; "
                ">100,000 plant species and >2 million fungal species remain unnamed; "
                "4,600 plants and 7,800 fungi newly named in 2024–2025; "
                "ghost palm Plectocomiopsis hantu named 92 years after first collection. "
                "Kew names this the Katuš shortfall: unrecorded loss of known AND unknown species."
            ),
            gap_statement=(
                "An unnamed plant or fungus can go extinct without minting a death certificate. "
                "Red List cannot list what has no name. The loss is real; the record is structurally impossible."
            ),
            identifier_absent=True,
            cessation_possible=True,
            ledger_can_record=False,
            prior_class_overlap="",
            industrial_pressure=0.72,
            freshness=1.00,
            uniqueness=0.78,
            notes="TODAY'S LOCK. Kew named the biodiversity instance. Class is the cross-realm remainder.",
        ),
        UCCInstance(
            id="CCZ_UNNAMED",
            realm="ocean",
            name="Clarion-Clipperton Zone unnamed fauna under mining contracts",
            sense="touch",
            source="NHM CCZ checklist; Earth.com 2026-09-09; ISA 17 exploration contracts",
            source_date="2026-09-09",
            known_fact=(
                "5,578 animal species recorded in the CCZ; only 436 formally described; "
                "88–92% lack names; 17 international exploration contracts sit on the same seafloor."
            ),
            gap_statement=(
                "Extraction licensed against organisms that have no Red List identity, "
                "hence no legal death. Census is not a precondition of the license."
            ),
            identifier_absent=True,
            cessation_possible=True,
            ledger_can_record=False,
            prior_class_overlap="",
            industrial_pressure=0.95,
            freshness=0.92,
            uniqueness=0.70,
            notes="Not DIC (the habitat, not a single seen specimen, is consumed). Not CIC (the issue is namelessness, not clock mismatch).",
        ),
        UCCInstance(
            id="GHOST_PALM_LAG",
            realm="land",
            name="Ghost palm 92-year identifier lag",
            sense="time",
            source="Kew 2026 (Plectocomiopsis hantu)",
            source_date="2026-09-10",
            known_fact="Named 92 years after first collection.",
            gap_statement=(
                "A collected specimen can sit unnamed longer than many plant populations persist. "
                "The lag itself is a certificate-absence window."
            ),
            identifier_absent=False,  # it WAS eventually named
            cessation_possible=True,
            ledger_can_record=True,  # now named
            prior_class_overlap="",
            industrial_pressure=0.20,
            freshness=1.00,
            uniqueness=0.65,
            notes="Used as ILW iterate primary, not as winning UCC instance (identifier now exists).",
        ),
        UCCInstance(
            id="ODL_10000_UNSEEN",
            realm="ocean",
            name="99.999% unseen seafloor can lose ecosystems with no before-image",
            sense="vision",
            source="Bell et al. Science Advances 2025-05-07; ODL Global Deep Sea Exploration Goals 2026-04/2026-09-09",
            source_date="2026-09-09",
            known_fact=(
                "Visual coverage of deep seafloor 0.0006–0.001% (max 3,823 km² of 335.7 million km²). "
                "65% of dives within 200 nm of US/Japan/NZ. 10,000 target sites proposed to nearly double unique locations."
            ),
            gap_statement=(
                "A site never imaged cannot generate a before/after extinction record. "
                "The 10,000-site grid is a sampling design, not a census of what can already have ceased."
            ),
            identifier_absent=True,
            cessation_possible=True,
            ledger_can_record=False,
            prior_class_overlap="UND",
            industrial_pressure=0.80,
            freshness=0.90,
            uniqueness=0.40,
            notes="PENALIZE: closest to Undersampling. UCC holds only for the cessation-without-before-image slice, not the unseen-as-unseen.",
        ),
        UCCInstance(
            id="INSECT_450YR",
            realm="animals",
            name="Insect Linnaean clock vs unnamed cessation",
            sense="vision",
            source="npj Biodiversity 2025; ~10,000 insect spp/year vs ~5.5 million estimated",
            source_date="2025",
            known_fact="At ~10,000 newly described insect species per year it would take ~450 years to name an estimated 5.5 million.",
            gap_statement="Most insect cessations in the next century will have no species-level death certificate.",
            identifier_absent=True,
            cessation_possible=True,
            ledger_can_record=False,
            prior_class_overlap="CIC",
            industrial_pressure=0.60,
            freshness=0.35,
            uniqueness=0.45,
            notes="PENALIZE: CIC already owns rate-vs-rate. UCC slice is the nameless deaths, not the two clocks.",
        ),
        UCCInstance(
            id="MIDWATER_GELATA",
            realm="ocean",
            name="Midwater gelatinous fauna destroyed by nets before description",
            sense="touch",
            source="Falkor (too) tropical South Atlantic, April 2026; Osborn/Smithsonian; 31 species in ~2 weeks",
            source_date="2026-07-25",
            known_fact=(
                "Midwater is ~90% of Earth's living space. Nets and preservatives destroy gelatinous bodies. "
                "April 2026 cruise identified 31 species new to science in ~15 days."
            ),
            gap_statement="A body plan that cannot survive collection cannot enter the catalog; its regional cessation is unrecordable.",
            identifier_absent=True,
            cessation_possible=True,
            ledger_can_record=False,
            prior_class_overlap="DIC",
            industrial_pressure=0.40,
            freshness=0.70,
            uniqueness=0.55,
            notes="KILLED as UCC primary: DIC owns seen-object-consumed-by-protocol. Digital-specimen work is the DIC surrogate.",
        ),
        UCCInstance(
            id="SOIL_NEMATODE",
            realm="land",
            name="Soil nematode cessations without species identity",
            sense="chemical",
            source="Van den Hoogen et al. 2019; Grilo/EA 2026; Kuzyakov et al. Soil Biology & Biochemistry Jan 2026",
            source_date="2026-01",
            known_fact=(
                "4.4e20 nematodes in top 15 cm globally. Functions of most soil-relevant prokaryotes remain unknown. "
                "Grand questions in soil biology still include 'which level of understanding of microbial communities do we need?'"
            ),
            gap_statement="Tillage, pesticide, and land-use change can cease unnamed soil taxa without a species-level event.",
            identifier_absent=True,
            cessation_possible=True,
            ledger_can_record=False,
            prior_class_overlap="",
            industrial_pressure=0.85,
            freshness=0.55,
            uniqueness=0.62,
            notes="Allowed UCC. Not wood-wide web (IOA, zeroed as Type I). Function-unknown is the certificate-absence of processes.",
        ),
        UCCInstance(
            id="MICROBIAL_DARK_GENES",
            realm="earth",
            name="Unannotated environmental genes lost before function assignment",
            sense="chemical",
            source="MDM literature; >50% genes neither functionally nor taxonomically annotated at 95% ID (Fondi et al. re-cited)",
            source_date="2024-2026 reviews",
            known_fact="Most environmental genes in metagenomes lack function and taxon assignment; <2% of microbes are cultured.",
            gap_statement="A gene variant can disappear from an environment before anyone knows what it did.",
            identifier_absent=True,
            cessation_possible=True,
            ledger_can_record=False,
            prior_class_overlap="TAC",
            industrial_pressure=0.50,
            freshness=0.30,
            uniqueness=0.40,
            notes="PENALIZE/KILL toward TAC: 'microbial dark matter' is a named-dark signal. UCC only if we refuse the 'dark' label and treat absence of ID as certificate-absence.",
        ),
        UCCInstance(
            id="NASA_41_CANCEL",
            realm="space",
            name="41 NASA science missions cancelled — witness retraction",
            sense="vision",
            source="Planetary Society, 2026-09-09; OMB May 2025 plan, 47% science cut",
            source_date="2026-09-09",
            known_fact="Plan to cancel no fewer than 41 space missions, including some already paid for and launched.",
            gap_statement="Questions those missions owned will never mint a measurement. The unknown dies as a research object without a negative result.",
            identifier_absent=True,
            cessation_possible=True,
            ledger_can_record=False,
            prior_class_overlap="INSTITUTIONAL",
            industrial_pressure=0.88,
            freshness=0.95,
            uniqueness=0.50,
            notes="Institutional dual. Iterate #2. Not a natural kind. PENALIZED, not promoted.",
        ),
        UCCInstance(
            id="WIMP_MAJORITY_DEATH",
            realm="space",
            name="WIMP-as-default ceased as majority without textbook death certificate",
            sense="time",
            source="Afshordi et al. APS Physics 19, 34 (2026-05-12); arXiv:2605.11058; WIMP 10%",
            source_date="2026-05-12",
            known_fact="WIMP chosen by only 10% of surveyed physicists; axion 17%; modified gravity 22%; hybrid 21%. Λ only ~25%.",
            gap_statement="A standard-bearer hypothesis can lose majority without a successor being sworn in, and without textbooks recording a death.",
            identifier_absent=False,
            cessation_possible=True,
            ledger_can_record=True,
            prior_class_overlap="PPC",
            industrial_pressure=0.40,
            freshness=0.60,
            uniqueness=0.25,
            notes="KILLED: PPC owns pipeline-intact after majority loss. Identifier exists (the word WIMP).",
        ),
        UCCInstance(
            id="LYA_DE_SIGNFLIP",
            realm="space",
            name="DESI Lyα full-shape July 2026 pulls evolving-DE residual toward ΛCDM",
            sense="time",
            source="DESI Collaboration / Turner, 2026-07-30; DESI DR2 Lyα full-shape",
            source_date="2026-07-30",
            known_fact=(
                "Full-shape Lyα forest measurements have smaller uncertainty and a central value "
                "that shifts toward ΛCDM relative to BAO-only evolving-DE preference."
            ),
            gap_statement="The residual that licensed DE patches may be withdrawing; papers that patched it are not withdrawn.",
            identifier_absent=False,
            cessation_possible=True,
            ledger_can_record=True,
            prior_class_overlap="PPC",
            industrial_pressure=0.30,
            freshness=0.75,
            uniqueness=0.55,
            notes="KILLED as UCC: this is PPC's next move (orphan patch), not certificate-absence. Logged as adjacent, not reclaimed.",
        ),
        UCCInstance(
            id="MESOPELAGIC_FLUX",
            realm="ocean",
            name="Mesopelagic carbon-export carriers unnamed in a 0.3–40% span",
            sense="chemical",
            source="WHOI twilight-zone expert survey (93 experts, 26 countries); WIRED mesopelagic; NSF PAR",
            source_date="2025-2026",
            known_fact=(
                "62–87% of experts judged understanding of fishing/climate/mining/pollution impacts as limited. "
                "Mesopelagic contribution to biological carbon pump estimated anywhere from 0.3% to 40%."
            ),
            gap_statement=(
                "A planetary flux sits in climate arithmetic; the fish that carry it are mostly unnamed and uncounted. "
                "A fishery decision cannot generate a species-level mortality ledger."
            ),
            identifier_absent=True,
            cessation_possible=True,
            ledger_can_record=False,
            prior_class_overlap="IOA",
            industrial_pressure=0.78,
            freshness=0.50,
            uniqueness=0.58,
            notes="PENALIZE: IOA owns two-scale carbon pump without a transfer function. UCC slice is nameless carriers, not missing operator.",
        ),
        UCCInstance(
            id="HADAL_INCERTA",
            realm="ocean",
            name="Hadal Animalia incerta sedis",
            sense="vision",
            source="Jamieson et al. 2026 (DIC primary 2026-09-06)",
            source_date="2026-09-06",
            known_fact="Filmed twice to 9,137 m; cannot be assigned to a known phylum; collection without pressure-retaining sampler ruins evidence.",
            gap_statement="n/a — DIC owns this.",
            identifier_absent=True,
            cessation_possible=True,
            ledger_can_record=False,
            prior_class_overlap="DIC",
            industrial_pressure=0.20,
            freshness=0.20,
            uniqueness=0.20,
            notes="KILLED. DIC primary. Do not reclaim.",
        ),
        UCCInstance(
            id="DARK_OXYGEN",
            realm="ocean",
            name="Nodule dark oxygen",
            sense="chemical",
            source="Sweetman et al. 2024; Nature Geoscience Editor's Note 2026-04-08; F1000 2026-05; Frontiers 2025",
            source_date="2026-04-08",
            known_fact="Editor's note 8 Apr 2026; unreplicated; re-analysis finds O2 rise independent of nodule presence.",
            gap_statement="n/a — ZEROED.",
            identifier_absent=False,
            cessation_possible=False,
            ledger_can_record=True,
            prior_class_overlap="FAC",
            industrial_pressure=0.90,
            freshness=0.40,
            uniqueness=0.10,
            notes="ZEROED control.",
        ),
        UCCInstance(
            id="H0_TENSION",
            realm="space",
            name="Hubble tension",
            sense="time",
            source="H0DN 73.50±0.81; Planck+SPT+ACT 67.24±0.35; ~7σ",
            source_date="2026-04",
            known_fact="Local Distance Network H0 = 73.50 ± 0.81 km s−1 Mpc−1; CMB 67.24 ± 0.35; >6–7σ.",
            gap_statement="n/a — FAC owns the tension.",
            identifier_absent=False,
            cessation_possible=False,
            ledger_can_record=True,
            prior_class_overlap="FAC",
            industrial_pressure=0.20,
            freshness=0.50,
            uniqueness=0.10,
            notes="KILLED/RETAIN FAC. Identifier exists (H0).",
        ),
        UCCInstance(
            id="LANGUAGE_DEATH",
            realm="humans",
            name="Last-speaker ecological knowledge cessation",
            sense="hearing",
            source="UNESCO language endangerment; ethnobiology last-speaker literature (general, not a 2026 lock)",
            source_date="ongoing",
            known_fact="When a last speaker dies, unnamed organism-knowledge (local taxa, uses, seasonal clocks) dies with them.",
            gap_statement="A folk taxon with no Linnaean mapping cannot generate a scientific extinction or knowledge-loss certificate.",
            identifier_absent=True,
            cessation_possible=True,
            ledger_can_record=False,
            prior_class_overlap="",
            industrial_pressure=0.55,
            freshness=0.25,
            uniqueness=0.60,
            notes="Allowed but not primary: not today's lock, literature-old, still a clean UCC instance in the human realm.",
        ),
        UCCInstance(
            id="DEEP_BIOSPHERE_INTERVALS",
            realm="earth",
            name="Deep-biosphere low- or no-cell intervals",
            sense="touch",
            source="Deep biosphere reviews; Wikipedia Deep biosphere 2026-09-06 citing unknown reasons for no-cell intervals",
            source_date="2026-09-06",
            known_fact=(
                "Deep biosphere ~2–2.3 billion km³, carbon 15–23 billion tonnes. "
                "Low- or no-cell intervals exist; reasons unknown. Absolute limits of life not found."
            ),
            gap_statement="A subsurface community that ceased leaves no fossil certificate at those depths; the interval is an absence, not a death record.",
            identifier_absent=True,
            cessation_possible=True,
            ledger_can_record=False,
            prior_class_overlap="DBH",
            industrial_pressure=0.15,
            freshness=0.20,
            uniqueness=0.35,
            notes="KILLED: Dark Biosphere Hypothesis overlap. Do not reclaim.",
        ),
        UCCInstance(
            id="CONSCIOUSNESS",
            realm="humans",
            name="Hard problem of consciousness",
            sense="proprioception",
            source="archive refused",
            source_date="n/a",
            known_fact="Archive-refused across sessions.",
            gap_statement="n/a",
            identifier_absent=False,
            cessation_possible=False,
            ledger_can_record=True,
            prior_class_overlap="CONSCIOUSNESS",
            industrial_pressure=0.0,
            freshness=0.0,
            uniqueness=0.0,
            notes="KILLED. Archive-refused. Not a back door.",
        ),
        UCCInstance(
            id="FUNGAL_HYPHAE_FUNCTION",
            realm="land",
            name="110 quadrillion km fungal filaments — function claims exceed evidence",
            sense="chemical",
            source="The Conversation 2026-06-12; global mycorrhizal mapping; 3.12 Gt CO2e/year into soil",
            source_date="2026-06-12",
            known_fact=(
                "Topsoils contain ~110 quadrillion km of living fungal filaments; AM fungi channel "
                "an estimated 3.12 billion tonnes CO2e/year into soil. Wood-wide-web active-sharing claims exceed evidence."
            ),
            gap_statement="A mapped length is not a named function. Cessation of a functional guild has no certificate if the guild was never functionally identified.",
            identifier_absent=False,
            cessation_possible=True,
            ledger_can_record=False,
            prior_class_overlap="IOA",
            industrial_pressure=0.70,
            freshness=0.55,
            uniqueness=0.40,
            notes="PENALIZE: IOA / wood-wide-web Type I retain. Length is an identifier of a kind; function is the missing operator.",
        ),
        UCCInstance(
            id="DARK_DIMENSION",
            realm="space",
            name="Dark-dimension coupling of DE × DM",
            sense="time",
            source="PPC primary 2026-09-08",
            source_date="2026-09-08",
            known_fact="PPC primary. Extra unobservable DOF coupling two TAC objects.",
            gap_statement="n/a — PPC owns this.",
            identifier_absent=False,
            cessation_possible=False,
            ledger_can_record=True,
            prior_class_overlap="PPC",
            industrial_pressure=0.20,
            freshness=0.80,
            uniqueness=0.20,
            notes="KILLED. Yesterday's primary.",
        ),
    ]


def run_engine() -> dict[str, Any]:
    catalog = build_catalog()
    scored = [score_ucc_instance(i) for i in catalog]
    scored.sort(key=lambda r: (-r["score"], r["name"]))

    by_status: dict[str, int] = {}
    for r in scored:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1

    gaps = [r for r in scored if r["status"] == "STRUCTURAL_GAP"]
    primary = gaps[0] if gaps else None

    # Iterate 1: Identifier-Lag Window on ghost palm + hypothetical unnamed
    ilw = [
        identifier_lag_window(1933, 2025, estimated_remaining_lifetime_years=80),  # ghost palm
        identifier_lag_window(2010, None, estimated_remaining_lifetime_years=12),  # hypothetical collected unnamed
        identifier_lag_window(2020, None, estimated_remaining_lifetime_years=40),
    ]

    # Iterate 2: Witness-retraction on NASA 41
    wr = witness_retraction_score(
        cancelled_count=41,
        questions_owned=41,
        replacement_funded=False,
    )

    winning = "Unrecorded-Cessation Class" if primary else "NONE"
    novelty = NOVELTY_CAP if primary else 0.0
    coherence = COHERENCE_PRIOR if primary else 0.0

    return {
        "session_id": "2026-09-10-ucc-unrecorded-cessation",
        "timestamp": "2026-09-10T13:40:00-04:00",
        "winning_class": winning,
        "novelty_cap": novelty,
        "coherence": coherence,
        "primary": primary,
        "status_counts": by_status,
        "ranked": scored,
        "iterate_ilw": ilw,
        "iterate_witness_retraction": wr,
        "archived_classes_subtracted": ARCHIVED_CLASSES,
        "zeroed_controls": ZEROED_CONTROLS,
        "claim_hygiene": (
            "Research-stage classification. Not a physical discovery, not peer review, "
            "not a patent. Scores are a classification heuristic, not measurements of nature. "
            "Kew named the Katuš shortfall for plants/fungi; this session does not claim that coinage. "
            "The class is the cross-realm remainder after fourteen archived classes."
        ),
    }


def render_text(result: dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 72)
    lines.append(f"WINNING CLASS: {result['winning_class']}")
    lines.append(f"novelty_cap {result['novelty_cap']} | coherence {result['coherence']}")
    sc = result["status_counts"]
    lines.append(
        f"STRUCTURAL_GAP {sc.get('STRUCTURAL_GAP', 0)} | "
        f"PENALIZED {sc.get('PENALIZED', 0)} | "
        f"KILLED {sc.get('KILLED', 0)} | "
        f"ZEROED {sc.get('ZEROED', 0)}"
    )
    if result["primary"]:
        p = result["primary"]
        lines.append(f"primary {p['id']} {p['score']}")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"{'score':>7}  {'status':<16}  {'realm':<8}  name")
    lines.append("-" * 72)
    for r in result["ranked"]:
        lines.append(f"{r['score']:7.2f}  {r['status']:<16}  {r['realm']:<8}  {r['name']}")
    lines.append("")
    lines.append("ITERATE 1 — Identifier-Lag Window")
    for w in result["iterate_ilw"]:
        lines.append(
            f"  collected {w['collected_year']} named {w['named_year']} "
            f"lag={w['lag_years']}y  {w['status']}"
        )
    lines.append("")
    lines.append("ITERATE 2 — Witness-Retraction (institutional dual, not promoted)")
    wr = result["iterate_witness_retraction"]
    lines.append(f"  {wr}")
    lines.append("")
    lines.append(result["claim_hygiene"])
    return "\n".join(lines)


def main() -> int:
    result = run_engine()
    text = render_text(result)
    print(text)
    out_json = "/workspace/artifacts/ucc_2026_09_10/ucc_engine_output.json"
    out_txt = "/workspace/artifacts/ucc_2026_09_10/ucc_engine_output.txt"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(f"\nWrote {out_json}")
    print(f"Wrote {out_txt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
