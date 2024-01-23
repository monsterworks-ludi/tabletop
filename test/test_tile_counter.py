import tile_counter as tc

def test_onesided_tiles():
    # example on page 62
    assert (tc.onesided_tiles(4, 2) ==
            {(0, 0, 0, 0): ((0, 0, 0, 0),),
             (0, 0, 0, 1): ((0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 0, 0), (1, 0, 0, 0)),
             (0, 0, 1, 1): ((0, 0, 1, 1), (0, 1, 1, 0), (1, 0, 0, 1), (1, 1, 0, 0)),
             (0, 1, 0, 1): ((0, 1, 0, 1), (1, 0, 1, 0)),
             (0, 1, 1, 1): ((0, 1, 1, 1), (1, 0, 1, 1), (1, 1, 0, 1), (1, 1, 1, 0)),
             (1, 1, 1, 1): ((1, 1, 1, 1),)}), "OOPS"

def test_count_onesided_tiles():
    # Carcassonne example, p. 56
    assert tc.count_onesided_tiles(4, 3) == 24
    # Cascadia example, p. 58
    assert tc.count_onesided_tiles(6, 5) == 2635


def test_count_free_tiles():
    # Railroad Ink example, p. 57
    assert tc.count_free_tiles(4, 3) == 21


if __name__ == "__main__":
    ...
