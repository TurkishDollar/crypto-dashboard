import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Live Whale & Market Tracker", layout="wide")

st.title("🐋 Canlı Balina & Piyasa Takip Paneli (Live Market Data)")
st.caption(f"Son Güncelleme (UTC+3): {datetime.now().strftime('%H:%M:%S')}")

if st.button("🔄 Verileri Şimdi Yenile"):
    st.rerun()

@st.cache_data(ttl=10)
def get_market_data():
    # 1. Öncelik: Binance Spot Public API
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        res = requests.get(url, timeout=5)
        data = res.json()
        if isinstance(data, list):
            usdt_pairs = [x for x in data if isinstance(x, dict) and x.get('symbol', '').endswith('USDT')]
            return usdt_pairs, "Binance Spot"
    except Exception:
        pass
        
    # 2. Öncelik: CoinCap API (Yedek)
    try:
        url = "https://api.coincap.io/v2/assets?limit=50"
        res = requests.get(url, timeout=5)
        data = res.json()
        if isinstance(data, dict) and 'data' in data:
            return data['data'], "CoinCap"
    except Exception:
        pass

    return [], "None"

raw_data, source = get_market_data()

if raw_data:
    processed_signals = []
    
    if source == "Binance Spot":
        # Binance Veri İşleme
        sorted_data = sorted(raw_data, key=lambda x: abs(float(x.get('priceChangePercent', 0))), reverse=True)
        for item in sorted_data[:50]:
            symbol = item.get('symbol', '')
            price = float(item.get('lastPrice', 0))
            price_change = float(item.get('priceChangePercent', 0))
            quote_volume = float(item.get('quoteVolume', 0)) / 1_000_000
            
            if price_change >= 5.0:
                signal_type = "PUMP 🚀"
            elif price_change <= -5.0:
                signal_type = "DUMP 📉"
            elif price_change > 0:
                signal_type = "LONG 🟢"
            else:
                signal_type = "SHORT 🔴"
                
            processed_signals.append({
                "Symbol": symbol.replace("USDT", ""),
                "Pair": f"{symbol[:6]}/USDT",
                "Exchange": "Binance Live",
                "Type (LONG/SHORT)": signal_type,
                "Price": f"${price:,.4f}" if price < 1 else f"${price:,.2f}",
                "24h %": f"{price_change:+.2f}%",
                "Live Whale Vol": f"${quote_volume:.2f}M",
                "Market Temp": int(min(100, max(10, (price_change + 10) * 5)))
            })

    elif source == "CoinCap":
        # CoinCap Yedek Veri İşleme
        for item in raw_data:
            symbol = item.get('symbol', '')
            price = float(item.get('priceUsd', 0))
            price_change = float(item.get('changePercent24Hr', 0))
            volume = float(item.get('volumeUsd24Hr', 0)) / 1_000_000
            
            if price_change >= 5.0:
                signal_type = "PUMP 🚀"
            elif price_change <= -5.0:
                signal_type = "DUMP 📉"
            elif price_change > 0:
                signal_type = "LONG 🟢"
            else:
                signal_type = "SHORT 🔴"

            processed_signals.append({
                "Symbol": symbol,
                "Pair": f"{symbol}/USDT",
                "Exchange": "Global Aggregator",
                "Type (LONG/SHORT)": signal_type,
                "Price": f"${price:,.4f}" if price < 1 else f"${price:,.2f}",
                "24h %": f"{price_change:+.2f}%",
                "Live Whale Vol": f"${volume:.2f}M",
                "Market Temp": int(min(100, max(10, (price_change + 10) * 5)))
            })

    if processed_signals:
        df = pd.DataFrame(processed_signals)
        
        st.subheader("📈 TOP 50 LIVE WHALE & MARKET SIGNALS (REAL-TIME)")
        
        def highlight_type(val):
            if 'LONG' in val or 'PUMP' in val:
                return 'color: #00FF7F; font-weight: bold;'
            elif 'SHORT' in val or 'DUMP' in val:
                return 'color: #FF4500; font-weight: bold;'
            return ''

        st.dataframe(
            df.style.map(highlight_type, subset=['Type (LONG/SHORT)']),
            use_container_width=True,
            height=600
        )
else:
    st.warning("⚠️ Canlı piyasa verileri şu anda alınamıyor, lütfen birkaç saniye sonra 'Verileri Şimdi Yenile' butonuna basınız.")

st.divider()

st.subheader("🎯 Coinglass BTC Balina Likidite Haritası")
col1, col2 = st.columns(2)

with col1:
    st.error("🔴 Satış / Direnç Bölgesi (Short Likiditesi)")
    st.markdown("""
    * **$68,000:** $21.67M
    * **$66,522 - $66,033:** ~$13.31M Kümelenmiş Emir
    * **$64,388 - $64,288:** ~$14.63M Balina Satış Duvarı
    """)

with col2:
    st.success("🟢 Alım / Destek Bölgesi (Long Likiditesi)")
    st.markdown("""
    * **$61,300:** $78.53M *(En Yüksek Destek)*
    * **$55,000:** $30.93M
    * **$52,050:** $42.35M
    * **$48,000:** $27.36M
    """)
