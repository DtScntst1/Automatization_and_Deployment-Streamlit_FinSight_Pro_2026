import pandas as pd
import numpy as np


def calculate_sma(df: pd.DataFrame, window: int) -> pd.Series:
    """Simple Moving Average."""
    return df["Close"].rolling(window=window).mean()


def calculate_ema(df: pd.DataFrame, window: int) -> pd.Series:
    """Exponential Moving Average."""
    return df["Close"].ewm(span=window, adjust=False).mean()


def calculate_rsi(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Relative Strength Index (RSI)."""
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=window - 1, min_periods=window).mean()
    avg_loss = loss.ewm(com=window - 1, min_periods=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """MACD, Signal, and Histogram."""
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(
    df: pd.DataFrame, window: int = 20, num_std: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands: upper, middle (SMA), lower."""
    middle = df["Close"].rolling(window=window).mean()
    std = df["Close"].rolling(window=window).std()
    upper = middle + (num_std * std)
    lower = middle - (num_std * std)
    return upper, middle, lower


def calculate_atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Average True Range (ATR)."""
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.rolling(window=window).mean()


def calculate_stochastic(
    df: pd.DataFrame, k_window: int = 14, d_window: int = 3
) -> tuple[pd.Series, pd.Series]:
    """Stochastic Oscillator (%K and %D)."""
    lowest_low = df["Low"].rolling(window=k_window).min()
    highest_high = df["High"].rolling(window=k_window).max()
    k = 100 * ((df["Close"] - lowest_low) / (highest_high - lowest_low))
    d = k.rolling(window=d_window).mean()
    return k, d


def calculate_obv(df: pd.DataFrame) -> pd.Series:
    """On-Balance Volume (OBV)."""
    direction = df["Close"].diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    return (direction * df["Volume"]).cumsum()


def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Generate buy/sell signals based on technical indicators."""
    signals = pd.DataFrame(index=df.index)
    signals["Close"] = df["Close"]

    # RSI
    rsi = calculate_rsi(df)
    signals["RSI"] = rsi

    # MACD
    macd_line, signal_line, _ = calculate_macd(df)
    signals["MACD"] = macd_line
    signals["MACD_Signal"] = signal_line

    # SMA
    signals["SMA_20"] = calculate_sma(df, 20)
    signals["SMA_50"] = calculate_sma(df, 50)

    # Buy Signal: RSI < 30 AND MACD crosses above signal
    # Sell Signal: RSI > 70 AND MACD crosses below signal
    signals["Buy_Signal"] = (
        (rsi < 35) & (macd_line > signal_line)
    )
    signals["Sell_Signal"] = (
        (rsi > 65) & (macd_line < signal_line)
    )

    return signals


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add all technical indicators to the dataframe."""
    result = df.copy()
    result["SMA_20"] = calculate_sma(df, 20)
    result["SMA_50"] = calculate_sma(df, 50)
    result["SMA_200"] = calculate_sma(df, 200)
    result["EMA_12"] = calculate_ema(df, 12)
    result["EMA_26"] = calculate_ema(df, 26)
    result["RSI"] = calculate_rsi(df)
    macd, signal, hist = calculate_macd(df)
    result["MACD"] = macd
    result["MACD_Signal"] = signal
    result["MACD_Hist"] = hist
    bb_upper, bb_mid, bb_lower = calculate_bollinger_bands(df)
    result["BB_Upper"] = bb_upper
    result["BB_Mid"] = bb_mid
    result["BB_Lower"] = bb_lower
    result["ATR"] = calculate_atr(df)
    result["OBV"] = calculate_obv(df)
    k, d = calculate_stochastic(df)
    result["Stoch_K"] = k
    result["Stoch_D"] = d
    return result
