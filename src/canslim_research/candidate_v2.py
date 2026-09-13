from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

PATTERN_SCHEMA_VERSION = "oneil-pattern-output-v2"
EXPECTED_PATTERN_ENGINE_VERSION = "33-core-p8-frozen-v1"
EXPECTED_LABELLED_VALIDATION_STATUS = "P8_CONDITIONAL_PASS_FROZEN"
CANDIDATE_SPEC_VERSION = "theory-faithful-candidate-spec-v1"
CANDIDATE_OUTPUT_SCHEMA_VERSION = "canslim-candidate-output-v2"
CANDIDATE_GENERATOR_VERSION = "34-candidate-generator-v0.2"

CORE_PATTERNS = frozenset({
    "FLAT_BASE",
    "DOUBLE_BOTTOM",
    "CUP_WITHOUT_HANDLE",
    "CUP_WITH_HANDLE",
})
PATTERN_STATUSES = frozenset({"RECOGNIZED", "AMBIGUOUS", "REJECTED"})
EXPECTED_DETECTOR_VERSIONS = {
    "FLAT_BASE": "flat-base-v2",
    "DOUBLE_BOTTOM": "double-bottom-v3",
    "CUP_WITHOUT_HANDLE": "cup-family-v2",
    "CUP_WITH_HANDLE": "cup-family-v2",
}


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
        engine = str(row.get("engine_version", ""))
        if engine != EXPECTED_PATTERN_ENGINE_VERSION:
            raise ValueError(f"unsupported #33 engine version: {engine!r}")
        validation_status = str(row.get("labelled_validation_status", ""))
        if validation_status != EXPECTED_LABELLED_VALIDATION_STATUS:
            raise ValueError(f"unsupported #33 validation status: {validation_status!r}")
        pattern = str(row.get("pattern", ""))
        if pattern not in CORE_PATTERNS:
            raise ValueError(f"pattern outside frozen #33 core contract: {pattern!r}")
        detector_version = str(row.get("detector_contract_version", ""))
        expected_detector = EXPECTED_DETECTOR_VERSIONS[pattern]
        if detector_version != expected_detector:
            raise ValueError(
                f"unsupported detector version for {pattern}: {detector_version!r}; expected {expected_detector!r}"
            )
        status = str(row.get("normalized_status", ""))
        if status not in PATTERN_STATUSES:
            raise ValueError(f"unsupported normalized_status: {status!r}")
        return cls(
            assessment_id=str(row["assessment_id"]),
            output_schema_version=schema,
            engine_version=engine,
            labelled_validation_status=validation_status,
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
            detector_contract_version=detector_version,
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
    rs_rating_proxy_percentile: float | None = None
    M_market_state: str = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class CandidateRecord:
    assessment_id: str
    candidate_id: str
    base_id: str
    lineage_id: str
    security_id: str
    ticker: str
    asof_date: str
    breakout_date: str | None
    pattern: str
    pattern_status: str
    native_detector_state: str
    candidate_semantics: str
    structural_signature: tuple[str, ...]
    structural_start: str
    structural_end: str | None
    depth_pct: float | None
    detector_faults: tuple[str, ...]
    pattern_engine_version: str
    pattern_validation_status: str
    pattern_contract_version: str
    detector_contract_version: str
    pivot_level: float | None
    pivot_source_date: str | None
    pivot_crossed_intraday: bool
    first_tradeable_daily_bar_crossed_pivot: bool
    prior_cross_after_structure: bool
    open_above_pivot: bool
    gap_through_pivot: bool
    close_above_pivot: bool
    close_position_quality: float | None
    extension_from_pivot_pct: float | None
    within_traditional_buy_zone: bool
    extended_above_traditional_buy_zone: bool
    volume_avg_50_prior: float | None
    volume_ratio: float | None
    volume_confirmation_state: str
    volume_confirmation_date: str | None
    candidate_stage: str
    eligibility_reason_codes: tuple[str, ...]
    C_screen_state: str
    A_screen_state: str
    L_individual_leadership_state: str
    rs_rating_proxy_percentile: float | None
    M_market_state: str
    M_entry_state: str
    N_price_state: str
    N_catalyst_state: str
    S_evidence_state: str
    I_evidence_state: str
    industry_evidence_state: str
    candidate_output_schema_version: str = CANDIDATE_OUTPUT_SCHEMA_VERSION
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


def _prior_cross_after_structure(
    bars: Sequence[DailyBar], *, pivot: float, structural_end: str | None, asof_date: str
) -> bool:
    if structural_end is None:
        return False
    return any(
        bar.session_date >= structural_end
        and bar.session_date < asof_date
        and bar.high > pivot
        for bar in bars
    )


def _close_position_quality(bar: DailyBar) -> float | None:
    spread = bar.high - bar.low
    if spread <= 0:
        return None
    return max(0.0, min(1.0, (bar.close - bar.low) / spread))


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
    first_cross = False
    prior_cross = False
    open_above = False
    gap_through = False
    close_above = False
    close_quality = None
    extension = None
    within_zone = False
    extended = False
    avg50 = None
    volume_ratio = None
    volume_state = "NOT_EVALUABLE"
    volume_confirmation_date = None
    breakout_date = None

    if ambiguous:
        reasons.append("PATTERN_AMBIGUOUS")
    elif pattern.normalized_status == "REJECTED":
        reasons.append("PATTERN_REJECTED")

    if recognized and pattern.pivot_level is None:
        reasons.append("PIVOT_NOT_DEFINED")

    if pivot_defined and bar is not None:
        pivot = float(pattern.pivot_level)
        raw_cross = bar.high > pivot
        prior_cross = _prior_cross_after_structure(
            bars, pivot=pivot, structural_end=pattern.structural_end, asof_date=pattern.asof_date
        )
        first_cross = raw_cross and not prior_cross
        pivot_crossed = first_cross
        open_above = first_cross and bar.open > pivot
        gap_through = first_cross and bar.open > pivot and bar.low > pivot
        close_above = first_cross and bar.close > pivot
        close_quality = _close_position_quality(bar) if first_cross else None
        if first_cross:
            breakout_date = pattern.asof_date
            extension = ((bar.close / pivot) - 1.0) * 100.0
            within_zone = 0.0 <= extension <= 5.0
            extended = extension > 5.0
            avg50 = _prior_50_volume(bars, pattern.asof_date)
            if avg50 is not None and avg50 > 0:
                volume_ratio = bar.volume / avg50
                if volume_ratio >= 1.40:
                    volume_state = "CONFIRMED_ON_BREAKOUT"
                    volume_confirmation_date = pattern.asof_date
                else:
                    volume_state = "PENDING_CONFIRMATION"
            else:
                volume_state = "NOT_EVALUABLE"
        elif raw_cross and prior_cross:
            reasons.append("BREAKOUT_ALREADY_OCCURRED")
    elif pivot_defined:
        reasons.append("BREAKOUT_BAR_NOT_EVALUABLE")

    if not recognized:
        stage = "NOT_ELIGIBLE"
    elif not pivot_defined:
        stage = "BASE_RECOGNIZED"
    elif not first_cross:
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

    n_price_state = "PASS" if first_cross else evidence.N_price_state
    if volume_state == "CONFIRMED_ON_BREAKOUT":
        s_evidence_state = "POSITIVE"
    elif volume_state == "PENDING_CONFIRMATION":
        s_evidence_state = "NEUTRAL"
    else:
        s_evidence_state = evidence.S_evidence_state

    return CandidateRecord(
        assessment_id=pattern.assessment_id,
        candidate_id=pattern.candidate_id,
        base_id=pattern.base_id,
        lineage_id=pattern.lineage_id,
        security_id=pattern.security_id,
        ticker=pattern.ticker,
        asof_date=pattern.asof_date,
        breakout_date=breakout_date,
        pattern=pattern.pattern,
        pattern_status=pattern.normalized_status,
        native_detector_state=pattern.native_state,
        candidate_semantics=pattern.candidate_semantics,
        structural_signature=pattern.structural_signature,
        structural_start=pattern.structural_start,
        structural_end=pattern.structural_end,
        depth_pct=pattern.depth_pct,
        detector_faults=pattern.detector_faults,
        pattern_engine_version=pattern.engine_version,
        pattern_validation_status=pattern.labelled_validation_status,
        pattern_contract_version=pattern.output_schema_version,
        detector_contract_version=pattern.detector_contract_version,
        pivot_level=pattern.pivot_level,
        pivot_source_date=pattern.pivot_source_date,
        pivot_crossed_intraday=pivot_crossed,
        first_tradeable_daily_bar_crossed_pivot=first_cross,
        prior_cross_after_structure=prior_cross,
        open_above_pivot=open_above,
        gap_through_pivot=gap_through,
        close_above_pivot=close_above,
        close_position_quality=close_quality,
        extension_from_pivot_pct=extension,
        within_traditional_buy_zone=within_zone,
        extended_above_traditional_buy_zone=extended,
        volume_avg_50_prior=avg50,
        volume_ratio=volume_ratio,
        volume_confirmation_state=volume_state,
        volume_confirmation_date=volume_confirmation_date,
        candidate_stage=stage,
        eligibility_reason_codes=tuple(reasons),
        C_screen_state=evidence.C_screen_state,
        A_screen_state=evidence.A_screen_state,
        L_individual_leadership_state=evidence.L_individual_leadership_state,
        rs_rating_proxy_percentile=evidence.rs_rating_proxy_percentile,
        M_market_state=evidence.M_market_state,
        M_entry_state=evidence.M_entry_state,
        N_price_state=n_price_state,
        N_catalyst_state=evidence.N_catalyst_state,
        S_evidence_state=s_evidence_state,
        I_evidence_state=evidence.I_evidence_state,
        industry_evidence_state=evidence.industry_evidence_state,
    )
