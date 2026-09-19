# Historical Golden-Case Reconstruction v1

Status: ACTIVE / VALIDATION ONLY / NEVER PRODUCTION

This workstream is isolated from CAN SLIM v2 production. It must not modify production READY pointers, candidate publication, frozen O'Neil Pattern Engine semantics, or live execution/lifecycle state.

## Purpose

Replay documented historical O'Neil/CAN SLIM examples using historical data available at the relevant date, then compare the frozen engine's observed result with a source-backed reference oracle. This is not a backtest.

## Non-negotiable boundaries

- Reconstruction means historical/as-of data, not current 2026 READY data.
- C/A may be accepted as REFERENCE_PASS when an authoritative example explicitly documents the relevant fundamental evidence.
- Expected pattern/pivot/breakout facts are oracle fields only; never detector inputs.
- Canonical frozen O'Neil Pattern Engine: azharmz/ussy-oneil-patterns at c433cc1e35a5aa32a46f732cd8c5545935e36e40; schema oneil-pattern-output-v2; engine 33-core-p8-frozen-v1.
- Mismatch is validation evidence, not permission to tune morphology.
- Artifacts: HISTORICAL_RECONSTRUCTION_FIXTURE / NEVER_PRODUCTION.

## Two entry layers

Original O'Neil/source-faithful: assess the breakout-day T buy opportunity from proper base, pivot/buy point, price-volume action and buy zone. Do not impose USSY T+1 Open.

USSY adaptation: after completed T daily data is known, evaluate the frozen causal T+1 Open contract. A valid original breakout may coexist with USSY MISSED_EXTENDED; classify that as an execution-adaptation gap.

Daily OHLCV cannot reconstruct exact intraday ordering/cumulative volume at crossing; label this limitation explicitly.

## Methodology classification

Tag every reconstructed field/rule: ORIGINAL, OPERATIONALIZATION, DATA_ADAPTATION, PROXY, ENGINEERING, or UNAVAILABLE. USSY cross-sectional RS is a proxy/data adaptation, not the proprietary IBD RS Rating.

## Golden Case 001 — LRCX 2020 — ORACLE VERIFIED

Authoritative source:
- Investor's Business Daily, "How To Buy Stocks: Lam Research's Cup With Handle Launched A 75% Advance"
- https://www.investors.com/how-to-invest/investors-corner/how-to-buy-stocks-lam-research-cup-with-handle-launched-75-percent-advance/

Source facts verified directly for the reconstruction oracle:
- expected family: CUP_WITH_HANDLE
- reported pivot/buy point: 381.96
- reported breakout date: 2020-11-04
- base duration: 13 weeks
- base depth: 24%
- handle duration: two weeks
- prior advance: more than 113%
- quarterly earnings growth: 78%
- sales/revenue growth: 47%
- the later ~75% advance is context only and MUST NOT be supplied to signal-time reconstruction

Oracle state: FROZEN_SOURCE_ORACLE_V1.
Do not silently add facts not explicitly supported by the source. Subsequent return is not a validation target.


## LRCX replay finding — frozen evidence

Replay lineage:
- reconstruction branch: validation/historical-golden-reconstruction-v1
- frozen pattern engine: c433cc1e35a5aa32a46f732cd8c5545935e36e40
- price basis: DATA_ADAPTATION restoring the contemporaneous pre-2024 10-for-1 split basis
- detector cutoff: 2020-11-04; T+1 bar is excluded from detector input

Expected vs observed morphology:
- Oracle CUP_WITH_HANDLE structure is present in the frozen landmark vocabulary: 2020-08-03 high 387.70 -> 2020-09-11 low 292.28 -> 2020-10-14 right rim 381.96 -> 2020-10-28 handle low 333.31.
- Exact cup body is CUP_RECOGNIZED with no cup faults; depth 24.6118%, 52 sessions, right-rim/left-rim ratio 98.52%.
- Open-right-edge handle is causally observable by 2020-11-04, but frozen handle semantics return HANDLE_REJECTED solely for BELOW_CUP_MIDPOINT. Its depth is 12.737%.
- The implied open-right-edge pivot is 381.95999, an exact practical match to the 381.96 source oracle.
- Therefore the final CWH mismatch is localized to handle morphology semantics, not candidate OHLCV, cup landmarks, cup segmentation, cup-body recognition, or pivot reconstruction.
- Classification: MORPHOLOGY_FIDELITY_GAP / HANDLE_GATE_BELOW_CUP_MIDPOINT. No frozen-engine tuning is authorized by this finding.

Breakout-day observation (ORIGINAL layer):
- 2020-11-04 OHLC on contemporaneous basis: O 373.89 / H 383.20 / L 367.28 / C 380.34.
- The daily high crossed the 381.96 pivot, while the close finished 0.424% below pivot.
- Daily-bar evidence therefore supports BREAKOUT_DAY_CONFIRMED_FROM_DAILY_BAR for a price crossing, with INTRADAY_ENTRY_TIMING_NOT_RECONSTRUCTED.
- Observed volume was 1,528,000 versus prior-50-session mean about 1,760,441 (-13.20%). This raw daily comparison does not independently reproduce a strong +40% volume-confirmation condition. Preserve the distinction between the official source oracle and this reconstructed provider/bar calculation.

USSY T+1 observation (OPERATIONALIZATION layer):
- 2020-11-05 open: 390.00.
- T+1 open was +2.105% versus the 381.96 pivot and +2.540% versus the breakout-day close.
- 390.00 remained inside the original 5% buy zone upper bound of 401.058.
- This is an execution observation only. It does not override the frozen CAN SLIM candidate eligibility result or retroactively convert the rejected frozen handle into a production candidate.

Three-layer disposition:
| Layer | Reference / expected | Observed | Classification |
|---|---|---|---|
| O'Neil morphology | CWH, 24% depth, pivot 381.96 | cup/pivot reconstructed; handle rejected BELOW_CUP_MIDPOINT | FIDELITY GAP |
| Original breakout day | breakout 2020-11-04 | high crossed pivot; close below; reconstructed volume not elevated vs prior-50 mean | DAILY-BAR PARTIAL / SOURCE ORACLE PRESERVED |
| USSY execution adaptation | evaluate only after finalized T | T+1 open 390.00, within 5% buy zone | EXECUTION OBSERVATION; NO RETROACTIVE FILL |


## Historical L comparison-universe decision v1

Status: FROZEN FOR GOLDEN RECONSTRUCTION / NOT PRODUCTION.

The production L gate is a cross-sectional RS proxy percentile and therefore cannot be reconstructed from LRCX alone. A 2026 READY/Musaffa membership must not be projected backward to 2020.

Source audit found no existing PIT historical US-wide membership asset in ussy-data or this repository. The research-quality reference is a survivorship-aware security master such as CRSP, but no licensed CRSP dataset is available in this workstream. Free/current exchange lists are not acceptable substitutes for an exact 2020-11-04 broad-universe membership.

For Golden Case 001, freeze:
- L_individual_state: NOT_EVALUABLE
- reason: HISTORICAL_COMPARISON_UNIVERSE_NOT_AVAILABLE
- rs_proxy_percentile: null
- proprietary historical IBD RS Rating, if later sourced, is REFERENCE ORACLE only and must not be substituted for the USSY cross-sectional proxy.
- current/future survivor membership must not be back-projected.

This is a data-availability limitation, not an L FAIL and not permission to invent a smaller comparison set. The case remains useful because frozen morphology and breakout-volume gates already determine v2 ineligibility independently of L.

A future reusable historical-L fixture may replace NOT_EVALUABLE only when it pins a defensible PIT membership source, identity rules, decision date, constituent manifest checksum, OHLCV lineage, RS formula/version and producer identity. Such a fixture is isolated historical reconstruction data and must never advance production READY pointers.


## Golden Case 001 — consolidated CAN SLIM v2 eligibility

Decision date: 2020-11-04. This section evaluates the frozen production-v2 contract without changing any upstream evidence.

| Frozen v2 gate | Reconstructed state | Eligibility effect |
|---|---|---|
| Watchlist C/A | NOT EVALUABLE AS QUALIFIED: C quarterly reference is documented, but required A annual evidence is not documented | WATCHLIST_NOT_QUALIFIED |
| Pattern | expected source CWH; frozen engine does not recognize the source-faithful handle (BELOW_CUP_MIDPOINT) | PATTERN_NOT_RECOGNIZED |
| Pivot | defined at 381.95999 and daily high crossed it | passes pivot-defined / pivot-crossed gates |
| Breakout volume | reconstructed daily volume does not meet the frozen >=1.40 prior-50-volume confirmation rule | BREAKOUT_VOLUME_UNCONFIRMED |
| L | NOT_EVALUABLE because no defensible PIT historical comparison universe is available | L_NOT_EVALUABLE |
| M | FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS from the frozen historical index-only replay | passes M gate |

Frozen v2 disposition: **NOT_ELIGIBLE**.

