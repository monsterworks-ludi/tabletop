import itertools as it

import sympy as sp

from mwmath.adjacency_matrices import submatrix_symbolic, find_all_paths
from mwgame.ticket_to_ride import (
    NE_CITIES,
    NE_COST_MATRIX, NE_POINTS_MATRIX, NE_COMBINED_MATRIX, NE_COLOR_MATRIX,
    NE_CONNECTIONS,
    pittsburgh, washington, toronto, new_york, montreal, boston,
    x, v, b, g, p, r, t, w, y,

    CITIES,
    COST_MATRIX, POINTS_MATRIX, COMBINED_MATRIX, COLOR_POINTS_MATRIX,
    ADJACENCY_MATRIX, COLOR_CITY_POINTS_MATRIX, CITY_POINTS_MATRIX,
    connection_weight,
    los_angeles, duluth, helena, denver, phoenix, oklahoma_city, el_paso
)

class TestSimple:
    @staticmethod
    def test_costs() -> None:
        south_cost_matrix = submatrix_symbolic(
            NE_CITIES,
            NE_COST_MATRIX,
            (pittsburgh, washington),
            (toronto, new_york),
        )
        # Fig 4.10a, p. 75
        assert south_cost_matrix.equals(
            sp.Matrix([[x**2, 2 * x**2], [0, 2 * x**2]])
        )
        north_cost_matrix = submatrix_symbolic(
            NE_CITIES,
            NE_COST_MATRIX,
            (toronto, new_york),
            (montreal, boston),
        )
        # Fig 4.10b, p. 75
        assert north_cost_matrix.equals(sp.Matrix([[x**2, 0], [x**3, 2 * x**2]]))
        # Example, p. 76
        assert (south_cost_matrix * north_cost_matrix).equals(
            sp.Matrix([[2 * x**5 + x**4, 4 * x**4], [2 * x**5, 4 * x**4]])
        )

    @staticmethod
    def test_points() -> None:
        south_points_matrix = submatrix_symbolic(
            NE_CITIES,
            NE_POINTS_MATRIX,
            (pittsburgh, washington),
            (toronto, new_york),
        )
        # Example, p. 76
        assert south_points_matrix.equals(
            sp.Matrix([[v**2, 2 * v**2], [0, 2 * v**2]])
        )
        north_points_matrix = submatrix_symbolic(
            NE_CITIES,
            NE_POINTS_MATRIX,
            (toronto, new_york),
            (montreal, boston),
        )
        # Example, p. 76
        assert north_points_matrix.equals(
            sp.Matrix([[v**2, 0], [v**4, 2 * v**2]])
        )
        # Example, p. 76
        assert (south_points_matrix * north_points_matrix).equals(
            sp.Matrix([[v**4 + 2 * v**6, 4 * v**4], [2 * v**6, 4 * v**4]])
        )

    @staticmethod
    def test_combined() -> None:
        south_combined_matrix = submatrix_symbolic(
            NE_CITIES,
            NE_COMBINED_MATRIX,
            (pittsburgh, washington),
            (toronto, new_york),
        )
        # Example, p. 77
        assert south_combined_matrix.equals(
            sp.Matrix(
                [[x**2 * v**2, 2 * x**2 * v**2], [0, 2 * x**2 * v**2]]
            )
        )
        north_combined_matrix = submatrix_symbolic(
            NE_CITIES,
            NE_COMBINED_MATRIX,
            (toronto, new_york),
            (montreal, boston),
        )
        # Example, p. 77
        assert north_combined_matrix.equals(
            sp.Matrix([[x**2 * v**2, 0], [x**3 * v**4, 2 * x**2 * v**2]])
        )
        # Example, p. 77
        assert (south_combined_matrix * north_combined_matrix).equals(
            sp.Matrix(
                [
                    [x**4 * v**4 + 2 * x**5 * v**6, 4 * x**4 * v**4],
                    [2 * x**5 * v**6, 4 * x**4 * v**4],
                ]
            )
        )

    @staticmethod
    def test_color() -> None:
        south_color_matrix = submatrix_symbolic(
            NE_CITIES,
            NE_COLOR_MATRIX,
            (pittsburgh, washington),
            (toronto, new_york),
        )
        # Example, p. 78
        assert south_color_matrix.equals(
            sp.Matrix([[x**2, w**2 + g**2], [0, b**2 + t**2]])
        )
        north_color_matrix = submatrix_symbolic(
            NE_CITIES,
            NE_COLOR_MATRIX,
            (toronto, new_york),
            (montreal, boston),
        )
        # Example, p. 78
        assert north_color_matrix.equals(
            sp.Matrix([[x**2, 0], [b**3, y**2 + r**2]])
        )
        # Example, p. 78
        assert (south_color_matrix * north_color_matrix).equals(
            sp.Matrix(
                [
                    [
                        x**4 + w**2 * b**3 + g**2 * b**3,
                        w**2 * y**2
                        + w**2 * r**2
                        + g**2 * y**2
                        + g**2 * r**2,
                    ],
                    [
                        b**5 + b**3 * t**2,
                        b**2 * y**2
                        + b**2 * r**2
                        + t**2 * y**2
                        + t**2 * r**2,
                    ],
                ]
            )
        )

    @staticmethod
    def test_paths() -> None:
        all_paths = find_all_paths(NE_CONNECTIONS, (("", montreal),))
        # Figure 4.11, p. 80
        assert all_paths == {
            2: {
                (("", montreal), ("bbb", new_york), ("rr", boston)),
                (("", montreal), ("bbb", new_york), ("yy", boston)),
                (("", montreal), ("bbb", new_york), ("tt", washington)),
                (("", montreal), ("bbb", new_york), ("bb", washington)),
            },
            3: {
                (
                    ("", montreal),
                    ("bbb", new_york),
                    ("gg", pittsburgh),
                    ("xx", toronto),
                ),
                (
                    ("", montreal),
                    ("bbb", new_york),
                    ("ww", pittsburgh),
                    ("xx", toronto),
                ),
            },
            4: {
                (
                    ("", montreal),
                    ("xx", toronto),
                    ("xx", pittsburgh),
                    ("ww", new_york),
                    ("rr", boston),
                ),
                (
                    ("", montreal),
                    ("xx", toronto),
                    ("xx", pittsburgh),
                    ("ww", new_york),
                    ("yy", boston),
                ),
                (
                    ("", montreal),
                    ("xx", toronto),
                    ("xx", pittsburgh),
                    ("ww", new_york),
                    ("tt", washington),
                ),
                (
                    ("", montreal),
                    ("xx", toronto),
                    ("xx", pittsburgh),
                    ("ww", new_york),
                    ("bb", washington),
                ),
                (
                    ("", montreal),
                    ("xx", toronto),
                    ("xx", pittsburgh),
                    ("gg", new_york),
                    ("rr", boston),
                ),
                (
                    ("", montreal),
                    ("xx", toronto),
                    ("xx", pittsburgh),
                    ("gg", new_york),
                    ("yy", boston),
                ),
                (
                    ("", montreal),
                    ("xx", toronto),
                    ("xx", pittsburgh),
                    ("gg", new_york),
                    ("tt", washington),
                ),
                (
                    ("", montreal),
                    ("xx", toronto),
                    ("xx", pittsburgh),
                    ("gg", new_york),
                    ("bb", washington),
                ),
            },
        }

    @staticmethod
    def test_paths_to_toronto() -> None:
        all_paths = find_all_paths(
            NE_CONNECTIONS, (("", montreal),), dest=toronto
        )
        assert all_paths == {
            1: {(("", montreal), ("xx", toronto))},
            3: {
                (
                    ("", montreal),
                    ("bbb", new_york),
                    ("gg", pittsburgh),
                    ("xx", toronto),
                ),
                (
                    ("", montreal),
                    ("bbb", new_york),
                    ("ww", pittsburgh),
                    ("xx", toronto),
                ),
            },
        }


