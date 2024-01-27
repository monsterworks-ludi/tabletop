import sympy as sp
import itertools as it

from icecream import ic  # type: ignore

import adjacency_matrices as am
import ticket_to_ride as ttr
from ticket_to_ride import x, v, b, g, p, r, t, w, y


class TestSimple:
    @staticmethod
    def test_costs() -> None:
        south_cost_matrix = am.submatrix_symbolic(
            ttr.NE_CITIES,
            ttr.NE_COST_MATRIX,
            (ttr.pittsburgh, ttr.washington),
            (ttr.toronto, ttr.new_york),
        )
        # Fig 4.10a, p. 75
        assert south_cost_matrix.equals(
            sp.Matrix([[x**2, 2 * x**2], [0, 2 * x**2]])
        )
        north_cost_matrix = am.submatrix_symbolic(
            ttr.NE_CITIES,
            ttr.NE_COST_MATRIX,
            (ttr.toronto, ttr.new_york),
            (ttr.montreal, ttr.boston),
        )
        # Fig 4.10b, p. 75
        assert north_cost_matrix.equals(sp.Matrix([[x**2, 0], [x**3, 2 * x**2]]))
        # Example, p. 76
        assert (south_cost_matrix * north_cost_matrix).equals(
            sp.Matrix([[2 * x**5 + x**4, 4 * x**4], [2 * x**5, 4 * x**4]])
        )

    @staticmethod
    def test_points() -> None:
        south_points_matrix = am.submatrix_symbolic(
            ttr.NE_CITIES,
            ttr.NE_POINTS_MATRIX,
            (ttr.pittsburgh, ttr.washington),
            (ttr.toronto, ttr.new_york),
        )
        # Example, p. 76
        assert south_points_matrix.equals(
            sp.Matrix([[v**2, 2 * v**2], [0, 2 * v**2]])
        )
        north_points_matrix = am.submatrix_symbolic(
            ttr.NE_CITIES,
            ttr.NE_POINTS_MATRIX,
            (ttr.toronto, ttr.new_york),
            (ttr.montreal, ttr.boston),
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
        south_combined_matrix = am.submatrix_symbolic(
            ttr.NE_CITIES,
            ttr.NE_COMBINED_MATRIX,
            (ttr.pittsburgh, ttr.washington),
            (ttr.toronto, ttr.new_york),
        )
        # Example, p. 77
        assert south_combined_matrix.equals(
            sp.Matrix(
                [[x**2 * v**2, 2 * x**2 * v**2], [0, 2 * x**2 * v**2]]
            )
        )
        north_combined_matrix = am.submatrix_symbolic(
            ttr.NE_CITIES,
            ttr.NE_COMBINED_MATRIX,
            (ttr.toronto, ttr.new_york),
            (ttr.montreal, ttr.boston),
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
        south_color_matrix = am.submatrix_symbolic(
            ttr.NE_CITIES,
            ttr.NE_COLOR_MATRIX,
            (ttr.pittsburgh, ttr.washington),
            (ttr.toronto, ttr.new_york),
        )
        # Example, p. 78
        assert south_color_matrix.equals(
            sp.Matrix([[x**2, w**2 + g**2], [0, b**2 + t**2]])
        )
        north_color_matrix = am.submatrix_symbolic(
            ttr.NE_CITIES,
            ttr.NE_COLOR_MATRIX,
            (ttr.toronto, ttr.new_york),
            (ttr.montreal, ttr.boston),
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
        all_paths = am.find_all_paths(ttr.NE_CONNECTIONS, (("", ttr.montreal),))
        # Figure 4.11, p. 80
        assert all_paths == {
            2: {
                (("", ttr.montreal), ("bbb", ttr.new_york), ("rr", ttr.boston)),
                (("", ttr.montreal), ("bbb", ttr.new_york), ("yy", ttr.boston)),
                (("", ttr.montreal), ("bbb", ttr.new_york), ("tt", ttr.washington)),
                (("", ttr.montreal), ("bbb", ttr.new_york), ("bb", ttr.washington)),
            },
            3: {
                (
                    ("", ttr.montreal),
                    ("bbb", ttr.new_york),
                    ("gg", ttr.pittsburgh),
                    ("xx", ttr.toronto),
                ),
                (
                    ("", ttr.montreal),
                    ("bbb", ttr.new_york),
                    ("ww", ttr.pittsburgh),
                    ("xx", ttr.toronto),
                ),
            },
            4: {
                (
                    ("", ttr.montreal),
                    ("xx", ttr.toronto),
                    ("xx", ttr.pittsburgh),
                    ("ww", ttr.new_york),
                    ("rr", ttr.boston),
                ),
                (
                    ("", ttr.montreal),
                    ("xx", ttr.toronto),
                    ("xx", ttr.pittsburgh),
                    ("ww", ttr.new_york),
                    ("yy", ttr.boston),
                ),
                (
                    ("", ttr.montreal),
                    ("xx", ttr.toronto),
                    ("xx", ttr.pittsburgh),
                    ("ww", ttr.new_york),
                    ("tt", ttr.washington),
                ),
                (
                    ("", ttr.montreal),
                    ("xx", ttr.toronto),
                    ("xx", ttr.pittsburgh),
                    ("ww", ttr.new_york),
                    ("bb", ttr.washington),
                ),
                (
                    ("", ttr.montreal),
                    ("xx", ttr.toronto),
                    ("xx", ttr.pittsburgh),
                    ("gg", ttr.new_york),
                    ("rr", ttr.boston),
                ),
                (
                    ("", ttr.montreal),
                    ("xx", ttr.toronto),
                    ("xx", ttr.pittsburgh),
                    ("gg", ttr.new_york),
                    ("yy", ttr.boston),
                ),
                (
                    ("", ttr.montreal),
                    ("xx", ttr.toronto),
                    ("xx", ttr.pittsburgh),
                    ("gg", ttr.new_york),
                    ("tt", ttr.washington),
                ),
                (
                    ("", ttr.montreal),
                    ("xx", ttr.toronto),
                    ("xx", ttr.pittsburgh),
                    ("gg", ttr.new_york),
                    ("bb", ttr.washington),
                ),
            },
        }

    @staticmethod
    def test_paths_to_toronto() -> None:
        all_paths = am.find_all_paths(
            ttr.NE_CONNECTIONS, (("", ttr.montreal),), dest=ttr.toronto
        )
        assert all_paths == {
            1: {(("", ttr.montreal), ("xx", ttr.toronto))},
            3: {
                (
                    ("", ttr.montreal),
                    ("bbb", ttr.new_york),
                    ("gg", ttr.pittsburgh),
                    ("xx", ttr.toronto),
                ),
                (
                    ("", ttr.montreal),
                    ("bbb", ttr.new_york),
                    ("ww", ttr.pittsburgh),
                    ("xx", ttr.toronto),
                ),
            },
        }


class TestFull:
    @staticmethod
    def test_ttr_costs() -> None:
        montreal_los_angeles_cost = 0 * x
        cost_matrix = sp.eye(len(ttr.CITIES))
        power = 0
        for power in it.count(1):
            cost_matrix *= ttr.COST_MATRIX
            montreal_los_angeles_cost = ttr.connection_weight(
                cost_matrix, ttr.los_angeles, ttr.montreal
            )
            if not montreal_los_angeles_cost == 0 * x:
                break
        # Not in text
        assert power == 6
        assert montreal_los_angeles_cost.equals(
            2 * x**27 + 9 * x**26 + 4 * x**25 + 5 * x**23 + 3 * x**22
        )
        assert montreal_los_angeles_cost.subs(x, 1) == 23

    @staticmethod
    def test_ttr_points() -> None:
        montreal_los_angeles_points = 0 * v
        points_matrix = sp.eye(len(ttr.CITIES))
        power = 0
        for power in it.count(1):
            points_matrix *= ttr.POINTS_MATRIX
            montreal_los_angeles_points = ttr.connection_weight(
                points_matrix, ttr.los_angeles, ttr.montreal
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
        montreal_los_angeles_combined = 0 * x * v
        combined_matrix = sp.eye(len(ttr.CITIES))
        power = 0
        for power in it.count(1):
            combined_matrix *= ttr.COMBINED_MATRIX
            montreal_los_angeles_combined = ttr.connection_weight(
                combined_matrix, ttr.los_angeles, ttr.montreal
            )
            if not montreal_los_angeles_combined == 0 * x * v:
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
        montreal_los_angeles_colors = 0 * x
        color_matrix = sp.eye(len(ttr.CITIES))
        power = 0
        for power in it.count(1):
            color_matrix *= ttr.COLOR_POINTS_MATRIX
            montreal_los_angeles_colors = ttr.connection_weight(
                color_matrix, ttr.los_angeles, ttr.montreal
            )
            if not montreal_los_angeles_colors == 0 * x:
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
        seven_hop_matrix = ttr.ADJACENCY_MATRIX**7
        montreal_los_angeles_seven_hops = ttr.connection_weight(
            seven_hop_matrix, ttr.los_angeles, ttr.montreal
        )
        # Comment, p. 78
        assert montreal_los_angeles_seven_hops == 356
        eight_hop_matrix = seven_hop_matrix * ttr.ADJACENCY_MATRIX
        montreal_los_angeles_eight_hops = ttr.connection_weight(
            eight_hop_matrix, ttr.los_angeles, ttr.montreal
        )
        # Comment, p. 78
        assert montreal_los_angeles_eight_hops == 3763

    @staticmethod
    def test_six_hop_route() -> None:
        ic.enable()
        montreal_los_angeles_route = 0 * x
        route_matrix = sp.eye(len(ttr.CITIES))
        power = 0
        for power in it.count(1):
            route_matrix *= ttr.COLOR_CITY_POINTS_MATRIX
            montreal_los_angeles_route = ttr.connection_weight(
                route_matrix, ttr.los_angeles, ttr.montreal
            )
            if not montreal_los_angeles_route == 0 * x:
                break
        # Comment on p. 78
        assert power == 6
        print(montreal_los_angeles_route.expand().as_expr().coeff(v, 55))
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
                * ttr.toronto
                * ttr.duluth
                * ttr.helena
                * ttr.denver
                * ttr.phoenix
                * ttr.los_angeles
            )
        )
        ic.disable()

    # takes about 108 seconds on my computer
    @staticmethod
    def test_seven_hop_route() -> None:
        points_matrix = ttr.CITY_POINTS_MATRIX**7
        montreal_los_angeles_route_coeffs = sp.Poly(
            ttr.connection_weight(points_matrix, ttr.los_angeles, ttr.montreal), v
        ).all_coeffs()
        # Comment, p. 78
        assert len(montreal_los_angeles_route_coeffs) == 74
        assert montreal_los_angeles_route_coeffs[0].equals(
            1
            * ttr.toronto
            * ttr.duluth
            * ttr.helena
            * ttr.denver
            * ttr.oklahoma_city
            * ttr.el_paso
            * ttr.los_angeles
        )


if __name__ == "__main__":
    ...
