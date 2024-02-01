from icecream import ic  # type: ignore
from math import hand_counter as hc

ic.disable()

class TestHandCounter:

    @staticmethod
    def test_count_hands_permutation() -> None:
        # flamme rouge, p. 17
        assert hc.count_hands_permutation({3: 5}, 3) == 35, "Incorrect Hand Count"
        # flamme rouge, p. 17
        assert hc.count_hands_permutation({0: 1, 1: 1, 2: 2, 3: 1}, 3) == 14, "Incorrect Hand Count"
        # brass birmingham, p. 18, requires roughly 34 years to complete on my computer
        # assert count_hands_permutation({1: 2, 2: 12, 3: 7, 4: 1, 5: 1, 8: 1}, 8) == 5_739_197, "Incorrect Hand Count"

    @staticmethod
    def test_count_hands_generating() -> None:
        # standard poker hands
        assert hc.count_hands_generating({1: 52}, 5) == 2_598_960, "Incorrect Hand Count"
        # flamme rouge, p. 17
        assert hc.count_hands_generating({3: 5}, 3) == 35, "Incorrect Hand Count"
        # flamme rouge, p. 17
        assert hc.count_hands_generating({0: 1, 1: 1, 2: 2, 3: 1}, 3) == 14, "Incorrect Hand Count"
        # brass birmingham, p. 18
        assert hc.count_hands_generating({1: 2, 2: 12, 3: 7, 4: 1, 5: 1, 8: 1}, 8) == 5_739_197, "Incorrect Hand Count"

if __name__ == '__main__':
    ...
