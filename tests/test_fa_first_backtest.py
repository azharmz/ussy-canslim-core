from canslim_research.candidate_v2 import DailyBar
from canslim_research.fa_first_backtest import (
    FundamentalPassInterval,
    assert_prefix_stability,
    monitor_pass_interval,
    prefix_bars,
)


def bars():
    return [
        DailyBar("2020-01-01", 10, 11, 9, 10, 100),
        DailyBar("2020-01-02", 10, 11, 9, 10, 100),
        DailyBar("2020-01-03", 10, 11, 9, 10, 100),
        DailyBar("2020-01-06", 10, 11, 9, 10, 100),
    ]


def test_prefix_never_contains_future_bar():
    out = prefix_bars(bars(), "2020-01-03")
    assert [x.session_date for x in out] == ["2020-01-01", "2020-01-02", "2020-01-03"]


def test_interval_only_invokes_pattern_inside_watchlist():
    interval = FundamentalPassInterval("i1", "sid", "ABC", "2020-01-02", "2020-01-03", "state1")
    seen = []

    def runner(security_id, decision_date, prefix):
        seen.append((security_id, decision_date, prefix[-1].session_date))
        return []

    def evidence(interval, decision_date):
        raise AssertionError("evidence provider should not be needed when no assessment exists")

    # Evidence is evaluated once per monitored session by design, so use a harmless provider.
    from canslim_research.candidate_v2 import CandidateEvidence
    def evidence_ok(interval, decision_date):
        return CandidateEvidence("PASS", "PASS", "PASS", "ALLOW_NEW_BUYS")

    out = monitor_pass_interval(interval, bars(), pattern_runner=runner, evidence_provider=evidence_ok)
    assert out == []
    assert seen == [
        ("sid", "2020-01-02", "2020-01-02"),
        ("sid", "2020-01-03", "2020-01-03"),
    ]


def test_prefix_stability_adapter_contract():
    interval = FundamentalPassInterval("i1", "sid", "ABC", "2020-01-02", "2020-01-03", "state1")

    def runner(security_id, decision_date, prefix):
        return [{"date": decision_date, "n": len(prefix)}]

    assert_prefix_stability(interval, bars(), pattern_runner=runner)
