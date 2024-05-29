from mwmath.hand_counter import count_hands_generating

def test_count_hands_generating() -> None:
    # standard poker hands
    assert count_hands_generating({1: 52}, 5) == 2_598_960, "Incorrect Hand Count"

if __name__ == '__main__':
    ...
