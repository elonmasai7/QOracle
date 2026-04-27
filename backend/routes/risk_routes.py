import uuid
from flask import Blueprint, request, jsonify
from ..auth import auth_required, get_auth_context, role_required
from ..extensions import db
from ..extensions import limiter
from ..models import AnalysisRun, Portfolio, RiskResult
from ..services.platform_data import stress_scenario_catalog


risk_bp = Blueprint("risk", __name__, url_prefix="/api/v1/risk")


@risk_bp.post("/run")
@auth_required
@role_required("admin", "analyst")
@limiter.limit("30/minute")
def run_risk():
    from ..tasks import run_risk_job

    ctx = get_auth_context()
    tenant_id = ctx["tenant_id"]
    tenant_uuid = uuid.UUID(tenant_id)
    payload = request.get_json(force=True)

    portfolio_id = payload.get("portfolio_id")
    mode = payload.get("mode", "hybrid")
    paths = int(payload.get("paths", 10000))
    horizon_days = int(payload.get("horizon_days", 1))
    portfolio_uuid = uuid.UUID(str(portfolio_id))

    portfolio = Portfolio.query.filter_by(id=portfolio_uuid, tenant_id=tenant_uuid).first()
    if not portfolio:
        return jsonify({"error": "portfolio_not_found"}), 404

    analysis_run = AnalysisRun(
        tenant_id=tenant_uuid,
        portfolio_id=portfolio_uuid,
        status="queued",
        engine=mode,
        configuration={
            "paths": paths,
            "horizon_days": horizon_days,
        },
        summary={},
    )
    db.session.add(analysis_run)
    db.session.flush()

    task = run_risk_job.delay(
        tenant_id=tenant_id,
        portfolio_id=portfolio_id,
        analysis_run_id=str(analysis_run.id),
        mode=mode,
        paths=paths,
        horizon_days=horizon_days,
    )
    analysis_run.task_id = task.id
    db.session.commit()
    return jsonify({"task_id": task.id, "analysis_run_id": str(analysis_run.id), "status": analysis_run.status}), 202


@risk_bp.get("/task/<task_id>")
@auth_required
def risk_task_status(task_id):
    from ..tasks import run_risk_job

    result = run_risk_job.AsyncResult(task_id)
    if result.successful():
        return jsonify({"status": "completed", "result": result.result})
    if result.failed():
        return jsonify({"status": "failed", "error": str(result.result)}), 500
    return jsonify({"status": result.status})


@risk_bp.get("/runs")
@auth_required
def list_analysis_runs():
    ctx = get_auth_context()
    tenant_uuid = uuid.UUID(ctx["tenant_id"])

    rows = AnalysisRun.query.filter_by(tenant_id=tenant_uuid).order_by(AnalysisRun.created_at.desc()).all()
    return jsonify(
        [
            {
                "id": str(row.id),
                "portfolio_id": str(row.portfolio_id),
                "task_id": row.task_id,
                "status": row.status,
                "engine": row.engine,
                "runtime_ms": row.runtime_ms,
                "configuration": row.configuration,
                "summary": row.summary,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]
    )


@risk_bp.get("/results/<portfolio_id>/latest")
@auth_required
def latest_risk_result(portfolio_id):
    ctx = get_auth_context()
    tenant_uuid = uuid.UUID(ctx["tenant_id"])
    portfolio_uuid = uuid.UUID(portfolio_id)

    result = (
        RiskResult.query.filter_by(tenant_id=tenant_uuid, portfolio_id=portfolio_uuid)
        .order_by(RiskResult.created_at.desc())
        .first()
    )
    if not result:
        return jsonify({"error": "risk_result_not_found"}), 404

    return jsonify(
        {
            "portfolio_id": str(result.portfolio_id),
            "var_95": result.var_95,
            "var_99": result.var_99,
            "cvar_95": result.cvar_95,
            "expected_shortfall": result.expected_shortfall,
            "liquidity_risk": result.liquidity_risk,
            "credit_risk": result.credit_risk,
            "volatility_forecast": result.volatility_forecast,
            "composite_risk_score": result.composite_risk_score,
            "mode": result.mode,
            "simulation_paths": result.simulation_paths,
            "recommendations": result.recommendations,
            "created_at": result.created_at.isoformat(),
        }
    )


@risk_bp.get("/scenarios")
def list_scenarios():
    return jsonify(stress_scenario_catalog())
