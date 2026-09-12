#!/usr/bin/env python3
"""Diagnose frozen Flat Base gates for one authoritative DEVELOPMENT label."""

from __future__ import annotations

import argparse
import csv
from datetime import date, timedelta
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
from canslim_research.pattern_diagnostics import diagnose_flat_base_window  # noqa: E402
from canslim_research.pattern_engine import DEFAULT_POLICY, normalize_rows  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", default="data/p8/labels_v0.csv")
    parser.add_argument("--example-id", default="p8-label-0001")
    parser.add_argument("--context-calendar-days", type=int, default=240)
    parser.add_argument("--output", default="results/p8-flat-label-diagnostic.json")
    return parser.parse_args()


def _load(path: Path, example_id: str) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["example_id"] == example_id:
                if row["split"] != "DEVELOPMENT":
                    raise ValueError("diagnostics are DEVELOPMENT only")
                if row["pattern"] != "FLAT_BASE":
                    raise ValueError("this diagnostic runner is Flat Base only")
                return row
    raise ValueError(f"unknown example id: {example_id}")


def _prior_advance_stats(rows, start: int) -> dict[str, dict]:
    result: dict[str, dict] = {}
    prebase_close = float(rows[start - 1]["close"])
    base_start_high = float(rows[start]["high"])
    for lookback in (40, 60, 80, 120):
        if start < lookback:
            result[str(lookback)] = {"state": "NOT_EVALUABLE"}
            continue
        segment = rows[start - lookback : start]
        first_close = float(segment[0]["close"])
        low_row = min(segment, key=lambda row: float(row["low"]))
        low_price = float(low_row["low"])
        result[str(lookback)] = {
            "state": "EVALUABLE",
            "first_close_to_prebase_close_gain": round(prebase_close / first_close - 1.0, 6),
            "trailing_low_date": str(low_row["date"])[:10],
            "trailing_low_price": round(low_price, 8),
            "trailing_low_to_prebase_close_gain": round(prebase_close / low_price - 1.0, 6),
            "trailing_low_to_base_start_high_gain": round(base_start_high / low_price - 1.0, 6),
        }
    return result


def main() -> int:
    args = parse_args()
    label = _load(ROOT / args.labels, args.example_id)
    context_start = (date.fromisoformat(label["window_start"]) - timedelta(days=args.context_calendar_days)).isoformat()
    security_id = resolve_security_id_from_r2(label["symbol"], "current")
    routed = route_ohlcv(
        {
            "r2": lambda: r2_provider(security_id=security_id, start=context_start, end=label["asof_date"]),
            "yahoo": lambda: yahoo_provider(ticker=label["symbol"], start=context_start, end=label["asof_date"]),
            "tiingo": lambda: tiingo_provider(ticker=label["symbol"], start=context_start, end=label["asof_date"]),
        }
    )
    rows = normalize_rows(routed.rows)
    indexes = {str(row["date"])[:10]: index for index, row in enumerate(rows)}
    try:
        start = indexes[label["window_start"]]
        end = indexes[label["window_end"]]
    except KeyError as exc:
        raise ValueError(f"authoritative boundary not present in OHLCV: {exc}") from exc

    diagnostic = diagnose_flat_base_window(rows, start, end, DEFAULT_POLICY)
    body_end = end - 1
    pre_breakout_diagnostic = diagnose_flat_base_window(rows, start, body_end, DEFAULT_POLICY)
    report = {
        "stage": "P8",
        "scope": "AUTHORITATIVE_FLAT_BASE_GATE_DIAGNOSTIC",
        "example_id": label["example_id"],
        "symbol": label["symbol"],
        "source_pattern": label["pattern"],
        "source_window_start": label["window_start"],
        "source_window_end": label["window_end"],
        "source_asof_date": label["asof_date"],
        "selected_source": routed.source,
        "security_id": security_id,
        "input_row_count": len(rows),
        "policy": DEFAULT_POLICY.__dict__,
        "source_window_including_breakout_day": diagnostic.to_dict(),
        "base_body_through_prior_session": pre_breakout_diagnostic.to_dict(),
        "alternative_prior_advance_diagnostics": _prior_advance_stats(rows, start),
        "guardrails": [
            "diagnostic only; detector semantics are unchanged",
            "DEVELOPMENT authoritative label only",
            "OHLCV ends at source asof_date",
            "alternative prior-advance calculations are diagnostics, not promoted thresholds",
            "no post-breakout return/CAGR/PF data is inspected",
        ],
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
