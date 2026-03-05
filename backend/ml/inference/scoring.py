import os
import pickle
import torch
import numpy as np
from ..models.lstm_volatility import LSTMVolatilityModel


def score_volatility(sequence, registry_path, version="v1"):
    model_path = os.path.join(registry_path, f"volatility_{version}.pt")
    model = LSTMVolatilityModel(input_size=sequence.shape[-1])
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()
    with torch.no_grad():
        pred = model(torch.tensor(sequence, dtype=torch.float32)).item()
    return float(max(pred, 0))


def score_credit(features, registry_path, version="v1"):
    model_path = os.path.join(registry_path, f"credit_{version}.pkl")
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    dmat = __import__("xgboost").DMatrix(np.array(features).reshape(1, -1))
    return float(model.predict(dmat)[0])
