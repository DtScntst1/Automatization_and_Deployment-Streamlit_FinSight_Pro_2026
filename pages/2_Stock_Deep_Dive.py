import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_fetcher import get_stock_data, get_stock_info, format_large_number
from utils.technical_indicators import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_sma, calculate_ema, generate_signals
)

st.set_page_config(page_title="Stock Deep Dive | FinSight Pro", page_icon="🔍", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header {visibility: hidden;}
.stApp { background: linear-gradient(135deg, #0A0E1A 0%, #0D1529 50%, #0A0E1A 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0D1529 0%, #111827 100%); border-right: 1px solid rgba(0,212,255,0.15); }
[data-testid="stMetric"] { background: rgba(255,255,255,0.03); border: 1px solid rgba(0,212,255,0.15); border-radius: 12px; padding: 1rem; transition: transform 0.2s; }
[data-testid="stMetric"]:hover { transform: translateY(-2px); }
.stButton > button { background: linear-gradient(135deg, #00D4FF, #0080FF) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
.signal-buy { background: rgba(72,187,120,0.15); border: 1px solid rgba(72,187,120,0.4); border-radius: 10px; padding: 1rem; }
.signal-sell { background: rgba(245,101,101,0.15); border: 1px solid rgba(245,101,101,0.4); border-radius: 10px; padding: 1rem; }
.signal-neutral { background: rgba(246,173,85,0.15); border: 1px solid rgba(246,173,85,0.4); border-radius: 10px; padding: 1rem; }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #0A0E1A; } ::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="padding: 1.5rem 0; border-bottom: 1px solid rgba(0,212,255,0.1); margin-bottom: 2rem;">
    <h1 style="margin:0; font-size:2.2rem; font-weight:800;
        background: linear-gradient(135deg,#FFFFFF,#00D4FF);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
        🔍 Stock Deep Dive
    </h1>
    <p style="color:#64748B; margin:0.3rem 0 0; font-size:0.95rem;">
        Advanced technical analysis with buy/sell signals
    </p>
</div>
""", unsafe_allow_html=True)

# ── Controls ───────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
with col1:
    ticker = st.text_input("Stock Ticker", value="AAPL", placeholder="e.g. AAPL, TSLA, MSFT").upper().strip()
with col2:
    period = st.selectbox("Time Period", ["1mo","3mo","6mo","1y","2y","5y"], index=3)
with col3:
    interval = st.selectbox("Interval", ["1d","1wk"], index=0)
with col4:
    st.markdown("<br>", unsafe_allow_html=True)
    analyze = st.button("Analyze 🚀")

if not ticker:
    st.info("Enter a stock ticker to begin analysis.")
    st.stop()

# ── Fetch Data ─────────────────────────────────────────────────────────────────
with st.spinner(f"Loading data for {ticker}..."):
    df = get_stock_data(ticker, period=period, interval=interval)
    info = get_stock_info(ticker)

if df.empty:
    st.error(f"No data found for '{ticker}'. Please check the ticker symbol.")
    st.stop()

# ── Company Header ─────────────────────────────────────────────────────────────
company_name = info.get("shortName", ticker)
sector = info.get("sector", "N/A")
industry = info.get("industry", "N/A")
website = info.get("website", "#")
current_price = df["Close"].iloc[-1]
prev_price = df["Close"].iloc[-2] if len(df) > 1 else current_price
price_change = current_price - prev_price
price_pct = (price_change / prev_price) * 100

arrow = "▲" if price_change >= 0 else "▼"
color = "#48BB78" if price_change >= 0 else "#F56565"

st.markdown(f"""
<div style="
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
">
    <div>
        <div style="font-size: 1.8rem; font-weight: 800; color: #E8EAF6;">{company_name}</div>
        <div style="font-size: 0.9rem; color: #64748B; margin-top: 0.3rem;">
            <span style="background: rgba(0,212,255,0.1); border-radius: 4px; padding: 2px 8px; margin-right: 8px;">{ticker}</span>
            {sector} • {industry}
        </div>
    </div>
    <div style="text-align: right;">
        <div style="font-size: 2.5rem; font-weight: 700; color: {color};">${current_price:.2f}</div>
        <div style="font-size: 1rem; color: {color};">{arrow} ${abs(price_change):.2f} ({price_pct:+.2f}%)</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Key Metrics ────────────────────────────────────────────────────────────────
cols = st.columns(5)
metrics = [
    ("Market Cap", format_large_number(info.get("marketCap", 0))),
    ("P/E Ratio", f"{info.get('trailingPE', 0):.2f}" if info.get('trailingPE') else "N/A"),
    ("52W High", f"${info.get('fiftyTwoWeekHigh', 0):.2f}" if info.get('fiftyTwoWeekHigh') else "N/A"),
    ("52W Low", f"${info.get('fiftyTwoWeekLow', 0):.2f}" if info.get('fiftyTwoWeekLow') else "N/A"),
    ("Dividend Yield", f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "N/A"),
]
for i, (label, val) in enumerate(metrics):
    with cols[i]:
        st.metric(label, val)

st.markdown("<br>", unsafe_allow_html=True)

# ── Indicators Selection ───────────────────────────────────────────────────────
st.markdown("#### 📐 Chart Overlays & Indicators")
col_a, col_b, col_c, col_d, col_e = st.columns(5)
with col_a: show_sma20 = st.checkbox("SMA 20", value=True)
with col_b: show_sma50 = st.checkbox("SMA 50", value=True)
with col_c: show_ema20 = st.checkbox("EMA 20", value=False)
with col_d: show_bb = st.checkbox("Bollinger Bands", value=True)
with col_e: show_signals = st.checkbox("Buy/Sell Signals", value=True)

# ── Main Chart ─────────────────────────────────────────────────────────────────
fig = make_subplots(
    rows=4, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.5, 0.15, 0.18, 0.17],
    subplot_titles=["", "Volume", "RSI (14)", "MACD"],
)

# Candlestick
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"], high=df["High"],
    low=df["Low"], close=df["Close"],
    increasing_line_color="#48BB78", decreasing_line_color="#F56565",
    increasing_fillcolor="#48BB78", decreasing_fillcolor="#F56565",
    name="OHLC",
), row=1, col=1)

# Overlays
if show_sma20:
    sma20 = calculate_sma(df, 20)
    fig.add_trace(go.Scatter(x=df.index, y=sma20, name="SMA 20", line=dict(color="#00D4FF", width=1.5, dash="solid")), row=1, col=1)
if show_sma50:
    sma50 = calculate_sma(df, 50)
    fig.add_trace(go.Scatter(x=df.index, y=sma50, name="SMA 50", line=dict(color="#F6AD55", width=1.5, dash="solid")), row=1, col=1)
if show_ema20:
    ema20 = calculate_ema(df, 20)
    fig.add_trace(go.Scatter(x=df.index, y=ema20, name="EMA 20", line=dict(color="#B794F4", width=1.5, dash="dot")), row=1, col=1)
if show_bb:
    bb_upper, bb_mid, bb_lower = calculate_bollinger_bands(df)
    fig.add_trace(go.Scatter(x=df.index, y=bb_upper, name="BB Upper", line=dict(color="rgba(0,212,255,0.4)", width=1, dash="dash"), showlegend=True), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=bb_lower, name="BB Lower", line=dict(color="rgba(0,212,255,0.4)", width=1, dash="dash"),
        fill="tonexty", fillcolor="rgba(0,212,255,0.04)", showlegend=True), row=1, col=1)

# Buy/Sell signals
if show_signals:
    signals = generate_signals(df)
    buy_mask = signals["Buy_Signal"]
    sell_mask = signals["Sell_Signal"]
    if buy_mask.any():
        fig.add_trace(go.Scatter(
            x=df.index[buy_mask], y=df["Low"][buy_mask] * 0.99,
            mode="markers", name="Buy Signal",
            marker=dict(symbol="triangle-up", size=12, color="#48BB78", line=dict(color="white", width=1)),
        ), row=1, col=1)
    if sell_mask.any():
        fig.add_trace(go.Scatter(
            x=df.index[sell_mask], y=df["High"][sell_mask] * 1.01,
            mode="markers", name="Sell Signal",
            marker=dict(symbol="triangle-down", size=12, color="#F56565", line=dict(color="white", width=1)),
        ), row=1, col=1)

# Volume
vol_colors = ["#48BB78" if c >= o else "#F56565" for c, o in zip(df["Close"], df["Open"])]
fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume", marker_color=vol_colors, opacity=0.7), row=2, col=1)

# RSI
rsi = calculate_rsi(df)
fig.add_trace(go.Scatter(x=df.index, y=rsi, name="RSI", line=dict(color="#B794F4", width=2)), row=3, col=1)
fig.add_hline(y=70, line_dash="dash", line_color="#F56565", opacity=0.6, row=3, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="#48BB78", opacity=0.6, row=3, col=1)
fig.add_hrect(y0=70, y1=100, fillcolor="rgba(245,101,101,0.05)", row=3, col=1)
fig.add_hrect(y0=0, y1=30, fillcolor="rgba(72,187,120,0.05)", row=3, col=1)

# MACD
macd_line, signal_line, histogram = calculate_macd(df)
hist_colors = ["#48BB78" if v >= 0 else "#F56565" for v in histogram]
fig.add_trace(go.Bar(x=df.index, y=histogram, name="MACD Hist", marker_color=hist_colors, opacity=0.6), row=4, col=1)
fig.add_trace(go.Scatter(x=df.index, y=macd_line, name="MACD", line=dict(color="#00D4FF", width=1.5)), row=4, col=1)
fig.add_trace(go.Scatter(x=df.index, y=signal_line, name="Signal", line=dict(color="#F6AD55", width=1.5)), row=4, col=1)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#E8EAF6",
    xaxis_rangeslider_visible=False,
    height=850,
    margin=dict(t=30, b=20, l=10, r=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.01, bgcolor="rgba(0,0,0,0)", font_size=11),
    hovermode="x unified",
)
for i in range(1, 5):
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.04)", row=i, col=1)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.04)", row=i, col=1)

