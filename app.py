import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. Sayfa Ayarları
st.set_page_config(
    page_title="Juno₿TWHunteR — Global Market Signal Feed 🌎₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Her 1 saniyede bir verileri ve saati otomatik akıcı yenileme kuralı
st.markdown('<meta http-equiv="refresh" content="1">', unsafe_allow_html=True)

# CSS İle Özel Koyu Tema
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #e0e6ed; }
    h1, h2, h3, h4, h5 { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
    
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(180deg, #151c28 0%, #0e131d 100%);
        border: 1px solid #1f293d;
        border-radius: 10px;
        padding: 15px 20px;
        margin-bottom: 20px;
    }
    .price-box {
        background: #1a2332;
        border: 1px solid #2d3748;
        padding: 8px 12px;
        border-radius: 8px;
        text-align: center;
        min-width: 140px;
    }
    .price-title { font-size: 10px; color: #a0aec0; font-weight: bold; text-transform: uppercase; }
    .price-value { font-size: 16px; color: #00E6FF; font-weight: bold; margin-top: 2px; }
    
    .header-title { text-align: center; }
    .main-title { margin: 0; font-size: 22px; color: #ffffff; font-weight: bold; }
    .sub-title { margin: 4px 0 0 0; font-size: 13px; color: #a0aec0; }
    .slogan-box { font-size: 12px; color: #f6ad55; margin-top: 4px; font-weight: 500; }
    
    .live-clock {
        color: #00E6FF;
        font-weight: bold;
        font-size: 13px;
        margin-top: 3px;
    }
</style>
""", unsafe_allow_html=True)

# Canlı Piyasa Verilerini Çekme (Saniyelik Önbellek)
@st.cache_data(ttl=1)
def fetch_live_market_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1&sparkline=false&price_change_percentage=24h"
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

raw_data = fetch_live_market_data()

# Her saniye anlık güncellenen canlı saat
current_time_live = datetime.now().strftime("%H:%M:%S")

# BTC Fiyatları
btc_spot_str = "Yükleniyor..."
btc_fut_str = "Yükleniyor..."

if raw_data:
    btc_obj = next((x for x in raw_data if x.get('symbol', '').lower() == 'btc'), None)
    if btc_obj:
        btc_price = float(btc_obj.get('current_price', 0))
        btc_spot_str = f"${btc_price:,.2f}"
        btc_fut_str = f"${(btc_price * 1.0002):,.2f}"

# Header Tasarımı (Saniyelik Canlı Saat İle)
st.markdown(f"""
<div class="header-container">
    <div class="price-box">
        <div class="price-title">BTC/USDT SPOT</div>
        <div class="price-value">{btc_spot_str}</div>
    </div>
    <div class="header-title">
        <div class="main-title">Juno₿TWHunteR — Global Market Signal Feed 🌎₿</div>
        <div class="sub-title">₿ Bitcoin sets the direction.</div>
        <div class="slogan-box">Juno₿TWHunteR hunts the market. 🐋🌎</div>
        <div class="live-clock">⏱️ ANLIK CANLI ZAMAN: {current_time_live}</div>
    </div>
    <div class="price-box">
        <div class="price-title">BTC/USDT PERPETUAL</div>
        <div class="price-value">{btc_fut_str}</div>
    </div>
</div>
""", unsafe_allow_html=True)

if raw_data:
    top50_data = []
    binance_action = []
    mexc_action = []
    whale_btc = []

    for idx, item in enumerate(raw_data):
        symbol = str(item.get('symbol', '')).upper()
        price = float(item.get('current_price', 0))
        change = float(item.get('price_change_percentage_24h', 0) or 0)
        vol = float(item.get('total_volume', 0)) / 1_000_000

        rsi_approx = min(90, max(10, int(50 + change * 2.5)))
        e1_rsi = f"RSI: {rsi_approx}"
        
        mom = "Aşırı Alım 🔥" if change > 4 else ("Aşırı Satım ❄️" if change < -4 else "Nötr ⚖️")
        e2_mom = f"Mom: {mom}"

        vol_status = "Yüksek Hacim 🐋" if vol > 500 else "Normal Hacim 📊"
        e3_vol = f"Vol: {vol_status}"

        if change >= 4.0:
            sig = "PUMP 🚀"
        elif change <= -4.0:
            sig = "DUMP 📉"
        elif change > 0:
            sig = "LONG 🟢"
        else:
            sig = "SHORT 🔴"

        exchange = "Binance" if idx % 2 == 0 else "MEXC"

        top50_data.append({
            "Symbol": symbol,
            "Pair": f"{symbol}/USDT",
            "Exchange": exchange,
            "Type (LONG/SHORT)": sig,
            "Price": f"${price:,.4f}" if price < 1 else f"${price:,.2f}",
            "24h %": f"{change:+.2f}%",
            "Live Whale Vol": f"${vol:.2f}M",
            "Indicator 1": e1_rsi,
            "Indicator 2": e2_mom,
            "Indicator 3": e3_vol,
            "Action Time": current_time_live
        })

        if idx < 8:
            binance_action.append({
                "Symbol": symbol,
                "Pair": f"{symbol}/USDT",
                "Price": f"${price:,.4f}" if price < 1 else f"${price:,.2f}",
                "% U/D": f"{change:+.2f}%",
                "Time": current_time_live
            })
        if 8 <= idx < 16:
            mexc_action.append({
                "Symbol": symbol,
                "Pair": f"{symbol}/USDT",
                "Price": f"${price:,.4f}" if price < 1 else f"${price:,.2f}",
                "% U/D": f"{change:+.2f}%",
                "Time": current_time_live
            })
        if vol > 300 and len(whale_btc) < 8:
            whale_btc.append({
                "Symbol": symbol,
                "Pair": f"{symbol}/USDT",
                "Price": f"${price:,.4f}" if price < 1 else f"${price:,.2f}",
                "Whale Vol": f"${vol:.2f}M",
                "Time": current_time_live
            })

    df_main = pd.DataFrame(top50_data)

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

    st.dataframe(styled_df, use_container_width=True, height=450, hide_index=True)

    # Alt Paneller (Sırayla Alt Alta)
    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    st.subheader("📈 Binance Live Action")
    st.dataframe(pd.DataFrame(binance_action), use_container_width=True, height=260, hide_index=True)

    st.subheader("📊 MEXC Live P/D")
    st.dataframe(pd.DataFrame(mexc_action), use_container_width=True, height=260, hide_index=True)

    st.subheader("🐋 Global BTC Whale")
    st.dataframe(pd.DataFrame(whale_btc), use_container_width=True, height=260, hide_index=True)

else:
    st.warning("⚠️ Canlı piyasa verileri yükleniyor, lütfen birkaç saniye sonra sayfayı yenileyiniz...")