Reason set: WATCHLIST_NOT_QUALIFIED; PATTERN_NOT_RECOGNIZED; BREAKOUT_VOLUME_UNCONFIRMED; L_NOT_EVALUABLE.

M is not a blocker. Pivot definition/crossing are not blockers.

This disposition must not be read as a claim that the documented O'Neil trade was invalid. It answers the separate production-adaptation question: the frozen USSY CAN SLIM v2 contract would not have produced an eligible candidate from the reconstructed evidence available here. The principal source-fidelity discrepancy remains the handle morphology gate; the reconstructed breakout-volume rule is an additional production-contract mismatch. Missing A/L evidence remains NOT_EVALUABLE rather than FAIL.

The T+1 open of 390.00 therefore remains an execution observation only: no production fill is authorized because eligibility was false before the execution layer.


## Golden Case 002 — AMD 2019 — MORPHOLOGY/BREAKOUT REPLAY VERIFIED

Decision/breakout date: 2019-11-04.

Frozen source oracle for the replay:
- expected family: CUP_WITHOUT_HANDLE
- reported pivot/buy point: 35.55
- reported breakout date: 2019-11-04
- source-reported cup low: 27.43
- source context reports breakout volume about 67% above average
- quarterly reference evidence is C-layer evidence only; do not infer A annual evidence from it

Replay identity:
- branch: validation/historical-golden-reconstruction-v1
- successful run: 35411908528
- producer commit: 09aeb26b0a49ddb72efe179072ff2cca5d0ae87c
- frozen Pattern Engine: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- candidate detector cutoff: 2019-11-04; T+1 2019-11-05 is excluded from detector input
- candidate price basis: provider historical basis unchanged; no reconstruction split transform applied

Source-fidelity morphology finding:
- Frozen engine emits a source-faithful OPEN_RIGHT_EDGE_CNH candidate with LEFT_RIM 2019-08-09, CUP_LOW 2019-10-03, pivot_source_date 2019-08-09 and pivot 35.54999924.
- Candidate state: CUP_WITHOUT_HANDLE_RECOGNIZED / RECOGNIZED.
- Candidate depth: 22.841066%; detector_faults: [].
- Observed trough price is 27.43 and pivot is an exact practical match to the 35.55 oracle.
- Therefore AMD provides a positive source-fidelity case for frozen CUP_WITHOUT_HANDLE morphology and pivot reconstruction. Other emitted historical candidates are not substituted for the source-faithful candidate.

Breakout-day observation (ORIGINAL layer):
- 2019-11-04 OHLC: O 35.189999 / H 36.450001 / L 34.759998 / C 36.290001.
- Both daily high and close are above the 35.55 pivot; close is +2.0816% versus pivot and remains inside the original 5% buy zone upper bound 37.3275.
- Volume: 83,343,800 versus frozen prior-50 completed-session mean 49,447,172, or +68.5512% / ratio 1.6855.
- This exceeds the frozen USSY >=1.40 breakout-volume confirmation threshold and closely corroborates the source-reported approximately +67% volume expansion.
- Daily bars support BREAKOUT_DAY_CONFIRMED_FROM_DAILY_BAR. Exact intraday crossing/cumulative-volume sequence remains INTRADAY_ENTRY_TIMING_NOT_RECONSTRUCTED.

Historical M (DATA_ADAPTATION layer):
- market_state: FOLLOW_THROUGH_CONFIRMED.
- M_entry_state: ALLOW_NEW_BUYS.
- reason: NO_NEW_STATE_CHANGING_EVIDENCE / M45_NEW_ENTRIES_ALLOWED.
- provenance: HISTORICAL_INDEX_ONLY_FROZEN_46_REPLAY, adapter fa-first-historical-m-adapter-v0.1.
- The index-only limitation remains explicit; leadership/weakening/correction-reset facts are not fabricated.

USSY T+1 observation (OPERATIONALIZATION layer):
- 2019-11-05 open: 36.560001.
- T+1 open is +2.8411% versus pivot and +0.7440% versus breakout-day close.
- T+1 open remains inside the original 5% buy zone.
- Therefore this case does not exhibit a T+1 extended-price adaptation gap. This is still an execution observation, not an automatic production fill.

Three-layer disposition:
| Layer | Reference / expected | Observed | Classification |
|---|---|---|---|
| O'Neil morphology | CUP_WITHOUT_HANDLE, pivot 35.55 | source-faithful candidate RECOGNIZED; pivot 35.549999; trough 27.43; no faults | SOURCE-FIDELITY MATCH |
| Original breakout day | breakout 2019-11-04 with strong volume | high/close above pivot; volume ratio 1.6855; close inside 5% zone | DAILY-BAR MATCH; INTRADAY TIMING UNAVAILABLE |
| USSY execution adaptation | evaluate after finalized T | T+1 open 36.56, +2.84% vs pivot, inside 5% zone | NO EXTENDED-PRICE ADAPTATION GAP |

Historical L follows the frozen Golden Case 001 governance: no defensible PIT broad comparison-universe asset is available in this workstream. Freeze L_individual_state=NOT_EVALUABLE / HISTORICAL_COMPARISON_UNIVERSE_NOT_AVAILABLE rather than back-projecting a current universe.

### Golden Case 002 — current CAN SLIM v2 reconstruction boundary

The morphology, pivot, breakout-volume and M hard gates are positively reconstructed for AMD. Historical L remains NOT_EVALUABLE. C quarterly reference evidence may be recorded as reference evidence, but A annual evidence must remain NOT_DOCUMENTED unless an authoritative source is frozen. Therefore do not label the complete frozen-v2 candidate ELIGIBLE yet; missing watchlist C/A qualification and L remain evidence-availability blockers, not negative morphology/breakout findings.

The important validation result is narrower and stronger: unlike LRCX, AMD reproduces the documented O'Neil pattern family, pivot and breakout-volume behavior under the frozen engine without tuning.


## Golden Case 003 — IPHI 2019 — DOUBLE-BOTTOM FIDELITY/LIFECYCLE REPLAY VERIFIED

Decision/breakout date: 2019-10-15.

Frozen source oracle:
- expected family: DOUBLE_BOTTOM
- reported pivot/buy point: 64.85
- reported breakout date: 2019-10-15
- source context: third-stage double-bottom; breakout subsequently failed and the historical example invokes the O'Neil loss-cut discipline

Replay identity:
- successful lifecycle run: 35413742554
- producer commit: 8b88fe1f0da94c1b9a434da62b19a92f2700f7ff
- frozen Pattern Engine: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- candidate provider: Tiingo fallback because Yahoo/yfinance no longer returned the delisted symbol
- detector cutoff: 2019-10-15; post-T bars are excluded from morphology and revealed only for lifecycle
- provider historical basis unchanged; no corporate-action transform applied

Source-fidelity morphology finding:
- The closest frozen-engine DOUBLE_BOTTOM uses LEFT_HIGH 2019-08-08, TROUGH_1 2019-08-28, MIDDLE_PEAK 2019-09-20 and TROUGH_2 2019-10-02.
- Engine pivot is 64.75 versus source oracle 64.85, a 0.10 absolute difference.
- Candidate state is DOUBLE_BOTTOM_AMBIGUOUS / AMBIGUOUS with fault NO_SECOND_TROUGH_UNDERCUT.
- Therefore the engine reconstructs the intended structural neighborhood and near-matching pivot but does not recognize the documented double bottom under its frozen second-trough-undercut gate.
- Classification: MORPHOLOGY_FIDELITY_GAP / NO_SECOND_TROUGH_UNDERCUT. No detector threshold is changed.

Breakout-day observation (ORIGINAL layer):
- 2019-10-15 OHLC: O 63.41 / H 66.20 / L 63.41 / C 64.99.
- Daily high and close are above oracle pivot 64.85; close is +0.2159% versus pivot and inside the 5% buy zone.
- Volume 983,203 versus prior-50 completed-session mean 857,768.86, or +14.6233% / ratio 1.1462.
- This does not meet the frozen USSY >=1.40 breakout-volume confirmation threshold.
- Daily bars establish price crossing but not exact intraday crossing/cumulative-volume timing.

Historical M:
- FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS on 2019-10-15.
- provenance: HISTORICAL_INDEX_ONLY_FROZEN_46_REPLAY.
- M is not a blocker in this reconstruction.

USSY T+1 observation:
- 2019-10-16 open: 65.06.
- +0.3238% versus oracle pivot and +0.1077% versus breakout close.
- Open remains inside the original 5% buy zone.
- Therefore there is no T+1 extended-price adaptation gap. This remains an execution observation, not a production fill.

Original O'Neil loss-cut lifecycle observation:
- Reference basis is the oracle pivot 64.85; 7% level = 60.3105 and 8% level = 59.662.
- On 2019-10-22 the daily low reached 59.50, breaching both the -7% and -8% reference levels; close 59.81 was below -7% but still above the -8% close threshold.
- On 2019-10-23 close reached 59.09, the first reconstructed close below the -8% reference level.
- Exact intraday stop timing is not reconstructed from daily bars.
- This causally corroborates the documented failed-breakout/loss-cut character of the golden case without inventing an intraday fill.

