from __future__ import annotations

import hashlib
import io
import json
import os
import sys
from collections import Counter
from pathlib import Path

import boto3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from canslim_research.labels import LabelResult, a_label, c_label  # noqa: E402

OUT = ROOT / "results" / "historical-fundamental-screener-v1"


def log(msg: str) -> None:
    print(f"[historical-fundamental-screener] {msg}", flush=True)


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.environ["R2_ENDPOINT"],
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    )


def read_bytes(s3, bucket: str, key: str) -> bytes:
    return s3.get_object(Bucket=bucket, Key=key)["Body"].read()


def read_json(s3, bucket: str, key: str) -> dict:
    return json.loads(read_bytes(s3, bucket, key))


def normalize_cik(v) -> str | None:
    if pd.isna(v):
        return None
    s = str(v).strip()
    if s.endswith(".0"):
        s = s[:-2]
    digits = "".join(ch for ch in s if ch.isdigit())
    return digits.zfill(10) if digits else None


def scalar(row, name):
    v = row.get(name)
    return None if pd.isna(v) else float(v)


def latest_quarter_asof(q: pd.DataFrame, cutoff: pd.Timestamp):
    x = q.loc[q["accepted_at"].le(cutoff)]
    if x.empty:
        return None
    latest_period = x["fiscal_period_end"].max()
    x = x.loc[x["fiscal_period_end"].eq(latest_period)].sort_values("accepted_at")
    return x.iloc[-1] if len(x) else None


def accession_fy_map(long_df: pd.DataFrame) -> pd.DataFrame:
    required = {"accession", "form", "fy"}
    missing = required.difference(long_df.columns)
    if missing:
        raise RuntimeError(f"Long PIT missing FY bridge columns: {sorted(missing)}")
    x = long_df.loc[
        long_df["form"].astype(str).isin(["10-K", "10-K/A"]) & long_df["accession"].notna(),
        ["accession", "fy"],
    ].copy()
    x["accession"] = x["accession"].astype(str)
    x["annual_fy"] = pd.to_numeric(x["fy"], errors="coerce")
    x = x.dropna(subset=["annual_fy"])
    ambiguity = x.groupby("accession")["annual_fy"].nunique()
    bad = ambiguity[ambiguity.gt(1)]
    if not bad.empty:
        raise RuntimeError(f"Ambiguous accession->FY mapping for {len(bad)} filings")
    return x[["accession", "annual_fy"]].drop_duplicates("accession")


def build_annual_states(wide: pd.DataFrame, long_df: pd.DataFrame) -> pd.DataFrame:
    required = {"annual_eps_accepted_at", "annual_eps_source_accession", "annual_eps_growth"}
    missing = required.difference(wide.columns)
    if missing:
        raise RuntimeError(f"Missing annual PIT state columns: {sorted(missing)}")
    cols = ["cik_norm", "annual_eps_accepted_at", "annual_eps_source_accession", "annual_eps_growth"]
    x = wide[cols].copy()
    x["annual_eps_accepted_at"] = pd.to_datetime(x["annual_eps_accepted_at"], errors="coerce", utc=True)
    x = x.dropna(subset=["cik_norm", "annual_eps_accepted_at", "annual_eps_source_accession"])
    x["annual_eps_source_accession"] = x["annual_eps_source_accession"].astype(str)
    x = x.sort_values("annual_eps_accepted_at").drop_duplicates(
        ["cik_norm", "annual_eps_source_accession"], keep="last"
    )
    fy = accession_fy_map(long_df).rename(columns={"accession": "annual_eps_source_accession"})
    return x.merge(fy, on="annual_eps_source_accession", how="left", validate="many_to_one")


