import numpy as np
from mwmath.normal_form import iterated_reduction


def test_reduction():
    # loss zero power (no card) = 0
    # loss three power = 1
    # loss two power = 2
    # loss one power = 3
    # win three power = 4
    # win two power = 5
    # win one power = 6
    # win zero power = 7

    payoffs = np.array(
        [
            [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
            [(1, 0), (7, 0), (0, 6), (0, 5), (0, 4)],
            [(2, 0), (6, 0), (6, 3), (3, 5), (3, 4)],
            [(3, 0), (5, 0), (5, 3), (5, 2), (2, 4)],
        ],
        dtype=[("rose", "<i4"), ("colin", "<i4")],
    )

    assert np.array_equal(
        iterated_reduction(payoffs),
        np.array(
            [
                [(0, 0), (0, 3), (0, 4)],
                [(2, 0), (3, 5), (3, 4)],
                [(3, 0), (5, 2), (2, 4)],
            ],
            dtype=[("rose", "<i4"), ("colin", "<i4")],
        )
    )
