from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Callable, Iterable, Mapping, Sequence

from canslim_research.candidate_v2 import CandidateEvidence, CandidateRecord, DailyBar, PatternAssessment, build_candidate

RUNNER_VERSION = "fa-first-historical-runner-v0.1"
FROZEN_ONEIL_SHA = "c433cc1e35a5aa32a46f732cd8c5545935e36e40"
FROZEN_PATTERN_SCHEMA = "oneil-pattern-output-v2"


@dataclass(frozen=True, slots=True)
class FundamentalPassInterval:
    interval_id: str
    security_id: str
    ticker: str
    start_date: str
    end_date: str
    state_identity: str


@dataclass(frozen=True, slots=True)
class MonitoringEvent:
    interval_id: str
    security_id: str
    ticker: str
    decision_date: str
    assessment_id: str
    candidate_id: str
    base_id: str
    pattern: str
    candidate_stage: str
    pivot_level: float | None
    volume_ratio: float | None
    M_market_state: str
    M_entry_state: str
    signal: bool
    runner_version: str = RUNNER_VERSION
    oneil_sha: str = FROZEN_ONEIL_SHA


PatternRunner = Callable[[str, str, Sequence[DailyBar]], Iterable[Mapping[str, object]]]
EvidenceProvider = Callable[[FundamentalPassInterval, str], CandidateEvidence]


def _iso(x: str) -> date:
    return date.fromisoformat(x)


def validate_interval(x: FundamentalPassInterval) -> None:
    if _iso(x.end_date) < _iso(x.start_date):
        raise ValueError("fundamental PASS interval ends before it starts")
    if not x.interval_id or not x.state_identity:
        raise ValueError("interval lineage is required")


def prefix_bars(bars: Sequence[DailyBar], decision_date: str) -> list[DailyBar]:
    out = [b for b in bars if b.session_date <= decision_date]
    if any(b.session_date > decision_date for b in out):
        raise AssertionError("future OHLCV leaked into decision prefix")
    if len({b.session_date for b in out}) != len(out):
        raise ValueError("duplicate OHLCV session")
    return sorted(out, key=lambda b: b.session_date)


def monitor_pass_interval(
    interval: FundamentalPassInterval,
    bars: Sequence[DailyBar],
    *,
    pattern_runner: PatternRunner,
    evidence_provider: EvidenceProvider,
) -> list[MonitoringEvent]:
    """Monitor exactly one frozen fundamental PASS interval, causally day by day.

    pattern_runner is an adapter to the pinned ussy-oneil-patterns implementation.
    This module deliberately does not contain a second morphology implementation.
    """
    validate_interval(interval)
    sessions = sorted(
        b.session_date
        for b in bars
        if interval.start_date <= b.session_date <= interval.end_date
    )
    events: list[MonitoringEvent] = []

    for decision_date in sessions:
        prefix = prefix_bars(bars, decision_date)
        raw = list(pattern_runner(interval.security_id, decision_date, prefix))
        evidence = evidence_provider(interval, decision_date)

        for row in raw:
            assessment = PatternAssessment.from_mapping(row)
            if assessment.security_id != interval.security_id:
                raise ValueError("pattern security differs from watchlist interval")
            if assessment.asof_date != decision_date:
                raise ValueError("pattern assessment is not exact decision date")
            candidate: CandidateRecord = build_candidate(assessment, prefix, evidence)
            events.append(MonitoringEvent(
                interval_id=interval.interval_id,
                security_id=interval.security_id,
                ticker=interval.ticker,
                decision_date=decision_date,
                assessment_id=candidate.assessment_id,
                candidate_id=candidate.candidate_id,
                base_id=candidate.base_id,
                pattern=candidate.pattern,
                candidate_stage=candidate.candidate_stage,
                pivot_level=candidate.pivot_level,
                volume_ratio=candidate.volume_ratio,
                M_market_state=candidate.M_market_state,
                M_entry_state=candidate.M_entry_state,
                signal=candidate.candidate_stage == "CANSLIM_ELIGIBLE",
            ))
    return events


def assert_prefix_stability(
    interval: FundamentalPassInterval,
    bars: Sequence[DailyBar],
    *,
    pattern_runner: PatternRunner,
) -> None:
    """Fail if the adapter exposes future bars or changes an already-observed prefix result."""
    sessions = sorted(
        b.session_date
        for b in bars
        if interval.start_date <= b.session_date <= interval.end_date
    )
    for decision_date in sessions:
        prefix = prefix_bars(bars, decision_date)
        a = list(pattern_runner(interval.security_id, decision_date, prefix))
        # Re-create the same prefix from the full history. A pinned engine must see identical input.
        b = list(pattern_runner(interval.security_id, decision_date, prefix_bars(list(bars), decision_date)))
        if a != b:
            raise AssertionError(f"prefix instability at {decision_date}")
