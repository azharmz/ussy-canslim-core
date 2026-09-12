#!/usr/bin/env python3
"""Run the Stage #33 DEVELOPMENT-only pattern engine on routed OHLCV."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
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
from canslim_research.pattern_engine import (  # noqa: E402
    DEFAULT_POLICY,
    PATTERN_ENGINE_VERSION,
    detect_patterns,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run P8 DEVELOPMENT pattern engine")
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--start", required=True, help="inclusive YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="inclusive YYYY-MM-DD")
    parser.add_argument("--security-id")
    parser.add_argument("--snapshot-date", default="current")
    parser.add_argument("--split", default="DEVELOPMENT")
    parser.add_argument("--min-confidence", type=float, default=0.75)
    parser.add_argument("--output", default="results/p8-pattern-engine.json")
    return parser.parse_args()


def run(args: argparse.Namespace) -> dict:
    if args.split != "DEVELOPMENT":
        raise ValueError("P8 pattern engine is frozen to split=DEVELOPMENT")
    if not 0.0 <= args.min_confidence <= 1.0:
        raise ValueError("min-confidence must be between 0 and 1")

    ticker = args.ticker.strip().upper()
    security_id = args.security_id or resolve_security_id_from_r2(ticker, args.snapshot_date)
    routed = route_ohlcv(
        {
            "r2": lambda: r2_provider(security_id=security_id, start=args.start, end=args.end),
            "yahoo": lambda: yahoo_provider(ticker=ticker, start=args.start, end=args.end),
            "tiingo": lambda: tiingo_provider(ticker=ticker, start=args.start, end=args.end),
        }
    )
    rows = list(routed.rows)
    candidates = detect_patterns(rows, min_confidence=args.min_confidence)
    counts = Counter(candidate.pattern_type for candidate in candidates)
    ambiguous = sum(candidate.pattern_evidence_state == "AMBIGUOUS" for candidate in candidates)
    latest = sorted(
        candidates,
        key=lambda candidate: (candidate.base_end_or_breakout_ready_date, candidate.confidence),
        reverse=True,
    )[:25]

    return {
        "stage": "P8",
        "workstream": "#33 O'Neil Pattern Recognition Engine",
        "split": "DEVELOPMENT",
        "ticker": ticker,
        "security_id": security_id,
        "requested_start": args.start,
        "requested_end": args.end,
        "selected_source": routed.source,
        "source_metadata": dict(routed.metadata),
        "input_row_count": len(rows),
        "pattern_engine_version": PATTERN_ENGINE_VERSION,
        "policy": DEFAULT_POLICY.__dict__,
        "min_confidence": args.min_confidence,
        "candidate_count": len(candidates),
        "ambiguous_candidate_count": ambiguous,
        "pattern_counts": dict(sorted(counts.items())),
        "latest_candidates": [candidate.to_dict() for candidate in latest],
        "all_candidates": [candidate.to_dict() for candidate in candidates],
        "guardrails": [
            "DEVELOPMENT only",
            "OHLCV morphology only; no return/CAGR/PF labels",
            "named pattern is not forced when rules are unmet",
            "pattern-specific pivot is persisted with landmarks",
        ],
    }


def main() -> int:
    args = parse_args()
    report = run(args)
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "all_candidates"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
