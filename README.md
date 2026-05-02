# FinSight Pro — AI-Powered Market Intelligence Dashboard

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-F7931E?logo=scikit-learn&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**A premium, AI-powered financial dashboard built with Streamlit — featuring real-time market data, machine learning price predictions, technical analysis, crypto tracking, NLP sentiment analysis, and portfolio management.**

</div>

---

## 🚀 Features

### 📊 Market Overview
- Real-time global market indices (S&P 500, NASDAQ, Dow Jones, FTSE 100, VIX)
- Top gainers and losers from S&P 500 sample
- Interactive market heat map (treemap)

### 🔍 Stock Deep Dive
- Advanced candlestick charts (OHLCV)
- Technical indicators: **RSI, MACD, Bollinger Bands, SMA, EMA**
- Automated **Buy/Sell signal** generation
- Company financials: Market Cap, P/E, 52-week range, Dividend Yield

### 🤖 AI Price Predictor
- Three ML models: **Random Forest, Gradient Boosting, Linear Regression**
- 7, 14, or 30-day forecast horizon
- Engineered features: lag prices, rolling stats, RSI, MACD, volume ratios
- Confidence bands, R² score, RMSE, MAE metrics
- Feature importance visualization
- Day-by-day prediction table

### ₿ Crypto Tracker
- Live prices for 15+ cryptocurrencies
- 24h change, market cap, volume
- Normalized historical performance comparison
- Multi-select crypto comparison

### 📰 Market Sentiment
- Yahoo Finance RSS news feed
- **TextBlob NLP** sentiment analysis (Positive / Negative / Neutral)
- Polarity & subjectivity metrics
- Pie, histogram, and scatter visualizations
- Clickable styled news cards

### 💼 Portfolio Manager
- Add/remove/update holdings (persisted in session)
- Real-time P&L tracking
- Portfolio allocation (by stock & sector)
- Historical performance comparison
- Risk analysis: Volatility, Sharpe Ratio, Max Drawdown
- Risk-Return scatter plot
- CSV export

---

## 🛠️ Tech Stack

| Library | Purpose |
|---|---|
| `streamlit` | Web framework |
| `yfinance` | Real-time market data |
| `plotly` | Interactive charts |
| `scikit-learn` | ML models (RF, GB, LR) |
| `textblob` | NLP sentiment analysis |
| `feedparser` | RSS news parsing |
| `pandas / numpy` | Data processing |
| `ta` | Technical analysis indicators |

---

## ⚙️ Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/DtScntst1/FinSight_Pro.git
cd FinSight_Pro

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download TextBlob corpora (for sentiment analysis)
python -m textblob.download_corpora

# 5. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📁 Project Structure

```
FinSight_Pro/
├── app.py                        # 🏠 Home page
├── requirements.txt              # 📦 Dependencies
├── README.md                     # 📖 Documentation
├── .streamlit/
│   └── config.toml               # 🎨 Theme configuration
├── pages/
│   ├── 1_Market_Overview.py      # 📊 Global market overview
│   ├── 2_Stock_Deep_Dive.py      # 🔍 Technical analysis
│   ├── 3_AI_Price_Predictor.py   # 🤖 ML price prediction
│   ├── 4_Crypto_Tracker.py       # ₿  Crypto markets
│   ├── 5_Market_Sentiment.py     # 📰 NLP news sentiment
│   └── 6_Portfolio_Manager.py    # 💼 Portfolio tracking
└── utils/
    ├── data_fetcher.py           # 📡 Data fetching (yfinance)
    ├── technical_indicators.py   # 📐 RSI, MACD, BB, etc.
    └── ml_models.py              # 🧠 ML training & prediction
```

---

## 📸 Screenshots

> Navigate through 6 powerful modules from the sidebar.

---

## ⚠️ Disclaimer

This application is built for **educational purposes only**. The information and predictions provided do not constitute financial advice. Always do your own research before making investment decisions.

---

## 👤 Author

**Mahsun Yalçın**
- GitHub: [@DtScntst1](https://github.com/DtScntst1)
- LinkedIn: [mahsun-yalçın](https://www.linkedin.com/in/mahsun-yal%C3%A7%C4%B1n-103467296/)

---

## 📄 License

MIT License — feel free to use and adapt this project.
