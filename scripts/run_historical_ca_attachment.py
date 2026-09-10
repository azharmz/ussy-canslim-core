from __future__ import annotations

import io
import json
import os
import sys
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo

import boto3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from canslim_research.labels import a_label, c_label  # noqa: E402
from run_e1_e4_static_trade_diagnostics import generate_candidates  # noqa: E402
from run_e0_static_history_candidates import s3_client  # noqa: E402

OUT = ROOT / "results" / "historical-ca-attachment-v1"
ET = ZoneInfo("America/New_York")
READY = {"PASS_FULL", "PASS_3Y_FALLBACK"}


def read_bytes(s3, bucket: str, key: str) -> bytes:
    return s3.get_object(Bucket=bucket, Key=key)["Body"].read()


def read_json(s3, bucket: str, key: str) -> dict:
    return json.loads(read_bytes(s3, bucket, key))


def cutoff_utc(signal_date) -> pd.Timestamp:
    d = pd.Timestamp(signal_date).date()
    return pd.Timestamp(d.year, d.month, d.day, 16, 0, tz=ET).tz_convert("UTC")


def scalar(row, name):
    v = row.get(name)
    return None if pd.isna(v) else float(v)


def normalize_cik(v) -> str | None:
    if pd.isna(v):
        return None
    s = str(v).strip()
    if s.endswith(".0"):
        s = s[:-2]
    digits = "".join(ch for ch in s if ch.isdigit())
    return digits.zfill(10) if digits else None


def latest_quarter_asof(q: pd.DataFrame, cutoff: pd.Timestamp):
    x = q.loc[q["accepted_at"].le(cutoff)].copy()
    if x.empty:
        return None
    latest_period = x["fiscal_period_end"].max()
    x = x.loc[x["fiscal_period_end"].eq(latest_period)].sort_values("accepted_at")
    return x.iloc[-1] if len(x) else None