class TestFull:
    @staticmethod
    def test_ttr_costs() -> None:
        montreal_los_angeles_cost = sp.Integer(0)
        cost_matrix = sp.eye(len(CITIES))
        power = 0
        for power in it.count(1):
            cost_matrix *= COST_MATRIX
            montreal_los_angeles_cost = connection_weight(
                cost_matrix, los_angeles, montreal
            )
            if not montreal_los_angeles_cost == sp.Integer(0):
                break
        # Not in text
        assert power == 6
        assert montreal_los_angeles_cost.equals(
            2 * x**27 + 9 * x**26 + 4 * x**25 + 5 * x**23 + 3 * x**22
        )
        assert montreal_los_angeles_cost.subs(x, 1) == 23

    @staticmethod
    def test_ttr_points() -> None:
        montreal_los_angeles_points = sp.Integer(0)
        points_matrix = sp.eye(len(CITIES))
        power = 0
        for power in it.count(1):
            points_matrix *= POINTS_MATRIX
            montreal_los_angeles_points = connection_weight(
                points_matrix, los_angeles, montreal
            )
            if not montreal_los_angeles_points == 0:
                break
        # Example, p. 77
        assert power == 6
        assert montreal_los_angeles_points.equals(
            v**55
            + v**53
            + 4 * v**52
            + 5 * v**50
            + 4 * v**47
            + v**44
            + 3 * v**42
            + 2 * v**39
            + 2 * v**37
        )
        assert montreal_los_angeles_points.subs(v, 1) == 23

    @staticmethod
    def test_ttr_combined() -> None:
        montreal_los_angeles_combined = sp.Integer(0)
        combined_matrix = sp.eye(len(CITIES))
        power = 0
        for power in it.count(1):
            combined_matrix *= COMBINED_MATRIX
            montreal_los_angeles_combined = connection_weight(
                combined_matrix, los_angeles, montreal
            )
            if not montreal_los_angeles_combined == sp.Integer(0):
                break
        # Example, p.77
        assert power == 6
        assert montreal_los_angeles_combined.equals(
            v**55 * x**27
            + v**53 * x**27
            + 4 * v**52 * x**26
            + 5 * v**50 * x**26
            + 4 * v**47 * x**25
            + v**44 * x**23
            + 3 * v**42 * x**23
            + v**39 * x**23
            + v**39 * x**22
            + 2 * v**37 * x**22
        )
        assert montreal_los_angeles_combined.subs(v, 1).subs(x, 1) == 23

    @staticmethod
    def test_ttr_colors() -> None:
        montreal_los_angeles_colors = sp.Integer(0)
        color_matrix = sp.eye(len(CITIES))
        power = 0
        for power in it.count(1):
            color_matrix *= COLOR_POINTS_MATRIX
            montreal_los_angeles_colors = connection_weight(
                color_matrix, los_angeles, montreal
            )
            if not montreal_los_angeles_colors == sp.Integer(0):
                break
        # Example, p.78
        assert power == 6
        assert (
            montreal_los_angeles_colors.expand()
            .as_expr()
            .coeff(v, 55)
            .equals(g**4 * p**6 * t**6 * w**5 * x**6)
        )

    @staticmethod
    def test_route_counts() -> None:
        seven_hop_matrix = ADJACENCY_MATRIX**7
        montreal_los_angeles_seven_hops = connection_weight(
            seven_hop_matrix, los_angeles, montreal
        )
        # Comment, p. 78
        assert montreal_los_angeles_seven_hops == 356
        eight_hop_matrix = seven_hop_matrix * ADJACENCY_MATRIX
        montreal_los_angeles_eight_hops = connection_weight(
            eight_hop_matrix, los_angeles, montreal
        )
        # Comment, p. 78
        assert montreal_los_angeles_eight_hops == 3763

    @staticmethod
    def test_six_hop_route() -> None:
        montreal_los_angeles_route = sp.Integer(0)
        route_matrix = sp.eye(len(CITIES))
        power = 0
        for power in it.count(1):
            route_matrix *= COLOR_CITY_POINTS_MATRIX
            montreal_los_angeles_route = connection_weight(
                route_matrix, los_angeles, montreal
            )
            if not montreal_los_angeles_route == sp.Integer(0):
                break
        # Comment on p. 78
        assert power == 6
        assert (
            montreal_los_angeles_route.expand()
            .as_expr()
            .coeff(v, 55)
            .equals(
                1
                * g**4
                * p**6
                * t**6
                * w**5
                * x**6
                * toronto
                * duluth
                * helena
                * denver
                * phoenix
                * los_angeles
            )
        )

    # takes about 108 seconds on my computer
    @staticmethod
    def test_seven_hop_route() -> None:
        points_matrix = CITY_POINTS_MATRIX**7
        montreal_los_angeles_route_coeffs = sp.Poly(
            connection_weight(points_matrix, los_angeles, montreal), v
        ).all_coeffs()
        # Comment, p. 78
        assert len(montreal_los_angeles_route_coeffs) == 74
        assert montreal_los_angeles_route_coeffs[0].equals(
            1
            * toronto
            * duluth
            * helena
            * denver
            * oklahoma_city
            * el_paso
            * los_angeles
        )


if __name__ == "__main__":
    ...
