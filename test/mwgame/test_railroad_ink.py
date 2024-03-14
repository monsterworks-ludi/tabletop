from mwmath.tile_counter import count_free_tiles

def test_count_free_tiles() -> None:
    # Railroad Ink example, p. 57
    assert count_free_tiles(4, 3) == 21


if __name__ == "__main__":
    ...
