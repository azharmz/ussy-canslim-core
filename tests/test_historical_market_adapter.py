from canslim_research.historical_market_adapter import decision_on, replay_historical_market
from canslim_research.market_state_v1 import IndexBar


def _bars():
    # Same synthetic chronology for all three canonical index identities.
    rows = (
        IndexBar("2020-01-02", 99.0, 100.0, 100.0),
        IndexBar("2020-01-03", 100.0, 101.0, 110.0),
        IndexBar("2020-01-06", 101.0, 102.0, 120.0),
        IndexBar("2020-01-07", 102.0, 103.0, 130.0),
        IndexBar("2020-01-08", 103.0, 105.0, 150.0),
    )
    return {k: rows for k in ("NASDAQ_COMPOSITE", "SP500", "DJIA")}


def test_historical_m_is_exact_date_and_index_only():
    out = replay_historical_market(index_series=_bars())
    assert len(out) == 5
    last = decision_on(out, "2020-01-08")
    assert last.asof_date == "2020-01-08"
    assert last.provenance == "HISTORICAL_INDEX_ONLY_FROZEN_46_REPLAY"
    assert last.M_entry_state in {"ALLOW_NEW_BUYS", "BLOCK_NEW_BUYS", "NOT_EVALUABLE"}


def test_historical_m_does_not_accept_stale_lookup():
    out = replay_historical_market(index_series=_bars())
    try:
        decision_on(out, "2020-01-09")
    except ValueError as exc:
        assert "exactly one decision" in str(exc)
    else:
        raise AssertionError("missing exact-date market state must fail closed")
