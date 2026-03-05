import numpy as np
from backend.services.risk_engine import compute_risk_metrics, composite_score


def test_risk_metrics_shapes_and_bounds():
    weights = np.array([0.4, 0.6])
    prices = np.array([100.0, 200.0])
    returns = np.random.normal(0, 0.02, (5000, 2))

    metrics = compute_risk_metrics(weights, prices, returns)

    assert metrics["var_99"] >= metrics["var_95"]
    assert 0 <= metrics["liquidity_risk"] <= 1
    assert 0 <= metrics["credit_risk"] <= 1

    score = composite_score(metrics)
    assert 0 <= score <= 100
