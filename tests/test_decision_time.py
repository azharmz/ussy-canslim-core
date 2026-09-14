from datetime import date, datetime, timezone

import pytest

from canslim_research.decision_time import (
    information_available,
    regular_close_cutoff,
    resolve_information_cutoff,
)

UTC = timezone.utc


def test_regular_close_respects_us_dst():
    assert regular_close_cutoff(date(2026, 9, 15)) == datetime(2026, 9, 15, 20, 0, tzinfo=UTC)
    assert regular_close_cutoff(date(2026, 12, 15)) == datetime(2026, 12, 15, 21, 0, tzinfo=UTC)


def test_before_cutoff_is_available():
    cutoff = datetime(2026, 9, 15, 20, 0, tzinfo=UTC)
    assert information_available(datetime(2026, 9, 15, 19, 59, 59, tzinfo=UTC), cutoff)


def test_exactly_at_cutoff_is_available():
    cutoff = datetime(2026, 9, 15, 20, 0, tzinfo=UTC)
    assert information_available(cutoff, cutoff)


def test_after_market_close_is_not_available_for_same_close_decision():
    cutoff = regular_close_cutoff(date(2026, 9, 15))
    assert not information_available(datetime(2026, 9, 15, 20, 0, 1, tzinfo=UTC), cutoff)


def test_next_day_filing_cannot_leak_backward():
    cutoff = regular_close_cutoff(date(2026, 9, 15))
    assert not information_available(datetime(2026, 9, 16, 12, 0, tzinfo=UTC), cutoff)


def test_amendment_obeys_same_timestamp_rule():
    cutoff = regular_close_cutoff(date(2026, 9, 15))
    original = datetime(2026, 9, 15, 18, 0, tzinfo=UTC)
    amendment = datetime(2026, 9, 15, 20, 30, tzinfo=UTC)
    assert information_available(original, cutoff)
    assert not information_available(amendment, cutoff)


def test_preclose_decision_timestamp_tightens_cutoff():
    decision = datetime(2026, 9, 15, 18, 30, tzinfo=UTC)
    cutoff = resolve_information_cutoff(session_date=date(2026, 9, 15), decision_asof_timestamp=decision)
    assert cutoff == decision
    assert not information_available(datetime(2026, 9, 15, 18, 31, tzinfo=UTC), cutoff)


def test_postclose_decision_timestamp_does_not_expand_same_close_cutoff():
    decision = datetime(2026, 9, 15, 22, 0, tzinfo=UTC)
    cutoff = resolve_information_cutoff(session_date=date(2026, 9, 15), decision_asof_timestamp=decision)
    assert cutoff == datetime(2026, 9, 15, 20, 0, tzinfo=UTC)


def test_naive_timestamps_are_rejected():
    with pytest.raises(ValueError):
        information_available(datetime(2026, 9, 15, 19, 0), datetime(2026, 9, 15, 20, 0, tzinfo=UTC))
