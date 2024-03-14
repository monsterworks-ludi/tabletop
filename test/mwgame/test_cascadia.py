from mwmath.combinations import perm
from mwmath.tile_counter import count_onesided_tiles

def test_cascadia() -> None:
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

def test_count_onesided_tiles() -> None:
    # Cascadia example, p. 58
    assert count_onesided_tiles(6, 5) == 2635

if __name__ == "__main__":
    ...
