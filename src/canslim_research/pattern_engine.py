from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Sequence


PATTERN_ENGINE_VERSION = "p8-v0.1-development-preregistered"

CORE_PATTERNS = (
    "CUP_WITH_HANDLE",
    "CUP_WITHOUT_HANDLE",
    "DOUBLE_BOTTOM",
    "FLAT_BASE",
)


@dataclass(frozen=True)
class EnginePolicy:
    """Development-only morphology thresholds.

    These values are preregistered implementation assumptions derived from the
    frozen theory contract. They are not selected from return/CAGR/PF outcomes.
    """

    prior_uptrend_lookback: int = 40
    prior_uptrend_min_gain: float = 0.20
    flat_min_sessions: int = 25
    flat_max_sessions: int = 35
    flat_max_depth: float = 0.15
    cup_min_sessions: int = 35
    cup_max_sessions: int = 130
    cup_min_depth: float = 0.12
    cup_max_depth: float = 0.50
    cup_right_recovery_min: float = 0.90
    cup_no_handle_recovery_min: float = 0.95
    handle_min_sessions: int = 5
    handle_max_sessions: int = 20
    handle_max_depth: float = 0.15
    double_bottom_min_sessions: int = 35
    double_bottom_max_sessions: int = 90
    double_bottom_low_tolerance: float = 0.05
    double_bottom_min_middle_rebound: float = 0.10


DEFAULT_POLICY = EnginePolicy()


@dataclass
class PatternCandidate:
    pattern_type: str
    pattern_evidence_state: str
    confidence: float
    base_start_date: str
    base_end_or_breakout_ready_date: str
    base_duration_sessions: int
    base_depth_pct: float
    prior_uptrend_state: str
    pivot_level: float
    pivot_landmark_type: str
    pivot_source_date: str
    landmarks: dict[str, Any] = field(default_factory=dict)
    fault_flags: list[str] = field(default_factory=list)
    ambiguity_with: list[str] = field(default_factory=list)
    pattern_engine_version: str = PATTERN_ENGINE_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _date(row: dict[str, Any]) -> str:
    return str(row["date"])[:10]


def _price(row: dict[str, Any], field: str) -> float:
    value = float(row[field])
    if value <= 0:
        raise ValueError(f"{field} must be positive")
    return value


def normalize_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = [dict(row) for row in rows]
    if not normalized:
        raise ValueError("pattern engine requires at least one OHLCV row")
    required = {"date", "open", "high", "low", "close", "volume"}
    for index, row in enumerate(normalized):
        missing = required - set(row)
        if missing:
            raise ValueError(f"row {index} missing columns: {sorted(missing)}")
        for field in ("open", "high", "low", "close"):
            _price(row, field)
        if _price(row, "high") < max(_price(row, "open"), _price(row, "low"), _price(row, "close")):
            raise ValueError(f"row {index} high below OHLC range")
        if _price(row, "low") > min(_price(row, "open"), _price(row, "high"), _price(row, "close")):
            raise ValueError(f"row {index} low above OHLC range")
        if float(row["volume"]) < 0:
            raise ValueError(f"row {index} volume must be nonnegative")
    normalized.sort(key=_date)
    dates = [_date(row) for row in normalized]
    if len(dates) != len(set(dates)):
        raise ValueError("duplicate session dates are not allowed")
    return normalized


def prior_uptrend_state(rows: Sequence[dict[str, Any]], base_start: int, policy: EnginePolicy = DEFAULT_POLICY) -> str:
    lookback = policy.prior_uptrend_lookback
    if base_start < lookback:
        return "NOT_EVALUABLE"
    start_close = _price(rows[base_start - lookback], "close")
    prebase_close = _price(rows[base_start - 1], "close")
    gain = prebase_close / start_close - 1.0
    return "PASS" if gain >= policy.prior_uptrend_min_gain else "FAIL"


def _depth(high: float, low: float) -> float:
    return 1.0 - low / high


def _argmax(rows: Sequence[dict[str, Any]], field: str, start: int, end: int) -> int:
    return max(range(start, end), key=lambda i: _price(rows[i], field))


def _argmin(rows: Sequence[dict[str, Any]], field: str, start: int, end: int) -> int:
    return min(range(start, end), key=lambda i: _price(rows[i], field))