Three-layer disposition:

| Layer | Reference / expected | Observed | Classification |
|---|---|---|---|
| O'Neil morphology | DOUBLE_BOTTOM, pivot 64.85 | structural neighborhood reproduced; pivot 64.75; AMBIGUOUS because NO_SECOND_TROUGH_UNDERCUT | MORPHOLOGY_FIDELITY_GAP |
| Original breakout/lifecycle | breakout 2019-10-15 followed by failed trade/loss cut | price crossed pivot; later low breaches 8% on Oct 22 and close breaches 8% on Oct 23 | DAILY-BAR LIFECYCLE CORROBORATION |
| USSY adaptation | evaluate at finalized T then T+1 Open | T+1 65.06, inside 5% zone; morphology and volume hard gates remain unsatisfied | NO EXTENDED-PRICE GAP; NO PRODUCTION FILL |

Historical L remains NOT_EVALUABLE under the same frozen governance as Cases 001-002. The frozen v2 contract also lacks pattern recognition and >=1.40 breakout-volume confirmation here, so this case must not be converted into an eligible production trade merely because the historical source labels it a valid O'Neil setup.


## Golden Case 004 — AAPL 2019 — FLAT-BASE FIDELITY REPLAY VERIFIED

Decision/breakout date: 2019-09-11 (source breakout week ending 2019-09-13).

Frozen source oracle:
- expected family: FLAT_BASE
- pivot/buy point: 221.37
- breakout observation date used for daily replay: 2019-09-11

Replay identity:
- successful run: 35417737472
- producer commit: 0e5b80786fcee7d50138647ab65e8b2576023ee8
- frozen Pattern Engine: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- Yahoo pre-2020 AAPL bars were restored to contemporaneous 2019 basis for the later 4-for-1 split: OHLC/adj_close x4, volume /4
- detector cutoff remains 2019-09-11

Source-fidelity morphology finding:
- Frozen landmarks independently recover the exact oracle left high: 2019-07-31 at 221.369995.
- Base low is 2019-08-05 at 192.580002, giving depth 13.0054%.
- Frozen FLAT_BASE candidate therefore carries pivot 221.369995, effectively exact to oracle 221.37.
- Confirmed-structure candidate is REJECTED with TOO_SHORT and WIDE_LOOSE; open-right-edge candidate through 2019-09-11 is AMBIGUOUS with WIDE_LOOSE.
- Classification: MORPHOLOGY_FIDELITY_GAP / FLAT_BASE_GEOMETRY_GATE. No detector threshold is changed.

Breakout-day observation:
- 2019-09-11 OHLC: O 218.07 / H 223.71 / L 217.73 / C 223.59.
- High and close exceed 221.37; close is +1.0028% versus pivot and remains in the 5% buy zone.
- Volume 44,289,600 versus prior-50 completed-session mean 25,930,154: +70.8035%, ratio 1.7080.
- The frozen USSY >=1.40 breakout-volume threshold therefore passes.

Historical M:
- FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS on 2019-09-11.
- provenance: HISTORICAL_INDEX_ONLY_FROZEN_46_REPLAY.
- M is not a blocker.

USSY T+1 observation:
- 2019-09-12 open: 224.80.
- +1.5494% versus pivot and +0.5412% versus breakout close.
- T+1 open remains inside the original 5% buy zone.
- Therefore there is no extended-price execution-adaptation gap.

Three-layer disposition:

| Layer | Expected | Observed | Classification |
|---|---|---|---|
| O'Neil morphology | FLAT_BASE, pivot 221.37 | exact left-high/pivot recovered; candidate not RECOGNIZED because TOO_SHORT/WIDE_LOOSE or WIDE_LOOSE | MORPHOLOGY_FIDELITY_GAP |
| Original breakout | price-volume breakout through 221.37 | high/close above pivot; prior-50 volume ratio 1.7080 | DAILY-BAR BREAKOUT CORROBORATION |
| USSY adaptation | finalized T then T+1 Open | 224.80, +1.55% vs pivot, inside 5% zone | NO EXTENDED-PRICE GAP; pattern gate prevents production eligibility |

Historical L remains NOT_EVALUABLE under frozen governance. This case completes first-pass coverage of all four frozen core morphology families without tuning the detector.


## Cross-case fidelity matrix v1 — first-pass adjudication

Status: FIRST-PASS COMPLETE / VALIDATION EVIDENCE / NO ENGINE CHANGE AUTHORIZED.

| Case | Frozen core family | Oracle pivot | Engine pivot | Morphology result | Breakout-volume reconstruction | Historical M | T+1 vs 5% zone | Primary finding |
|---|---|---:|---:|---|---|---|---|---|
| LRCX 2020 | CUP_WITH_HANDLE | 381.96 | 381.95999 | cup/pivot match; final handle rejected | below frozen 1.40 threshold | ALLOW_NEW_BUYS | inside | HANDLE_GATE_BELOW_CUP_MIDPOINT fidelity gap |
| AMD 2019 | CUP_WITHOUT_HANDLE | 35.55 | 35.549999 | RECOGNIZED, no faults | 1.6855, passes | ALLOW_NEW_BUYS | inside | positive morphology/pivot fidelity control |
| IPHI 2019 | DOUBLE_BOTTOM | 64.85 | 64.75 | AMBIGUOUS | 1.1462, fails | ALLOW_NEW_BUYS | inside | NO_SECOND_TROUGH_UNDERCUT fidelity gap |
| AAPL 2019 | FLAT_BASE | 221.37 | 221.369995 | REJECTED/AMBIGUOUS | 1.7080, passes | ALLOW_NEW_BUYS | inside | FLAT_BASE geometry-gate fidelity gap |

### What the four cases establish

1. Pivot reconstruction is not the dominant problem in this first-pass suite. LRCX, AMD and AAPL reproduce the source pivot to practical equality; IPHI differs by only 0.10.
2. The principal source-fidelity discrepancies are localized morphology semantics, not an inability to locate the relevant price structures:
   - CWH: handle upper-half gate (`BELOW_CUP_MIDPOINT`).
   - DOUBLE_BOTTOM: strict second-trough-undercut gate (`NO_SECOND_TROUGH_UNDERCUT`).
   - FLAT_BASE: duration/tightness geometry (`TOO_SHORT` / `WIDE_LOOSE`).
3. CUP_WITHOUT_HANDLE has a positive historical control: AMD is recognized with source-faithful pivot/trough and no detector faults. Therefore the suite is not merely a collection of detector failures.
4. Breakout-volume adaptation is independently material. AMD and AAPL pass the frozen >=1.40 prior-50 threshold; LRCX and IPHI do not. This is separate from morphology fidelity.
5. Historical M is not responsible for any of the four discrepancies: every replay returns `ALLOW_NEW_BUYS` under the frozen historical index-only adapter.
6. T+1 Open is not the source of rejection in these four examples. Every reconstructed T+1 open remains inside the original 5% buy zone. This does not prove T+1 is generally harmless; it only bounds these four cases.
7. Historical L remains intentionally NOT_EVALUABLE because no defensible PIT broad comparison universe is frozen. This must not be converted to either PASS or FAIL.

### Action classification

| Finding | Action now | Production implication |
|---|---|---|
| AMD CWOH positive match | PRESERVE as regression control | none; confirms one frozen family can reproduce a documented example |
| LRCX handle gate | OPEN VALIDATION QUESTION | no production change; research whether the frozen upper-half requirement is source-faithful across multiple authoritative CWH examples |
| IPHI second-trough undercut gate | OPEN VALIDATION QUESTION | no production change; research whether strict undercut is universal, optional, or provider-sensitive |
| AAPL flat-base geometry gates | OPEN VALIDATION QUESTION | no production change; determine whether daily detector duration/tightness semantics align with documented weekly flat-base examples |
| Breakout-volume mismatches | KEEP SEPARATE FROM MORPHOLOGY | do not alter morphology to compensate for volume behavior |
| Historical L unavailable | DATA GAP / HOLD | acquire defensible PIT universe only if justified; never back-project current membership |
| T+1 observations | PRESERVE AS ADAPTATION EVIDENCE | no rule change from four cases |

### Decision gate before any engine revision

No frozen-engine modification is justified by one golden case. A morphology rule may move from validation question to change proposal only after:
- multiple independent authoritative examples for the same family are reconstructed;
- the discrepancy repeats under defensible historical price bases/providers;
- the source methodology supports the proposed semantic interpretation;
- positive controls and counterexamples are included so relaxing a gate is not evaluated only on cases it would rescue;
- the proposal is reviewed separately from this historical-reconstruction branch.

Until that evidence exists, `c433cc1e35a5aa32a46f732cd8c5545935e36e40` remains the authoritative frozen Pattern Engine for this workstream.

### Next validation tranche

