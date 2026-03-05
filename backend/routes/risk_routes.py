from flask import Blueprint, request, jsonify
from ..auth import auth_required, get_auth_context, role_required
from ..extensions import limiter
from ..tasks import run_risk_job


risk_bp = Blueprint("risk", __name__, url_prefix="/api/v1/risk")


@risk_bp.post("/run")
@auth_required
@role_required("admin", "analyst")
@limiter.limit("30/minute")
def run_risk():
    ctx = get_auth_context()
    tenant_id = ctx["tenant_id"]
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
@auth_required
def risk_task_status(task_id):
    result = run_risk_job.AsyncResult(task_id)
    if result.successful():
        return jsonify({"status": "completed", "result": result.result})
    if result.failed():
        return jsonify({"status": "failed", "error": str(result.result)}), 500
    return jsonify({"status": result.status})
