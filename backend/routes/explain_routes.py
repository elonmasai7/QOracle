from flask import Blueprint, current_app, jsonify, request
from ..auth import auth_required, role_required


explain_bp = Blueprint("explain", __name__, url_prefix="/api/v1/explain")


@explain_bp.post("/credit")
@auth_required
@role_required("admin", "analyst", "viewer")
def explain_credit_endpoint():
    from ..services.explainability import explain_credit

    payload = request.get_json(force=True)
    use_shap = bool(payload.get("use_shap", False))

    features = payload.get("features")
    if isinstance(features, dict):
        features = [
            features.get("debt_to_equity", 0.0),
            features.get("current_ratio", 0.0),
            features.get("ebitda_volatility", 0.0),
        ]
    if not isinstance(features, list):
        return jsonify({"error": "features_must_be_list_or_dict"}), 400

    out = explain_credit(
        features=features,
        registry_path=current_app.config["MODEL_REGISTRY_PATH"],
        version=payload.get("version", "v1"),
        use_shap=use_shap,
    )
    return jsonify(out)


@explain_bp.post("/credit/batch")
@auth_required
@role_required("admin", "analyst", "viewer")
def explain_credit_batch_endpoint():
    from ..services.explainability import explain_credit_batch

    payload = request.get_json(force=True)
    batch = payload.get("batch_features")
    if not isinstance(batch, list) or not batch:
        return jsonify({"error": "batch_features_must_be_non_empty_list"}), 400

    out = explain_credit_batch(
        batch_features=batch,
        registry_path=current_app.config["MODEL_REGISTRY_PATH"],
        version=payload.get("version", "v1"),
    )
    return jsonify(out)
