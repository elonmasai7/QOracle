import os
import pickle
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from ..features.feature_engineering import create_credit_features
from ..models.credit_xgb import train_credit_model


def train(data_path, registry_path, version="v1"):
    os.makedirs(registry_path, exist_ok=True)
    df = pd.read_csv(data_path)
    df = create_credit_features(df)

    feature_cols = ["debt_to_equity", "current_ratio", "ebitda_volatility"]
    X = df[feature_cols].fillna(0)
    y = df["default_flag"]

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    model = train_credit_model(X_train, y_train, X_val, y_val)

    preds = model.predict(__import__("xgboost").DMatrix(X_val))
    auc = roc_auc_score(y_val, preds)

    model_path = os.path.join(registry_path, f"credit_{version}.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    metadata = {
        "model": "credit_xgboost",
        "version": version,
        "auc": float(auc),
        "features": feature_cols,
    }
    with open(os.path.join(registry_path, "credit_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return metadata


if __name__ == "__main__":
    train("/app/sample_data/us_sme_credit.csv", "/app/backend/ml/registry", "v1")
