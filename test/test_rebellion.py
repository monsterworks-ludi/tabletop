import sys
import random
import pytest

import sympy as sp

import rebellion as rb


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
        assert p**2 == rb.rat_mat(
            [[25, 0, 0, 0], [85, 144, 0, 0], [17, 0, 144, 0], [17, 0, 0, 144]], 144
        )
        assert (p**2)[:, 0] == rb.rat_mat([[25], [85], [17], [17]], 144)
        rounded_tenth = ((p**10)[:, 0]).applyfunc(lambda x: round(x, 5))
        assert (
            rounded_tenth - sp.Matrix([[0.00016], [0.71417], [0.14283], [0.14283]])
        ).norm(2) < 0.000005
        assert rb.to_infinity(p)[:, 0] == rb.rat_mat([[0], [5], [1], [1]], 7)

    @staticmethod
    def test_tie_y_mean() -> None:
        k = sp.Symbol("k")
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
        assert rn == rb.rat_mat([[5], [1], [1]], 7)
        assert on == rb.rat_mat([[12]], 7)

    @staticmethod
    @pytest.mark.parametrize("power", [5])
    def test_tie_y_markov_powers(power: int) -> None:
        q = rb.rat_mat([[5]], 12, exact=False)
        r = rb.rat_mat([[5], [1], [1]], 12, exact=False)
        p = rb.markov(q, r)
        n = rb.markov_n(q)
        ppow = p**power
        assert (ppow - rb.markov(sp.zeros(q.rows, q.cols), r * n)).norm() < 0.05

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
        assert abs(both_destroyed / trials - 1 / 7) < 0.005
        assert abs(tie_destroyed / trials - 1 / 7) < 0.005
        assert abs(y_destroyed / trials - 5 / 7) < 0.005


class TestExciting:
    ...
