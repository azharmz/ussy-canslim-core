from datetime import date

import pytest

from scripts.retain_candidate_snapshots import run_id, snapshot_date, snapshot_prefix_from_key


def canonical_by_date(prefixes, current_prefix):
    by_date = {}
    for prefix in prefixes:
        by_date.setdefault(snapshot_date(prefix), []).append(prefix)
    return {
        d: current_prefix if current_prefix in ps else max(ps, key=run_id)
        for d, ps in by_date.items()
    }


def retention_plan(prefixes, current_prefix, explicit_protected=(), keep_newest_dates=2):
    canonical = canonical_by_date(prefixes, current_prefix)
    by_date = {}
    for prefix in prefixes:
        by_date.setdefault(snapshot_date(prefix), []).append(prefix)
    newest_dates = sorted(by_date, reverse=True)[:keep_newest_dates]
    protected = {current_prefix, *explicit_protected}
    protected.update(canonical[d] for d in newest_dates)
    duplicates = {
        prefix
        for d, ps in by_date.items()
        for prefix in ps
        if prefix != canonical[d] and prefix not in protected
    }
    return canonical, protected, duplicates


def p(d, run):
    return f"canslim/candidates/snapshots/{d}/run-{run}/"


def test_current_pointer_wins_same_session_even_if_not_highest_run():
    current = p("2026-09-14", 100)
    newer_rerun = p("2026-09-14", 200)
    canonical, _, duplicates = retention_plan([current, newer_rerun], current)
    assert canonical[date(2026, 9, 14)] == current
    assert duplicates == {newer_rerun}


def test_highest_numeric_run_is_canonical_when_date_is_not_current():
    current = p("2026-09-15", 300)
    old_a = p("2026-09-14", 9)
    old_b = p("2026-09-14", 10)
    canonical, _, duplicates = retention_plan([current, old_a, old_b], current)
    assert canonical[date(2026, 9, 14)] == old_b
    assert duplicates == {old_a}


def test_keep_newest_counts_distinct_session_dates_not_runs():
    current = p("2026-09-15", 300)
    same_date_duplicate = p("2026-09-15", 301)
    prior = p("2026-09-14", 200)
    older = p("2026-09-13", 100)
    canonical, protected, duplicates = retention_plan(
        [current, same_date_duplicate, prior, older], current, keep_newest_dates=2
    )
    assert canonical[date(2026, 9, 15)] == current
    assert current in protected
    assert prior in protected
    assert older not in protected
    assert same_date_duplicate in duplicates


def test_explicitly_protected_noncanonical_duplicate_is_preserved():
    current = p("2026-09-15", 300)
    canonical_old = p("2026-09-14", 200)
    protected_duplicate = p("2026-09-14", 100)
    _, protected, duplicates = retention_plan(
        [current, canonical_old, protected_duplicate],
        current,
        explicit_protected={protected_duplicate},
    )
    assert protected_duplicate in protected
    assert protected_duplicate not in duplicates


def test_prefix_parser_and_run_id_fail_closed():
    good_key = p("2026-09-14", 123) + "manifest.json"
    assert snapshot_prefix_from_key(good_key) == p("2026-09-14", 123)
    assert run_id(p("2026-09-14", 123)) == 123
    with pytest.raises(RuntimeError):
        run_id("canslim/candidates/snapshots/2026-09-14/manual/")
    with pytest.raises(RuntimeError):
        snapshot_prefix_from_key("other/prefix/file.json")
