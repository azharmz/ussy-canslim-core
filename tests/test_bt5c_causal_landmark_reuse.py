from __future__ import annotations

import pandas as pd
import pytest

from bt5c_causal_landmark_reuse import (
    ReuseInvariantError,
    assert_exact_causal_prefix,
    source_identity,
)


def frame(dates):
    return pd.DataFrame({"date": pd.to_datetime(dates), "close": range(len(dates))})


def test_exact_prefix_is_accepted():
    full = frame(["2024-01-02", "2024-01-03", "2024-01-04"])
    assert_exact_causal_prefix(source_identity(full), full.iloc[:2].copy())


def test_non_prefix_fails_closed():
    full = frame(["2024-01-02", "2024-01-03", "2024-01-04"])
    bad = frame(["2024-01-02", "2024-01-04"])
    with pytest.raises(ReuseInvariantError, match="BT5C_REUSE_GUARD_NOT_PREFIX"):
        assert_exact_causal_prefix(source_identity(full), bad)


def test_duplicate_source_fails_closed():
    bad = frame(["2024-01-02", "2024-01-02"])
    with pytest.raises(ReuseInvariantError, match="BT5C_REUSE_GUARD_SOURCE_ORDER"):
        source_identity(bad)
