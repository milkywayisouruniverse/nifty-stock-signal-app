import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="Indian Stock Signal App", layout="wide")

st.title("📈 Indian Stock Buy/Sell Signal Generator")
st.markdown("Analyze NIFTY50 or any Indian stock using Moving Averages + RSI")

# Input from user
ticker = st.text_input("Enter NSE stock symbol (e.g., RELIANCE.NS, INFY.NS, ^NSEI)", value="^NSEI")
start_date = st.date_input("Start Date", pd.to_datetime("2021-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("today"))

# Load stock data
df = yf.download(ticker, start=start_date, end=end_date)
if df.empty:
    st.error("⚠️ No data found. Please check the symbol.")
    st.stop()

df = df[['Close']].copy()

# Calculate indicators
df['MA20'] = df['Close'].rolling(window=20).mean()
df['MA50'] = df['Close'].rolling(window=50).mean()

# RSI
delta = df['Close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()
rs = avg_gain / avg_loss
df['RSI'] = 100 - (100 / (1 + rs))

# Signals
df['Signal'] = 'Hold'
for i in range(1, len(df)):
    if df['MA20'].iloc[i] > df['MA50'].iloc[i] and df['MA20'].iloc[i-1] <= df['MA50'].iloc[i-1]:
        df.at[df.index[i], 'Signal'] = 'Buy'
    elif df['MA20'].iloc[i] < df['MA50'].iloc[i] and df['MA20'].iloc[i-1] >= df['MA50'].iloc[i-1]:
        df.at[df.index[i], 'Signal'] = 'Sell'
df.loc[df['RSI'] < 30, 'Signal'] = 'Buy'
df.loc[df['RSI'] > 70, 'Signal'] = 'Sell'

# Plotting
fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(df['Close'], label='Close Price', color='blue')
ax.plot(df['MA20'], label='MA20', color='green', alpha=0.6)
ax.plot(df['MA50'], label='MA50', color='orange', alpha=0.6)

buy_signals = df[df['Signal'] == 'Buy']
sell_signals = df[df['Signal'] == 'Sell']
ax.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='lime', label='Buy', s=100)
ax.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', label='Sell', s=100)

ax.set_title(f"{ticker} – Buy/Sell Signal Chart")
ax.set_xlabel("Date")
ax.set_ylabel("Price (INR)")
ax.legend()
ax.grid(True)

st.pyplot(fig)

# Latest signal
latest = df.iloc[-1]
st.subheader("📍 Latest Signal")
st.markdown(f"**Signal:** `{latest['Signal']}`  
**Date:** `{df.index[-1].date()}`  
**Close Price:** ₹{round(latest['Close'], 2)}")

# Show table
st.markdown("### 📊 Recent Data")
st.dataframe(df.tail(10).style.highlight_max(axis=0, color='lightgreen'))