def annual_states_asof(a: pd.DataFrame, cutoff: pd.Timestamp):
    x = a.loc[a["annual_eps_accepted_at"].le(cutoff)].copy()
    if x.empty:
        return x, 0, False
    unresolved = int(x["annual_fy"].isna().sum())
    r = x.dropna(subset=["annual_fy"]).copy()
    if r.empty:
        return r, unresolved, False
    r["annual_fy"] = r["annual_fy"].astype(int)
    r = r.sort_values(["annual_fy", "annual_eps_accepted_at"]).groupby("annual_fy", as_index=False).tail(1)
    r = r.sort_values("annual_fy").tail(3)
    years = r["annual_fy"].astype(int).tolist()
    consecutive = len(years) == 3 and years == list(range(years[0], years[0] + 3))
    return r, unresolved, consecutive


def a_from_selected(selected: pd.DataFrame, unresolved: int, consecutive: bool) -> LabelResult:
    if unresolved:
        return LabelResult(None, "NOT_EVALUABLE", "ANNUAL_FY_UNRESOLVED")
    growths = [scalar(r, "annual_eps_growth") for _, r in selected.iterrows()]
    if len(growths) >= 3 and not consecutive:
        return LabelResult(None, "NOT_EVALUABLE", "NON_CONSECUTIVE_ANNUAL_FY")
    return a_label(growths, data_ready=True, fallback_3y=False)


