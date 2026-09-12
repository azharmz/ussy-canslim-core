#!/usr/bin/env python3
"""Run the Stage #33 DEVELOPMENT-only pattern engine on routed OHLCV."""

from __future__ import annotations

import argparse
from datetime import date, timedelta
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
from canslim_research.pattern_conflict import (  # noqa: E402
    CONFLICT_LAYER_VERSION,
    detect_pattern_conflicts,
)
from canslim_research.pattern_engine import DEFAULT_POLICY  # noqa: E402
from canslim_research.pattern_engine_v02 import (  # noqa: E402
    PATTERN_ENGINE_VERSION,
    PRIOR_UPTREND_LOOKBACK,
    PRIOR_UPTREND_MIN_GAIN,
    detect_patterns_v02,
)
from canslim_research.pattern_identity import (  # noqa: E402
    BASE_IDENTITY_VERSION,
    cluster_base_identities,
)
from canslim_research.pattern_lineage import (  # noqa: E402
    BASE_LINEAGE_VERSION,
    cluster_base_lineages,
)

WARMUP_CALENDAR_DAYS = 240


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run P8 DEVELOPMENT pattern engine")
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--start", required=True, help="inclusive evaluation start YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="inclusive evaluation end YYYY-MM-DD")
    parser.add_argument("--security-id")
    parser.add_argument("--snapshot-date", default="current")
    parser.add_argument("--split", default="DEVELOPMENT")
    parser.add_argument("--min-confidence", type=float, default=0.75)
    parser.add_argument("--output", default="results/p8-pattern-engine.json")
    return parser.parse_args()


def _active_policy_report() -> dict:
    """Expose the actual v0.3 semantics instead of stale v0.1 policy fields."""
    geometry = dict(DEFAULT_POLICY.__dict__)
    legacy_prior = {
        "prior_uptrend_lookback": geometry.pop("prior_uptrend_lookback"),
        "prior_uptrend_min_gain": geometry.pop("prior_uptrend_min_gain"),
    }
    return {
        **geometry,
        "prior_uptrend_lookback": PRIOR_UPTREND_LOOKBACK,
        "prior_uptrend_min_gain": PRIOR_UPTREND_MIN_GAIN,
        "prior_uptrend_semantics": "lowest low in prior 120 completed sessions to base-start high >=30%",
        "flat_pivot_semantics": "highest high in the preregistered first-third left-side zone; breakout-day new high cannot redefine the pivot",
        "legacy_v01_prior_uptrend_fields_not_active": legacy_prior,
    }


