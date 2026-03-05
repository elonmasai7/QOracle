from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required


webhook_bp = Blueprint("webhook", __name__, url_prefix="/api/v1/webhooks")


@webhook_bp.post("/risk-events")
@jwt_required()
def risk_events():
    payload = request.get_json(force=True)
    # Production implementation would fan-out to signed outbound webhook subscribers.
    return jsonify({"accepted": True, "event": payload.get("event", "unknown")}), 202
