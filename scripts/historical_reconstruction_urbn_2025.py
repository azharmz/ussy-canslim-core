#!/usr/bin/env python3
from __future__ import annotations
from datetime import date
import hashlib, json, subprocess, sys
from pathlib import Path


ENGINE_REPO = "https://github.com/azharmz/ussy-oneil-patterns.git"
ENGINE_SHA = "c433cc1e35a5aa32a46f732cd8c5545935e36e40"
SYMBOL = "URBN"
ASOF = date(2025,7,21)
EXECUTION_END = date(2025,7,22)
START = date(2024,7,1)
ORACLE = {"pattern":"CUP_WITH_HANDLE","pivot":74.45,"breakout_date":"2025-07-21"}
ROOT=Path("artifacts/historical-reconstruction/urbn-2025")
ROOT.mkdir(parents=True,exist_ok=True)

def main():
    eng=Path(".tmp/ussy-oneil-patterns")
    if not eng.exists():
        eng.parent.mkdir(exist_ok=True)
        subprocess.run(["git","clone","--quiet",ENGINE_REPO,str(eng)],check=True)
    subprocess.run(["git","-C",str(eng),"checkout","--quiet",ENGINE_SHA],check=True)
    subprocess.run([sys.executable,"-m","pip","install","-q","-e",f"{eng}[validation]"],check=True)

    import pandas as pd
    sys.path.insert(0,str(Path("src").resolve()))
    sys.path.insert(0,str(eng/"src"))
    from oneil_patterns.validation.external_ohlcv import fetch_yfinance
    from oneil_patterns.production.engine import analyze_security
    from oneil_patterns.landmarks.excursion import extract_excursion_landmarks
    from oneil_patterns.landmarks.confirmed_window import extract_confirmed_window_landmarks
    from oneil_patterns.landmarks.fusion import fuse_landmark_sources
    from oneil_patterns.segmentation.segmenter import segment_base_candidates
    from oneil_patterns.validation.structural_assembly import assemble_multiturn_segments, assemble_handle_geometries
    from oneil_patterns.morphology.cup_body import build_cup_body_geometry
    from oneil_patterns.morphology.cup_body_detector import assess_cup_body
    from oneil_patterns.morphology.cup_family import assess_handle
    from oneil_patterns.validation.pivot_adapter import cup_with_handle_pivot
    from oneil_patterns.validation.open_right_edge_handle import enumerate_open_right_edge_handles
    from canslim_research.market_state_v1 import IndexBar
    from canslim_research.historical_market_adapter import replay_historical_market, decision_on

    frame=fetch_yfinance(SYMBOL,START,EXECUTION_END)
    market_raw={}
    market_ids={"NASDAQ_COMPOSITE":"^IXIC","SP500":"^GSPC","DJIA":"^DJI"}
    for index_id,ticker in market_ids.items():
        market_raw[index_id]=fetch_yfinance(ticker,date(2025,1,1),ASOF)
    raw_csv=ROOT/"ohlcv-yahoo-split-adjusted.csv"
    frame.to_csv(raw_csv,index=False)
    raw_sha=hashlib.sha256(raw_csv.read_bytes()).hexdigest()

    # URBN has no price-scale transformation in this replay; provider basis is retained unchanged.
    contemporaneous=frame.copy()
    detector_frame=contemporaneous[pd.to_datetime(contemporaneous["date"]).dt.date <= ASOF].copy()

    csv=ROOT/"ohlcv-2025-provider-basis.csv"
    contemporaneous.to_csv(csv,index=False)
    sha=hashlib.sha256(csv.read_bytes()).hexdigest()
    observed=analyze_security("URBN",SYMBOL,detector_frame,ASOF)

    primary=extract_excursion_landmarks(detector_frame)
    auxiliary=extract_confirmed_window_landmarks(detector_frame)
    fused=[x for x in fuse_landmark_sources(detector_frame,primary,auxiliary) if x.confirmed_date <= ASOF]
    atomic=segment_base_candidates(detector_frame,fused,asof_date=ASOF)
    multi=assemble_multiturn_segments(detector_frame,fused,asof_date=ASOF)
    # Diagnostic only: expose the frozen candidate vocabulary near the 13-week
    # oracle horizon. No thresholds are changed and no oracle fact is fed into
    # landmark/segmentation generation.
    cutoff=date(2025,1,1)
    target=[]  # AMD oracle landmarks are not injected into detector selection; inspect emitted candidates first.
    target_diag=None
    if target:
        seg=target[0]
        cup=build_cup_body_geometry(detector_frame,seg.start,seg.trough,seg.recovery)
        body=assess_cup_body(cup)
        handles=assemble_handle_geometries(detector_frame,cup,fused,asof_date=ASOF)
        target_diag={
          "cup_geometry":{"left_rim":cup.left_rim.price_date.isoformat(),"trough":cup.trough.price_date.isoformat(),"right_rim":cup.right_rim.price_date.isoformat(),"duration_sessions":cup.duration_sessions,"depth_pct":cup.depth_pct,"right_rim_to_left_rim_ratio":cup.right_rim_to_left_rim_ratio,"sessions_within_5pct_of_trough":cup.sessions_within_5pct_of_trough,"sessions_within_10pct_of_trough":cup.sessions_within_10pct_of_trough,"max_bottom_run_10pct":cup.max_bottom_run_10pct},
          "cup_assessment":{"state":body.state.value,"faults":[x.value for x in body.faults],"theory_gates_pass":body.theory_gates_pass,"research_bands_pass":body.research_bands_pass},
          "handles":[],
          "open_right_edge_handles":[]
        }
        for o in enumerate_open_right_edge_handles(detector_frame,cup,fused,asof_date=ASOF):
            target_diag["open_right_edge_handles"].append({"low":o.handle_low.price_date.isoformat(),"asof_date":o.asof_date.isoformat(),"duration_sessions":o.duration_sessions,"depth_pct":o.depth_pct,"low_in_upper_half":o.low_in_upper_half,"state":o.state.value,"faults":[x.value for x in o.faults],"implied_pivot":cup.right_rim.price,"implied_pivot_date":cup.right_rim.price_date.isoformat()})
        for h in handles:
            ha=assess_handle(h); pv=cup_with_handle_pivot(cup,h)
            target_diag["handles"].append({"low":h.handle_low.price_date.isoformat(),"recovery":h.handle_recovery.price_date.isoformat(),"duration_sessions":h.duration_sessions,"depth_pct":h.depth_pct,"low_in_upper_half":h.low_in_upper_half,"state":ha.state.value,"faults":[x.value for x in ha.faults],"pivot":pv.pivot_level,"pivot_date":pv.pivot_source_date.isoformat()})
    index_series={}
    market_lineage={}
    for index_id,mf in market_raw.items():
        mf=mf[pd.to_datetime(mf["date"]).dt.date <= ASOF].copy()
        index_series[index_id]=tuple(IndexBar(date=pd.Timestamp(r["date"]).date().isoformat(),low=float(r["low"]),close=float(r["close"]),volume=float(r["volume"]) if pd.notna(r["volume"]) else None) for _,r in mf.iterrows())
        raw=mf.to_csv(index=False).encode()
        market_lineage[index_id]={"source":"Yahoo via yfinance","symbol":market_ids[index_id],"start":pd.Timestamp(mf.iloc[0]["date"]).date().isoformat(),"end":pd.Timestamp(mf.iloc[-1]["date"]).date().isoformat(),"rows":len(mf),"sha256":hashlib.sha256(raw).hexdigest()}
    m_decisions=replay_historical_market(index_series=index_series)
    m_on_t=decision_on(m_decisions,ASOF.isoformat())

    bar_t=contemporaneous[pd.to_datetime(contemporaneous["date"]).dt.date == ASOF].iloc[0]
    bar_t1=contemporaneous[pd.to_datetime(contemporaneous["date"]).dt.date == EXECUTION_END].iloc[0]
    pivot=ORACLE["pivot"]
    avg50=float(detector_frame.iloc[:-1].tail(50)["volume"].mean())
    breakout={
      "classification":"ORIGINAL",
      "daily_bar_limitation":"INTRADAY_ENTRY_TIMING_NOT_RECONSTRUCTED",
      "date":ASOF.isoformat(),"pivot":pivot,
      "open":float(bar_t["open"]),"high":float(bar_t["high"]),"low":float(bar_t["low"]),"close":float(bar_t["close"]),"volume":float(bar_t["volume"]),
      "high_above_pivot":bool(float(bar_t["high"])>pivot),"close_above_pivot":bool(float(bar_t["close"])>pivot),
      "close_vs_pivot_pct":float(bar_t["close"])/pivot-1,
      "prior_50_session_avg_volume":avg50,
      "volume_vs_prior_50_avg_pct":float(bar_t["volume"])/avg50-1,
      "buy_zone_upper_5pct":pivot*1.05,
      "close_in_5pct_buy_zone":bool(pivot <= float(bar_t["close"]) <= pivot*1.05)
    }
    t1={
      "classification":"OPERATIONALIZATION","date":EXECUTION_END.isoformat(),"open":float(bar_t1["open"]),
      "open_vs_pivot_pct":float(bar_t1["open"])/pivot-1,
      "open_vs_breakout_close_pct":float(bar_t1["open"])/float(bar_t["close"])-1,
      "in_original_5pct_buy_zone_at_open":bool(pivot <= float(bar_t1["open"]) <= pivot*1.05)
    }
    diag={
      "target_oracle_structure_diagnostic":target_diag,
      "breakout_day_assessment":breakout,
      "ussy_t1_execution_observation":t1,
      "historical_M_reconstruction":{"classification":"DATA_ADAPTATION","decision":{"asof_date":m_on_t.asof_date,"market_state":m_on_t.market_state,"M_entry_state":m_on_t.M_entry_state,"classifier_reason":m_on_t.classifier_reason,"entry_reason":m_on_t.entry_reason,"provenance":m_on_t.provenance,"version":m_on_t.version},"input_lineage":market_lineage,"limitation":"index-only frozen historical adapter; leadership/weakening booleans and correction-reset evidence are not fabricated"},
      "primary_landmarks":[{"type":x.type.value,"price_date":x.price_date.isoformat(),"confirmed_date":x.confirmed_date.isoformat(),"price":x.price} for x in primary if x.price_date>=cutoff and x.confirmed_date<=ASOF],
      "auxiliary_landmarks":[{"type":x.type.value,"price_date":x.price_date.isoformat(),"confirmed_date":x.confirmed_date.isoformat(),"price":x.price} for x in auxiliary if x.price_date>=cutoff and x.confirmed_date<=ASOF],
      "fused_landmarks":[{"type":x.type.value,"price_date":x.price_date.isoformat(),"confirmed_date":x.confirmed_date.isoformat(),"price":x.price} for x in fused if x.price_date>=cutoff],
      "segments":[{"start":x.start_date.isoformat(),"trough":x.trough.price_date.isoformat(),"recovery":x.recovery.price_date.isoformat() if x.recovery else None,"depth_pct":x.depth_pct,"assembly":x.evidence.get("assembly_mode","ATOMIC")} for x in (atomic+multi) if x.start_date>=cutoff],
    }
    (ROOT/"candidate-diagnostics.json").write_text(json.dumps(diag,indent=2,default=str)+"\n")
    payload={
      "fixture_class":"HISTORICAL_RECONSTRUCTION_FIXTURE",
      "production_use":"NEVER_PRODUCTION",
      "symbol":SYMBOL,"asof_date":ASOF.isoformat(),
      "source":{"provider":"Yahoo via yfinance","auto_adjust":False,"start":START.isoformat(),"end":EXECUTION_END.isoformat(),"detector_asof":ASOF.isoformat(),"rows":len(frame),"yahoo_split_adjusted_sha256":raw_sha},
      "price_basis":{"classification":"DATA_ADAPTATION","corporate_action":"NONE_APPLIED_FOR_GOLDEN_REPLAY","price_transform":"identity","volume_transform":"identity","provider_basis_sha256":sha},
      "engine":{"repo":"azharmz/ussy-oneil-patterns","sha":ENGINE_SHA},
      "oracle":ORACLE,
      "candidate_diagnostics":diag,
      "observed":[r.to_dict() if hasattr(r,"to_dict") else r.__dict__ for r in observed],
    }
    (ROOT/"replay.json").write_text(json.dumps(payload,indent=2,default=str)+"\n")
    print(json.dumps(payload,indent=2,default=str))

if __name__=="__main__":
    main()
