from __future__ import annotations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import canslim_research.ohlcv_providers as providers
from canslim_research.ohlcv_router import ProviderResult, SourceStatus


def test_r2_ticker_absence_is_explicit_unavailable(monkeypatch):
    def absent(ticker, snapshot_date="current"):
        raise providers.R2TickerNotInSnapshot("not in current membership")

    monkeypatch.setattr(providers, "resolve_security_id_from_r2", absent)
    result = providers.r2_ticker_provider(ticker="TW", start="2024-01-01", end="2024-11-20")
    assert result.status is SourceStatus.UNAVAILABLE
    assert result.metadata["membership_resolution"] == "ABSENT"


def test_r2_ticker_ambiguous_mapping_is_terminal_failure(monkeypatch):
    def ambiguous(ticker, snapshot_date="current"):
        raise providers.R2TickerAmbiguous("multiple security ids")

    monkeypatch.setattr(providers, "resolve_security_id_from_r2", ambiguous)
    result = providers.r2_ticker_provider(ticker="TW", start="2024-01-01", end="2024-11-20")
    assert result.status is SourceStatus.FAILED
    assert "R2TickerAmbiguous" in result.reason


def test_r2_ticker_success_delegates_to_canonical_security_id(monkeypatch):
    monkeypatch.setattr(providers, "resolve_security_id_from_r2", lambda ticker, snapshot_date="current": "SEC123")

    seen = {}
    def fake_r2_provider(*, security_id, start, end):
        seen.update(security_id=security_id, start=start, end=end)
        return ProviderResult("r2", SourceStatus.AVAILABLE, rows=({"date":"2024-01-02","open":1,"high":1,"low":1,"close":1,"volume":1},), metadata={"security_id":security_id})

    monkeypatch.setattr(providers, "r2_provider", fake_r2_provider)
    result = providers.r2_ticker_provider(ticker="ABC", start="2024-01-01", end="2024-01-31")
    assert result.status is SourceStatus.AVAILABLE
    assert seen["security_id"] == "SEC123"
    assert result.metadata["security_id"] == "SEC123"
