from mwmath.tile_counter import onesided_tiles

def test_onesided_tiles() -> None:
    # example on page 62
    assert (onesided_tiles(4, 2) ==
            {(0, 0, 0, 0): {(0, 0, 0, 0)},
             (0, 0, 0, 1): {(0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 0, 0), (1, 0, 0, 0)},
             (0, 0, 1, 1): {(0, 0, 1, 1), (0, 1, 1, 0), (1, 0, 0, 1), (1, 1, 0, 0)},
             (0, 1, 0, 1): {(0, 1, 0, 1), (1, 0, 1, 0)},
             (0, 1, 1, 1): {(0, 1, 1, 1), (1, 0, 1, 1), (1, 1, 0, 1), (1, 1, 1, 0)},
             (1, 1, 1, 1): {(1, 1, 1, 1)}
             }
            )

if __name__ == "__main__":
    ...