def combine(c_state: str, a_state: str) -> str:
    if c_state == "PASS" and a_state == "PASS":
        return "PASS"
    if "NOT_EVALUABLE" in {c_state, a_state}:
        return "NOT_EVALUABLE"
    return "FAIL"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_pass_intervals(transitions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for security_id, g in transitions.sort_values("effective_accepted_at").groupby("security_id", sort=False):
        active = None
        for r in g.itertuples(index=False):
            if r.ca_state == "PASS" and active is None:
                active = r
            elif r.ca_state != "PASS" and active is not None:
                rows.append({
                    "security_id": security_id,
                    "symbol": active.symbol,
                    "cik": active.cik,
                    "pass_from_accepted_at": active.effective_accepted_at,
                    "pass_until_accepted_at_exclusive": r.effective_accepted_at,
                })
                active = None
        if active is not None:
            rows.append({
                "security_id": security_id,
                "symbol": active.symbol,
                "cik": active.cik,
                "pass_from_accepted_at": active.effective_accepted_at,
                "pass_until_accepted_at_exclusive": None,
            })
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    log("START: load pinned current fundamentals snapshot and frozen research-universe bridge")
    s3 = s3_client()
    bucket = os.environ["R2_BUCKET_NAME"]
    pointer = read_json(s3, bucket, "fundamentals/current.json")
    manifest = read_json(s3, bucket, pointer["manifest_key"])
    art = manifest["artifacts"]
    wide = pd.read_parquet(io.BytesIO(read_bytes(s3, bucket, art["fundamentals_point_in_time.parquet"]["key"])))
    long_df = pd.read_parquet(io.BytesIO(read_bytes(s3, bucket, art["fundamentals_point_in_time_long.parquet"]["key"])))
    bridge = pd.read_csv(io.BytesIO(read_bytes(s3, bucket, art["current_universe.csv"]["key"])), dtype=str)
    report = pd.read_csv(io.BytesIO(read_bytes(s3, bucket, art["fundamentals_final_production_report.csv"]["key"])), dtype=str)
    log(f"LOADED: wide={len(wide):,} long={len(long_df):,} universe={len(bridge):,}")

    wide["accepted_at"] = pd.to_datetime(wide["accepted_at"], errors="coerce", utc=True)
    wide["fiscal_period_end"] = pd.to_datetime(wide["fiscal_period_end"], errors="coerce")
    wide["cik_norm"] = wide["cik"].map(normalize_cik)
    annual_states = build_annual_states(wide, long_df)

    sid_col = "security_id"
    symbol_col = "symbol" if "symbol" in bridge.columns else "ticker"
    report_symbol = "symbol" if "symbol" in report.columns else "ticker"
    status_col = "production_status" if "production_status" in report.columns else "status"
    bridge2 = bridge[[sid_col, symbol_col]].dropna().drop_duplicates(sid_col).rename(columns={symbol_col: "symbol"})
    report2 = report[[report_symbol, "cik", status_col]].dropna(subset=[report_symbol]).drop_duplicates(report_symbol, keep="last")
    report2 = report2.rename(columns={report_symbol: "symbol", status_col: "current_production_status"})
    report2["cik"] = report2["cik"].map(normalize_cik)
    identity = bridge2.merge(report2[["symbol", "cik", "current_production_status"]], on="symbol", how="left", validate="many_to_one")
    identity[sid_col] = identity[sid_col].astype(str)
    if identity[sid_col].duplicated().any():
        raise RuntimeError("Duplicate security_id in identity bridge")
    log(f"IDENTITY: securities={len(identity):,} missing_cik={identity['cik'].isna().sum():,}")

    qmask = wide[["quarterly_eps", "quarterly_revenue", "quarterly_eps_yoy", "quarterly_revenue_yoy"]].notna().any(axis=1)
    q_by_cik = {k: g.sort_values(["fiscal_period_end", "accepted_at"]) for k, g in wide.loc[qmask & wide["cik_norm"].notna()].groupby("cik_norm")}
    a_by_cik = {k: g.sort_values("annual_eps_accepted_at") for k, g in annual_states.groupby("cik_norm")}

    rows = []
    leakage = 0
    log("EVALUATE: event-driven PIT state transitions (no technical candidate population)")
    for i, ident in enumerate(identity.itertuples(index=False), start=1):
        base = ident._asdict()
        cik = base.get("cik")
        if not cik:
            continue
        q = q_by_cik.get(cik, pd.DataFrame(columns=wide.columns))
        a = a_by_cik.get(cik, pd.DataFrame(columns=annual_states.columns))
        events = []
        if not q.empty:
            events.extend(q["accepted_at"].dropna().tolist())
        if not a.empty:
            events.extend(a["annual_eps_accepted_at"].dropna().tolist())
        events = sorted(set(events))
        previous_signature = None
        for cutoff in events:
            qrow = latest_quarter_asof(q, cutoff)
            selected, unresolved, consecutive = annual_states_asof(a, cutoff)
            if qrow is None:
                c = c_label(None, None, data_ready=True)
                q_acc = q_end = eps_yoy = rev_yoy = None
            else:
                eps_yoy = scalar(qrow, "quarterly_eps_yoy")
                rev_yoy = scalar(qrow, "quarterly_revenue_yoy")
                c = c_label(eps_yoy, rev_yoy, data_ready=True)
                q_acc = qrow["accepted_at"]
                q_end = qrow["fiscal_period_end"]
            aa = a_from_selected(selected, unresolved, consecutive)
            years = selected["annual_fy"].astype(int).tolist() if not selected.empty else []
            accessions = selected["annual_eps_source_accession"].astype(str).tolist() if not selected.empty else []
            growths = [scalar(x, "annual_eps_growth") for _, x in selected.iterrows()]
            max_a_acc = selected["annual_eps_accepted_at"].max() if not selected.empty else None
            if q_acc is not None and pd.notna(q_acc) and q_acc > cutoff:
                leakage += 1
            if max_a_acc is not None and pd.notna(max_a_acc) and max_a_acc > cutoff:
                leakage += 1
            ca = combine(c.state, aa.state)
            signature = (c.state, c.reason, q_acc, aa.state, aa.reason, tuple(years), tuple(accessions), ca)
            if signature == previous_signature:
                continue
            previous_signature = signature
            rows.append({
                "security_id": base[sid_col], "symbol": base["symbol"], "cik": cik,
                "current_production_status_provenance_only": base.get("current_production_status"),
                "effective_accepted_at": cutoff,
                "c_state": c.state, "c_reason": c.reason, "c_pass": c.value,
                "c_quarter_end": q_end, "c_source_accepted_at": q_acc,
                "quarterly_eps_yoy": eps_yoy, "quarterly_revenue_yoy": rev_yoy,
                "a_state": aa.state, "a_reason": aa.reason, "a_pass": aa.value,
                "a_fiscal_years": ",".join(map(str, years)),
                "a_source_accessions": ",".join(accessions), "a_growths": json.dumps(growths),
                "a_unresolved_fy_states": unresolved, "a_fy_consecutive": consecutive,
                "a_max_source_accepted_at": max_a_acc, "ca_state": ca,
            })
        if i % 100 == 0 or i == len(identity):
            log(f"PROGRESS: {i}/{len(identity)} securities; transitions={len(rows):,}")

    transitions = pd.DataFrame(rows)
    if transitions.empty:
        raise RuntimeError("No historical fundamental state transitions produced")
    if transitions.duplicated(["security_id", "effective_accepted_at"]).any():
        raise RuntimeError("Duplicate security/time transition rows")
    if leakage:
        raise RuntimeError(f"Future accepted_at leakage violations: {leakage}")
    bad_a = transitions.loc[transitions["a_state"].eq("PASS") & (~transitions["a_fy_consecutive"] | transitions["a_unresolved_fy_states"].gt(0))]
    if not bad_a.empty:
        raise RuntimeError(f"A PASS without resolved consecutive FY identity: {len(bad_a)}")

    intervals = build_pass_intervals(transitions)
    latest = transitions.sort_values("effective_accepted_at").groupby("security_id", as_index=False).tail(1)
    latest_pass = latest.loc[latest["ca_state"].eq("PASS")].copy()

    transitions_path = OUT / "fundamental_state_transitions.csv"
    intervals_path = OUT / "ca_pass_intervals.csv"
    latest_path = OUT / "latest_ca_pass.csv"
    transitions.to_csv(transitions_path, index=False)
    intervals.to_csv(intervals_path, index=False)
    latest_pass.to_csv(latest_path, index=False)

    summary = {
        "workstream": "HISTORICAL_FUNDAMENTAL_SCREENER_V1",
        "population": "frozen/current research universe from pinned fundamentals snapshot; no technical candidates",
        "time_model": "event-driven PIT transitions; query any decision cutoff T using latest effective_accepted_at <= T",
        "fundamentals_manifest_key": pointer["manifest_key"],
        "fundamentals_source_run_id": pointer.get("source_run_id"),
        "universe_securities": int(len(identity)),
        "identity_missing_cik": int(identity["cik"].isna().sum()),
        "state_transitions": int(len(transitions)),
        "securities_with_transitions": int(transitions["security_id"].nunique()),
        "c_distribution": dict(Counter(transitions["c_state"])),
        "a_distribution": dict(Counter(transitions["a_state"])),
        "ca_distribution": dict(Counter(transitions["ca_state"])),
        "ca_pass_intervals": int(len(intervals)),
        "securities_ever_ca_pass": int(intervals["security_id"].nunique()) if not intervals.empty else 0,
        "latest_ca_pass": int(len(latest_pass)),
        "critical_future_accepted_at_violations": int(leakage),
        "current_production_status_policy": "provenance only; not a retroactive historical economic-quality gate",
        "artifacts": {},
    }
    for p in (transitions_path, intervals_path, latest_path):
        summary["artifacts"][p.name] = {"sha256": sha256_file(p), "bytes": p.stat().st_size}
    (OUT / "fundamentals_current_pointer.json").write_text(json.dumps(pointer, indent=2, sort_keys=True), encoding="utf-8")
    (OUT / "fundamentals_snapshot_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    log(f"DONE: transitions={len(transitions):,} pass_intervals={len(intervals):,} ever_pass={summary['securities_ever_ca_pass']:,} latest_pass={len(latest_pass):,}")


if __name__ == "__main__":
    main()