st.plotly_chart(fig, use_container_width=True)

# ── Signal Summary ─────────────────────────────────────────────────────────────
st.markdown("### 🎯 Technical Signal Summary")
rsi_val = rsi.iloc[-1] if not rsi.empty else 50
macd_val = macd_line.iloc[-1]
signal_val = signal_line.iloc[-1]

rsi_signal = "Oversold 🟢" if rsi_val < 30 else ("Overbought 🔴" if rsi_val > 70 else "Neutral 🟡")
macd_signal = "Bullish 🟢" if macd_val > signal_val else "Bearish 🔴"

# Overall signal
bullish_count = sum([rsi_val < 50, macd_val > signal_val])
overall = "BUY 🟢" if bullish_count >= 2 else ("SELL 🔴" if bullish_count == 0 else "HOLD 🟡")
overall_class = "signal-buy" if "BUY" in overall else ("signal-sell" if "SELL" in overall else "signal-neutral")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="signal-neutral">
        <div style="font-size:0.85rem; color:#94A3B8; margin-bottom:0.3rem;">RSI (14)</div>
        <div style="font-size:1.5rem; font-weight:700; color:#E8EAF6;">{rsi_val:.1f}</div>
        <div style="font-size:0.9rem; color:#F6AD55;">{rsi_signal}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="signal-neutral">
        <div style="font-size:0.85rem; color:#94A3B8; margin-bottom:0.3rem;">MACD Signal</div>
        <div style="font-size:1.5rem; font-weight:700; color:#E8EAF6;">{macd_val:.3f}</div>
        <div style="font-size:0.9rem; color:#F6AD55;">{macd_signal}</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="{overall_class}">
        <div style="font-size:0.85rem; color:#94A3B8; margin-bottom:0.3rem;">Overall Signal</div>
        <div style="font-size:1.8rem; font-weight:800; color:#E8EAF6;">{overall}</div>
        <div style="font-size:0.85rem; color:#94A3B8;">Based on RSI + MACD</div>
    </div>
    """, unsafe_allow_html=True)

# ── Raw Data ───────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📋 View Raw Data"):
    st.dataframe(
        df[["Open","High","Low","Close","Volume"]].tail(50).sort_index(ascending=False)
        .style.format({"Open":"${:.2f}","High":"${:.2f}","Low":"${:.2f}","Close":"${:.2f}","Volume":"{:,.0f}"}),
        use_container_width=True,
    )

st.caption("⚠️ Data from Yahoo Finance. For educational purposes only — not financial advice.")
