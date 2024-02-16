import numpy as np
from itertools import combinations


# last column and last row are headers and are not part of the reduction
def iterated_reduction(payoffs):

    def dominated_rows():
        rows = len(payoffs) - 1
        cols = len(payoffs[0]) - 1
        result = set()
        for row1, row2 in combinations(range(rows), 2):
            if all(
                payoffs[row1][col][0] <= payoffs[row2][col][0] for col in range(cols)
            ):
                result.add(row1)
            elif all(
                payoffs[row1][col][0] >= payoffs[row2][col][0] for col in range(cols)
            ):
                result.add(row2)
        return result

    def dominated_cols():
        rows = len(payoffs) - 1
        cols = len(payoffs[0]) - 1
        result = set()
        for col1, col2 in combinations(range(cols), 2):
            if all(
                payoffs[row][col1][1] <= payoffs[row][col2][1] for row in range(rows)
            ):
                result.add(col1)
            elif all(
                payoffs[row][col1][1] >= payoffs[row][col2][1] for row in range(rows)
            ):
                result.add(col2)
        return result

    deletions = 1
    while deletions > 0:
        deletions = 0
        rows_to_delete = dominated_rows()
        deletions += len(rows_to_delete)
        payoffs = np.delete(payoffs, list(rows_to_delete), 0)
        cols_to_delete = dominated_cols()
        deletions += len(cols_to_delete)
        payoffs = np.delete(payoffs, list(cols_to_delete), 1)

    return payoffs

print("~ Scythe  " + 50*"~")

# loss zero power (no card) = 0
# loss three power = 1
# loss two power = 2
# loss one power = 3
# win three power = 4
# win two power = 5
# win one power = 6
# win zero power = 7

SCYTHE_PAYOFFS = np.array(
    [
        [(7, 0), (0, 6), (0, 5), (0, 4), (0, 4)],
        [(6, 0), (6, 3), (3, 5), (3, 4), (1, 4)],
        [(5, 0), (5, 3), (5, 2), (2, 4), (2, 4)],
        [(3, 0), (3, 1), (3, 2), (3, 3), (3, 4)],
    ],
    dtype=[("rose", "<i4"), ("colin", "<i4")],
)

print(iterated_reduction(SCYTHE_PAYOFFS))

print("~ Rising Sun  " + 50*"~")

RISING_SUN_PAYOFFS = np.array(
    [
        [(2, -2), (2, -2), (2, -2), (-1, 1), (0, 4)],
        [(-3, 3), (2, -2), (0, 0), (-1, 1), (1, 4)],
        [(3, -3), (0, 0), (1, -1), (-3, 3), (2, 4)],
        [(0, 0), (0, 0), (1, -1), (2, -2), (3, 4)],
        [(4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
    ],
    dtype=[("rose", "<i4"), ("colin", "<i4")],
)

print(iterated_reduction(RISING_SUN_PAYOFFS))
