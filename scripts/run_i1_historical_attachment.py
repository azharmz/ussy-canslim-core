from __future__ import annotations

import io
import json
import os
import sys
from collections import Counter
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_e1_e4_static_trade_diagnostics import generate_candidates  # noqa: E402
from run_e0_static_history_candidates import s3_client  # noqa: E402

OUT = ROOT / "results" / "historical-i1-attachment-v1"


def read_bytes(s3, bucket: str, key: str) -> bytes:
    return s3.get_object(Bucket=bucket, Key=key)["Body"].read()


def read_json(s3, bucket: str, key: str) -> dict:
    return json.loads(read_bytes(s3, bucket, key))


def download_key(s3, bucket: str, key: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    s3.download_file(bucket, key, str(path))


def derived_cusip(security_id: str) -> str | None:
    sid = str(security_id).strip().upper()
    if len(sid) == 12 and sid.startswith("US"):
        return sid[2:11]
    return None


def consecutive_quarters(latest: pd.Timestamp, prior: pd.Timestamp) -> bool:
    if pd.isna(latest) or pd.isna(prior):
        return False
    return (latest.to_period("Q") - prior.to_period("Q")).n == 1


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = s3_client()
    bucket = os.environ["R2_BUCKET_NAME"]

    candidates, membership, spy_pointer = generate_candidates(s3, bucket)
    candidates = candidates.copy().reset_index(drop=True)
    candidates["candidate_id"] = candidates.index.astype("int64")
    candidates["signal_date"] = pd.to_datetime(candidates["date"], errors="coerce").dt.normalize()
    candidates["security_id"] = candidates["security_id"].astype(str)
    candidates["cusip"] = candidates["security_id"].map(derived_cusip)

    pointer = read_json(s3, bucket, "institutional_sponsorship/current.json")
    if pointer.get("status") != "READY":
        raise RuntimeError(f"Institutional sponsorship pointer not READY: {pointer}")
    manifest = read_json(s3, bucket, pointer["manifest_key"])
    if manifest.get("status") != "READY":
        raise RuntimeError("Institutional sponsorship manifest not READY")

    event_path = OUT / "_sponsorship_state_events.parquet"
    uncertainty_path = OUT / "_uncertainty_state_events.parquet"
    download_key(s3, bucket, pointer["history_state_events_key"], event_path)
    download_key(s3, bucket, pointer["uncertainty_state_events_key"], uncertainty_path)

    joinable = candidates.loc[candidates["cusip"].notna(), ["candidate_id", "cusip", "signal_date"]].copy()
    con = duckdb.connect(database=":memory:")
    con.register("candidates", joinable)

    # For each candidate and report period, recover the last aggregate sponsorship
    # state that was available by the signal date. source_accession is a deterministic
    # tiebreaker for multiple state changes sharing the same conservative available_on.
    states = con.execute(
        f"""
        SELECT candidate_id, period_of_report, I_manager_count,
               I_reported_value_total, I_reported_share_total,
               available_on, source_accession
        FROM (
          SELECT c.candidate_id,
                 CAST(e.period_of_report AS DATE) AS period_of_report,
                 e.I_manager_count,
                 e.I_reported_value_total,
                 e.I_reported_share_total,
                 CAST(e.available_on AS DATE) AS available_on,
                 e.source_accession,
                 ROW_NUMBER() OVER (
                   PARTITION BY c.candidate_id, e.period_of_report
                   ORDER BY CAST(e.available_on AS DATE) DESC, e.source_accession DESC
                 ) AS rn
          FROM candidates c
          JOIN read_parquet('{event_path.as_posix()}') e
            ON e.cusip = c.cusip
           AND CAST(e.available_on AS DATE) <= c.signal_date
        ) x
        WHERE rn = 1
        """
    ).df()

    # Uncertainty is a time-varying state. Missing uncertainty event means zero
    # uncertainty, not missing sponsorship; a positive latest state quarantines the
    # affected CUSIP-period only.
    uncertainty = con.execute(
        f"""
        SELECT candidate_id, period_of_report, I_uncertain_manager_count
        FROM (
          SELECT c.candidate_id,
                 CAST(u.period_of_report AS DATE) AS period_of_report,
                 u.I_uncertain_manager_count,
                 ROW_NUMBER() OVER (
                   PARTITION BY c.candidate_id, u.period_of_report
                   ORDER BY CAST(u.available_on AS DATE) DESC, u.source_accession DESC
                 ) AS rn
          FROM candidates c
          JOIN read_parquet('{uncertainty_path.as_posix()}') u
            ON u.cusip = c.cusip
           AND CAST(u.available_on AS DATE) <= c.signal_date
        ) x
        WHERE rn = 1
        """
    ).df()
    con.close()

    states["period_of_report"] = pd.to_datetime(states["period_of_report"], errors="coerce")
    states["available_on"] = pd.to_datetime(states["available_on"], errors="coerce")
    if not uncertainty.empty:
        uncertainty["period_of_report"] = pd.to_datetime(uncertainty["period_of_report"], errors="coerce")
    u_lookup = {
        (int(r.candidate_id), r.period_of_report): int(r.I_uncertain_manager_count)
        for r in uncertainty.itertuples(index=False)
    }

    by_candidate = {int(k): g.sort_values("period_of_report") for k, g in states.groupby("candidate_id")}
    rows = []
    future_violations = 0

    for r in candidates.itertuples(index=False):
        cid = int(r.candidate_id)
        base = r._asdict()
        cusip = base.get("cusip")
        signal_date = pd.Timestamp(base["signal_date"])

        label = "NOT_EVALUABLE"
        reason = "UNMAPPED_NON_US_ISIN" if cusip is None else "INSUFFICIENT_PERIODS"
        latest = prior = None
        latest_u = prior_u = 0

        g = by_candidate.get(cid)
        if cusip is not None and g is not None and len(g) >= 2:
            latest = g.iloc[-1]
            prior = g.iloc[-2]
            latest_u = u_lookup.get((cid, latest["period_of_report"]), 0)
            prior_u = u_lookup.get((cid, prior["period_of_report"]), 0)

            if pd.Timestamp(latest["available_on"]) > signal_date or pd.Timestamp(prior["available_on"]) > signal_date:
                future_violations += 1
                reason = "FUTURE_AVAILABILITY_VIOLATION"
            elif not consecutive_quarters(latest["period_of_report"], prior["period_of_report"]):
                reason = "NON_CONSECUTIVE_REPORT_PERIODS"
            elif latest_u > 0 or prior_u > 0:
                reason = "UNRESOLVED_LINEAGE_UNCERTAINTY"
            else:
                delta = int(latest["I_manager_count"]) - int(prior["I_manager_count"])
                label = "PASS" if delta > 0 else "FAIL"
                reason = "MANAGER_COUNT_INCREASE" if delta > 0 else "NO_MANAGER_COUNT_INCREASE"

        rows.append({
            "candidate_id": cid,
            "security_id": base["security_id"],
            "ticker": base.get("ticker"),
            "signal_date": signal_date,
            "cusip": cusip,
            "I_v1_label": label,
            "I_reason": reason,
            "I_manager_count_latest": None if latest is None else int(latest["I_manager_count"]),
            "I_manager_count_prior": None if prior is None else int(prior["I_manager_count"]),
            "I_manager_count_qoq_delta": None if latest is None or prior is None else int(latest["I_manager_count"]) - int(prior["I_manager_count"]),
            "I_latest_period_of_report": None if latest is None else latest["period_of_report"],
            "I_prior_period_of_report": None if prior is None else prior["period_of_report"],
            "I_latest_available_on": None if latest is None else latest["available_on"],
            "I_prior_available_on": None if prior is None else prior["available_on"],
            "I_latest_uncertain_manager_count": latest_u,
            "I_prior_uncertain_manager_count": prior_u,
            "I_mapping_method": "US_ISIN_TO_CUSIP9" if cusip is not None else None,
        })

    out = pd.DataFrame(rows)
    if len(out) != len(candidates):
        raise RuntimeError(f"Attachment count mismatch: {len(out)} != {len(candidates)}")
    if out["candidate_id"].duplicated().any():
        raise RuntimeError("Duplicate candidate attachment rows")
    if future_violations:
        raise RuntimeError(f"Future availability violations: {future_violations}")

    out.to_csv(OUT / "candidate_i1_labels.csv", index=False)
    summary = {
        "experiment": "HISTORICAL_I1_ATTACHMENT_V1",
        "candidate_count": int(len(out)),
        "candidate_symbols": int(out["security_id"].nunique()),
        "label_distribution": dict(Counter(out["I_v1_label"])),
        "reason_distribution": dict(Counter(out["I_reason"])),
        "mapped_candidate_rows": int(out["cusip"].notna().sum()),
        "unmapped_candidate_rows": int(out["cusip"].isna().sum()),
        "critical_future_availability_violations": int(future_violations),
        "sponsorship_manifest_key": pointer["manifest_key"],
        "sponsorship_history_source_run_id": pointer.get("history_source_run_id"),
        "sponsorship_uncertainty_source_run_id": pointer.get("uncertainty_source_run_id"),
        "historical_availability_semantics": manifest.get("semantics", {}).get("historical_availability"),
        "strategy_returns_inspected": False,
        "fwd1_modified": False,
        "rule": "PASS iff latest two consecutive usable report periods have manager_count_latest > manager_count_prior",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))

    event_path.unlink(missing_ok=True)
    uncertainty_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
