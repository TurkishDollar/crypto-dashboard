import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime, timezone

# ============================================================
# JUNO₿TWHUNTER
# REAL BINANCE MARKET DATA
# NO MOCK / NO DEMO DATA
# ============================================================

st.set_page_config(
    page_title="Juno₿TWHunteR",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

SPOT_API = "https://api.binance.com"
FUTURES_API = "https://fapi.binance.com"

KLINE_LIMIT = 250

session = requests.Session()
session.headers.update({
    "User-Agent": "JunoBTWHunteR/1.0"
})


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background: #080b11;
    color: #e8edf5;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}

.title {
    text-align: center;
    font-size: 30px;
    font-weight: 900;
    color: white;
}

.subtitle {
    text-align: center;
    color: #8d98aa;
    font-size: 13px;
    margin-bottom: 20px;
}

.card {
    background: #111823;
    border: 1px solid #253044;
    border-radius: 14px;
    padding: 16px;
    text-align: center;
}

.card-title {
    color: #8d98aa;
    font-size: 11px;
    font-weight: bold;
}

.card-value {
    color: white;
    font-size: 21px;
    font-weight: 900;
    margin-top: 6px;
}

.long-box {
    background: rgba(0,230,118,0.10);
    border: 3px solid #00e676;
    color: #00ff88;
    border-radius: 18px;
    padding: 25px;
    text-align: center;
    font-size: 42px;
    font-weight: 900;
    box-shadow: 0 0 30px rgba(0,230,118,0.18);
}

.short-box {
    background: rgba(255,48,79,0.10);
    border: 3px solid #ff304f;
    color: #ff304f;
    border-radius: 18px;
    padding: 25px;
    text-align: center;
    font-size: 42px;
    font-weight: 900;
    box-shadow: 0 0 30px rgba(255,48,79,0.18);
}

.wait-box {
    background: rgba(130,140,155,0.10);
    border: 3px solid #778196;
    color: #c0c6d0;
    border-radius: 18px;
    padding: 25px;
    text-align: center;
    font-size: 42px;
    font-weight: 900;
}

.confidence {
    text-align: center;
    font-size: 22px;
    font-weight: 800;
    margin-top: 10px;
}

.reason {
    background: #111823;
    border-left: 4px solid #344155;
    border-radius: 6px;
    padding: 10px;
    margin-bottom: 7px;
}

.online {
    color: #00e676;
    font-weight: bold;
}

.offline {
    color: #ff304f;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# API FUNCTION
# ============================================================

def api_get(url, params=None):

    try:

        response = session.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:

            return {
                "error": True,
                "status": response.status_code,
                "message": response.text,
                "url": response.url
            }

        return {
            "error": False,
            "data": response.json(),
            "url": response.url
        }

    except requests.exceptions.Timeout:

        return {
            "error": True,
            "status": "TIMEOUT",
            "message": "Binance API zaman aşımına uğradı.",
            "url": url
        }

    except requests.exceptions.ConnectionError:

        return {
            "error": True,
            "status": "CONNECTION ERROR",
            "message": "Binance API bağlantısı kurulamadı.",
            "url": url
        }

    except Exception as e:

        return {
            "error": True,
            "status": "ERROR",
            "message": str(e),
            "url": url
        }


# ============================================================
# BINANCE CONNECTION TEST
# ============================================================

def test_spot():

    result = api_get(
        f"{SPOT_API}/api/v3/ping"
    )

    return not result["error"], result


def test_futures():

    result = api_get(
        f"{FUTURES_API}/fapi/v1/ping"
    )

    return not result["error"], result


# ============================================================
# SPOT PRICE
# ============================================================

def get_spot_price(symbol):

    result = api_get(
        f"{SPOT_API}/api/v3/ticker/price",
        {"symbol": symbol}
    )

    if result["error"]:
        return None, result

    try:
        return float(result["data"]["price"]), result

    except Exception:
        return None, result


# ============================================================
# FUTURES PRICE
# ============================================================

def get_futures_price(symbol):

    result = api_get(
        f"{FUTURES_API}/fapi/v1/ticker/price",
        {"symbol": symbol}
    )

    if result["error"]:
        return None, result

    try:
        return float(result["data"]["price"]), result

    except Exception:
        return None, result


# ============================================================
# FUTURES 24H
# ============================================================

def get_futures_24h(symbol):

    result = api_get(
        f"{FUTURES_API}/fapi/v1/ticker/24hr",
        {"symbol": symbol}
    )

    if result["error"]:
        return None, result

    try:

        data = result["data"]

        return {
            "change": float(data["priceChangePercent"]),
            "high": float(data["highPrice"]),
            "low": float(data["lowPrice"]),
            "volume": float(data["quoteVolume"]),
            "trades": int(data["count"])
        }, result

    except Exception:

        return None, result


# ============================================================
# FUTURES KLINES
# ============================================================

def get_klines(symbol, interval):

    result = api_get(
        f"{FUTURES_API}/fapi/v1/klines",
        {
            "symbol": symbol,
            "interval": interval,
            "limit": KLINE_LIMIT
        }
    )

    if result["error"]:
        return None, result

    try:

        data = result["data"]

        columns = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore"
        ]

        df = pd.DataFrame(
            data,
            columns=columns
        )

        numeric = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "quote_volume",
            "trades",
            "taker_buy_base",
            "taker_buy_quote"
        ]

        for column in numeric:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        df["open_time"] = pd.to_datetime(
            df["open_time"],
            unit="ms"
        )

        return df, result

    except Exception as e:

        return None, {
            "error": True,
            "status": "DATA ERROR",
            "message": str(e)
        }