The next work is **targeted replication**, not broad backtesting and not detector tuning. Priorities:
1. Add at least two independent authoritative examples for each discrepant family: CWH, DOUBLE_BOTTOM and FLAT_BASE.
2. Include at least one source-backed negative/counterexample per family where possible.
3. Replay with the same frozen engine and classify whether each gate discrepancy repeats.
4. Only then issue a morphology-fidelity adjudication for that family: source-faithful, over-restrictive, under-restrictive, or unresolved.

CUP_WITHOUT_HANDLE does not need immediate gate investigation; AMD remains the positive-control case while resources focus on the three observed discrepancy families.


## Targeted replication candidate registry v1

Status: SOURCE DISCOVERY STARTED / ORACLE NOT YET FROZEN.

Purpose: expand only the three morphology families with first-pass fidelity gaps. Candidate inclusion here is not evidence that a setup will rescue or contradict the frozen detector.

### Source-methodology anchors

Authoritative IBD educational material defines the common pattern boundaries used to frame source review:
- CUP_WITH_HANDLE: minimum base length seven weeks; the handle requires at least five trading sessions. The LRCX educational example explicitly notes its handle was two weeks and 13% deep.
- DOUBLE_BOTTOM: IBD's buying checklist describes a seven-week minimum and a buy point above the middle peak of the W.
- FLAT_BASE: minimum five weeks, generally no more than 15% deep; buy point above the highest point in the base.

These are source-methodology anchors only. They do not overwrite the frozen detector semantics.

### Candidate queue

| Priority | Family | Candidate/source | Why useful | Oracle status |
|---|---|---|---|---|
| 1 | FLAT_BASE | Synopsys (SNPS), IBD educational flat-base case | Source describes a six-week flat base and breakout on May 18 with volume 163% above average; directly useful against AAPL TOO_SHORT/WIDE_LOOSE | SOURCE LOCATED; exact year/pivot/date facts must be frozen from article before replay |
| 2 | DOUBLE_BOTTOM | Mobileye (MBLY), IBD Stock Guide Spring 2017 | Source explicitly labels a first-stage eight-week double-bottom base and describes a June 17 move with volume 52% above average | SOURCE LOCATED; determine exact base landmarks/buy point before replay |
| 3 | CUP_WITH_HANDLE | Edwards Lifesciences (EW), IBD Top Stocks 2019 | Source explicitly describes a later solid cup with handle, 16.3% correction and proper buy point 195.10 around July 22-24 | SOURCE LOCATED; freeze exact source chronology before replay |
| 4 | CUP_WITH_HANDLE | BRP Group (BRP), IBD Top Stocks 2020 | Source explicitly identifies a cup-with-handle and new buy point 18.88 | SOURCE LOCATED; may be setup/pre-breakout rather than completed historical breakout, so suitability requires source adjudication |

### Selection rules

A candidate becomes a frozen reconstruction case only when the authoritative source supplies enough information to establish, without chart-fitting:
- symbol and historical period;
- source-labelled pattern family;
- source buy point/pivot or sufficient explicit source structure to identify it;
- breakout/decision date when the validation question requires breakout behavior;
- no use of the expected landmarks as detector inputs.

For each discrepant family, the target remains at least two additional independent authoritative examples plus a negative/counterexample when a defensible source exists.

### Immediate execution order

1. SNPS flat-base source-oracle extraction, because its source-described six-week duration directly tests whether the AAPL geometry discrepancy repeats on an unambiguously >=5-week educational example.
2. MBLY double-bottom source-oracle extraction, because the source explicitly calls the base eight weeks and therefore supplies an independent structural example.
3. EW cup-with-handle source-oracle extraction, with special attention to handle geometry and whether the frozen upper-half gate agrees.
4. BRP is reserve CWH evidence until a completed breakout can be source-frozen.

No detector code or production rule is changed by this registry.


## Golden Case 005 — SNPS flat-base source oracle v1

Status: FROZEN_SOURCE_ORACLE_V1 / REPLAY NOT YET ADJUDICATED.

Authoritative source:
- Investor's Business Daily, "Synopsys Blasted From This Bullish Pattern Found In Many Market Winners."
- The article identifies Synopsys (SNPS) as the educational example.

Source facts frozen as oracle fields:
- expected family: FLAT_BASE
- prior peak / base high: 392.79 on 2023-04-04
- source buy point: 392.79
- base duration: six weeks
- base trading range/depth characterization: tight 8% range
- breakout date: 2023-05-18
- breakout move: gap up 8.7%
- breakout volume: 163% above its 50-day average
- source buy-zone upper bound: 412.43
- prior context: an earlier cup-with-handle breakout occurred Feb. 1; this fact is context only and must not be used to force the flat-base detector

Year resolution:
- RESOLVED: 2023. Independent contemporaneous company evidence places the earnings release on 2023-05-17, immediately before the source-described May 18 breakout; the source chronology also references the May 25 buyback catalyst.
- Replay decision date T is therefore frozen at 2023-05-18; T+1 is 2023-05-19.
- Provider OHLCV must still fail closed if the 2023 fixture does not corroborate the source chronology/price neighborhood.

Validation question:
Does the frozen FLAT_BASE detector independently recover the source-labelled six-week structure and 392.79 pivot when supplied only historical bars through the resolved May-18 decision date?

Special reason for selection:
This is an independent test of the AAPL finding. Unlike AAPL's frozen candidate, the source explicitly characterizes SNPS as a six-week flat base, which is above IBD's five-week educational minimum. If the frozen engine still fails TOO_SHORT, that would materially strengthen the duration-semantics fidelity concern. WIDE_LOOSE must be evaluated separately.

Oracle-input prohibition:
392.79, six weeks, 8%, and May 18 are comparison/oracle fields. They may be used to select and validate the historical fixture, but never injected as detector landmarks or pattern boundaries.

Next checkpoint:
1. resolve/freeze the unique historical year and candidate OHLCV basis;
2. truncate detector input at breakout date T;
3. run frozen engine unchanged;
4. compare emitted FLAT_BASE family, pivot, duration/depth and faults;
5. only afterward reconstruct breakout volume, M and T+1.


## Golden Case 005 — SNPS 2023 — FLAT-BASE REPLICATION VERIFIED

Replay identity:
- successful corrected run: 35418641005
- producer commit: 1d718ae31336491b9929a9c65df3efda99e79c4f
- the earlier run 35418204224 is INVALID AS EVIDENCE because inherited AAPL dates remained in the first SNPS script revision
- frozen Pattern Engine unchanged: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- decision date: 2023-05-18; T+1: 2023-05-19
- provider historical basis unchanged

Source-fidelity morphology finding:
- The frozen engine independently recovers the exact source high/pivot: LEFT_HIGH 2023-04-04, pivot 392.79000854 versus oracle 392.79.
- It independently locates BASE_LOW 2023-04-25 and measures depth 8.2538%, closely consistent with the source's approximately 8% characterization.
- The confirmed-structure FLAT_BASE candidate is REJECTED with TOO_SHORT and WIDE_LOOSE.
- The open-right-edge FLAT_BASE through breakout day preserves the same 2023-04-04 / 2023-04-25 structure and exact pivot, but is AMBIGUOUS with WIDE_LOOSE.
- Therefore the AAPL FLAT_BASE discrepancy repeats on a second independent source-labelled flat base. In SNPS, however, the source explicitly calls the base six weeks, so the frozen TOO_SHORT result is now a stronger duration-semantics fidelity concern rather than merely an uncertain AAPL boundary.
- Classification: REPEATED_MORPHOLOGY_FIDELITY_GAP / FLAT_BASE_DURATION_AND_TIGHTNESS_SEMANTICS.
- No detector rule is changed.

Important cross-pattern observation:
- The same 2023-04-04 pivot / 2023-04-25 low is also emitted as a RECOGNIZED open-right-edge CUP_WITHOUT_HANDLE with no faults.
- A separate longer cup-with-handle candidate using 2023-04-04 as right rim is also recognized.
- These alternate-family outputs do not replace the source oracle. They are evidence that the frozen engine sees the price structure but classifies the source-labelled six-week flat base differently.

Breakout-day observation:
- 2023-05-18 OHLC: O 387.50 / H 410.91 / L 386.50 / C 409.71.
- High and close exceed 392.79; close is +4.3076% versus pivot and remains barely inside the original 5% buy zone upper bound 412.4295.
- Volume 2,005,700 versus prior-50 completed-session mean 738,404: +171.6264%, ratio 2.7163.
- This exceeds the frozen USSY >=1.40 breakout-volume threshold and is directionally consistent with the source's very large breakout-volume expansion.
- Daily bars support BREAKOUT_DAY_CONFIRMED_FROM_DAILY_BAR; exact intraday crossing/cumulative-volume timing is unavailable.

Historical M:
- FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS on 2023-05-18.
- classifier reason: VALID_DAY4_PLUS_FOLLOW_THROUGH.
- provenance: HISTORICAL_INDEX_ONLY_FROZEN_46_REPLAY.
- M is not a blocker.

