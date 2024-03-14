from mwmath.hand_counter import count_hands_generating

def test_count_hands_permutation() -> None:
    pass
    # brass birmingham, p. 18, requires roughly 34 years to complete on my computer
    # assert count_hands_permutation({1: 2, 2: 12, 3: 7, 4: 1, 5: 1, 8: 1}, 8) == 5_739_197, "Incorrect Hand Count"

def test_count_hands_generating() -> None:
    # brass birmingham, p. 18
    assert count_hands_generating({1: 2, 2: 12, 3: 7, 4: 1, 5: 1, 8: 1}, 8) == 5_739_197, "Incorrect Hand Count"

if __name__ == '__main__':
    ...
