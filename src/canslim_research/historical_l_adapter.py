from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence

from canslim_research.candidate_v2_adapters import l_screen_state

VERSION = "fa-first-historical-l-adapter-v0.1"
LOOKBACKS = (63, 126, 189, 252)
WEIGHTS = (0.40, 0.20, 0.20, 0.20)


@dataclass(frozen=True, slots=True)
class HistoricalLDecision:
    security_id: str
    asof_date: str
    rs_raw: float | None
    rs_percentile: float | None
    L_state: str
    reason: str
    version: str = VERSION


def _rs_raw(adj_close: Sequence[float]) -> float | None:
    if len(adj_close) <= max(LOOKBACKS):
        return None
    latest = float(adj_close[-1])
    if not isfinite(latest) or latest <= 0:
        return None
    returns = []
    for n in LOOKBACKS:
        base = float(adj_close[-1 - n])
        if not isfinite(base) or base <= 0:
            return None
        returns.append(latest / base - 1.0)
    return sum(w * r for w, r in zip(WEIGHTS, returns))


def evaluate_historical_l_day(
    *,
    asof_date: str,
    adjusted_close_history: Mapping[str, Sequence[float]],
) -> tuple[HistoricalLDecision, ...]:
    """Reproduce frozen production L cross-sectional percentile for one date.

    The input universe must be the governed PIT universe for the decision date;
    callers must not rank only the C+A PASS subset.
    """
    raw = {sid: _rs_raw(values) for sid, values in adjusted_close_history.items()}
    evaluable = sorted((sid, value) for sid, value in raw.items() if value is not None)
    if not evaluable:
        return tuple(
            HistoricalLDecision(sid, asof_date, value, None, "NOT_EVALUABLE", "L_RS_PERCENTILE_MISSING")
            for sid, value in sorted(raw.items())
        )

    values = sorted(v for _, v in evaluable)
    n = len(values)

    def percentile(value: float) -> float:
        # pandas rank(pct=True, method='average') semantics used by production.
        less = sum(v < value for v in values)
        equal = sum(v == value for v in values)
        average_rank = less + (equal + 1) / 2.0
        return average_rank / n * 100.0

    out = []
    for sid, value in sorted(raw.items()):
        pct = None if value is None else percentile(value)
        state, reason = l_screen_state(pct)
        out.append(HistoricalLDecision(sid, asof_date, value, pct, state, reason))
    return tuple(out)
