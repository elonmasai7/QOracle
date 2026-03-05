import json
import os
import pickle
import numpy as np
import xgboost as xgb


def _load_credit_model(registry_path: str, version: str):
    model_path = os.path.join(registry_path, f"credit_{version}.pkl")
    with open(model_path, "rb") as f:
        return pickle.load(f)


def _load_credit_feature_names(registry_path: str):
    meta_path = os.path.join(registry_path, "credit_metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f).get("features", ["debt_to_equity", "current_ratio", "ebitda_volatility"])
    return ["debt_to_equity", "current_ratio", "ebitda_volatility"]


def explain_credit(features, registry_path: str, version: str = "v1", use_shap: bool = False):
    model = _load_credit_model(registry_path, version)
    feature_names = _load_credit_feature_names(registry_path)

    arr = np.array(features, dtype=float).reshape(1, -1)
    dmat = xgb.DMatrix(arr, feature_names=feature_names[: arr.shape[1]])

    pred = float(model.predict(dmat)[0])
    contribs = model.predict(dmat, pred_contribs=True)[0]
    bias = float(contribs[-1])
    values = contribs[:-1]

    response = {
        "prediction_default_probability": pred,
        "bias": bias,
        "feature_contributions": {
            feature_names[i]: float(values[i]) for i in range(len(values))
        },
        "method": "xgboost_pred_contribs",
    }

    if use_shap:
        try:
            import shap

            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(arr)
            response["feature_contributions"] = {
                feature_names[i]: float(shap_values[0][i]) for i in range(arr.shape[1])
            }
            response["method"] = "shap_tree_explainer"
        except Exception:
            pass

    return response


def explain_credit_batch(batch_features, registry_path: str, version: str = "v1"):
    model = _load_credit_model(registry_path, version)
    feature_names = _load_credit_feature_names(registry_path)

    arr = np.array(batch_features, dtype=float)
    dmat = xgb.DMatrix(arr, feature_names=feature_names[: arr.shape[1]])
    contribs = model.predict(dmat, pred_contribs=True)[:, :-1]

    mean_abs = np.mean(np.abs(contribs), axis=0)
    ranking = sorted(
        [{"feature": feature_names[i], "mean_abs_contribution": float(v)} for i, v in enumerate(mean_abs)],
        key=lambda x: x["mean_abs_contribution"],
        reverse=True,
    )
    return {
        "global_feature_importance": ranking,
        "sample_count": int(arr.shape[0]),
        "method": "xgboost_pred_contribs",
    }
