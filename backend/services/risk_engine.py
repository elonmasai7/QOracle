import numpy as np
from scipy.stats import norm


def cholesky_correlated_paths(mu, sigma, corr, n_assets, n_paths, horizon_days=1):
    dt = horizon_days / 252
    chol = np.linalg.cholesky(corr)
    z = np.random.normal(size=(n_paths, n_assets))
    correlated = z @ chol.T
    returns = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * correlated
    return returns


def jump_diffusion_paths(mu, sigma, lam, jump_mu, jump_sigma, n_assets, n_paths):
    base = cholesky_correlated_paths(mu, sigma, np.eye(n_assets), n_assets, n_paths)
    jumps = np.random.poisson(lam=lam, size=(n_paths, n_assets))
    jump_sizes = np.random.normal(jump_mu, jump_sigma, size=(n_paths, n_assets)) * jumps
    return base + jump_sizes


def compute_risk_metrics(weights, prices, returns):
    pnl = (returns @ (weights * prices))
    losses = -pnl
    var_95 = np.quantile(losses, 0.95)
    var_99 = np.quantile(losses, 0.99)
    cvar_95 = losses[losses >= var_95].mean()
    expected_shortfall = cvar_95

    liquidity_risk = np.clip(np.std(losses) / (np.mean(np.abs(prices)) + 1e-6), 0, 1)
    credit_risk = np.clip(norm.cdf((np.mean(losses) - np.median(losses)) / (np.std(losses) + 1e-6)), 0, 1)
    volatility_forecast = np.std(returns)

    return {
        "var_95": float(var_95),
        "var_99": float(var_99),
        "cvar_95": float(cvar_95),
        "expected_shortfall": float(expected_shortfall),
        "liquidity_risk": float(liquidity_risk),
        "credit_risk": float(credit_risk),
        "volatility_forecast": float(volatility_forecast),
    }


def macro_stress_test(base_returns, fed_shock=0.02, cpi_spike=0.03, gdp_contraction=-0.02, liquidity_freeze=0.4):
    shocked = base_returns.copy()
    shocked -= fed_shock * 0.15
    shocked -= cpi_spike * 0.20
    shocked += gdp_contraction * 0.35
    shocked -= liquidity_freeze * 0.10
    return shocked


def composite_score(metrics):
    norm_var = min(metrics["var_99"] / (metrics["var_99"] + 10000), 1)
    norm_cvar = min(metrics["cvar_95"] / (metrics["cvar_95"] + 10000), 1)
    norm_vol = min(metrics["volatility_forecast"] / 0.1, 1)
    norm_credit = metrics["credit_risk"]
    norm_liquidity = metrics["liquidity_risk"]
    score = 100 * (0.3 * norm_var + 0.25 * norm_cvar + 0.2 * norm_vol + 0.15 * norm_credit + 0.1 * norm_liquidity)
    return float(np.clip(score, 0, 100))


def hedge_recommendations(metrics):
    recs = []
    if metrics["var_99"] > 5000:
        recs.append("Increase index put option coverage for equity beta tail protection")
    if metrics["liquidity_risk"] > 0.5:
        recs.append("Shift 10-20% allocation into highly liquid Treasury ETFs")
    if metrics["credit_risk"] > 0.55:
        recs.append("Reduce lower-rated credit exposures; add CDS hedge where available")
    if metrics["volatility_forecast"] > 0.03:
        recs.append("Apply dynamic delta-hedging and short-dated volatility overlays")
    return recs or ["Maintain current hedge policy with weekly risk recalibration"]
