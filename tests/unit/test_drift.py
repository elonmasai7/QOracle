from backend.ml.monitoring.drift import population_stability_index


def test_psi_small_for_similar_distributions():
    expected = [0.1, 0.2, 0.3, 0.4, 0.5]
    actual = [0.11, 0.21, 0.31, 0.39, 0.49]
    psi = population_stability_index(expected, actual)
    assert psi < 0.2
