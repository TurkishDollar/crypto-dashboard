import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime, timezone

# ============================================================
# JUNO₿TWHUNTER — REAL MARKET SIGNAL ENGINE
# REAL BINANCE DATA ONLY — NO MOCK / NO DEMO DATA
# ============================================================

st.set_page_config(
    page_title="Juno₿TWHunteR — Real Market Intelligence",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CONFIG
# ============================================================

SPOT_API = "https://api.binance.com"
FUTURES_API = "https://fapi.binance.com"

REFRESH_SECONDS = 5
KLINE_LIMIT = 250

# Büyük işlem eşiği
WHALE_USDT_THRESHOLD = 100000

# ============================================================
# STYLE
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

.main-title {
    text-align: center;
    font-size: 28px;
    font-weight: 900;
    color: #ffffff;
    margin-bottom: 2px;
}

.sub-title {
    text-align: center;
    color: #8f9bad;
    font-size: 13px;
    margin-bottom: 20px;
}

.market-card {
    background: linear-gradient(145deg,#121925,#0d131d);
    border: 1px solid #202b3c;
    border-radius: 14px;
    padding: 16px;
    text-align: center;
}

.market-label {
    color: #8793a6;
    font-size: 11px;
    font-weight: 700;
}

.market-value {
    color: #ffffff;
    font-size: 21px;
    font-weight: 900;
    margin-top: 5px;
}

.signal-long {
    background: rgba(0,220,120,0.12);
    border: 2px solid #00e676;
    color: #00ff88;
    border-radius: 16px;
    padding: 22px;
    text-align: center;
    font-size: 38px;
    font-weight: 1000;
    box-shadow: 0 0 25px rgba(0,230,118,0.18);
}

.signal-short {
    background: rgba(255,45,70,0.12);
    border: 2px solid #ff304f;
    color: #ff304f;
    border-radius: 16px;
    padding: 22px;
    text-align: center;
    font-size: 38px;
    font-weight: 1000;
    box-shadow: 0 0 25px rgba(255,48,79,0.18);
}

.signal-wait {
    background: rgba(150,160,175,0.10);
    border: 2px solid #778196;
    color: #b8c0cc;
    border-radius: 16px;
    padding: 22px;
    text-align: center;
    font-size: 38px;
    font-weight: 1000;
}

.confidence {
    text-align: center;
    font-size: 22px;
    font-weight: 800;
    margin-top: 10px;
}

.reason {
    background: #101722;
    border-left: 4px solid #344155;
    padding: 10px 14px;
    border-radius: 6px;
    margin-bottom: 7px;
}

.real-data {
    color: #00e676;
    font-weight: 800;
}

.warning-data {
    color: #ffb300;
    font-weight: 800;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# HTTP SESSION
# ============================================================

session = requests.Session()

session.headers.update({
    "User-Agent": "JunoBTWHunteR/1.0"
})


# ============================================================
# GENERIC REQUEST
# ============================================================

def api_get(url, params=None):

    try:

        response = session.get(
            url,
            params=params,
            timeout=8
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        return None


# ============================================================
# SPOT PRICE
# ============================================================

def get_spot_price(symbol):

    data = api_get(
        f"{SPOT_API}/api/v3/ticker/price",
        {"symbol": symbol}
    )

    if not data:
        return None

    try:
        return float(data["price"])
    except:
        return None


# ============================================================
# FUTURES PRICE
# ============================================================

def get_futures_price(symbol):

    data = api_get(
        f"{FUTURES_API}/fapi/v1/ticker/price",
        {"symbol": symbol}
    )

    if not data:
        return None

    try:
        return float(data["price"])
    except:
        return None


# ============================================================
# 24H FUTURES STATISTICS
# ============================================================

def get_futures_24h(symbol):

    data = api_get(
        f"{FUTURES_API}/fapi/v1/ticker/24hr",
        {"symbol": symbol}
    )

    if not data:
        return None

    try:

        return {
            "price_change": float(data["priceChange"]),
            "price_change_percent": float(data["priceChangePercent"]),
            "volume": float(data["volume"]),
            "quote_volume": float(data["quoteVolume"]),
            "high": float(data["highPrice"]),
            "low": float(data["lowPrice"])
        }

    except:
        return None


# ============================================================
# KLINES
# ============================================================

def get_futures_klines(symbol, interval):

    data = api_get(
        f"{FUTURES_API}/fapi/v1/klines",
        {
            "symbol": symbol,
            "interval": interval,
            "limit": KLINE_LIMIT
        }
    )

    if not data:
        return None

    try:

        df = pd.DataFrame(
            data,
            columns=[
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
        )

        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "quote_volume",
            "taker_buy_base",
            "taker_buy_quote"
        ]

        for col in numeric_columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        df["open_time"] = pd.to_datetime(
            df["open_time"],
            unit="ms"
        )

        return df

    except:
        return None


# ============================================================
# RSI
# ============================================================

def calculate_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)

    rsi = 100 - (
        100 / (1 + rs)
    )

    return rsi.fillna(50)


# ============================================================
# VWAP
# ============================================================

def calculate_vwap(df):

    typical_price = (
        df["high"]
        + df["low"]
        + df["close"]
    ) / 3

    cumulative_volume = df["volume"].cumsum()

    cumulative_value = (
        typical_price * df["volume"]
    ).cumsum()

    return cumulative_value / cumulative_volume


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

    df["vwap"] = calculate_vwap(df)

    df["volume_ma20"] = df["volume"].rolling(
        20
    ).mean()

    df["volume_ratio"] = (
        df["volume"]
        / df["volume_ma20"]
    )

    return df


# ============================================================
# SIGNAL ENGINE
# ============================================================

def generate_signal(df):

    if df is None or len(df) < 200:
        return {
            "signal": "WAIT",
            "confidence": 0,
            "reasons": [
                "Yeterli gerçek mum verisi bekleniyor."
            ]
        }

    last = df.iloc[-1]

    score = 0
    reasons = []

    # --------------------------------------------------------
    # EMA
    # --------------------------------------------------------

    if last["ema9"] > last["ema21"]:

        score += 2

        reasons.append(
            "EMA 9 > EMA 21 → kısa vadeli bullish yapı"
        )

    else:

        score -= 2

        reasons.append(
            "EMA 9 < EMA 21 → kısa vadeli bearish yapı"
        )

    # --------------------------------------------------------
    # EMA 50
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # EMA 200
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    rsi = float(last["rsi"])

    if 50 < rsi < 70:

        score += 1

        reasons.append(
            f"RSI {rsi:.1f} → bullish momentum"
        )

    elif 30 < rsi < 50:

        score -= 1

        reasons.append(
            f"RSI {rsi:.1f} → bearish momentum"
        )

    elif rsi >= 70:

        reasons.append(
            f"RSI {rsi:.1f} → aşırı alım bölgesi"
        )

    elif rsi <= 30:

        reasons.append(
            f"RSI {rsi:.1f} → aşırı satım bölgesi"
        )

    # --------------------------------------------------------
    # VWAP
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    volume_ratio = last["volume_ratio"]

    if pd.notna(volume_ratio):

        if volume_ratio >= 1.5:

            if score > 0:
                score += 1

            elif score < 0:
                score -= 1

            reasons.append(
                f"Hacim güçlü → {volume_ratio:.2f}x ortalama"
            )

        else:

            reasons.append(
                f"Hacim normal → {volume_ratio:.2f}x ortalama"
            )

    # --------------------------------------------------------
    # FINAL SIGNAL
    # --------------------------------------------------------

    max_score = 8

    confidence = min(
        99,
        int(
            50
            + abs(score) / max_score * 49
        )
    )

    # Güçlü fikir yoksa WAIT
    if abs(score) < 3:

        signal = "WAIT"

        confidence = max(
            50,
            100 - confidence
        )

    elif score >= 3:

        signal = "LONG"

    else:

        signal = "SHORT"

    return {
        "signal": signal,
        "confidence": confidence,
        "score": score,
        "rsi": rsi,
        "reasons": reasons
    }


# ============================================================
# WHALE SCANNER
# ============================================================

def get_whale_trades(symbol):

    data = api_get(
        f"{FUTURES_API}/fapi/v1/aggTrades",
        {
            "symbol": symbol,
            "limit": 100
        }
    )

    if not data:
        return []

    whales = []

    for trade in data:

        try:

            price = float(trade["p"])
            quantity = float(trade["q"])

            usdt_value = price * quantity

            if usdt_value >= WHALE_USDT_THRESHOLD:

                # m = buyer was market maker
                # m=True → seller aggressor
                # m=False → buyer aggressor

                side = (
                    "SELL"
                    if trade["m"]
                    else "BUY"
                )

                whales.append({
                    "side": side,
                    "price": price,
                    "quantity": quantity,
                    "usdt": usdt_value,
                    "time": datetime.fromtimestamp(
                        trade["T"] / 1000,
                        timezone.utc
                    ).strftime("%H:%M:%S")
                })

        except:
            continue

    return whales


# ============================================================
# SYMBOLS
# ============================================================

@st.cache_data(ttl=300)
def get_usdt_symbols():

    data = api_get(
        f"{FUTURES_API}/fapi/v1/exchangeInfo"
    )

    if not data:
        return []

    symbols = []

    try:

        for item in data["symbols"]:

            if (
                item.get("quoteAsset") == "USDT"
                and item.get("status") == "TRADING"
                and item.get("contractType") == "PERPETUAL"
            ):

                symbols.append(
                    item["symbol"]
                )

    except:
        pass

    return sorted(symbols)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">Juno₿TWHunteR 🌎₿</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'REAL-TIME BINANCE MARKET INTELLIGENCE — NO MOCK DATA'
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
        value="BTCUSDT"
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
        "🐋 Whale Threshold (USDT)",
        min_value=10000,
        max_value=10000000,
        value=WHALE_USDT_THRESHOLD,
        step=10000
    )

    if st.button("🔄 Şimdi Yenile"):
        st.rerun()


# ============================================================
# REAL MARKET DATA
# ============================================================

spot_price = get_spot_price(symbol)

futures_price = get_futures_price(symbol)

stats = get_futures_24h(symbol)

df = get_futures_klines(
    symbol,
    timeframe
)

# ============================================================
# DATA VALIDATION
# ============================================================

if futures_price is None or df is None:

    st.error(
        "❌ Gerçek Binance verisi alınamadı. "
        "Sistem sahte veri göstermiyor."
    )

    st.stop()


df = calculate_indicators(df)

signal_data = generate_signal(df)

# ============================================================
# MARKET HEADER
# ============================================================

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.markdown(
        f"""
        <div class="market-card">
            <div class="market-label">
                BINANCE SPOT
            </div>
            <div class="market-value">
                ${spot_price:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:

    st.markdown(
        f"""
        <div class="market-card">
            <div class="market-label">
                BINANCE USDT-M PERPETUAL
            </div>
            <div class="market-value">
                ${futures_price:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:

    change = (
        stats["price_change_percent"]
        if stats
        else 0
    )

    change_text = (
        f"{change:+.2f}%"
    )

    st.markdown(
        f"""
        <div class="market-card">
            <div class="market-label">
                24H CHANGE
            </div>
            <div class="market-value">
                {change_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:

    st.markdown(
        f"""
        <div class="market-card">
            <div class="market-label">
                TIMEFRAME
            </div>
            <div class="market-value">
                {timeframe.upper()}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# ============================================================
# MAIN SIGNAL
# ============================================================

signal = signal_data["signal"]

confidence = signal_data["confidence"]

if signal == "LONG":

    st.markdown(
        f"""
        <div class="signal-long">
            🟢 LONG
        </div>
        <div class="confidence">
            Güven: {confidence}%
        </div>
        """,
        unsafe_allow_html=True
    )

elif signal == "SHORT":

    st.markdown(
        f"""
        <div class="signal-short">
            🔴 SHORT
        </div>
        <div class="confidence">
            Güven: {confidence}%
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        f"""
        <div class="signal-wait">
            ⚪ WAIT
        </div>
        <div class="confidence">
            Güven: {confidence}%
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# INDICATOR VALUES
# ============================================================

last = df.iloc[-1]

st.write("")

st.subheader("📊 Gerçek Teknik Veriler")

i1, i2, i3, i4, i5 = st.columns(5)

with i1:
    st.metric(
        "RSI",
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


# ============================================================
# VWAP
# ============================================================

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

    if pd.notna(ratio):

        st.metric(
            "Volume Ratio",
            f"{ratio:.2f}x"
        )

    else:

        st.metric(
            "Volume Ratio",
            "N/A"
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
# PRICE CHART
# ============================================================

st.subheader(
    f"📈 {symbol} — {timeframe.upper()} Gerçek Binance Futures Grafiği"
)

chart_df = df[
    [
        "open_time",
        "open",
        "high",
        "low",
        "close"
    ]
].copy()

chart_df = chart_df.set_index(
    "open_time"
)

st.line_chart(
    chart_df["close"],
    height=400
)


# ============================================================
# WHALE SCANNER
# ============================================================

st.subheader(
    f"🐋 Whale Scanner — Son Büyük İşlemler "
    f"(≥ ${whale_threshold:,.0f})"
)

# Kullanıcının sidebar threshold değerini fonksiyona uyguluyoruz
WHALE_USDT_THRESHOLD = whale_threshold

whales = get_whale_trades(symbol)

if whales:

    whale_df = pd.DataFrame(
        whales
    )

    whale_df["usdt"] = whale_df["usdt"].map(
        lambda x: f"${x:,.0f}"
    )

    whale_df["price"] = whale_df["price"].map(
        lambda x: f"${x:,.2f}"
    )

    whale_df["quantity"] = whale_df["quantity"].map(
        lambda x: f"{x:,.6f}"
    )

    whale_df.columns = [
        "Yön",
        "Fiyat",
        "Miktar",
        "İşlem Değeri",
        "UTC Saat"
    ]

    st.dataframe(
        whale_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "Son gerçek işlemler içinde belirlenen whale "
        "eşiğini geçen işlem bulunamadı."
    )


# ============================================================
# DATA STATUS
# ============================================================

utc_time = datetime.now(
    timezone.utc
).strftime("%Y-%m-%d %H:%M:%S UTC")

st.markdown(
    f"""
    <hr>
    <div style="text-align:center;color:#758096;font-size:12px;">
        🟢 LIVE REAL DATA |
        Binance USDT-M |
        Last update: {utc_time}
        <br>
        ❌ Mock Data Disabled |
        ❌ Demo Data Disabled
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# AUTO REFRESH
# ============================================================

time.sleep(
    REFRESH_SECONDS
)

st.rerun()
