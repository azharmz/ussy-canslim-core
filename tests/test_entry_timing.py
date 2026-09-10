import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from canslim_research.entry_timing import x1_immediate, x2_first_valid, x3_pivot_hold, x4_retest_hold


def test_x1_uses_t1_only():
    assert x1_immediate(pivot=100.0, opens=[104.0]).entry_offset == 1
    assert not x1_immediate(pivot=100.0, opens=[106.0]).accepted


def test_x2_can_wait_until_t3():
    r = x2_first_valid(pivot=100.0, opens=[106.0, 99.0, 103.0])
    assert r.accepted
    assert r.entry_offset == 3
    assert r.entry_price == 103.0


def test_x3_confirmation_is_causal_and_fills_next_open():
    r = x3_pivot_hold(
        pivot=100.0,
        opens=[102.0, 103.0, 104.0],
        lows=[100.5, 101.0, 102.0],
        closes=[102.5, 103.5, 104.0],
    )
    assert r.accepted
    assert r.confirmation_offset == 1
    assert r.entry_offset == 2
    assert r.entry_price == 103.0


def test_x3_rejects_intraday_pivot_break():
    r = x3_pivot_hold(
        pivot=100.0,
        opens=[102.0, 103.0, 104.0],
        lows=[99.5, 99.8, 102.0],
        closes=[102.5, 103.5, 104.0],
    )
    assert not r.accepted


def test_x4_retest_hold_then_next_open():
    r = x4_retest_hold(
        pivot=100.0,
        opens=[104.0, 102.0, 103.0],
        lows=[101.5, 101.0, 102.0],
        closes=[103.0, 102.5, 103.0],
    )
    assert r.accepted
    assert r.confirmation_offset == 1
    assert r.entry_offset == 2
    assert r.entry_price == 102.0


def test_x4_does_not_use_t3_close_for_t4_fill():
    r = x4_retest_hold(
        pivot=100.0,
        opens=[106.0, 106.0, 103.0],
        lows=[104.0, 104.0, 101.0],
        closes=[104.0, 104.0, 102.0],
    )
    assert not r.accepted
