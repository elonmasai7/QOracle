# Risk Model Mathematics

## 1. Monte Carlo VaR/CVaR
Portfolio PnL path: `PnL = r^T (w .* p)`.
Loss `L = -PnL`.
- `VaR_alpha = Quantile_alpha(L)` at alpha = 0.95 and 0.99.
- `CVaR_alpha = E[L | L >= VaR_alpha]`.
- Expected Shortfall equals CVaR in this implementation.

## 2. Correlated GBM + Jump Diffusion
`r = (mu - 0.5 sigma^2) dt + sigma sqrt(dt) Z_corr + J`
- `Z_corr = Z * Chol(Corr)`
- Jump term `J` sampled from Poisson jump count and Gaussian jump sizes.

## 3. LSTM Volatility Forecast
Sequence-to-one model predicts future realized volatility from rolling return features over 30-90 day windows.

## 4. Credit Risk (XGBoost)
Default probability `p(default|x)` trained on SME ratios:
- debt-to-equity
- current ratio
- EBITDA volatility

## 5. Bayesian Macro Stress
Scenario vector `s = [fed, cpi, gdp, liquidity]` sampled from posterior multivariate normal calibrated on historical shocks.

## 6. Composite Risk Score
`Score = 100 * (0.30*VaR_n + 0.25*CVaR_n + 0.20*Vol_n + 0.15*Credit_n + 0.10*Liquidity_n)`
with each normalized term in `[0,1]`.
