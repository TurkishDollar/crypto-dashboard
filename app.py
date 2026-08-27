import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone

# ============================================================
# JUNO₿TWHUNTER
# OKX REAL MARKET DATA
# NO MOCK / NO DEMO DATA
# ============================================================

st.set_page_config(
    page_title="Juno₿TWHunteR",
    page_icon="₿",
    layout="wide"
)

OKX_URL = "https://www.okx.com"
TIMEOUT = 10


# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #05070b;
    color: #ffffff;
}

.title {
    text-align: center;
    font-size: 34px;
    font-weight: 900;
    color: #ffffff;
}

.subtitle {
    text-align: center;
    color: #8d98aa;
    font-size: 13px;
    margin-bottom: 25px;
}

.card {
    background: #111722;
    border: 1px solid #293449;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}

.label {
    color: #8d98aa;
    font-size: 11px;
    font-weight: 800;
}

.value {
    color: #ffffff;
    font-size: 24px;
    font-weight: 900;
    margin-top: 8px;
}

.online {
    color: #00e676;
    font-weight: 900;
}

.offline {
    color: #ff304f;
    font-weight: 900;
}

.long {
    background: rgba(0,230,118,0.12);
    border: 2px solid #00e676;
    color: #00ff88;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    font-size: 38px;
    font-weight: 900;
}

.short {
    background: rgba(255,48,79,0.12);
    border: 2px solid #ff304f;
    color: #ff304f;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    font-size: 38px;
    font-weight: 900;
}

.wait {
    background: rgba(150,160,175,0.10);
    border: 2px solid #778196;
    color: #b8c0cc;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    font-size: 38px;
    font-weight: 900;
}

.reason {
    background: #111722;
    border-left: 4px solid #344155;
    padding: 10px 14px;
    margin-bottom: 7px;
    border-radius: 6px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="title">Juno₿TWHunteR 🌎₿</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'REAL-TIME OKX MARKET INTELLIGENCE — NO MOCK / NO DEMO'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Market Settings")

coin = st.sidebar.text_input(
    "Coin",
    value="BTC"
).upper().strip()

timeframe = st.sidebar.selectbox(
    "Timeframe",
    [
        "1m",
        "3m",
        "5m",
        "15m",
        "30m",
        "1H",
        "4H",
        "1D"
    ],
    index=3
)

if st.sidebar.button("🔄 Gerçek Veriyi Yenile"):
    st.rerun()


# ============================================================
# OKX SYMBOL
# ============================================================

inst_id = coin + "-USDT-SWAP"


# ============================================================
# SAFE OKX REQUEST
# ============================================================

def okx_get(endpoint, params=None):

    try:

        response = requests.get(
            OKX_URL + endpoint,
            params=params,
            timeout=TIMEOUT,
            headers={
                "User-Agent": "JunoBTWHunteR/1.0"
            }
        )

        text = response.text

        if response.status_code != 200:

            return None, (
                f"HTTP {response.status_code}: {text}"
            )

        try:

            data = response.json()

        except Exception:

            return None, (
                "OKX JSON olmayan cevap döndürdü: "
                + text[:500]
            )

        return data, None

    except Exception as error:

        return None, str(error)


# ============================================================
# TICKER
# ============================================================

def get_ticker():

    data, error = okx_get(
        "/api/v5/market/ticker",
        {
            "instId": inst_id
        }
    )

    if error:
        return None, error

    try:

        if data["code"] != "0":
            return None, str(data)

        if not data["data"]:
            return None, "OKX sembol bulunamadı."

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
            "open": open24,
            "change": change,
            "high": float(item["high24h"]),
            "low": float(item["low24h"]),
            "volume": float(item["vol24h"]),
            "quote_volume": float(item["volCcy24h"])
        }, None

    except Exception as error:

        return None, str(error)


# ============================================================
# CANDLES
# ============================================================

def get_candles():

    interval_map = {
        "1m": "1m",
        "3m": "3m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1H": "1H",
        "4H": "4H",
        "1D": "1D"
    }

    data, error = okx_get(
        "/api/v5/market/candles",
        {
            "instId": inst_id,
            "bar": interval_map[timeframe],
            "limit": "200"
        }
    )

    if error:
        return None, error

    try:

        if data["code"] != "0":
            return None, str(data)

        rows = data["data"]

        rows.reverse()

        df = pd.DataFrame(
            rows,
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "volume_currency",
                "volume_usdt",
                "confirm"
            ]
        )

        df["timestamp"] = pd.to_datetime(
            pd.to_numeric(df["timestamp"]),
            unit="ms"
        )

        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "volume_currency",
            "volume_usdt"
        ]

        for column in numeric_columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        return df, None

    except Exception as error:

        return None, str(error)


