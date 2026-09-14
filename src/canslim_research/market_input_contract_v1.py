"""Production input/provenance boundary for frozen #46 market-state classifier."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Sequence

VERSION = "47-market-input-data-contract-v1"
CANONICAL_INDEX_IDS = frozenset({"NASDAQ_COMPOSITE", "SP500", "DJIA"})
ETF_IDENTITIES = frozenset({"SPY", "QQQ", "DIA"})


@dataclass(frozen=True)
class MarketIndexBar:
    index_id: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float]
    source_provider: str
    source_symbol: str
    fetched_at: str
    source_contract_version: str


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...]
    version: str = VERSION


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_market_index_series(bars: Sequence[MarketIndexBar]) -> ValidationResult:
    errors: list[str] = []
    if not bars:
        return ValidationResult(False, ("EMPTY_SERIES",))

    ids = {b.index_id for b in bars}
    if len(ids) != 1:
        errors.append("MIXED_INDEX_IDENTITIES")
    for index_id in ids:
        if index_id in ETF_IDENTITIES:
            errors.append("ETF_SUBSTITUTION_FORBIDDEN")
        elif index_id not in CANONICAL_INDEX_IDS:
            errors.append("NONCANONICAL_INDEX_ID")

    parsed_dates: list[date] = []
    for b in bars:
        try:
            d = _parse_date(b.date)
            parsed_dates.append(d)
        except ValueError:
            errors.append("INVALID_DATE")
            continue

        if not b.source_provider or not b.source_symbol or not b.source_contract_version:
            errors.append("MISSING_SOURCE_PROVENANCE")
        try:
            fetched = _parse_datetime(b.fetched_at)
            if fetched.date() < d:
                errors.append("FETCHED_BEFORE_SESSION_DATE")
        except ValueError:
            errors.append("INVALID_FETCHED_AT")

        if min(b.open, b.high, b.low, b.close) <= 0:
            errors.append("NONPOSITIVE_OHLC")
        if b.high < max(b.open, b.low, b.close) or b.low > min(b.open, b.high, b.close):
            errors.append("INVALID_OHLC_ENVELOPE")
        if b.volume is not None and b.volume < 0:
            errors.append("NEGATIVE_VOLUME")

    if len(parsed_dates) == len(bars):
        if len(set(parsed_dates)) != len(parsed_dates):
            errors.append("DUPLICATE_DATE")
        if parsed_dates != sorted(parsed_dates):
            errors.append("NONMONOTONIC_DATES")

    return ValidationResult(not errors, tuple(dict.fromkeys(errors)))


def to_market_state_inputs(bars: Sequence[MarketIndexBar]):
    """Return frozen #46 IndexBar values without imputing missing volume."""
    result = validate_market_index_series(bars)
    if not result.valid:
        raise ValueError(",".join(result.errors))
    from canslim_research.market_state_v1 import IndexBar
    return tuple(IndexBar(date=b.date, low=b.low, close=b.close, volume=b.volume) for b in bars)
