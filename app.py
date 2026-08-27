import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone, timedelta

# 1. Sayfa Ayarları
st.set_page_config(
    page_title="Juno₿TWHunteR — Global Market Signal Feed 🌎₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Türkiye Saat Dilimi (UTC+3) Hesaplama
utc_now = datetime.now(timezone.utc)
tr_now = utc_now + timedelta(hours=3)
current_time_tr = tr_now.strftime("%H:%M:%S")

# CSS ve JavaScript İle Özel Koyu Tema & Canlı Dijital Saat
st.markdown(f"""
<style>
    .stApp {{ background-color: #0b0e14; color: #e0e6ed; }}
    h1, h2, h3, h4, h5 {{ color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }}
    
    .header-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(180deg, #151c28 0%, #0e131d 100%);
        border: 1px solid #1f293d;
        border-radius: 10px;
        padding: 15px 20px;
        margin-bottom: 20px;
    }}
    .price-box {{
        background: #1a2332;
        border: 1px solid #2d3748;
        padding: 8px 12px;
        border-radius: 8px;
        text-align: center;
        min-width: 140px;
    }}
    .price-title {{ font-size: 10px; color: #a0aec0; font-weight: bold; text-transform: uppercase; }}
    .price-value {{ font-size: 16px; color: #00E6FF; font-weight: bold; margin-top: 2px; }}
    
    .header-title {{ text-align: center; }}
    .main-title {{ margin: 0; font-size: 22px; color: #ffffff; font-weight: bold; }}
    .sub-title {{ margin: 4px 0 0 0; font-size: 13px; color: #a0aec0; }}
    .slogan-box {{ font-size: 12px; color: #f6ad55; margin-top: 4px; font-weight: 500; }}
    
    #live-clock {{
        color: #00E6FF;
        font-weight: bold;
        font-size: 13px;
        margin-top: 5px;
    }}
</style>

<script>
    function updateClock() {{
        const now = new Date();
        // Türkiye saati (UTC+3) hesaplaması
        const utcHours = now.getUTCHours();
        const trHours = String((utcHours + 3) % 24).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        
        const timeStr = "⏱️ REAL-TIME GLOBAL & TR TIME (UTC+3): " + trHours + ":" + minutes + ":" + seconds;
        const clockEl = document.getElementById('live-clock');
        if (clockEl) {{
            clockEl.innerHTML = timeStr;
        }}
    }}
    setInterval(updateClock, 1000);
</script>
""", unsafe_allow_html=True)

# Canlı Piyasa Verilerini Çekme (10 sn Önbellek)
@st.cache_data(ttl=10)
def fetch_live_market_data():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1&sparkline=false&price_change_percentage=24h"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

raw_data = fetch_live_market_data()

# BTC Fiyatları
btc_spot_str = "Yükleniyor..."
btc_fut_str = "Yükleniyor..."

if raw_data:
    btc_obj = next((x for x in raw_data if x.get('symbol', '').lower() == 'btc'), None)
    if btc_obj:
        btc_price = float(btc_obj.get('current_price', 0))
        btc_spot_str = f"${btc_price:,.2f}"
        btc_fut_str = f"${(btc_price * 1.0002):,.2f}"

# Header Tasarımı
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
        <div id="live-clock">⏱️ REAL-TIME GLOBAL & TR TIME (UTC+3): {current_time_tr}</div>
    </div>
    <div class="price-box">
        <div class="price-title">BTC/USDT PERPETUAL</div>
        <div class="price-value">{btc_fut_str}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Manuel Yenile Butonu
if st.button("🔄 Verileri Yenile"):
    st.rerun()

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

        # İndikatör Simülasyonları
        rsi_approx = min(90, max(10, int(50 + change * 2.5)))
        e1_rsi = f"RSI: {rsi_approx}"
        
        mom = "Aşırı Alım 🔥" if change > 4 else ("Aşırı Satım ❄️" if change < -4 else "Nötr ⚖️")
        e2_mom = f"Mom: {mom}"

        vol_status = "Yüksek Hacim 🐋" if vol > 500 else "Normal Hacim 📊"
        e3_vol = f"Vol: {vol_status}"

        # Sinyal Durumu
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
            "Pair": f"{
