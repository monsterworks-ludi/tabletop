import itertools as it
import random

from pytest import mark

from mwmath.monte_carlo import set_seed, bad_seed_message

from mwmath.combinations import fact, comb, mult
from mwmath.hand_counter import count_hands_permutation, count_hands_generating

def test_hand_counts() -> None:
    # Example, p. 13
    assert fact(15) / (fact(3)) ** 5 == 168_168_000
    assert mult((3, 3, 3, 3, 3)) == 168_168_000
    assert mult((3, 3, 3, 3, 3)) == 1 * comb(15, 3) * comb(12, 3) * comb(9, 3) * comb(
        6, 3
    ) * comb(3, 3)

    # flamme rouge, p. 17
    assert count_hands_permutation({3: 5}, 3) == 35, "Incorrect Hand Count"
    # flamme rouge, p. 17
    assert (
        count_hands_permutation({0: 1, 1: 1, 2: 2, 3: 1}, 3) == 14
    ), "Incorrect Hand Count"
    # flamme rouge, p. 17
    assert count_hands_generating({3: 5}, 3) == 35, "Incorrect Hand Count"
    # flamme rouge, p. 17
    assert (
        count_hands_generating({0: 1, 1: 1, 2: 2, 3: 1}, 3) == 14
    ), "Incorrect Hand Count"

def test_one_nine_formula() -> None:
    # Formula, p. 106
    assert abs(comb(2, 1) * comb(4, 2) / comb(6, 3) - 3 / 5) < 1e-15
    assert abs(3 / 5 - 0.60) < 0.005

def test_one_nine_exhaustive() -> None:
    trials = 0
    successes = 0
    deck = [(2, 0), (2, 1), (4, 0), (5, 0), (9, 0), (9, 1)]
    for perm in it.permutations(deck, 3):
        trials += 1
        nines = 0
        card: tuple[int, int]
        for card in perm:
            if card[0] == 9:
                nines += 1
        if nines == 1:
            successes += 1
    assert trials == 120
    assert successes == 72
    # Formula, p. 106
    assert abs(successes / trials - 3 / 5) < 1e-15
    assert abs(3 / 5 - 0.60) < 0.05

@mark.parametrize("trials", [100_000])
def test_one_nine_monte_carlo(trials: int) -> None:
    seed = set_seed()
    successes = 0
    deck = [(2, 0), (2, 1), (4, 0), (5, 0), (9, 0), (9, 1)]
    for _ in range(trials):
        nines = 0
        random.shuffle(deck)
        for i in range(3):
            if deck[i][0] == 9:
                nines += 1
        if nines == 1:
            successes += 1
    # Formula, p. 106
    assert (
        abs(successes / trials - 3 / 5) < 0.005
    ), bad_seed_message(seed, trials)

if __name__ == "__main__":
    ...
