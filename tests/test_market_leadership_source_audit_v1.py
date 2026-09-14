from canslim_research.market_leadership_source_audit_v1 import (
    SourceAuditStatus,
    SourceStackEvidence,
    audit_source_stack,
)


def _base(**overrides):
    values = dict(
        source_id="X",
        broad_market_membership_valid=True,
        membership_pit_provenance=True,
        leader_selection_authoritative_or_separately_frozen=True,
        institutional_flow_explicit=True,
        machine_reproducible=True,
        availability_timestamped=True,
        future_returns_not_used=True,
        restricted_universe_not_used_as_proxy=True,
    )
    values.update(overrides)
    return SourceStackEvidence(**values)


def test_approved_only_when_all_required_gates_true():
    r = audit_source_stack(_base())
    assert r.status == SourceAuditStatus.APPROVED.value
    assert r.reason == "ALL_REQUIRED_SOURCE_GATES_SATISFIED"


def test_unknown_required_evidence_is_not_evaluable():
    r = audit_source_stack(_base(institutional_flow_explicit=None))
    assert r.status == SourceAuditStatus.NOT_EVALUABLE.value
    assert "institutional_flow_explicit" in r.reason


def test_any_false_required_gate_rejects_stack():
    r = audit_source_stack(_base(machine_reproducible=False))
    assert r.status == SourceAuditStatus.REJECTED.value
    assert "machine_reproducible" in r.reason


def test_restricted_universe_proxy_is_rejected():
    r = audit_source_stack(_base(restricted_universe_not_used_as_proxy=False))
    assert r.status == SourceAuditStatus.REJECTED.value
    assert "restricted_universe_not_used_as_proxy" in r.reason


def test_future_return_selected_leaders_are_rejected():
    r = audit_source_stack(_base(future_returns_not_used=False))
    assert r.status == SourceAuditStatus.REJECTED.value
    assert "future_returns_not_used" in r.reason


def test_nasdaq_directory_alone_cannot_pass_51():
    r = audit_source_stack(
        _base(
            source_id="NASDAQ_TRADER_DIRECTORY_ONLY",
            leader_selection_authoritative_or_separately_frozen=False,
            institutional_flow_explicit=False,
        )
    )
    assert r.status == SourceAuditStatus.REJECTED.value


def test_ohlcv_alone_cannot_pass_without_leader_contract():
    r = audit_source_stack(
        _base(
            source_id="BROAD_OHLCV_ONLY",
            leader_selection_authoritative_or_separately_frozen=False,
            institutional_flow_explicit=False,
        )
    )
    assert r.status == SourceAuditStatus.REJECTED.value


def test_theory_aligned_source_with_unknown_operational_contract_stays_not_evaluable():
    r = audit_source_stack(
        _base(
            source_id="THEORY_ALIGNED_PROPRIETARY_SOURCE",
            machine_reproducible=None,
            availability_timestamped=None,
            membership_pit_provenance=None,
        )
    )
    assert r.status == SourceAuditStatus.NOT_EVALUABLE.value
