"""BT5C cross-as-of landmark-state equivalence probe.

Research branch only. Frozen O'Neil code is imported unchanged. This does NOT
claim production/replay authorization. It tests the first plausible exact reuse
boundary: whether landmarks computed once on a later causal prefix can be
filtered by confirmed_date to reproduce landmarks from earlier untouched
prefixes.

Why this boundary: canonical_predictions recomputes excursion + confirmed-window
landmarks on every as-of call. Confirmed-window landmarks have an explicit causal
confirmation date. Excursion landmarks are causal state-machine confirmations.
If later-prefix extraction + confirmation filtering is exact, landmark extraction
can potentially be amortized across replay dates. If any mismatch occurs, the
proposal fails closed before morphology acceleration is attempted.
"""
from __future__ import annotations
from dataclasses import asdict, is_dataclass
from datetime import date
import hashlib
import json
import time
from typing import Any

import pandas as pd

from oneil_patterns.landmarks.excursion import extract_excursion_landmarks
from oneil_patterns.landmarks.confirmed_window import extract_confirmed_window_landmarks
from oneil_patterns.landmarks.fusion import fuse_landmark_sources

CONTRACT = "BT5C_CROSS_ASOF_LANDMARK_EQUIVALENCE_PROBE_V1"
FROZEN_ONEIL_SHA = "c433cc1e35a5aa32a46f732cd8c5545935e36e40"


def _jsonable(v: Any) -> Any:
    if v is None or isinstance(v, (str, int, float, bool)):
        return v
    if isinstance(v, (date, pd.Timestamp)):
        return str(v)
    if isinstance(v, dict):
        return {str(k): _jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple, set)):
        return [_jsonable(x) for x in v]
    if is_dataclass(v):
        return _jsonable(asdict(v))
    if hasattr(v, "value"):
        return _jsonable(v.value)
    return str(v)


def canonical_landmark(item: Any) -> dict[str, Any]:
    # Explicit semantic fields; evidence is included because downstream fusion
    # may depend on source/method details and exactness must not ignore them.
    return {
        "type": _jsonable(item.type),
        "price": float(item.price),
        "price_date": _jsonable(item.price_date),
        "confirmed_date": _jsonable(item.confirmed_date),
        "method": str(item.method),
        "evidence": _jsonable(item.evidence),
    }


def canonical(items) -> list[dict[str, Any]]:
    rows = [canonical_landmark(x) for x in items]
    rows.sort(key=lambda x: (
        x["price_date"], x["confirmed_date"], x["type"], x["method"],
        json.dumps(x["evidence"], sort_keys=True, separators=(",", ":")),
    ))
    return rows


def digest(rows) -> str:
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def prefix(frame: pd.DataFrame, asof: date) -> pd.DataFrame:
    f = frame.copy()
    f["date"] = pd.to_datetime(f["date"], errors="raise")
    return f.loc[f["date"].dt.date <= asof].sort_values("date").drop_duplicates("date").reset_index(drop=True)


def extract_all(frame: pd.DataFrame) -> dict[str, Any]:
    t = time.perf_counter()
    exc = extract_excursion_landmarks(frame)
    t_exc = time.perf_counter()
    win = extract_confirmed_window_landmarks(frame)
    t_win = time.perf_counter()
    fused = fuse_landmark_sources(frame, exc, win)
    t_fused = time.perf_counter()
    return {
        "excursion_objects": exc,
        "window_objects": win,
        "fused_objects": fused,
        "excursion": canonical(exc),
        "window": canonical(win),
        "fused": canonical(fused),
        "timing_sec": {
            "excursion": round(t_exc - t, 6),
            "window": round(t_win - t_exc, 6),
            "fusion": round(t_fused - t_win, 6),
            "total": round(t_fused - t, 6),
        },
    }


def filtered_later(later_objects, asof: date):
    return canonical(x for x in later_objects if x.confirmed_date <= asof)


def compare_rows(oracle, reused):
    return {
        "exact": oracle == reused,
        "oracle_count": len(oracle),
        "reused_count": len(reused),
        "oracle_sha256": digest(oracle),
        "reused_sha256": digest(reused),
    }


def run_probe(frame: pd.DataFrame, asof_dates: list[date]) -> dict[str, Any]:
    if len(asof_dates) < 2:
        raise ValueError("need at least two as-of dates")
    dates = sorted(set(asof_dates))
    latest = dates[-1]
    latest_frame = prefix(frame, latest)
    latest_state = extract_all(latest_frame)

    cases = []
    all_exact = True
    for asof in dates[:-1]:
        earlier = prefix(frame, asof)
        oracle = extract_all(earlier)
        components = {}
        for name, obj_key in (
            ("excursion", "excursion_objects"),
            ("window", "window_objects"),
            ("fused", "fused_objects"),
        ):
            reused = filtered_later(latest_state[obj_key], asof)
            cmp = compare_rows(oracle[name], reused)
            components[name] = cmp
            all_exact = all_exact and cmp["exact"]
        cases.append({
            "asof_date": asof.isoformat(),
            "bars": len(earlier),
            "oracle_timing_sec": oracle["timing_sec"],
            "components": components,
        })

    return {
        "contract": CONTRACT,
        "frozen_oneil_sha": FROZEN_ONEIL_SHA,
        "latest_asof_date": latest.isoformat(),
        "latest_bars": len(latest_frame),
        "latest_extraction_timing_sec": latest_state["timing_sec"],
        "cases": cases,
        "all_exact": all_exact,
        "landmark_cross_asof_reuse_authorized": False,
        "morphology_cross_asof_reuse_authorized": False,
        "bounded_replay_authorized": False,
        "production_eligibility_emitted": False,
        "strategy_returns_computed": False,
        "verdict": (
            "LANDMARK_REUSE_EQUIVALENCE_OBSERVED_MORE_CASES_REQUIRED"
            if all_exact else
            "LANDMARK_REUSE_NOT_EXACT_FAIL_CLOSED"
        ),
    }
