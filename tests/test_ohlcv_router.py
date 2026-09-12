import pytest

from canslim_research.ohlcv_router import (
    DEFAULT_SOURCE_ORDER,
    NoSourceAvailable,
    ProviderResult,
    SourceRoutingError,
    SourceStatus,
    route_ohlcv,
)


def _good_rows():
    return (
        {"date": "2023-01-03", "open": 100, "high": 103, "low": 99, "close": 102, "volume": 1000},
        {"date": "2023-01-04", "open": 102, "high": 104, "low": 101, "close": 103, "volume": 1200},
    )


def test_default_source_order_is_frozen():
    assert DEFAULT_SOURCE_ORDER == ("r2", "yahoo", "tiingo")


def test_r2_unavailable_falls_back_to_yahoo():
    calls = []

    def r2():
        calls.append("r2")
        return ProviderResult("r2", SourceStatus.UNAVAILABLE, reason="window absent")

    def yahoo():
        calls.append("yahoo")
        return ProviderResult("yahoo", SourceStatus.AVAILABLE, rows=_good_rows())

    def tiingo():
        calls.append("tiingo")
        return ProviderResult("tiingo", SourceStatus.AVAILABLE, rows=_good_rows())

    result = route_ohlcv({"r2": r2, "yahoo": yahoo, "tiingo": tiingo})
    assert result.source == "yahoo"
    assert calls == ["r2", "yahoo"]


def test_r2_failure_is_terminal_and_yahoo_is_not_called():
    calls = []

    def r2():
        calls.append("r2")
        return ProviderResult("r2", SourceStatus.FAILED, reason="R2 authentication failed")

    def yahoo():
        calls.append("yahoo")
        return ProviderResult("yahoo", SourceStatus.AVAILABLE, rows=_good_rows())

    with pytest.raises(SourceRoutingError, match="authentication failed"):
        route_ohlcv({"r2": r2, "yahoo": yahoo, "tiingo": yahoo})
    assert calls == ["r2"]


def test_r2_qc_failure_is_terminal():
    bad_rows = (
        {"date": "2023-01-03", "open": 100, "high": 98, "low": 99, "close": 102, "volume": 1000},
    )

    def r2():
        return ProviderResult("r2", SourceStatus.AVAILABLE, rows=bad_rows)

    def should_not_run():
        raise AssertionError("fallback must not run after QC failure")

    with pytest.raises(SourceRoutingError, match="QC failed"):
        route_ohlcv({"r2": r2, "yahoo": should_not_run, "tiingo": should_not_run})


def test_r2_and_yahoo_unavailable_falls_back_to_tiingo():
    calls = []

    def unavailable(name):
        def provider():
            calls.append(name)
            return ProviderResult(name, SourceStatus.UNAVAILABLE, reason="window absent")
        return provider

    def tiingo():
        calls.append("tiingo")
        return ProviderResult("tiingo", SourceStatus.AVAILABLE, rows=_good_rows())

    result = route_ohlcv(
        {"r2": unavailable("r2"), "yahoo": unavailable("yahoo"), "tiingo": tiingo}
    )
    assert result.source == "tiingo"
    assert calls == ["r2", "yahoo", "tiingo"]


def test_all_sources_unavailable_raises_no_source_available():
    def unavailable(name):
        return lambda: ProviderResult(name, SourceStatus.UNAVAILABLE, reason="window absent")

    with pytest.raises(NoSourceAvailable):
        route_ohlcv(
            {
                "r2": unavailable("r2"),
                "yahoo": unavailable("yahoo"),
                "tiingo": unavailable("tiingo"),
            }
        )


def test_provider_exception_is_terminal():
    called = []

    def r2():
        called.append("r2")
        raise RuntimeError("network timeout")

    def yahoo():
        called.append("yahoo")
        return ProviderResult("yahoo", SourceStatus.AVAILABLE, rows=_good_rows())

    with pytest.raises(SourceRoutingError, match="network timeout"):
        route_ohlcv({"r2": r2, "yahoo": yahoo, "tiingo": yahoo})
    assert called == ["r2"]
