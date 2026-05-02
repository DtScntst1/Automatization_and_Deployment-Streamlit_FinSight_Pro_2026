import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import sys, os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_fetcher import get_stock_news, get_stock_info

st.set_page_config(page_title="Market Sentiment | FinSight Pro", page_icon="📰", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header {visibility: hidden;}
.stApp { background: linear-gradient(135deg, #0A0E1A 0%, #0D1529 50%, #0A0E1A 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0D1529 0%, #111827 100%); border-right: 1px solid rgba(0,212,255,0.15); }
.stButton > button { background: linear-gradient(135deg, #00D4FF, #0080FF) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #0A0E1A; } ::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="padding: 1.5rem 0; border-bottom: 1px solid rgba(0,212,255,0.1); margin-bottom: 2rem;">
    <h1 style="margin:0; font-size:2.2rem; font-weight:800;
        background: linear-gradient(135deg,#FFFFFF,#00D4FF);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
        📰 Market Sentiment
    </h1>
    <p style="color:#64748B; margin:0.3rem 0 0; font-size:0.95rem;">
        NLP-powered news sentiment analysis for stocks and cryptocurrencies
    </p>
</div>
""", unsafe_allow_html=True)

# ── TextBlob sentiment (with fallback) ────────────────────────────────────────
def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment using TextBlob."""
    try:
        from textblob import TextBlob
        blob = TextBlob(str(text))
        polarity = blob.sentiment.polarity        # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        if polarity > 0.1:
            label = "Positive"
            color = "#48BB78"
            emoji = "🟢"
        elif polarity < -0.1:
            label = "Negative"
            color = "#F56565"
            emoji = "🔴"
        else:
            label = "Neutral"
            color = "#F6AD55"
            emoji = "🟡"
        return {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "label": label,
            "color": color,
            "emoji": emoji,
        }
    except Exception:
        return {"polarity": 0, "subjectivity": 0.5, "label": "Neutral", "color": "#F6AD55", "emoji": "🟡"}

# ── Controls ───────────────────────────────────────────────────────────────────
col1, col2, _ = st.columns([3, 2, 2])
with col1:
    ticker = st.text_input("Stock / Crypto Ticker", value="AAPL", placeholder="e.g. AAPL, BTC-USD, TSLA").upper().strip()
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("Analyze Sentiment 📊")

if not ticker:
    st.info("Enter a ticker to analyze market sentiment.")
    st.stop()

# ── Fetch News ─────────────────────────────────────────────────────────────────
info = get_stock_info(ticker)
company_name = info.get("shortName", ticker)

with st.spinner(f"Fetching latest news for {ticker}..."):
    articles = get_stock_news(ticker)

if not articles:
    st.warning(f"No news articles found for '{ticker}'. Try a different ticker (e.g. AAPL, TSLA, MSFT).")
    st.stop()

# ── Sentiment Analysis ─────────────────────────────────────────────────────────
try:
    import textblob
    textblob_available = True
except ImportError:
    textblob_available = False
    st.info("💡 Install `textblob` for full sentiment analysis: `pip install textblob`")

sentiments = []
for article in articles:
    text = f"{article['title']} {article.get('summary', '')}"
    sentiment = analyze_sentiment(text)
    sentiments.append({
        **article,
        **sentiment,
    })

sent_df = pd.DataFrame(sentiments)

# ── Overall Sentiment Summary ──────────────────────────────────────────────────
st.markdown(f"### 🎯 Sentiment Overview — {company_name} ({ticker})")

pos_count = len(sent_df[sent_df["label"] == "Positive"])
neg_count = len(sent_df[sent_df["label"] == "Negative"])
neu_count = len(sent_df[sent_df["label"] == "Neutral"])
avg_polarity = sent_df["polarity"].mean()
avg_subjectivity = sent_df["subjectivity"].mean()
total = len(sent_df)

overall_label = "Positive 🟢" if avg_polarity > 0.05 else ("Negative 🔴" if avg_polarity < -0.05 else "Neutral 🟡")
overall_color = "#48BB78" if avg_polarity > 0.05 else ("#F56565" if avg_polarity < -0.05 else "#F6AD55")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(0,212,255,0.15); border-radius:12px; padding:1.2rem; text-align:center;">
        <div style="font-size:0.8rem; color:#64748B;">Overall Sentiment</div>
        <div style="font-size:1.5rem; font-weight:800; color:{overall_color}; margin-top:0.3rem;">{overall_label}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(72,187,120,0.2); border-radius:12px; padding:1.2rem; text-align:center;">
        <div style="font-size:0.8rem; color:#64748B;">Positive Articles</div>
        <div style="font-size:1.8rem; font-weight:800; color:#48BB78; margin-top:0.3rem;">{pos_count}</div>
        <div style="font-size:0.75rem; color:#64748B;">{pos_count/total*100:.0f}% of total</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(245,101,101,0.2); border-radius:12px; padding:1.2rem; text-align:center;">
        <div style="font-size:0.8rem; color:#64748B;">Negative Articles</div>
        <div style="font-size:1.8rem; font-weight:800; color:#F56565; margin-top:0.3rem;">{neg_count}</div>
        <div style="font-size:0.75rem; color:#64748B;">{neg_count/total*100:.0f}% of total</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(246,173,85,0.2); border-radius:12px; padding:1.2rem; text-align:center;">
        <div style="font-size:0.8rem; color:#64748B;">Avg. Polarity</div>
        <div style="font-size:1.8rem; font-weight:800; color:{overall_color}; margin-top:0.3rem;">{avg_polarity:+.2f}</div>
        <div style="font-size:0.75rem; color:#64748B;">Range: -1 to +1</div>
    </div>
    """, unsafe_allow_html=True)
with col5:
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(0,212,255,0.15); border-radius:12px; padding:1.2rem; text-align:center;">
        <div style="font-size:0.8rem; color:#64748B;">Subjectivity</div>
        <div style="font-size:1.8rem; font-weight:800; color:#00D4FF; margin-top:0.3rem;">{avg_subjectivity:.2f}</div>
        <div style="font-size:0.75rem; color:#64748B;">0=Objective, 1=Subjective</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Sentiment Distribution Charts ─────────────────────────────────────────────
col_pie, col_hist = st.columns([1, 2])

with col_pie:
    st.markdown("#### Distribution")
    fig_pie = go.Figure(go.Pie(
        labels=["Positive", "Negative", "Neutral"],
        values=[pos_count, neg_count, neu_count],
        hole=0.6,
        marker_colors=["#48BB78", "#F56565", "#F6AD55"],
        textinfo="label+percent",
        hovertemplate="%{label}: %{value} articles<extra></extra>",
    ))
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#E8EAF6",
        showlegend=False,
        height=280,
        margin=dict(t=10, b=10, l=10, r=10),
        annotations=[dict(text=f"<b>{total}</b><br>Articles", x=0.5, y=0.5,
                          font_size=16, font_color="#E8EAF6", showarrow=False)],
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_hist:
    st.markdown("#### Polarity Distribution")
    fig_hist = go.Figure(go.Histogram(
        x=sent_df["polarity"],
        nbinsx=20,
        marker=dict(
            color=sent_df["polarity"],
            colorscale=[[0, "#F56565"], [0.5, "#F6AD55"], [1, "#48BB78"]],
            line=dict(color="rgba(0,0,0,0.3)", width=0.5),
        ),
        hovertemplate="Polarity: %{x:.2f}<br>Count: %{y}<extra></extra>",
    ))
    fig_hist.add_vline(x=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
    fig_hist.add_vline(x=avg_polarity, line_dash="solid", line_color=overall_color,
                       annotation_text=f"Mean: {avg_polarity:+.2f}", annotation_position="top right",
                       annotation_font_color=overall_color)
    fig_hist.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E8EAF6",
        height=280,
        margin=dict(t=10, b=20, l=10, r=10),
        xaxis=dict(title="Polarity Score", showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(title="Count", showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
        showlegend=False,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ── Polarity Scatter ───────────────────────────────────────────────────────────
st.markdown("#### 🎯 Sentiment Scatter — Polarity vs Subjectivity")
fig_scat = go.Figure()
for label, color in [("Positive", "#48BB78"), ("Negative", "#F56565"), ("Neutral", "#F6AD55")]:
    mask = sent_df["label"] == label
    if mask.any():
        subset = sent_df[mask]
        fig_scat.add_trace(go.Scatter(
            x=subset["polarity"],
            y=subset["subjectivity"],
            mode="markers+text",
            name=label,
            text=[t[:35] + "..." if len(t) > 35 else t for t in subset["title"]],
            textposition="top center",
            textfont=dict(size=8, color="rgba(255,255,255,0.4)"),
            marker=dict(size=14, color=color, opacity=0.8, line=dict(color="white", width=1)),
            hovertemplate="<b>%{text}</b><br>Polarity: %{x:.2f}<br>Subjectivity: %{y:.2f}<extra></extra>",
        ))
fig_scat.add_vline(x=0, line_dash="dash", line_color="rgba(255,255,255,0.15)")
fig_scat.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#E8EAF6",
    height=380,
    margin=dict(t=30, b=20, l=10, r=10),
    xaxis=dict(title="Polarity (Negative ← → Positive)", showgrid=True, gridcolor="rgba(255,255,255,0.04)", zeroline=False),
    yaxis=dict(title="Subjectivity (Objective ← → Subjective)", showgrid=True, gridcolor="rgba(255,255,255,0.04)"),
    legend=dict(orientation="h", yanchor="bottom", y=1.01, bgcolor="rgba(0,0,0,0)"),
)
st.plotly_chart(fig_scat, use_container_width=True)

# ── News Articles ──────────────────────────────────────────────────────────────
st.markdown("### 📰 Latest News Articles")
filter_label = st.selectbox("Filter by sentiment", ["All", "Positive", "Negative", "Neutral"])
filtered = sent_df if filter_label == "All" else sent_df[sent_df["label"] == filter_label]

for _, row in filtered.iterrows():
    border_color = row["color"]
    st.markdown(f"""
    <a href="{row.get('link', '#')}" target="_blank" style="text-decoration: none;">
    <div style="
        background: rgba(255,255,255,0.02);
        border: 1px solid {border_color}40;
        border-left: 3px solid {border_color};
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        cursor: pointer;
        transition: all 0.2s ease;
    " onmouseover="this.style.background='rgba(255,255,255,0.04)'" onmouseout="this.style.background='rgba(255,255,255,0.02)'">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:1rem;">
            <div style="font-size:0.95rem; font-weight:600; color:#E8EAF6; line-height:1.4;">
                {row['title']}
            </div>
            <div style="
                background: {border_color}20;
                border: 1px solid {border_color}60;
                border-radius: 6px;
                padding: 2px 10px;
                font-size:0.78rem;
                font-weight:600;
                color:{border_color};
                white-space: nowrap;
                flex-shrink: 0;
            ">{row['emoji']} {row['label']}</div>
        </div>
        <div style="font-size:0.8rem; color:#475569; margin-top:0.5rem;">
            Polarity: <span style="color:{border_color}">{row['polarity']:+.2f}</span> •
            Subjectivity: {row['subjectivity']:.2f} •
            <span style="color:#00D4FF;">Read more →</span>
        </div>
    </div>
    </a>
    """, unsafe_allow_html=True)

st.caption("⚠️ Sentiment analysis powered by TextBlob NLP. For educational purposes only.")
