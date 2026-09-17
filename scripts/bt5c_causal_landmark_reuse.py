"""Authorized BT5C causal-prefix landmark reuse for Historical BT5 research.

This module is deliberately narrow. It may reuse only raw excursion and
confirmed-window landmarks precomputed from the exact same complete-history
source. Fusion, segmentation, structural geometry, detectors and production
record conversion remain inside the untouched frozen O'Neil engine and are
recomputed for every as-of date.

Any source/prefix invariant failure raises ReuseInvariantError. Callers must
route that case to the untouched oracle; approximation is forbidden.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import pandas as pd

FROZEN_ONEIL_SHA = "c433cc1e35a5aa32a46f732cd8c5545935e36e40"
EXPECTED_OUTPUT_SCHEMA = "oneil-pattern-output-v2"
EXPECTED_ENGINE_VERSION = "33-core-p8-frozen-v1"
REUSE_CONTRACT = "BT5C_AUTHORIZED_CAUSAL_PREFIX_RAW_LANDMARK_REUSE_V1"


class ReuseInvariantError(RuntimeError):
    """Fail-closed signal: caller must use untouched full causal oracle."""


@dataclass(frozen=True)
class SourceIdentity:
    row_count: int
    first_date: str
    last_date: str
    dates: tuple[str, ...]


def normalized_dates(frame: pd.DataFrame) -> pd.Series:
    if "date" not in frame.columns:
        raise ReuseInvariantError("BT5C_REUSE_GUARD_DATE_UNAVAILABLE")
    dates = pd.to_datetime(frame["date"], errors="raise").reset_index(drop=True)
    if dates.empty:
        raise ReuseInvariantError("BT5C_REUSE_GUARD_EMPTY_FRAME")
    if dates.duplicated().any() or not dates.is_monotonic_increasing:
        raise ReuseInvariantError("BT5C_REUSE_GUARD_SOURCE_ORDER")
    return dates


def source_identity(complete_history: pd.DataFrame) -> SourceIdentity:
    dates = normalized_dates(complete_history)
    iso = tuple(x.isoformat() for x in dates)
    return SourceIdentity(len(iso), iso[0], iso[-1], iso)


def assert_exact_causal_prefix(identity: SourceIdentity, local_frame: pd.DataFrame) -> None:
    dates = normalized_dates(local_frame)
    n = len(dates)
    if n > identity.row_count:
        raise ReuseInvariantError("BT5C_REUSE_GUARD_NOT_PREFIX")
    local = tuple(x.isoformat() for x in dates)
    if local != identity.dates[:n]:
        raise ReuseInvariantError("BT5C_REUSE_GUARD_NOT_PREFIX")


def reusable_landmarks(
    landmarks: Sequence[Any], identity: SourceIdentity, local_frame: pd.DataFrame
) -> list[Any]:
    """Return only raw landmarks causally available inside an exact prefix."""
    assert_exact_causal_prefix(identity, local_frame)
    cutoff = pd.Timestamp(local_frame.iloc[-1]["date"]).date()
    local_dates = set(pd.to_datetime(local_frame["date"], errors="raise").dt.date)
    out = []
    for mark in landmarks:
        price_date = getattr(mark, "price_date", None)
        confirmed_date = getattr(mark, "confirmed_date", None)
        if price_date is None or confirmed_date is None:
            raise ReuseInvariantError("BT5C_REUSE_GUARD_LANDMARK_CONTRACT")
        if price_date in local_dates and confirmed_date <= cutoff:
            out.append(mark)
    return out


def validate_frozen_engine(records: Sequence[Any]) -> None:
    """Fail closed if the imported O'Neil output contract is not the frozen one."""
    for record in records:
        schema = getattr(record, "output_schema_version", None)
        engine = getattr(record, "engine_version", None)
        if schema != EXPECTED_OUTPUT_SCHEMA or engine != EXPECTED_ENGINE_VERSION:
            raise ReuseInvariantError("BT5C_FROZEN_ENGINE_SCHEMA_MISMATCH")
