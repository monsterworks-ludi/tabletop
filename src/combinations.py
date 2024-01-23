from scipy.special import perm as spperm  # type: ignore
from scipy.special import comb as spcomb  # type: ignore
from sympy import factorial as spfactorial
from sympy import multinomial_coefficients as spmc

# making these type safe (and probably slightly less efficient)

def fact(n: int) -> int:
    return int(spfactorial(n))

def perm(n: int, k: int) -> int:
    return int(spperm(n, k, exact=True))


def comb(n: int, k: int) -> int:
    return int(spcomb(n, k, exact=True, repetition=False))


def mult(params: tuple[int, ...]) -> int:
    m = len(params)
    n = sum(params)
    if any(param < 0 for param in params):
        return 0
    return spmc(m, n)[tuple(params)]
