from __future__ import annotations

import io
import json
import os
import re
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

from run_e0_static_history_candidates import MEMBERSHIP_KEY, read_json, s3_client

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "i0-13f-coverage-audit"
SEC_ZIP_URL = "https://www.sec.gov/files/structureddata/data/form-13f-data-sets/01mar2026-31may2026_form13f.zip"
USER_AGENT = os.getenv(
    "SEC_USER_AGENT",
    "azharmz/ussy-canslim-research 127322848+azharmz@users.noreply.github.com",
)
US_ISIN_RE = re.compile(r"^US[A-Z0-9]{9}[0-9]$")


def download_sec_zip() -> tuple[bytes | None, dict]:
    req = urllib.request.Request(
        SEC_ZIP_URL,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/zip,application/octet-stream,*/*",
            "Accept-Encoding": "identity",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = resp.read()
        if len(payload) < 1_000_000:
            raise RuntimeError(f"SEC 13F ZIP unexpectedly small: {len(payload)} bytes")
        return payload, {"status": "SUCCESS", "http_status": 200, "error": None}
    except urllib.error.HTTPError as exc:
        return None, {"status": "BLOCKED_HTTP", "http_status": int(exc.code), "error": str(exc)}
    except Exception as exc:
        return None, {"status": "ERROR", "http_status": None, "error": f"{type(exc).__name__}: {exc}"}


def read_tsv_from_zip(zf: zipfile.ZipFile, suffix: str) -> pd.DataFrame:
    matches = [n for n in zf.namelist() if n.upper().endswith(suffix.upper())]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {suffix}; found {matches}")
    with zf.open(matches[0]) as fh:
        return pd.read_csv(fh, sep="\t", dtype=str, low_memory=False)


def normalize_cusip(s: pd.Series) -> pd.Series:
    return s.fillna("").astype(str).str.upper().str.strip().str.replace(r"\s+", "", regex=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    s3 = s3_client()
    bucket = os.environ["R2_BUCKET_NAME"]
    membership = read_json(s3, bucket, MEMBERSHIP_KEY)
    rows = [r for r in membership.get("records", []) if r.get("sharia_compliance") == "COMPLIANT"]
    universe = pd.DataFrame(rows)
    if universe.empty or "security_id" not in universe.columns:
        raise RuntimeError("Frozen compliant membership unavailable or malformed")

    universe["security_id"] = universe["security_id"].astype(str)
    universe["ticker"] = universe.get("ticker", pd.Series(index=universe.index, dtype=str)).fillna("").astype(str)
    universe["us_isin_mappable"] = universe["security_id"].str.match(US_ISIN_RE)
    universe["derived_cusip9"] = universe["security_id"].where(universe["us_isin_mappable"], "").str.slice(2, 11)
    universe["observed_in_bulk_stock_rows"] = False

    payload, download = download_sec_zip()
    bulk = {
        "sec_zip_bytes": None,
        "mapped_securities_observed_in_bulk_stock_rows": None,
        "observed_fraction_among_us_isin_mappable": None,
        "matched_stock_holding_rows": None,
        "matched_unique_accessions": None,
        "bulk_unique_stock_cusips": None,
        "bulk_info_rows": None,
        "bulk_stock_rows_ex_options": None,
        "submission_rows": None,
        "latest_filing_date_in_bulk": None,
        "report_periods_seen": [],
        "submission_type_counts": {},
        "infotable_columns": [],
        "submission_columns": [],
        "coverpage_columns": [],
    }

    if payload is not None:
        with zipfile.ZipFile(io.BytesIO(payload)) as zf:
            info = read_tsv_from_zip(zf, "INFOTABLE.tsv")
            submission = read_tsv_from_zip(zf, "SUBMISSION.tsv")
            cover = read_tsv_from_zip(zf, "COVERPAGE.tsv")

        if "CUSIP" not in info.columns or "ACCESSION_NUMBER" not in info.columns:
            raise RuntimeError(f"Unexpected INFOTABLE schema: {list(info.columns)}")

        info = info.copy()
        info["CUSIP"] = normalize_cusip(info["CUSIP"])
        info["PUTCALL_NORM"] = info.get("PUTCALL", pd.Series(index=info.index, dtype=str)).fillna("").astype(str).str.upper().str.strip()
        stock_rows = info[~info["PUTCALL_NORM"].isin(["PUT", "CALL"])].copy()
        observed_cusips = set(stock_rows.loc[stock_rows["CUSIP"].str.len().eq(9), "CUSIP"])
        universe["observed_in_bulk_stock_rows"] = universe["derived_cusip9"].isin(observed_cusips) & universe["us_isin_mappable"]

        mapped = universe[universe["us_isin_mappable"]].copy()
        matched = mapped[mapped["observed_in_bulk_stock_rows"]].copy()
        matched_info = stock_rows[stock_rows["CUSIP"].isin(set(matched["derived_cusip9"]))].copy()

        latest_filing_date = None
        for col in ("FILING_DATE", "FILINGDATE"):
            if col in submission.columns:
                d = pd.to_datetime(submission[col], errors="coerce")
                if d.notna().any():
                    latest_filing_date = str(d.max().date())
                break

        report_period_col = next((c for c in ("PERIODOFREPORT", "REPORTCALENDARORQUARTER") if c in submission.columns), None)
        report_periods = []
        if report_period_col:
            report_periods = sorted(set(submission[report_period_col].dropna().astype(str)))
        elif "REPORTCALENDARORQUARTER" in cover.columns:
            report_periods = sorted(set(cover["REPORTCALENDARORQUARTER"].dropna().astype(str)))

        amendment_col = next((c for c in ("SUBMISSIONTYPE", "SUBMISSION_TYPE") if c in submission.columns), None)
        submission_type_counts = {}
        if amendment_col:
            submission_type_counts = {
                str(k): int(v) for k, v in submission[amendment_col].fillna("<NA>").value_counts().to_dict().items()
            }

        bulk.update({
            "sec_zip_bytes": len(payload),
            "mapped_securities_observed_in_bulk_stock_rows": int(len(matched)),
            "observed_fraction_among_us_isin_mappable": float(len(matched) / len(mapped)) if len(mapped) else None,
            "matched_stock_holding_rows": int(len(matched_info)),
            "matched_unique_accessions": int(matched_info["ACCESSION_NUMBER"].nunique()),
            "bulk_unique_stock_cusips": int(stock_rows.loc[stock_rows["CUSIP"].str.len().eq(9), "CUSIP"].nunique()),
            "bulk_info_rows": int(len(info)),
            "bulk_stock_rows_ex_options": int(len(stock_rows)),
            "submission_rows": int(len(submission)),
            "latest_filing_date_in_bulk": latest_filing_date,
            "report_periods_seen": report_periods[-12:],
            "submission_type_counts": submission_type_counts,
            "infotable_columns": list(info.columns),
            "submission_columns": list(submission.columns),
            "coverpage_columns": list(cover.columns),
        })

    mapped_n = int(universe["us_isin_mappable"].sum())
    summary = {
        "experiment": "I0_13F_COVERAGE_AUDIT",
        "evidence_class": "DATA_QUALITY_FEASIBILITY_NOT_STRATEGY_PERFORMANCE",
        "methodology": "docs/methodology/institutional-sponsorship-v1.md",
        "sec_source_url": SEC_ZIP_URL,
        "sec_bulk_download": download,
        "frozen_compliant_universe_count": int(len(universe)),
        "us_isin_deterministically_mappable_count": mapped_n,
        "non_us_isin_deferred_count": int((~universe["us_isin_mappable"]).sum()),
        "us_isin_mapping_fraction": float(mapped_n / len(universe)),
        **bulk,
        "strategy_returns_inspected": False,
        "fwd1_modified": False,
        "status": "BULK_AUDIT_COMPLETE" if payload is not None else "MAPPING_AUDIT_COMPLETE_SEC_BULK_BLOCKED",
        "verdict_rule": "I0 audits feasibility only. It cannot promote an I hard filter.",
    }

    universe[["security_id", "ticker", "us_isin_mappable", "derived_cusip9", "observed_in_bulk_stock_rows"]].to_csv(
        OUT / "universe_mapping_audit.csv", index=False
    )
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
