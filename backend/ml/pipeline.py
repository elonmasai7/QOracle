from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class PipelineForecast:
    forecast_volatility: float
    liquidity_stress: float
    factor_contributions: list[dict[str, Any]]


def run_hybrid_ml_pipeline(feature_frame: np.ndarray) -> PipelineForecast:
    if feature_frame.size == 0:
        return PipelineForecast(
            forecast_volatility=0.0,
            liquidity_stress=0.0,
            factor_contributions=[],
        )

    volatility = float(np.clip(np.std(feature_frame), 0.01, 0.45))
    liquidity = float(np.clip(np.mean(np.abs(feature_frame)) / 10, 0.05, 0.8))
    return PipelineForecast(
        forecast_volatility=volatility,
        liquidity_stress=liquidity,
        factor_contributions=[
            {"factor": "Rates volatility", "weight": 0.31},
            {"factor": "Credit spreads", "weight": 0.24},
            {"factor": "FX basis", "weight": 0.18},
            {"factor": "Liquidity proxy", "weight": 0.12},
        ],
    )
