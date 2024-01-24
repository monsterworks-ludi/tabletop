from sympy import factorial as spfactorial
from sympy.functions.combinatorial.numbers import nC as spnc
from sympy.functions.combinatorial.numbers import nP as spnp
from sympy import multinomial_coefficients as spmc

# making these type safe (and probably slightly less efficient)

def fact(n: int) -> int:
    return int(spfactorial(n))

def perm(n: int, k: int) -> int:
    return int(spnp(n, k, replacement=False))


def comb(n: int, k: int) -> int:
    return int(spnc(n, k, replacement=False))


def mult(params: tuple[int, ...]) -> int:
    m = len(params)
    n = sum(params)
    if any(param < 0 for param in params):
        return 0
    return spmc(m, n)[tuple(params)]
