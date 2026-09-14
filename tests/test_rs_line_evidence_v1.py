from canslim_research.rs_line_evidence_v1 import (
    BENCHMARK_ID,
    VERSION,
    RSLineObservation,
    evaluate_rs_line,
)


def obs(date, stock, benchmark):
    return RSLineObservation(date, stock, benchmark)


def evaluate(rows, **kwargs):
    base = dict(
        asof_date=rows[-1].session_date if rows else "2026-09-11",
        input_window_id="DECLARED_TEST_WINDOW",
        stock_source_provenance="stock-source-run",
        benchmark_source_provenance="sp500-source-run",
    )
    base.update(kwargs)
    return evaluate_rs_line(rows, **base)


def test_constants_are_frozen():
    assert VERSION == "54-rs-line-evidence-v1"
    assert BENCHMARK_ID == "SP500"


def test_rising_rs_line_and_new_window_high():
    rows = [
        obs("2026-09-09", 100, 100),
        obs("2026-09-10", 105, 102),
        obs("2026-09-11", 110, 103),
    ]
    r = evaluate(rows)
    assert r.state == "EVALUABLE"
    assert r.direction_vs_prior == "RISING"
    assert r.at_input_window_high is True
    assert r.new_input_window_high is True


def test_stock_can_rise_while_rs_line_falls():
    rows = [obs("2026-09-10", 100, 100), obs("2026-09-11", 101, 105)]
    r = evaluate(rows)
    assert r.direction_vs_prior == "FALLING"
    assert r.new_input_window_high is False


def test_equal_rs_line_is_flat_and_at_high_but_not_new_high():
    rows = [obs("2026-09-10", 100, 100), obs("2026-09-11", 110, 110)]
    r = evaluate(rows)
    assert r.direction_vs_prior == "FLAT"
    assert r.at_input_window_high is True
    assert r.new_input_window_high is False


def test_latest_can_rise_without_being_window_high():
    rows = [
        obs("2026-09-09", 120, 100),
        obs("2026-09-10", 100, 100),
        obs("2026-09-11", 110, 100),
    ]
    r = evaluate(rows)
    assert r.direction_vs_prior == "RISING"
    assert r.at_input_window_high is False
    assert r.new_input_window_high is False


def test_spy_is_not_accepted_as_canonical_benchmark():
    rows = [obs("2026-09-10", 100, 100), obs("2026-09-11", 110, 105)]
    r = evaluate(rows, benchmark_id="SPY")
    assert r.state == "NOT_EVALUABLE"
    assert r.reason == "NONCANONICAL_BENCHMARK"


def test_missing_window_identity_is_not_evaluable():
    rows = [obs("2026-09-10", 100, 100), obs("2026-09-11", 110, 105)]
    r = evaluate(rows, input_window_id=None)
    assert r.state == "NOT_EVALUABLE"
    assert r.reason == "INPUT_WINDOW_ID_MISSING"


def test_missing_provenance_is_not_evaluable():
    rows = [obs("2026-09-10", 100, 100), obs("2026-09-11", 110, 105)]
    r = evaluate(rows, stock_source_provenance=None)
    assert r.state == "NOT_EVALUABLE"
    assert r.reason == "SOURCE_PROVENANCE_MISSING"


def test_one_observation_is_not_evaluable():
    r = evaluate([obs("2026-09-11", 100, 100)])
    assert r.state == "NOT_EVALUABLE"
    assert r.reason == "INSUFFICIENT_ALIGNED_OBSERVATIONS"


def test_duplicate_or_nonmonotonic_dates_are_rejected():
    dup = [obs("2026-09-11", 100, 100), obs("2026-09-11", 110, 105)]
    assert evaluate(dup).reason == "DUPLICATE_SESSION_DATE"
    nonmono = [obs("2026-09-11", 100, 100), obs("2026-09-10", 110, 105)]
    r = evaluate(nonmono, asof_date="2026-09-10")
    assert r.reason == "NONMONOTONIC_SESSION_DATES"


def test_asof_must_equal_final_observation():
    rows = [obs("2026-09-10", 100, 100), obs("2026-09-11", 110, 105)]
    r = evaluate(rows, asof_date="2026-09-12")
    assert r.state == "NOT_EVALUABLE"
    assert r.reason == "ASOF_DATE_NOT_FINAL_OBSERVATION"


def test_nonpositive_price_is_not_evaluable():
    rows = [obs("2026-09-10", 100, 100), obs("2026-09-11", 110, 0)]
    r = evaluate(rows)
    assert r.state == "NOT_EVALUABLE"
    assert r.reason == "INVALID_NONPOSITIVE_OR_NONFINITE_PRICE"
