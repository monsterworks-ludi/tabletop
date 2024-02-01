from sympy import factorial as spfactorial
from sympy.functions.combinatorial.numbers import nC as spnc
from sympy.functions.combinatorial.numbers import nP as spnp
from sympy import multinomial_coefficients as spmc

def fact(n: int) -> int:
    """

    :param n: number of objects being chosen from
    :return: n!
    """
    return int(spfactorial(n))

def perm(n: int, k: int) -> int:
    """

    :param n: number of objects being chosen from
    :param k: number of objects to be chosen
    :return: P(n, k)
    """
    if k < 0 or k > n:
        return 0
    return spnp(n, k, replacement=False)


def comb(n: int, k: int) -> int:
    """

    :param n: number of objects being chosen from
    :param k: number of objects to be chosen
    :return: C(n, k)
    """
    if k < 0 or k > n:
        return 0
    return spnc(n, k, replacement=False)


def mult(params: tuple[int, ...]) -> int:
    """

    :param params: the lower indices of the multinomial
    :return: M(params)
    """
    m = len(params)
    n = sum(params)
    if any(param < 0 for param in params):
        return 0
    return spmc(m, n)[tuple(params)]
