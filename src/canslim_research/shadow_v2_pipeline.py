"""Pure orchestration helpers for the CAN SLIM v2 shadow path.

No R2 writes, no production pointer mutation, no Entry/Lifecycle side effects.
The qualified READY subset is the only dataset permitted to reach frozen #33.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Callable, Mapping, TypeVar

import pandas as pd

from .watchlist_v2 import WatchlistAssessment, WatchlistLineage, qualified_security_ids

T = TypeVar("T")


def watchlist_checkpoint_payload(
    assessments: Mapping[str, WatchlistAssessment],
    lineage: WatchlistLineage,
    *,
    producer_commit: str,
    producer_run: str,
) -> dict:
    rows = [asdict(assessments[k]) for k in sorted(assessments)]
    logical = {
        "contract_version": "canslim-watchlist-contract-v2",
        "lineage": asdict(lineage),
        "rows": rows,
    }
    checksum = hashlib.sha256(
        json.dumps(logical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        **logical,
        "row_count": len(rows),
        "qualified_count": sum(r["watchlist_state"] == "QUALIFIED" for r in rows),
        "content_sha256": checksum,
        "producer_commit": producer_commit,
        "producer_run": producer_run,
    }


def validate_checkpoint_lineage(checkpoint: Mapping, expected: WatchlistLineage) -> None:
    got = checkpoint.get("lineage") or {}
    want = asdict(expected)
    if got != want:
        raise RuntimeError(f"WATCHLIST_CHECKPOINT_LINEAGE_MISMATCH: expected={want} actual={got}")
    if checkpoint.get("contract_version") != "canslim-watchlist-contract-v2":
        raise RuntimeError("WATCHLIST_CHECKPOINT_CONTRACT_MISMATCH")


def qualified_ready_frame(
    ready_frame: pd.DataFrame,
    assessments: Mapping[str, WatchlistAssessment],
) -> pd.DataFrame:
    if "security_id" not in ready_frame.columns:
        raise RuntimeError("READY_MISSING_SECURITY_ID")
    ids = qualified_security_ids(assessments)
    out = ready_frame.loc[ready_frame["security_id"].astype(str).isin(ids)].copy()
    leaked = set(out["security_id"].astype(str).unique()) - set(ids)
    if leaked:
        raise RuntimeError(f"NONQUALIFIED_SECURITY_LEAK_TO_P33:{sorted(leaked)}")
    return out


def run_frozen_p33_for_qualified(
    ready_frame: pd.DataFrame,
    assessments: Mapping[str, WatchlistAssessment],
    *,
    runner: Callable[[pd.DataFrame], T],
) -> T:
    """Invoke an injected frozen-#33 runner only with qualified securities."""
    subset = qualified_ready_frame(ready_frame, assessments)
    return runner(subset)
