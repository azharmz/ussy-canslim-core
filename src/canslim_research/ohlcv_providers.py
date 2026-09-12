"""Concrete OHLCV providers used by the Stage #33 DEVELOPMENT probe.

Provider contract:
- a genuinely absent object / ticker window => UNAVAILABLE;
- auth, transport, parse, or QC problems => FAILED/QC_FAILED;
- only UNAVAILABLE permits the router to try the next source.
"""

from __future__ import annotations

import io
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .ohlcv_router import ProviderResult, SourceStatus, validate_ohlcv_rows


class R2TickerNotInSnapshot(LookupError):
    """Ticker is genuinely absent from the requested R2 membership snapshot."""


class R2TickerAmbiguous(LookupError):
    """Ticker maps to more than one security_id and must not silently fall back."""


def _records_from_frame(frame) -> tuple[dict[str, Any], ...]:
    import pandas as pd

    if frame is None or frame.empty:
        return ()
    work = frame.copy()
    work["date"] = pd.to_datetime(work["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    work = work.dropna(subset=["date"]).sort_values("date")
    fields = ["date", "open", "high", "low", "close", "volume"]
    if "adj_close" in work.columns:
        fields.append("adj_close")
    records = []
    for raw in work[fields].to_dict(orient="records"):
        row = {
            "date": str(raw["date"]),
            "open": float(raw["open"]),
            "high": float(raw["high"]),
            "low": float(raw["low"]),
            "close": float(raw["close"]),
            "volume": float(raw["volume"]),
        }
        if "adj_close" in raw and raw["adj_close"] is not None:
            row["adj_close"] = float(raw["adj_close"])
        records.append(row)
    return tuple(records)


def _validate_result(source: str, rows, **metadata) -> ProviderResult:
    valid, reason = validate_ohlcv_rows(rows)
    if not valid:
        return ProviderResult(source, SourceStatus.QC_FAILED, rows=rows, reason=reason, metadata=metadata)
    return ProviderResult(source, SourceStatus.AVAILABLE, rows=rows, metadata=metadata)


def make_r2_client():
    import boto3
    from botocore.config import Config

    return boto3.client(
        "s3",
        endpoint_url=os.environ["R2_ENDPOINT"],
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
        config=Config(retries={"max_attempts": 5, "mode": "adaptive"}),
    )


def resolve_security_id_from_r2(ticker: str, snapshot_date: str = "current") -> str:
    """Resolve ticker to security_id using the same R2 membership contract as ussy-data."""
    client = make_r2_client()
    bucket = os.environ["R2_BUCKET_NAME"]
    if snapshot_date == "current":
        pointer = json.loads(client.get_object(Bucket=bucket, Key="universe/current.json")["Body"].read())
        snapshot_date = str(pointer["snapshot_date"])
    payload = json.loads(
        client.get_object(Bucket=bucket, Key=f"universe/membership/{snapshot_date}.json")["Body"].read()
    )
    matches = [
        str(row["security_id"])
        for row in payload.get("records", [])
        if str(row.get("ticker", "")).upper() == ticker.upper()
    ]
    if not matches:
        raise R2TickerNotInSnapshot(f"ticker {ticker} not present in R2 membership snapshot {snapshot_date}")
    if len(set(matches)) != 1:
        raise R2TickerAmbiguous(f"ticker {ticker} maps to multiple security_ids in snapshot {snapshot_date}: {sorted(set(matches))}")
    return matches[0]


def r2_provider(*, security_id: str, start: str, end: str) -> ProviderResult:
    import pandas as pd
    from botocore.exceptions import ClientError

    source = "r2"
    key = f"backtest/ohlcv/{security_id}.parquet"
    bucket = os.environ.get("R2_BUCKET_NAME")
    if not bucket:
        return ProviderResult(source, SourceStatus.FAILED, reason="R2_BUCKET_NAME is not configured")
    try:
        client = make_r2_client()
        try:
            payload = client.get_object(Bucket=bucket, Key=key)["Body"].read()
        except ClientError as exc:
            code = str(exc.response.get("Error", {}).get("Code", ""))
            if code in {"404", "NoSuchKey", "NotFound"}:
                return ProviderResult(source, SourceStatus.UNAVAILABLE, reason=f"object absent: {key}")
            raise
        frame = pd.read_parquet(io.BytesIO(payload), engine="pyarrow")
        required = {"date", "open", "high", "low", "close", "volume"}
        missing = required - set(frame.columns)
        if missing:
            return ProviderResult(source, SourceStatus.QC_FAILED, reason=f"parquet missing columns: {sorted(missing)}")
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
        mask = (frame["date"] >= pd.Timestamp(start)) & (frame["date"] <= pd.Timestamp(end))
        window = frame.loc[mask].copy()
        if window.empty:
            return ProviderResult(source, SourceStatus.UNAVAILABLE, reason=f"requested window {start}..{end} absent in {key}")
        rows = _records_from_frame(window)
        return _validate_result(source, rows, object_key=key, security_id=security_id)
    except Exception as exc:
        return ProviderResult(source, SourceStatus.FAILED, reason=f"{type(exc).__name__}: {exc}")


def r2_ticker_provider(*, ticker: str, start: str, end: str, snapshot_date: str = "current") -> ProviderResult:
    """Resolve an R2 security_id and fetch OHLCV, preserving strict fallback semantics.

    A ticker genuinely absent from the membership snapshot is explicit UNAVAILABLE,
    so source-first morphology validation may continue to Yahoo/Tiingo. Ambiguous
    mappings and operational resolver failures remain terminal FAILED states.
    This does not change the frozen universe; it only classifies R2 availability.
    """
    source = "r2"
    try:
        security_id = resolve_security_id_from_r2(ticker, snapshot_date)
    except R2TickerNotInSnapshot as exc:
        return ProviderResult(
            source,
            SourceStatus.UNAVAILABLE,
            reason=str(exc),
            metadata={"ticker": ticker, "membership_resolution": "ABSENT"},
        )
    except Exception as exc:
        return ProviderResult(
            source,
            SourceStatus.FAILED,
            reason=f"ticker resolution failed: {type(exc).__name__}: {exc}",
            metadata={"ticker": ticker, "membership_resolution": "FAILED"},
        )
    return r2_provider(security_id=security_id, start=start, end=end)


def yahoo_provider(*, ticker: str, start: str, end: str) -> ProviderResult:
    import pandas as pd
    import yfinance as yf

    source = "yahoo"
    try:
        # yfinance end is exclusive; add one calendar day to keep the CLI contract inclusive.
        inclusive_end = (pd.Timestamp(end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        frame = yf.download(
            ticker,
            start=start,
            end=inclusive_end,
            interval="1d",
            auto_adjust=False,
            actions=False,
            repair=False,
            prepost=False,
            progress=False,
            threads=False,
            timeout=30,
        )
        if frame.empty:
            return ProviderResult(source, SourceStatus.UNAVAILABLE, reason=f"Yahoo returned no rows for {ticker} {start}..{end}")
        if isinstance(frame.columns, pd.MultiIndex):
            if ticker in frame.columns.get_level_values(1):
                frame = frame.xs(ticker, axis=1, level=1)
            elif ticker in frame.columns.get_level_values(0):
                frame = frame[ticker]
            else:
                return ProviderResult(source, SourceStatus.FAILED, reason="Yahoo MultiIndex did not contain requested ticker")
        frame = frame.reset_index().rename(
            columns={"Date": "date", "Datetime": "date", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Adj Close": "adj_close", "Volume": "volume"}
        )
        rows = _records_from_frame(frame)
        if not rows:
            return ProviderResult(source, SourceStatus.UNAVAILABLE, reason=f"Yahoo returned no usable rows for {ticker} {start}..{end}")
        return _validate_result(source, rows, ticker=ticker)
    except Exception as exc:
        return ProviderResult(source, SourceStatus.FAILED, reason=f"{type(exc).__name__}: {exc}")


def tiingo_provider(*, ticker: str, start: str, end: str) -> ProviderResult:
    source = "tiingo"
    token = os.environ.get("TIINGO_API_KEY")
    if not token:
        return ProviderResult(source, SourceStatus.FAILED, reason="TIINGO_API_KEY is not configured")
    query = urllib.parse.urlencode({"startDate": start, "endDate": end, "token": token})
    request = urllib.request.Request(
        f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?{query}",
        headers={"User-Agent": "ussy-canslim-research/1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500].replace(token, "[REDACTED]")
        # 404 is an explicit absence; entitlement/quota/auth errors are failures.
        if exc.code == 404:
            return ProviderResult(source, SourceStatus.UNAVAILABLE, reason=f"Tiingo has no symbol/window: {ticker}")
        return ProviderResult(source, SourceStatus.FAILED, reason=f"Tiingo HTTP {exc.code}: {detail}")
    except Exception as exc:
        return ProviderResult(source, SourceStatus.FAILED, reason=f"{type(exc).__name__}: {exc}")

    if not isinstance(data, list):
        return ProviderResult(source, SourceStatus.FAILED, reason=f"unexpected Tiingo payload: {str(data)[:200]}")
    if not data:
        return ProviderResult(source, SourceStatus.UNAVAILABLE, reason=f"Tiingo returned no rows for {ticker} {start}..{end}")

    rows = []
    try:
        for item in data:
            row = {
                "date": str(item["date"])[:10],
                "open": float(item["open"]),
                "high": float(item["high"]),
                "low": float(item["low"]),
                "close": float(item["close"]),
                "volume": float(item["volume"]),
            }
            if item.get("adjClose") is not None:
                row["adj_close"] = float(item["adjClose"])
            rows.append(row)
    except (KeyError, TypeError, ValueError) as exc:
        return ProviderResult(source, SourceStatus.QC_FAILED, reason=f"Tiingo parse/QC error: {exc}")
    rows.sort(key=lambda row: row["date"])
    return _validate_result(source, tuple(rows), ticker=ticker)