USSY T+1 execution adaptation:
- 2023-05-19 open: 413.03.
- +5.1529% versus pivot and +0.8103% versus breakout close.
- This is just outside the original 5% buy-zone upper bound 412.4295.
- Classification: MISSED_EXTENDED / T1_OPEN_ABOVE_5PCT_BUY_ZONE.
- This is the first golden reconstruction in the suite where an original breakout-day opportunity and the USSY T+1 Open adaptation materially diverge on the 5% buy-zone rule.

Three-layer disposition:

| Layer | Source / expected | Observed | Classification |
|---|---|---|---|
| O'Neil morphology | six-week FLAT_BASE, pivot 392.79, ~8% range | exact pivot/high and ~8.25% depth recovered; FLAT_BASE rejected/ambiguous on TOO_SHORT/WIDE_LOOSE | REPEATED MORPHOLOGY FIDELITY GAP |
| Original breakout | 2023-05-18 with exceptional volume | high/close above pivot; close +4.31%; volume ratio 2.7163 | DAILY-BAR BREAKOUT CORROBORATION |
| USSY adaptation | finalized T then T+1 Open | 413.03 = +5.153% vs pivot, outside 5% zone | MISSED_EXTENDED / EXECUTION ADAPTATION GAP |

### Flat-base validation state after AAPL + SNPS

The flat-base question is no longer supported by only one golden example:
- AAPL: source pivot exactly recovered; FLAT_BASE fails/ambiguous on TOO_SHORT/WIDE_LOOSE.
- SNPS: source explicitly says six weeks and ~8%; exact pivot and ~8.25% provider depth recovered, yet FLAT_BASE again fails/ambiguous on TOO_SHORT/WIDE_LOOSE.

This is **repeat evidence**, not authorization to relax the detector. At least one further independent authoritative flat-base example and a defensible counterexample/negative control should be reconstructed before a family-level semantic change proposal is considered.


## Golden Case 006 — TSM 2024 — DOUBLE-BOTTOM REPLICATION VERIFIED

Replay identity:
- successful run: 35420754613
- producer commit: 0d28126a589367e2b05b24b6c80161abdbafcd0c
- frozen Pattern Engine unchanged: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- decision date: 2024-05-10; T+1: 2024-05-13
- source oracle: DOUBLE_BOTTOM, buy point 148.43

Source-fidelity morphology finding:
- The frozen engine independently emits a RECOGNIZED DOUBLE_BOTTOM whose pivot is 148.42999268, effectively exact versus the source oracle 148.43.
- Structural signature: LEFT_HIGH 2024-02-09; TROUGH_1 2024-03-19; MIDDLE_PEAK 2024-04-10; TROUGH_2 2024-04-22.
- normalized_status: RECOGNIZED.
- native_state: DOUBLE_BOTTOM_RECOGNIZED.
- detector_faults: [].
- measured depth: 6.9468%.
- Therefore TSM is a positive-control double-bottom case. The IPHI NO_SECOND_TROUGH_UNDERCUT discrepancy does **not** automatically repeat on another authoritative double-bottom.
- Classification: SOURCE_FIDELITY_MATCH / DOUBLE_BOTTOM_POSITIVE_CONTROL.

The detector also emits other alternative DOUBLE_BOTTOM candidates, several with NO_SECOND_TROUGH_UNDERCUT or other faults. Those are not substituted for the source-faithful candidate: the decisive fact is that the frozen engine independently recovers the source pivot 148.43 with a fault-free RECOGNIZED double-bottom.

Breakout-day observation:
- 2024-05-10 OHLC: O 147.22 / H 150.50 / L 146.93 / C 149.26.
- high and close exceed pivot 148.43; close is +0.5592% versus pivot and remains inside the 5% buy zone.
- volume: 23,671,400 versus prior-50 completed-session mean 16,163,340.
- volume expansion: +46.4512%, ratio 1.4645.
- therefore the frozen USSY >=1.40 breakout-volume requirement passes.
- This daily reconstruction corroborates IBD's contemporaneous report that TSM broke out of a double-bottom at 148.43. Exact intraday crossing/cumulative-volume timing is not reconstructed.

USSY T+1 execution adaptation:
- 2024-05-13 open: 148.0200.
- open is -0.2762% below pivot and -0.8308% below breakout close.
- The script's strict original-buy-zone boolean is false because the open is below the pivot, not because price is extended above the 5% upper bound.
- Classification: T1_OPEN_BELOW_PIVOT / NOT_EXTENDED.
- This must not be mislabeled MISSED_EXTENDED. Whether a production order would fill depends on the production entry/order semantics, which is a separate operationalization question.

Double-bottom adjudication after IPHI + TSM:
- IPHI remains a real source-fidelity discrepancy: official source calls the setup DOUBLE_BOTTOM, while the source-near frozen candidate is AMBIGUOUS on NO_SECOND_TROUGH_UNDERCUT.
- TSM is a clean positive control: exact source pivot recovered as DOUBLE_BOTTOM_RECOGNIZED with no faults.
- Consequently the current evidence does **not** justify saying the frozen undercut gate is generally incompatible with O'Neil double bottoms.
- The correct next question is narrower: why does IPHI's documented double bottom fail that gate while TSM passes? Possible explanations to test separately are source morphology nuance, provider/price-basis differences, landmark selection, or an over-restrictive gate for a subset of documented examples.
- No detector change is authorized.

Three-layer disposition:

| Layer | Source / expected | Observed | Classification |
|---|---|---|---|
| O'Neil morphology | DOUBLE_BOTTOM, pivot 148.43 | exact pivot 148.42999268; RECOGNIZED; no faults | SOURCE-FIDELITY MATCH |
| Original breakout | breakout through 148.43 | high/close above pivot; volume ratio 1.4645 | DAILY-BAR BREAKOUT CORROBORATION |
| USSY adaptation | finalized T then T+1 Open | open 148.02, slightly below pivot | T1_OPEN_BELOW_PIVOT / NOT_EXTENDED |

### Double-bottom validation state

TSM changes the interpretation of the IPHI result. The family now has both:
- IPHI: documented DOUBLE_BOTTOM with a localized NO_SECOND_TROUGH_UNDERCUT fidelity gap.
- TSM: documented DOUBLE_BOTTOM with exact pivot and fault-free recognition.

The next double-bottom replication should therefore be selected to discriminate the undercut semantics directly, ideally an authoritative example whose two trough relationship can be reconstructed unambiguously. It should not be chosen merely to accumulate another passing case.


## Golden Case 007 — WMT 2024 — DOUBLE-BOTTOM LANDMARK/SEGMENTATION FIDELITY GAP

Replay identity:
- valid diagnostic run: 35428260263
- producer commit: 6aedc85b7b09c63591d95b112217532366857e37
- frozen Pattern Engine unchanged: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- source oracle: DOUBLE_BOTTOM; pivot 60.89; first low 58.88; second low 58.55; breakout date 2024-05-16
- diagnostic oracle landmarks are comparison-only and are never injected into detector generation.

Detector result:
- no emitted DOUBLE_BOTTOM candidate matched any of the source-target 2024 oracle landmarks used by the diagnostic.
- `oracle_candidate_matches=[]`.
- diagnostic landmark/segment arrays for the source-target path are empty.
- the engine does emit an older, unrelated fault-free DOUBLE_BOTTOM (2023-09-13 / 2023-10-06 / 2023-11-15 / 2023-12-11; pivot 56.64666748). That older candidate must not be substituted for the source-labelled 2024 structure.
- therefore WMT does not test the `NO_SECOND_TROUGH_UNDERCUT` morphology gate at all: the source-target structure fails upstream of morphology assessment.
- boundary diagnostic run `35428665101` localizes the failure further: primary, auxiliary, and fused landmark vocabularies contain no April-May 2024 landmarks; consequently atomic and multiturn segment sets also contain no April-May 2024 structure.
- classification refined to: `MORPHOLOGY_FIDELITY_GAP / LANDMARK_GENERATION_MISS`.
- segmentation is downstream-empty, not independently implicated by this replay.
- no detector change is authorized.

Breakout / execution observations, retained separately from morphology:
- 2024-05-16: O 64.22 / H 64.42 / L 62.94 / C 64.01 versus oracle pivot 60.89.
- close is +5.1240% above pivot, just above the conventional 5% buy-zone ceiling 63.9345.
- volume 60,545,600 versus prior-50 completed-session mean 15,207,442: total ratio 3.9813x, or +298.13% above average.
- T+1 2024-05-17 open 64.24: +5.5017% versus pivot and therefore above the 5% buy zone.
- historical M on 2024-05-16: FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS.
- these observations do not repair the morphology miss and must not be used as detector inputs.

