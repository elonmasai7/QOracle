from __future__ import annotations

from typing import Any

import numpy as np

from .hybrid_runner import run_hybrid_benchmark


def run_quantum_tail_workflow(losses: np.ndarray, threshold: float, enabled: bool = True) -> dict[str, Any]:
    if not enabled:
        return {
            "benchmark": {
                "classical_estimate": float(np.mean(losses >= threshold)),
                "hybrid_estimate": None,
                "quantum_mode_active": False,
                "runtime_ms": 0,
            },
            "fallback_used": True,
            "details": {"reason": "quantum_mode_disabled"},
        }
    return run_hybrid_benchmark(losses, threshold)
