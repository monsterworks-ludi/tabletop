from mwmath.combinations import (
    fact, perm, comb, mult
)

def test_conventions() -> None:
    # Conventions, p. 11
    assert 0**0 == 1
    assert fact(0) == 1
    assert perm(1, -1) == 0
    assert perm(1, 2) == 0
    assert comb(1, -1) == 0
    assert comb(1, 2) == 0
    # Conventions, p. 14
    assert mult((1, 1, -1)) == 0

if __name__ == "__main__":
    ...
