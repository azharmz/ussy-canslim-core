from __future__ import annotations

import io
import json
import os
from collections import Counter
from pathlib import Path

import boto3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "ca-period-semantics-audit"


def env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing {name}")
    return v


def client():
    return boto3.client(
        "s3",
        endpoint_url=env("R2_ENDPOINT"),
        aws_access_key_id=env("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"),
        region_name="auto",
    )


def get_bytes(s3, bucket: str, key: str) -> bytes:
    return s3.get_object(Bucket=bucket, Key=key)["Body"].read()


def get_json(s3, bucket: str, key: str) -> dict:
    return json.loads(get_bytes(s3, bucket, key))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = client()
    bucket = env("R2_BUCKET_NAME")
    pointer = get_json(s3, bucket, "fundamentals/current.json")
    manifest = get_json(s3, bucket, pointer["manifest_key"])
    art = manifest["artifacts"]
    wide = pd.read_parquet(io.BytesIO(get_bytes(s3, bucket, art["fundamentals_point_in_time.parquet"]["key"])))
    long = pd.read_parquet(io.BytesIO(get_bytes(s3, bucket, art["fundamentals_point_in_time_long.parquet"]["key"])))

    wide["accepted_at"] = pd.to_datetime(wide["accepted_at"], errors="coerce", utc=True)
    wide["fiscal_period_end"] = pd.to_datetime(wide["fiscal_period_end"], errors="coerce")

    quarterly_metric_present = wide[["quarterly_eps", "quarterly_revenue", "quarterly_eps_yoy", "quarterly_revenue_yoy"]].notna().any(axis=1)
    quarterly = wide.loc[quarterly_metric_present].copy()
    annual_metric_present = wide[["annual_eps", "annual_eps_growth"]].notna().any(axis=1)
    annual = wide.loc[annual_metric_present].copy()

    fp_counts = Counter(quarterly["fp"].fillna("<NA>").astype(str))
    form_fp = (
        quarterly.assign(fp_norm=quarterly["fp"].fillna("<NA>").astype(str), form_norm=quarterly["form"].fillna("<NA>").astype(str))
        .groupby(["form_norm", "fp_norm"]).size().sort_values(ascending=False).head(30)
    )

    # For each issuer + fiscal period end, inspect whether multiple accepted states exist.
    multi_state = (
        quarterly.groupby(["symbol", "cik", "fiscal_period_end"], dropna=False)
        .agg(rows=("accepted_at", "size"), accepted_unique=("accepted_at", "nunique"), forms=("form", lambda s: sorted(set(map(str, s.dropna())))))
        .reset_index()
    )
    multi_state_rows = multi_state.loc[multi_state["accepted_unique"] > 1]

    # Determine how often latest accepted quarterly row for a symbol differs from latest fiscal-period-end row.
    latest_by_accepted = quarterly.sort_values(["symbol", "accepted_at", "fiscal_period_end"]).groupby("symbol", as_index=False).tail(1)
    latest_period = quarterly.sort_values(["symbol", "fiscal_period_end", "accepted_at"]).groupby("symbol", as_index=False).tail(1)
    cmp = latest_by_accepted[["symbol", "fiscal_period_end", "accepted_at", "fp", "form"]].merge(
        latest_period[["symbol", "fiscal_period_end", "accepted_at", "fp", "form"]], on="symbol", suffixes=("_by_accepted", "_by_period")
    )
    mismatch = cmp.loc[
        (cmp["fiscal_period_end_by_accepted"] != cmp["fiscal_period_end_by_period"])
        | (cmp["accepted_at_by_accepted"] != cmp["accepted_at_by_period"])
    ]

    # Q4 diagnostics.
    q4 = quarterly.loc[quarterly["fp"].astype(str).str.upper().eq("Q4")].copy()
    q4_provenance = Counter()
    for col in ["quarterly_eps_missing_reason", "quarterly_revenue_missing_reason", "quarterly_eps_yoy_missing_reason", "quarterly_revenue_yoy_missing_reason"]:
        if col in q4.columns:
            q4_provenance.update(f"{col}:{x}" for x in q4[col].dropna().astype(str))

    # Annual semantics from long: 10-K rows and fy coverage.
    long_annual = long.loc[long["form"].astype(str).str.upper().isin(["10-K", "10-K/A"])].copy()
    fy_counts = long_annual.groupby("symbol")["fy"].nunique(dropna=True)

    summary = {
        "audit": "CA_PERIOD_SEMANTICS_V1",
        "manifest_key": pointer["manifest_key"],
        "wide_rows": int(len(wide)),
        "quarterly_rows_with_any_metric": int(len(quarterly)),
        "annual_rows_with_any_metric": int(len(annual)),
        "quarterly_fp_counts": dict(fp_counts),
        "quarterly_form_fp_top": [
            {"form": idx[0], "fp": idx[1], "rows": int(v)} for idx, v in form_fp.items()
        ],
        "quarterly_unique_symbols": int(quarterly["symbol"].nunique()),
        "quarterly_period_groups_with_multiple_accepted_states": int(len(multi_state_rows)),
        "symbols_where_latest_by_accepted_differs_from_latest_period_state": int(len(mismatch)),
        "q4_rows": int(len(q4)),
        "q4_rows_eps_yoy_numeric": int(q4["quarterly_eps_yoy"].notna().sum()),
        "q4_rows_revenue_yoy_numeric": int(q4["quarterly_revenue_yoy"].notna().sum()),
        "q4_missing_reason_top": dict(q4_provenance.most_common(20)),
        "long_10k_rows": int(len(long_annual)),
        "long_10k_symbols": int(long_annual["symbol"].nunique()),
        "annual_fy_count_distribution": {str(k): int(v) for k, v in fy_counts.value_counts().sort_index().to_dict().items()},
        "recommended_quarter_selection": "At each cutoff, restrict to rows accepted by cutoff. Determine latest fiscal_period_end among rows representing quarterly state; within that period choose latest accepted_at by cutoff. Do not choose globally latest accepted row if it refers to an older amended period.",
        "recommended_annual_selection": "At cutoff, restrict 10-K/10-K/A evidence by accepted_at; per FY retain latest accepted evidence; then take latest three FY growth states. Preserve undefined growth as NOT_EVALUABLE.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))
    mismatch.head(200).to_csv(OUT / "latest_state_mismatches.csv", index=False)
    multi_state_rows.head(500).to_csv(OUT / "multi_accepted_periods.csv", index=False)
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
