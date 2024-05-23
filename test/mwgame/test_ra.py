import itertools
import random

import numpy as np
from pytest import mark
from pytest_check import check

from mwmath.monte_carlo import set_seed, bad_seed_message
from mwgame.ra import RaBidder, run_continuous_ra_auction


@mark.parametrize("trials", [100_000])
def test_continuous_ra_shading(trials):
    # Table, p.
    seed = set_seed()
    expected0 = np.array([[0.08, 0.08, 0.08, 0.08, 0.08],
                          [0.26, 0.26, 0.26, 0.26, 0.26],
                          [0.44, 0.44, 0.44, 0.44, 0.44],
                          [0.52, 0.52, 0.52, 0.52, 0.52],
                          [0.41, 0.41, 0.41, 0.41, 0.41]])
    expected1 = np.array([[0.69, 1.04, 1.16, 1.04, 0.65],
                          [0.82, 1.04, 1.14, 1.02, 0.64],
                          [0.88, 1.02, 1.09, 0.98, 0.62],
                          [0.84, 0.94, 0.99, 0.91, 0.58],
                          [0.74, 0.82, 0.86, 0.79, 0.52]])
    expected2 = np.array([[5.56, 4.74, 3.98, 3.28, 2.72],
                          [4.73, 4.27, 3.66, 3.05, 2.54],
                          [3.94, 3.64, 3.21, 2.71, 2.27],
                          [3.30, 3.03, 2.72, 2.32, 1.96],
                          [2.70, 2.52, 2.27, 1.96, 1.66]])
    actual0 = np.zeros(shape=(5, 5), dtype=float)
    actual1 = np.zeros(shape=(5, 5), dtype=float)
    actual2 = np.zeros(shape=(5, 5), dtype=float)
    for row, col in itertools.product(range(5), repeat=2):
        for _ in range(trials):
            valuations = [random.uniform(0, 14), random.uniform(0, 14), random.uniform(0, 14)]
            bidders = [
                RaBidder(0, valuations[0], (row + 1) / 6, [5, 11]),
                RaBidder(1, valuations[1], (col + 1) / 6, [4, 9, 12]),
                RaBidder(2, valuations[2], 0 / 6, [6, 13])
            ]
            winning_bid, winning_bidder = run_continuous_ra_auction(bidders)
            if winning_bidder.index == 0:
                actual0[row, col] += (winning_bidder.valuation - winning_bid) / trials
            elif winning_bidder.index == 1:
                actual1[row, col] += (winning_bidder.valuation - winning_bid) / trials
            else:
                assert winning_bidder.index == 2
                actual2[row, col] += (winning_bidder.valuation - winning_bid) / trials

    # these are the important checks, as they verify that we want shadings of 2/3 and 1/2
    for index in range(0, 5):
        with check():
            column = actual0[:, index]
            assert max(column) == column[3], bad_seed_message(seed, trials)
        with check():
            row = actual1[index, :]
            assert max(row) == row[2], bad_seed_message(seed, trials)

    # these are slightly less important, but would have been in the table if I had been more careful
    # I think the values in the table were taken from a run where I was playing around with different distributions
    with check():
        assert (abs(expected0 - actual0) < 5e-2).all(), bad_seed_message(seed, trials)
    with check():
        assert (abs(expected1 - actual1) < 5e-2).all(), bad_seed_message(seed, trials)
    with check():
        assert (abs(expected2 - actual2) < 5e-2).all(), bad_seed_message(seed, trials)
