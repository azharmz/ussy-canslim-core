#!/usr/bin/env python3
"""Evaluate authoritative P8 DEVELOPMENT morphology labels without outcome data."""

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

from canslim_research.labelled_morphology import (  # noqa: E402
    LABELLED_EVAL_VERSION,
    MorphologyLabel,
    evaluate_positive_label,
)
from canslim_research.ohlcv_providers import (  # noqa: E402
    r2_provider,
    resolve_security_id_from_r2,
    tiingo_provider,
    yahoo_provider,
)
from canslim_research.ohlcv_router import route_ohlcv  # noqa: E402
from canslim_research.pattern_engine import PATTERN_ENGINE_VERSION, detect_patterns  # noqa: E402
from canslim_research.pattern_identity import BASE_IDENTITY_VERSION, cluster_base_identities  # noqa: E402
from canslim_research.pattern_lineage import BASE_LINEAGE_VERSION, cluster_base_lineages  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate P8 authoritative DEVELOPMENT labels")
    parser.add_argument("--labels", default="data/p8/labels_v0.csv")
    parser.add_argument("--example-id")
    parser.add_argument("--context-calendar-days", type=int, default=120)
    parser.add_argument("--boundary-tolerance-days", type=int, default=10)
    parser.add_argument("--output", default="results/p8-labelled-development.json")
    return parser.parse_args()


def _load_labels(path: Path) -> list[MorphologyLabel]:
    labels: list[MorphologyLabel] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["split"] != "DEVELOPMENT":
                continue
            labels.append(
                MorphologyLabel(
                    example_id=row["example_id"],
                    symbol=row["symbol"],
                    pattern=row["pattern"],
                    label=row["label"],
                    window_start=row["window_start"],
                    window_end=row["window_end"],
                    asof_date=row["asof_date"],
                    provenance=row["provenance"],
                    source_name=row["source_name"],
                    source_reference=row["source_reference"],
                    rationale=row["rationale"],
                    split=row["split"],
                )
            )
    return labels


def _run_label(label: MorphologyLabel, *, context_days: int, boundary_tolerance: int) -> dict:
    context_start = (date.fromisoformat(label.window_start) - timedelta(days=context_days)).isoformat()
    security_id = resolve_security_id_from_r2(label.symbol, "current")
    routed = route_ohlcv(
        {
            "r2": lambda: r2_provider(security_id=security_id, start=context_start, end=label.asof_date),
            "yahoo": lambda: yahoo_provider(ticker=label.symbol, start=context_start, end=label.asof_date),
            "tiingo": lambda: tiingo_provider(ticker=label.symbol, start=context_start, end=label.asof_date),
        }
    )
    candidates = detect_patterns(routed.rows)
    identities = cluster_base_identities(candidates, security_id=security_id)
    lineages = cluster_base_lineages(identities)
    agreement = evaluate_positive_label(
        label,
        lineages,
        identities,
        boundary_tolerance_days=boundary_tolerance,
    )
    return {
        "label": label.__dict__,
        "security_id": security_id,
        "context_start": context_start,
        "selected_source": routed.source,
        "source_metadata": dict(routed.metadata),
        "input_row_count": len(routed.rows),
        "candidate_count": len(candidates),
        "base_identity_count": len(identities),
        "base_lineage_count": len(lineages),
        "agreement": agreement.to_dict(),
        "same_pattern_lineages": [item.to_dict() for item in lineages if item.pattern_type == label.pattern],
    }


def main() -> int:
    args = parse_args()
    if args.context_calendar_days < 60:
        raise ValueError("context-calendar-days must be >=60 so prior-uptrend state is evaluable")
    labels = _load_labels(ROOT / args.labels)
    if args.example_id:
        labels = [label for label in labels if label.example_id == args.example_id]
    if not labels:
        raise ValueError("no DEVELOPMENT labels selected")

    results = [
        _run_label(
            label,
            context_days=args.context_calendar_days,
            boundary_tolerance=args.boundary_tolerance_days,
        )
        for label in labels
    ]
    report = {
        "stage": "P8",
        "scope": "AUTHORITATIVE_LABELLED_DEVELOPMENT",
        "pattern_engine_version": PATTERN_ENGINE_VERSION,
        "base_identity_version": BASE_IDENTITY_VERSION,
        "base_lineage_version": BASE_LINEAGE_VERSION,
        "labelled_eval_version": LABELLED_EVAL_VERSION,
        "context_calendar_days": args.context_calendar_days,
        "boundary_tolerance_days": args.boundary_tolerance_days,
        "result_count": len(results),
        "agreement_counts": {
            state: sum(item["agreement"]["agreement_state"] == state for item in results)
            for state in sorted({item["agreement"]["agreement_state"] for item in results})
        },
        "results": results,
        "guardrails": [
            "DEVELOPMENT split only; VALIDATION labels are not read into detector comparison",
            "reference-first authoritative labels are frozen before detector comparison",
            "OHLCV is truncated at each label asof_date; no future bars are supplied",
            "agreement is morphology/boundary fidelity only; no return/CAGR/PF outcome is inspected",
        ],
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
