import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone

# ============================================================
# JUNO₿TWHUNTER
# REAL MARKET DATA
# BYBIT + OKX
# NO MOCK / NO DEMO DATA
# ============================================================

st.set_page_config(
    page_title="Juno₿TWHunteR",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BYBIT_API = "https://api.bybit.com"
OKX_API = "https://www.okx.com"

KLINE_LIMIT = 200

session = requests.Session()

session.headers.update({
    "User-Agent": "JunoBTWHunteR/2.0"
})


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background:#080b11;
    color:#e8edf5;
}

.block-container {
    padding-top:1rem;
}

.title {
    text-align:center;
    font-size:32px;
    font-weight:900;
    color:#ffffff;
}

.subtitle {
    text-align:center;
    color:#8b97aa;
    font-size:13px;
    margin-bottom:20px;
}

.card {
    background:#111823;
    border:1px solid #263247;
    border-radius:14px;
    padding:16px;
    text-align:center;
}

.label {
    color:#8793a6;
    font-size:11px;
    font-weight:800;
}

.value {
    color:#ffffff;
    font-size:21px;
    font-weight:900;
    margin-top:5px;
}

.long {
    background:rgba(0,230,118,.10);
    border:3px solid #00e676;
    color:#00ff88;
    border-radius:18px;
    padding:24px;
    text-align:center;
    font-size:42px;
    font-weight:900;
    box-shadow:0 0 25px rgba(0,230,118,.15);
}

.short {
    background:rgba(255,48,79,.10);
    border:3px solid #ff304f;
    color:#ff304f;
    border-radius:18px;
    padding:24px;
    text-align:center;
    font-size:42px;
    font-weight:900;
    box-shadow:0 0 25px rgba(255,48,79,.15);
}

.wait {
    background:rgba(130,140,155,.10);
    border:3px solid #778196;
    color:#c0c6d0;
    border-radius:18px;
    padding:24px;
    text-align:center;
    font-size:42px;
    font-weight:900;
}

.confidence {
    text-align:center;
    font-size:22px;
    font-weight:900;
    margin:12px 0 20px;
}

.reason {
    background:#111823;
    border-left:4px solid #344155;
    border-radius:6px;
    padding:10px;
    margin-bottom:7px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# GENERIC REQUEST
# ============================================================

def get_json(url, params=None):

    try:

        response = session.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:

            return None

        data = response.json()

        return data

    except Exception:

        return None


# ============================================================
# BYBIT SERVER TEST
# ============================================================

def bybit_test():

    data = get_json(
        f"{BYBIT_API}/v5/market/time"
    )

    return data is not None


# ============================================================
# OKX SERVER TEST
# ============================================================

def okx_test():

    data = get_json(
        f"{OKX_API}/api/v5/public/time"
    )

    return data is not None


# ============================================================
# BYBIT TICKER
# ============================================================

def bybit_ticker(symbol):

    data = get_json(
        f"{BYBIT_API}/v5/market/tickers",
        {
            "category": "linear",
            "symbol": symbol
        }
    )

    if not data:
        return None

    try:

        item = data["result"]["list"][0]

        return {
            "price": float(item["lastPrice"]),
            "change": float(item["price24hPcnt"]) * 100,
            "high": float(item["highPrice24h"]),
            "low": float(item["lowPrice24h"]),
            "volume": float(item["turnover24h"]),
            "open_interest": float(item["openInterest"])
        }

    except Exception:

        return None


# ============================================================
# BYBIT KLINES
# ============================================================

def bybit_klines(symbol, interval):

    interval_map = {
        "1m": "1",
        "3m": "3",
        "5m": "5",
        "15m": "15",
        "30m": "30",
        "1h": "60",
        "4h": "240",
        "1d": "D"
    }

    bybit_interval = interval_map[interval]

    data = get_json(
        f"{BYBIT_API}/v5/market/kline",
        {
            "category": "linear",
            "symbol": symbol,
            "interval": bybit_interval,
            "limit": KLINE_LIMIT
        }
    )

    if not data:
        return None

    try:

        rows = data["result"]["list"]

        rows = list(reversed(rows))

        df = pd.DataFrame(
            rows,
            columns=[
                "time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "turnover"
            ]
        )

        df["time"] = pd.to_datetime(
            pd.to_numeric(df["time"]),
            unit="ms"
        )

        for col in [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "turnover"
        ]:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        return df

    except Exception:

        return None


# ============================================================
# OKX TICKER
# ============================================================

def okx_ticker(symbol):

    inst_id = symbol.replace(
        "USDT",
        "-USDT-SWAP"
    )

    data = get_json(
        f"{OKX_API}/api/v5/market/ticker",
        {
            "instId": inst_id
        }
    )

    if not data:
        return None

    try:

        item = data["data"][0]

        last = float(item["last"])
        open24 = float(item["open24h"])

        change = (
            (last - open24)
            / open24
            * 100
        )

        return {
            "price": last,
            "change": change,
            "high": float(item["high24h"]),
            "low": float(item["low24h"]),
            "volume": float(item["volCcy24h"])
        }

    except Exception:

        return None


# ============================================================
# OKX KLINES
# ============================================================

def okx_klines(symbol, interval):

    inst_id = symbol.replace(
        "USDT",
        "-USDT-SWAP"
    )

    bar_map = {
        "1m": "1m",
        "3m": "3m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1H",
        "4h": "4H",
        "1d": "1D"
    }

    data = get_json(
        f"{OKX_API}/api/v5/market/candles",
        {
            "instId": inst_id,
            "bar": bar_map[interval],
            "limit": str(KLINE_LIMIT)
        }
    )

    if not data:
        return None

    try:

        rows = list(
            reversed(data["data"])
        )

        df = pd.DataFrame(
            rows,
            columns=[
                "time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "vol_ccy",
                "vol_ccy_quote",
                "confirm"
            ]
        )

        df["time"] = pd.to_datetime(
            pd.to_numeric(df["time"]),
            unit="ms"
        )

        for col in [
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        return df

    except Exception:

        return None


# ============================================================
# RSI
# ============================================================

def rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(
        lower=0
    )

    loss = -delta.clip(
        upper=0
    )

    avg_gain = gain.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    rs = avg_gain / avg_loss.replace(
        0,
        float("nan")
    )

    result = 100 - (
        100 / (1 + rs)
    )

    return result.fillna(50)


# ============================================================
# INDICATORS
# ============================================================

def indicators(df):

    df = df.copy()

    df["ema9"]
