import streamlit as st

st.set_page_config(
    page_title="FinSight Pro | AI Market Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.stApp { background: linear-gradient(135deg, #0A0E1A 0%, #0D1529 50%, #0A0E1A 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0D1529 0%, #111827 100%); border-right: 1px solid rgba(0,212,255,0.15); }
[data-testid="stMetric"] { background: rgba(255,255,255,0.03); border: 1px solid rgba(0,212,255,0.15); border-radius: 12px; padding: 1rem; transition: transform 0.2s ease; }
[data-testid="stMetric"]:hover { transform: translateY(-2px); border-color: rgba(0,212,255,0.4); }
.stSelectbox > div > div { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(0,212,255,0.2) !important; border-radius: 8px !important; }
.stTextInput > div > div > input { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(0,212,255,0.2) !important; border-radius: 8px !important; color: #E8EAF6 !important; }
.stButton > button { background: linear-gradient(135deg, #00D4FF, #0080FF) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; transition: all 0.2s ease !important; box-shadow: 0 4px 15px rgba(0,212,255,0.3) !important; }
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(0,212,255,0.5) !important; }
.stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.03); border-radius: 10px; padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; color: #94A3B8; font-weight: 500; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(0,128,255,0.15)) !important; color: #00D4FF !important; border: 1px solid rgba(0,212,255,0.3) !important; }
hr { border-color: rgba(0,212,255,0.1); }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #0A0E1A; } ::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.3); border-radius: 3px; } ::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,0.5); }
</style>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.html("""
<div style="text-align:center;padding:4rem 2rem;background:radial-gradient(ellipse at 50% 0%,rgba(0,212,255,0.12) 0%,transparent 70%);border-radius:20px;margin-bottom:2rem;border:1px solid rgba(0,212,255,0.08);">
  <div style="display:inline-block;background:linear-gradient(135deg,rgba(0,212,255,0.15),rgba(0,128,255,0.15));border:1px solid rgba(0,212,255,0.3);border-radius:50px;padding:0.3rem 1.2rem;font-size:0.8rem;font-weight:600;color:#00D4FF;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:1.5rem;">🤖 AI-Powered &bull; Real-Time Data &bull; ML Predictions</div>
  <h1 style="font-size:4rem;font-weight:800;background:linear-gradient(135deg,#FFFFFF 0%,#00D4FF 50%,#0080FF 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0.5rem 0;line-height:1.1;">FinSight Pro</h1>
  <p style="font-size:1.3rem;color:#94A3B8;margin:1rem auto;max-width:600px;font-weight:300;line-height:1.6;">Your intelligent companion for market analysis, AI price predictions, and portfolio management &mdash; all in one dashboard.</p>
  <div style="display:flex;justify-content:center;gap:1.5rem;margin-top:2rem;flex-wrap:wrap;">
    <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(0,212,255,0.15);border-radius:10px;padding:0.8rem 1.5rem;color:#94A3B8;font-size:0.9rem;">&#128202; 6 Analysis Modules</div>
    <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(0,212,255,0.15);border-radius:10px;padding:0.8rem 1.5rem;color:#94A3B8;font-size:0.9rem;">&#129302; 3 ML Models</div>
    <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(0,212,255,0.15);border-radius:10px;padding:0.8rem 1.5rem;color:#94A3B8;font-size:0.9rem;">&#9889; Real-Time Data</div>
    <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(0,212,255,0.15);border-radius:10px;padding:0.8rem 1.5rem;color:#94A3B8;font-size:0.9rem;">&#8383; Crypto Support</div>
  </div>
</div>
""")

# ── Feature Cards ──────────────────────────────────────────────────────────────
pages = [
    ("📊", "Market Overview", "Real-time global indices, top gainers/losers, and interactive market heat map."),
    ("🔍", "Stock Deep Dive", "Full candlestick charts with RSI, MACD, Bollinger Bands & automated buy/sell signals."),
    ("🤖", "AI Price Predictor", "Random Forest, Gradient Boosting & Linear Regression models for price forecasting."),
    ("₿", "Crypto Tracker", "Live cryptocurrency prices, market caps, 24h performance & historical comparison."),
    ("📰", "Market Sentiment", "NLP-powered news sentiment analysis using TextBlob for any stock or crypto."),
    ("💼", "Portfolio Manager", "Build, track and analyze your portfolio with risk/return metrics and P&L tracking."),
]

cols = st.columns(3)
for i, (icon, name, desc) in enumerate(pages):
    with cols[i % 3]:
        st.html(f"""
        <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(0,212,255,0.12);border-radius:16px;padding:1.8rem;min-height:160px;display:flex;flex-direction:column;justify-content:space-between;margin-bottom:1rem;position:relative;overflow:hidden;">
          <div style="position:absolute;top:0;right:0;width:100px;height:100px;background:radial-gradient(circle,rgba(0,212,255,0.06) 0%,transparent 70%);border-radius:50%;"></div>
          <div>
            <div style="font-size:2rem;margin-bottom:0.5rem;">{icon}</div>
            <div style="font-size:1.1rem;font-weight:700;color:#E8EAF6;margin-bottom:0.4rem;">{name}</div>
            <div style="font-size:0.85rem;color:#64748B;line-height:1.5;">{desc}</div>
          </div>
          <div style="font-size:0.75rem;color:#00D4FF;font-weight:600;letter-spacing:0.05em;margin-top:1rem;">Navigate from sidebar &rarr;</div>
        </div>
        """)

# ── Quick Stats ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.html("""
<div style="background:rgba(0,212,255,0.04);border:1px solid rgba(0,212,255,0.12);border-radius:16px;padding:1.5rem 2rem;margin-bottom:2rem;">
  <h3 style="color:#00D4FF;margin:0 0 1rem;font-size:1rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;">&#9889; Quick Start Guide</h3>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;">
    <div>
      <div style="color:#E8EAF6;font-weight:600;margin-bottom:0.3rem;">1. Pick a Module</div>
      <div style="color:#64748B;font-size:0.88rem;">Select any analysis module from the left sidebar to get started.</div>
    </div>
    <div>
      <div style="color:#E8EAF6;font-weight:600;margin-bottom:0.3rem;">2. Enter a Ticker</div>
      <div style="color:#64748B;font-size:0.88rem;">Type any stock (AAPL, TSLA) or crypto (BTC-USD) ticker symbol.</div>
    </div>
    <div>
      <div style="color:#E8EAF6;font-weight:600;margin-bottom:0.3rem;">3. Explore Insights</div>
      <div style="color:#64748B;font-size:0.88rem;">Get real-time charts, ML predictions, sentiment scores and more.</div>
    </div>
  </div>
</div>
""")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.html("""
<div style="text-align:center;padding:2rem;border-top:1px solid rgba(0,212,255,0.1);color:#475569;font-size:0.85rem;">
  <div style="margin-bottom:0.5rem;">Built with &#10084;&#65039; using <strong style="color:#00D4FF">Streamlit</strong> &amp; <strong style="color:#00D4FF">Python</strong> | Data powered by <strong style="color:#00D4FF">Yahoo Finance</strong></div>
  <div>&#9888;&#65039; <em>This tool is for educational purposes only. Not financial advice.</em></div>
</div>
""")