# ============================================================
# RSI
# ============================================================

def calculate_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    average_gain = gain.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    average_loss = loss.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    rs = average_gain / average_loss.replace(
        0,
        float("nan")
    )

    rsi = 100 - (
        100 / (1 + rs)
    )

    return rsi.fillna(50)


# ============================================================
# INDICATORS
# ============================================================

def calculate_indicators(df):

    df = df.copy()

    df["ema9"] = df["close"].ewm(
        span=9,
        adjust=False
    ).mean()

    df["ema21"] = df["close"].ewm(
        span=21,
        adjust=False
    ).mean()

    df["ema50"] = df["close"].ewm(
        span=50,
        adjust=False
    ).mean()

    df["ema200"] = df["close"].ewm(
        span=200,
        adjust=False
    ).mean()

    df["rsi"] = calculate_rsi(
        df["close"],
        14
    )

    typical_price = (
        df["high"]
        + df["low"]
        + df["close"]
    ) / 3

    df["vwap"] = (
        typical_price * df["volume"]
    ).cumsum() / df["volume"].cumsum()

    df["volume_ma20"] = (
        df["volume"]
        .rolling(20)
        .mean()
    )

    df["volume_ratio"] = (
        df["volume"]
        / df["volume_ma20"]
    )

    return df


# ============================================================
# SIGNAL ENGINE
# ============================================================

def generate_signal(df):

    if len(df) < 200:

        return {
            "signal": "WAIT",
            "confidence": 0,
            "score": 0,
            "reasons": [
                "200 mum tamamlanana kadar WAIT."
            ]
        }

    last = df.iloc[-1]

    score = 0
    reasons = []

    # EMA 9 / 21
    if last["ema9"] > last["ema21"]:

        score += 2

        reasons.append(
            "EMA 9 > EMA 21 → LONG yönlü momentum"
        )

    else:

        score -= 2

        reasons.append(
            "EMA 9 < EMA 21 → SHORT yönlü momentum"
        )

    # EMA 50
    if last["close"] > last["ema50"]:

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
    if last["close"] > last["ema200"]:

        score += 2

        reasons.append(
            "Fiyat EMA 200 üzerinde → ana trend bullish"
        )

    else:

        score -= 2

        reasons.append(
            "Fiyat EMA 200 altında → ana trend bearish"
        )

    # RSI
    rsi = float(last["rsi"])

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
    if last["close"] > last["vwap"]:

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
    volume_ratio = last["volume_ratio"]

    if pd.notna(volume_ratio):

        reasons.append(
            f"Hacim oranı: {volume_ratio:.2f}x"
        )

        if volume_ratio >= 1.5:

            if score > 0:
                score += 1
            elif score < 0:
                score -= 1

    # Final
    if score >= 4:

        signal = "LONG"

    elif score <= -4:

        signal = "SHORT"

    else:

        signal = "WAIT"

    confidence = min(
        99,
        int(
            50 + abs(score) * 6
        )
    )

    return {
        "signal": signal,
        "confidence": confidence,
        "score": score,
        "rsi": rsi,
        "reasons": reasons
    }


