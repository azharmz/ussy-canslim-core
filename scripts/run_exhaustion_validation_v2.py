from __future__ import annotations

import io
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from run_e0_static_history_candidates import read_bytes, s3_client  # noqa: E402
from run_e1_e4_static_trade_diagnostics import generate_candidates  # noqa: E402

OUT = ROOT / "results" / "exhaustion-validation-v2"
BOUNDARY = pd.Timestamp("2026-09-11")
EXTREME_SHOCK = 0.0533333333333332
MIN_GROUP_N = 50


def load_history(s3, bucket: str, sid: str) -> pd.DataFrame:
    payload = read_bytes(s3, bucket, f"backtest/ohlcv/{sid}.parquet")
    g = pd.read_parquet(io.BytesIO(payload))[["date", "open", "high", "low", "close"]].copy()
    g["date"] = pd.to_datetime(g["date"], errors="coerce").dt.normalize()
    return g.dropna(subset=["date"]).drop_duplicates("date", keep="last").sort_values("date").reset_index(drop=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for p in OUT.iterdir():
        if p.is_file():
            p.unlink()

    s3 = s3_client()
    bucket = os.environ["R2_BUCKET_NAME"]
    candidates, membership, spy_pointer = generate_candidates(s3, bucket)
    candidates = candidates.copy()
    candidates["date"] = pd.to_datetime(candidates["date"], errors="coerce").dt.normalize()
    forward = candidates[candidates["date"] > BOUNDARY].copy()
    forward["security_id"] = forward["security_id"].astype(str)

    ids = sorted(forward["security_id"].unique().tolist()) if len(forward) else []
    histories: dict[str, pd.DataFrame] = {}
    failures = []
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = {pool.submit(load_history, s3, bucket, sid): sid for sid in ids}
        for fut in as_completed(futures):
            sid = futures[fut]
            try:
                histories[sid] = fut.result()
            except Exception as exc:
                failures.append({"security_id": sid, "error": str(exc)[:300]})
    if failures:
        raise RuntimeError(f"EXH2 history load failures: {failures[:5]}")

    rows = []
    for r in forward.itertuples(index=False):
        h = histories[str(r.security_id)]
        idxmap = {d: i for i, d in enumerate(h.date)}
        t0 = pd.Timestamp(r.date).normalize()
        i = idxmap.get(t0)
        shock = float(r.tminus1_to_t0)
        base = {
            "signal_date": t0.date().isoformat(),
            "security_id": str(r.security_id),
            "ticker": r.ticker,
            "pivot": float(r.pivot),
            "shock_tminus1_t0": shock,
            "extreme_shock": bool(shock >= EXTREME_SHOCK),
        }
        if i is None or i + 3 >= len(h):
            rows.append({**base, "mature": False})
            continue
        b0, b1, b2, b3 = h.iloc[i], h.iloc[i + 1], h.iloc[i + 2], h.iloc[i + 3]
        t1_bearish = float(b1.close) < float(b1.open)
        t1_below = float(b1.close) < float(b0.close)
        min_close = min(float(b1.close), float(b2.close), float(b3.close))
        rows.append({
            **base,
            "mature": True,
            "t1_bearish": bool(t1_bearish),
            "t1_below_t0_close": bool(t1_below),
            "t1_rejection": bool(t1_bearish and t1_below),
            "retest_pivot_by_t3": bool(min_close <= float(r.pivot) * 1.01),
            "breakdown_below_pivot_by_t3": bool(min_close < float(r.pivot)),
            "t3_close_vs_t0": float(b3.close) / float(b0.close) - 1.0,
        })

    obs = pd.DataFrame(rows)
    obs.to_csv(OUT / "observations.csv", index=False)

    mature = obs[(obs.get("mature", False) == True) & (obs.get("extreme_shock", False) == True)].copy() if len(obs) else pd.DataFrame()
    groups = []
    for rejection in (True, False):
        g = mature[mature["t1_rejection"] == rejection] if len(mature) else pd.DataFrame()
        groups.append({
            "group": "EXTREME_REJECTED" if rejection else "EXTREME_NOT_REJECTED",
            "n": int(len(g)),
            "breakdown_below_pivot_by_t3_rate": float(g["breakdown_below_pivot_by_t3"].mean()) if len(g) else None,
            "retest_pivot_by_t3_rate": float(g["retest_pivot_by_t3"].mean()) if len(g) else None,
            "median_t3_close_vs_t0": float(g["t3_close_vs_t0"].median()) if len(g) else None,
        })
    group_df = pd.DataFrame(groups)
    group_df.to_csv(OUT / "group_summary.csv", index=False)

    rejected_n = int(group_df.loc[group_df.group == "EXTREME_REJECTED", "n"].iloc[0])
    control_n = int(group_df.loc[group_df.group == "EXTREME_NOT_REJECTED", "n"].iloc[0])
    gate_pass = rejected_n >= MIN_GROUP_N and control_n >= MIN_GROUP_N
    summary = {
        "experiment": "EXH2_PROSPECTIVE_EXHAUSTION_VALIDATION",
        "methodology": "docs/methodology/exhaustion-validation-v2.md",
        "preregistered_boundary_exclusive": str(BOUNDARY.date()),
        "extreme_shock_cutoff": EXTREME_SHOCK,
        "source_discovery_run": "34466747136",
        "candidate_count_post_boundary": int(len(obs)),
        "mature_candidate_count": int(obs["mature"].sum()) if len(obs) else 0,
        "mature_extreme_shock_count": int(len(mature)),
        "rejected_extreme_mature_n": rejected_n,
        "non_rejected_extreme_mature_n": control_n,
        "minimum_each_group": MIN_GROUP_N,
        "status": "REVIEW_ELIGIBLE" if gate_pass else "ACCUMULATING",
        "review_eligible": bool(gate_pass),
        "primary_endpoint": "breakdown_below_pivot_by_t3_rate",
        "directional_hypothesis": "EXTREME_REJECTED rate > EXTREME_NOT_REJECTED rate",
        "fwd1_modified": False,
        "spy_parquet_key": spy_pointer.get("parquet_key"),
        "spy_sha256": spy_pointer.get("sha256"),
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "guardrail": "Diagnostic only. T+1 rejection is not available at T+1 open and cannot modify frozen FWD1 execution.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (OUT / "membership_snapshot.json").write_text(json.dumps(membership, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
