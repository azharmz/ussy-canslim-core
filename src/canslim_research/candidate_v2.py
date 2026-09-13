from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

PATTERN_SCHEMA_VERSION = "oneil-pattern-output-v2"
CANDIDATE_SPEC_VERSION = "theory-faithful-candidate-spec-v1"
CANDIDATE_GENERATOR_VERSION = "34-candidate-generator-v0.1"

CORE_PATTERNS = frozenset({
    "FLAT_BASE",
    "DOUBLE_BOTTOM",
    "CUP_WITHOUT_HANDLE",
    "CUP_WITH_HANDLE",
})
PATTERN_STATUSES = frozenset({"RECOGNIZED", "AMBIGUOUS", "REJECTED"})


@dataclass(frozen=True, slots=True)
class PatternAssessment:
    assessment_id: str
    output_schema_version: str
    engine_version: str
    labelled_validation_status: str
    security_id: str
    ticker: str
    asof_date: str
    candidate_id: str
    base_id: str
    lineage_id: str
    pattern: str
    normalized_status: str
    native_state: str
    candidate_semantics: str
    structural_signature: tuple[str, ...]
    structural_start: str
    structural_end: str | None
    pivot_source_date: str | None
    pivot_level: float | None
    depth_pct: float | None
    detector_faults: tuple[str, ...]
    detector_contract_version: str

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> "PatternAssessment":
        schema = str(row.get("output_schema_version", ""))
        if schema != PATTERN_SCHEMA_VERSION:
            raise ValueError(f"unsupported pattern schema: {schema!r}")
        pattern = str(row.get("pattern", ""))
        if pattern not in CORE_PATTERNS:
            raise ValueError(f"pattern outside frozen #33 core contract: {pattern!r}")
        status = str(row.get("normalized_status", ""))
        if status not in PATTERN_STATUSES:
            raise ValueError(f"unsupported normalized_status: {status!r}")
        return cls(
            assessment_id=str(row["assessment_id"]),
            output_schema_version=schema,
            engine_version=str(row["engine_version"]),
            labelled_validation_status=str(row["labelled_validation_status"]),
            security_id=str(row["security_id"]),
            ticker=str(row["ticker"]),
            asof_date=str(row["asof_date"]),
            candidate_id=str(row["candidate_id"]),
            base_id=str(row["base_id"]),
            lineage_id=str(row["lineage_id"]),
            pattern=pattern,
            normalized_status=status,
            native_state=str(row["native_state"]),
            candidate_semantics=str(row["candidate_semantics"]),
            structural_signature=tuple(str(x) for x in row.get("structural_signature", ())),
            structural_start=str(row["structural_start"]),
            structural_end=str(row["structural_end"]) if row.get("structural_end") is not None else None,
            pivot_source_date=str(row["pivot_source_date"]) if row.get("pivot_source_date") is not None else None,
            pivot_level=float(row["pivot_level"]) if row.get("pivot_level") is not None else None,
            depth_pct=float(row["depth_pct"]) if row.get("depth_pct") is not None else None,
            detector_faults=tuple(str(x) for x in row.get("detector_faults", ())),
            detector_contract_version=str(row["detector_contract_version"]),
        )


@dataclass(frozen=True, slots=True)
class DailyBar:
    session_date: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True, slots=True)
class CandidateEvidence:
    C_screen_state: str
    A_screen_state: str
    L_individual_leadership_state: str
    M_entry_state: str
    N_price_state: str = "NOT_EVALUABLE"
    N_catalyst_state: str = "NOT_IMPLEMENTED"
    S_evidence_state: str = "NOT_EVALUABLE"
    I_evidence_state: str = "NOT_EVALUABLE"
    industry_evidence_state: str = "NOT_IMPLEMENTED"


@dataclass(frozen=True, slots=True)
class CandidateRecord:
    assessment_id: str
    candidate_id: str
    base_id: str
    lineage_id: str
    security_id: str
    ticker: str
    asof_date: str
    pattern: str
    pattern_status: str
    native_detector_state: str
    candidate_semantics: str
    detector_faults: tuple[str, ...]
    pattern_engine_version: str
    pattern_contract_version: str
    pivot_level: float | None
    pivot_source_date: str | None
    pivot_crossed_intraday: bool
    open_above_pivot: bool
    gap_through_pivot: bool
    close_above_pivot: bool
    extension_from_pivot_pct: float | None
    within_traditional_buy_zone: bool
    volume_avg_50_prior: float | None
    volume_ratio: float | None
    volume_confirmation_state: str
    candidate_stage: str
    eligibility_reason_codes: tuple[str, ...]
    C_screen_state: str
    A_screen_state: str
    L_individual_leadership_state: str
    M_entry_state: str
    N_price_state: str
    N_catalyst_state: str
    S_evidence_state: str
    I_evidence_state: str
    industry_evidence_state: str
    spec_version: str = CANDIDATE_SPEC_VERSION
    candidate_generator_version: str = CANDIDATE_GENERATOR_VERSION