# ============================================================
# PAGE TITLE
# ============================================================

st.markdown(
    '<div class="title">Juno₿TWHunteR 🌎₿</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'REAL-TIME BINANCE MARKET INTELLIGENCE — '
    'NO MOCK / NO DEMO DATA'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Market Settings")

    symbol = st.text_input(
        "Coin",
        "BTCUSDT"
    ).upper().strip()

    timeframe = st.selectbox(
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

    whale_threshold = st.number_input(
        "🐋 Whale Threshold USDT",
        min_value=10000,
        max_value=10000000,
        value=100000,
        step=10000
    )

    refresh = st.button(
        "🔄 Verileri Yenile"
    )

    if refresh:
        st.cache_data.clear()
        st.rerun()


# ============================================================
# API STATUS
# ============================================================

spot_online, spot_test = test_spot()

futures_online, futures_test = test_futures()

status1, status2 = st.columns(2)

with status1:

    if spot_online:

        st.success(
            "🟢 BINANCE SPOT API: ONLINE"
        )

    else:

        st.error(
            "🔴 BINANCE SPOT API: OFFLINE"
        )

        st.code(
            str(spot_test)
        )

with status2:

    if futures_online:

        st.success(
            "🟢 BINANCE FUTURES API: ONLINE"
        )

    else:

        st.error(
            "🔴 BINANCE FUTURES API: OFFLINE"
        )

        st.code(
            str(futures_test)
        )


# ============================================================
# STOP IF API OFFLINE
# ============================================================

if not spot_online or not futures_online:

    st.warning(
        "Gerçek Binance verisi alınamadığı için "
        "uygulama sahte veri göstermiyor."
    )

    st.stop()


# ============================================================
# REAL DATA
# ============================================================

spot_price, spot_result = get_spot_price(
    symbol
)

futures_price, futures_result = get_futures_price(
    symbol
)

stats, stats_result = get_futures_24h(
    symbol
)

df, kline_result = get_klines(
    symbol,
    timeframe
)


# ============================================================
# DATA ERROR
# ============================================================

if spot_price is None:

    st.error(
        "❌ Spot fiyat alınamadı."
    )

    st.code(
        str(spot_result)
    )

    st.stop()


if futures_price is None:

    st.error(
        "❌ Futures fiyat alınamadı."
    )

    st.code(
        str(futures_result)
    )

    st.stop()


if df is None:

    st.error(
        "❌ Futures mum verisi alınamadı."
    )

    st.code(
        str(kline_result)
    )

    st.stop()


# ============================================================
# INDICATORS
# ============================================================

df = calculate_indicators(
    df
)

signal_data = generate_signal(
    df
)

last = df.iloc[-1]


# ============================================================
# MARKET CARDS
# ============================================================

c1, c2, c3, c4, c5 = st.columns(5)

with c1:

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">
                BINANCE SPOT
            </div>
            <div class="card-value">
                ${spot_price:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">
                USDT-M PERPETUAL
            </div>
            <div class="card-value">
                ${futures_price:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">
                24H CHANGE
            </div>
            <div class="card-value">
                {stats["change"]:+.2f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">
                24H HIGH
            </div>
            <div class="card-value">
                ${stats["high"]:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c5:

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">
                24H LOW
            </div>
            <div class="card-value">
                ${stats["low"]:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# ============================================================
# SIGNAL
# ============================================================

signal = signal_data["signal"]
confidence = signal_data["confidence"]

if signal == "LONG":

    st.markdown(
        f"""
        <div class="long-box">
            🟢 LONG
        </div>
        <div class="confidence">
            GÜVEN: {confidence}%
        </div>
        """,
        unsafe_allow_html=True
    )

elif signal == "SHORT":

    st.markdown(
        f"""
        <div class="short-box">
            🔴 SHORT
        </div>
        <div class="confidence">
            GÜVEN: {confidence}%
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        f"""
        <div class="wait-box">
            ⚪ WAIT
        </div>
        <div class="confidence">
            GÜVEN: {confidence}%
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# INDICATORS
# ============================================================

st.subheader("📊 Gerçek Teknik Veriler")

i1, i2, i3, i4, i5 = st.columns(5)

with i1:
    st.metric(
        "RSI 14",
        f"{last['rsi']:.2f}"
    )

with i2:
    st.metric(
        "EMA 9",
        f"{last['ema9']:,.2f}"
    )

with i3:
    st.metric(
        "EMA 21",
        f"{last['ema21']:,.2f}"
    )

with i4:
    st.metric(
        "EMA 50",
        f"{last['ema50']:,.2f}"
    )

with i5:
    st.metric(
        "EMA 200",
        f"{last['ema200']:,.2f}"
    )


v1, v2, v3 = st.columns(3)

with v1:
    st.metric(
        "VWAP",
        f"{last['vwap']:,.2f}"
    )

with v2:
    st.metric(
        "Volume",
        f"{last['volume']:,.2f}"
    )

with v3:

    ratio = last["volume_ratio"]

    st.metric(
        "Volume Ratio",
        f"{ratio:.2f}x"
        if pd.notna(ratio)
        else "N/A"
    )


# ============================================================
# SIGNAL REASONS
# ============================================================

st.subheader("🧠 Sinyal Nedenleri")

for reason in signal_data["reasons"]:

    st.markdown(
        f"""
        <div class="reason">
            {reason}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# CANDLESTICK CHART
# ============================================================

st.subheader(
    f"📈 {symbol} — Binance Futures"
)

fig = go.Figure()

fig.add_trace(
    go.Candlestick(
        x=df["open_time"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Price"
    )
)

fig.add_trace(
    go.Scatter(
        x=df["open_time"],
        y=df["ema9"],
        name="EMA 9",
        mode="lines"
    )
)

fig.add_trace(
    go.Scatter(
        x=df["open_time"],
        y=df["ema21"],
        name="EMA 21",
        mode="lines"
    )
)

fig.add_trace(
    go.Scatter(
        x=df["open_time"],
        y=df["ema50"],
        name="EMA 50",
        mode="lines"
    )
)

fig.add_trace(
    go.Scatter(
        x=df["open_time"],
        y=df["ema200"],
        name="EMA 200",
        mode="lines"
    )
)

fig.add_trace(
    go.Scatter(
        x=df["open_time"],
        y=df["vwap"],
        name="VWAP",
        mode="lines"
    )
)

fig.update_layout(
    height=600,
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    dragmode="pan"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# WHALE SCANNER
# ============================================================

st.subheader(
    f"🐋 Whale Scanner — ≥ ${whale_threshold:,.0f}"
)

agg_result = api_get(
    f"{FUTURES_API}/fapi/v1/aggTrades",
    {
        "symbol": symbol,
        "limit": 1000
    }
)

whales = []

if not agg_result["error"]:

    for trade in agg_result["data"]:

        try:

            price = float(trade["p"])
            quantity = float(trade["q"])

            value = price * quantity

            if value >= whale_threshold:

                side = (
                    "SELL"
                    if trade["m"]
                    else "BUY"
                )

                whales.append({
                    "Yön": side,
                    "Fiyat": price,
                    "Miktar": quantity,
                    "USDT": value,
                    "UTC": datetime.fromtimestamp(
                        trade["T"] / 1000,
                        timezone.utc
                    ).strftime("%H:%M:%S")
                })

        except Exception:
            continue


if whales:

    whale_df = pd.DataFrame(
        whales
    )

    st.dataframe(
        whale_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "Son gerçek Binance işlemleri içinde "
        "belirlenen whale eşiğini geçen işlem bulunamadı."
    )


# ============================================================
# DATA STATUS
# ============================================================

now = datetime.now(
    timezone.utc
)

tr_time = now.strftime(
    "%H:%M:%S"
)

st.divider()

st.markdown(
    f"""
    <div style="text-align:center;color:#788396;">
        🟢 LIVE REAL DATA<br>
        Binance Spot: ONLINE<br>
        Binance Futures: ONLINE<br>
        Last Update: {now.strftime("%Y-%m-%d %H:%M:%S UTC")}<br>
        Türkiye Saati: {tr_time} UTC+3<br><br>
        MOCK DATA: DISABLED<br>
        DEMO DATA: DISABLED
    </div>
    """,
    unsafe_allow_html=True
)
