import pytest

from canslim_research.market_input_contract_v1 import (
    VERSION, MarketIndexBar, to_market_state_inputs, validate_market_index_series,
)


def bar(**kw):
    base = dict(index_id="NASDAQ_COMPOSITE", date="2026-09-10", open=100.0, high=102.0,
                low=99.0, close=101.0, volume=1_000_000.0, source_provider="TEST",
                source_symbol="INDEX", fetched_at="2026-09-10T22:00:00+00:00",
                source_contract_version="source-v1")
    base.update(kw)
    return MarketIndexBar(**base)


def test_contract_version_frozen():
    assert VERSION == "47-market-input-data-contract-v1"


def test_three_canonical_index_identities_allowed():
    for index_id in ("NASDAQ_COMPOSITE", "SP500", "DJIA"):
        assert validate_market_index_series([bar(index_id=index_id)]).valid


def test_spy_and_qqq_cannot_masquerade_as_indexes():
    for ticker in ("SPY", "QQQ"):
        r = validate_market_index_series([bar(index_id=ticker)])
        assert not r.valid and "ETF_SUBSTITUTION_FORBIDDEN" in r.errors


def test_noncanonical_identity_rejected():
    r = validate_market_index_series([bar(index_id="RUSSELL2000")])
    assert not r.valid and "NONCANONICAL_INDEX_ID" in r.errors


def test_missing_volume_is_preserved_not_imputed():
    b = bar(volume=None)
    assert validate_market_index_series([b]).valid
    adapted = to_market_state_inputs([b])
    assert adapted[0].volume is None


def test_negative_volume_rejected():
    r = validate_market_index_series([bar(volume=-1)])
    assert not r.valid and "NEGATIVE_VOLUME" in r.errors


def test_invalid_ohlc_envelope_rejected():
    r = validate_market_index_series([bar(high=100.0, close=101.0)])
    assert not r.valid and "INVALID_OHLC_ENVELOPE" in r.errors


def test_missing_provenance_rejected():
    r = validate_market_index_series([bar(source_provider="")])
    assert not r.valid and "MISSING_SOURCE_PROVENANCE" in r.errors


def test_duplicate_dates_rejected():
    r = validate_market_index_series([bar(), bar()])
    assert not r.valid and "DUPLICATE_DATE" in r.errors


def test_nonmonotonic_dates_rejected():
    r = validate_market_index_series([bar(date="2026-09-11"), bar(date="2026-09-10")])
    assert not r.valid and "NONMONOTONIC_DATES" in r.errors


def test_fetched_before_session_date_rejected():
    r = validate_market_index_series([bar(fetched_at="2026-09-09T23:00:00+00:00")])
    assert not r.valid and "FETCHED_BEFORE_SESSION_DATE" in r.errors


def test_adapter_preserves_raw_close_low_and_volume():
    b = bar(low=98.5, close=101.25, volume=12345)
    x = to_market_state_inputs([b])[0]
    assert (x.date, x.low, x.close, x.volume) == (b.date, 98.5, 101.25, 12345)


def test_mixed_index_series_rejected():
    r = validate_market_index_series([bar(index_id="NASDAQ_COMPOSITE"), bar(index_id="SP500", date="2026-09-11")])
    assert not r.valid and "MIXED_INDEX_IDENTITIES" in r.errors
