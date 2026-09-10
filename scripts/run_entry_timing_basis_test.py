from __future__ import annotations

import io
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from canslim_research.entry_timing import x1_immediate, x2_first_valid, x3_pivot_hold, x4_retest_hold  # noqa: E402
from canslim_research.execution import HARD_STOP_LOSS, PROFIT_TARGET_FROM_PIVOT, resolve_bar_exit  # noqa: E402
from run_e1_e4_static_trade_diagnostics import generate_candidates  # noqa: E402
from run_e0_static_history_candidates import read_bytes, s3_client  # noqa: E402

OUT = ROOT / "results" / "entry-timing-basis-test-v1"
VARIANTS = ("X1", "X2", "X3", "X4")


def load_history(s3, bucket: str, security_id: str) -> pd.DataFrame:
    payload = read_bytes(s3, bucket, f"backtest/ohlcv/{security_id}.parquet")
    g = pd.read_parquet(io.BytesIO(payload))
    cols = ["date", "open", "high", "low", "close"]
    g = g[cols].copy()
    g["date"] = pd.to_datetime(g["date"], errors="coerce").dt.normalize()
    return g.dropna(subset=["date"]).drop_duplicates("date", keep="last").sort_values("date").reset_index(drop=True)


def timing_decision(variant: str, pivot: float, forward: pd.DataFrame):
    opens = forward["open"].tolist()
    lows = forward["low"].tolist()
    closes = forward["close"].tolist()
    if variant == "X1":
        return x1_immediate(pivot=pivot, opens=opens)
    if variant == "X2":
        return x2_first_valid(pivot=pivot, opens=opens)
    if variant == "X3":
        return x3_pivot_hold(pivot=pivot, opens=opens, lows=lows, closes=closes)
    if variant == "X4":
        return x4_retest_hold(pivot=pivot, opens=opens, lows=lows, closes=closes)
    raise ValueError(variant)


def simulate_variant(variant: str, candidates: pd.DataFrame, histories: dict[str, pd.DataFrame]):
    trades, events = [], []
    for sid, g in candidates.groupby("security_id"):
        history = histories[str(sid)]
        date_to_idx = {d: i for i, d in enumerate(history["date"])}
        active_until = -1
        for row in g.sort_values("date").itertuples(index=False):
            signal_date = pd.Timestamp(row.date).normalize()
            idx = date_to_idx.get(signal_date)
            base = {"variant": variant, "security_id": sid, "ticker": row.ticker, "signal_date": signal_date, "pivot": float(row.pivot)}
            if idx is None or idx + 1 >= len(history):
                events.append({**base, "event": "NO_FORWARD_BAR"})
                continue
            if idx + 1 <= active_until:
                events.append({**base, "event": "SKIP_ALREADY_OPEN"})
                continue
            forward = history.iloc[idx + 1: idx + 4].reset_index(drop=True)
            d = timing_decision(variant, float(row.pivot), forward)
            events.append({**base, "event": d.reason, "entry_offset": d.entry_offset, "confirmation_offset": d.confirmation_offset, "entry_price": d.entry_price})
            if not d.accepted:
                continue
            entry_idx = idx + int(d.entry_offset)
            entry = float(d.entry_price)
            stop = entry * (1.0 - HARD_STOP_LOSS)
            target = float(row.pivot) * (1.0 + PROFIT_TARGET_FROM_PIVOT)
            max_high = entry
            min_low = entry
            exit_idx = None
            exit_price = None
            exit_reason = "CENSORED_OPEN"
            for j in range(entry_idx, len(history)):
                bar = history.iloc[j]
                ex = resolve_bar_exit(open_price=float(bar.open), high=float(bar.high), low=float(bar.low), hard_stop=stop, profit_target=target)
                if ex.exited:
                    exit_idx, exit_price, exit_reason = j, float(ex.exit_price), ex.reason
                    break
                max_high = max(max_high, float(bar.high))
                min_low = min(min_low, float(bar.low))
            if exit_idx is None:
                exit_idx = len(history) - 1
                exit_price = float(history.iloc[exit_idx].close)
                realized = None
            else:
                realized = exit_price / entry - 1.0
            active_until = exit_idx
            trades.append({
                **base,
                "entry_offset": int(d.entry_offset),
                "confirmation_offset": d.confirmation_offset,
                "entry_date": history.iloc[entry_idx].date,
                "entry_price": entry,
                "entry_extension": entry / float(row.pivot) - 1.0,
                "exit_date": history.iloc[exit_idx].date,
                "exit_price": exit_price,
                "exit_reason": exit_reason,
                "realized_return": realized,
                "pre_exit_mfe": max_high / entry - 1.0,
                "pre_exit_mae": min_low / entry - 1.0,
            })
    return pd.DataFrame(trades), pd.DataFrame(events)


