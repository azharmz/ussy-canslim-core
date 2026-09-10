from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import boto3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from canslim_research.labels import a_label, c_label  # noqa: E402

OUT = ROOT / "results" / "ca-label-distribution-v1"
READY = {"PASS_FULL", "PASS_3Y_FALLBACK"}


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable {name}")
    return value


def client():
    return boto3.client(
        "s3",
        endpoint_url=env("R2_ENDPOINT"),
        aws_access_key_id=env("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"),
        region_name="auto",
    )


def read_json(s3, bucket: str, key: str) -> dict:
    return json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read())


def download(s3, bucket: str, key: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    s3.download_file(bucket, key, str(path))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pick_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    return next((c for c in candidates if c in df.columns), None)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = client()
    bucket = env("R2_BUCKET_NAME")
    pointer = read_json(s3, bucket, "fundamentals/current.json")
    manifest = read_json(s3, bucket, pointer["manifest_key"])
    (OUT / "fundamentals_current_pointer.json").write_text(json.dumps(pointer, indent=2, sort_keys=True))
    (OUT / "fundamentals_snapshot_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))

    artifacts = manifest["artifacts"]
    wide_path = OUT / "_fundamentals_point_in_time.parquet"
    long_path = OUT / "_fundamentals_point_in_time_long.parquet"
    ready_path = OUT / "_fundamentals_final_production_report.csv"
    download(s3, bucket, artifacts["fundamentals_point_in_time.parquet"]["key"], wide_path)
    download(s3, bucket, artifacts["fundamentals_point_in_time_long.parquet"]["key"], long_path)
    download(s3, bucket, artifacts["fundamentals_final_production_report.csv"]["key"], ready_path)

    # Verify immutable snapshot artifacts before interpretation.
    for name, path in [("fundamentals_point_in_time.parquet", wide_path), ("fundamentals_point_in_time_long.parquet", long_path), ("fundamentals_final_production_report.csv", ready_path)]:
        expected = artifacts[name].get("sha256")
        if expected and sha256(path) != expected:
            raise RuntimeError(f"Checksum mismatch: {name}")

    wide = pd.read_parquet(wide_path)
    long = pd.read_parquet(long_path)
    readiness = pd.read_csv(ready_path, dtype={"cik": str})
    readiness = readiness[readiness["production_status"].isin(READY)].copy()
    ready_symbols = set(readiness["symbol"].astype(str))

    symbol_col = pick_col(wide, ["symbol", "ticker"])
    accepted_col = pick_col(wide, ["accepted_at", "filed_at"])
    eps_yoy_col = pick_col(wide, ["quarterly_eps_yoy", "eps_yoy"])
    rev_yoy_col = pick_col(wide, ["quarterly_revenue_yoy", "revenue_yoy"])
    if not all([symbol_col, accepted_col, eps_yoy_col, rev_yoy_col]):
        raise RuntimeError(f"Wide schema missing required C columns. Columns={list(wide.columns)}")

    wide = wide[wide[symbol_col].astype(str).isin(ready_symbols)].copy()
    wide[accepted_col] = pd.to_datetime(wide[accepted_col], errors="coerce", utc=True)
    latest = wide.sort_values(accepted_col).groupby(symbol_col, as_index=False).tail(1)

    # Annual growth may be represented directly in wide or as annual observations in long.
    annual_growth_col = pick_col(long, ["annual_eps_growth", "annual_eps_yoy"])
    annual_eps_col = pick_col(long, ["annual_eps"])
    long_symbol = pick_col(long, ["symbol", "ticker"])
    fy_col = pick_col(long, ["fiscal_year", "fy"])
    long_accepted = pick_col(long, ["accepted_at", "filed_at"])
    if not long_symbol or not fy_col or not long_accepted:
        raise RuntimeError(f"Long schema missing annual identity columns. Columns={list(long.columns)}")

    long = long[long[long_symbol].astype(str).isin(ready_symbols)].copy()
    long[long_accepted] = pd.to_datetime(long[long_accepted], errors="coerce", utc=True)
    annual_rows = long.copy()
    if "form" in annual_rows.columns:
        annual_rows = annual_rows[annual_rows["form"].astype(str).str.upper().isin(["10-K", "10-K/A"])]

    annual_by_symbol: dict[str, list[float | None]] = {}
    for symbol, g in annual_rows.groupby(long_symbol):
        g = g.sort_values([fy_col, long_accepted]).drop_duplicates(fy_col, keep="last")
        vals: list[float | None] = []
        if annual_growth_col:
            vals = [None if pd.isna(x) else float(x) for x in g[annual_growth_col].tolist()]
        elif annual_eps_col:
            eps = pd.to_numeric(g[annual_eps_col], errors="coerce")
            prev = eps.shift(1)
            growth = (eps - prev) / prev
            growth[(prev <= 0) | prev.isna()] = float("nan")
            vals = [None if pd.isna(x) else float(x) for x in growth.tolist()]
        annual_by_symbol[str(symbol)] = vals

    readiness_map = readiness.set_index("symbol")["production_status"].to_dict()
    rows = []
    for _, r in latest.iterrows():
        symbol = str(r[symbol_col])
        c = c_label(None if pd.isna(r[eps_yoy_col]) else float(r[eps_yoy_col]), None if pd.isna(r[rev_yoy_col]) else float(r[rev_yoy_col]))
        status = readiness_map.get(symbol, "")
        a = a_label(annual_by_symbol.get(symbol, []), fallback_3y=status == "PASS_3Y_FALLBACK")
        rows.append({
            "symbol": symbol,
            "production_status": status,
            "latest_accepted_at": r[accepted_col],
            "quarterly_eps_yoy": r[eps_yoy_col],
            "quarterly_revenue_yoy": r[rev_yoy_col],
            "C_state": c.state,
            "C_reason": c.reason,
            "A_state": a.state,
            "A_reason": a.reason,
            "CA_state": "PASS" if c.state == "PASS" and a.state == "PASS" else ("NOT_EVALUABLE" if "NOT_EVALUABLE" in {c.state, a.state} else "FAIL"),
        })

    result = pd.DataFrame(rows).sort_values("symbol")
    result.to_csv(OUT / "distribution.csv", index=False)
    summary = {
        "study": "ca-label-distribution-v1",
        "trading_metrics_used": False,
        "thresholds": {"C_eps_yoy": 0.25, "C_revenue_yoy": 0.25, "A_each_of_latest_3_annual_eps_yoy": 0.25},
        "snapshot": {"manifest_key": pointer["manifest_key"], "source_run_id": pointer.get("source_run_id"), "source_commit": pointer.get("source_commit"), "requested_symbols": pointer.get("requested_symbols"), "production_ready": pointer.get("production_ready")},
        "ready_symbols_expected": len(ready_symbols),
        "symbols_evaluated": int(len(result)),
        "C_counts": {str(k): int(v) for k, v in result["C_state"].value_counts(dropna=False).to_dict().items()},
        "A_counts": {str(k): int(v) for k, v in result["A_state"].value_counts(dropna=False).to_dict().items()},
        "CA_counts": {str(k): int(v) for k, v in result["CA_state"].value_counts(dropna=False).to_dict().items()},
        "readiness_counts": {str(k): int(v) for k, v in result["production_status"].value_counts(dropna=False).to_dict().items()},
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str))
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))

    # Raw production data are intentionally not retained as workflow artifacts.
    for p in [wide_path, long_path, ready_path]:
        p.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
