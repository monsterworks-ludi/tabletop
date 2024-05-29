from mwgame.grizzled import (
    assault, gas, shelling,
    count_threats, count_nonthreats
)

def test_grizzled_simple() -> None:
    t = count_threats(set())
    n = count_nonthreats({assault, gas, shelling})
    a_ = count_threats({assault})
    g_ = count_threats({gas})
    s_ = count_threats({shelling})
    a_g = count_threats({assault, gas})
    a_s = count_threats({assault, shelling})
    g_s = count_threats({gas, shelling})
    a_g_s = count_threats({assault, gas, shelling})
    # Example, p. 6
    assert (t - n) == 35  # ignore cards with none of these threats
    assert a_ == 14
    assert g_ == 14
    assert s_ == 14
    assert a_g == 3
    assert a_s == 3
    assert g_s == 3
    assert a_g_s == 2
    assert (t - n) == (a_ + g_ + s_) - (a_g + a_s + g_s) + a_g_s

if __name__ == "__main__":
    pass
