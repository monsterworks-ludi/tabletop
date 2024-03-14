from mwmath.adjacency_matrices import (
    build_matrix,
    determine_terminal_matrix,
    reverse_connections,
    count_all_directed_paths
)

def test_gloomhaven() -> None:
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
    matrix = build_matrix(connections)
    steps, terminal_matrix = determine_terminal_matrix(matrix, {11, 13, 15, 26})
    assert steps == 10
    assert terminal_matrix[11, 0] == 5
    assert terminal_matrix[13, 0] == 5
    assert terminal_matrix[15, 0] == 6
    assert terminal_matrix[26, 0] == 22
    #
    rev_conn = reverse_connections(connections)
    counted_paths = count_all_directed_paths(rev_conn)
    assert counted_paths[11] == 5
    assert counted_paths[13] == 5
    assert counted_paths[15] == 6
    assert counted_paths[26] == 22

if __name__ == "__main__":
    ...
