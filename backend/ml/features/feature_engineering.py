import pandas as pd


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["return_1d"] = out["close"].pct_change().fillna(0)
    out["return_5d"] = out["close"].pct_change(5).fillna(0)
    out["rolling_vol_20"] = out["return_1d"].rolling(20).std().fillna(0)
    out["rolling_mean_20"] = out["return_1d"].rolling(20).mean().fillna(0)
    return out


def create_credit_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["debt_to_equity"] = out["total_debt"] / (out["total_equity"] + 1e-6)
    out["current_ratio"] = out["current_assets"] / (out["current_liabilities"] + 1e-6)
    out["ebitda_volatility"] = out["ebitda"].rolling(4).std().fillna(out["ebitda"].std())
    return out
