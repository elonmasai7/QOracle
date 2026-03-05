import uuid
import numpy as np
import time
from celery import Celery
from flask import Flask
from .config import Config
from .extensions import db
from .models import Asset, RiskResult, StressResult, BillingRecord
from .services.risk_engine import (
    cholesky_correlated_paths,
    jump_diffusion_paths,
    compute_risk_metrics,
    macro_stress_test,
    composite_score,
    hedge_recommendations,
)
from .quantum.hybrid_runner import run_hybrid_benchmark
from .services.audit import write_audit_log


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
def run_risk_job(self, tenant_id, portfolio_id, mode="hybrid", paths=10000, horizon_days=1):
    started = time.time()
    assets = Asset.query.filter_by(
        tenant_id=uuid.UUID(tenant_id), portfolio_id=uuid.UUID(portfolio_id)
    ).all()
    if not assets:
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

    losses = -(returns @ (weights * prices))
    threshold = metrics["var_99"]
    quantum = run_hybrid_benchmark(losses, threshold) if mode in {"hybrid", "quantum"} else None

    risk_score = composite_score(metrics)
    recs = hedge_recommendations(metrics)

    saved = RiskResult(
        tenant_id=uuid.UUID(tenant_id),
        portfolio_id=uuid.UUID(portfolio_id),
        var_95=metrics["var_95"],
        var_99=metrics["var_99"],
        cvar_95=metrics["cvar_95"],
        expected_shortfall=metrics["expected_shortfall"],
        liquidity_risk=metrics["liquidity_risk"],
        credit_risk=metrics["credit_risk"],
        volatility_forecast=metrics["volatility_forecast"],
        composite_risk_score=risk_score,
        mode="hybrid" if quantum and quantum["benchmark"]["quantum_mode_active"] else "classical",
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
                    tenant_id=uuid.UUID(tenant_id),
                    usage_type="quantum_run",
                    units=units,
                    unit_price=5.0,
                    total=5.0 * units,
                )
            )

    db.session.commit()
    write_audit_log(tenant_id, "risk_run", "risk", {"portfolio_id": portfolio_id, "mode": mode})

    runtime_ms = int((time.time() - started) * 1000)
    return {
        "portfolio_id": portfolio_id,
        "metrics": metrics,
        "stress_metrics": stress_metrics,
        "composite_risk_score": risk_score,
        "hedge_recommendations": recs,
        "quantum": quantum,
        "runtime_ms": runtime_ms,
    }
