import os
import json
import torch
import numpy as np
import pandas as pd
from torch import nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import TimeSeriesSplit
from ..models.lstm_volatility import LSTMVolatilityModel
from ..features.feature_engineering import add_time_features


def build_sequences(df, feature_cols, target_col, window=30):
    X, y = [], []
    vals = df[feature_cols + [target_col]].values
    for i in range(window, len(vals)):
        X.append(vals[i - window : i, : len(feature_cols)])
        y.append(vals[i, len(feature_cols)])
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


def train(data_path, registry_path, version="v1"):
    os.makedirs(registry_path, exist_ok=True)
    df = pd.read_csv(data_path)
    df = add_time_features(df)
    feature_cols = ["return_1d", "return_5d", "rolling_vol_20", "rolling_mean_20"]
    target_col = "rolling_vol_20"
    X, y = build_sequences(df, feature_cols, target_col, window=30)

    tscv = TimeSeriesSplit(n_splits=3)
    cv_losses = []

    for train_idx, val_idx in tscv.split(X):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        model = LSTMVolatilityModel(input_size=len(feature_cols))
        opt = torch.optim.Adam(model.parameters(), lr=1e-3)
        loss_fn = nn.MSELoss()

        train_loader = DataLoader(TensorDataset(torch.tensor(X_train), torch.tensor(y_train).unsqueeze(1)), batch_size=64, shuffle=False)

        model.train()
        for _ in range(8):
            for xb, yb in train_loader:
                pred = model(xb)
                loss = loss_fn(pred, yb)
                opt.zero_grad()
                loss.backward()
                opt.step()

        model.eval()
        with torch.no_grad():
            val_pred = model(torch.tensor(X_val))
            val_loss = loss_fn(val_pred, torch.tensor(y_val).unsqueeze(1)).item()
            cv_losses.append(val_loss)

    final_model = model
    model_path = os.path.join(registry_path, f"volatility_{version}.pt")
    torch.save(final_model.state_dict(), model_path)

    metadata = {
        "model": "lstm_volatility",
        "version": version,
        "cv_mse_mean": float(np.mean(cv_losses)),
        "features": feature_cols,
    }
    with open(os.path.join(registry_path, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return metadata


if __name__ == "__main__":
    train("/app/sample_data/us_market_timeseries.csv", "/app/backend/ml/registry", "v1")
