import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_fetcher import get_stock_data, get_stock_info
from utils.ml_models import train_and_predict

st.set_page_config(page_title="AI Price Predictor | FinSight Pro", page_icon="🤖", layout="wide")

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
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #0A0E1A; } ::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="padding: 1.5rem 0; border-bottom: 1px solid rgba(0,212,255,0.1); margin-bottom: 2rem;">
    <h1 style="margin:0; font-size:2.2rem; font-weight:800;
        background: linear-gradient(135deg,#FFFFFF,#00D4FF);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
        🤖 AI Price Predictor
    </h1>
    <p style="color:#64748B; margin:0.3rem 0 0; font-size:0.95rem;">
        Machine learning models to forecast stock prices
    </p>
</div>
""", unsafe_allow_html=True)

# ── Controls ───────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
with col1:
    ticker = st.text_input("Stock Ticker", value="AAPL", placeholder="e.g. AAPL, TSLA, MSFT").upper().strip()
with col2:
    model_type = st.selectbox("ML Model", ["Random Forest", "Gradient Boosting", "Linear Regression"])
with col3:
    forecast_days = st.selectbox("Forecast Horizon", [7, 14, 30], format_func=lambda x: f"{x} Days")
with col4:
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("Predict 🤖")

# ── Info Box ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: rgba(0,212,255,0.04);
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    font-size: 0.88rem;
    color: #64748B;
    line-height: 1.7;
">
    <strong style="color:#00D4FF">ℹ️ How it works:</strong>
    The model uses 2 years of historical OHLCV data, engineered features (lag prices, rolling statistics,
    RSI, MACD, volume ratios), and time-series cross-validation to train a prediction model.
    Past performance is not indicative of future results.
</div>
""", unsafe_allow_html=True)

if not ticker:
    st.info("Enter a ticker and click Predict.")
    st.stop()

# ── Fetch + Train ──────────────────────────────────────────────────────────────
with st.spinner(f"Fetching 2 years of data for {ticker}..."):
    df = get_stock_data(ticker, period="2y", interval="1d")
    info = get_stock_info(ticker)

if df.empty:
    st.error(f"No data found for '{ticker}'.")
    st.stop()

company_name = info.get("shortName", ticker)

with st.spinner(f"Training {model_type} model... This may take a moment."):
    result = train_and_predict(df, forecast_days=forecast_days, model_type=model_type)

if "error" in result:
    st.error(result["error"])
    st.stop()

# ── Metrics ────────────────────────────────────────────────────────────────────
st.markdown(f"### 📊 Model Performance — {company_name} ({ticker})")

metrics = result["metrics"]
current_price = result["current_price"]
predicted_final = result["predicted_final"]
price_diff = predicted_final - current_price if predicted_final else 0
pct_diff = (price_diff / current_price) * 100 if current_price else 0

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Current Price", f"${current_price:.2f}")
with col2:
    st.metric(f"Predicted ({forecast_days}d)", f"${predicted_final:.2f}" if predicted_final else "N/A",
              delta=f"{pct_diff:+.2f}%")
with col3:
    st.metric("RMSE", f"${metrics['RMSE']:.2f}")
with col4:
    st.metric("MAE", f"${metrics['MAE']:.2f}")
with col5:
    r2_pct = metrics['R²'] * 100
    st.metric("R² Score", f"{r2_pct:.1f}%")

