import sympy as sp

import adjacency_matrices as am


def test_pandemic():
    adjacency = sp.Matrix(
        17,
        17,
        lambda dest, orig: (
            1
            if (
                (dest == orig + 1)
                or (orig % 2 == 0 and dest == orig + 2)
                or (orig == 16 and dest == 16)
            )
            else 0
        ),
    )
    steps, terminal_matrix = am.terminal_matrix(adjacency, (16,))
    assert steps == 16
    assert terminal_matrix[16, 0] == 256


def test_gloomhaven():
    connections = {
        0: {3, 4, 5},
        #
        1: {6},
        2: {1, 6, 7},
        3: {2, 8},
        4: {8},
        5: {9, 10},
        #
        6: {12},
        7: {12},
        8: {7, 14, 9},
        9: {14},
        10: {14},
        #
        11: {11},
        12: {17},
        13: {13},
        14: {19, 20},
        15: {15},
        #
        16: {11, 21},
        17: {18, 22},
        18: {13, 23},
        19: {24, 25},
        20: {15},
        #
        21: {26},
        22: {16},
        23: {26},
        24: {25},
        25: {26},
        #
        26: {26},
    }
    matrix = am.build_matrix(connections)
    steps, terminal_matrix = am.terminal_matrix(matrix, (11, 13, 15, 26))
    assert steps == 10
    assert terminal_matrix[11, 0] == 5
    assert terminal_matrix[13, 0] == 5
    assert terminal_matrix[15, 0] == 6
    assert terminal_matrix[26, 0] == 22


def test_hoplomachus():
    # may be able to code this as a lambda function
    connections = {
        0: {1, 2, 3, 4},
        #
        1: {5, 6, 7, 8},
        2: {5, 6, 7, 8},
        3: {5, 6, 7, 8},
        4: {5, 6, 7, 8},
        #
        5: {9, 10, 11, 12},
        6: {9, 10, 11, 12},
        7: {9, 10, 11, 12},
        8: {9, 10, 11, 12},
        #
        9: {13, 14, 15, 16},
        10: {13, 14, 15, 16},
        11: {13, 14, 15, 16},
        12: {13, 14, 15, 16},
        #
        13: {17},
        14: {17},
        15: {17},
        16: {17},
        #
        17: {18, 19, 20, 21},
        #
        18: {22, 23, 24, 25},
        19: {22, 23, 24, 25},
        20: {22, 23, 24, 25},
        21: {22, 23, 24, 25},
        #
        22: {26, 27, 28, 29},
        23: {26, 27, 28, 29},
        24: {26, 27, 28, 29},
        25: {26, 27, 28, 29},
        #
        26: {30, 31, 32, 33},
        27: {30, 31, 32, 33},
        28: {30, 31, 32, 33},
        29: {30, 31, 32, 33},
        #
        30: {34},
        31: {34},
        32: {34},
        33: {34},
        #
        34: {34},
    }
    matrix = am.build_matrix(connections)
    steps, terminal_matrix = am.terminal_matrix(matrix, (34,))
    assert steps == 10
    assert terminal_matrix[34, 0] == 65_536

if __name__ == "__main__":
    ...
