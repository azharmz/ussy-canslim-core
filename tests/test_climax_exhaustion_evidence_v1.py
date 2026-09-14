from canslim_research.climax_exhaustion_evidence_v1 import DailyBar, WeeklyBar, evaluate_climax_exhaustion_evidence, validate_climax_exhaustion_evidence


def b(d,o,h,l,c,v=100): return DailyBar(d,o,h,l,c,v)


def test_insufficient_history_keeps_sequence_flags_none():
    x = evaluate_climax_exhaustion_evidence(candidate_id='c', security_id='s', breakout_date='2026-01-01', daily_bars=[b('2026-01-01',10,11,9,10)])
    assert x.seven_of_eight_up_days is None
    assert x.eight_of_ten_up_days is None


def test_strict_largest_up_day_boundary():
    bars=[b('2026-01-01',10,11,9,10), b('2026-01-02',10,12,10,12), b('2026-01-03',12,14,12,14)]
    x=evaluate_climax_exhaustion_evidence(candidate_id='c', security_id='s', breakout_date='2026-01-01', daily_bars=bars)
    assert x.largest_up_day_point_gain_since_breakout is False


def test_largest_up_day_true_when_strictly_greater():
    bars=[b('2026-01-01',10,11,9,10), b('2026-01-02',10,12,10,11), b('2026-01-03',11,14,11,14)]
    x=evaluate_climax_exhaustion_evidence(candidate_id='c', security_id='s', breakout_date='2026-01-01', daily_bars=bars)
    assert x.largest_up_day_point_gain_since_breakout is True


def test_heaviest_volume_strict():
    bars=[b('2026-01-01',10,11,9,10,100), b('2026-01-02',10,12,10,11,200), b('2026-01-03',11,13,11,12,200)]
    x=evaluate_climax_exhaustion_evidence(candidate_id='c', security_id='s', breakout_date='2026-01-01', daily_bars=bars)
    assert x.heaviest_daily_volume_since_breakout is False


def test_seven_of_eight_up_days():
    closes=[10,11,12,13,14,15,16,15,16]
    bars=[b(f'2026-01-{i+1:02d}',c,c+1,c-1,c) for i,c in enumerate(closes)]
    x=evaluate_climax_exhaustion_evidence(candidate_id='c', security_id='s', breakout_date='2026-01-01', daily_bars=bars)
    assert x.up_days_last_8 == 7 and x.seven_of_eight_up_days is True


def test_eight_of_ten_up_days():
    closes=[10,11,12,13,12,13,14,15,16,15,16]
    bars=[b(f'2026-01-{i+1:02d}',c,c+1,c-1,c) for i,c in enumerate(closes)]
    x=evaluate_climax_exhaustion_evidence(candidate_id='c', security_id='s', breakout_date='2026-01-01', daily_bars=bars)
    assert x.up_days_last_10 == 8 and x.eight_of_ten_up_days is True


def test_raw_exhaustion_gap_uses_low_above_prior_high():
    bars=[b('2026-01-01',10,11,9,10), b('2026-01-02',12,13,11.5,12.5)]
    x=evaluate_climax_exhaustion_evidence(candidate_id='c', security_id='s', breakout_date='2026-01-01', daily_bars=bars)
    assert x.exhaustion_gap_raw is True


def test_weekly_range_strict_largest():
    weeks=[WeeklyBar('2026-01-09',15,10), WeeklyBar('2026-01-16',18,10)]
    x=evaluate_climax_exhaustion_evidence(candidate_id='c', security_id='s', breakout_date='2026-01-01', daily_bars=[b('2026-01-01',10,11,9,10)], weekly_bars=weeks)
    assert x.weekly_range == 8 and x.largest_weekly_range_since_breakout is True


def test_evidence_only_boundary():
    x=evaluate_climax_exhaustion_evidence(candidate_id='c', security_id='s', breakout_date='2026-01-01', daily_bars=[b('2026-01-01',10,11,9,10)])
    assert x.promotion_state == 'EVIDENCE_ONLY'
    assert x.prior_advance_context_state == 'CONTEXT_RECORDED_NOT_ACTIONABLE'


def test_validator_green():
    x=evaluate_climax_exhaustion_evidence(candidate_id='c', security_id='s', breakout_date='2026-01-01', daily_bars=[b('2026-01-01',10,11,9,10)])
    assert validate_climax_exhaustion_evidence(x) == []
