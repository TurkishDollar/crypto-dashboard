import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

# 1. Sayfa Ayarları (Koyu Tema ve Geniş Ekran)
st.set_page_config(
    page_title="CRW: Live Trading Signals & Whale Activity",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Özel CSS İle Görseldeki Dark Dashboard Tasarımı
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
    .badge-long { background-color: rgba(0, 255, 127, 0.15); color: #00FF7F; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    .badge-short { background-color: rgba(255, 69, 0, 0.15); color: #FF4500; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    .badge-pump { background-color: rgba(0, 230, 255, 0.15); color: #00E6FF; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    .badge-dump { background-color: rgba(255, 0, 100, 0.15); color: #FF0064; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
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

# Oto Yenileme Butonu ve Filtreler
col_btn, col_filter, col_space = st.columns([2, 3, 5])
with col_btn:
    if st.button("🔄 Verileri Live Yenile"):
        st.rerun()

# Live Veri Çekme Fonksiyonu
@st.cache_data(ttl=5)
def fetch_binance_futures():
    try:
        url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    # Backup Spot API
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        return []

raw_data = fetch_binance_futures()

if raw_data and isinstance(raw_data, list):
    usdt_data = [x for x in raw_data if isinstance(x, dict) and x.get('symbol', '').endswith('USDT')]
    sorted_data = sorted(usdt_data, key=lambda x: abs(float(x.get('priceChangePercent', 0))), reverse=True)
    
    top50_list = []
    binance_action = []
    whale_btc = []
    
    for item in sorted_data[:50]:
        symbol = item.get('symbol', '').replace('USDT', '')
        price = float(item.get('lastPrice', 0))
        change = float(item.get('priceChangePercent', 0))
        vol = float(item.get('quoteVolume', 0)) / 1_000_000
        
        # Sinyal Tipi
        if change >= 4.0:
            sig = "PUMP 🚀"
        elif change <= -4.0:
            sig = "DUMP 📉"
        elif change > 0:
            sig = "LONG 🟢"
        else:
            sig = "SHORT 🔴"

        # Borsa Seçimi (Görseldeki Çeşitlilik)
        exchange = "Binance" if len(symbol) % 2 == 0 else "MEXC"
        
        # Temp hesaplama
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

    # Sub Tables Data Generation
    for item in sorted_data[:8]:
        sym = item.get('symbol', '').replace('USDT', '')
        prc = float(item.get('lastPrice', 0))
        chg = float(item.get('priceChangePercent', 0))
        
        binance_action.append({
            "Symbol": sym,
            "Pair": f"{sym}/USDT",
            "Price": f"{prc:.4f}" if prc < 1 else f"{prc:.2f}",
            "% U/D": f"{chg:+.2f}%",
            "Time": current_time_str
        })

    df_main = pd.DataFrame(top50_list)

    st.subheader("📊 TOP 50 LIVE WHALE & MARKET SIGNALS (REAL-TIME)")
    
    # Renkli Sütun Stili
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

    # ------------------ ALT PANELLER (3 SÜTUNLU YAPI) ------------------
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 📈 Binance Live Action")
        df_act = pd.DataFrame(binance_action)
        st.dataframe(df_act, use_container_width=True, height=280)

    with c2:
        st.markdown("### 📊 MEXC Live P/D")
        df_mexc = pd.DataFrame(binance_action[::-1]) # Örnek ters sıralama
        st.dataframe(df_mexc, use_container_width=True, height=280)

    with c3:
        st.markdown("### 🐋 Global BTC Whale")
        df_whale = pd.DataFrame(binance_action[::2])
        st.dataframe(df_whale, use_container_width=True, height=280)

else:
    st.error("Veri bağlantısı kuruluyor, lütfen sayfayı yenileyiniz...")
