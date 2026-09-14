from canslim_research.market_state_v1 import IndexBar, classify_index, classify_market


def bars(rows):
    return [IndexBar(str(i), low, close, vol) for i, (low, close, vol) in enumerate(rows)]


def test_day1_starts_on_up_close():
    e = classify_index("N", bars([(99,100,100),(100,101,90)]))
    assert e.rally_day == 1 and e.rally_day1_low == 100


def test_day1_low_undercut_resets_attempt():
    e = classify_index("N", bars([(99,100,100),(100,101,90),(99,100.5,80)]))
    assert e.attempt_intact is False


def test_equal_day1_low_does_not_undercut():
    e = classify_index("N", bars([(99,100,100),(100,101,90),(100,100.5,80)]))
    assert e.attempt_intact is True and e.rally_day == 2


def test_ftd_cannot_occur_before_day4():
    e = classify_index("N", bars([(99,100,100),(100,101,90),(100,102,95),(101,104,120)]))
    assert e.rally_day == 3 and e.follow_through_today is False


def test_day4_ftd_requires_125pct_and_higher_volume():
    e = classify_index("N", bars([(99,100,100),(100,101,90),(100,101.5,85),(101,102,80),(102,103.275,100)]))
    assert e.rally_day == 4 and e.follow_through_today is True


def test_ftd_exact_boundary_fails_without_higher_volume():
    e = classify_index("N", bars([(99,100,100),(100,101,90),(100,101.5,85),(101,102,80),(102,103.275,80)]))
    assert e.follow_through_today is False


def test_distribution_exact_point2_and_higher_volume():
    e = classify_index("N", bars([(99,100,100),(100,101,90),(100,100.798,100)]))
    assert e.distribution_today is True


def test_market_ftd_from_one_major_index_confirms():
    s = bars([(99,100,100),(100,101,90),(100,101.5,85),(101,102,80),(102,103.275,100)])
    x = classify_market(index_series={"N":s}, prior_state="RALLY_ATTEMPT")
    assert x.state == "FOLLOW_THROUGH_CONFIRMED"


def test_leadership_promotes_confirmed_to_healthy():
    s = bars([(99,100,100),(100,100.5,90)])
    x = classify_market(index_series={"N":s}, prior_state="FOLLOW_THROUGH_CONFIRMED", leadership_confirming=True)
    assert x.state == "UPTREND_HEALTHY"


def test_weakening_has_precedence_over_leadership():
    s = bars([(99,100,100),(100,100.5,90)])
    x = classify_market(index_series={"N":s}, prior_state="UPTREND_HEALTHY", leadership_confirming=True, weakening_confirmed=True)
    assert x.state == "UPTREND_WEAKENING"


def test_distribution_alone_does_not_invent_weakening_threshold():
    s = bars([(99,100,100),(100,101,90),(99,100,120)])
    x = classify_market(index_series={"N":s}, prior_state="UPTREND_HEALTHY")
    assert x.state == "UPTREND_HEALTHY"


def test_explicit_correction_reset_wins():
    s = bars([(99,100,100),(100,101,90)])
    x = classify_market(index_series={"N":s}, prior_state="UPTREND_WEAKENING", correction_reset=True)
    assert x.state == "CORRECTION"


def test_no_index_data_is_not_evaluable():
    x = classify_market(index_series={}, prior_state="CORRECTION")
    assert x.state == "NOT_EVALUABLE"
