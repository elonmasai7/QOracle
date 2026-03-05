import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, jwt_required
from ..auth import role_required
from ..extensions import limiter
from ..tasks import run_risk_job


risk_bp = Blueprint("risk", __name__, url_prefix="/api/v1/risk")


@risk_bp.post("/run")
@jwt_required()
@role_required("admin", "analyst")
@limiter.limit("30/minute")
def run_risk():
    claims = get_jwt()
    tenant_id = claims["tenant_id"]
    payload = request.get_json(force=True)

    portfolio_id = payload.get("portfolio_id")
    mode = payload.get("mode", "hybrid")
    paths = int(payload.get("paths", 10000))
    horizon_days = int(payload.get("horizon_days", 1))

    task = run_risk_job.delay(
        tenant_id=tenant_id,
        portfolio_id=portfolio_id,
        mode=mode,
        paths=paths,
        horizon_days=horizon_days,
    )
    return jsonify({"task_id": task.id}), 202


@risk_bp.get("/task/<task_id>")
@jwt_required()
def risk_task_status(task_id):
    result = run_risk_job.AsyncResult(task_id)
    if result.successful():
        return jsonify({"status": "completed", "result": result.result})
    if result.failed():
        return jsonify({"status": "failed", "error": str(result.result)}), 500
    return jsonify({"status": result.status})
