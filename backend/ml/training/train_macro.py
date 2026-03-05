import os
import pickle
import json
import pandas as pd
from ..models.bayesian_macro import BayesianMacroStress


def train(data_path, registry_path, version="v1"):
    os.makedirs(registry_path, exist_ok=True)
    df = pd.read_csv(data_path)
    cols = ["fed_shock", "cpi_spike", "gdp_contraction", "liquidity_freeze"]
    X = df[cols].values

    model = BayesianMacroStress()
    model.fit(X)

    model_path = os.path.join(registry_path, f"macro_{version}.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    metadata = {
        "model": "bayesian_macro",
        "version": version,
        "posterior_mean": model.posterior_mean.tolist(),
    }
    with open(os.path.join(registry_path, "macro_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return metadata


if __name__ == "__main__":
    train("/app/sample_data/us_macro_scenarios.csv", "/app/backend/ml/registry", "v1")
