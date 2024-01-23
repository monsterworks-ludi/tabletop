from combinations import *
import counting as ct
from counting import a, g, s

# Testing of very basic counting from Section 1.1 -- 1.3

def test_grizzled():
    # Example, p. 6
    t = ct.count_threats(tuple())
    a_ = ct.count_threats((a,))
    g_ = ct.count_threats((g,))
    s_ = ct.count_threats((s,))
    a_g = ct.count_threats((a, g))
    a_s = ct.count_threats((a, s))
    g_s = ct.count_threats((g, s))
    a_g_s = ct.count_threats((a, g, s))
    assert t == 35
    assert a_ == 14
    assert g_ == 14
    assert s_ == 14
    assert a_g == 3
    assert a_s == 3
    assert g_s == 3
    assert a_g_s == 2
    assert t == (a_ + g_ + s_) - (a_g + a_s + g_s) + a_g_s


def test_cascadia():
    # Example, p. 8
    assert 5 * 20 == 100
    # Example, p. 8
    assert 85 * 100 == 8_500
    # Example, p. 9
    assert 3**5 == 243
    # Example, p. 9
    assert 85 * 84 * 83 * 82 == 48_594_840
    assert perm(85, 4) == 48_594_840
    # Example, p. 10
    assert perm(45, 9) == 321_570_878_428_800


def test_conventions():
    # Conventions, p. 11
    assert 0**0 == 1
    assert fact(0) == 1
    assert perm(1, -1) == 0
    assert perm(1, 2) == 0
    # Conventions, p. 14
    assert mult((1, 1, -1)) == 0


def test_ark_nova():
    # Example, p. 12
    assert perm(11, 2) / fact(2) == 55
    assert comb(11, 2) == 55
    assert perm(212, 8) / fact(8) == 88_535_640_906_570
    assert comb(212, 8) == 88_535_640_906_570
    assert (
        perm(11, 2) / fact(2) * perm(212, 8) / fact(8)
        == 4_869_460_249_861_350
    )


def test_flamme_rouge():
    # Example, p. 13
    assert fact(15) / (fact(3)) ** 5 == 168_168_000
    assert mult((3, 3, 3, 3, 3)) == 168_168_000
    assert (mult((3, 3, 3, 3, 3)) == 1 * comb(15, 3) * comb(12, 3)
            * comb(9, 3) * comb(6, 3) * comb(3, 3))


if __name__ == "__main__":
    ...
