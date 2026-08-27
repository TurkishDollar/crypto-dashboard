import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone

# ============================================================
# JUNO₿TWHUNTER
# REAL DATA TEST
# BYBIT + OKX
# NO MOCK / NO DEMO DATA
# ============================================================

st.set_page_config(
    page_title="Juno₿TWHunteR",
    page_icon="₿",
    layout="wide"
)

BYBIT = "https://api.bybit.com"
OKX = "https://www.okx.com"

TIMEOUT = 10


# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #080b11;
    color: white;
}

.title {
    text-align: center;
    font-size: 32px;
    font-weight: 900;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #9aa4b5;
    margin-bottom: 25px;
}

.card {
    background: #111823;
    border: 1px solid #293449;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}

.label {
    color: #8d98aa;
    font-size: 12px;
    font-weight: bold;
}

.value {
    color: white;
    font-size: 25px;
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
    'REAL MARKET DATA — NO MOCK / NO DEMO'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SETTINGS
# ============================================================

st.sidebar.header("⚙️ Market Settings")

symbol = st.sidebar.text_input(
    "Coin",
    value="BTCUSDT"
).upper().strip()

timeframe = st.sidebar.selectbox(
    "Timeframe",
    [
        "1m",
        "3m",
        "5m",
        "15m",
        "30m",
        "1h",
        "4h",
        "1d"
    ],
    index=3
)

if st.sidebar.button("🔄 Yenile"):

    st.rerun()


# ============================================================
# BYBIT REQUEST
# ============================================================

def bybit_request(endpoint, params=None):

    try:

        response = requests.get(
            BYBIT + endpoint,
            params=params,
            timeout=TIMEOUT
        )

        return response.status_code, response.json()

    except Exception as e:

        return None, {
            "error": str(e)
        }


# ============================================================
# OKX REQUEST
# ============================================================

def okx_request(endpoint, params=None):

    try:

        response = requests.get(
            OKX + endpoint,
            params=params,
            timeout=TIMEOUT
        )

        return response.status_code, response.json()

    except Exception as e:

        return None, {
            "error": str(e)
        }


# ============================================================
# BYBIT SERVER
# ============================================================

bybit_status, bybit_time = bybit_request(
    "/v5/market/time"
)


# ============================================================
# OKX SERVER
# ============================================================

okx_status, okx_time = okx_request(
    "/api/v5/public/time"
)


# ============================================================
# CONNECTION STATUS
# ============================================================

st.subheader("🌐 Veri Kaynakları")

c1, c2 = st.columns(2)

with c1:

    if bybit_status == 200:

        st.markdown(
            '<div class="online">'
            '🟢 BYBIT API — ONLINE'
            '</div>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            '<div class="offline">'
            '🔴 BYBIT API — OFFLINE'
            '</div>',
            unsafe_allow_html=True
        )

        st.write(bybit_time)


with c2:

    if okx_status == 200:

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

        st.write(okx_time)


# ============================================================
# BYBIT TICKER
# ============================================================

def get_bybit_ticker():

    status, data = bybit_request(
        "/v5/market/tickers",
        {
            "category": "linear",
            "symbol": symbol
        }
    )

    if status != 200:

        return None

    try:

        item = data["result"]["list"][0]

        return {
            "price": float(item["lastPrice"]),
            "change": float(item["price24hPcnt"]) * 100,
            "high": float(item["highPrice24h"]),
            "low": float(item["lowPrice24h"]),
            "volume": float(item["turnover24h"])
        }

    except Exception:

        return None


# ============================================================
# OKX TICKER
# ============================================================

def get_okx_ticker():

    inst_id = symbol.replace(
        "USDT",
        "-USDT-SWAP"
    )

    status, data = okx_request(
        "/api/v5/market/ticker",
        {
            "instId": inst_id
        }
    )

    if status != 200:

        return None

    try:

        item = data["data"][0]

        price = float(
            item["last"]
        )

        open_price = float(
            item["open24h"]
        )

        change = (
            (price - open_price)
            / open_price
            * 100
        )

        return {
            "price": price,
            "change": change,
            "high": float(item["high24h"]),
            "low": float(item["low24h"])
        }

    except Exception:

        return None


# ============================================================
# FETCH PRICES
# ============================================================

bybit = get_bybit_ticker()

okx = get_okx_ticker()


# ============================================================
# ERROR CHECK
# ============================================================

if bybit is None:

    st.error(
        "❌ Bybit gerçek fiyat verisi alınamadı."
    )

    st.stop()


# ============================================================
# MARKET HEADER
# ============================================================

st.subheader(
    f"💰 {symbol} Gerçek Piyasa Verisi"
)

a, b, c, d = st.columns(4)

with a:

    st.markdown(
        f"""
        <div class="card">
            <div class="label">
                BYBIT
            </div>

            <div class="value">
                ${bybit["price"]:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with b:

    if okx:

        st.markdown(
            f"""
            <div class="card">
                <div class="label">
                    OKX
                </div>

                <div class="value">
                    ${okx["price"]:,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <div class="card">
                <div class="label">
                    OKX
                </div>

                <div class="value">
                    VERİ YOK
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

with c:

    st.markdown(
        f"""
        <div class="card">
            <div class="label">
                BYBIT 24H
            </div>

            <div class="value">
                {bybit["change"]:+.2f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with d:

    st.markdown(
        f"""
        <div class="card">
            <div class="label">
                TIMEFRAME
            </div>

            <div class="value">
                {timeframe}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# BYBIT 24H
# ============================================================

st.subheader("📊 Bybit Gerçek Verileri")

x1, x2, x3 = st.columns(3)

with x1:

    st.metric(
        "24H High",
        f"${bybit['high']:,.2f}"
    )

with x2:

    st.metric(
        "24H Low",
        f"${bybit['low']:,.2f}"
    )

with x3:

    st.metric(
        "24H Turnover",
        f"${bybit['volume']:,.0f}"
    )


# ============================================================
# BYBIT KLINES
# ============================================================

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


status, kline_data = bybit_request(
    "/v5/market/kline",
    {
        "category": "linear",
        "symbol": symbol,
        "interval": interval_map[timeframe],
        "limit": 100
    }
)


# ============================================================
# KLINE DISPLAY
# ============================================================

if status == 200:

    try:

        rows = kline_data[
            "result"
        ][
            "list"
        ]

        rows
