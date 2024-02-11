import sympy as sp

from game.azul import use_rational, use_natural


def test_rational_dfs():
    dfs = use_rational()
    assert dfs("", 0, ["b", "r", "t"]) == ((+3, -3), ("r", "t", "b"))


def test_natural_dfs():
    dfs = use_natural()
    assert dfs("", 0, ["b", "r", "t"]) == (
        (sp.Rational(17, 5), -sp.Rational(17, 5)),
        ("t", "*"),
    )
