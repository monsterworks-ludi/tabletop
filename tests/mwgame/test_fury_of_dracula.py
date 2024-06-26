import sympy as sp

from mwmath.adjacency_matrices import (
    submatrix_symbolic,
    centers
)
from mwgame.fury_of_dracula import (
    IBERIA_CITIES,
    IBERIA_ROAD_MATRIX, IBERIA_RAIL_MATRIX, IBERIA_MATRIX,
    cadiz, granada, lisbon, madrid, alicante, santander, saragossa, barcelona,
    CITIES,
    IDENTITY_MATRIX, TRAVEL_MATRIX,
    cologne, paris, marseilles, hamburg, prague,
    athens, manchester, castle_dracula, dublin, constanta, galatz, sofia, valona, varna
)

class TestIberia:
    @staticmethod
    def test_build_matrix() -> None:
        # Iberian road adjacency matrix, p. 69
        assert IBERIA_ROAD_MATRIX.equals(
            sp.Matrix(
                [
                    [0, 1, 0, 1, 1, 0, 0, 0],
                    [1, 0, 1, 0, 1, 1, 0, 0],
                    [0, 1, 0, 0, 0, 0, 0, 0],
                    [1, 0, 0, 0, 1, 0, 1, 0],
                    [1, 1, 0, 1, 0, 1, 1, 1],
                    [0, 1, 0, 0, 1, 0, 0, 1],
                    [0, 0, 0, 1, 1, 0, 0, 1],
                    [0, 0, 0, 0, 1, 1, 1, 0],
                ]
            )
        )
        col_one = sp.ones(len(IBERIA_CITIES), 1)
        assert (IBERIA_ROAD_MATRIX * col_one).equals(
            sp.Matrix(len(IBERIA_CITIES), 1, [3, 4, 1, 3, 6, 3, 3, 3])
        )
        # Iberian rail adjacency matrix, p. 69
        assert IBERIA_RAIL_MATRIX.equals(
            sp.Matrix(
                [
                    [0, 0, 0, 0, 1, 0, 0, 0],
                    [0, 0, 1, 0, 1, 0, 0, 0],
                    [0, 1, 0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 1, 0, 0, 0],
                    [1, 1, 0, 1, 0, 1, 0, 0],
                    [0, 0, 1, 0, 1, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                ]
            )
        )
        assert (IBERIA_RAIL_MATRIX * col_one).equals(
            sp.Matrix(len(IBERIA_CITIES), 1, [1, 2, 2, 1, 4, 2, 0, 0])
        )
        # Iberian adjacency matrix, p. 70
        assert IBERIA_MATRIX.equals(
            sp.Matrix(
                [
                    [0, 1, 0, 1, 2, 0, 0, 0],
                    [1, 0, 2, 0, 2, 1, 0, 0],
                    [0, 2, 0, 0, 0, 1, 0, 0],
                    [1, 0, 0, 0, 2, 0, 1, 0],
                    [2, 2, 0, 2, 0, 2, 1, 1],
                    [0, 1, 1, 0, 2, 0, 0, 1],
                    [0, 0, 0, 1, 1, 0, 0, 1],
                    [0, 0, 0, 0, 1, 1, 1, 0],
                ]
            )
        )
        # three hop matrix, p. 73
        iberia_three_hop_matrix = IBERIA_MATRIX**3
        assert iberia_three_hop_matrix.equals(
            sp.Matrix(
                [
                    [16, 23, 13, 17, 43, 16, 10, 12],
                    [23, 20, 26, 14, 55, 22, 12, 12],
                    [13, 26, 4, 14, 11, 19, 7, 8],
                    [17, 14, 14, 12, 43, 14, 12, 9],
                    [43, 55, 11, 43, 34, 49, 24, 24],
                    [16, 22, 19, 14, 49, 16, 9, 13],
                    [10, 12, 7, 12, 24, 9, 6, 9],
                    [12, 12, 8, 9, 24, 13, 9, 6],
                ]
            )
        )
        iberia_four_hop_matrix = IBERIA_MATRIX**4
        # four hop matrix, p. 73
        assert iberia_four_hop_matrix[3, 7] == 69

    @staticmethod
    def test_fod_simple() -> None:
        # walk count example, p. 72
        south_matrix = submatrix_symbolic(
            IBERIA_CITIES,
            IBERIA_MATRIX,
            (cadiz, granada),
            (lisbon, madrid, alicante),
        )
        north_matrix = submatrix_symbolic(
            IBERIA_CITIES,
            IBERIA_MATRIX,
            (lisbon, madrid, alicante),
            (santander, saragossa, barcelona),
        )
        assert (south_matrix * north_matrix).equals(sp.Matrix([[3, 2, 0], [2, 3, 1]]))


class TestFull:
    @staticmethod
    def test_full_map() -> None:
        # distances in Fury of Dracula, p. 74
        prev_matrix = IDENTITY_MATRIX
        power_matrix = IDENTITY_MATRIX
        max_neighbors = 1
        prev_cities: set[sp.Symbol] = set()
        central_cities: set[sp.Symbol] = set()
        hops = 0
        while max_neighbors < len(CITIES) or len(central_cities) < len(CITIES):
            prev_cities = central_cities
            prev_matrix = power_matrix
            hops += 1
            power_matrix = TRAVEL_MATRIX * power_matrix
            max_neighbors, central_cities = centers(
                CITIES, power_matrix[0 : len(CITIES), 0 : len(CITIES)]
            )
            if hops == 1:
                assert max_neighbors == 16 and central_cities == {
                    cologne,
                    paris,
                }
            if hops == 2:
                assert max_neighbors == 33 and central_cities == {
                    paris,
                    marseilles,
                }
            if hops == 3:
                assert max_neighbors == 49 and central_cities == {prague}
            if hops == 4:
                assert max_neighbors == 59 and central_cities == {
                    cologne,
                    hamburg,
                    prague,
                }
            elif hops == 5:
                assert max_neighbors == 60 and len(central_cities) == 18
            elif hops == 7:
                assert len(central_cities) == len(CITIES) - 9
        assert hops == 8
        distant_cities = [city for city in central_cities if city not in prev_cities]
        eight_hop_trips = set()
        for city in distant_cities:
            row = CITIES.index(city)
            for col in range(CITIES.index(city), len(CITIES)):
                if prev_matrix[row, col] == 0:
                    eight_hop_trips.add((city, CITIES[col]))
        assert eight_hop_trips == {
            (athens, manchester),
            (castle_dracula, dublin),
            (constanta, dublin),
            (dublin, galatz),
            (dublin, sofia),
            (dublin, valona),
            (dublin, varna),
        }


if __name__ == "__main__":
    ...
