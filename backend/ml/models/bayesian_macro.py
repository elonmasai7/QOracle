import numpy as np


class BayesianMacroStress:
    def __init__(self):
        self.posterior_mean = np.array([0.02, 0.03, -0.02, 0.4])
        self.posterior_cov = np.diag([0.01, 0.01, 0.01, 0.02])

    def fit(self, X):
        self.posterior_mean = np.mean(X, axis=0)
        self.posterior_cov = np.cov(X.T) + np.eye(X.shape[1]) * 1e-5

    def sample_scenario(self, n_samples=100):
        return np.random.multivariate_normal(self.posterior_mean, self.posterior_cov, n_samples)