def annual_growths_asof(a: pd.DataFrame, cutoff: pd.Timestamp):
    x = a.loc[a["accepted_at"].le(cutoff)].copy()
    if x.empty:
        return [], []
    x = x.sort_values(["fy_num", "accepted_at"]).groupby("fy_num", as_index=False).tail(1)
    x = x.sort_values("fy_num")
    latest = x.tail(3)
    years = latest["fy_num"].astype(int).tolist()
    growths = [scalar(r, "annual_eps_growth") for _, r in latest.iterrows()]
    return years, growths


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = s3_client()
    bucket = os.environ["R2_BUCKET_NAME"]

    candidates, membership, spy_pointer = generate_candidates(s3, bucket)
    candidates = candidates.copy()
    candidates["signal_date"] = pd.to_datetime(candidates["date"], errors="coerce").dt.normalize()
    candidates["signal_cutoff_utc"] = candidates["signal_date"].map(cutoff_utc)

    pointer = read_json(s3, bucket, "fundamentals/current.json")
    manifest = read_json(s3, bucket, pointer["manifest_key"])
    art = manifest["artifacts"]
    wide = pd.read_parquet(io.BytesIO(read_bytes(s3, bucket, art["fundamentals_point_in_time.parquet"]["key"])))
    bridge = pd.read_csv(io.BytesIO(read_bytes(s3, bucket, art["current_universe.csv"]["key"])), dtype=str)
    report = pd.read_csv(io.BytesIO(read_bytes(s3, bucket, art["fundamentals_final_production_report.csv"]["key"])), dtype=str)

    wide["accepted_at"] = pd.to_datetime(wide["accepted_at"], errors="coerce", utc=True)
    wide["fiscal_period_end"] = pd.to_datetime(wide["fiscal_period_end"], errors="coerce")
    wide["cik_norm"] = wide["cik"].map(normalize_cik)
    if "fy" in wide.columns:
        wide["fy_num"] = pd.to_numeric(wide["fy"], errors="coerce")
    elif "fiscal_year" in wide.columns:
        wide["fy_num"] = pd.to_numeric(wide["fiscal_year"], errors="coerce")
    else:
        raise RuntimeError("No FY column in fundamentals PIT")

    sid_col = "security_id"
    symbol_col = "symbol" if "symbol" in bridge.columns else "ticker"
    bridge2 = bridge[[sid_col, symbol_col]].dropna().drop_duplicates(sid_col).rename(columns={symbol_col: "bridge_symbol"})
    report_symbol = "symbol" if "symbol" in report.columns else "ticker"
    status_col = "production_status" if "production_status" in report.columns else "status"
    report2 = report[[report_symbol, "cik", status_col]].dropna(subset=[report_symbol]).drop_duplicates(report_symbol, keep="last")
    report2 = report2.rename(columns={report_symbol: "bridge_symbol", status_col: "production_status"})
    report2["cik_norm"] = report2["cik"].map(normalize_cik)
    identity = bridge2.merge(report2[["bridge_symbol", "cik_norm", "production_status"]], on="bridge_symbol", how="left")
    candidates[sid_col] = candidates[sid_col].astype(str)
    identity[sid_col] = identity[sid_col].astype(str)
    candidates = candidates.merge(identity, on=sid_col, how="left", validate="many_to_one")

    quarterly_mask = wide[["quarterly_eps", "quarterly_revenue", "quarterly_eps_yoy", "quarterly_revenue_yoy"]].notna().any(axis=1)
    annual_mask = wide[["annual_eps", "annual_eps_growth"]].notna().any(axis=1)
    q_by_cik = {k: g.sort_values(["fiscal_period_end", "accepted_at"]) for k, g in wide.loc[quarterly_mask & wide["cik_norm"].notna()].groupby("cik_norm")}
    a_by_cik = {k: g.dropna(subset=["fy_num"]).sort_values(["fy_num", "accepted_at"]) for k, g in wide.loc[annual_mask & wide["cik_norm"].notna()].groupby("cik_norm")}

    rows = []
    leakage = 0
    for r in candidates.itertuples(index=False):
        base = r._asdict()
        cik = base.get("cik_norm")
        cutoff = base["signal_cutoff_utc"]
        ready = base.get("production_status") in READY
        qrow = latest_quarter_asof(q_by_cik.get(cik, pd.DataFrame(columns=wide.columns)), cutoff) if cik else None
        years, growths = annual_growths_asof(a_by_cik.get(cik, pd.DataFrame(columns=wide.columns)), cutoff) if cik else ([], [])

        if qrow is None:
            c = c_label(None, None, data_ready=False if not ready else True)
            q_acc = q_end = None
            eps_yoy = rev_yoy = None
        else:
            eps_yoy = scalar(qrow, "quarterly_eps_yoy")
            rev_yoy = scalar(qrow, "quarterly_revenue_yoy")
            c = c_label(eps_yoy, rev_yoy, data_ready=ready)
            q_acc = qrow["accepted_at"]
            q_end = qrow["fiscal_period_end"]
            if q_acc > cutoff:
                leakage += 1

        fallback = base.get("production_status") == "PASS_3Y_FALLBACK"
        a = a_label(growths, data_ready=ready, fallback_3y=fallback)
        annual_used = a_by_cik.get(cik, pd.DataFrame())
        max_a_acc = None
        if cik and len(years) and not annual_used.empty:
            tmp = annual_used.loc[annual_used["accepted_at"].le(cutoff) & annual_used["fy_num"].isin(years)]
            if not tmp.empty:
                max_a_acc = tmp["accepted_at"].max()
                if max_a_acc > cutoff:
                    leakage += 1

        rows.append({
            "security_id": base[sid_col], "ticker": base.get("ticker"), "signal_date": base["signal_date"],
            "signal_cutoff_utc": cutoff, "pivot": base.get("pivot"), "bridge_symbol": base.get("bridge_symbol"),
            "cik": cik, "production_status": base.get("production_status"),
            "c_state": c.state, "c_reason": c.reason, "c_pass": c.value,
            "c_quarter_end": q_end, "c_source_accepted_at": q_acc,
            "quarterly_eps_yoy": eps_yoy, "quarterly_revenue_yoy": rev_yoy,
            "a_state": a.state, "a_reason": a.reason, "a_pass": a.value,
            "a_fiscal_years": ",".join(map(str, years)), "a_growths": json.dumps(growths),
            "a_max_source_accepted_at": max_a_acc,
        })

    out = pd.DataFrame(rows)
    out["ca_state"] = out.apply(lambda x: "PASS" if x.c_state == "PASS" and x.a_state == "PASS" else ("NOT_EVALUABLE" if "NOT_EVALUABLE" in {x.c_state, x.a_state} else "FAIL"), axis=1)
    out.to_csv(OUT / "candidate_ca_labels.csv", index=False)

    dist_c = Counter(out["c_state"])
    dist_a = Counter(out["a_state"])
    dist_ca = Counter(out["ca_state"])
    summary = {
        "experiment": "HISTORICAL_CA_ATTACHMENT_V1",
        "candidate_count": int(len(out)),
        "candidate_symbols": int(out["security_id"].nunique()),
        "fundamentals_manifest_key": pointer["manifest_key"],
        "fundamentals_source_run_id": pointer.get("source_run_id"),
        "c_distribution": dict(dist_c), "a_distribution": dict(dist_a), "ca_distribution": dict(dist_ca),
        "identity_missing_cik_rows": int(out["cik"].isna().sum()),
        "critical_future_accepted_at_violations": int(leakage),
        "cutoff": "16:00 America/New_York on signal T0, DST-aware",
        "quarter_selection": "latest fiscal_period_end known by cutoff; latest accepted state within that period",
        "annual_selection": "latest accepted state per FY known by cutoff; latest three FY",
        "thresholds_changed": False,
        "performance_metrics_computed": False,
        "research_universe": "CURRENT_COMPLIANT_UNIVERSE_FROZEN_AT_2026_08_28",
        "spy_parquet_key": spy_pointer.get("parquet_key"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))
    (OUT / "fundamentals_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    (OUT / "membership_snapshot.json").write_text(json.dumps(membership, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    if leakage:
        raise RuntimeError(f"PIT leakage invariant failed: {leakage} future accepted_at uses")


if __name__ == "__main__":
    main()
