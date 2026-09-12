#!/usr/bin/env python3
"""P8 DEVELOPMENT-only OHLCV source probe for Stage #33.

This runner does not classify patterns yet. It establishes a deterministic,
auditable input window before the detector is allowed to consume the data.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from canslim_research.ohlcv_providers import (  # noqa: E402
    r2_provider,
    resolve_security_id_from_r2,
    tiingo_provider,
    yahoo_provider,
)
from canslim_research.ohlcv_router import route_ohlcv  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run P8 DEVELOPMENT OHLCV source probe")
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--start", required=True, help="inclusive YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="inclusive YYYY-MM-DD")
    parser.add_argument("--security-id", help="optional; otherwise resolve from R2 membership")
    parser.add_argument("--snapshot-date", default="current")
    parser.add_argument("--split", default="DEVELOPMENT")
    parser.add_argument("--output", default="results/p8-development-source.json")
    return parser.parse_args()


def run(args: argparse.Namespace) -> dict:
    if args.split != "DEVELOPMENT":
        raise ValueError("P8 is frozen to split=DEVELOPMENT; validation/test access is not allowed yet")
    ticker = args.ticker.strip().upper()
    if not ticker:
        raise ValueError("ticker is required")

    security_id = args.security_id
    if not security_id:
        security_id = resolve_security_id_from_r2(ticker, args.snapshot_date)

    result = route_ohlcv(
        {
            "r2": lambda: r2_provider(security_id=security_id, start=args.start, end=args.end),
            "yahoo": lambda: yahoo_provider(ticker=ticker, start=args.start, end=args.end),
            "tiingo": lambda: tiingo_provider(ticker=ticker, start=args.start, end=args.end),
        }
    )
    rows = list(result.rows)
    return {
        "stage": "P8",
        "split": "DEVELOPMENT",
        "ticker": ticker,
        "security_id": security_id,
        "requested_start": args.start,
        "requested_end": args.end,
        "selected_source": result.source,
        "source_metadata": dict(result.metadata),
        "row_count": len(rows),
        "first_date": rows[0]["date"],
        "last_date": rows[-1]["date"],
        "columns": list(rows[0].keys()),
        "routing_policy": ["r2", "yahoo", "tiingo"],
        "fallback_policy": "fallback only on explicit UNAVAILABLE; FAILED/QC_FAILED are terminal",
    }


def main() -> int:
    args = parse_args()
    report = run(args)
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
