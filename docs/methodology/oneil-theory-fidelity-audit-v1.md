# O'Neil Theory Fidelity Audit v1

Date: 2026-09-12
Status: ACTIVE

## Purpose
Audit frozen CAN SLIM quantitative v1 against William J. O'Neil / IBD methodology. Theory first: `Theory -> specification -> implementation -> validation -> performance`. The 10,731 v1 candidates remain evidence for the old proxy, not CAN SLIM ground truth.

## Workstream status
| # | Workstream | Status |
|---|---|---|
| 25 | Theory Fidelity Audit | ACTIVE |
| 26 | Proper-base definitions | COMPLETE — theory audit |
| 27 | Pivot / buy-point definition | COMPLETE — theory audit |
| 28 | Breakout + volume confirmation | COMPLETE — theory audit |
| 29 | RS / leadership fidelity | NEXT |
| 30 | C/A/S/I/M role fidelity | NOT STARTED |
| 31 | Sell / risk-management fidelity | NOT STARTED |
| 32 | Theory-faithful candidate specification | NOT STARTED |
| 33 | O'Neil Pattern Recognition Engine | NOT STARTED |
| 34 | Theory-faithful candidate generator | NOT STARTED |
| 35 | New-candidate validation | NOT STARTED |
| 36 | Execution / entry research | PARKED |

## #26 Proper Base — conclusion
Overall v1 proper-base fidelity: **WEAK_PROXY**. The generic prior-35-session/depth<=40% rule captures consolidation broadly but not O'Neil-specific morphology. Future specification must distinguish cup with handle, cup without handle/cup base, double bottom, flat base, and preserve base-on-base, ascending base and IPO-base special structures. No detector thresholds are authorized by #26.

## #27 Pivot / Buy Point — conclusion
Overall v1 pivot fidelity: **WEAK-to-REASONABLE_PROXY**.

```text
pivot_level = pattern-specific structural resistance
```

| Pattern | Structural pivot |
|---|---|
| Cup with handle | highest price in valid handle |
| Cup without handle / cup base | prior / left-side high |
| Double bottom | middle peak of W |
| Flat base | base / left-side high |
| Ascending base | final / pattern structural resistance |
| Base-on-base | pivot from second-base morphology |

Legacy fixed-price buffers above resistance must remain documented as legacy. The 5% buy zone is execution/anti-chasing, not pivot definition. Early/aggressive entries remain separate and X1-X4 remain parked.

## #28 Breakout + Volume Confirmation — conclusion
Overall v1 breakout/volume fidelity: **REASONABLE_PROXY**. Its volume rule is highly faithful; its daily-close condition is stricter than the theory trigger and it conflates the 5% execution zone with candidate-day screening.

### Breakout event vs breakout quality
A conventional breakout begins when price **passes/clears the proper pattern-specific buy point**. IBD material supports acting as the stock reaches/moves through the buy point during the session. A close above resistance and a close high in the day's range are desirable strength evidence, but daily close above pivot is not the universal definition of whether a pivot crossing occurred.

Carry separately into #32:

```text
pivot_crossed_intraday
close_above_pivot
close_position_quality
```

A theory-faithful engine must preserve the first pivot-cross event even if the stock later closes below the pivot; the close can downgrade breakout quality rather than erase the event.

### Volume confirmation
Current IBD guidance repeatedly uses **at least 40% above average volume** as the normal minimum for a proper breakout. Detailed IBD educational material identifies the reference as the **50-day average daily volume**. Historical IBD material often said 40–50%; current material commonly states >=40%.

Canonical daily-EOD measure for #32:

```text
volume_ratio = Volume(T0) / mean(Volume of prior 50 completed sessions)
strong_volume_confirmed = volume_ratio >= 1.40
```

T0 must be excluded from its own baseline. The threshold is a general minimum, not a guarantee; small/mid-cap leaders may be expected to show materially greater expansion.

### Initial-day vs later confirmation
Strong volume on the **initial breakout day** is preferred and is the canonical textbook confirmation. IBD also recognizes an initially light breakout that receives stronger volume in the next few sessions. Preserve chronology:

```text
breakout_date
volume_confirmed_on_breakout
later_volume_confirmation_date  # optional
```

A low-volume pivot cross is not equivalent to a fully confirmed textbook breakout. #32 must define a short explicit confirmation window if later confirmation is supported; implementation must never backdate later volume to make T0 appear confirmed.

### Gap breakouts
A gap through a proper pivot can be a legitimate and powerful breakout. Daily OHLCV R2 can identify `Open > pivot`, gap magnitude, daily price action and daily volume. Current IBD also describes special breakaway-gap entry protocols using 5/15-minute bars when the gap opens far beyond the traditional buy zone. Daily R2 **cannot** reproduce that intraday entry protocol; that belongs to #36 and must not be fabricated.

### 5% buy zone
The normal range `[pivot, pivot*1.05]` is an execution/extension concept, not breakout identity. A stock may validly break out and then become >5% extended; that makes a traditional entry unattractive, not the breakout nonexistent.

### Audit of frozen v1
Frozen v1 uses:

```text
T0 Close > pivot
T0 Close <= pivot * 1.05
T0 Volume >= 1.40 * prior-50-session average Volume
```

| v1 component | Verdict | Reason |
|---|---|---|
| `Close > pivot` | **OVER-STRICT PROXY** | end-of-day hold is quality evidence; crossing the proper pivot is the underlying breakout event |
| `Close <= pivot*1.05` | **SEMANTIC MISMATCH / REASONABLE EXECUTION PROXY** | 5% is buy-zone/anti-chasing guidance, not breakout definition |
| `Volume >=1.40x prior 50d avg` | **HIGH FIDELITY** | matches current general IBD minimum and comparison concept |
| confirmation only on T0 | **TOO STRICT FOR FULL THEORY** | initial-day confirmation preferred, but later volume can confirm an initially light move |
| gap handling | **PARTIAL** | daily OHLCV can detect a gap breakout; special intraday gap entry cannot be reconstructed |

### Frozen #28 principles for #32
1. Separate breakout event from breakout quality.
2. Tie breakout to the pattern-specific pivot from #27.
3. Do not require daily close above pivot merely to acknowledge a pivot cross.
4. Preserve close-above-pivot and close-in-range as quality evidence.
5. Use >=1.40x prior 50-session average daily volume as canonical strong-volume confirmation.
6. Prefer initial-day confirmation; preserve any later confirmation with its true date/state.
7. A low-volume cross is not a fully confirmed textbook breakout.
8. Gap-through-pivot can be valid; daily data cannot reproduce special intraday gap-entry mechanics.
9. Keep the 5% buy zone as execution/extension state, not breakout identity.
10. Do not tune these rules from CAGR/PF before #32 is frozen.

## #33 — O'Neil Pattern Recognition Engine
After #32 is frozen, #33 will translate the theory specification into reproducible pattern/landmark recognition using existing daily OHLCV R2. Scope includes base segmentation, swing/landmark extraction, named-pattern detectors, base relationships, quality/fault flags, ambiguity handling and morphology validation. It must not optimize definitions against trading performance.

## Guardrails
- Do not retrofit theory-fidelity changes into FWD1.
- Do not mix EXH2 with this audit.
- Do not optimize X3 or other entry rules now.
- Do not tune pattern/breakout thresholds from historical returns.
- Do not treat v1 candidates as O'Neil ground truth.
- Do not start #33 before #32 is frozen.
- Preserve explicit uncertainty/evidence states rather than forcing full confirmation.

## Next action
Proceed with **#29 — RS / Leadership Fidelity**. After #29–31, freeze #32 before any #33 implementation.