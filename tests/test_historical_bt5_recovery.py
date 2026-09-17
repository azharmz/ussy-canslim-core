from __future__ import annotations

import pandas as pd
import pytest

from bt5c_authorized_reuse import SourceIdentity, assert_exact_causal_prefix
from historical_bt5_checkpoint import ReplayLineage, make_checkpoint, validate_checkpoint


def frame(n=6):
    return pd.DataFrame({
        "date": pd.date_range("2020-01-01", periods=n, freq="D"),
        "open": range(1, n + 1), "high": range(2, n + 2), "low": range(n),
        "close": range(1, n + 1), "volume": [100] * n,
    })


def test_exact_prefix_accepted():
    full = frame()
    source = SourceIdentity.from_frame(full)
    assert len(assert_exact_causal_prefix(source, full.iloc[:4])) == 4


def test_non_prefix_rejected():
    full = frame(); source = SourceIdentity.from_frame(full)
    bad = full.iloc[:4].copy(); bad.loc[1, "date"] = pd.Timestamp("2020-02-01")
    with pytest.raises(RuntimeError, match="BT5C_REUSE_GUARD_NOT_PREFIX"):
        assert_exact_causal_prefix(source, bad)


def test_checkpoint_roundtrip_and_lineage_mismatch():
    lineage = ReplayLineage("bt5-test", "abc", "inventory", "config")
    cp = make_checkpoint(lineage=lineage, completed_work_units=["A"], output_parts=[])
    validate_checkpoint(cp, lineage)
    other = ReplayLineage("bt5-test", "different", "inventory", "config")
    with pytest.raises(RuntimeError, match="BT5_CHECKPOINT_LINEAGE_MISMATCH"):
        validate_checkpoint(cp, other)