# ── Model Accuracy Bar ─────────────────────────────────────────────────────────
accuracy = max(0, min(100, r2_pct))
acc_color = "#48BB78" if accuracy > 80 else ("#F6AD55" if accuracy > 60 else "#F56565")
st.markdown(f"""
<div style="margin: 1rem 0;">
    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #94A3B8; margin-bottom: 4px;">
        <span>Model Accuracy (R²)</span><span style="color:{acc_color}">{accuracy:.1f}%</span>
    </div>
    <div style="background: rgba(255,255,255,0.05); border-radius: 50px; height: 8px;">
        <div style="width: {accuracy}%; height: 8px; border-radius: 50px;
            background: linear-gradient(90deg, {acc_color}, rgba(0,212,255,0.5));"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Chart ──────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
fig = go.Figure()

# Historical price (last 90 days for clarity)
hist_tail = df["Close"].tail(90)
fig.add_trace(go.Scatter(
    x=hist_tail.index, y=hist_tail,
    name="Historical Price",
    line=dict(color="rgba(148,163,184,0.7)", width=1.5),
    mode="lines",
))

# Test actual vs predicted
test_actual = result["test_actual"].tail(60)
test_pred = result["test_predicted"].tail(60)
fig.add_trace(go.Scatter(
    x=test_actual.index, y=test_actual,
    name="Actual (Test)",
    line=dict(color="#E8EAF6", width=2),
))
fig.add_trace(go.Scatter(
    x=test_pred.index, y=test_pred,
    name=f"Predicted (Test — {model_type})",
    line=dict(color="#00D4FF", width=2, dash="dot"),
))

# Future predictions
future_dates = result["future_dates"]
future_preds = result["future_predictions"]
if future_preds:
    # Connect from last historical point
    connect_x = [df.index[-1]] + future_dates
    connect_y = [df["Close"].iloc[-1]] + future_preds
    direction_color = "#48BB78" if future_preds[-1] > df["Close"].iloc[-1] else "#F56565"
    fig.add_trace(go.Scatter(
        x=connect_x, y=connect_y,
        name=f"Forecast ({forecast_days}d)",
        line=dict(color=direction_color, width=3, dash="solid"),
        mode="lines+markers",
        marker=dict(size=6, color=direction_color, line=dict(color="white", width=1)),
    ))

    # Confidence band (±10% of ATR-estimated uncertainty)
    std_est = df["Close"].tail(30).std() * 0.5
    upper_band = [p + std_est * (i + 1) ** 0.5 for i, p in enumerate(future_preds)]
    lower_band = [p - std_est * (i + 1) ** 0.5 for i, p in enumerate(future_preds)]
    fig.add_trace(go.Scatter(
        x=future_dates + future_dates[::-1],
        y=upper_band + lower_band[::-1],
        fill="toself",
        fillcolor=f"rgba({'72,187,120' if direction_color == '#48BB78' else '245,101,101'},0.08)",
        line=dict(color="rgba(255,255,255,0)"),
        showlegend=True,
        name="Confidence Band",
    ))

# Vertical line for today — convert Timestamp to string for plotly compatibility
today_str = df.index[-1].strftime('%Y-%m-%d')
fig.add_vline(x=today_str, line_dash="dash", line_color="rgba(0,212,255,0.4)", line_width=1.5,
              annotation_text="Today", annotation_position="top right",
              annotation_font_color="#00D4FF")

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#E8EAF6",
    height=500,
    margin=dict(t=30, b=20, l=10, r=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.01, bgcolor="rgba(0,0,0,0)", font_size=11),
    hovermode="x unified",
    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", tickprefix="$"),
)
st.plotly_chart(fig, use_container_width=True)

# ── Feature Importance ─────────────────────────────────────────────────────────
if result.get("feature_importance"):
    st.markdown("### 🔑 Top Predictive Features")
    fi = result["feature_importance"]
    fi_df = pd.DataFrame(list(fi.items()), columns=["Feature", "Importance"])
    fi_df = fi_df.sort_values("Importance", ascending=True)

    fig_fi = go.Figure(go.Bar(
        x=fi_df["Importance"], y=fi_df["Feature"],
        orientation="h",
        marker=dict(
            color=fi_df["Importance"],
            colorscale=[[0, "#0D1529"], [0.5, "#0080FF"], [1, "#00D4FF"]],
        ),
        text=[f"{v:.4f}" for v in fi_df["Importance"]],
        textposition="outside",
    ))
    fig_fi.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E8EAF6",
        height=350,
        margin=dict(t=10, b=20, l=10, r=60),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_fi, use_container_width=True)

# ── Prediction Table ───────────────────────────────────────────────────────────
if future_dates and future_preds:
    st.markdown("### 📅 Day-by-Day Forecast")
    pred_df = pd.DataFrame({
        "Date": [d.strftime("%Y-%m-%d (%a)") for d in future_dates],
        "Predicted Price": [f"${p:.2f}" for p in future_preds],
        "Change from Current": [f"{((p - current_price)/current_price)*100:+.2f}%" for p in future_preds],
    })
    st.dataframe(pred_df, use_container_width=True, hide_index=True)

st.caption("⚠️ ML predictions are for educational purposes only. Not financial advice.")
