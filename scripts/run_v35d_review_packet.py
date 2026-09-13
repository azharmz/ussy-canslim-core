from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

import boto3
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from oneil_patterns.production.engine import analyze_security

CASES = ROOT / "evidence" / "v35" / "frozen_case_ids_v1.csv"
OUT = ROOT / "results" / "v35d-review-packet"


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable {name}")
    return value


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=env("R2_ENDPOINT"),
        aws_access_key_id=env("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=env("R2_SECRET_ACCESS_KEY"),
        region_name="auto",
    )


def load_history(s3, bucket: str, security_id: str) -> pd.DataFrame:
    key = f"backtest/ohlcv/{security_id}.parquet"
    payload = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    frame = pd.read_parquet(io.BytesIO(payload))
    frame["date"] = pd.to_datetime(frame["date"], errors="raise").dt.normalize()
    return frame.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    charts = OUT / "charts"
    charts.mkdir(parents=True, exist_ok=True)

    cases = pd.read_csv(CASES, dtype=str)
    if len(cases) != 60:
        raise RuntimeError(f"Expected 60 frozen cases, found {len(cases)}")

    s3 = s3_client()
    bucket = env("R2_BUCKET_NAME")
    histories = {sid: load_history(s3, bucket, sid) for sid in sorted(cases.security_id.unique())}

    packet_rows: list[dict] = []
    bar_rows: list[pd.DataFrame] = []
    missing: list[dict] = []

    for case in cases.itertuples(index=False):
        asof = pd.Timestamp(case.asof_date)
        history = histories[case.security_id]
        window = history[history["date"] <= asof].tail(300).copy()
        if len(window) < 300:
            missing.append({"validation_case_id": case.validation_case_id, "reason": "INSUFFICIENT_300_BAR_WINDOW"})
            continue

        assessments = analyze_security(
            case.security_id,
            case.ticker,
            window[["date", "open", "high", "low", "close", "volume"]],
            asof.date(),
        )
        matched = [x.to_dict() for x in assessments if x.to_dict().get("candidate_id") == case.candidate_id]
        if len(matched) != 1:
            missing.append({"validation_case_id": case.validation_case_id, "reason": f"CANDIDATE_MATCH_COUNT_{len(matched)}"})
            continue

        item = matched[0]
        packet_rows.append({
            "validation_case_id": case.validation_case_id,
            "security_id": case.security_id,
            "ticker": case.ticker,
            "asof_date": case.asof_date,
            "candidate_id": case.candidate_id,
            "expected_pattern": case.pattern,
            "expected_status": case.pattern_status,
            "actual_pattern": item.get("pattern"),
            "actual_status": item.get("pattern_status"),
            "structural_start": item.get("structural_start"),
            "structural_end": item.get("structural_end"),
            "pivot_level": item.get("pivot_level"),
            "pivot_source_date": item.get("pivot_source_date"),
            "depth_pct": item.get("depth_pct"),
            "native_detector_state": item.get("native_detector_state"),
            "detector_faults": json.dumps(item.get("detector_faults") or [], separators=(",", ":")),
        })

        annotated = window.copy()
        annotated.insert(0, "validation_case_id", case.validation_case_id)
        bar_rows.append(annotated)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True, height_ratios=[3, 1])
        ax1.plot(window["date"], window["close"], linewidth=1.0)
        pivot = item.get("pivot_level")
        if pivot is not None:
            ax1.axhline(float(pivot), linestyle="--", linewidth=1.0)
        for key in ("structural_start", "structural_end", "pivot_source_date"):
            value = item.get(key)
            if value:
                ax1.axvline(pd.Timestamp(value), linestyle=":", linewidth=0.8)
        ax1.set_title(f"{case.validation_case_id} | {case.ticker} | {case.asof_date} | {case.pattern} | {case.pattern_status}")
        ax1.set_ylabel("Raw close")
        ax2.bar(window["date"], window["volume"], width=1.0)
        ax2.set_ylabel("Volume")
        fig.tight_layout()
        fig.savefig(charts / f"{case.validation_case_id}_{case.ticker}.png", dpi=120)
        plt.close(fig)

    packet = pd.DataFrame(packet_rows)
    packet.to_csv(OUT / "case_metadata.csv", index=False)
    pd.concat(bar_rows, ignore_index=True).to_csv(OUT / "bars.csv", index=False)
    pd.DataFrame(missing, columns=["validation_case_id", "reason"]).to_csv(OUT / "missing.csv", index=False)

    mismatches = packet[(packet.expected_pattern != packet.actual_pattern) | (packet.expected_status != packet.actual_status)] if not packet.empty else packet
    summary = {
        "frozen_case_count": len(cases),
        "packet_case_count": len(packet),
        "missing_case_count": len(missing),
        "pattern_status_mismatch_count": len(mismatches),
        "future_bars_included": False,
        "bars_per_case": 300,
        "chart_count": len(list(charts.glob("*.png"))),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if missing or len(mismatches):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
