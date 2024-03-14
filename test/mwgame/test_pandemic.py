from mwmath.adjacency_matrices import (
    build_matrix,
    determine_terminal_matrix,
    reverse_connections,
    count_all_directed_paths
)

def test_pandemic() -> None:
    connections = {
        vertex: {vertex + 1, vertex + 2} if vertex % 2 == 0 else {vertex + 1}
        for vertex in range(17)
    }
    connections[16] = {16}
    matrix = build_matrix(connections)
    steps, terminal_matrix = determine_terminal_matrix(matrix, {16})
    assert steps == 16
    assert terminal_matrix[16, 0] == 256
    rev_conn = reverse_connections(connections)
    counted_paths = count_all_directed_paths(rev_conn)
    assert counted_paths[16] == 256

if __name__ == "__main__":
    ...
