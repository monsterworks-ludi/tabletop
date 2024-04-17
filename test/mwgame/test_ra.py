import itertools
import array
import random

import numpy as np
from pytest import mark

from mwgame.ra import run_continuous_auctions

@mark.parametrize("trials", [100_000])
def test_shading(trials):
    expected1 = np.array([[0.08, 0.08, 0.08, 0.08, 0.08],
                       [0.26, 0.26, 0.26, 0.26, 0.26],
                       [0.44, 0.44, 0.44, 0.44, 0.44],
                       [0.52, 0.52, 0.52, 0.52, 0.52],
                       [0.41, 0.41, 0.41, 0.41, 0.41]])
    expected2 = np.array([[0.69, 1.04, 1.16, 1.04, 0.65],
                       [0.82, 1.04, 1.14, 1.02, 0.64],
                       [0.88, 1.02, 1.09, 0.98, 0.62],
                       [0.84, 0.94, 0.99, 0.91, 0.58],
                       [0.74, 0.82, 0.86, 0.79, 0.52]])
    actual1 = np.zeros(shape=(5, 5), dtype=float)
    actual2 = np.zeros(shape=(5, 5), dtype=float)
    for row, col in itertools.product(range(5), repeat=2):
        random.seed(1)
        avg_revenue, avg_wins_gains = run_continuous_auctions(
            trials,
            [(row+1) / 6, (col+1) / 6, 0],
            [[5, 11], [4, 9, 12], [6, 13]]
        )
        actual1[row, col] = avg_wins_gains[1][1]
        actual2[row, col] = avg_wins_gains[2][1]

    assert (abs(expected1 - actual1) < 5e-3).all()
    assert (abs(expected2 - actual2) < 5e-3).all()
