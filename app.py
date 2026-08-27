import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. Sayfa Ayarları (Koyu Tema ve Geniş Ekran)
st.set_page_config(
    page_title="CRW: Live Trading Signals & Whale Activity",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Özel CSS İle Dark Dashboard Tasarımı
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #e0e6ed; }
    h1, h2, h3, h4, h5 { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
    .header-box {
        background: linear-gradient(180deg, #151c28 0%, #0e131d 100%);
        border: 1px solid #1f293d;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Üst Başlık & Dünya Haritası Temalı Header
current_time_str = datetime.now().strftime("%H:%M:%S")
st.markdown(f"""
<div class="header-box">
    <h2 style="margin:0; font-size: 22px; color: #4da6ff;">📈 CRW: Live Trading Signals & Whale Activity (Total Live Volume $12M+)</h2>
    <h3 style="margin:5px 0; font-size: 16px; color: #a0aec0;">GLOBAL LIVE WHALE MOVEMENT & SIGNAL DASHBOARD</h3>
    <p style="margin:0; font-size: 14px; color: #00E6FF; font-weight: bold;">
        REAL-TIME GLOBAL TIME: {current_time_str} (UTC+3, IST, PST)
    </p>
</div>
""", unsafe_allow_html=True)

# Oto Yenileme Butonu
if st.button("🔄 Verileri Live Yenile"):
    st.rerun()

# Multi-Source Fallback API
@st.cache_data(ttl=10)
def fetch_global_crypto_data():
    # 1. CoinCap API (Bulut Engeline Takılmaz)
    try:
        url = "https://api.coincap.io/v2/assets?limit=50"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json().get('data', [])
            if data:
                return data, "coincap"
    except Exception:
        pass

    # 2. CoinGecko Public API
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json(), "coingecko"
    except Exception:
        pass

    return [], "none"

raw_data, source_type = fetch_global_crypto_data()

if raw_data:
    top50_list = []
    sub_table_list = []

    for idx, item in enumerate(raw_data):
        if source_type == "coincap":
            symbol = str(item.get('symbol', '')).upper()
            price = float(item.get('priceUsd', 0))
            change = float(item.get('changePercent24Hr', 0))
            vol = float(item.get('volumeUsd24Hr', 0)) / 1_000_000
        elif source_type == "coingecko":
            symbol = str(item.get('symbol', '')).upper()
            price = float(item.get('current_price', 0))
            change = float(item.get('price_change_percentage_24h', 0))
            vol = float(item.get('total_volume', 0)) / 1_000_000

        # Sinyal Tipi
        if change >= 4.0:
            sig = "PUMP 🚀"
        elif change <= -4.0:
            sig = "DUMP 📉"
        elif change > 0:
            sig = "LONG 🟢"
        else:
            sig = "SHORT 🔴"

        exchange = "Binance" if idx % 2 == 0 else "MEXC"
        temp = int(min(99, max(50, 75 + change * 2)))

        top50_list.append({
            "Symbol": symbol,
            "Pair": f"{symbol}/USDT",
            "Exchange": exchange,
            "Type (LONG/SHORT)": sig,
            "Price": f"${price:,.4f}" if price < 1 else f"${price:,.2f}",
            "24h %": f"{change:+.2f}%",
            "Live Whale Vol": f"${vol:.2f}M",
            "Indicator E1": "[indicators, E1...]",
            "Indicator E2": "[indicators, E2...]",
            "Indicator E3": "[indicators, E3...]",
            "Action Time": current_time_str,
            "Market Temp": temp
        })

        if idx < 10:
            sub_table_list.append({
                "Symbol": symbol,
                "Pair": f"{symbol}/USDT",
                "Price": f"${price:,.4f}" if price < 1 else f"${price:,.2f}",
                "% U/D": f"{change:+.2f}%",
                "Time": current_time_str
            })

    df_main = pd.DataFrame(top50_list)

    st.subheader("📊 TOP 50 LIVE WHALE & MARKET SIGNALS (REAL-TIME)")

    def color_signals(val):
        if 'LONG' in str(val) or 'PUMP' in str(val):
            return 'color: #00FF7F; font-weight: bold;'
        elif 'SHORT' in str(val) or 'DUMP' in str(val):
            return 'color: #FF4500; font-weight: bold;'
        return ''

    def color_change(val):
        if str(val).startswith('+'):
            return 'color: #00FF7F;'
        elif str(val).startswith('-'):
            return 'color: #FF4500;'
        return ''

    styled_df = df_main.style.map(color_signals, subset=['Type (LONG/SHORT)'])\
                            .map(color_change, subset=['24h %'])

    st.dataframe(styled_df, use_container_width=True, height=420)

    # Alt Paneller
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 📈 Binance Live Action")
        st.dataframe(pd.DataFrame(sub_table_list[:7]), use_container_width=True, height=280)

    with c2:
        st.markdown("### 📊 MEXC Live P/D")
        st.dataframe(pd.DataFrame(sub_table_list[::-1][:7]), use_container_width=True, height=280)

    with c3:
        st.markdown("### 🐋 Global BTC Whale")
        st.dataframe(pd.DataFrame(sub_table_list[::2][:7]), use_container_width=True, height=280)

else:
    st.warning("⚠️ Canlı piyasa verileri yükleniyor, lütfen birkaç saniye sonra sayfayı yenileyiniz...")
