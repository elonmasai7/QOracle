import numpy as np


def population_stability_index(expected, actual, buckets=10):
    expected = np.array(expected)
    actual = np.array(actual)
    effective_buckets = min(buckets, max(2, int(np.sqrt(min(len(expected), len(actual))))))
    min_v = min(expected.min(), actual.min())
    max_v = max(expected.max(), actual.max())
    if np.isclose(min_v, max_v):
        return 0.0
    cuts = np.linspace(min_v, max_v, effective_buckets + 1)

    psi = 0.0
    for i in range(effective_buckets):
        if i < effective_buckets - 1:
            e = ((expected >= cuts[i]) & (expected < cuts[i + 1])).mean()
            a = ((actual >= cuts[i]) & (actual < cuts[i + 1])).mean()
        else:
            e = ((expected >= cuts[i]) & (expected <= cuts[i + 1])).mean()
            a = ((actual >= cuts[i]) & (actual <= cuts[i + 1])).mean()
        if e == 0 and a == 0:
            continue
        e = max(e, 1e-6)
        a = max(a, 1e-6)
        psi += (a - e) * np.log(a / e)
    return float(psi)
