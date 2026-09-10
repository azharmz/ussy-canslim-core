import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from canslim_research.execution import entry_decision, resolve_bar_exit


def test_fill_inside_buy_zone_is_accepted():
    r = entry_decision(pivot=100.0, h1_open=104.0)
    assert r.accepted
    assert r.entry_price == 104.0
    assert abs(r.hard_stop - 96.72) < 1e-12
    assert r.profit_target == 120.0


def test_exact_5pct_fill_is_accepted():
    assert entry_decision(pivot=100.0, h1_open=105.0).accepted


def test_above_5pct_fill_is_skipped():
    r = entry_decision(pivot=100.0, h1_open=105.01)
    assert not r.accepted
    assert r.reason == "ABOVE_BUY_ZONE_AT_FILL"


def test_fill_below_or_at_pivot_is_skipped():
    assert entry_decision(pivot=100.0, h1_open=100.0).reason == "BELOW_PIVOT_AT_FILL"
    assert entry_decision(pivot=100.0, h1_open=99.0).reason == "BELOW_PIVOT_AT_FILL"


def test_same_bar_stop_and_target_is_stop_first():
    r = resolve_bar_exit(open_price=100.0, high=125.0, low=90.0, hard_stop=93.0, profit_target=120.0)
    assert r.reason == "HARD_STOP_7PCT"
    assert r.exit_price == 93.0


def test_stop_gap_through_uses_open():
    r = resolve_bar_exit(open_price=90.0, high=95.0, low=89.0, hard_stop=93.0, profit_target=120.0)
    assert r.reason == "STOP_GAP_THROUGH"
    assert r.exit_price == 90.0


def test_target_gap_through_uses_open():
    r = resolve_bar_exit(open_price=125.0, high=127.0, low=124.0, hard_stop=93.0, profit_target=120.0)
    assert r.reason == "TARGET_GAP_THROUGH"
    assert r.exit_price == 125.0
