"""Source-stack acceptance gate for #52 PIT broad-market leadership evidence."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

VERSION = "52-pit-broad-market-leadership-source-audit-v1"


class SourceAuditStatus(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NOT_EVALUABLE = "NOT_EVALUABLE"


@dataclass(frozen=True)
class SourceStackEvidence:
    source_id: str
    broad_market_membership_valid: bool | None
    membership_pit_provenance: bool | None
    leader_selection_authoritative_or_separately_frozen: bool | None
    institutional_flow_explicit: bool | None
    machine_reproducible: bool | None
    availability_timestamped: bool | None
    future_returns_not_used: bool | None
    restricted_universe_not_used_as_proxy: bool | None


@dataclass(frozen=True)
class SourceAuditResult:
    source_id: str
    status: str
    reason: str
    version: str = VERSION


_REQUIRED_FIELDS = (
    "broad_market_membership_valid",
    "membership_pit_provenance",
    "leader_selection_authoritative_or_separately_frozen",
    "institutional_flow_explicit",
    "machine_reproducible",
    "availability_timestamped",
    "future_returns_not_used",
    "restricted_universe_not_used_as_proxy",
)


def audit_source_stack(e: SourceStackEvidence) -> SourceAuditResult:
    values = {name: getattr(e, name) for name in _REQUIRED_FIELDS}
    unknown = [name for name, value in values.items() if value is None]
    if unknown:
        return SourceAuditResult(
            e.source_id,
            SourceAuditStatus.NOT_EVALUABLE.value,
            "UNKNOWN_REQUIRED_EVIDENCE:" + ",".join(unknown),
        )

    failed = [name for name, value in values.items() if value is False]
    if failed:
        return SourceAuditResult(
            e.source_id,
            SourceAuditStatus.REJECTED.value,
            "FAILED_REQUIRED_GATE:" + ",".join(failed),
        )

    return SourceAuditResult(
        e.source_id,
        SourceAuditStatus.APPROVED.value,
        "ALL_REQUIRED_SOURCE_GATES_SATISFIED",
    )
