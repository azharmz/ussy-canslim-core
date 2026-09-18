from canslim_research.eligibility_v2 import EligibilityV2Input, evaluate_v2
from canslim_research.watchlist_v2 import WatchlistLineage, assess_watchlist, qualified_security_ids


LINEAGE = WatchlistLineage(
    decision_date="2026-09-17",
    ready_key="production/ready/runs/2026-09-17.parquet",
    ready_sha256="abc",
    fundamental_source_identity="fund-v1",
)


def wl(c="PASS", a="PASS", sid="US0000000001"):
    return assess_watchlist(
        security_id=sid,
        symbol_asof="TEST",
        lineage=LINEAGE,
        C_state=c,
        A_state=a,
    )


def eligible(**changes):
    values = dict(
        watchlist_state="QUALIFIED",
        pattern_state="RECOGNIZED",
        pivot_defined=True,
        pivot_crossed=True,
        breakout_volume_state="CONFIRMED_ON_BREAKOUT",
        L_individual_state="PASS",
        M_entry_state="ALLOW_NEW_BUYS",
    )
    values.update(changes)
    return evaluate_v2(EligibilityV2Input(**values))


def test_watchlist_requires_c_and_a():
    assert wl().qualified
    assert wl(c="FAIL").reason_codes == ("C_FAIL",)
    assert wl(a="FAIL").reason_codes == ("A_FAIL",)
    x = wl(c="NOT_EVALUABLE", a="FAIL")
    assert not x.qualified
    assert x.reason_codes == ("C_NOT_EVALUABLE", "A_FAIL")


def test_only_qualified_ids_are_handed_downstream():
    assessments = {
        "one": wl(sid="one"),
        "two": wl(c="FAIL", sid="two"),
        "three": wl(a="NOT_EVALUABLE", sid="three"),
    }
    assert qualified_security_ids(assessments) == frozenset({"one"})


def test_role_aware_hard_path_passes():
    ok, reasons = eligible()
    assert ok is True
    assert reasons == ()


def test_i_and_n_nonprice_do_not_become_universal_vetoes():
    ok, reasons = eligible(I_evidence_state="NEGATIVE", N_catalyst_state="NOT_IMPLEMENTED")
    assert ok is True
    assert reasons == ()


def test_breakout_volume_l_and_m_remain_hard_boundaries():
    ok, reasons = eligible(
        breakout_volume_state="UNCONFIRMED",
        L_individual_state="FAIL",
        M_entry_state="BLOCK_NEW_BUYS",
    )
    assert ok is False
    assert reasons == (
        "BREAKOUT_VOLUME_UNCONFIRMED",
        "L_SCREEN_FAIL",
        "M_BLOCK_NEW_BUYS",
    )


def test_ambiguous_pattern_blocks():
    ok, reasons = eligible(pattern_state="AMBIGUOUS")
    assert ok is False
    assert "PATTERN_AMBIGUOUS" in reasons


def test_nonqualified_watchlist_cannot_bypass_fundamentals():
    ok, reasons = eligible(watchlist_state="C_FAIL")
    assert ok is False
    assert reasons[0] == "WATCHLIST_NOT_QUALIFIED"
