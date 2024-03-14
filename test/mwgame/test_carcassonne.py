from mwmath.tile_counter import count_onesided_tiles


def test_count_onesided_tiles() -> None:
    # Carcassonne example, p. 56
    assert count_onesided_tiles(4, 3) == 24


if __name__ == "__main__":
    ...
