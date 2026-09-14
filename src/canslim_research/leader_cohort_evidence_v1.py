"""PIT evidence-packet boundary for #54 leader-cohort study.

This module deliberately does not classify securities as production market leaders.
It validates that candidate evidence packets are point-in-time and provenance-complete
for later preregistered selector research.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

VERSION = "54-pit-leader-cohort-evidence-study-v1"


class PacketStatus(str, Enum):
    STUDY_ELIGIBLE = "STUDY_ELIGIBLE"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class LeaderEvidencePacket:
    security_id: str
    asof_date: str
    membership_run_id: str | None
    membership_manifest_sha256: str | None
    membership_valid_asof: bool | None
    restricted_universe_used_as_proxy: bool | None
    future_returns_used: bool | None
    rs_evidence_available: bool | None
    price_leadership_evidence_available: bool | None
    demand_evidence_available: bool | None
    institutional_sponsorship_evidence_available: bool | None
    evidence_timestamped: bool | None


@dataclass(frozen=True)
class PacketAssessment:
    security_id: str
    status: str
    reason: str
    version: str = VERSION


def assess_packet(packet: LeaderEvidencePacket) -> PacketAssessment:
    """Assess research eligibility only; never return a leader/non-leader label."""
    if packet.future_returns_used is True:
        return PacketAssessment(packet.security_id, PacketStatus.REJECTED.value, "FUTURE_RETURNS_USED")
    if packet.restricted_universe_used_as_proxy is True:
        return PacketAssessment(packet.security_id, PacketStatus.REJECTED.value, "RESTRICTED_UNIVERSE_PROXY")
    if packet.membership_valid_asof is False:
        return PacketAssessment(packet.security_id, PacketStatus.REJECTED.value, "MEMBERSHIP_NOT_VALID_ASOF")

    provenance = (
        packet.membership_run_id,
        packet.membership_manifest_sha256,
        packet.membership_valid_asof,
        packet.restricted_universe_used_as_proxy,
        packet.future_returns_used,
        packet.evidence_timestamped,
    )
    if any(value is None or value == "" for value in provenance):
        return PacketAssessment(packet.security_id, PacketStatus.NOT_EVALUABLE.value, "INCOMPLETE_PIT_PROVENANCE")
    if packet.evidence_timestamped is not True:
        return PacketAssessment(packet.security_id, PacketStatus.REJECTED.value, "EVIDENCE_NOT_TIMESTAMPED")

    evidence = (
        packet.rs_evidence_available,
        packet.price_leadership_evidence_available,
        packet.demand_evidence_available,
        packet.institutional_sponsorship_evidence_available,
    )
    if any(value is None for value in evidence):
        return PacketAssessment(packet.security_id, PacketStatus.NOT_EVALUABLE.value, "UNKNOWN_EVIDENCE_CHANNEL")
    if not any(value is True for value in evidence):
        return PacketAssessment(packet.security_id, PacketStatus.NOT_EVALUABLE.value, "NO_ADMISSIBLE_EVIDENCE_AVAILABLE")

    return PacketAssessment(packet.security_id, PacketStatus.STUDY_ELIGIBLE.value, "PIT_PACKET_READY_FOR_PREREGISTERED_STUDY")
