from __future__ import annotations

import hashlib
import io
import json
import os
import zipfile
from pathlib import Path

import pandas as pd
from botocore.exceptions import ClientError

from run_e0_static_history_candidates import read_bytes, read_json, s3_client

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "i1-13f-normalize-staged"
RAW_POINTER_KEY = os.getenv("SEC13F_RAW_POINTER_KEY", "research/sec13f/raw/current.json")


def write_summary(summary: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


def read_tsv_from_zip(zf: zipfile.ZipFile, suffix: str) -> pd.DataFrame:
    matches = [n for n in zf.namelist() if n.upper().endswith(suffix.upper())]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one {suffix}; found {matches}")
    with zf.open(matches[0]) as fh:
        return pd.read_csv(fh, sep="\t", dtype=str, low_memory=False)


def norm(s: pd.Series) -> pd.Series:
    return s.fillna("").astype(str).str.strip()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    s3 = s3_client()
    bucket = os.environ["R2_BUCKET_NAME"]

    try:
        pointer = read_json(s3, bucket, RAW_POINTER_KEY)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code in {"NoSuchKey", "404", "NotFound"}:
            write_summary({
                "experiment": "I1_13F_NORMALIZE_STAGED_V1",
                "status": "WAITING_FOR_RAW_SOURCE",
                "evidence_class": "DATA_PIPELINE_ONLY_NOT_STRATEGY_PERFORMANCE",
                "raw_pointer_key": RAW_POINTER_KEY,
                "strategy_returns_inspected": False,
                "fwd1_modified": False,
                "pit_attach_ready": False,
                "reason": "No staged first-party SEC 13F raw pointer exists in R2.",
            })
            return
        raise

    required = {"source_type", "source_url", "retrieved_at", "object_key", "sha256"}
    missing = sorted(required - set(pointer))
    if missing:
        raise RuntimeError(f"Raw SEC13F pointer missing required fields: {missing}")
    if pointer["source_type"] != "SEC_13F_BULK_ZIP":
        raise RuntimeError(f"Unsupported source_type: {pointer['source_type']}")

    payload = read_bytes(s3, bucket, pointer["object_key"])
    actual_sha = hashlib.sha256(payload).hexdigest()
    if actual_sha != pointer["sha256"]:
        raise RuntimeError("Staged SEC 13F raw object SHA256 mismatch")

    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        info = read_tsv_from_zip(zf, "INFOTABLE.tsv")
        submission = read_tsv_from_zip(zf, "SUBMISSION.tsv")

    required_info = {"ACCESSION_NUMBER", "CUSIP"}
    required_submission = {"ACCESSION_NUMBER"}
    if not required_info.issubset(info.columns):
        raise RuntimeError(f"INFOTABLE missing required columns: {sorted(required_info - set(info.columns))}")
    if not required_submission.issubset(submission.columns):
        raise RuntimeError(f"SUBMISSION missing required columns: {sorted(required_submission - set(submission.columns))}")

    info = info.copy()
    info["ACCESSION_NUMBER"] = norm(info["ACCESSION_NUMBER"])
    info["CUSIP"] = norm(info["CUSIP"]).str.upper().str.replace(r"\s+", "", regex=True)
    info["PUTCALL_NORM"] = norm(info.get("PUTCALL", pd.Series(index=info.index, dtype=str))).str.upper()
    stock = info[~info["PUTCALL_NORM"].isin(["PUT", "CALL"])].copy()

    sub = submission.copy()
    sub["ACCESSION_NUMBER"] = norm(sub["ACCESSION_NUMBER"])
    filing_col = next((c for c in ("FILING_DATE", "FILINGDATE") if c in sub.columns), None)
    report_col = next((c for c in ("PERIODOFREPORT", "REPORTCALENDARORQUARTER") if c in sub.columns), None)
    type_col = next((c for c in ("SUBMISSIONTYPE", "SUBMISSION_TYPE") if c in sub.columns), None)

    meta = pd.DataFrame({"ACCESSION_NUMBER": sub["ACCESSION_NUMBER"]})
    meta["filing_date"] = norm(sub[filing_col]) if filing_col else ""
    meta["period_of_report"] = norm(sub[report_col]) if report_col else ""
    meta["submission_type"] = norm(sub[type_col]).str.upper() if type_col else ""
    meta = meta.drop_duplicates("ACCESSION_NUMBER", keep="last")

    keep = [c for c in [
        "ACCESSION_NUMBER", "CUSIP", "NAMEOFISSUER", "TITLEOFCLASS", "VALUE", "SSHPRNAMT",
        "SSHPRNAMTTYPE", "PUTCALL", "FIGI", "OTHER_MANAGER", "VOTING_AUTH_SOLE",
        "VOTING_AUTH_SHARED", "VOTING_AUTH_NONE"
    ] if c in stock.columns]
    normalized = stock[keep].merge(meta, on="ACCESSION_NUMBER", how="left", validate="many_to_one")
    normalized["accepted_at"] = ""
    normalized["pit_state"] = "NEEDS_EDGAR_ACCEPTED_AT"
    normalized["amendment_state"] = normalized["submission_type"].map(
        lambda x: "UNRESOLVED_AMENDMENT" if x.endswith("/A") else "BASE_OR_UNKNOWN"
    )
    normalized.to_csv(OUT / "normalized_stock_holdings.csv", index=False)
    meta.to_csv(OUT / "submission_metadata.csv", index=False)

    summary = {
        "experiment": "I1_13F_NORMALIZE_STAGED_V1",
        "status": "NORMALIZED_PIT_NOT_READY",
        "evidence_class": "DATA_PIPELINE_ONLY_NOT_STRATEGY_PERFORMANCE",
        "raw_pointer_key": RAW_POINTER_KEY,
        "source_type": pointer["source_type"],
        "source_url": pointer["source_url"],
        "retrieved_at": pointer["retrieved_at"],
        "object_key": pointer["object_key"],
        "sha256": actual_sha,
        "info_rows": int(len(info)),
        "stock_rows_ex_options": int(len(stock)),
        "unique_accessions": int(normalized["ACCESSION_NUMBER"].nunique()),
        "unique_cusip9": int(normalized.loc[normalized["CUSIP"].str.len().eq(9), "CUSIP"].nunique()),
        "amendment_rows": int((normalized["amendment_state"] == "UNRESOLVED_AMENDMENT").sum()),
        "accepted_at_hydrated": False,
        "pit_attach_ready": False,
        "strategy_returns_inspected": False,
        "fwd1_modified": False,
        "guardrail": "Normalized holdings cannot be joined to strategy dates until exact EDGAR accepted_at and amendment lineage are hydrated and audited.",
    }
    write_summary(summary)


if __name__ == "__main__":
    main()