Double-bottom adjudication after IPHI + TSM + WMT:
- IPHI: source-near candidate reaches morphology but is AMBIGUOUS due `NO_SECOND_TROUGH_UNDERCUT`.
- TSM: source structure is independently recovered with exact pivot and fault-free `DOUBLE_BOTTOM_RECOGNIZED`.
- WMT: source-labelled 2024 structure is not emitted because landmark generation itself produces no April-May 2024 landmarks; segmentation is downstream-empty.
- Consequently there is still no evidence that one universal double-bottom gate is the dominant family-level problem. The discrepancies occupy different layers.
- WMT boundary diagnosis is now localized to landmark generation. Any future engineering investigation belongs in the landmark extractor workstream and must be tested against independent positive/negative controls before proposing a frozen-engine change; do not relax `NO_SECOND_TROUGH_UNDERCUT` or tune morphology from this case.


## Required data by component

| Component | Reconstruction input |
|---|---|
| C | authoritative reference fact where documented |
| A | authoritative reference fact where documented; if annual evidence is not explicit, do not infer it |
| N | reference fact if documented; otherwise NOT_DOCUMENTED |
| S | historical OHLCV/volume; broader supply evidence only if available |
| L | historical comparison universe on same date; official historical RS separately if available |
| I | reference fact if documented; otherwise NOT_DOCUMENTED |
| M | historical market context through T only |
| Pattern/base | candidate historical OHLCV only |
| Pivot | engine-derived; 381.96 is oracle only |
| Breakout | historical price/volume |
| Original entry | breakout-day/source-faithful assessment |
| USSY execution | historical T+1 Open |
| Lifecycle | future historical bars revealed causally |

NOT_DOCUMENTED and NOT_EVALUABLE are not FAIL.

## Replay stages

1. Freeze authoritative source oracle. COMPLETE for LRCX v1.
2. Acquire/freeze candidate historical OHLCV with sufficient pre-base warm-up.
3. Run frozen O'Neil Pattern Engine on candidate data truncated as-of T.
4. Compare observed family, landmarks, pivot and ambiguity state against oracle.
5. Reconstruct breakout-day price/volume and original O'Neil entry opportunity.
6. Only after morphology/pivot replay, freeze comparison-universe identity/OHLCV for L and reconstruct M.
7. Assemble CAN SLIM v2 reconstruction evidence preserving NOT_DOCUMENTED.
8. Cross explicit boundary into USSY adaptation and reveal T+1 Open.
9. Evaluate USSY execution without retroactive fills.
10. Reveal later bars causally and replay lifecycle.
11. Publish expected-vs-observed discrepancies with lineage.

## Output contract

Preserve: case_id; symbol; decision/breakout date; authoritative source; source retrieval date; oracle facts/version; OHLCV provider/price basis/corporate-action policy/range/checksum; comparison-universe identity/checksum; M input identity; frozen Pattern Engine SHA/version; expected/observed pattern and pivot; breakout price/volume; original_oneil_entry; USSY T+1 execution; adaptation gap; lifecycle result; discrepancy classification; producer commit/run identity.

## Coverage matrix

| Area | LRCX 2020 | Next |
|---|---|---|
| Source oracle | VERIFIED/FROZEN v1 | preserve provenance |
| C quarterly reference | VERIFIED | reference only |
| A annual reference | NOT YET DOCUMENTED | do not infer |
| Cup with handle | VERIFIED oracle; cup/pivot reconstructed; final handle gate mismatch | frozen finding documented |
| Pivot | VERIFIED 381.96; observed 381.95999 on oracle structure | MATCH |
| Breakout | VERIFIED 2020-11-04; daily high crossed pivot | reconstruction complete |
| S / breakout volume | reconstructed; frozen v2 volume confirmation not met | BREAKOUT_VOLUME_UNCONFIRMED |
| L | NOT_EVALUABLE — PIT historical comparison universe unavailable | do not fabricate/back-project 2026 membership |
| I | not frozen | source fact or NOT_DOCUMENTED |
| N | not frozen | source fact or NOT_DOCUMENTED |
| M | FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS | reconstruction complete |
| Original entry | daily crossing reconstructed; intraday timing unavailable; volume discrepancy preserved | source-fidelity adjudication needed |
| T+1 adaptation | 2020-11-05 open 390.00; inside 5% buy zone | observation complete; eligibility boundary preserved |
| Lifecycle | not reconstructed | causal future-bar replay |
| DOUBLE_BOTTOM | IPHI 2019 structural neighborhood/pivot reproduced; frozen engine AMBIGUOUS on NO_SECOND_TROUGH_UNDERCUT; failed-trade lifecycle causally corroborated | COVERED / FIDELITY GAP CASE |
| FLAT_BASE | AAPL 2019 exact oracle pivot recovered; frozen engine fails geometry gates (TOO_SHORT/WIDE_LOOSE) while breakout volume and T+1 are corroborated | COVERED / FIDELITY GAP CASE |
| CUP_WITHOUT_HANDLE | AMD 2019 source-faithful candidate RECOGNIZED; pivot 35.549999 vs oracle 35.55; breakout volume ratio 1.6855 | COVERED / POSITIVE FIDELITY CASE |

## Recovery boundary

Freeze reusable stages with lineage:
source oracle -> candidate OHLCV -> morphology raw result -> comparison-universe manifest -> L/M raw reconstruction -> execution/lifecycle -> report.

Semantic changes to source, price basis, universe, decision date, methodology contract or frozen engine identity invalidate affected downstream checkpoints.

## Progress accounting

CAN SLIM v2 engineering implementation remains 100% complete.

Historical reconstruction first-pass core-pattern coverage is complete: all four frozen families now have a source-backed replay, with AMD as the positive morphology control and LRCX/IPHI/AAPL carrying localized fidelity questions. No frozen-engine change is authorized. Targeted multi-example replication is the next validation tranche. IPHI Golden Case 003 morphology/pivot, breakout, M, T+1 and original O'Neil loss-cut lifecycle are complete; the frozen engine preserves a DOUBLE_BOTTOM fidelity gap at NO_SECOND_TROUGH_UNDERCUT. AMD Golden Case 002 morphology/pivot, breakout-volume, historical M and T+1 reconstruction are now complete as a positive CUP_WITHOUT_HANDLE fidelity case; C/A and L evidence boundaries remain explicit. LRCX source oracle, candidate OHLCV replay, price-basis audit, morphology/pivot diagnosis, breakout-day daily-bar observation, T+1 observation and historical M replay are complete. Historical L is explicitly NOT_EVALUABLE because a defensible PIT comparison universe is unavailable. Consolidated CAN SLIM v2 eligibility reconstruction is complete for LRCX: NOT_ELIGIBLE under the frozen v2 contract. Lifecycle reconstruction remains separate.


## Golden Case 008 — EW 2019 — CUP_WITH_HANDLE

Status: **COMPLETE / FROZEN — VALIDATION EVIDENCE / NO ENGINE CHANGE AUTHORIZED**

Source oracle: IBD Top Stocks 2019 describes Edwards Lifesciences (EW) as a solid cup with handle, 16.3% deep, with proper buy point 195.10. Source chronology distinguishes thin-volume pivot crossing around July 22–23 from the July 24 breakaway gap / strong-volume confirmation.

Price-basis adaptation: Yahoo historical 2019 bars reflect the later 3-for-1 split basis. For source-faithful reconstruction, OHLC/adj_close are restored x3 and volume /3 before detector replay. Oracle facts remain reference-only and are not detector inputs.

Frozen engine replay (run 35433862533, engine c433cc1e35a5aa32a46f732cd8c5545935e36e40):
- source-target diagnostic: null; no CUP_WITH_HANDLE candidate matching the 195.10 source structure was emitted.
- primary/fused landmarks do contain the source-near cup body: SWING_HIGH 2019-03-18 at 197.85999 and SWING_LOW 2019-05-29 at 165.689999.
- atomic segment: start 2019-03-18, trough 2019-05-29, recovery null, depth 16.25897%, closely matching the source 16.3% depth.
- therefore the evidence localizes the discrepancy downstream of cup-body landmark/depth discovery: the frozen engine does not assemble/recognize the documented CWH structure by the July 24 as-of date.

Classification: **MORPHOLOGY_FIDELITY_GAP / CWH_ASSEMBLY_OR_HANDLE_RECOGNITION_MISS**. This is distinct from LRCX's explicit BELOW_CUP_MIDPOINT rejection: EW reaches a source-faithful cup-body geometry but produces no source-target CWH diagnostic. No detector tuning is authorized from this case alone.

Breakaway confirmation observation on 2019-07-24 (daily-bar reconstruction): O 218.16, H 219.71, L 210.73, C 214.88, volume 3,633,500 on contemporaneous basis. Prior-50-session average volume 1,307,968; ratio 2.77797x (+177.80%), comfortably above the frozen >=1.40 confirmation threshold. Close was +10.14% above the 195.10 pivot and already outside the original 5% buy zone. Daily OHLCV cannot reconstruct exact intraday entry timing.

USSY T+1 observation: 2019-07-25 open 212.55, +8.94% vs pivot and -1.08% vs July 24 close; outside the original 5% buy zone => **MISSED_EXTENDED / T1_OPEN_ABOVE_5PCT_BUY_ZONE** if July 24 strong-volume confirmation is used as finalized T.