def _prior_50_volume(bars: Sequence[DailyBar], asof_date: str) -> float | None:
    prior = [bar.volume for bar in bars if bar.session_date < asof_date]
    if len(prior) < 50:
        return None
    return sum(prior[-50:]) / 50.0


def _bar_on(bars: Sequence[DailyBar], asof_date: str) -> DailyBar | None:
    matches = [bar for bar in bars if bar.session_date == asof_date]
    if len(matches) > 1:
        raise ValueError(f"duplicate OHLCV bar for {asof_date}")
    return matches[0] if matches else None


def build_candidate(
    pattern: PatternAssessment,
    bars: Sequence[DailyBar],
    evidence: CandidateEvidence,
) -> CandidateRecord:
    """Consume frozen #33 output; never infer or mutate morphology downstream."""
    reasons: list[str] = []
    recognized = pattern.normalized_status == "RECOGNIZED"
    ambiguous = pattern.normalized_status == "AMBIGUOUS"
    pivot_defined = recognized and pattern.pivot_level is not None

    bar = _bar_on(bars, pattern.asof_date)
    pivot_crossed = False
    open_above = False
    gap_through = False
    close_above = False
    extension = None
    within_zone = False
    avg50 = None
    volume_ratio = None
    volume_state = "NOT_EVALUABLE"

    if ambiguous:
        reasons.append("PATTERN_AMBIGUOUS")
    elif pattern.normalized_status == "REJECTED":
        reasons.append("PATTERN_REJECTED")

    if recognized and pattern.pivot_level is None:
        reasons.append("PIVOT_NOT_DEFINED")

    if pivot_defined and bar is not None:
        pivot = float(pattern.pivot_level)
        pivot_crossed = bar.high > pivot
        open_above = bar.open > pivot
        gap_through = bar.open > pivot and bar.low > pivot
        close_above = bar.close > pivot
        extension = ((bar.close / pivot) - 1.0) * 100.0
        within_zone = 0.0 <= extension <= 5.0
        avg50 = _prior_50_volume(bars, pattern.asof_date)
        if pivot_crossed and avg50 is not None and avg50 > 0:
            volume_ratio = bar.volume / avg50
            volume_state = "CONFIRMED_ON_BREAKOUT" if volume_ratio >= 1.40 else "PENDING_CONFIRMATION"
        elif pivot_crossed:
            volume_state = "NOT_EVALUABLE"
    elif pivot_defined:
        reasons.append("BREAKOUT_BAR_NOT_EVALUABLE")

    if not recognized:
        stage = "NOT_ELIGIBLE"
    elif not pivot_defined:
        stage = "BASE_RECOGNIZED"
    elif not pivot_crossed:
        stage = "PIVOT_DEFINED"
    elif volume_state != "CONFIRMED_ON_BREAKOUT":
        stage = "PIVOT_CROSSED"
    else:
        hard_states = {
            "C": evidence.C_screen_state == "PASS",
            "A": evidence.A_screen_state == "PASS",
            "L": evidence.L_individual_leadership_state in {"PASS", "STRONG"},
            "M": evidence.M_entry_state == "ALLOW_NEW_BUYS",
        }
        for key, passed in hard_states.items():
            if not passed:
                reasons.append(f"{key}_CORE_NOT_PASS")
        stage = "CANSLIM_ELIGIBLE" if all(hard_states.values()) else "BREAKOUT_CONFIRMED"

    return CandidateRecord(
        assessment_id=pattern.assessment_id,
        candidate_id=pattern.candidate_id,
        base_id=pattern.base_id,
        lineage_id=pattern.lineage_id,
        security_id=pattern.security_id,
        ticker=pattern.ticker,
        asof_date=pattern.asof_date,
        pattern=pattern.pattern,
        pattern_status=pattern.normalized_status,
        native_detector_state=pattern.native_state,
        candidate_semantics=pattern.candidate_semantics,
        detector_faults=pattern.detector_faults,
        pattern_engine_version=pattern.engine_version,
        pattern_contract_version=pattern.output_schema_version,
        pivot_level=pattern.pivot_level,
        pivot_source_date=pattern.pivot_source_date,
        pivot_crossed_intraday=pivot_crossed,
        open_above_pivot=open_above,
        gap_through_pivot=gap_through,
        close_above_pivot=close_above,
        extension_from_pivot_pct=extension,
        within_traditional_buy_zone=within_zone,
        volume_avg_50_prior=avg50,
        volume_ratio=volume_ratio,
        volume_confirmation_state=volume_state,
        candidate_stage=stage,
        eligibility_reason_codes=tuple(reasons),
        C_screen_state=evidence.C_screen_state,
        A_screen_state=evidence.A_screen_state,
        L_individual_leadership_state=evidence.L_individual_leadership_state,
        M_entry_state=evidence.M_entry_state,
        N_price_state=evidence.N_price_state,
        N_catalyst_state=evidence.N_catalyst_state,
        S_evidence_state=evidence.S_evidence_state,
        I_evidence_state=evidence.I_evidence_state,
        industry_evidence_state=evidence.industry_evidence_state,
    )
