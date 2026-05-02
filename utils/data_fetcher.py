import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st


@st.cache_data(ttl=300)
def get_stock_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Fetch OHLCV data for a given ticker."""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        if df.empty:
            return pd.DataFrame()
        df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize(None)
        return df
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_stock_info(ticker: str) -> dict:
    """Fetch company information for a given ticker."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info
    except Exception:
        return {}


@st.cache_data(ttl=60)
def get_market_indices() -> dict:
    """Fetch major market indices data."""
    indices = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "Dow Jones": "^DJI",
        "Russell 2000": "^RUT",
        "VIX": "^VIX",
        "FTSE 100": "^FTSE",
    }
    results = {}
    for name, symbol in indices.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if not hist.empty and len(hist) >= 2:
                current = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2]
                change = current - prev
                pct_change = (change / prev) * 100
                results[name] = {
                    "symbol": symbol,
                    "price": current,
                    "change": change,
                    "pct_change": pct_change,
                }
            elif not hist.empty:
                current = hist["Close"].iloc[-1]
                results[name] = {
                    "symbol": symbol,
                    "price": current,
                    "change": 0,
                    "pct_change": 0,
                }
        except Exception:
            pass
    return results


@st.cache_data(ttl=300)
def get_top_movers(tickers: list) -> pd.DataFrame:
    """Get top gainers and losers from a list of tickers."""
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            if not hist.empty and len(hist) >= 2:
                current = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2]
                pct_change = ((current - prev) / prev) * 100
                info = stock.info
                data.append({
                    "Ticker": ticker,
                    "Company": info.get("shortName", ticker),
                    "Price": current,
                    "Change %": pct_change,
                    "Volume": hist["Volume"].iloc[-1],
                })
        except Exception:
            pass
    if data:
        return pd.DataFrame(data).sort_values("Change %", ascending=False)
    return pd.DataFrame()


@st.cache_data(ttl=120)
def get_crypto_data(symbols: list) -> pd.DataFrame:
    """Fetch cryptocurrency data."""
    data = []
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            info = ticker.info
            if not hist.empty:
                current = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2] if len(hist) >= 2 else current
                pct_change = ((current - prev) / prev) * 100 if prev != 0 else 0
                data.append({
                    "Symbol": symbol.replace("-USD", ""),
                    "Name": info.get("shortName", symbol),
                    "Price": current,
                    "Change_24h": pct_change,
                    "Volume_24h": hist["Volume"].iloc[-1],
                    "Market_Cap": info.get("marketCap", 0),
                    "High_24h": hist["High"].iloc[-1],
                    "Low_24h": hist["Low"].iloc[-1],
                })
        except Exception:
            pass
    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def get_stock_news(ticker: str) -> list:
    """Fetch news for a given ticker."""
    try:
        import feedparser
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:15]:
            articles.append({
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
            })
        return articles
    except Exception:
        return []


@st.cache_data(ttl=300)
def get_multiple_stocks(tickers: list, period: str = "1y") -> dict:
    """Fetch data for multiple stocks at once."""
    data = {}
    for ticker in tickers:
        df = get_stock_data(ticker, period=period)
        if not df.empty:
            data[ticker] = df
    return data


def format_large_number(num: float) -> str:
    """Format large numbers with T/B/M suffixes."""
    if num is None or num == 0:
        return "N/A"
    if abs(num) >= 1e12:
        return f"${num/1e12:.2f}T"
    elif abs(num) >= 1e9:
        return f"${num/1e9:.2f}B"
    elif abs(num) >= 1e6:
        return f"${num/1e6:.2f}M"
    else:
        return f"${num:.2f}"