Historical M: FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS. Historical L remains NOT_EVALUABLE under the frozen cross-sectional-universe limitation.

CWH adjudication after LRCX + EW: two authoritative CWH examples now show source-fidelity discrepancies, but not the same terminal gate. LRCX is an explicit handle midpoint-gate rejection; EW preserves the source-like cup body yet fails to assemble/recognize the source-target CWH. This supports continued targeted CWH replication and component-level diagnostics, not a family-wide rule change.


## Targeted replication checkpoint — BRP 2020 CWH suitability

Status: **SOURCE-ORACLE SUITABILITY REVIEWED / NOT PROMOTED TO COMPLETED-BREAKOUT GOLDEN CASE**.

Authoritative IBD Top Stocks 2020 material explicitly identifies BRP Group (BRP) as forming a cup-with-handle and gives a new buy point of 18.88. The source language is prospective: the stock "is forming a handle" / "is forming a cup-with-handle base". It does not, in the located passage, freeze a completed breakout date through 18.88 with breakout-day price/volume evidence.

Decision: retain BRP as **PRE-BREAKOUT / SETUP-STATE CWH EVIDENCE**, not as a completed-breakout replication equivalent to LRCX or EW. Do not infer a breakout date from later bars merely to make the case fit the validation template. This preserves source fidelity and the oracle-input prohibition.

Usefulness: BRP can later test whether the frozen engine recognizes a source-labelled in-progress CWH as-of the publication/setup state, but it cannot by itself answer the current completed-breakout CWH discrepancy question. The next CWH replication candidate should therefore be another authoritative example with an explicit completed breakout chronology, pivot, and sufficient historical date resolution.


## Golden Case 009 — NVO 2024 — CWH REPLICATION VERIFIED

Status: **FROZEN VALIDATION EVIDENCE / NO ENGINE CHANGE AUTHORIZED**.

Replay identity:
- successful run: 35438338999
- producer commit: 0481bcb8754571918e299d01296ca2344380dc8b
- frozen engine: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- source oracle: CUP_WITH_HANDLE, pivot 137.22, breakout 2024-06-04
- provider price basis retained unchanged; breakout bar price neighborhood corroborates the 137.22 oracle scale.

Source-fidelity morphology finding:
- The frozen engine does emit an open-right-edge CUP_WITH_HANDLE candidate relevant to the source period, but it is **AMBIGUOUS**, not RECOGNIZED.
- Engine structure: LEFT_RIM 2023-11-24; CUP_LOW 2023-12-11; RIGHT_RIM 2024-03-07; HANDLE_LOW 2024-05-03.
- Engine pivot: 138.27999878 versus source oracle 137.22 (~0.77% higher).
- Cup depth: 10.369949%.
- Terminal detector fault: **DEEP_HANDLE_EXCEPTIONAL**.
- Classification: **MORPHOLOGY_FIDELITY_GAP / DEEP_HANDLE_EXCEPTIONAL**.

Breakout-day reconstruction (2024-06-04):
- O 136.44 / H 140.00 / L 135.78 / C 139.92; volume 5,071,200.
- Source pivot 137.22 was crossed and the close finished +1.9676% above pivot, inside the original 5% buy zone.
- Prior-50-session average volume: 3,712,446; breakout volume +36.60% (1.366x), below the USSY >=1.40 confirmation threshold.
- Daily-bar limitation remains INTRADAY_ENTRY_TIMING_NOT_RECONSTRUCTED.

USSY T+1 observation (2024-06-05):
- open 141.36; +3.0171% versus source pivot and +1.0292% versus breakout close.
- T+1 open remained inside the original 5% buy zone: **T1_OPEN_IN_BUY_ZONE / NOT_EXTENDED**.

Historical M reconstruction:
- FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS.
- Historical L remains NOT_EVALUABLE under the frozen cross-sectional-universe boundary.

CWH adjudication after LRCX + EW + NVO:
- Three independent authoritative CWH examples now produce three distinct terminal fidelity mechanisms under the frozen engine: LRCX -> BELOW_CUP_MIDPOINT; EW -> CWH assembly/handle-recognition miss after source-like cup body; NVO -> DEEP_HANDLE_EXCEPTIONAL with a near-source pivot.
- This strengthens evidence that CWH source-fidelity is not yet robust, but does **not** identify one universal gate whose removal is justified.
- No detector tuning or production-rule change is authorized from these cases alone. Any engine revision requires a separate component-level study with authoritative positive and negative controls.


## Golden Case 010 — AVTR 2021 — CWOH REPLICATION

Status: **FROZEN VALIDATION EVIDENCE / NO ENGINE CHANGE AUTHORIZED**.

Replay identity:
- successful first run: 35439158198
- producer commit: 72dcf424c366a08c3b4c91995aaecfca6bcc7515
- frozen engine: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- source oracle: CUP_WITHOUT_HANDLE, pivot 33.99, breakout 2021-06-16
- provider historical basis retained unchanged; breakout bar neighborhood independently corroborates the oracle price scale.

Source-fidelity morphology finding:
- The frozen engine emits multiple CUP_WITHOUT_HANDLE_RECOGNIZED structures, but none of the emitted source pivots is near the source oracle 33.99 at the 2021-06-16 as-of date.
- Representative latest recognized structure uses LEFT_RIM 2020-10-21 / CUP_LOW 2020-10-30 with pivot 25.70000076 and no detector faults; other recognized CWOH pivots include 28.97999954, 19.50, and 18.09000015.
- Therefore generic pattern-family recognition is present, but the source-labelled AVTR base is not reconstructed.
- Classification: **MORPHOLOGY_FIDELITY_GAP / SOURCE_TARGET_BASE_NOT_RECONSTRUCTED**.

Breakout-day reconstruction (2021-06-16):
- O 33.36 / H 34.50 / L 33.25 / C 34.05; volume 5,454,200.
- Oracle pivot 33.99 was crossed; close finished +0.1765% above pivot and inside the 5% buy zone.
- Prior-50-session average volume 3,960,106; breakout volume +37.73% (1.3773x), narrowly below the USSY >=1.40 confirmation threshold.
- Daily-bar limitation remains INTRADAY_ENTRY_TIMING_NOT_RECONSTRUCTED.

USSY T+1 observation (2021-06-17):
- open 34.05; +0.1765% versus pivot and unchanged versus breakout close.
- T+1 open remained inside the original 5% buy zone: **T1_OPEN_IN_BUY_ZONE / NOT_EXTENDED**.

Historical M reconstruction:
- FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS.
- Historical L remains NOT_EVALUABLE under the frozen cross-sectional-universe boundary.

CWOH adjudication checkpoint:
- AMD remains the clean source-fidelity positive control.
- AVTR shows that recognizing some CWOH structures on the same security is not sufficient: source-target base selection/assembly can still miss the authoritative base.
- No detector tuning is authorized from this single discrepancy; continue the planned 10-case CWOH tranche.


## Golden Case 011 — SE 2019 — CWOH REPLICATION

Status: **FROZEN VALIDATION EVIDENCE / NO ENGINE CHANGE AUTHORIZED**.

Source oracle: IBD Top Stocks 2019 identifies Sea Limited (SE) as a cup-without-handle base with 38.10 buy point and states the stock moved into the buy range on 2019-11-20. This is treated as an intraday pivot-cross event; the daily replay must not silently reinterpret it as a close-confirmed breakout.

Replay identity:
- successful run: 35439712313
- producer commit: 957ea5bc19dd231dd473a9c824d7df98a4349bea
- frozen engine: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- provider historical basis retained unchanged.

Source-fidelity morphology finding:
- The frozen engine recognizes an open-right-edge CUP_WITHOUT_HANDLE through the oracle date with LEFT_RIM 2019-08-19, CUP_LOW 2019-10-21, pivot 36.90000153, depth 28.428188%, and no detector faults.
- IBD oracle pivot is 38.10, so the family is recognized but pivot/base geometry does not exactly reproduce the source-labelled structure.
- Classification: **MORPHOLOGY_FIDELITY_GAP / CWOH_PIVOT_GEOMETRY_MISMATCH**.

Breakout-day reconstruction (2019-11-20):
- O 37.02 / H 38.98 / L 36.69 / C 37.27; volume 4,860,100.
- High crossed the 38.10 oracle pivot, but close finished 2.1785% below pivot; therefore this is consistent with an intraday pivot cross that faded by the close, not a close-confirmed breakout.
- Prior-50-session average volume 4,004,580; volume +21.36% (1.2136x), below the USSY >=1.40 confirmation threshold.
- Daily-bar limitation: INTRADAY_ENTRY_TIMING_NOT_RECONSTRUCTED.

USSY T+1 observation (2019-11-21):
- open 37.28; 2.1522% below oracle pivot and therefore not in the original buy zone at the open.
- State: **T1_OPEN_BELOW_PIVOT / NOT_EXTENDED**.

Historical M reconstruction: FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS. Historical L remains NOT_EVALUABLE under the frozen cross-sectional-universe boundary.

