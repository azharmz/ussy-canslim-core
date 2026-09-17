from __future__ import annotations

import io
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import boto3
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from canslim_research.execution import entry_decision, resolve_bar_exit  # noqa: E402
from canslim_research.technical import (  # noqa: E402
    BASE_DEPTH_MAX,
    BUY_ZONE_MAX,
    PRICE_FLOOR,
    RS_PERCENTILE_MIN,
    VOLUME_RATIO_MIN,
)
from run_e0_static_history_candidates import (  # noqa: E402
    MEMBERSHIP_KEY,
    OHLCV_PREFIX,
    SPY_POINTER,
    build_spy_market_state,
    list_keys,
    load_security,
    ohlcv_key,
    read_bytes,
    read_json,
    s3_client,
    verify,
)

OUT = ROOT / "results" / "e1-e4-static-trade-diagnostics-v1"


def load_full_history(s3, bucket: str, security_id: str) -> pd.DataFrame:
    payload = read_bytes(s3, bucket, ohlcv_key(security_id))
    g = pd.read_parquet(io.BytesIO(payload))
    required = ["date", "open", "high", "low", "close"]
    missing = set(required) - set(g.columns)
    if missing:
        raise RuntimeError(f"{security_id} missing {sorted(missing)}")
    g = g[required].copy()
    g["date"] = pd.to_datetime(g["date"], errors="coerce").dt.normalize()
    return g.dropna(subset=["date"]).drop_duplicates("date", keep="last").sort_values("date").reset_index(drop=True)


def generate_candidates(s3, bucket: str) -> tuple[pd.DataFrame, dict, dict]:
    membership = read_json(s3, bucket, MEMBERSHIP_KEY)
    records = membership.get("records", [])
    eligible = {
        str(r["security_id"]): str(r.get("ticker") or "")
        for r in records
        if r.get("sharia_compliance") == "COMPLIANT"
    }
    available = list_keys(s3, bucket, OHLCV_PREFIX)
    selected = [(sid, ticker) for sid, ticker in eligible.items() if ohlcv_key(sid) in available]
    print(f"[historical-ohlcv] canonical_prefix={OHLCV_PREFIX} objects={len(available)} eligible={len(eligible)} selected={len(selected)}", flush=True)
    if not selected:
        raise RuntimeError(f"No pinned-universe OHLCV objects found under canonical prefix {OHLCV_PREFIX}")

    frames: list[pd.DataFrame] = []
    failures: list[dict] = []
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = {pool.submit(load_security, s3, bucket, sid, ticker): sid for sid, ticker in selected}
        for fut in as_completed(futures):
            sid = futures[fut]
            try:
                f = fut.result()
                if not f.empty:
                    frames.append(f)
            except Exception as exc:
                failures.append({"security_id": sid, "error": str(exc)[:300]})
    if failures:
        raise RuntimeError(f"Feature load failures: {failures[:5]}")
    if not frames:
        raise RuntimeError(f"No feature-evaluable historical frames under canonical prefix {OHLCV_PREFIX}")

    x = pd.concat(frames, ignore_index=True)
    x["rs_percentile"] = x.groupby("date")["rs_proxy_raw"].rank(pct=True, method="average") * 100.0

    spy_pointer = read_json(s3, bucket, SPY_POINTER)
    spy_payload = read_bytes(s3, bucket, spy_pointer["parquet_key"])
    verify(spy_payload, spy_pointer.get("sha256"), "SPY")
    market = build_spy_market_state(pd.read_parquet(io.BytesIO(spy_payload)))
    x = x.merge(market, on="date", how="left")

    x["price_pass"] = x["close"] >= PRICE_FLOOR
    x["N_pass"] = (
        x["pivot"].notna()
        & (x["base_depth"] <= BASE_DEPTH_MAX)
        & (x["close"] > x["pivot"])
        & (x["close"] <= x["pivot"] * (1.0 + BUY_ZONE_MAX))
    )
    x["S_pass"] = x["volume_ratio"] >= VOLUME_RATIO_MIN
    x["L_pass"] = x["rs_percentile"] >= RS_PERCENTILE_MIN
    x["M_pass"] = x["M_pass_spy_only"].fillna(False)
    x["technical_pass"] = x[["price_pass", "N_pass", "S_pass", "L_pass", "M_pass"]].all(axis=1)
    return x.loc[x["technical_pass"]].sort_values(["security_id", "date"]).copy(), membership, spy_pointer


