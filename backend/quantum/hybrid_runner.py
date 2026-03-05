import time
from .qae_engine import estimate_tail_probability


def run_hybrid_benchmark(losses, threshold):
    start = time.time()
    qae = estimate_tail_probability(losses, threshold)
    total_ms = int((time.time() - start) * 1000)
    return {
        "benchmark": {
            "classical_estimate": qae["classical_tail_probability"],
            "hybrid_estimate": qae["quantum_tail_probability"],
            "quantum_mode_active": qae["quantum_available"],
            "runtime_ms": total_ms,
        },
        "fallback_used": not qae["quantum_available"],
        "details": qae,
    }
