import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_fetcher import get_crypto_data, get_stock_data, format_large_number

st.set_page_config(page_title="Crypto Tracker | FinSight Pro", page_icon="₿", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header {visibility: hidden;}
.stApp { background: linear-gradient(135deg, #0A0E1A 0%, #0D1529 50%, #0A0E1A 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0D1529 0%, #111827 100%); border-right: 1px solid rgba(0,212,255,0.15); }
[data-testid="stMetric"] { background: rgba(255,255,255,0.03); border: 1px solid rgba(246,173,85,0.2); border-radius: 12px; padding: 1rem; transition: transform 0.2s; }
[data-testid="stMetric"]:hover { transform: translateY(-2px); border-color: rgba(246,173,85,0.5); }
.stButton > button { background: linear-gradient(135deg, #F6AD55, #ED8936) !important; color: #0A0E1A !important; border: none !important; border-radius: 8px !important; font-weight: 700 !important; box-shadow: 0 4px 15px rgba(246,173,85,0.3) !important; }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #0A0E1A; } ::-webkit-scrollbar-thumb { background: rgba(246,173,85,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="padding: 1.5rem 0; border-bottom: 1px solid rgba(246,173,85,0.15); margin-bottom: 2rem;">
    <h1 style="margin:0; font-size:2.2rem; font-weight:800;
        background: linear-gradient(135deg,#FFFFFF,#F6AD55);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
        ₿ Crypto Tracker
    </h1>
    <p style="color:#64748B; margin:0.3rem 0 0; font-size:0.95rem;">
        Live cryptocurrency prices, market caps, and performance analysis
    </p>
</div>
""", unsafe_allow_html=True)

# ── Top Cryptos ────────────────────────────────────────────────────────────────
TOP_CRYPTOS = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD",
    "ADA-USD", "DOGE-USD", "AVAX-USD", "DOT-USD", "MATIC-USD",
    "LINK-USD", "UNI-USD", "ATOM-USD", "LTC-USD", "BCH-USD",
]

CRYPTO_ICONS = {
    "BTC": "₿", "ETH": "Ξ", "BNB": "◈", "SOL": "◎", "XRP": "✕",
    "ADA": "◬", "DOGE": "Ð", "AVAX": "▲", "DOT": "●", "MATIC": "⬡",
    "LINK": "⬡", "UNI": "🦄", "ATOM": "⚛", "LTC": "Ł", "BCH": "Ƀ",
}

col_r, col_sel, _ = st.columns([1, 3, 3])
with col_r:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()
with col_sel:
    selected_cryptos = st.multiselect(
        "Select Cryptocurrencies",
        options=TOP_CRYPTOS,
        default=["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD"],
        format_func=lambda x: x.replace("-USD", ""),
    )

if not selected_cryptos:
    st.info("Please select at least one cryptocurrency.")
    st.stop()

with st.spinner("Fetching live crypto data..."):
    crypto_df = get_crypto_data(selected_cryptos)

if crypto_df.empty:
    st.error("Could not load crypto data. Please check your connection.")
    st.stop()

# ── Metric Cards ───────────────────────────────────────────────────────────────
st.markdown("### 💰 Live Prices")
num_cols = min(len(crypto_df), 6)
cols = st.columns(num_cols)
for i, (_, row) in enumerate(crypto_df.head(num_cols).iterrows()):
    with cols[i]:
        icon = CRYPTO_ICONS.get(row["Symbol"], "🪙")
        st.metric(
            label=f"{icon} {row['Symbol']}",
            value=f"${row['Price']:,.2f}" if row["Price"] > 1 else f"${row['Price']:.6f}",
            delta=f"{row['Change_24h']:+.2f}%",
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Main Crypto Table ──────────────────────────────────────────────────────────
st.markdown("### 📊 Market Summary")
display_df = crypto_df.copy()
display_df["Market Cap"] = display_df["Market_Cap"].apply(format_large_number)
display_df["Volume 24h"] = display_df["Volume_24h"].apply(lambda x: format_large_number(x) if x > 0 else "N/A")
display_df["Price"] = display_df["Price"].apply(lambda x: f"${x:,.4f}" if x < 1 else f"${x:,.2f}")
display_df["24h Change"] = display_df["Change_24h"].apply(lambda x: f"{x:+.2f}%")
display_df["24h High"] = display_df["High_24h"].apply(lambda x: f"${x:,.2f}")
display_df["24h Low"] = display_df["Low_24h"].apply(lambda x: f"${x:,.2f}")

show_cols = ["Symbol", "Name", "Price", "24h Change", "Market Cap", "Volume 24h", "24h High", "24h Low"]
st.dataframe(
    display_df[show_cols].style.apply(
        lambda col: [
            "color: #48BB78" if "+" in str(v) else ("color: #F56565" if "-" in str(v) else "")
            for v in col
        ] if col.name == "24h Change" else ["" for _ in col],
        axis=0,
    ),
    use_container_width=True,
    hide_index=True,
    height=350,
)

# ── Performance Chart ──────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📈 Historical Performance Comparison")

period_map = {"1 Week": "7d", "1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y"}
period_label = st.select_slider("Time Period", options=list(period_map.keys()), value="3 Months")
period = period_map[period_label]

crypto_colors = ["#F6AD55", "#00D4FF", "#48BB78", "#B794F4", "#F56565", "#76E4F7", "#FBD38D", "#9AE6B4"]

fig_perf = go.Figure()
with st.spinner("Loading historical data..."):
    for idx, sym in enumerate(selected_cryptos[:8]):
        hist = get_stock_data(sym, period=period, interval="1d")
        if not hist.empty:
            normalized = (hist["Close"] / hist["Close"].iloc[0]) * 100
            fig_perf.add_trace(go.Scatter(
                x=hist.index,
                y=normalized,
                name=sym.replace("-USD", ""),
                line=dict(color=crypto_colors[idx % len(crypto_colors)], width=2),
                hovertemplate=f"<b>{sym.replace('-USD', '')}</b><br>Date: %{{x}}<br>Return: %{{y:.1f}}%<extra></extra>",
            ))

fig_perf.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.2)", line_width=1,
                   annotation_text="Baseline", annotation_position="right", annotation_font_color="#94A3B8")

fig_perf.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#E8EAF6",
    height=450,
    margin=dict(t=30, b=20, l=10, r=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.01, bgcolor="rgba(0,0,0,0)", font_size=11),
    hovermode="x unified",
    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", ticksuffix="%", title="Indexed Return (Base=100)"),
)
st.plotly_chart(fig_perf, use_container_width=True)

# ── 24h Change Bar Chart ───────────────────────────────────────────────────────
st.markdown("### 📊 24-Hour Performance")
fig_bar = go.Figure()
bar_colors = ["#48BB78" if v >= 0 else "#F56565" for v in crypto_df["Change_24h"]]
fig_bar.add_trace(go.Bar(
    x=crypto_df["Symbol"],
    y=crypto_df["Change_24h"],
    marker_color=bar_colors,
    text=[f"{v:+.2f}%" for v in crypto_df["Change_24h"]],
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>24h Change: %{y:+.2f}%<extra></extra>",
))
fig_bar.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#E8EAF6",
    height=350,
    margin=dict(t=30, b=20, l=10, r=10),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", ticksuffix="%"),
    showlegend=False,
)
fig_bar.add_hline(y=0, line_color="rgba(255,255,255,0.2)", line_width=1)
st.plotly_chart(fig_bar, use_container_width=True)

st.caption("⚠️ Data from Yahoo Finance. For educational purposes only — not financial advice.")
