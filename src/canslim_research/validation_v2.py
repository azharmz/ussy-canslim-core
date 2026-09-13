"""Validation-only checks for workstream #35.

These checks audit frozen #33/#34 semantics. They must not tune detector or
candidate parameters and contain no trading-performance logic.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from canslim_research.candidate_v2 import CandidateRecord


@dataclass(frozen=True, slots=True)
class ValidationFinding:
    code: str
    severity: str
    detail: str


def audit_candidate_record(record: CandidateRecord) -> tuple[ValidationFinding, ...]:
    findings: list[ValidationFinding] = []

    if record.pattern_status in {"AMBIGUOUS", "REJECTED"} and record.candidate_stage != "NOT_ELIGIBLE":
        findings.append(ValidationFinding("STATUS_PROMOTION", "ERROR", "non-recognized #33 status was promoted"))

    if record.prior_cross_after_structure and record.pivot_crossed_intraday:
        findings.append(ValidationFinding("REPEATED_BREAKOUT_RECOUNT", "ERROR", "prior post-structure cross was recounted"))

    if record.pivot_crossed_intraday != record.first_tradeable_daily_bar_crossed_pivot:
        findings.append(ValidationFinding("CROSSING_FLAG_INCONSISTENT", "ERROR", "crossing flags disagree"))

    if record.volume_confirmation_state == "CONFIRMED_ON_BREAKOUT":
        if record.volume_ratio is None or record.volume_ratio < 1.40:
            findings.append(ValidationFinding("VOLUME_CONFIRMATION_INVALID", "ERROR", "confirmed breakout has volume ratio below 1.40 or missing"))
        if record.volume_confirmation_date != record.breakout_date:
            findings.append(ValidationFinding("VOLUME_DATE_INVALID", "ERROR", "on-breakout confirmation date differs from breakout date"))

    if record.candidate_stage == "CANSLIM_ELIGIBLE":
        required = {
            "C": record.C_screen_state == "PASS",
            "A": record.A_screen_state == "PASS",
            "L": record.L_individual_leadership_state in {"PASS", "STRONG"},
            "M": record.M_entry_state == "ALLOW_NEW_BUYS",
            "volume": record.volume_confirmation_state == "CONFIRMED_ON_BREAKOUT",
            "pattern": record.pattern_status == "RECOGNIZED",
        }
        failed = [name for name, ok in required.items() if not ok]
        if failed:
            findings.append(ValidationFinding("ELIGIBILITY_GATE_INVALID", "ERROR", f"eligible record fails gates: {','.join(failed)}"))

    if record.candidate_stage == "BREAKOUT_CONFIRMED" and record.volume_confirmation_state != "CONFIRMED_ON_BREAKOUT":
        findings.append(ValidationFinding("CONFIRMED_STAGE_WITHOUT_VOLUME", "ERROR", "BREAKOUT_CONFIRMED lacks breakout-day volume confirmation"))

    if record.candidate_stage == "PIVOT_CROSSED" and not record.pivot_crossed_intraday:
        findings.append(ValidationFinding("PIVOT_CROSSED_STAGE_INVALID", "ERROR", "PIVOT_CROSSED stage lacks first crossing"))

    if record.breakout_date is not None and not record.pivot_crossed_intraday:
        findings.append(ValidationFinding("BREAKOUT_DATE_WITHOUT_CROSS", "ERROR", "breakout_date exists without first crossing"))

    if record.pattern_status == "RECOGNIZED" and record.pivot_level is None and record.candidate_stage not in {"BASE_RECOGNIZED", "NOT_ELIGIBLE"}:
        findings.append(ValidationFinding("MISSING_PIVOT_STAGE_INVALID", "ERROR", "recognized record without pivot advanced beyond base stage"))

    return tuple(findings)


def audit_records(records: Iterable[CandidateRecord]) -> tuple[ValidationFinding, ...]:
    findings: list[ValidationFinding] = []
    for record in records:
        findings.extend(audit_candidate_record(record))
    return tuple(findings)
