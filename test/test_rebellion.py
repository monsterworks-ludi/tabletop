import sys
import random

from icecream import ic  # type: ignore
import pytest

import sympy as sp

from collections import defaultdict

from game import rebellion as rb

ic.disable()


def round_to(decimals):
    return lambda x: round(x, decimals)


def set_seed() -> int:
    seed = random.randrange(sys.maxsize)
    random.seed(seed)
    return seed


class TestSimple:
    TIE_Y_MAT = rb.rat_mat(
        [[5, 0, 0, 0], [5, 12, 0, 0], [1, 0, 12, 0], [1, 0, 0, 12]], 12
    )

    @staticmethod
    def test_tie_y_powers() -> None:
        p = TestSimple.TIE_Y_MAT
        # Example, p. 114
        assert p**2 == rb.rat_mat(
            [[25, 0, 0, 0], [85, 144, 0, 0], [17, 0, 144, 0], [17, 0, 0, 144]], 144
        )
        # Example, p. 115
        assert (p**2)[:, 0] == rb.rat_mat([[25], [85], [17], [17]], 144)
        rounded_tenth = ((p**10)[:, 0]).applyfunc(lambda x: round(x, 5))
        # Example, p.115
        assert (
            rb.mat_max(rounded_tenth - sp.Matrix([[0.00016], [0.71417], [0.14283], [0.14283]]))
        ) < 0.000005
        # Example, p. 115
        assert rb.to_infinity(p)[:, 0] == rb.rat_mat([[0], [5], [1], [1]], 7)

    @staticmethod
    def test_tie_y_mean() -> None:
        k = sp.Symbol("k")
        # Example, p. 115
        assert sp.Sum(
            k * sp.Rational(5, 12) ** (k - 1) * sp.Rational(7, 12), (k, 0, sp.oo)
        ).doit() == sp.Rational(12, 7)

    @staticmethod
    def test_tie_y_formula() -> None:
        q = rb.rat_mat([[5]], 12)
        r = rb.rat_mat([[5], [1], [1]], 12)
        n = rb.markov_n(q)
        rn = r * n
        on = sp.ones(1, n.rows) * n
        # Example, p. 116
        assert rn == rb.rat_mat([[5], [1], [1]], 7)
        # Example, p. 116
        assert on == rb.rat_mat([[12]], 7)

    @staticmethod
    @pytest.mark.parametrize("power", [5])
    def test_tie_y_markov_powers(power: int) -> None:
        q = rb.rat_mat([[5]], 12, exact=False)
        r = rb.rat_mat([[5], [1], [1]], 12, exact=False)
        p = rb.markov(q, r)
        n = rb.markov_n(q)
        ppow = p**power
        assert rb.mat_max(ppow - rb.markov(sp.zeros(q.rows, q.cols), r * n)) < 0.05

    @staticmethod
    @pytest.mark.parametrize("trials", [100_000])
    def test_tie_y_monte_carlo(trials) -> None:
        seed = set_seed()
        both_destroyed = 0
        tie_destroyed = 0
        y_destroyed = 0
        for _ in range(trials):
            tie_hits = 0
            y_hits = 0
            while tie_hits == 0 and y_hits == 0:
                if random.randrange(6) in {0, 1, 2}:
                    y_hits += 1
                if random.randrange(6) in {0}:
                    tie_hits += 1
            if tie_hits == 1 and y_hits == 1:
                both_destroyed += 1
            elif tie_hits == 1:
                tie_destroyed += 1
            else:
                assert y_hits == 1
                y_destroyed += 1
        # Example, p. 115
        assert abs(y_destroyed / trials - 5 / 7) < 0.005, f"Bad Seed: {seed} and Trials: {trials}"
        # Example, p. 115
        assert abs(both_destroyed / trials - 1 / 7) < 0.005, f"Bad Seed: {seed} and Trials: {trials}"
        # Example, p. 115
        assert abs(tie_destroyed / trials - 1 / 7) < 0.005, f"Bad Seed: {seed} and Trials: {trials}"