def simulate_symbol(security_id: str, candidates: pd.DataFrame, history: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    date_to_idx = {d: i for i, d in enumerate(history["date"])}
    trades: list[dict] = []
    events: list[dict] = []
    active_until_idx = -1
    for row in candidates.itertuples(index=False):
        signal_date = pd.Timestamp(row.date).normalize()
        idx = date_to_idx.get(signal_date)
        base = {"date": signal_date, "security_id": security_id, "ticker": row.ticker, "pivot": float(row.pivot), "close_t0": float(row.close), "tminus1_to_t0": row.tminus1_to_t0, "h1_open": row.h1_open, "h1_gap": row.h1_gap, "t0_pivot_extension": row.t0_pivot_extension, "h1_fill_extension": row.h1_fill_extension, "rs_percentile": row.rs_percentile, "volume_ratio": row.volume_ratio}
        if idx is None or idx + 1 >= len(history):
            events.append({**base, "entry_event": "NO_H1_BAR"}); continue
        if idx + 1 <= active_until_idx:
            events.append({**base, "entry_event": "SKIP_ALREADY_OPEN"}); continue
        h1_open = float(history.iloc[idx + 1]["open"])
        dec = entry_decision(pivot=float(row.pivot), h1_open=h1_open)
        events.append({**base, "h1_open": h1_open, "h1_fill_extension": h1_open / float(row.pivot) - 1.0, "entry_event": dec.reason})
        if not dec.accepted: continue
        entry_idx = idx + 1; entry_date = history.iloc[entry_idx]["date"]; entry = float(dec.entry_price); stop = float(dec.hard_stop); target = float(dec.profit_target)
        pre_exit_max_high = entry; pre_exit_min_low = entry; exit_idx = None; exit_price = None; exit_reason = "CENSORED_OPEN"
        for j in range(entry_idx, len(history)):
            bar = history.iloc[j]
            result = resolve_bar_exit(open_price=float(bar["open"]), high=float(bar["high"]), low=float(bar["low"]), hard_stop=stop, profit_target=target)
            if result.exited:
                exit_idx = j; exit_price = float(result.exit_price); exit_reason = result.reason; break
            pre_exit_max_high = max(pre_exit_max_high, float(bar["high"])); pre_exit_min_low = min(pre_exit_min_low, float(bar["low"]))
        if exit_idx is None:
            exit_idx = len(history) - 1; exit_price = float(history.iloc[exit_idx]["close"]); realized_return = None; mark_return = exit_price / entry - 1.0
        else:
            realized_return = exit_price / entry - 1.0; mark_return = realized_return
        active_until_idx = exit_idx
        trades.append({**base, "entry_date": entry_date, "entry_price": entry, "hard_stop": stop, "profit_target": target, "exit_date": history.iloc[exit_idx]["date"], "exit_price": exit_price, "exit_reason": exit_reason, "holding_sessions": int(exit_idx-entry_idx+1), "realized_return": realized_return, "mark_return": mark_return, "pre_exit_mfe": pre_exit_max_high/entry-1.0, "pre_exit_mae": pre_exit_min_low/entry-1.0})
    return trades, events


def quantiles(series: pd.Series) -> dict[str, float | None]:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty: return {"p10": None, "p25": None, "p50": None, "p75": None, "p90": None}
    q = s.quantile([.10,.25,.50,.75,.90]); return {f"p{int(k*100)}": float(v) for k,v in q.items()}


def descriptive_by_quantile(df: pd.DataFrame, feature: str) -> list[dict]:
    x = df.loc[df[feature].notna()].copy()
    if len(x) < 4: return []
    x["bucket"] = pd.qcut(x[feature],4,duplicates="drop"); rows=[]
    for bucket,g in x.groupby("bucket",observed=True):
        realized=pd.to_numeric(g["realized_return"],errors="coerce").dropna()
        rows.append({"feature":feature,"bucket":str(bucket),"n":int(len(g)),"realized_n":int(len(realized)),"target_rate":float((g["exit_reason"].str.contains("TARGET")).mean()),"stop_rate":float((g["exit_reason"].str.contains("STOP")).mean()),"censored_rate":float((g["exit_reason"]=="CENSORED_OPEN").mean()),"median_realized_return":float(realized.median()) if len(realized) else None,"median_pre_exit_mfe":float(g["pre_exit_mfe"].median()),"median_pre_exit_mae":float(g["pre_exit_mae"].median())})
    return rows


def extension_threshold_table(events: pd.DataFrame) -> list[dict]:
    rows=[]
    for threshold in (.03,.05,.08):
        valid=pd.to_numeric(events["h1_fill_extension"],errors="coerce"); rows.append({"threshold":threshold,"candidate_events_with_h1":int(valid.notna().sum()),"within_threshold":int((valid<=threshold).sum()),"above_threshold":int((valid>threshold).sum())})
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True); s3=s3_client(); bucket=os.environ["R2_BUCKET_NAME"]
    candidates,membership,spy_pointer=generate_candidates(s3,bucket)
    trades_all=[]; events_all=[]; failures=[]; grouped={str(sid):g.copy() for sid,g in candidates.groupby("security_id")}
    print(f"[trade-diagnostics] candidate_rows={len(candidates)} symbols={len(grouped)}", flush=True)
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures={pool.submit(load_full_history,s3,bucket,sid):sid for sid in grouped}; histories={}
        for fut in as_completed(futures):
            sid=futures[fut]
            try: histories[sid]=fut.result()
            except Exception as exc: failures.append({"security_id":sid,"error":str(exc)[:300]})
    if failures: raise RuntimeError(f"History load failures: {failures[:5]}")
    for sid,g in grouped.items():
        trades,events=simulate_symbol(sid,g,histories[sid]); trades_all.extend(trades); events_all.extend(events)
    trades=pd.DataFrame(trades_all); events=pd.DataFrame(events_all); trades.to_csv(OUT/"trades.csv",index=False); events.to_csv(OUT/"entry_events.csv",index=False)
    quantile_rows=[]
    for feature in ("tminus1_to_t0","h1_gap","t0_pivot_extension","h1_fill_extension"): quantile_rows.extend(descriptive_by_quantile(trades,feature))
    pd.DataFrame(quantile_rows).to_csv(OUT/"quantile_diagnostics.csv",index=False); pd.DataFrame(extension_threshold_table(events)).to_csv(OUT/"fill_extension_3_5_8.csv",index=False)
    realized=pd.to_numeric(trades.get("realized_return"),errors="coerce").dropna() if len(trades) else pd.Series(dtype=float); gross_profit=float(realized[realized>0].sum()) if len(realized) else 0.; gross_loss=float(-realized[realized<0].sum()) if len(realized) else 0.; pf=gross_profit/gross_loss if gross_loss>0 else None
    event_counts={str(k):int(v) for k,v in events["entry_event"].value_counts().to_dict().items()} if len(events) else {}; exit_counts={str(k):int(v) for k,v in trades["exit_reason"].value_counts().to_dict().items()} if len(trades) else {}
    summary={"experiment":"E1-E4-STATIC-TRADE-DIAGNOSTICS-V1","evidence_class":"STATIC_2026_08_28_UNIVERSE_EXPLORATORY_NOT_PIT_UNIVERSE","membership_key":MEMBERSHIP_KEY,"ohlcv_prefix":OHLCV_PREFIX,"candidate_events":int(len(candidates)),"candidate_symbols":int(candidates["security_id"].nunique()),"entry_event_counts":event_counts,"accepted_trade_count":int(len(trades)),"exit_counts":exit_counts,"realized_trade_count":int(len(realized)),"censored_open_count":int((trades["exit_reason"]=="CENSORED_OPEN").sum()) if len(trades) else 0,"descriptive_trade_level_pf":pf,"median_realized_return":float(realized.median()) if len(realized) else None,"median_pre_exit_mfe":float(trades["pre_exit_mfe"].median()) if len(trades) else None,"median_pre_exit_mae":float(trades["pre_exit_mae"].median()) if len(trades) else None,"feature_quantiles_all_candidates":{"tminus1_to_t0":quantiles(events["tminus1_to_t0"]),"h1_gap":quantiles(events["h1_gap"]),"t0_pivot_extension":quantiles(events["t0_pivot_extension"]),"h1_fill_extension":quantiles(events["h1_fill_extension"])},"pre_specified_fill_extension_counts":extension_threshold_table(events),"market_proxy_scope":"SPY_ONLY","execution_baseline":"X1_7PCT_STOP_20PCT_PIVOT_TARGET","portfolio_metrics_computed":False,"allowed_use":"E1-E4 exploratory mechanism diagnostics only. Do not tune thresholds or infer unbiased strategy performance.","survivorship_warning":"2026-08-28 membership is held fixed across historical dates; historical eligibility is not PIT.","spy_parquet_key":spy_pointer.get("parquet_key"),"spy_sha256":spy_pointer.get("sha256")}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)); (OUT/"membership_snapshot.json").write_text(json.dumps(membership,indent=2,sort_keys=True)); print(json.dumps(summary,indent=2,sort_keys=True),flush=True)


if __name__ == "__main__": main()
