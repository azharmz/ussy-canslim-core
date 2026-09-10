from __future__ import annotations

import io
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from canslim_research.execution import entry_decision, resolve_bar_exit  # noqa: E402
from run_e1_e4_static_trade_diagnostics import generate_candidates  # noqa: E402
from run_e0_static_history_candidates import read_bytes, s3_client  # noqa: E402

OUT = ROOT / "results" / "post-breakout-exhaustion-v1"


def load_history(s3, bucket: str, sid: str) -> pd.DataFrame:
    payload = read_bytes(s3, bucket, f"backtest/ohlcv/{sid}.parquet")
    g = pd.read_parquet(io.BytesIO(payload))[["date", "open", "high", "low", "close"]].copy()
    g["date"] = pd.to_datetime(g["date"], errors="coerce").dt.normalize()
    return g.dropna(subset=["date"]).drop_duplicates("date", keep="last").sort_values("date").reset_index(drop=True)


def pf(x: pd.Series) -> float | None:
    s = pd.to_numeric(x, errors="coerce").dropna()
    gp = float(s[s > 0].sum())
    gl = float(-s[s < 0].sum())
    return gp / gl if gl > 0 else None


def simulate_x1(entry_idx: int, pivot: float, history: pd.DataFrame):
    op = float(history.iloc[entry_idx].open)
    d = entry_decision(pivot=pivot, h1_open=op)
    if not d.accepted:
        return None
    entry = float(d.entry_price)
    stop = float(d.hard_stop)
    target = float(d.profit_target)
    max_high = entry
    min_low = entry
    for j in range(entry_idx, len(history)):
        b = history.iloc[j]
        ex = resolve_bar_exit(open_price=float(b.open), high=float(b.high), low=float(b.low), hard_stop=stop, profit_target=target)
        if ex.exited:
            return {
                "realized_return": float(ex.exit_price) / entry - 1.0,
                "exit_reason": ex.reason,
                "pre_exit_mfe": max_high / entry - 1.0,
                "pre_exit_mae": min_low / entry - 1.0,
            }
        max_high = max(max_high, float(b.high))
        min_low = min(min_low, float(b.low))
    return {"realized_return": None, "exit_reason": "CENSORED_OPEN", "pre_exit_mfe": max_high / entry - 1.0, "pre_exit_mae": min_low / entry - 1.0}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = s3_client()
    bucket = os.environ["R2_BUCKET_NAME"]
    candidates, membership, spy_pointer = generate_candidates(s3, bucket)

    ids = [str(x) for x in candidates.security_id.unique()]
    histories = {}
    with ThreadPoolExecutor(max_workers=16) as pool:
        futs = {pool.submit(load_history, s3, bucket, sid): sid for sid in ids}
        for fut in as_completed(futs):
            histories[futs[fut]] = fut.result()

    rows = []
    for sid, g in candidates.groupby("security_id"):
        h = histories[str(sid)]
        idxmap = {d: i for i, d in enumerate(h.date)}
        for r in g.itertuples(index=False):
            t0 = pd.Timestamp(r.date).normalize()
            i = idxmap.get(t0)
            if i is None or i < 1 or i + 3 >= len(h):
                continue
            tminus1 = h.iloc[i - 1]
            b0 = h.iloc[i]
            b1, b2, b3 = h.iloc[i + 1], h.iloc[i + 2], h.iloc[i + 3]
            shock = float(b0.close) / float(tminus1.close) - 1.0
            t1_gap = float(b1.open) / float(b0.close) - 1.0
            t1_oc = float(b1.close) / float(b1.open) - 1.0
            t1_vs_t0 = float(b1.close) / float(b0.close) - 1.0
            t2_vs_t0 = float(b2.close) / float(b0.close) - 1.0
            t3_vs_t0 = float(b3.close) / float(b0.close) - 1.0
            min_close_t1_t3 = min(float(b1.close), float(b2.close), float(b3.close))
            pivot = float(r.pivot)
            x1 = simulate_x1(i + 1, pivot, h)
            rows.append({
                "security_id": sid,
                "ticker": r.ticker,
                "signal_date": t0,
                "pivot": pivot,
                "shock_tminus1_t0": shock,
                "t1_gap": t1_gap,
                "t1_open_close": t1_oc,
                "t1_close_vs_t0": t1_vs_t0,
                "t2_close_vs_t0": t2_vs_t0,
                "t3_close_vs_t0": t3_vs_t0,
                "t1_bearish": bool(float(b1.close) < float(b1.open)),
                "t1_below_t0_close": bool(float(b1.close) < float(b0.close)),
                "retest_pivot_by_t3": bool(min_close_t1_t3 <= pivot * 1.01),
                "breakdown_below_pivot_by_t3": bool(min_close_t1_t3 < pivot),
                "x1_entry_valid": x1 is not None,
                "x1_realized_return": None if x1 is None else x1["realized_return"],
                "x1_exit_reason": None if x1 is None else x1["exit_reason"],
                "x1_pre_exit_mfe": None if x1 is None else x1["pre_exit_mfe"],
                "x1_pre_exit_mae": None if x1 is None else x1["pre_exit_mae"],
            })

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "candidate_exhaustion_features.csv", index=False)

    # Descriptive shock deciles; no cutoff is declared from these results.
    d = df[df.shock_tminus1_t0.notna()].copy()
    d["shock_decile"] = pd.qcut(d.shock_tminus1_t0, 10, duplicates="drop")
    dec = []
    for bucket, g in d.groupby("shock_decile", observed=True):
        x = g[g.x1_entry_valid]
        dec.append({
            "shock_bucket": str(bucket),
            "n_candidates": int(len(g)),
            "median_shock": float(g.shock_tminus1_t0.median()),
            "t1_bearish_rate": float(g.t1_bearish.mean()),
            "t1_below_t0_close_rate": float(g.t1_below_t0_close.mean()),
            "retest_pivot_by_t3_rate": float(g.retest_pivot_by_t3.mean()),
            "breakdown_below_pivot_by_t3_rate": float(g.breakdown_below_pivot_by_t3.mean()),
            "x1_valid_rate": float(g.x1_entry_valid.mean()),
            "x1_pf": pf(x.x1_realized_return),
            "x1_stop_rate": float(x.x1_exit_reason.astype(str).str.contains("STOP").mean()) if len(x) else None,
            "x1_target_rate": float(x.x1_exit_reason.astype(str).str.contains("TARGET").mean()) if len(x) else None,
            "median_x1_mfe": float(pd.to_numeric(x.x1_pre_exit_mfe, errors="coerce").median()) if len(x) else None,
            "median_x1_mae": float(pd.to_numeric(x.x1_pre_exit_mae, errors="coerce").median()) if len(x) else None,
        })
    dec_df = pd.DataFrame(dec)
    dec_df.to_csv(OUT / "shock_deciles.csv", index=False)

    # Interaction: shock quintile x T1 rejection state.
    q = df[df.shock_tminus1_t0.notna()].copy()
    q["shock_quintile"] = pd.qcut(q.shock_tminus1_t0, 5, labels=["Q1","Q2","Q3","Q4","Q5"], duplicates="drop")
    q["t1_rejection_state"] = np.select(
        [q.t1_bearish & q.t1_below_t0_close, q.t1_bearish, q.t1_below_t0_close],
        ["BEARISH_AND_BELOW_T0", "BEARISH_ONLY", "BELOW_T0_ONLY"],
        default="NO_REJECTION",
    )
    inter = []
    for (sq, state), g in q.groupby(["shock_quintile", "t1_rejection_state"], observed=True):
        x = g[g.x1_entry_valid]
        inter.append({
            "shock_quintile": str(sq),
            "t1_rejection_state": state,
            "n_candidates": int(len(g)),
            "retest_pivot_by_t3_rate": float(g.retest_pivot_by_t3.mean()),
            "breakdown_below_pivot_by_t3_rate": float(g.breakdown_below_pivot_by_t3.mean()),
            "x1_valid_n": int(len(x)),
            "x1_pf": pf(x.x1_realized_return),
            "x1_stop_rate": float(x.x1_exit_reason.astype(str).str.contains("STOP").mean()) if len(x) else None,
            "x1_target_rate": float(x.x1_exit_reason.astype(str).str.contains("TARGET").mean()) if len(x) else None,
        })
    pd.DataFrame(inter).to_csv(OUT / "shock_x_t1_rejection.csv", index=False)

    top = d.nlargest(max(1, len(d)//10), "shock_tminus1_t0")
    bottom = d.nsmallest(max(1, len(d)//10), "shock_tminus1_t0")
    summary = {
        "experiment": "POST_BREAKOUT_EXHAUSTION_V1",
        "candidate_count": int(len(df)),
        "candidate_symbols": int(df.security_id.nunique()),
        "research_universe": "CURRENT_COMPLIANT_UNIVERSE_FROZEN_AT_2026_08_28",
        "no_threshold_tuning": True,
        "top_shock_decile": {
            "median_shock": float(top.shock_tminus1_t0.median()),
            "t1_bearish_rate": float(top.t1_bearish.mean()),
            "t1_below_t0_close_rate": float(top.t1_below_t0_close.mean()),
            "retest_pivot_by_t3_rate": float(top.retest_pivot_by_t3.mean()),
            "breakdown_below_pivot_by_t3_rate": float(top.breakdown_below_pivot_by_t3.mean()),
            "x1_pf": pf(top[top.x1_entry_valid].x1_realized_return),
        },
        "bottom_shock_decile": {
            "median_shock": float(bottom.shock_tminus1_t0.median()),
            "t1_bearish_rate": float(bottom.t1_bearish.mean()),
            "t1_below_t0_close_rate": float(bottom.t1_below_t0_close.mean()),
            "retest_pivot_by_t3_rate": float(bottom.retest_pivot_by_t3.mean()),
            "breakdown_below_pivot_by_t3_rate": float(bottom.breakdown_below_pivot_by_t3.mean()),
            "x1_pf": pf(bottom[bottom.x1_entry_valid].x1_realized_return),
        },
        "interpretation_rule": "Use only to test whether extreme T-1->T0 expansion followed by T+1 rejection is associated with near-term retracement/exhaustion. Do not derive a hard momentum cutoff from this same sample.",
        "spy_parquet_key": spy_pointer.get("parquet_key"),
        "spy_sha256": spy_pointer.get("sha256"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))
    (OUT / "membership_snapshot.json").write_text(json.dumps(membership, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
