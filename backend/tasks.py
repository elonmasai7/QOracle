import uuid
import numpy as np
import time
from celery import Celery
from flask import Flask
from .config import Config
from .extensions import db
from .models import AnalysisRun, Asset, RiskResult, StressResult, BillingRecord
from .services.risk_engine import (
    cholesky_correlated_paths,
    jump_diffusion_paths,
    compute_risk_metrics,
    macro_stress_test,
    composite_score,
    hedge_recommendations,
)
from .ml.pipeline import run_hybrid_ml_pipeline
from .quantum.hybrid_workflow import run_quantum_tail_workflow
from .services.audit import write_audit_log
from .services.webhook_dispatch import dispatch_event


celery = Celery(__name__)


def create_celery_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


create_celery_app()


@celery.task(bind=True, name="risk.run")
def run_risk_job(self, tenant_id, portfolio_id, analysis_run_id=None, mode="hybrid", paths=10000, horizon_days=1):
    started = time.time()
    tenant_uuid = uuid.UUID(tenant_id)
    portfolio_uuid = uuid.UUID(portfolio_id)
    analysis_run = (
        AnalysisRun.query.filter_by(id=uuid.UUID(str(analysis_run_id)), tenant_id=tenant_uuid).first()
        if analysis_run_id
        else None
    )
    if analysis_run:
        analysis_run.status = "running"
        db.session.commit()

    assets = Asset.query.filter_by(
        tenant_id=tenant_uuid, portfolio_id=portfolio_uuid
    ).all()
    if not assets:
        if analysis_run:
            analysis_run.status = "failed"
            analysis_run.summary = {"error": "No assets found"}
            db.session.commit()
        raise ValueError("No assets found")

    prices = np.array([a.price for a in assets])
    quantities = np.array([a.quantity for a in assets])
    weights = quantities / np.sum(quantities)

    n_assets = len(assets)
    mu = np.full(n_assets, 0.08)
    sigma = np.full(n_assets, 0.2)
    corr = np.full((n_assets, n_assets), 0.25)
    np.fill_diagonal(corr, 1.0)

    base_returns = cholesky_correlated_paths(mu, sigma, corr, n_assets, paths, horizon_days)
    jump_returns = jump_diffusion_paths(mu, sigma, lam=0.08, jump_mu=-0.02, jump_sigma=0.04, n_assets=n_assets, n_paths=paths)
    returns = 0.6 * base_returns + 0.4 * jump_returns

    metrics = compute_risk_metrics(weights, prices, returns)
    stress_returns = macro_stress_test(returns)
    stress_metrics = compute_risk_metrics(weights, prices, stress_returns)
    ml_forecast = run_hybrid_ml_pipeline(returns)
    metrics["volatility_forecast"] = ml_forecast.forecast_volatility
    metrics["liquidity_risk"] = ml_forecast.liquidity_stress

    losses = -(returns @ (weights * prices))
    threshold = metrics["var_99"]
    quantum = run_quantum_tail_workflow(losses, threshold, enabled=mode in {"hybrid", "quantum"})

    risk_score = composite_score(metrics)
    recs = hedge_recommendations(metrics)

    if analysis_run is None:
        analysis_run = AnalysisRun(
            tenant_id=tenant_uuid,
            portfolio_id=portfolio_uuid,
            task_id=self.request.id,
            status="completed",
            engine=mode,
            configuration={
                "paths": paths,
                "horizon_days": horizon_days,
                "confidence_interval": 0.99,
            },
            runtime_ms=0,
            summary={},
        )
        db.session.add(analysis_run)

    saved = RiskResult(
        tenant_id=tenant_uuid,
        portfolio_id=portfolio_uuid,
        var_95=metrics["var_95"],
        var_99=metrics["var_99"],
        cvar_95=metrics["cvar_95"],
        expected_shortfall=metrics["expected_shortfall"],
        liquidity_risk=metrics["liquidity_risk"],
        credit_risk=metrics["credit_risk"],
        volatility_forecast=metrics["volatility_forecast"],
        composite_risk_score=risk_score,
        mode="hybrid" if quantum and quantum["benchmark"]["quantum_mode_active"] else "classical",
        confidence_interval=0.99,
        simulation_paths=paths,
        recommendations=recs,
    )
    db.session.add(saved)

    scenario = StressResult(
        tenant_id=uuid.UUID(tenant_id),
        portfolio_id=uuid.UUID(portfolio_id),
        scenario="us_macro_baseline_shock",
        pnl_impact=-(stress_metrics["var_95"] - metrics["var_95"]),
        details={
            "fed_funds_shock": 0.02,
            "cpi_spike": 0.03,
            "gdp_contraction": -0.02,
            "liquidity_freeze": 0.40,
        },
    )
    db.session.add(scenario)

    if quantum:
        units = 1 if quantum["benchmark"]["quantum_mode_active"] else 0
        if units > 0:
            db.session.add(
                BillingRecord(
                    tenant_id=tenant_uuid,
                    usage_type="quantum_run",
                    units=units,
                    unit_price=5.0,
                    total=5.0 * units,
                )
            )

    db.session.commit()
    write_audit_log(tenant_id, "risk_run", "risk", {"portfolio_id": portfolio_id, "mode": mode})

    runtime_ms = int((time.time() - started) * 1000)
    analysis_run.status = "completed"
    analysis_run.runtime_ms = runtime_ms
    analysis_run.summary = {
        "composite_risk_score": risk_score,
        "hedge_recommendations": recs,
        "result_id": str(saved.id),
    }
    db.session.commit()
    dispatch_event(
        uuid.UUID(tenant_id),
        "risk.completed",
        {
            "event": "risk.completed",
            "portfolio_id": portfolio_id,
            "metrics": metrics,
            "stress_metrics": stress_metrics,
            "composite_risk_score": risk_score,
            "forecast": {
                "volatility": ml_forecast.forecast_volatility,
                "liquidity_stress": ml_forecast.liquidity_stress,
            },
            "runtime_ms": runtime_ms,
        },
    )
    return {
        "portfolio_id": portfolio_id,
        "metrics": metrics,
        "stress_metrics": stress_metrics,
        "composite_risk_score": risk_score,
        "hedge_recommendations": recs,
        "quantum": quantum,
        "forecast": {
            "volatility": ml_forecast.forecast_volatility,
            "liquidity_stress": ml_forecast.liquidity_stress,
            "factors": ml_forecast.factor_contributions,
        },
        "runtime_ms": runtime_ms,
    }