def _candidate(
    *,
    rows: Sequence[dict[str, Any]],
    pattern_type: str,
    start: int,
    end: int,
    low_index: int,
    prior_state: str,
    confidence: float,
    pivot_level: float,
    pivot_landmark_type: str,
    pivot_source_index: int,
    landmarks: dict[str, Any],
    fault_flags: list[str] | None = None,
) -> PatternCandidate:
    base_high = max(_price(row, "high") for row in rows[start : end + 1])
    base_low = _price(rows[low_index], "low")
    return PatternCandidate(
        pattern_type=pattern_type,
        pattern_evidence_state="PASS",
        confidence=round(max(0.0, min(1.0, confidence)), 4),
        base_start_date=_date(rows[start]),
        base_end_or_breakout_ready_date=_date(rows[end]),
        base_duration_sessions=end - start + 1,
        base_depth_pct=round(_depth(base_high, base_low), 6),
        prior_uptrend_state=prior_state,
        pivot_level=round(pivot_level, 8),
        pivot_landmark_type=pivot_landmark_type,
        pivot_source_date=_date(rows[pivot_source_index]),
        landmarks=landmarks,
        fault_flags=fault_flags or [],
    )


def detect_flat_base(
    rows: Sequence[dict[str, Any]], start: int, end: int, policy: EnginePolicy = DEFAULT_POLICY
) -> PatternCandidate | None:
    duration = end - start + 1
    if not policy.flat_min_sessions <= duration <= policy.flat_max_sessions:
        return None
    prior_state = prior_uptrend_state(rows, start, policy)
    if prior_state != "PASS":
        return None
    high_index = _argmax(rows, "high", start, end + 1)
    low_index = _argmin(rows, "low", start, end + 1)
    high = _price(rows[high_index], "high")
    low = _price(rows[low_index], "low")
    depth = _depth(high, low)
    if depth > policy.flat_max_depth:
        return None
    first_third_end = start + max(2, duration // 3)
    left_high_index = _argmax(rows, "high", start, first_third_end)
    left_high = _price(rows[left_high_index], "high")
    if high > left_high * 1.04:
        return None
    confidence = 0.75 + 0.20 * (1.0 - depth / policy.flat_max_depth)
    return _candidate(
        rows=rows,
        pattern_type="FLAT_BASE",
        start=start,
        end=end,
        low_index=low_index,
        prior_state=prior_state,
        confidence=confidence,
        pivot_level=high,
        pivot_landmark_type="flat_left_high",
        pivot_source_index=high_index,
        landmarks={
            "flat_left_high": {"date": _date(rows[high_index]), "price": high},
            "base_low": {"date": _date(rows[low_index]), "price": low},
        },
    )


def _cup_geometry(
    rows: Sequence[dict[str, Any]], start: int, cup_end: int, policy: EnginePolicy
) -> tuple[int, int, int, float, float, float] | None:
    duration = cup_end - start + 1
    if not policy.cup_min_sessions <= duration <= policy.cup_max_sessions:
        return None
    left_zone_end = start + max(3, int(duration * 0.25))
    right_zone_start = start + max(3, int(duration * 0.75))
    if right_zone_start >= cup_end:
        return None
    left_peak = _argmax(rows, "high", start, left_zone_end)
    cup_low = _argmin(rows, "low", left_peak + 1, right_zone_start + 1)
    right_high = _argmax(rows, "high", right_zone_start, cup_end + 1)
    left_price = _price(rows[left_peak], "high")
    low_price = _price(rows[cup_low], "low")
    right_price = _price(rows[right_high], "high")
    depth = _depth(left_price, low_price)
    if not policy.cup_min_depth <= depth <= policy.cup_max_depth:
        return None
    if right_price / left_price < policy.cup_right_recovery_min:
        return None
    if cup_low - left_peak < 5 or right_high - cup_low < 5:
        return None
    # Reject obvious V-shapes: at least three sessions must spend near the lower
    # quartile of the cup range.
    lower_quartile = low_price + 0.25 * (left_price - low_price)
    low_band_sessions = sum(
        1 for row in rows[left_peak : right_high + 1] if _price(row, "low") <= lower_quartile
    )
    if low_band_sessions < 3:
        return None
    return left_peak, cup_low, right_high, left_price, low_price, right_price


def detect_cup_without_handle(
    rows: Sequence[dict[str, Any]], start: int, end: int, policy: EnginePolicy = DEFAULT_POLICY
) -> PatternCandidate | None:
    prior_state = prior_uptrend_state(rows, start, policy)
    if prior_state != "PASS":
        return None
    geometry = _cup_geometry(rows, start, end, policy)
    if geometry is None:
        return None
    left_peak, cup_low, right_high, left_price, low_price, right_price = geometry
    recovery = right_price / left_price
    if recovery < policy.cup_no_handle_recovery_min:
        return None
    depth = _depth(left_price, low_price)
    confidence = 0.72 + 0.14 * min(1.0, (recovery - policy.cup_no_handle_recovery_min) / 0.05 + 0.5)
    confidence += 0.08 * (1.0 - abs(depth - 0.25) / 0.25)
    return _candidate(
        rows=rows,
        pattern_type="CUP_WITHOUT_HANDLE",
        start=start,
        end=end,
        low_index=cup_low,
        prior_state=prior_state,
        confidence=confidence,
        pivot_level=left_price,
        pivot_landmark_type="left_peak",
        pivot_source_index=left_peak,
        landmarks={
            "left_peak": {"date": _date(rows[left_peak]), "price": left_price},
            "cup_low": {"date": _date(rows[cup_low]), "price": low_price},
            "right_side_high": {"date": _date(rows[right_high]), "price": right_price},
        },
    )


def detect_cup_with_handle(
    rows: Sequence[dict[str, Any]], start: int, end: int, policy: EnginePolicy = DEFAULT_POLICY
) -> PatternCandidate | None:
    prior_state = prior_uptrend_state(rows, start, policy)
    if prior_state != "PASS":
        return None
    duration = end - start + 1
    for handle_duration in range(policy.handle_min_sessions, policy.handle_max_sessions + 1):
        handle_start = end - handle_duration + 1
        cup_end = handle_start - 1
        if cup_end <= start:
            continue
        geometry = _cup_geometry(rows, start, cup_end, policy)
        if geometry is None:
            continue
        left_peak, cup_low, right_high, left_price, low_price, right_price = geometry
        handle_high_index = _argmax(rows, "high", handle_start, end + 1)
        handle_low_index = _argmin(rows, "low", handle_start, end + 1)
        handle_high = _price(rows[handle_high_index], "high")
        handle_low = _price(rows[handle_low_index], "low")
        handle_depth = _depth(handle_high, handle_low)
        if handle_depth > policy.handle_max_depth:
            continue
        cup_midpoint = low_price + 0.5 * (left_price - low_price)
        if handle_low <= cup_midpoint:
            continue
        if handle_high > left_price * 1.03:
            continue
        if right_price / left_price < policy.cup_right_recovery_min:
            continue
        fault_flags: list[str] = []
        if handle_low_index <= handle_start + 1:
            fault_flags.append("HANDLE_LOW_TOO_EARLY")
        confidence = 0.78 + 0.10 * (1.0 - handle_depth / policy.handle_max_depth)
        confidence += 0.07 * min(1.0, right_price / left_price)
        return _candidate(
            rows=rows,
            pattern_type="CUP_WITH_HANDLE",
            start=start,
            end=end,
            low_index=cup_low,
            prior_state=prior_state,
            confidence=confidence,
            pivot_level=handle_high,
            pivot_landmark_type="handle_high",
            pivot_source_index=handle_high_index,
            landmarks={
                "left_peak": {"date": _date(rows[left_peak]), "price": left_price},
                "cup_low": {"date": _date(rows[cup_low]), "price": low_price},
                "right_side_high": {"date": _date(rows[right_high]), "price": right_price},
                "handle_start": {"date": _date(rows[handle_start]), "price": _price(rows[handle_start], "close")},
                "handle_high": {"date": _date(rows[handle_high_index]), "price": handle_high},
                "handle_low": {"date": _date(rows[handle_low_index]), "price": handle_low},
            },
            fault_flags=fault_flags,
        )
    return None


def detect_double_bottom(
    rows: Sequence[dict[str, Any]], start: int, end: int, policy: EnginePolicy = DEFAULT_POLICY
) -> PatternCandidate | None:
    duration = end - start + 1
    if not policy.double_bottom_min_sessions <= duration <= policy.double_bottom_max_sessions:
        return None
    prior_state = prior_uptrend_state(rows, start, policy)
    if prior_state != "PASS":
        return None
    first_zone_start = start + max(3, int(duration * 0.15))
    first_zone_end = start + max(5, int(duration * 0.55))
    second_zone_start = start + max(6, int(duration * 0.55))
    second_zone_end = start + max(8, int(duration * 0.92))
    if second_zone_end <= second_zone_start or first_zone_end <= first_zone_start:
        return None
    first_bottom = _argmin(rows, "low", first_zone_start, first_zone_end)
    second_bottom = _argmin(rows, "low", second_zone_start, min(second_zone_end, end + 1))
    if second_bottom - first_bottom < 5:
        return None
    middle_peak = _argmax(rows, "high", first_bottom + 1, second_bottom)
    first_low = _price(rows[first_bottom], "low")
    second_low = _price(rows[second_bottom], "low")
    middle_high = _price(rows[middle_peak], "high")
    low_delta = abs(second_low / first_low - 1.0)
    if low_delta > policy.double_bottom_low_tolerance:
        return None
    if middle_high / first_low - 1.0 < policy.double_bottom_min_middle_rebound:
        return None
    prebase_high_index = _argmax(rows, "high", start, first_bottom + 1)
    prebase_high = _price(rows[prebase_high_index], "high")
    depth = _depth(prebase_high, min(first_low, second_low))
    if depth > 0.50:
        return None
    fault_flags: list[str] = []
    if second_low >= first_low:
        fault_flags.append("SECOND_LOW_DID_NOT_UNDERCUT_FIRST")
    confidence = 0.78 + 0.10 * (1.0 - low_delta / policy.double_bottom_low_tolerance)
    if second_low < first_low:
        confidence += 0.05
    return _candidate(
        rows=rows,
        pattern_type="DOUBLE_BOTTOM",
        start=start,
        end=end,
        low_index=first_bottom if first_low <= second_low else second_bottom,
        prior_state=prior_state,
        confidence=confidence,
        pivot_level=middle_high,
        pivot_landmark_type="middle_peak",
        pivot_source_index=middle_peak,
        landmarks={
            "first_bottom": {"date": _date(rows[first_bottom]), "price": first_low},
            "middle_peak": {"date": _date(rows[middle_peak]), "price": middle_high},
            "second_bottom": {"date": _date(rows[second_bottom]), "price": second_low},
        },
        fault_flags=fault_flags,
    )


def _mark_ambiguity(candidates: list[PatternCandidate]) -> None:
    for i, left in enumerate(candidates):
        overlaps: list[str] = []
        for j, right in enumerate(candidates):
            if i == j or left.pattern_type == right.pattern_type:
                continue
            if left.base_end_or_breakout_ready_date != right.base_end_or_breakout_ready_date:
                continue
            if abs(left.confidence - right.confidence) <= 0.05:
                overlaps.append(right.pattern_type)
        if overlaps:
            left.pattern_evidence_state = "AMBIGUOUS"
            left.ambiguity_with = sorted(set(overlaps))


def detect_patterns(
    raw_rows: Iterable[dict[str, Any]],
    policy: EnginePolicy = DEFAULT_POLICY,
    *,
    min_confidence: float = 0.75,
) -> list[PatternCandidate]:
    """Detect named base candidates using only contemporaneous OHLCV geometry.

    The function intentionally returns zero candidates when the window does not
    satisfy a named morphology; it never forces a label.
    """

    rows = normalize_rows(raw_rows)
    n = len(rows)
    candidates: list[PatternCandidate] = []

    for end in range(n):
        # Flat base windows.
        for duration in range(policy.flat_min_sessions, policy.flat_max_sessions + 1):
            start = end - duration + 1
            if start < 0:
                continue
            candidate = detect_flat_base(rows, start, end, policy)
            if candidate and candidate.confidence >= min_confidence:
                candidates.append(candidate)

        # Cup family. Use a sparse but deterministic duration grid, plus the
        # exact maximum feasible duration, to avoid outcome-dependent search.
        max_cup = min(policy.cup_max_sessions, end + 1)
        cup_durations = list(range(policy.cup_min_sessions, max_cup + 1, 5))
        if max_cup >= policy.cup_min_sessions and max_cup not in cup_durations:
            cup_durations.append(max_cup)
        for duration in cup_durations:
            start = end - duration + 1
            cwh = detect_cup_with_handle(rows, start, end, policy)
            if cwh and cwh.confidence >= min_confidence:
                candidates.append(cwh)
            cwo = detect_cup_without_handle(rows, start, end, policy)
            if cwo and cwo.confidence >= min_confidence:
                candidates.append(cwo)

        # Double-bottom windows.
        max_db = min(policy.double_bottom_max_sessions, end + 1)
        db_durations = list(range(policy.double_bottom_min_sessions, max_db + 1, 5))
        if max_db >= policy.double_bottom_min_sessions and max_db not in db_durations:
            db_durations.append(max_db)
        for duration in db_durations:
            start = end - duration + 1
            candidate = detect_double_bottom(rows, start, end, policy)
            if candidate and candidate.confidence >= min_confidence:
                candidates.append(candidate)

    # Deduplicate exact morphology/landmark repeats created by adjacent window lengths.
    best: dict[tuple[str, str, str, str], PatternCandidate] = {}
    for candidate in candidates:
        key = (
            candidate.pattern_type,
            candidate.base_start_date,
            candidate.base_end_or_breakout_ready_date,
            candidate.pivot_source_date,
        )
        previous = best.get(key)
        if previous is None or candidate.confidence > previous.confidence:
            best[key] = candidate
    deduped = sorted(
        best.values(),
        key=lambda c: (c.base_end_or_breakout_ready_date, -c.confidence, c.pattern_type, c.base_start_date),
    )
    _mark_ambiguity(deduped)
    return deduped
