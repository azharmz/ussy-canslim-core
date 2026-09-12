#!/usr/bin/env python3
"""Audit structural identity/lineage effects of the v0.3 flat-pivot correction.

This is a DEVELOPMENT-only semantic audit. It projects the *same* raw v0.3
candidate windows back to the legacy v0.2 flat-pivot landmark rule (full-window
maximum high) and compares identity/lineage clustering. It does not rerun an old
detector, alter candidate membership, or inspect returns.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import date, timedelta
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from canslim_research.ohlcv_providers import r2_provider, resolve_security_id_from_r2, tiingo_provider, yahoo_provider
from canslim_research.ohlcv_router import route_ohlcv
from canslim_research.pattern_engine import _argmax, _date, _price, normalize_rows
from canslim_research.pattern_engine_v02 import PATTERN_ENGINE_VERSION, detect_patterns_v02
from canslim_research.pattern_identity import BASE_IDENTITY_VERSION, cluster_base_identities, structural_signature
from canslim_research.pattern_lineage import BASE_LINEAGE_VERSION, cluster_base_lineages

WARMUP_CALENDAR_DAYS = 240
LEGACY_PROJECTION = "p8-v0.2-flat-full-window-max-projection"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit P8 v0.3 identity/lineage changes")
    parser.add_argument("--ticker", default="SNPS")
    parser.add_argument("--start", default="2023-01-01")
    parser.add_argument("--end", default="2023-12-31")
    parser.add_argument("--snapshot-date", default="current")
    parser.add_argument("--output", default="results/p8-v03-identity-audit.json")
    return parser.parse_args()


def _legacy_flat_projection(candidate, rows, date_to_index):
    item = deepcopy(candidate)
    if item.pattern_type != "FLAT_BASE":
        return item
    start = date_to_index[item.base_start_date]
    end = date_to_index[item.base_end_or_breakout_ready_date]
    high_index = _argmax(rows, "high", start, end + 1)
    high_price = _price(rows[high_index], "high")
    high_date = _date(rows[high_index])
    item.pivot_level = round(high_price, 8)
    item.pivot_landmark_type = "flat_left_high"
    item.pivot_source_date = high_date
    item.landmarks["flat_left_high"] = {"date": high_date, "price": high_price}
    item.pattern_engine_version = LEGACY_PROJECTION
    return item


def _candidate_key(candidate) -> tuple[str, str, str, str]:
    return (
        candidate.pattern_type,
        candidate.base_start_date,
        candidate.base_end_or_breakout_ready_date,
        str(candidate.landmarks.get("base_low", {}).get("date", "")),
    )


def _identity_lookup(candidates, identities):
    by_signature = {(item.pattern_type, tuple(item.structural_signature)): item.base_id for item in identities}
    return {
        _candidate_key(candidate): by_signature[(candidate.pattern_type, structural_signature(candidate))]
        for candidate in candidates
    }


def _lineage_lookup(identities, lineages):
    result = {}
    for lineage in lineages:
        for base_id in lineage.member_base_ids:
            result[base_id] = lineage.lineage_id
    return result


def _transition_summary(old_assignments, new_assignments):
    old_to_new = defaultdict(set)
    new_to_old = defaultdict(set)
    for key, old_value in old_assignments.items():
        new_value = new_assignments[key]
        old_to_new[old_value].add(new_value)
        new_to_old[new_value].add(old_value)
    return {
        "old_groups_split_across_multiple_new_groups": sum(len(values) > 1 for values in old_to_new.values()),
        "new_groups_merging_multiple_old_groups": sum(len(values) > 1 for values in new_to_old.values()),
        "max_new_groups_from_one_old_group": max((len(values) for values in old_to_new.values()), default=0),
        "max_old_groups_into_one_new_group": max((len(values) for values in new_to_old.values()), default=0),
    }


def main() -> int:
    args = parse_args()
    ticker = args.ticker.upper()
    security_id = resolve_security_id_from_r2(ticker, args.snapshot_date)
    fetch_start = (date.fromisoformat(args.start) - timedelta(days=WARMUP_CALENDAR_DAYS)).isoformat()
    routed = route_ohlcv({
        "r2": lambda: r2_provider(security_id=security_id, start=fetch_start, end=args.end),
        "yahoo": lambda: yahoo_provider(ticker=ticker, start=fetch_start, end=args.end),
        "tiingo": lambda: tiingo_provider(ticker=ticker, start=fetch_start, end=args.end),
    })
    rows = normalize_rows(routed.rows)
    date_to_index = {_date(row): index for index, row in enumerate(rows)}
    detected = detect_patterns_v02(rows)
    current = [item for item in detected if args.start <= item.base_end_or_breakout_ready_date <= args.end]
    legacy = [_legacy_flat_projection(item, rows, date_to_index) for item in current]

    current_ids = cluster_base_identities(current, security_id=security_id)
    legacy_ids = cluster_base_identities(legacy, security_id=security_id)
    current_lineages = cluster_base_lineages(current_ids)
    legacy_lineages = cluster_base_lineages(legacy_ids)

    current_base_by_candidate = _identity_lookup(current, current_ids)
    legacy_base_by_candidate = _identity_lookup(legacy, legacy_ids)
    current_lineage_by_base = _lineage_lookup(current_ids, current_lineages)
    legacy_lineage_by_base = _lineage_lookup(legacy_ids, legacy_lineages)
    current_lineage_by_candidate = {key: current_lineage_by_base[base] for key, base in current_base_by_candidate.items()}
    legacy_lineage_by_candidate = {key: legacy_lineage_by_base[base] for key, base in legacy_base_by_candidate.items()}

    changed_flat_windows = sum(
        old.pivot_source_date != new.pivot_source_date or abs(old.pivot_level / new.pivot_level - 1.0) > 1e-12
        for old, new in zip(legacy, current)
        if new.pattern_type == "FLAT_BASE"
    )
    flat_windows = sum(item.pattern_type == "FLAT_BASE" for item in current)

    current_counts = Counter(item.pattern_type for item in current_ids)
    legacy_counts = Counter(item.pattern_type for item in legacy_ids)
    current_lineage_counts = Counter(item.pattern_type for item in current_lineages)
    legacy_lineage_counts = Counter(item.pattern_type for item in legacy_lineages)

    flat_keys = {key for key in current_base_by_candidate if key[0] == "FLAT_BASE"}
    identity_transition = _transition_summary(
        {key: legacy_base_by_candidate[key] for key in flat_keys},
        {key: current_base_by_candidate[key] for key in flat_keys},
    )
    lineage_transition = _transition_summary(
        {key: legacy_lineage_by_candidate[key] for key in flat_keys},
        {key: current_lineage_by_candidate[key] for key in flat_keys},
    )

    report = {
        "stage": "P8",
        "scope": "V0_3_STRUCTURAL_IDENTITY_AUDIT",
        "ticker": ticker,
        "security_id": security_id,
        "requested_start": args.start,
        "requested_end": args.end,
        "selected_source": routed.source,
        "pattern_engine_version": PATTERN_ENGINE_VERSION,
        "legacy_projection": LEGACY_PROJECTION,
        "base_identity_version": BASE_IDENTITY_VERSION,
        "base_lineage_version": BASE_LINEAGE_VERSION,
        "raw_candidate_window_count": len(current),
        "raw_candidate_membership_changed": False,
        "flat_window_count": flat_windows,
        "flat_windows_with_corrected_pivot": changed_flat_windows,
        "legacy_identity_count": len(legacy_ids),
        "current_identity_count": len(current_ids),
        "identity_delta": len(current_ids) - len(legacy_ids),
        "legacy_identity_pattern_counts": dict(sorted(legacy_counts.items())),
        "current_identity_pattern_counts": dict(sorted(current_counts.items())),
        "legacy_lineage_count": len(legacy_lineages),
        "current_lineage_count": len(current_lineages),
        "lineage_delta": len(current_lineages) - len(legacy_lineages),
        "legacy_lineage_pattern_counts": dict(sorted(legacy_lineage_counts.items())),
        "current_lineage_pattern_counts": dict(sorted(current_lineage_counts.items())),
        "flat_identity_transition": identity_transition,
        "flat_lineage_transition": lineage_transition,
        "interpretation": [
            "candidate membership is identical by construction; only the persisted flat-base pivot landmark is projected",
            "an identity-count increase is expected when corrected left-side pivot dates distinguish windows that the full-window maximum previously collapsed",
            "lineage clustering is the economic-base de-duplication layer; identity fragmentation is concerning only if it also creates unsupported lineage fragmentation",
            "no outcome, return, CAGR, profit factor, or post-event performance is inspected",
        ],
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
