from __future__ import annotations

import io
import json
import os
import sys
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from canslim_research.labels import LabelResult, a_label, c_label  # noqa: E402
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


def accession_fy_map(long_df: pd.DataFrame) -> pd.DataFrame:
    """Map annual source accession -> SEC fiscal year from the long PIT artifact.

    The wide consumer table omits FY, but the immutable long artifact preserves
    the SEC Companyfacts `fy` field on 10-K/10-K/A rows.  Accession numbers are
    filing identities, so they are the safe bridge back to fiscal-year identity.
    """
    required = {"accession", "form", "fy"}
    missing = required.difference(long_df.columns)
    if missing:
        raise RuntimeError(f"Long PIT missing FY bridge columns: {sorted(missing)}")

    x = long_df.loc[
        long_df["form"].astype(str).isin(["10-K", "10-K/A"])
        & long_df["accession"].notna()
    , ["accession", "fy"]].copy()
    x["accession"] = x["accession"].astype(str)
    x["annual_fy"] = pd.to_numeric(x["fy"], errors="coerce")
    x = x.dropna(subset=["annual_fy"])

    ambiguity = x.groupby("accession")["annual_fy"].nunique()
    bad = ambiguity[ambiguity.gt(1)]
    if not bad.empty:
        raise RuntimeError(f"Ambiguous accession->FY mapping for {len(bad)} filings")

    return x[["accession", "annual_fy"]].drop_duplicates("accession")


def build_annual_states(wide: pd.DataFrame, long_df: pd.DataFrame) -> pd.DataFrame:
    """Recover annual PIT states and attach explicit FY identity.

    Annual values/growth and accepted_at come from the production wide contract.
    Fiscal year is resolved by joining annual_eps_source_accession to the immutable
    long PIT artifact, which still carries SEC `fy` on 10-K/10-K/A filing rows.
    """
    required = {"annual_eps_accepted_at", "annual_eps_source_accession", "annual_eps_growth"}
    missing = required.difference(wide.columns)
    if missing:
        raise RuntimeError(f"Missing annual PIT state columns: {sorted(missing)}")

    cols = ["cik_norm", "annual_eps_accepted_at", "annual_eps_source_accession", "annual_eps_growth"]
    if "annual_eps" in wide.columns:
        cols.append("annual_eps")
    x = wide[cols].copy()
    x["annual_eps_accepted_at"] = pd.to_datetime(x["annual_eps_accepted_at"], errors="coerce", utc=True)
    x = x.dropna(subset=["cik_norm", "annual_eps_accepted_at", "annual_eps_source_accession"])
    x["annual_eps_source_accession"] = x["annual_eps_source_accession"].astype(str)
    x = x.sort_values("annual_eps_accepted_at").drop_duplicates(
        ["cik_norm", "annual_eps_source_accession"], keep="last"
    )

    fy = accession_fy_map(long_df).rename(columns={"accession": "annual_eps_source_accession"})
    x = x.merge(fy, on="annual_eps_source_accession", how="left", validate="many_to_one")
    return x


def annual_states_asof(a: pd.DataFrame, cutoff: pd.Timestamp):
    """Select latest accepted annual state per FY, then latest 3 distinct FY.

    Returns (selected, unresolved_count, consecutive).  Unresolved FY states are
    retained as a reason to mark A NOT_EVALUABLE rather than silently skipping them.
    """
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