class TestExciting:
    # region Expectations

    EXPECTED_EXCITING_P = sp.Matrix(
        [
            [
                sp.Rational(5, 192),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(5, 144),
                sp.Rational(5, 192),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(25, 576),
                sp.Rational(125, 1728),
                sp.Rational(25, 144),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(11, 192),
                sp.Integer(0),
                sp.Integer(0),
                sp.Rational(5, 192),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(11, 144),
                sp.Rational(11, 192),
                sp.Integer(0),
                sp.Rational(5, 144),
                sp.Rational(5, 192),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(55, 576),
                sp.Rational(275, 1728),
                sp.Rational(25, 144),
                sp.Rational(25, 576),
                sp.Rational(125, 1728),
                sp.Rational(25, 144),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(25, 576),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Rational(25, 288),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(5, 144),
                sp.Rational(5, 288),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Rational(55, 288),
                sp.Rational(25, 288),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(55, 576),
                sp.Integer(0),
                sp.Integer(0),
                sp.Rational(25, 576),
                sp.Integer(0),
                sp.Integer(0),
                sp.Rational(5, 48),
                sp.Integer(0),
                sp.Rational(25, 288),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(11, 144),
                sp.Rational(11, 288),
                sp.Integer(0),
                sp.Rational(5, 144),
                sp.Rational(5, 288),
                sp.Integer(0),
                sp.Rational(11, 48),
                sp.Rational(5, 48),
                sp.Rational(55, 288),
                sp.Rational(25, 288),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(1, 8),
                sp.Rational(4, 9),
                sp.Rational(47, 72),
                sp.Rational(23, 192),
                sp.Rational(23, 54),
                sp.Rational(47, 72),
                sp.Rational(1, 3),
                sp.Rational(19, 24),
                sp.Rational(1, 3),
                sp.Rational(19, 24),
                sp.Integer(1),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(7, 24),
                sp.Rational(5, 27),
                sp.Integer(0),
                sp.Rational(21, 32),
                sp.Rational(5, 12),
                sp.Rational(25, 144),
                sp.Rational(1, 18),
                sp.Rational(5, 288),
                sp.Rational(7, 18),
                sp.Rational(35, 288),
                sp.Integer(0),
                sp.Integer(1),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Rational(7, 192),
                sp.Rational(5, 216),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(1),
                sp.Integer(0),
            ],
            [
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Rational(1, 192),
                sp.Rational(1, 54),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(1),
            ],
        ]
    )

    EXPECTED_EXCITING_ROUNDED_P = sp.Matrix(
        [
            [0.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.03, 0.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.04, 0.07, 0.17, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.06, 0.0, 0.0, 0.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.08, 0.06, 0.0, 0.03, 0.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [
                0.1,
                0.16,
                0.17,
                0.04,
                0.07,
                0.17,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            [0.04, 0.0, 0.0, 0.0, 0.0, 0.0, 0.09, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.03, 0.02, 0.0, 0.0, 0.0, 0.0, 0.19, 0.09, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.1, 0.0, 0.0, 0.04, 0.0, 0.0, 0.1, 0.0, 0.09, 0.0, 0.0, 0.0, 0.0, 0.0],
            [
                0.08,
                0.04,
                0.0,
                0.03,
                0.02,
                0.0,
                0.23,
                0.1,
                0.19,
                0.09,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            [
                0.12,
                0.44,
                0.65,
                0.12,
                0.43,
                0.65,
                0.33,
                0.79,
                0.33,
                0.79,
                1.0,
                0.0,
                0.0,
                0.0,
            ],
            [
                0.29,
                0.19,
                0.0,
                0.66,
                0.42,
                0.17,
                0.06,
                0.02,
                0.39,
                0.12,
                0.0,
                1.0,
                0.0,
                0.0,
            ],
            [0.0, 0.0, 0.0, 0.04, 0.02, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.01, 0.02, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        ]
    )

    EXPECTED_EXCITING_N = sp.Matrix(
        [
            [
                sp.Rational(192, 187),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(1280, 34969),
                sp.Rational(192, 187),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(713200, 12483933),
                sp.Rational(2000, 22253),
                sp.Rational(144, 119),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(192, 3179),
                sp.Integer(0),
                sp.Integer(0),
                sp.Rational(192, 187),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(50432, 594473),
                sp.Rational(192, 3179),
                sp.Integer(0),
                sp.Rational(1280, 34969),
                sp.Rational(192, 187),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(220290160, 1485588027),
                sp.Rational(587600, 2648107),
                sp.Rational(3600, 14161),
                sp.Rational(713200, 12483933),
                sp.Rational(2000, 22253),
                sp.Rational(144, 119),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(2400, 49181),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Rational(288, 263),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(120794720, 2418770761),
                sp.Rational(960, 49181),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Rational(15840, 69169),
                sp.Rational(288, 263),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(25462080, 219888251),
                sp.Integer(0),
                sp.Integer(0),
                sp.Rational(2400, 49181),
                sp.Integer(0),
                sp.Integer(0),
                sp.Rational(8640, 69169),
                sp.Integer(0),
                sp.Rational(288, 263),
                sp.Integer(0),
            ],
            [
                sp.Rational(1443557753664, 10814324072431),
                sp.Rational(10184832, 219888251),
                sp.Integer(0),
                sp.Rational(120794720, 2418770761),
                sp.Rational(960, 49181),
                sp.Integer(0),
                sp.Rational(5949504, 18191447),
                sp.Rational(8640, 69169),
                sp.Rational(15840, 69169),
                sp.Rational(288, 263),
            ],
        ]
    )

    EXPECTED_EXCITING_ROUNDED_N = sp.Matrix(
        [
            [1.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.04, 1.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.06, 0.09, 1.21, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.06, 0.0, 0.0, 1.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.08, 0.06, 0.0, 0.04, 1.03, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.15, 0.22, 0.25, 0.06, 0.09, 1.21, 0.0, 0.0, 0.0, 0.0],
            [0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 1.10, 0.0, 0.0, 0.0],
            [0.05, 0.02, 0.0, 0.0, 0.0, 0.0, 0.23, 1.10, 0.0, 0.0],
            [0.12, 0.0, 0.0, 0.05, 0.0, 0.0, 0.12, 0.0, 1.10, 0.0],
            [0.13, 0.05, 0.0, 0.05, 0.02, 0.0, 0.33, 0.12, 0.23, 1.10],
        ]
    )

    EXPECTED_EXCITING_RN = sp.Matrix(
        [
            [
                sp.Rational(126998994170048261, 243224962713045621),
                sp.Rational(1216084455128, 1648502217747),
                sp.Rational(13536, 14161),
                sp.Rational(163682641957, 706500950463),
                sp.Rational(2448982, 4788441),
                sp.Rational(94, 119),
                sp.Rational(15405708, 18191447),
                sp.Rational(66804, 69169),
                sp.Rational(37788, 69169),
                sp.Rational(228, 263),
            ],
            [
                sp.Rational(114754141789105432, 243224962713045621),
                sp.Rational(428269282675, 1648502217747),
                sp.Rational(625, 14161),
                sp.Rational(5626677558214, 7771510455093),
                sp.Rational(23480665, 52672851),
                sp.Rational(25, 119),
                sp.Rational(2785739, 18191447),
                sp.Rational(2365, 69169),
                sp.Rational(31381, 69169),
                sp.Rational(35, 263),
            ],
            [
                sp.Rational(66863, 16050771),
                sp.Rational(40, 28611),
                sp.Integer(0),
                sp.Rational(36143, 944163),
                sp.Rational(40, 1683),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
            [
                sp.Rational(30265, 16050771),
                sp.Rational(32, 28611),
                sp.Integer(0),
                sp.Rational(5689, 944163),
                sp.Rational(32, 1683),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
                sp.Integer(0),
            ],
        ]
    )

    EXPECTED_EXCITING_ROUNDED_RN = sp.Matrix(
        [
            [0.52, 0.74, 0.96, 0.23, 0.51, 0.79, 0.85, 0.97, 0.55, 0.87],
            [0.47, 0.26, 0.04, 0.72, 0.45, 0.21, 0.15, 0.03, 0.45, 0.13],
            [0.0, 0.0, 0.0, 0.04, 0.02, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.01, 0.02, 0.0, 0.0, 0.0, 0.0, 0.0],
        ]
    )

    EXPECTED_EXCITING_ONER = sp.Matrix(
        [
            [
                sp.Rational(15872756208302016, 9008331952335023),
                sp.Rational(268292298048, 183166913083),
                sp.Rational(20736, 14161),
                sp.Rational(1052790220912, 863501161677),
                sp.Rational(6649264, 5852539),
                sp.Rational(144, 119),
                sp.Rational(32308416, 18191447),
                sp.Rational(84384, 69169),
                sp.Rational(91584, 69169),
                sp.Rational(288, 263),
            ]
        ]
    )

    EXPECTED_EXCITING_ROUNDED_ONER = sp.Matrix(
        [[1.8, 1.5, 1.5, 1.2, 1.1, 1.2, 1.8, 1.2, 1.3, 1.1]]
    )

    # endregion

    @staticmethod
    def test_rounding():
        p = TestExciting.EXPECTED_EXCITING_P.applyfunc(round_to(2))
        rounded_p = TestExciting.EXPECTED_EXCITING_ROUNDED_P
        # Fig 5.7, p. 118
        assert rb.mat_max(p - rounded_p) < 0.005

        n = TestExciting.EXPECTED_EXCITING_N.applyfunc(round_to(2))
        rounded_n = TestExciting.EXPECTED_EXCITING_ROUNDED_N
        # Example, p. 119
        assert rb.mat_max(n - rounded_n) < 0.005

        rn = TestExciting.EXPECTED_EXCITING_RN.applyfunc(round_to(2))
        rounded_rn = TestExciting.EXPECTED_EXCITING_ROUNDED_RN
        # Example, p. 119
        assert rb.mat_max(rn - rounded_rn) < 0.005

        oner = TestExciting.EXPECTED_EXCITING_ONER.applyfunc(round_to(1))
        rounded_oner = TestExciting.EXPECTED_EXCITING_ROUNDED_ONER
        # Example, p. 119
        assert rb.mat_max(oner - rounded_oner) < 0.005

    @staticmethod
    def test_exciting_battle_markov():
        p = rb.transition_matrix(14, rb.exciting_transition_distribution)
        # Fig 5.7, p. 118
        assert p == TestExciting.EXPECTED_EXCITING_P
        q = p[0:10, 0:10]
        r = p[10:14, 0:10]
        n = rb.markov_n(q)
        # Example, p. 119
        assert n == TestExciting.EXPECTED_EXCITING_N
        # Example, p. 119
        assert r * n == TestExciting.EXPECTED_EXCITING_RN
        # Example, p. 119
        assert (sp.ones(1, n.rows) * n) == TestExciting.EXPECTED_EXCITING_ONER

    @staticmethod
    @pytest.mark.parametrize(
        "initial_state, trials", [(i, 100_000) for i in range(1, 15)]
    )
    def test_exciting_battle_transitions_monte_carlo(initial_state, trials):
        seed = set_seed()

        new_states = defaultdict(int)
        for _ in range(trials):
            new_state = rb.combat_transition(initial_state)
            new_states[new_state] += 1
        distribution = {key: value / trials for key, value in new_states.items()}
        assert rb.is_distribution(distribution)
        column = rb.distribution_to_column(len(rb.BATTLE_STATES), distribution)
        expected_column = TestExciting.EXPECTED_EXCITING_P[:, initial_state - 1]
        ic(abs(column - expected_column))
        # Fig 5.7, p. 118
        assert rb.mat_max(column - expected_column) < 0.005, f"Bad Seed: {seed} and Trials: {trials}"

    @staticmethod
    @pytest.mark.parametrize(
        "initial_state, trials", [(i, 100_000) for i in range(1, 11)]
    )
    def test_exciting_outcomes(initial_state, trials):
        seed = set_seed()

        distribution = defaultdict(int)
        duration = 0
        for _ in range(trials):
            terminal_state, rounds = rb.run_combat(initial_state)
            distribution[terminal_state] += 1
            duration += rounds
        distribution = {key: count/trials for key, count in distribution.items()}
        ic(distribution)
        duration = duration/trials
        ic(duration)
        column = rb.distribution_to_column(len(rb.BATTLE_STATES), distribution)
        ic(column)
        column = column[10:14, 0]
        ic(column)
        expected_column = TestExciting.EXPECTED_EXCITING_RN[:, initial_state - 1]
        assert rb.mat_max(column - expected_column) < 0.005, f"Bad Seed: {seed} and Trials: {trials}"
        expected_duration = TestExciting.EXPECTED_EXCITING_ONER[:, initial_state - 1][0]
        assert abs(duration - expected_duration) < 0.005, f"Bad Seed: {seed} and Trials: {trials}"
