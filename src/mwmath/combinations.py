import sympy as sp
from sympy.functions.combinatorial.numbers import nC as spnC
from sympy.functions.combinatorial.numbers import nP as spnP

def fact(n: int) -> int:
    """

    :param n: number of objects being chosen from
    :return: n!
    """
    return int(sp.factorial(n))

def perm(n: int, k: int) -> int:
    """

    :param n: number of objects being chosen from
    :param k: number of objects to be chosen
    :return: P(n, k)
    """
    if k < 0 or k > n:
        return 0
    return spnP(n, k, replacement=False)


def comb(n: int, k: int) -> int:
    """

    :param n: number of objects being chosen from
    :param k: number of objects to be chosen
    :return: C(n, k)
    """
    if k < 0 or k > n:
        return 0
    return spnC(n, k, replacement=False)


def mult(params: tuple[int, ...]) -> int:
    """

    :param params: the lower indices of the multinomial
    :return: M(params)
    """
    m = len(params)
    n = sum(params)
    if any(param < 0 for param in params):
        return 0
    return sp.multinomial_coefficients(m, n)[tuple(params)]
