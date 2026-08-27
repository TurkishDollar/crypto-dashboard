import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone

st.set_page_config(
    page_title="Juno₿TWHunteR",
    page_icon="₿",
    layout="wide"
)

# =========================================================
# JUNO₿TWHUNTER
# REAL DATA ONLY
# BYBIT + OKX
# =========================================================

BYBIT_URL = "https://api.bybit.com"
OKX_URL = "https://www.okx.com"

TIMEOUT = 10


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #05070b;
    color: #ffffff;
}

.title {
    text-align: center;
    font-size: 32px;
    font-weight: 900;
    color: white;
    margin-bottom: 5px;
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
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    font-size: 32px;
    font-weight: 900;
}

.short {
    background: rgba(255,48,79,0.12);
    border: 2px solid #ff304f;
    color: #ff304f;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    font-size: 32px;
    font-weight: 900;
}

.wait {
    background: rgba(150,160,175,0.10);
    border: 2px solid #778196;
    color: #b8c0cc;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    font-size: 32px;
    font-weight: 900;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# TITLE
# =========================================================

st.markdown(
    '<div class="title">Juno₿TWHunteR 🌎₿</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'REAL MARKET INTELLIGENCE — NO MOCK / NO DEMO DATA'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Market Settings")

symbol = st.sidebar.text_input(
    "Coin",
    "BTCUSDT"
).upper().strip()

timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["1m", "3m", "5m", "15m", "30m", "1h", "4h", "1d"],
    index=3
)

if st.sidebar.button("🔄 Yenile"):
    st.rerun()


# =========================================================
# REQUEST FUNCTION
# =========================================================

def get_json(url, params=None):

    try:

        response = requests.get(
            url,
            params=params,
            timeout=TIMEOUT
        )

        return response.status_code, response.json()

    except Exception as error:

        return None, {
            "error": str(error)
        }


# =========================================================
# BYBIT PRICE
# =========================================================

def get_bybit_price():

    status, data = get_json(
        BYBIT_URL + "/v5/market/tickers",
        {
            "category": "linear",
            "symbol": symbol
        }
    )

    if status != 200:
        return None, data

    try:

        item = data["result"]["list"][0]

        return {
            "price": float(item["lastPrice"]),
            "change": float(item["price24hPcnt"]) * 100,
            "high": float(item["highPrice24h"]),
            "low": float(item["lowPrice24h"]),
            "volume": float(item["turnover24h"])
        }, None

    except Exception as error:

        return None, {
            "error": str(error)
        }


# =========================================================
# OKX PRICE
# =========================================================

def get_okx_price():

    inst_id = symbol.replace(
        "USDT",
        "-USDT-SWAP"
    )

    status, data = get_json(
        OKX_URL + "/api/v5/market/ticker",
        {
            "instId": inst_id
        }
    )

    if status != 200:
        return None, data

    try:

        item = data["data"][0]

        price = float(item["last"])
        open_price = float(item["open24h"])

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
        }, None

    except Exception as error:

        return None, {
            "error": str(error)
        }


# =========================================================
# BYBIT KLINES
# =========================================================

def get_klines():

    interval = {
        "1m": "1",
        "3m": "3",
        "5m": "5",
        "15m": "15",
        "30m": "30",
        "1h": "60",
        "4h": "240",
        "1d": "D"
    }

    status, data = get_json(
        BYBIT_URL + "/v5/market/kline",
        {
            "category": "linear",
            "symbol": symbol,
            "interval": interval[timeframe],
            "limit": 100
        }
    )

    if status != 200:
        return None, data

    try:

        rows = data["result"]["list"]

        rows.reverse()

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

        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "turnover"
        ]

        for column in numeric_columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        return df, None

    except Exception as error:

        return None, {
            "error": str(error)
        }


# =========================================================
# GET REAL DATA
# =========================================================

bybit, bybit_error = get_bybit_price()

okx, okx_error = get_okx_price()

df, kline_error = get_klines()


# =========================================================
# CONNECTION STATUS
# =========================================================

st.subheader("🌐 Gerçek Veri Kaynakları")

col1, col2 = st.columns(2)

