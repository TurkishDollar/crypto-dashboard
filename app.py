import json
import threading
import time
from collections import deque
from datetime import datetime, timezone

import pandas as pd
import requests
import streamlit as st
import websocket
import plotly.graph_objects as go


st.set_page_config(
    page_title="Juno₿TWHunteR",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CONFIG
# ============================================================

OKX_REST = "https://www.okx.com"
OKX_WS = "wss://ws.okx.com:8443/ws/v5/public"

REST_TIMEOUT = 10
MAX_TRADES = 200


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background: #05070b;
        color: #f1f5f9;
    }

    .block-container {
        padding-top: 1rem;
        max-width: 1500px;
    }

    .title {
        text-align: center;
        font-size: 34px;
        font-weight: 900;
        color: white;
    }

    .subtitle {
        text-align: center;
        color: #8792a5;
        font-size: 13px;
        margin-bottom: 20px;
    }

    .card {
        background: #101620;
        border: 1px solid #263247;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        min-height: 90px;
    }

    .label {
        color: #8b96a8;
        font-size: 11px;
        font-weight: 800;
    }

    .value {
        color: white;
        font-size: 22px;
        font-weight: 900;
        margin-top: 7px;
    }

    .long {
        background: rgba(0, 230, 118, 0.12);
        border: 2px solid #00e676;
        color: #00ff88;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        font-size: 38px;
        font-weight: 900;
    }

    .short {
        background: rgba(255, 48, 79, 0.12);
        border: 2px solid #ff304f;
        color: #ff304f;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        font-size: 38px;
        font-weight: 900;
    }

    .wait {
        background: rgba(150, 160, 175, 0.10);
        border: 2px solid #687386;
        color: #c2c9d3;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        font-size: 38px;
        font-weight: 900;
    }

    .reason {
        background: #101620;
        border-left: 4px solid #40506a;
        padding: 10px 14px;
        border-radius: 7px;
        margin-bottom: 6px;
    }

    .green {
        color: #00e676;
        font-weight: 900;
    }

    .red {
        color: #ff304f;
        font-weight: 900;
    }

    .yellow {
        color: #ffc107;
        font-weight: 900;
    }
    </style>
    """,
    unsafe_allow_html=True
)


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

if not coin:
    coin = "BTC"

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

whale_threshold = st.sidebar.number_input(
    "🐋 Whale Threshold (USDT)",
    min_value=10000,
    max_value=10000000,
    value=100000,
    step=10000
)

if st.sidebar.button("🔄 Şimdi Yenile"):
    st.rerun()


INST_ID = f"{coin}-USDT-SWAP"


# ============================================================
# OKX REST
# ============================================================

def okx_get(endpoint, params=None):

    try:
        response = requests.get(
            OKX_REST + endpoint,
            params=params,
            timeout=REST_TIMEOUT,
            headers={
                "User-Agent": "JunoBTWHunteR/3.0"
            }
        )

        response.raise_for_status()

        data = response.json()

        if data.get("code") != "0":
            return None, str(data)

        return data, None

    except Exception as error:
        return None, str(error)


# ============================================================
# REST TICKER
# ============================================================

def get_ticker():

    data, error = okx_get(
        "/api/v5/market/ticker",
        {"instId": INST_ID}
    )

    if error:
        return None, error

    try:

        item = data["data"][0]

        price = float(item["last"])
        open24 = float(item["open24h"])

        change = 0

        if open24 != 0:
            change = (
                (price - open24)
                / open24
                * 100
            )

        return {
            "price": price,
            "change": change,
            "high": float(item["high24h"]),
            "low": float(item["low24h"]),
            "volume": float(item["vol24h"]),
            "quote_volume": float(item["volCcy24h"])
        }, None

    except Exception as error:
        return None, str(error)


# ============================================================
# OKX CANDLES
# ============================================================

def get_candles():

    data, error = okx_get(
        "/api/v5/market/candles",
        {
            "instId": INST_ID,
            "bar": timeframe,
            "limit": "200"
        }
    )

    if error:
        return None, error

    try:

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
                "vol_ccy",
                "vol_ccy_quote",
                "confirm"
            ]
        )

        df["timestamp"] = pd.to_datetime(
            pd.to_numeric(
                df["timestamp"]
            ),
            unit="ms",
            utc=True
        )

        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "vol_ccy",
            "vol_ccy_quote"
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
# TECHNICAL ANALYSIS
# ============================================================

def calculate_indicators(df):

    df = df.copy()

    df["EMA9"] = (
        df["close"]
        .ewm(
            span=9,
            adjust=False
        )
        .mean()
    )

    df["EMA21"] = (
        df["close"]
        .ewm(
            span=21,
            adjust=False
        )
        .mean()
    )

    df["EMA50"] = (
        df["close"]
        .ewm(
            span=50,
            adjust=False
        )
        .mean()
    )

    df["EMA200"] = (
        df["close"]
        .ewm(
            span=200,
            adjust=False
        )
        .mean()
    )

    delta = df["close"].diff()

    gain = delta.clip(
        lower=0
    )

    loss = -delta.clip(
        upper=0
    )

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

    df["RSI"] = (
        100 -
        (
            100 /
            (1 + rs)
        )
    )

    df["RSI"] = df["RSI"].fillna(50)

    typical_price = (
        df["high"]
        + df["low"]
        + df["close"]
    ) / 3

    df["VWAP"] = (
        typical_price * df["volume"]
    ).cumsum() / df["volume"].cumsum()

    df["VolumeMA20"] = (
        df["volume"]
        .rolling(20)
        .mean()
    )

    df["VolumeRatio"] = (
        df["volume"]
        /
        df["VolumeMA20"]
    )

    return df


# ============================================================
# WEBSOCKET ENGINE
# ============================================================

class OKXEngine:

    def __init__(self, inst_id):

        self.inst_id = inst_id

        self.connected = False
        self.error = None

        self.price = None
        self.bid = None
        self.ask = None

        self.bid_size = 0.0
        self.ask_size = 0.0

        self.buy_volume = 0.0
        self.sell_volume = 0.0

        self.trades = deque(
            maxlen=MAX_TRADES
        )

        self.thread = None

    def on_open(self, ws):

        self.connected = True
        self.error = None

        subscribe = {
            "op": "subscribe",
            "args": [
                {
                    "channel": "tickers",
                    "instId": self.inst_id
                },
                {
                    "channel": "trades",
                    "instId": self.inst_id
                },
                {
                    "channel": "books5",
                    "instId": self.inst_id
                }
            ]
        }

        ws.send(
            json.dumps(subscribe)
        )

    def on_message(self, ws, message):

        try:

            msg = json.loads(message)

            if msg.get("event") == "error":
                self.error = str(msg)
                return

            channel = (
                msg.get("arg", {})
                .get("channel")
            )

            data = msg.get(
                "data",
                []
            )

            if not data:
                return

            # -------------------------------
            # TICKER
            # -------------------------------

            if channel == "tickers":

                item = data[0]

                self.price = float(
                    item["last"]
                )

                self.bid = float(
                    item["bidPx"]
                )

                self.ask = float(
                    item["askPx"]
                )

            # -------------------------------
            # TRADES
            # -------------------------------

            elif channel == "trades":

                for item in data:

                    price = float(
                        item["px"]
                    )

                    size = float(
                        item["sz"]
                    )

                    side = item["side"]

                    timestamp = int(
                        item["ts"]
                    )

                    value = price * size

                    if side == "buy":
                        self.buy_volume += value
                    elif side == "sell":
                        self.sell_volume += value

                    self.trades.appendleft(
                        {
                            "side": side.upper(),
                            "price": price,
                            "size": size,
                            "value": value,
                            "time": datetime.fromtimestamp(
                                timestamp / 1000,
                                timezone.utc
                            ).strftime("%H:%M:%S")
                        }
                    )

            # -------------------------------
            # ORDER BOOK
            # -------------------------------

            elif channel == "books5":

                item = data[0]

                bids = item.get(
                    "bids",
                    []
                )

                asks = item.get(
                    "asks",
                    []
                )

                if bids:

                    self.bid = float(
                        bids[0][0]
                    )

                    self.bid_size = sum(
                        float(row[1])
                        for row in bids
                    )

                if asks:

                    self.ask = float(
                        asks[0][0]
                    )

                    self.ask_size = sum(
                        float(row[1])
                        for row in asks
                    )

        except Exception as error:

            self.error = str(error)

    def on_error(self, ws, error):

        self.connected = False
        self.error = str(error)

    def on_close(self, ws, code, message):

        self.connected = False

    def run(self):

        while True:

            try:

                ws = websocket.WebSocketApp(
                    OKX_WS,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close
                )

                ws.run_forever(
                    ping_interval=20,
                    ping_timeout=10
                )

            except Exception as error:

                self.connected = False
                self.error = str(error)

            time.sleep(3)

    def start(self):

        if self.thread is not None:
            return

        self.thread = threading.Thread(
            target=self.run,
            daemon=True
        )

        self.thread.start()


# ============================================================
# WEBSOCKET RESOURCE
# ============================================================

@st.cache_resource
def create_engine(inst_id):

    engine = OKXEngine(
        inst_id
    )

    engine.start()

    return engine


engine = create_engine(
    INST_ID
)


# ============================================================
# GET REAL DATA
# ============================================================

ticker, ticker_error = get_ticker()

candles, candle_error = get_candles()


# ============================================================
# DATA ERROR
# ============================================================

if ticker is None or candles is None:

    st.error(
        "❌ Gerçek OKX piyasa verisi alınamadı."
    )

    if ticker_error:
        st.code(
            "Ticker API:\n" +
            str(ticker_error)
        )

    if candle_error:
        st.code(
            "Candle API:\n" +
            str(candle_error)
        )

    st.warning(
        "Sistem sahte veya demo veri göstermiyor."
    )

    st.stop()


# ============================================================
# INDICATORS
# ============================================================

candles = calculate_indicators(
    candles
)

last = candles.iloc[-1]


# ============================================================
# LIVE PRICE
# ============================================================

live_price = engine.price

if live_price is None:
    live_price = ticker["price"]


# ============================================================
# ORDER BOOK IMBALANCE
# ============================================================

book_total = (
    engine.bid_size
    +
    engine.ask_size
)

if book_total > 0:

    book_imbalance = (
        engine.bid_size
        -
        engine.ask_size
    ) / book_total * 100

else:

    book_imbalance = 0.0


# ============================================================
# FLOW IMBALANCE
# ============================================================

flow_total = (
    engine.buy_volume
    +
    engine.sell_volume
)

if flow_total > 0:

    flow_imbalance = (
        engine.buy_volume
        -
        engine.sell_volume
    ) / flow_total * 100

else:

    flow_imbalance = 0.0


# ============================================================
# SIGNAL ENGINE
# ============================================================

score = 0
reasons = []


# EMA 9 / 21

if last["EMA9"] > last["EMA21"]:

    score += 2

    reasons.append(
        "EMA 9 > EMA 21 → kısa vadeli yükseliş"
    )

else:

    score -= 2

    reasons.append(
        "EMA 9 < EMA 21 → kısa vadeli düşüş"
    )


# EMA 50

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


# EMA 200

if last["close"] > last["EMA200"]:

    score += 2

    reasons.append(
        "Fiyat EMA 200 üzerinde"
    )

else:

    score -= 2

    reasons.append(
        "Fiyat EMA 200 altında"
    )


# RSI

rsi = float(
    last["RSI"]
)

if 50 < rsi < 70:

    score += 1

    reasons.append(
        f"RSI {rsi:.2f} → bullish momentum"
    )

elif 30 < rsi < 50:

    score -= 1

    reasons.append(
        f"RSI {rsi:.2f} → bearish momentum"
    )

elif rsi >= 70:

    reasons.append(
        f"RSI {rsi:.2f} → aşırı alım"
    )

else:

    reasons.append(
        f"RSI {rsi:.2f} → aşırı satım"
    )


# VWAP

if last["close"] > last["VWAP"]:

    score += 1

    reasons.append(
        "Fiyat VWAP üzerinde"
    )

else:

    score -= 1

    reasons.append(
        "Fiyat VWAP altında"
    )


# Volume

volume_ratio = last["VolumeRatio"]

if pd.notna(volume_ratio):

    if volume_ratio >= 1.5:

        if score > 0:
            score += 1

        elif score < 0:
            score -= 1

        reasons.append(
            f"Hacim güçlü → {volume_ratio:.2f}x"
        )

    else:

        reasons.append(
            f"Hacim normal → {volume_ratio:.2f}x"
        )


# Order book

if book_imbalance > 10:

    score += 2

    reasons.append(
        f"Order Book → alıcı baskısı "
        f"{book_imbalance:+.2f}%"
    )

elif book_imbalance < -10:

    score -= 2

    reasons.append(
        f"Order Book → satıcı baskısı "
        f"{book_imbalance:+.2f}%"
    )

else:

    reasons.append(
        f"Order Book → dengeli "
        f"{book_imbalance:+.2f}%"
    )


# Real trade flow

if flow_imbalance > 15:

    score += 2

    reasons.append(
        f"Gerçek işlem akışı → BUY "
        f"{flow_imbalance:+.2f}%"
    )

elif flow_imbalance < -15:

    score -= 2

    reasons.append(
        f"Gerçek işlem akışı → SELL "
        f"{flow_imbalance:+.2f}%"
    )

else:

    reasons.append(
        f"Gerçek işlem akışı → dengeli "
        f"{flow_imbalance:+.2f}%"
    )


# ============================================================
# FINAL SIGNAL
# ============================================================

if score >= 5:

    signal = "LONG"

elif score <= -5:

    signal = "SHORT"

else:

    signal = "WAIT"


signal_strength = min(
    100,
    int(
        abs(score) / 12 * 100
    )
)


# ============================================================
# CONNECTION STATUS
# ============================================================

st.subheader(
    "🌐 Gerçek Veri Kaynakları"
)

s1, s2 = st.columns(2)

with s1:

    if engine.connected:

        st.markdown(
            '<span class="
