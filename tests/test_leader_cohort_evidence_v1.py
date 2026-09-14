from canslim_research.leader_cohort_evidence_v1 import LeaderEvidencePacket, assess_packet


def packet(**overrides):
    values = dict(
        security_id="TEST",
        asof_date="2026-09-14",
        membership_run_id="53-run",
        membership_manifest_sha256="abc",
        membership_valid_asof=True,
        restricted_universe_used_as_proxy=False,
        future_returns_used=False,
        rs_evidence_available=True,
        price_leadership_evidence_available=True,
        demand_evidence_available=True,
        institutional_sponsorship_evidence_available=False,
        evidence_timestamped=True,
    )
    values.update(overrides)
    return LeaderEvidencePacket(**values)


def test_complete_pit_packet_is_study_eligible_not_leader_label():
    result = assess_packet(packet())
    assert result.status == "STUDY_ELIGIBLE"
    assert "LEADER" not in result.status


def test_future_returns_are_rejected():
    assert assess_packet(packet(future_returns_used=True)).reason == "FUTURE_RETURNS_USED"


def test_restricted_universe_proxy_is_rejected():
    assert assess_packet(packet(restricted_universe_used_as_proxy=True)).reason == "RESTRICTED_UNIVERSE_PROXY"


def test_invalid_asof_membership_is_rejected():
    assert assess_packet(packet(membership_valid_asof=False)).reason == "MEMBERSHIP_NOT_VALID_ASOF"


def test_missing_membership_lineage_is_not_evaluable():
    assert assess_packet(packet(membership_run_id=None)).status == "NOT_EVALUABLE"


def test_untimestamped_evidence_is_rejected():
    assert assess_packet(packet(evidence_timestamped=False)).reason == "EVIDENCE_NOT_TIMESTAMPED"


def test_unknown_evidence_channel_is_not_evaluable():
    assert assess_packet(packet(demand_evidence_available=None)).reason == "UNKNOWN_EVIDENCE_CHANNEL"


def test_no_admissible_evidence_is_not_evaluable():
    result = assess_packet(packet(
        rs_evidence_available=False,
        price_leadership_evidence_available=False,
        demand_evidence_available=False,
        institutional_sponsorship_evidence_available=False,
    ))
    assert result.reason == "NO_ADMISSIBLE_EVIDENCE_AVAILABLE"
