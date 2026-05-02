import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_fetcher import get_market_indices, get_top_movers, format_large_number

st.set_page_config(page_title="Market Overview | FinSight Pro", page_icon="📊", layout="wide")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header {visibility: hidden;}
.stApp { background: linear-gradient(135deg, #0A0E1A 0%, #0D1529 50%, #0A0E1A 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0D1529 0%, #111827 100%); border-right: 1px solid rgba(0,212,255,0.15); }
[data-testid="stMetric"] { background: rgba(255,255,255,0.03); border: 1px solid rgba(0,212,255,0.15); border-radius: 12px; padding: 1rem; transition: transform 0.2s; }
[data-testid="stMetric"]:hover { transform: translateY(-2px); border-color: rgba(0,212,255,0.4); }
.stButton > button { background: linear-gradient(135deg, #00D4FF, #0080FF) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #0A0E1A; } ::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 1.5rem 0; border-bottom: 1px solid rgba(0,212,255,0.1); margin-bottom: 2rem;">
    <h1 style="margin:0; font-size:2.2rem; font-weight:800;
        background: linear-gradient(135deg,#FFFFFF,#00D4FF);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
        📊 Market Overview
    </h1>
    <p style="color:#64748B; margin:0.3rem 0 0; font-size:0.95rem;">
        Real-time global market indices and top movers
    </p>
</div>
""", unsafe_allow_html=True)

# ── Refresh ────────────────────────────────────────────────────────────────────
col_r, _ = st.columns([1, 5])
with col_r:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# ── Market Indices ─────────────────────────────────────────────────────────────
st.markdown("### 🌍 Global Indices")
with st.spinner("Loading market data..."):
    indices = get_market_indices()

if indices:
    cols = st.columns(len(indices))
    for i, (name, data) in enumerate(indices.items()):
        with cols[i]:
            delta_color = "normal"
            price_str = f"${data['price']:,.2f}" if data['price'] > 100 else f"{data['price']:.2f}"
            st.metric(
                label=f"{name}",
                value=price_str,
                delta=f"{data['pct_change']:+.2f}%",
                delta_color=delta_color,
            )
else:
    st.warning("Could not load market index data. Please check your connection.")

st.markdown("<br>", unsafe_allow_html=True)

# ── Top Movers ─────────────────────────────────────────────────────────────────
SP500_SAMPLE = [
    "AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA","BRK-B","JPM","V",
    "JNJ","WMT","XOM","MA","PG","HD","CVX","MRK","ABBV","LLY",
    "AVGO","PEP","COST","KO","BAC","MCD","TMO","CSCO","ABT","ACN",
    "CRM","DHR","NFLX","NKE","INTC","TXN","QCOM","AMD","ADBE","AMGN",
]

st.markdown("### 📈 Top Movers (S&P 500 Sample)")
st.caption("⏳ Loading top movers — this may take a moment...")

with st.spinner("Fetching top movers data..."):
    movers_df = get_top_movers(SP500_SAMPLE)

if not movers_df.empty:
    tab1, tab2 = st.tabs(["🚀 Top Gainers", "📉 Top Losers"])

    with tab1:
        gainers = movers_df.nlargest(10, "Change %")
        fig_g = go.Figure()
        colors_g = [f"rgba(0,{int(200 * v/gainers['Change %'].max())},100,0.9)" for v in gainers["Change %"]]
        fig_g.add_trace(go.Bar(
            x=gainers["Ticker"],
            y=gainers["Change %"],
            marker_color=colors_g,
            text=[f"+{v:.2f}%" for v in gainers["Change %"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Change: %{y:.2f}%<extra></extra>",
        ))
        fig_g.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#E8EAF6",
            xaxis=dict(showgrid=False, tickfont=dict(size=12)),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", ticksuffix="%"),
            showlegend=False,
            height=350,
            margin=dict(t=20, b=20),
        )
        st.plotly_chart(fig_g, use_container_width=True)

        st.dataframe(
            gainers[["Ticker","Company","Price","Change %"]].style
            .format({"Price": "${:.2f}", "Change %": "{:+.2f}%"})
            .background_gradient(subset=["Change %"], cmap="Greens"),
            use_container_width=True, hide_index=True,
        )

    with tab2:
        losers = movers_df.nsmallest(10, "Change %")
        colors_l = [f"rgba(220,{int(50 * abs(v)/abs(losers['Change %'].min()))},50,0.9)" for v in losers["Change %"]]
        fig_l = go.Figure()
        fig_l.add_trace(go.Bar(
            x=losers["Ticker"],
            y=losers["Change %"],
            marker_color=colors_l,
            text=[f"{v:.2f}%" for v in losers["Change %"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Change: %{y:.2f}%<extra></extra>",
        ))
        fig_l.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#E8EAF6",
            xaxis=dict(showgrid=False, tickfont=dict(size=12)),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", ticksuffix="%"),
            showlegend=False,
            height=350,
            margin=dict(t=20, b=20),
        )
        st.plotly_chart(fig_l, use_container_width=True)
        st.dataframe(
            losers[["Ticker","Company","Price","Change %"]].style
            .format({"Price": "${:.2f}", "Change %": "{:+.2f}%"})
            .background_gradient(subset=["Change %"], cmap="Reds_r"),
            use_container_width=True, hide_index=True,
        )

    # ── Market Heatmap ─────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🌡️ Market Heat Map")

    heatmap_df = movers_df.copy()
    heatmap_df["color_val"] = heatmap_df["Change %"].clip(-5, 5)

    fig_heat = px.treemap(
        heatmap_df,
        path=["Ticker"],
        values=heatmap_df["Price"].abs(),
        color="color_val",
        color_continuous_scale=["#FF3B3B", "#FF6B6B", "#2D3748", "#48BB78", "#38A169"],
        color_continuous_midpoint=0,
        custom_data=["Company", "Change %", "Price"],
        hover_data={"color_val": False},
    )
    fig_heat.update_traces(
        hovertemplate="<b>%{label}</b><br>%{customdata[0]}<br>Price: $%{customdata[2]:.2f}<br>Change: %{customdata[1]:+.2f}%<extra></extra>",
        texttemplate="<b>%{label}</b><br>%{customdata[1]:+.2f}%",
        textfont_size=13,
    )
    fig_heat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#E8EAF6",
        coloraxis_showscale=False,
        height=400,
        margin=dict(t=10, b=10, l=10, r=10),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

else:
    st.error("Could not load top movers. Please check your internet connection.")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.caption("⚠️ Data from Yahoo Finance. For educational purposes only — not financial advice.")
