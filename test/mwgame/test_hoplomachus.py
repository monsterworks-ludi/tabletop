from mwmath.adjacency_matrices import (
    build_matrix,
    determine_terminal_matrix,
    reverse_connections,
    count_directed_paths,
    count_all_directed_paths
)

def test_hoplomachus() -> None:
    def connect(i):
        start = min(
            {val for val in (1, 5, 9, 13, 17, 18, 22, 26, 30, 34, 35) if val > i}
        )
        return {start, start + 1, start + 2, start + 3}

    connections = {vertex: connect(vertex) for vertex in range(35)}
    #
    connections[13] = {17}
    connections[14] = {17}
    connections[15] = {17}
    connections[16] = {17}
    #
    connections[30] = {34}
    connections[31] = {34}
    connections[32] = {34}
    connections[33] = {34}
    #
    connections[34] = {34}
    matrix = build_matrix(connections)
    steps, terminal_matrix = determine_terminal_matrix(matrix, {34})
    assert steps == 10
    assert terminal_matrix[34, 0] == 65_536
    rev_conn = reverse_connections(connections)
    assert count_directed_paths(rev_conn, 34) == 65_536

if __name__ == "__main__":
    pass