with col1:

    if bybit is not None:

        st.markdown(
            '<div class="online">🟢 BYBIT API — ONLINE</div>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            '<div class="offline">🔴 BYBIT API — OFFLINE</div>',
            unsafe_allow_html=True
        )

        st.code(str(bybit_error))


with col2:

    if okx is not None:

        st.markdown(
            '<div class="online">🟢 OKX API — ONLINE</div>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            '<div class="offline">🔴 OKX API — OFFLINE</div>',
            unsafe_allow_html=True
        )

        st.code(str(okx_error))


# =========================================================
# STOP IF NO REAL DATA
# =========================================================

if bybit is None:

    st.error(
        "❌ Gerçek piyasa verisi alınamadı."
    )

    st.warning(
        "Sistem sahte veya demo veri üretmiyor."
    )

    st.stop()


# =========================================================
# MARKET DATA
# =========================================================

st.subheader(
    f"💰 {symbol} — Gerçek Piyasa Verisi"
)

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.markdown(
        f"""
        <div class="card">
            <div class="label">BYBIT PERPETUAL</div>
            <div class="value">
                ${bybit["price"]:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:

    if okx is not None:

        okx_text = f"${okx['price']:,.2f}"

    else:

        okx_text = "VERİ YOK"

    st.markdown(
        f"""
        <div class="card">
            <div class="label">OKX PERPETUAL</div>
            <div class="value">
                {okx_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:

    st.markdown(
        f"""
        <div class="card">
            <div class="label">24H CHANGE</div>
            <div class="value">
                {bybit["change"]:+.2f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:

    st.markdown(
        f"""
        <div class="card">
            <div class="label">TIMEFRAME</div>
            <div class="value">
                {timeframe.upper()}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# HIGH / LOW / VOLUME
# =========================================================

st.subheader("📊 Gerçek 24H Piyasa Verileri")

a, b, c = st.columns(3)

with a:

    st.metric(
        "24H High",
        f"${bybit['high']:,.2f}"
    )

with b:

    st.metric(
        "24H Low",
        f"${bybit['low']:,.2f}"
    )

with c:

    st.metric(
        "24H Turnover",
        f"${bybit['volume']:,.0f}"
    )


# =========================================================
# REAL CANDLE DATA
# =========================================================

if df is not None:

    st.subheader(
        f"📈 {symbol} — {timeframe} Gerçek Mum Verileri"
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.error(
        "❌ Gerçek mum verisi alınamadı."
    )

    st.code(
        str(kline_error)
    )


# =========================================================
# BASIC REAL SIGNAL
# =========================================================

if df is not None and len(df) >= 21:

    df["EMA9"] = df["close"].ewm(
        span=9,
        adjust=False
    ).mean()

    df["EMA21"] = df["close"].ewm(
        span=21,
        adjust=False
    ).mean()

    last = df.iloc[-1]

    st.subheader("🎯 Gerçek Veri Tabanlı Sinyal")

    if last["EMA9"] > last["EMA21"]:

        st.markdown(
            '<div class="long">🟢 LONG</div>',
            unsafe_allow_html=True
        )

        st.info(
            "Gerçek Bybit mum verisinde EMA 9, EMA 21'in üzerinde."
        )

    elif last["EMA9"] < last["EMA21"]:

        st.markdown(
            '<div class="short">🔴 SHORT</div>',
            unsafe_allow_html=True
        )

        st.info(
            "Gerçek Bybit mum verisinde EMA 9, EMA 21'in altında."
        )

    else:

        st.markdown(
            '<div class="wait">⚪ WAIT</div>',
            unsafe_allow_html=True
        )


# =========================================================
# FOOTER
# =========================================================

now = datetime.now(
    timezone.utc
).strftime(
    "%Y-%m-%d %H:%M:%S UTC"
)

st.divider()

st.markdown(
    f"""
    <div style="
        text-align:center;
        color:#748095;
        font-size:12px;
    ">
        🟢 REAL DATA ONLY |
        ❌ MOCK DATA |
        ❌ DEMO DATA |
        Last update: {now}
    </div>
    """,
    unsafe_allow_html=True
)
