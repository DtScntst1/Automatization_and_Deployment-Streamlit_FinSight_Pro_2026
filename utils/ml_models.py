import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import TimeSeriesSplit


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create ML features from price data."""
    features = pd.DataFrame(index=df.index)
    features["Close"] = df["Close"]

    # Lag features
    for lag in [1, 2, 3, 5, 10, 20]:
        features[f"lag_{lag}"] = df["Close"].shift(lag)

    # Rolling stats
    for window in [5, 10, 20, 50]:
        features[f"sma_{window}"] = df["Close"].rolling(window).mean()
        features[f"std_{window}"] = df["Close"].rolling(window).std()
        features[f"max_{window}"] = df["Close"].rolling(window).max()
        features[f"min_{window}"] = df["Close"].rolling(window).min()

    # Returns
    features["return_1d"] = df["Close"].pct_change(1)
    features["return_5d"] = df["Close"].pct_change(5)
    features["return_10d"] = df["Close"].pct_change(10)

    # Volume features
    if "Volume" in df.columns:
        features["volume"] = df["Volume"]
        features["volume_ma_10"] = df["Volume"].rolling(10).mean()
        features["volume_ratio"] = df["Volume"] / df["Volume"].rolling(10).mean()

    # High/Low range
    if "High" in df.columns and "Low" in df.columns:
        features["hl_range"] = df["High"] - df["Low"]
        features["hl_ratio"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"] + 1e-9)

    # RSI
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).ewm(com=13, min_periods=14).mean()
    loss = (-delta.clip(upper=0)).ewm(com=13, min_periods=14).mean()
    rs = gain / (loss + 1e-9)
    features["rsi"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    features["macd"] = ema12 - ema26

    # Day of week, month (seasonality)
    features["day_of_week"] = pd.to_datetime(df.index).dayofweek
    features["month"] = pd.to_datetime(df.index).month

    features.dropna(inplace=True)
    return features


def train_and_predict(
    df: pd.DataFrame,
    forecast_days: int = 7,
    model_type: str = "RandomForest",
) -> dict:
    """
    Train ML model and predict future prices.
    Returns dict with predictions, metrics, and feature importance.
    """
    features_df = create_features(df)
    if len(features_df) < 60:
        return {"error": "Not enough data to train model (need at least 60 data points)."}

    X = features_df.drop(columns=["Close"])
    y = features_df["Close"]

    # Time-series split
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Select model
    if model_type == "Linear Regression":
        model = LinearRegression()
    elif model_type == "Gradient Boosting":
        model = GradientBoostingRegressor(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42)
    else:  # RandomForest (default)
        model = RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1)

    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred_test = model.predict(X_test_scaled)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    mae = mean_absolute_error(y_test, y_pred_test)
    r2 = r2_score(y_test, y_pred_test)
    mape = np.mean(np.abs((y_test.values - y_pred_test) / (y_test.values + 1e-9))) * 100

    # Future predictions (iterative)
    future_preds = []
    last_data = df.copy()

    for day in range(forecast_days):
        feat = create_features(last_data)
        if feat.empty:
            break
        last_feat = feat.drop(columns=["Close"]).iloc[[-1]]
        last_feat_scaled = scaler.transform(last_feat)
        pred_price = model.predict(last_feat_scaled)[0]
        future_preds.append(pred_price)

        # Append predicted row to last_data
        new_row = last_data.iloc[-1].copy()
        new_row["Close"] = pred_price
        new_row["Open"] = pred_price
        new_row["High"] = pred_price * 1.005
        new_row["Low"] = pred_price * 0.995
        new_row["Volume"] = last_data["Volume"].mean()
        next_date = last_data.index[-1] + pd.Timedelta(days=1)
        last_data = pd.concat([last_data, pd.DataFrame([new_row], index=[next_date])])

    # Feature importance (if available)
    feat_importance = {}
    if hasattr(model, "feature_importances_"):
        feat_names = X.columns.tolist()
        importances = model.feature_importances_
        feat_importance = dict(sorted(
            zip(feat_names, importances), key=lambda x: x[1], reverse=True
        )[:10])

    # Generate future dates (skip weekends)
    future_dates = []
    current_date = df.index[-1]
    added = 0
    while added < forecast_days:
        current_date += pd.Timedelta(days=1)
        if current_date.weekday() < 5:  # Mon-Fri
            future_dates.append(current_date)
            added += 1

    return {
        "model_type": model_type,
        "metrics": {"RMSE": rmse, "MAE": mae, "R²": r2, "MAPE": mape},
        "test_actual": y_test,
        "test_predicted": pd.Series(y_pred_test, index=y_test.index),
        "future_dates": future_dates,
        "future_predictions": future_preds,
        "feature_importance": feat_importance,
        "current_price": df["Close"].iloc[-1],
        "predicted_final": future_preds[-1] if future_preds else None,
    }