# ============================================================
# GET REAL DATA
# ============================================================

ticker, ticker_error = get_ticker()

candles, candles_error = get_candles()


# ============================================================
# API STATUS
# ============================================================

st.subheader("🌐 Gerçek Veri Kaynağı")

if ticker is not None:

    st.markdown(
        '<div class="online">'
        '🟢 OKX API — ONLINE'
        '</div>',
        unsafe_allow_html=True
    )

else:

    st.markdown(
        '<div class="offline">'
        '🔴 OKX API — OFFLINE'
        '</div>',
        unsafe_allow_html=True
    )

    st.code(str(ticker_error))

    st.stop()


# ============================================================
# MARKET HEADER
# ============================================================

st.subheader(
    f"💰 {coin}/USDT PERPETUAL"
)

c1, c2, c3, c4 = st.columns(4)


with c1:

    st.markdown(
        f"""
        <div class="card">
            <div class="label">
                OKX LIVE PRICE
            </div>
            <div class="value">
                ${ticker["price"]:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with c2:

    st.markdown(
        f"""
        <div class="card">
            <div class="label">
                24H CHANGE
            </div>
            <div class="value">
                {ticker["change"]:+.2f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with c3:

    st.markdown(
        f"""
        <div class="card">
            <div class="label">
                24H HIGH
            </div>
            <div class="value">
                ${ticker["high"]:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with c4:

    st.markdown(
        f"""
        <div class="card">
            <div class="label">
                24H LOW
            </div>
            <div class="value">
                ${ticker["low"]:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# VOLUME
# ============================================================

st.subheader("📊 Gerçek Piyasa Hacmi")

v1, v2 = st.columns(2)

with v1:

    st.metric(
        "24H Volume",
        f"{ticker['volume']:,.2f}"
    )

with v2:

    st.metric(
        "24H Quote Volume",
        f"${ticker['quote_volume']:,.0f}"
    )


# ============================================================
# CANDLE DATA
# ============================================================

if candles is None:

    st.error(
        "❌ Gerçek OKX mum verisi alınamadı."
    )

    st.code(str(candles_error))

    st.stop()


# ============================================================
# INDICATORS
# ============================================================

candles["EMA9"] = candles["close"].ewm(
    span=9,
    adjust=False
).mean()

candles["EMA21"] = candles["close"].ewm(
    span=21,
    adjust=False
).mean()

candles["EMA50"] = candles["close"].ewm(
    span=50,
    adjust=False
).mean()

candles["EMA200"] = candles["close"].ewm(
    span=200,
    adjust=False
).mean()


# ============================================================
# RSI
# ============================================================

delta = candles["close"].diff()

gain = delta.clip(lower=0)

loss = -delta.clip(upper=0)

avg_gain = gain.ewm(
    alpha=1 / 14,
    adjust=False
).mean()

avg_loss = loss.ewm(
    alpha=1 / 14,
    adjust=False
).mean()

rs = avg_gain / avg_loss.replace(
    0,
    pd.NA
)

candles["RSI"] = (
    100
    - (
        100
        / (1 + rs)
    )
)

candles["RSI"] = candles["RSI"].fillna(50)


# ============================================================
# LAST CANDLE
# ============================================================

last = candles.iloc[-1]


# ============================================================
# SIGNAL ENGINE
# ============================================================

score = 0

reasons = []


if last["EMA9"] > last["EMA21"]:

    score += 1

    reasons.append(
        "EMA 9 > EMA 21 → kısa vadeli yükseliş"
    )

else:

    score -= 1

    reasons.append(
        "EMA 9 < EMA 21 → kısa vadeli düşüş"
    )


if last["close"] > last["EMA50"]:

    score += 1

    reasons.append(
        "Fiyat EMA 50 üzerinde"
    )

else:

    score -= 1

    reasons.append(
        "Fiyat EMA 50 altında"
    )


if last["close"] > last["EMA200"]:

    score += 1

    reasons.append(
        "Fiyat EMA 200 üzerinde"
    )

else:

    score -= 1

    reasons.append(
        "Fiyat EMA 200 altında"
    )


if 50 < last["RSI"] < 70:

    score += 1

    reasons.append(
        f"RSI {last['RSI']:.2f} → bullish momentum"
    )

elif 30 < last["RSI"] < 50:

    score -= 1

    reasons.append(
        f"RSI {last['RSI']:.2f} → bearish momentum"
    )

elif last["RSI"] >= 70:

    reasons.append(
        f"RSI {last['RSI']:.2f} → aşırı alım"
    )

else:

    reasons.append(
        f"RSI {last['RSI']:.2f} → aşırı satım"
    )


# ============================================================
# FINAL SIGNAL
# ============================================================

if score >= 2:

    signal = "LONG"

    confidence = 60 + score * 8

elif score <= -2:

    signal = "SHORT"

    confidence = 60 + abs(score) * 8

else:

    signal = "WAIT"

    confidence = 50


confidence = min(
    confidence,
    95
)


# ============================================================
# SIGNAL DISPLAY
# ============================================================

st.subheader("🎯 Juno₿TWHunteR Sinyali")

if signal == "LONG":

    st.markdown(
        f"""
        <div class="long">
            🟢 LONG
            <br>
            <span style="font-size:20px;">
                Güven: {confidence}%
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

elif signal == "SHORT":

    st.markdown(
        f"""
        <div class="short">
            🔴 SHORT
            <br>
            <span style="font-size:20px;">
                Güven: {confidence}%
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        f"""
        <div class="wait">
            ⚪ WAIT
            <br>
            <span style="font-size:20px;">
                Güven: {confidence}%
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# INDICATOR VALUES
# ============================================================

st.subheader("📈 Gerçek Teknik Veriler")

i1, i2, i3, i4, i5 = st.columns(5)

with i1:

    st.metric(
        "RSI",
        f"{last['RSI']:.2f}"
    )

with i2:

    st.metric(
        "EMA 9",
        f"${last['EMA9']:,.2f}"
    )

with i3:

    st.metric(
        "EMA 21",
        f"${last['EMA21']:,.2f}"
    )

with i4:

    st.metric(
        "EMA 50",
        f"${last['EMA50']:,.2f}"
    )

with i5:

    st.metric(
        "EMA 200",
        f"${last['EMA200']:,.2f}"
    )


# ============================================================
# SIGNAL REASONS
# ============================================================

st.subheader("🧠 Sinyal Nedenleri")

for reason in reasons:

    st.markdown(
        f"""
        <div class="reason">
            {reason}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# REAL CANDLE CHART
# ============================================================

st.subheader(
    f"📊 {coin}/USDT — {timeframe}"
)

chart = candles.set_index(
    "timestamp"
)

st.line_chart(
    chart["close"],
    height=400
)


# ============================================================
# RAW REAL DATA
# ============================================================

with st.expander(
    "🔎 Gerçek OKX Mum Verisini Gör"
):

    st.dataframe(
        candles.tail(50),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

utc_now = datetime.now(
    timezone.utc
)

st.divider()

st.markdown(
    f"""
    <div style="
        text-align:center;
        color:#748095;
        font-size:12px;
    ">
        🟢 OKX REAL DATA<br>
        ❌ MOCK DATA<br>
        ❌ DEMO DATA<br>
        Last Update:
        {utc_now.strftime("%Y-%m-%d %H:%M:%S UTC")}
    </div>
    """,
    unsafe_allow_html=True
)
