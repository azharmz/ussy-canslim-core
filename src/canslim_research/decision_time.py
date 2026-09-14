from __future__ import annotations

from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
UTC = timezone.utc
REGULAR_CLOSE = time(16, 0)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(UTC)


def regular_close_cutoff(session_date: date) -> datetime:
    """Return the regular-session 16:00 America/New_York close in UTC.

    The ZoneInfo conversion intentionally carries DST semantics; callers must
    not hard-code a UTC hour for the US market close.
    """
    local_close = datetime.combine(session_date, REGULAR_CLOSE, tzinfo=NY)
    return local_close.astimezone(UTC)


def resolve_information_cutoff(
    *,
    session_date: date,
    decision_asof_timestamp: datetime | None = None,
) -> datetime:
    """Resolve the information cutoff for a same-session close decision.

    If a decision timestamp is supplied before the regular close, information
    is cut off at that timestamp. A timestamp at/after the close is capped at
    the regular close. Without an explicit timestamp, the regular close is the
    default contract for a close-based daily decision.
    """
    close = regular_close_cutoff(session_date)
    if decision_asof_timestamp is None:
        return close
    decision = _as_utc(decision_asof_timestamp)
    return min(decision, close)


def information_available(accepted_at: datetime, information_cutoff: datetime) -> bool:
    """SEC information is available iff its full acceptance timestamp is <= cutoff."""
    return _as_utc(accepted_at) <= _as_utc(information_cutoff)
