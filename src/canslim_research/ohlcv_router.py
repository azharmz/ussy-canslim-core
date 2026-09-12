"""Strict OHLCV source routing for pattern-development research.

The router intentionally distinguishes *unavailable* data from a broken source.
Fallback is permitted only when a provider can positively report that the
requested window is unavailable. Transport, authentication, parse, or QC
failures are terminal so a lower-priority provider cannot silently change the
price morphology used by the pattern engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Iterable, Mapping, Sequence


DEFAULT_SOURCE_ORDER = ("r2", "yahoo", "tiingo")


class SourceStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    FAILED = "FAILED"
    QC_FAILED = "QC_FAILED"


@dataclass(frozen=True)
class ProviderResult:
    source: str
    status: SourceStatus
    rows: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    reason: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


class SourceRoutingError(RuntimeError):
    """A higher-priority provider failed and fallback is forbidden."""


class NoSourceAvailable(SourceRoutingError):
    """Every configured provider positively reported the window unavailable."""


def validate_ohlcv_rows(rows: Sequence[Mapping[str, Any]]) -> tuple[bool, str | None]:
    """Minimal morphology-preserving OHLCV QC independent of pandas."""
    if not rows:
        return False, "empty requested window"

    required = ("date", "open", "high", "low", "close", "volume")
    previous_date: Any = None
    seen_dates: set[Any] = set()

    for index, row in enumerate(rows):
        missing = [name for name in required if row.get(name) is None]
        if missing:
            return False, f"row {index}: missing {','.join(missing)}"

        date = row["date"]
        if date in seen_dates:
            return False, f"row {index}: duplicate date {date}"
        if previous_date is not None and date <= previous_date:
            return False, f"row {index}: dates are not strictly increasing"
        seen_dates.add(date)
        previous_date = date

        try:
            open_ = float(row["open"])
            high = float(row["high"])
            low = float(row["low"])
            close = float(row["close"])
            volume = float(row["volume"])
        except (TypeError, ValueError):
            return False, f"row {index}: non-numeric OHLCV"

        if min(open_, high, low, close) <= 0:
            return False, f"row {index}: non-positive price"
        if volume < 0:
            return False, f"row {index}: negative volume"
        if high < max(open_, low, close):
            return False, f"row {index}: high violates OHLC envelope"
        if low > min(open_, high, close):
            return False, f"row {index}: low violates OHLC envelope"

    return True, None


def route_ohlcv(
    providers: Mapping[str, Callable[[], ProviderResult]],
    *,
    source_order: Iterable[str] = DEFAULT_SOURCE_ORDER,
    validator: Callable[[Sequence[Mapping[str, Any]]], tuple[bool, str | None]] = validate_ohlcv_rows,
) -> ProviderResult:
    """Return the first valid source, falling back only on UNAVAILABLE.

    A provider callable must convert an absent object / absent requested window
    into ``UNAVAILABLE``. Any operational failure must instead be returned as
    ``FAILED`` (or raised by the provider), and malformed data as ``QC_FAILED``.
    """
    unavailable_reasons: list[str] = []

    for source in tuple(source_order):
        if source not in providers:
            raise SourceRoutingError(f"provider not configured: {source}")

        try:
            result = providers[source]()
        except Exception as exc:  # provider errors are terminal by design
            raise SourceRoutingError(f"{source}: provider exception: {exc}") from exc

        if result.source != source:
            raise SourceRoutingError(
                f"{source}: provider returned mismatched source={result.source!r}"
            )

        if result.status is SourceStatus.UNAVAILABLE:
            unavailable_reasons.append(f"{source}: {result.reason or 'unavailable'}")
            continue

        if result.status is SourceStatus.FAILED:
            raise SourceRoutingError(f"{source}: {result.reason or 'source failure'}")
        if result.status is SourceStatus.QC_FAILED:
            raise SourceRoutingError(f"{source}: QC failed: {result.reason or 'unknown'}")
        if result.status is not SourceStatus.AVAILABLE:
            raise SourceRoutingError(f"{source}: unknown status {result.status!r}")

        valid, reason = validator(result.rows)
        if not valid:
            raise SourceRoutingError(f"{source}: QC failed: {reason}")
        return result

    detail = "; ".join(unavailable_reasons) or "no providers attempted"
    raise NoSourceAvailable(f"requested OHLCV window unavailable: {detail}")