CWOH checkpoint after AMD + AVTR + SE:
- AMD: clean source-fidelity positive control.
- AVTR: source-target base not reconstructed despite generic CWOH recognition.
- SE: source family recognized, but engine pivot geometry differs from the authoritative 38.10 source pivot.
- Continue the planned 10-case CWOH tranche; no detector tuning is authorized from these cases alone.


## Golden Case 012 — AMZN 2023 — CWOH REPLICATION

Status: **FROZEN VALIDATION EVIDENCE / NO ENGINE CHANGE AUTHORIZED**.

Authoritative IBD oracle: Amazon formed a cup-without-handle after a September 2023 pullback, with buy point 145.86. IBD describes the breakout in the week of Nov. 17; daily OHLCV establishes the first actual 145.86 pivot cross on 2023-11-20 (Nov. 17 high was 145.23). Daily replay therefore uses 2023-11-20 as the causal breakout session and 2023-11-21 as T+1.

Replay identity:
- valid successful run: 35439948453
- producer commit: 8d26eb6ab928e32924badcab50420e0c9e5a9ffd
- frozen engine: c433cc1e35a5aa32a46f732cd8c5545935e36e40 / oneil-pattern-output-v2 / 33-core-p8-frozen-v1
- provider basis unchanged.

Morphology finding:
- frozen engine emits CUP_WITHOUT_HANDLE_RECOGNIZED candidates, but the source-labelled September-November base/pivot 145.86 is not reconstructed.
- Representative recognized structure at the oracle as-of uses LEFT_RIM 2023-04-27 / CUP_LOW 2023-05-02 / pivot 110.86000061 / depth 8.758794%, no faults.
- Classification: **MORPHOLOGY_FIDELITY_GAP / SOURCE_TARGET_BASE_NOT_RECONSTRUCTED**.

Breakout day 2023-11-20:
- O 145.13 / H 146.63 / L 144.73 / C 146.13; volume 41,951,200.
- high and close above 145.86; close +0.1851% versus pivot and inside 5% buy zone.
- prior-50 average volume 55,536,578; breakout volume -24.46% versus average, below USSY >=1.40 confirmation threshold.

T+1 2023-11-21:
- open 143.91; -1.3369% versus pivot and -1.5192% versus breakout close.
- **T1_OPEN_BELOW_PIVOT / NOT_EXTENDED**.

Historical M: FOLLOW_THROUGH_CONFIRMED / ALLOW_NEW_BUYS. Historical L remains NOT_EVALUABLE.

CWOH progress: AMD, AVTR, SE, AMZN = **4 / 10 valid cases**.


## CWH completion tranche — Golden Cases 013–019

Status: **CWH 10/10 COMPLETE / FROZEN VALIDATION EVIDENCE / NO ENGINE CHANGE AUTHORIZED**.

Batch replay: run 35441720017 (OLED, TOL, URBN, SHOP, RBLX, DUOL; all jobs SUCCESS). TSLA required a corporate-action basis correction for Yahoo's later 2022 3-for-1 split; authoritative corrected replay is run 35441985710. Earlier TSLA batch evidence is superseded and must not be used.

### 013 OLED 2019
IBD oracle: second-stage CUP_WITH_HANDLE, pivot 177.05, breakout 2019-06-18. Daily replay: O 176.08 / H 186.31 / L 175.94 / C 184.70; volume 1,028,500 vs prior50 743,744 (~1.383x). T+1 2019-06-19 open 185.80, +4.9421% vs pivot, still inside 5% zone. Frozen engine does not reproduce the source-target 177.05 CWH; emitted CWH candidates are faulted (including DEEP_HANDLE_EXCEPTIONAL / BELOW_CUP_MIDPOINT). Classification: **MORPHOLOGY_FIDELITY_GAP / SOURCE_TARGET_CWH_NOT_RECONSTRUCTED**.

### 014 TSLA 2020
IBD oracle: off-kilter CUP_WITH_HANDLE, pivot 466.00, breakout 2020-11-18. Yahoo current history is adjusted for the later 2022 3-for-1 split; replay restores contemporaneous Nov-2020 basis by multiplying OHLC by 3 and dividing volume by 3. Corrected breakout: O 448.35 / H 496.00 / L 443.50 / C 486.64; volume 78,044,000 vs prior50 48,526,294 (~1.608x); close +4.4292% vs pivot and inside 5% zone. T+1 open 492.00, +5.5794%, above the 5% zone: **MISSED_EXTENDED / T1_OPEN_ABOVE_5PCT_BUY_ZONE**. Engine's representative CWH is AMBIGUOUS with pivot 358.998 and DEEP_HANDLE_EXCEPTIONAL, not the source-target structure. Classification: **MORPHOLOGY_FIDELITY_GAP / SOURCE_TARGET_CWH_NOT_RECONSTRUCTED**.

### 015 TOL 2024
IBD retrospective oracle: CUP_WITH_HANDLE pivot 128.75; breakout occurred one week before the 2024-05-22 selloff, reconstructed as 2024-05-15. Daily replay: O 131.56 / H 135.37 / L 131.05 / C 134.92; volume 2,067,000 vs prior50 1,213,256 (~1.704x); close +4.7922% and inside 5% zone. T+1 open 133.91, +4.0078%, inside zone. Frozen engine does not reconstruct the 128.75 source-target CWH; representative candidates are faulted BELOW_CUP_MIDPOINT. Classification: **MORPHOLOGY_FIDELITY_GAP / SOURCE_TARGET_CWH_NOT_RECONSTRUCTED**.

### 016 URBN 2025
IBD oracle: CUP_WITH_HANDLE pivot 74.45, breakout 2025-07-21. Daily replay: O 72.81 / H 75.98 / L 72.69 / C 74.62; volume 2,126,000 vs prior50 2,205,444 (~0.964x); close +0.2283%. T+1 open 75.79, +1.7999%, inside 5% zone. Frozen engine does not reproduce source-target 74.45 CWH; representative candidates carry DEEP_HANDLE_EXCEPTIONAL. Classification: **MORPHOLOGY_FIDELITY_GAP / SOURCE_TARGET_CWH_NOT_RECONSTRUCTED**.

### 017 SHOP 2025
IBD oracle: early-stage deep CUP_WITH_HANDLE pivot 112.38, breakout 2025-06-11. Daily replay: O 111.625 / H 117.36 / L 111.29 / C 114.13; volume 14,078,100 vs prior50 14,202,128 (~0.991x); close +1.5572%. T+1 open 113.25, +0.7742%, inside 5% zone. Frozen engine does not reproduce the source-target CWH; representative candidate pivot 111.00 is faulted BELOW_CUP_MIDPOINT. Classification: **MORPHOLOGY_FIDELITY_GAP / SOURCE_TARGET_CWH_NOT_RECONSTRUCTED**.

### 018 RBLX 2025
IBD/MarketSurge oracle: CUP_WITH_HANDLE pivot 74.24, breakout 2025-05-13. Daily replay: O 73.93 / H 77.24 / L 73.38 / C 77.02; volume 12,375,800 vs prior50 8,210,696 (~1.507x); close +3.7446%. T+1 open 77.40, +4.2565%, inside 5% zone. Frozen engine emits nearby CWH candidates but the representative 75.74 pivot is AMBIGUOUS/DEEP_HANDLE_EXCEPTIONAL rather than an exact source-target reconstruction. Classification: **MORPHOLOGY_FIDELITY_GAP / CWH_PIVOT_AND_HANDLE_SEMANTICS**.

### 019 DUOL 2024
IBD/MarketSurge oracle: CUP_WITH_HANDLE pivot 241.86; source documents the setup and later reporting confirms a brief move past the buy point. Daily replay uses 2024-05-06 as the completed daily crossing: O 242.245 / H 251.30 / L 241.156 / C 248.20; volume 863,700 vs prior50 839,762 (~1.029x); close +2.6213%. T+1 2024-05-07 open 246.19, +1.7903%, inside 5% zone. Frozen engine does not exactly reconstruct the 241.86 source-target CWH; representative candidates include pivot 231.89 with FRAGMENTED_BOTTOM + BELOW_CUP_MIDPOINT. Classification: **MORPHOLOGY_FIDELITY_GAP / SOURCE_TARGET_CWH_NOT_RECONSTRUCTED**.

### CWH family adjudication after 10 valid cases
The CWH tranche is now closed at **10/10**: LRCX, EW, NVO, OLED, TSLA, TOL, URBN, SHOP, RBLX, DUOL. The accumulated evidence shows repeated source-fidelity gaps, but they are not explained by one universal terminal gate: observed mechanisms include BELOW_CUP_MIDPOINT, assembly/handle-recognition misses, DEEP_HANDLE_EXCEPTIONAL, source-target base/pivot mismatch, and nearby-but-nonidentical handle/pivot semantics. This is strong evidence that CWH source fidelity of the frozen engine is not robust across authoritative historical examples, but **does not authorize detector tuning**. Any engine revision requires a separate morphology-engine workstream with positive and negative controls.
