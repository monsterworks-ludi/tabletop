import numpy as np
import mwmath.normal_form as nf


def test_rising_sun_reduction():
    payoffs = np.array(
        [
            [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
            [(1, 0), (2, -2), (2, -2), (2, -2), (-1, 1)],
            [(2, 0), (-3, 3), (2, -2), (0, 0), (-1, 1)],
            [(3, 0), (3, -3), (0, 0), (1, -1), (-3, 3)],
            [(4, 0), (0, 0), (0, 0), (1, -1), (2, -2)],
        ],
        dtype=[("rose", "<i4"), ("colin", "<i4")],
    )

    assert np.array_equal(
        nf.iterated_reduction(payoffs),
        np.array(
            [
                [(0, 0), (0, 2), (0, 4)],
                [(1, 0), (2, -2), (-1, 1)],
                [(4, 0), (0, 0), (2, -2)],
            ],
            dtype=[("rose", "<i4"), ("colin", "<i4")],
        ),
    )


def test_rising_sun_saddle():
    reduced_payoffs = np.array(
        [
            [(0, 0), (0, 2), (0, 4)],
            [(1, 0), (2, -2), (-1, 1)],
            [(4, 0), (0, 0), (2, -2)],
        ],
        dtype=[("rose", "<i4"), ("colin", "<i4")],
    )
    bn_equilibrium = nf.determine_saddle(reduced_payoffs)
    assert abs(bn_equilibrium[0] - 3 / 5) < 10**-15
    # NOTE: In rising Sun, q is the probability of the second row, not the first.
    # This was done to match the orientation of the table with the heat map.
    assert abs(bn_equilibrium[1] - (1 - 3 / 5)) < 10**-15
