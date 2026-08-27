import streamlit as st
import pandas as pd

# Sayfa Ayarları (Koyu Tema ve Geniş Ekran)
st.set_page_config(page_title="Crypto Whale Tracker", layout="wide")

st.title("🐋 Canlı Balina & Piyasa Takip Paneli")

# 1. Görseldeki Sinyal Tablosu
st.subheader("📊 Top 50 Live Whale & Market Signals")
data_signals = {
    "Symbol": ["BTC", "ETH", "ETH", "PEPE", "SOL", "ARB"],
    "Pair": ["BTC/USDT", "ETH/USDT", "ETP/USDT", "PEPE/USDT", "SOL/USDT", "ARB/USDT"],
    "Exchange": ["Binance", "Binance", "Binance", "MEXC", "MEXC", "MEXC"],
    "Type": ["LONG 🟢", "SHORT 🔴", "LONG 🟢", "PUMP 🚀", "SHORT 🔴", "DUMP 📉"],
    "Price": ["$12,500", "$1,450", "$1,250", "$3.9620", "$0.2475", "$0.7300"],
    "Whale Vol": ["$5.2M", "$2.3M", "$4.5M", "$2.4M", "$1.6M", "$0.73M"]
}
st.dataframe(pd.DataFrame(data_signals), use_container_width=True)

# 3. Görseldeki Coinglass Likidite Seviyeleri
st.subheader("🎯 Coinglass BTC Balina Likidite Seviyeleri")
col1, col2 = st.columns(2)

with col1:
    st.error("🔴 Satış / Direnç Bölgesi (Short Likiditesi)")
    st.write("• **$68.000:** $21.67M")
    st.write("• **$66.000 - $66.500:** ~$13.3M Clustered")

with col2:
    st.success("🟢 Alım / Destek Bölgesi (Long Likiditesi)")
    st.write("• **$61.300:** $78.53M (En Yüksek)")
    st.write("• **$52.050:** $42.35M")
    st.write("• **$50.000:** $23.45M")
