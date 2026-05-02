import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sys, os
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_fetcher import get_stock_data, get_stock_info, format_large_number

st.set_page_config(page_title="Portfolio Manager | FinSight Pro", page_icon="💼", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header {visibility: hidden;}
.stApp { background: linear-gradient(135deg, #0A0E1A 0%, #0D1529 50%, #0A0E1A 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0D1529 0%, #111827 100%); border-right: 1px solid rgba(0,212,255,0.15); }
[data-testid="stMetric"] { background: rgba(255,255,255,0.03); border: 1px solid rgba(0,212,255,0.15); border-radius: 12px; padding: 1rem; transition: transform 0.2s; }
[data-testid="stMetric"]:hover { transform: translateY(-2px); }
.stButton > button { background: linear-gradient(135deg, #00D4FF, #0080FF) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; box-shadow: 0 4px 15px rgba(0,212,255,0.3) !important; }
.stTextInput > div > div > input { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(0,212,255,0.2) !important; border-radius: 8px !important; color: #E8EAF6 !important; }
.stNumberInput > div > div > input { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(0,212,255,0.2) !important; border-radius: 8px !important; color: #E8EAF6 !important; }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #0A0E1A; } ::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="padding: 1.5rem 0; border-bottom: 1px solid rgba(0,212,255,0.1); margin-bottom: 2rem;">
    <h1 style="margin:0; font-size:2.2rem; font-weight:800;
        background: linear-gradient(135deg,#FFFFFF,#00D4FF);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
        💼 Portfolio Manager
    </h1>
    <p style="color:#64748B; margin:0.3rem 0 0; font-size:0.95rem;">
        Build, track and analyze your investment portfolio
    </p>
</div>
""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────────────────────────
if "portfolio" not in st.session_state:
    st.session_state.portfolio = [
        {"ticker": "AAPL", "shares": 10, "avg_price": 150.0},
        {"ticker": "MSFT", "shares": 5, "avg_price": 280.0},
        {"ticker": "GOOGL", "shares": 3, "avg_price": 2500.0},
        {"ticker": "NVDA", "shares": 8, "avg_price": 400.0},
        {"ticker": "TSLA", "shares": 7, "avg_price": 200.0},
    ]

# ── Add / Remove Holdings ──────────────────────────────────────────────────────
with st.expander("➕ Manage Holdings", expanded=False):
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    with col1:
        new_ticker = st.text_input("Ticker Symbol", placeholder="e.g. AAPL").upper().strip()
    with col2:
        new_shares = st.number_input("Number of Shares", min_value=0.01, value=1.0, step=0.1)
    with col3:
        new_avg = st.number_input("Avg. Buy Price ($)", min_value=0.01, value=100.0, step=0.5)
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Add +"):
            if new_ticker:
                # Update or add
                existing = [h for h in st.session_state.portfolio if h["ticker"] == new_ticker]
                if existing:
                    idx = st.session_state.portfolio.index(existing[0])
                    old = st.session_state.portfolio[idx]
                    total_shares = old["shares"] + new_shares
                    new_avg_price = (old["shares"] * old["avg_price"] + new_shares * new_avg) / total_shares
                    st.session_state.portfolio[idx] = {"ticker": new_ticker, "shares": total_shares, "avg_price": new_avg_price}
                    st.success(f"Updated {new_ticker} position!")
                else:
                    st.session_state.portfolio.append({"ticker": new_ticker, "shares": new_shares, "avg_price": new_avg})
                    st.success(f"Added {new_ticker} to portfolio!")
                st.rerun()

    st.markdown("<br>")
    if st.session_state.portfolio:
        ticker_to_remove = st.selectbox("Remove Holding", ["-- Select --"] + [h["ticker"] for h in st.session_state.portfolio])
        if ticker_to_remove != "-- Select --":
            if st.button(f"🗑️ Remove {ticker_to_remove}"):
                st.session_state.portfolio = [h for h in st.session_state.portfolio if h["ticker"] != ticker_to_remove]
                st.success(f"Removed {ticker_to_remove}")
                st.rerun()

if not st.session_state.portfolio:
    st.info("Your portfolio is empty. Add some holdings above.")
    st.stop()

# ── Fetch Current Prices ───────────────────────────────────────────────────────
with st.spinner("Fetching current market prices..."):
    portfolio_data = []
    for holding in st.session_state.portfolio:
        ticker = holding["ticker"]
        shares = holding["shares"]
        avg_price = holding["avg_price"]
        df = get_stock_data(ticker, period="5d", interval="1d")
        info = get_stock_info(ticker)
        if not df.empty:
            current_price = df["Close"].iloc[-1]
            prev_price = df["Close"].iloc[-2] if len(df) > 1 else current_price
            day_change_pct = ((current_price - prev_price) / prev_price) * 100
            cost_basis = shares * avg_price
            market_value = shares * current_price
            gain_loss = market_value - cost_basis
            gain_loss_pct = (gain_loss / cost_basis) * 100
            portfolio_data.append({
                "Ticker": ticker,
                "Company": info.get("shortName", ticker),
                "Shares": shares,
                "Avg Price": avg_price,
                "Current Price": current_price,
                "Day Change %": day_change_pct,
                "Cost Basis": cost_basis,
                "Market Value": market_value,
                "Gain/Loss $": gain_loss,
                "Gain/Loss %": gain_loss_pct,
                "Sector": info.get("sector", "Unknown"),
            })

if not portfolio_data:
    st.error("Could not fetch data for portfolio holdings.")
    st.stop()

port_df = pd.DataFrame(portfolio_data)

# ── Summary Metrics ────────────────────────────────────────────────────────────
total_value = port_df["Market Value"].sum()
total_cost = port_df["Cost Basis"].sum()
total_gain = total_value - total_cost
total_gain_pct = (total_gain / total_cost) * 100 if total_cost > 0 else 0
day_pnl = sum(row["Market Value"] * row["Day Change %"] / 100 for _, row in port_df.iterrows())

st.markdown("### 📊 Portfolio Summary")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Value", f"${total_value:,.2f}")
with col2:
    st.metric("Total Cost Basis", f"${total_cost:,.2f}")
with col3:
    st.metric("Total P&L", f"${total_gain:,.2f}", delta=f"{total_gain_pct:+.2f}%")
with col4:
    st.metric("Today's P&L", f"${day_pnl:+,.2f}")
with col5:
    st.metric("# Holdings", f"{len(port_df)}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🥧 Allocation", "📈 Performance", "⚠️ Risk Analysis", "📋 Holdings Table"])

with tab1:
    col_pie1, col_pie2 = st.columns(2)
    with col_pie1:
        st.markdown("#### Portfolio Allocation by Value")
        fig_alloc = go.Figure(go.Pie(
            labels=port_df["Ticker"],
            values=port_df["Market Value"],
            hole=0.55,
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Value: $%{value:,.2f}<br>Share: %{percent}<extra></extra>",
            marker=dict(colors=px.colors.qualitative.Bold),
        ))
        fig_alloc.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#E8EAF6",
            showlegend=True,
            legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11),
            height=350,
            margin=dict(t=20, b=20, l=10, r=10),
            annotations=[dict(text=f"<b>${total_value/1000:.1f}K</b>", x=0.5, y=0.5,
                              font_size=18, font_color="#E8EAF6", showarrow=False)],
        )
        st.plotly_chart(fig_alloc, use_container_width=True)

    with col_pie2:
        st.markdown("#### Allocation by Sector")
        sector_df = port_df.groupby("Sector")["Market Value"].sum().reset_index()
        fig_sector = go.Figure(go.Pie(
            labels=sector_df["Sector"],
            values=sector_df["Market Value"],
            hole=0.55,
            textinfo="label+percent",
            marker=dict(colors=px.colors.qualitative.Pastel),
        ))
        fig_sector.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#E8EAF6",
            showlegend=True,
            legend=dict(bgcolor="rgba(0,0,0,0)", font_size=10),
            height=350,
            margin=dict(t=20, b=20, l=10, r=10),
        )
        st.plotly_chart(fig_sector, use_container_width=True)

with tab2:
    st.markdown("#### Individual Stock P&L")
    colors_pnl = ["#48BB78" if v >= 0 else "#F56565" for v in port_df["Gain/Loss %"]]
    fig_pnl = go.Figure()
    fig_pnl.add_trace(go.Bar(
        x=port_df["Ticker"],
        y=port_df["Gain/Loss %"],
        marker_color=colors_pnl,
        text=[f"{v:+.1f}%" for v in port_df["Gain/Loss %"]],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>P&L: %{y:+.2f}%<br>$%{customdata:,.2f}<extra></extra>",
        customdata=port_df["Gain/Loss $"],
    ))
    fig_pnl.add_hline(y=0, line_color="rgba(255,255,255,0.2)", line_width=1)
    fig_pnl.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E8EAF6",
        height=380,
        margin=dict(t=30, b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", ticksuffix="%"),
        showlegend=False,
    )
    st.plotly_chart(fig_pnl, use_container_width=True)

    st.markdown("#### Historical Portfolio Performance")
    period_sel = st.selectbox("Period", ["1mo","3mo","6mo","1y"], index=2, key="perf_period")
    fig_hist_port = go.Figure()
    total_hist = None

    for _, row in port_df.iterrows():
        hist = get_stock_data(row["Ticker"], period=period_sel, interval="1d")
        if not hist.empty:
            position_value = hist["Close"] * row["Shares"]
            if total_hist is None:
                total_hist = position_value.copy()
            else:
                total_hist = total_hist.add(position_value, fill_value=0)
            normalized = (hist["Close"] / hist["Close"].iloc[0] - 1) * 100
            fig_hist_port.add_trace(go.Scatter(
                x=hist.index, y=normalized, name=row["Ticker"],
                line=dict(width=1.5), opacity=0.7,
                hovertemplate=f"<b>{row['Ticker']}</b>: %{{y:+.1f}}%<extra></extra>",
            ))

    if total_hist is not None:
        norm_total = (total_hist / total_hist.iloc[0] - 1) * 100
        fig_hist_port.add_trace(go.Scatter(
            x=total_hist.index, y=norm_total, name="📊 Portfolio Total",
            line=dict(color="#00D4FF", width=3, dash="solid"),
            hovertemplate="<b>Portfolio</b>: %{y:+.1f}%<extra></extra>",
        ))

    fig_hist_port.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig_hist_port.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E8EAF6",
        height=400,
        margin=dict(t=30, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11),
        hovermode="x unified",
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", ticksuffix="%", title="Return %"),
    )
    st.plotly_chart(fig_hist_port, use_container_width=True)

with tab3:
    st.markdown("#### Risk Metrics")
    risk_data = []
    with st.spinner("Computing risk metrics..."):
        for _, row in port_df.iterrows():
            hist = get_stock_data(row["Ticker"], period="1y", interval="1d")
            if not hist.empty and len(hist) > 20:
                returns = hist["Close"].pct_change().dropna()
                vol_ann = returns.std() * np.sqrt(252) * 100
                sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252) + 1e-9)
                max_dd = ((hist["Close"] / hist["Close"].cummax()) - 1).min() * 100
                beta_approx = returns.corr(returns.shift(1).fillna(0))  # simplified
                risk_data.append({
                    "Ticker": row["Ticker"],
                    "Weight %": row["Market Value"] / total_value * 100,
                    "Ann. Volatility %": vol_ann,
                    "Sharpe Ratio": sharpe,
                    "Max Drawdown %": max_dd,
                    "Gain/Loss %": row["Gain/Loss %"],
                })

    risk_df = pd.DataFrame(risk_data)
    if not risk_df.empty:
        # Risk-Return scatter
        fig_rr = go.Figure()
        colors_rr = ["#48BB78" if v >= 0 else "#F56565" for v in risk_df["Gain/Loss %"]]
        fig_rr.add_trace(go.Scatter(
            x=risk_df["Ann. Volatility %"],
            y=risk_df["Gain/Loss %"],
            mode="markers+text",
            text=risk_df["Ticker"],
            textposition="top center",
            textfont=dict(color="#E8EAF6", size=11),
            marker=dict(
                size=risk_df["Weight %"] * 2 + 8,
                color=colors_rr,
                opacity=0.8,
                line=dict(color="white", width=1.5),
            ),
            hovertemplate="<b>%{text}</b><br>Volatility: %{x:.1f}%<br>P&L: %{y:+.1f}%<extra></extra>",
        ))
        fig_rr.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#E8EAF6",
            height=380,
            margin=dict(t=30, b=20),
            xaxis=dict(title="Annualized Volatility %", showgrid=True, gridcolor="rgba(255,255,255,0.04)"),
            yaxis=dict(title="Gain/Loss %", showgrid=True, gridcolor="rgba(255,255,255,0.04)"),
        )
        st.plotly_chart(fig_rr, use_container_width=True)
        st.caption("Bubble size = portfolio weight")

        st.dataframe(
            risk_df.style.format({
                "Weight %": "{:.1f}%",
                "Ann. Volatility %": "{:.1f}%",
                "Sharpe Ratio": "{:.2f}",
                "Max Drawdown %": "{:.1f}%",
                "Gain/Loss %": "{:+.1f}%",
            }),
            use_container_width=True, hide_index=True,
        )

with tab4:
    st.markdown("#### Holdings Details")
    display_port = port_df.copy()
    st.dataframe(
        display_port[["Ticker","Company","Shares","Avg Price","Current Price","Day Change %",
                       "Cost Basis","Market Value","Gain/Loss $","Gain/Loss %","Sector"]].style.format({
            "Avg Price": "${:.2f}", "Current Price": "${:.2f}", "Day Change %": "{:+.2f}%",
            "Cost Basis": "${:,.2f}", "Market Value": "${:,.2f}",
            "Gain/Loss $": "${:+,.2f}", "Gain/Loss %": "{:+.2f}%",
        }).background_gradient(subset=["Gain/Loss %"], cmap="RdYlGn"),
        use_container_width=True, hide_index=True, height=400,
    )

    # Export
    csv_data = port_df.to_csv(index=False)
    st.download_button(
        "📥 Export Portfolio (CSV)",
        data=csv_data,
        file_name=f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

st.caption("⚠️ Data from Yahoo Finance. For educational purposes only — not financial advice.")