def summarize(variant: str, trades: pd.DataFrame, events: pd.DataFrame, candidate_count: int) -> dict:
    realized = pd.to_numeric(trades.get("realized_return"), errors="coerce").dropna() if len(trades) else pd.Series(dtype=float)
    gp = float(realized[realized > 0].sum()) if len(realized) else 0.0
    gl = float(-realized[realized < 0].sum()) if len(realized) else 0.0
    return {
        "variant": variant,
        "candidate_count": candidate_count,
        "entry_count": int(len(trades)),
        "entry_rate": float(len(trades) / candidate_count) if candidate_count else None,
        "median_entry_offset": float(trades["entry_offset"].median()) if len(trades) else None,
        "median_entry_extension": float(trades["entry_extension"].median()) if len(trades) else None,
        "realized_trade_count": int(len(realized)),
        "descriptive_trade_level_pf": gp / gl if gl > 0 else None,
        "median_realized_return": float(realized.median()) if len(realized) else None,
        "target_rate": float(trades["exit_reason"].str.contains("TARGET").mean()) if len(trades) else None,
        "stop_rate": float(trades["exit_reason"].str.contains("STOP").mean()) if len(trades) else None,
        "median_pre_exit_mfe": float(trades["pre_exit_mfe"].median()) if len(trades) else None,
        "median_pre_exit_mae": float(trades["pre_exit_mae"].median()) if len(trades) else None,
        "event_counts": {str(k): int(v) for k, v in events["event"].value_counts().to_dict().items()},
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = s3_client()
    bucket = os.environ["R2_BUCKET_NAME"]
    candidates, membership, spy_pointer = generate_candidates(s3, bucket)
    grouped_ids = [str(x) for x in candidates["security_id"].unique()]
    histories = {}
    failures = []
    with ThreadPoolExecutor(max_workers=16) as pool:
        futs = {pool.submit(load_history, s3, bucket, sid): sid for sid in grouped_ids}
        for fut in as_completed(futs):
            sid = futs[fut]
            try:
                histories[sid] = fut.result()
            except Exception as exc:
                failures.append({"security_id": sid, "error": str(exc)[:300]})
    if failures:
        raise RuntimeError(f"History failures: {failures[:5]}")

    summaries = []
    all_trades = []
    all_events = []
    for variant in VARIANTS:
        trades, events = simulate_variant(variant, candidates, histories)
        summaries.append(summarize(variant, trades, events, len(candidates)))
        all_trades.append(trades)
        all_events.append(events)

    trades_all = pd.concat(all_trades, ignore_index=True)
    events_all = pd.concat(all_events, ignore_index=True)
    trades_all.to_csv(OUT / "trades_all_variants.csv", index=False)
    events_all.to_csv(OUT / "entry_events_all_variants.csv", index=False)
    pd.DataFrame(summaries).to_csv(OUT / "variant_summary.csv", index=False)
    summary = {
        "experiment": "ENTRY_TIMING_BASIS_TEST_V1",
        "research_universe": "CURRENT_COMPLIANT_UNIVERSE_FROZEN_AT_2026_08_28",
        "universe_interpretation": "Historical price behavior of securities compliant in the frozen current research universe; historical Musaffa status is not a strategy input in this research question.",
        "candidate_count": int(len(candidates)),
        "candidate_symbols": int(candidates["security_id"].nunique()),
        "variants": summaries,
        "common_exit_rules": {"stop_from_fill": -0.07, "target_from_pivot": 0.20, "same_bar": "stop_first", "time_stop": None},
        "causality": "Any close-based confirmation is filled no earlier than the following session open.",
        "portfolio_metrics_computed": False,
        "evidence_scope": "ENTRY_TIMING_BASIS_TEST_ON_FROZEN_CURRENT_COMPLIANT_RESEARCH_UNIVERSE",
        "warning": "Trade-level metrics are basis-test evidence, not portfolio performance. Do not tune X3/X4 parameters from these results.",
        "spy_parquet_key": spy_pointer.get("parquet_key"),
        "spy_sha256": spy_pointer.get("sha256"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))
    (OUT / "membership_snapshot.json").write_text(json.dumps(membership, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
