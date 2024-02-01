from icecream import ic  # type: ignore

from math import adjacency_matrices as am

ic.disable()

class TestCampaigns:
    @staticmethod
    def test_pandemic() -> None:
        connections = {
            vertex: {vertex + 1, vertex + 2} if vertex % 2 == 0 else {vertex + 1}
            for vertex in range(17)
        }
        connections[16] = {16}
        ic(connections)
        matrix = am.build_matrix(connections)
        steps, terminal_matrix = am.terminal_matrix(matrix, (16,))
        assert steps == 16
        assert terminal_matrix[16, 0] == 256
        rev_conn = am.reverse_connections(connections)
        counted_paths = am.count_all_directed_paths(rev_conn)
        assert counted_paths[16] == 256

    @staticmethod
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
        matrix = am.build_matrix(connections)
        steps, terminal_matrix = am.terminal_matrix(matrix, (11, 13, 15, 26))
        assert steps == 10
        assert terminal_matrix[11, 0] == 5
        assert terminal_matrix[13, 0] == 5
        assert terminal_matrix[15, 0] == 6
        assert terminal_matrix[26, 0] == 22
        #
        rev_conn = am.reverse_connections(connections)
        counted_paths = am.count_all_directed_paths(rev_conn)
        assert counted_paths[11] == 5
        assert counted_paths[13] == 5
        assert counted_paths[15] == 6
        assert counted_paths[26] == 22

    @staticmethod
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
        matrix = am.build_matrix(connections)
        steps, terminal_matrix = am.terminal_matrix(matrix, (34,))
        assert steps == 10
        assert terminal_matrix[34, 0] == 65_536
        rev_conn = am.reverse_connections(connections)
        assert am.count_directed_paths(rev_conn, 34) == 65_536


if __name__ == "__main__":
    ...
