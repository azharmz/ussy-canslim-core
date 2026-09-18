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


def test_checkpoint_is_deterministic_and_pins_lineage():
    from canslim_research.shadow_v2_pipeline import watchlist_checkpoint_payload

    assessments = {"two": wl(c="FAIL", sid="two"), "one": wl(sid="one")}
    a = watchlist_checkpoint_payload(assessments, LINEAGE, producer_commit="sha", producer_run="run")
    b = watchlist_checkpoint_payload(dict(reversed(list(assessments.items()))), LINEAGE, producer_commit="sha", producer_run="run")
    assert a["content_sha256"] == b["content_sha256"]
    assert a["qualified_count"] == 1
    assert a["lineage"]["ready_sha256"] == "abc"


def test_checkpoint_lineage_mismatch_fails_closed():
    import pytest
    from canslim_research.shadow_v2_pipeline import validate_checkpoint_lineage, watchlist_checkpoint_payload

    checkpoint = watchlist_checkpoint_payload({"one": wl(sid="one")}, LINEAGE, producer_commit="sha", producer_run="run")
    wrong = WatchlistLineage(
        decision_date=LINEAGE.decision_date,
        ready_key=LINEAGE.ready_key,
        ready_sha256="different",
        fundamental_source_identity=LINEAGE.fundamental_source_identity,
    )
    with pytest.raises(RuntimeError, match="LINEAGE_MISMATCH"):
        validate_checkpoint_lineage(checkpoint, wrong)


def test_frozen_p33_runner_receives_only_qualified_rows():
    import pandas as pd
    from canslim_research.shadow_v2_pipeline import run_frozen_p33_for_qualified

    ready = pd.DataFrame({
        "security_id": ["one", "one", "two", "two"],
        "date": ["2026-09-16", "2026-09-17"] * 2,
    })
    assessments = {"one": wl(sid="one"), "two": wl(c="FAIL", sid="two")}
    observed = {}

    def fake_frozen_runner(frame):
        observed["ids"] = set(frame["security_id"])
        return "p33-result"

    assert run_frozen_p33_for_qualified(ready, assessments, runner=fake_frozen_runner) == "p33-result"
    assert observed["ids"] == {"one"}


def test_watchlist_builder_is_identity_deterministic_and_duplicate_safe():
    import pytest
    from canslim_research.watchlist_v2 import build_watchlist

    rows = [
        {"security_id": "two", "ticker": "TWO", "c": "FAIL", "a": "PASS"},
        {"security_id": "one", "ticker": "ONE", "c": "PASS", "a": "PASS"},
    ]
    resolver = lambda row: (row["c"], row["a"])
    built = build_watchlist(rows, lineage=LINEAGE, state_resolver=resolver)
    assert list(built) == ["one", "two"]
    assert built["one"].qualified
    assert not built["two"].qualified

    with pytest.raises(RuntimeError, match="DUPLICATE_WATCHLIST_SECURITY_ID"):
        build_watchlist([rows[0], dict(rows[0])], lineage=LINEAGE, state_resolver=resolver)


def test_watchlist_preserves_exact_not_evaluable_state():
    assert wl(c="NOT_EVALUABLE").watchlist_state == "C_NOT_EVALUABLE"
    assert wl(a="NOT_EVALUABLE").watchlist_state == "A_NOT_EVALUABLE"


def test_stale_m_fails_closed_explicitly():
    ok, reasons = eligible(M_entry_state="STALE")
    assert ok is False
    assert reasons == ("M_STALE",)
