import numpy as np
from itertools import combinations


def iterated_reduction(payoffs):

    def dominated_rows():
        rows = len(payoffs)
        cols = len(payoffs[0])
        result = set()
        for row1, row2 in combinations(range(1, rows), 2):
            if all(
                payoffs[row1][col][0] <= payoffs[row2][col][0] for col in range(1, cols)
            ):
                result.add(row1)
            elif all(
                payoffs[row1][col][0] >= payoffs[row2][col][0] for col in range(1, cols)
            ):
                result.add(row2)
        return result

    def dominated_cols():
        rows = len(payoffs)
        cols = len(payoffs[0])
        result = set()
        for col1, col2 in combinations(range(1, cols), 2):
            if all(
                payoffs[row][col1][1] <= payoffs[row][col2][1] for row in range(1, rows)
            ):
                result.add(col1)
            elif all(
                payoffs[row][col1][1] >= payoffs[row][col2][1] for row in range(1, rows)
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


def determine_saddle(reduced_payoffs):
    rows = len(reduced_payoffs)
    cols = len(reduced_payoffs[0])
    row_coefficients = [
        [reduced_payoffs[i, j][0] - reduced_payoffs[1, j][0] for j in range(1, cols)]
        for i in range(2, rows)
    ]
    row_coefficients.append([1 for i in range(1, cols)])
    constant = [0 for i in range(2, rows)]
    constant.append(1)
    x = np.linalg.solve(np.array(row_coefficients), np.array(constant))

    col_coefficients = [
        [reduced_payoffs[i, j][1] - reduced_payoffs[i, 1][1] for i in range(1, rows)]
        for j in range(2, cols)
    ]
    col_coefficients.append([1 for i in range(1, rows)])
    constant = [0 for i in range(2, cols)]
    constant.append(1)
    y = np.linalg.solve(np.array(col_coefficients), np.array(constant))

    return x[0], y[0]
