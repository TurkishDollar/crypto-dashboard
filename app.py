import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Live Whale & Market Tracker", layout="wide")

st.title("🐋 Canlı Balina & Piyasa Takip Paneli (Binance Live)")
st.caption(f"Son Güncelleme (UTC+3): {datetime.now().strftime('%H:%M:%S')}")

if st.button("🔄 Verileri Şimdi Yenile"):
    st.rerun()

@st.cache_data(ttl=5)
def get_binance_futures_data():
    try:
        url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
        response = requests.get(url, timeout=5)
        return [item for item in response.json() if item['symbol'].endswith('USDT')]
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
        return []

raw_data = get_binance_futures_data()

if raw_data:
    processed_signals = []
    
    sorted_data = sorted(raw_data, key=lambda x: abs(float(x['priceChangePercent'])), reverse=True)
    
    for item in sorted_data[:50]:
        symbol = item['symbol']
        price = float(item['lastPrice'])
        price_change = float(item['priceChangePercent'])
        quote_volume = float(item['quoteVolume']) / 1_000_000
        
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
            "Exchange": "Binance Futures",
            "Type (LONG/SHORT)": signal_type,
            "Price": f"${price:,.4f}" if price < 1 else f"${price:,.2f}",
            "24h %": f"{price_change:+.2f}%",
            "Live Whale Vol": f"${quote_volume:.2f}M",
            "Market Temp": int(min(100, max(10, (price_change + 10) * 5)))
        })
        
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
