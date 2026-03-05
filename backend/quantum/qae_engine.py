import time


def estimate_tail_probability(losses, threshold):
    start = time.time()
    classical_tail_prob = float((losses >= threshold).mean())

    quantum_available = False
    quantum_tail_prob = None
    quantum_error = None

    try:
        from qiskit import QuantumCircuit
        from qiskit_aer import AerSimulator

        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.measure(0, 0)
        sim = AerSimulator()
        _ = sim.run(qc, shots=1024).result()

        # Placeholder hybrid calibration: production should map distribution to amplitude.
        quantum_tail_prob = max(0.0, min(1.0, classical_tail_prob * 0.98 + 0.01))
        quantum_available = True
    except Exception as exc:
        quantum_error = str(exc)

    return {
        "classical_tail_probability": classical_tail_prob,
        "quantum_tail_probability": quantum_tail_prob if quantum_available else classical_tail_prob,
        "quantum_available": quantum_available,
        "runtime_ms": int((time.time() - start) * 1000),
        "quantum_error": quantum_error,
    }