def run(args: argparse.Namespace) -> dict:
    if args.split != "DEVELOPMENT":
        raise ValueError("P8 pattern engine is frozen to split=DEVELOPMENT")
    if not 0.0 <= args.min_confidence <= 1.0:
        raise ValueError("min-confidence must be between 0 and 1")

    ticker = args.ticker.strip().upper()
    security_id = args.security_id or resolve_security_id_from_r2(ticker, args.snapshot_date)
    fetch_start = (date.fromisoformat(args.start) - timedelta(days=WARMUP_CALENDAR_DAYS)).isoformat()
    routed = route_ohlcv(
        {
            "r2": lambda: r2_provider(security_id=security_id, start=fetch_start, end=args.end),
            "yahoo": lambda: yahoo_provider(ticker=ticker, start=fetch_start, end=args.end),
            "tiingo": lambda: tiingo_provider(ticker=ticker, start=fetch_start, end=args.end),
        }
    )
    rows = list(routed.rows)
    all_candidates = detect_patterns_v02(rows, min_confidence=args.min_confidence)
    candidates = [candidate for candidate in all_candidates if args.start <= candidate.base_end_or_breakout_ready_date <= args.end]
    bases = cluster_base_identities(candidates, security_id=security_id)
    lineages = cluster_base_lineages(bases)
    conflicts = detect_pattern_conflicts(lineages, bases)

    counts = Counter(candidate.pattern_type for candidate in candidates)
    base_counts = Counter(base.pattern_type for base in bases)
    lineage_counts = Counter(lineage.pattern_type for lineage in lineages)
    conflict_counts = Counter(conflict.relationship for conflict in conflicts)
    ambiguous = sum(candidate.pattern_evidence_state == "AMBIGUOUS" for candidate in candidates)
    ambiguous_bases = sum(base.pattern_evidence_state == "AMBIGUOUS" for base in bases)
    ambiguous_lineages = sum(lineage.pattern_evidence_state == "AMBIGUOUS" for lineage in lineages)
    latest = sorted(candidates, key=lambda candidate: (candidate.base_end_or_breakout_ready_date, candidate.confidence), reverse=True)[:25]
    latest_bases = sorted(bases, key=lambda base: (base.last_supported_date, base.confidence), reverse=True)[:25]
    latest_lineages = sorted(lineages, key=lambda lineage: (lineage.last_supported_date, lineage.confidence), reverse=True)[:25]

    requested_row_count = sum(args.start <= str(row["date"])[:10] <= args.end for row in rows)
    return {
        "stage": "P8",
        "workstream": "#33 O'Neil Pattern Recognition Engine",
        "split": "DEVELOPMENT",
        "ticker": ticker,
        "security_id": security_id,
        "requested_start": args.start,
        "requested_end": args.end,
        "warmup_fetch_start": fetch_start,
        "warmup_calendar_days": WARMUP_CALENDAR_DAYS,
        "selected_source": routed.source,
        "source_metadata": dict(routed.metadata),
        "input_row_count_with_warmup": len(rows),
        "requested_interval_row_count": requested_row_count,
        "pattern_engine_version": PATTERN_ENGINE_VERSION,
        "base_identity_version": BASE_IDENTITY_VERSION,
        "base_lineage_version": BASE_LINEAGE_VERSION,
        "conflict_layer_version": CONFLICT_LAYER_VERSION,
        "policy": _active_policy_report(),
        "min_confidence": args.min_confidence,
        "raw_candidate_window_count": len(candidates),
        "raw_ambiguous_window_count": ambiguous,
        "raw_pattern_counts": dict(sorted(counts.items())),
        "base_identity_count": len(bases),
        "ambiguous_base_count": ambiguous_bases,
        "base_pattern_counts": dict(sorted(base_counts.items())),
        "base_lineage_count": len(lineages),
        "ambiguous_lineage_count": ambiguous_lineages,
        "lineage_pattern_counts": dict(sorted(lineage_counts.items())),
        "pattern_conflict_count": len(conflicts),
        "conflict_relationship_counts": dict(sorted(conflict_counts.items())),
        "pattern_conflicts": [conflict.to_dict() for conflict in conflicts],
        "latest_base_lineages": [lineage.to_dict() for lineage in latest_lineages],
        "latest_base_identities": [base.to_dict() for base in latest_bases],
        "latest_raw_candidates": [candidate.to_dict() for candidate in latest],
        "all_base_lineages": [lineage.to_dict() for lineage in lineages],
        "all_base_identities": [base.to_dict() for base in bases],
        "all_candidates": [candidate.to_dict() for candidate in candidates],
        "guardrails": [
            "DEVELOPMENT only",
            "240 calendar days of warmup are fetched before the requested evaluation interval",
            "warmup-only candidates are excluded from reported evaluation output",
            "OHLCV morphology only; no return/CAGR/PF labels",
            "named pattern is not forced when rules are unmet",
            "reported policy fields reflect active v0.3 detector semantics; legacy v0.1 prior-uptrend values are retained only as inactive provenance",
            "flat-base pivot is the established left-side high, not an optional breakout-day new high",
            "pattern-specific pivot is persisted with landmarks",
            "rolling windows sharing the same pattern-specific structural landmarks collapse to one stable base_id",
            "nearby same-pattern base identities may collapse into one prefix-stable lineage only under conservative pattern-specific root anchors",
            "cross-pattern overlap is persisted as an explicit conflict record; no silent winner is selected",
            "cup handle/no-handle hierarchy is explicit and unresolved until morphology adjudication",
            "first_recognized_date is the earliest as-of date the frozen detector could recognize that structural identity",
        ],
    }


def main() -> int:
    args = parse_args()
    report = run(args)
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    hidden = {"all_candidates", "all_base_identities", "all_base_lineages"}
    print(json.dumps({key: value for key, value in report.items() if key not in hidden}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
