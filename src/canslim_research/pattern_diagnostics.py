from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Sequence

from .pattern_engine import DEFAULT_POLICY, EnginePolicy, _argmax, _argmin, _date, _depth, _price, prior_uptrend_state


@dataclass
class FlatBaseDiagnostic:
    start_date: str
    end_date: str
    duration_sessions: int
    prior_uptrend_state: str
    prior_uptrend_gain: float | None
    high_date: str
    high_price: float
    low_date: str
    low_price: float
    depth_pct: float
    first_third_left_high_date: str
    first_third_left_high_price: float
    max_high_vs_first_third_left_high: float
    gate_duration: str
    gate_prior_uptrend: str
    gate_depth: str
    gate_left_high_containment: str
    final_state: str
    failed_gates: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def diagnose_flat_base_window(
    rows: Sequence[dict[str, Any]],
    start: int,
    end: int,
    policy: EnginePolicy = DEFAULT_POLICY,
) -> FlatBaseDiagnostic:
    duration = end - start + 1
    duration_pass = policy.flat_min_sessions <= duration <= policy.flat_max_sessions

    prior_state = prior_uptrend_state(rows, start, policy)
    prior_gain = None
    if start >= policy.prior_uptrend_lookback:
        prior_start = _price(rows[start - policy.prior_uptrend_lookback], "close")
        prebase = _price(rows[start - 1], "close")
        prior_gain = prebase / prior_start - 1.0

    high_index = _argmax(rows, "high", start, end + 1)
    low_index = _argmin(rows, "low", start, end + 1)
    high = _price(rows[high_index], "high")
    low = _price(rows[low_index], "low")
    depth = _depth(high, low)

    first_third_end = start + max(2, duration // 3)
    left_high_index = _argmax(rows, "high", start, min(first_third_end, end + 1))
    left_high = _price(rows[left_high_index], "high")
    high_vs_left = high / left_high - 1.0

    failed: list[str] = []
    if not duration_pass:
        failed.append("DURATION")
    if prior_state != "PASS":
        failed.append("PRIOR_UPTREND")
    if depth > policy.flat_max_depth:
        failed.append("DEPTH")
    if high > left_high * 1.04:
        failed.append("LEFT_HIGH_CONTAINMENT")

    return FlatBaseDiagnostic(
        start_date=_date(rows[start]),
        end_date=_date(rows[end]),
        duration_sessions=duration,
        prior_uptrend_state=prior_state,
        prior_uptrend_gain=round(prior_gain, 6) if prior_gain is not None else None,
        high_date=_date(rows[high_index]),
        high_price=round(high, 8),
        low_date=_date(rows[low_index]),
        low_price=round(low, 8),
        depth_pct=round(depth, 6),
        first_third_left_high_date=_date(rows[left_high_index]),
        first_third_left_high_price=round(left_high, 8),
        max_high_vs_first_third_left_high=round(high_vs_left, 6),
        gate_duration="PASS" if duration_pass else "FAIL",
        gate_prior_uptrend="PASS" if prior_state == "PASS" else prior_state,
        gate_depth="PASS" if depth <= policy.flat_max_depth else "FAIL",
        gate_left_high_containment="PASS" if high <= left_high * 1.04 else "FAIL",
        final_state="PASS" if not failed else "FAIL",
        failed_gates=failed,
    )
