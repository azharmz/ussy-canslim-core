"""Bounded CI verification for #34 without changing frozen #33 semantics.

The wrapper limits only the number of securities sent through canonical #33
morphology so CI can verify plumbing quickly. The parent smoke module still loads
full ready OHLCV for cross-sectional RS and the same PIT fundamental/benchmark
contracts. This is verification infrastructure, not a production sampling rule.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_candidate_v2_smoke as smoke  # noqa: E402
from oneil_patterns.data.r2_ready import ReadyDataset, load_ready_asof  # noqa: E402
from oneil_patterns.production.runner import run_ready_dataset  # noqa: E402


def bounded_run_from_r2(s3, *, bucket, asof_date, analyze_security):
    dataset = load_ready_asof(s3, bucket, asof_date)
    max_securities = int(os.getenv("CANDIDATE_V2_SMOKE_SECURITIES", "100"))
    ids = sorted(dataset.frame["security_id"].astype(str).unique())[:max_securities]
    frame = dataset.frame[dataset.frame["security_id"].astype(str).isin(ids)].copy()
    bounded = ReadyDataset(frame=frame, manifest=dataset.manifest)
    return run_ready_dataset(bounded, asof_date=asof_date, analyze_security=analyze_security)


if __name__ == "__main__":
    smoke.run_from_r2 = bounded_run_from_r2
    smoke.main()