def a_from_selected(selected: pd.DataFrame, unresolved: int, consecutive: bool, *, ready: bool, fallback: bool) -> LabelResult:
    if not ready:
        return a_label([], data_ready=False, fallback_3y=fallback)
    if unresolved:
        return LabelResult(None, "NOT_EVALUABLE", "ANNUAL_FY_UNRESOLVED")
    growths = [scalar(r, "annual_eps_growth") for _, r in selected.iterrows()]
    if len(growths) >= 3 and not consecutive:
        return LabelResult(None, "NOT_EVALUABLE", "NON_CONSECUTIVE_ANNUAL_FY")
    return a_label(growths, data_ready=True, fallback_3y=fallback)


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
    long_df = pd.read_parquet(io.BytesIO(read_bytes(s3, bucket, art["fundamentals_point_in_time_long.parquet"]["key"])))
    bridge = pd.read_csv(io.BytesIO(read_bytes(s3, bucket, art["current_universe.csv"]["key"])), dtype=str)
    report = pd.read_csv(io.BytesIO(read_bytes(s3, bucket, art["fundamentals_final_production_report.csv"]["key"])), dtype=str)

    wide["accepted_at"] = pd.to_datetime(wide["accepted_at"], errors="coerce", utc=True)
    wide["fiscal_period_end"] = pd.to_datetime(wide["fiscal_period_end"], errors="coerce")
    wide["cik_norm"] = wide["cik"].map(normalize_cik)
    annual_states = build_annual_states(wide, long_df)

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
    q_by_cik = {k: g.sort_values(["fiscal_period_end", "accepted_at"]) for k, g in wide.loc[quarterly_mask & wide["cik_norm"].notna()].groupby("cik_norm")}
    a_by_cik = {k: g.sort_values("annual_eps_accepted_at") for k, g in annual_states.groupby("cik_norm")}

    rows = []
    leakage = 0
    nonconsecutive_rows = 0
    unresolved_fy_rows = 0
    for r in candidates.itertuples(index=False):
        base = r._asdict()
        cik = base.get("cik_norm")
        cutoff = base["signal_cutoff_utc"]
        ready = base.get("production_status") in READY
        qrow = latest_quarter_asof(q_by_cik.get(cik, pd.DataFrame(columns=wide.columns)), cutoff) if cik else None

        annual_all = a_by_cik.get(cik, pd.DataFrame(columns=annual_states.columns)) if cik else pd.DataFrame(columns=annual_states.columns)
        selected, unresolved, consecutive = annual_states_asof(annual_all, cutoff)
        fallback = base.get("production_status") == "PASS_3Y_FALLBACK"
        a = a_from_selected(selected, unresolved, consecutive, ready=ready, fallback=fallback)
        years = selected["annual_fy"].astype(int).tolist() if not selected.empty else []
        annual_state_ids = selected["annual_eps_source_accession"].astype(str).tolist() if not selected.empty else []
        growths = [scalar(x, "annual_eps_growth") for _, x in selected.iterrows()]
        if a.reason == "NON_CONSECUTIVE_ANNUAL_FY":
            nonconsecutive_rows += 1
        if a.reason == "ANNUAL_FY_UNRESOLVED":
            unresolved_fy_rows += 1

        if qrow is None:
            c = c_label(None, None, data_ready=ready)
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

        max_a_acc = selected["annual_eps_accepted_at"].max() if not selected.empty else None
        if max_a_acc is not None and pd.notna(max_a_acc) and max_a_acc > cutoff:
            leakage += 1

        rows.append({
            "security_id": base[sid_col], "ticker": base.get("ticker"), "signal_date": base["signal_date"],
            "signal_cutoff_utc": cutoff, "pivot": base.get("pivot"), "bridge_symbol": base.get("bridge_symbol"),
            "cik": cik, "production_status": base.get("production_status"),
            "c_state": c.state, "c_reason": c.reason, "c_pass": c.value,
            "c_quarter_end": q_end, "c_source_accepted_at": q_acc,
            "quarterly_eps_yoy": eps_yoy, "quarterly_revenue_yoy": rev_yoy,
            "a_state": a.state, "a_reason": a.reason, "a_pass": a.value,
            "a_fiscal_years": ",".join(map(str, years)),
            "a_source_accessions": ",".join(annual_state_ids), "a_growths": json.dumps(growths),
            "a_unresolved_fy_states": unresolved, "a_fy_consecutive": consecutive,
            "a_max_source_accepted_at": max_a_acc,
        })

    out = pd.DataFrame(rows)
    out["ca_state"] = out.apply(lambda x: "PASS" if x.c_state == "PASS" and x.a_state == "PASS" else ("NOT_EVALUABLE" if "NOT_EVALUABLE" in {x.c_state, x.a_state} else "FAIL"), axis=1)

    duplicate_attachment_rows = int(out.duplicated(["security_id", "signal_date"]).sum())
    if len(out) != len(candidates):
        raise RuntimeError(f"Candidate attachment count mismatch: {len(out)} != {len(candidates)}")
    if duplicate_attachment_rows:
        raise RuntimeError(f"Duplicate candidate attachment rows: {duplicate_attachment_rows}")
    bad_a_pass = out.loc[out["a_state"].eq("PASS") & (~out["a_fy_consecutive"] | out["a_unresolved_fy_states"].gt(0))]
    if not bad_a_pass.empty:
        raise RuntimeError(f"A PASS without resolved consecutive FY identity: {len(bad_a_pass)}")

    out.to_csv(OUT / "candidate_ca_labels.csv", index=False)

    summary = {
        "experiment": "HISTORICAL_CA_ATTACHMENT_V1",
        "candidate_count": int(len(out)),
        "candidate_symbols": int(out["security_id"].nunique()),
        "duplicate_candidate_attachment_rows": duplicate_attachment_rows,
        "fundamentals_manifest_key": pointer["manifest_key"],
        "fundamentals_source_run_id": pointer.get("source_run_id"),
        "c_distribution": dict(Counter(out["c_state"])),
        "a_distribution": dict(Counter(out["a_state"])),
        "ca_distribution": dict(Counter(out["ca_state"])),
        "a_reason_distribution": dict(Counter(out["a_reason"])),
        "identity_missing_cik_rows": int(out["cik"].isna().sum()),
        "annual_state_count": int(len(annual_states)),
        "annual_state_fy_resolved": int(annual_states["annual_fy"].notna().sum()),
        "annual_state_fy_unresolved": int(annual_states["annual_fy"].isna().sum()),
        "candidate_rows_nonconsecutive_annual_fy": int(nonconsecutive_rows),
        "candidate_rows_unresolved_annual_fy": int(unresolved_fy_rows),
        "critical_future_accepted_at_violations": int(leakage),
        "cutoff": "16:00 America/New_York on signal T0, DST-aware",
        "quarter_selection": "latest fiscal_period_end known by cutoff; latest accepted state within that period",
        "annual_selection": "accepted_at<=cutoff; resolve source accession->SEC fy from long PIT; latest accepted state per FY; latest three distinct consecutive FY",
        "annual_schema_note": "wide PIT omits FY; immutable long PIT preserves SEC fy and is used only as the accession->FY identity bridge",
        "thresholds_changed": False,
        "performance_metrics_computed": False,
        "research_universe": "CURRENT_COMPLIANT_UNIVERSE_FROZEN_AT_2026_08_28",
        "spy_parquet_key": spy_pointer.get("parquet_key"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))
    (OUT / "fundamentals_current_pointer.json").write_text(json.dumps(pointer, indent=2, sort_keys=True))
    (OUT / "fundamentals_snapshot_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    (OUT / "membership_snapshot.json").write_text(json.dumps(membership, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    if leakage:
        raise RuntimeError(f"PIT leakage invariant failed: {leakage} future accepted_at uses")


if __name__ == "__main__":
    main()
