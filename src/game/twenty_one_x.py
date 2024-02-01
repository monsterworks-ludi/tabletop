from itertools import combinations
from collections import defaultdict

from icecream import ic  # type: ignore

def two_x(x: int, _n: int) -> int:
    return 2 * x


def two_x_minus_six(x: int, _n: int) -> int:
    return 2 * x - 6


def ten_minus_two_x(x: int, _n: int) -> int:
    return 10 - 2 * x


def five_n(_x: int, n: int) -> int:
    return 5 * n


def two_n_minus_two_x(x: int, n: int) -> int:
    return 2 * n - 2 * x


def one_minus_x(x: int, _n: int) -> int:
    return 1 - x


def n_minus_two_x(x: int, n: int) -> int:
    return n - 2 * x


def three_n(_x: int, n: int) -> int:
    return 3 * n


def two_x_minus_ten(x: int, _n: int) -> int:
    return 2 * x - 10


def two_x_plus_four(x: int, _n: int) -> int:
    return 2 * x + 4


def seven_n(_x: int, n: int) -> int:
    return 7 * n


def four_x(x: int, _n: int) -> int:
    return 4 * x


def ten(_x: int, _n: int) -> int:
    return 10


def two_n_x(x: int, n: int) -> int:
    return 2 * n * x


def neg_three_n(_x: int, n: int) -> int:
    return -3 * n


def neg_two_x(x: int, _n: int) -> int:
    return -2 * x


def neg_five(_x: int, _n: int) -> int:
    return -5


def two_x_plus_n(x: int, n: int) -> int:
    return 2 * x + n


def n_x(x: int, n: int) -> int:
    return n * x


def six_x(x: int, _n: int) -> int:
    return 6 * x


def one_minus_n(_x: int, n: int) -> int:
    return 1 - n


LEVEL_ONE_DECK = [
    two_x,
    two_x_minus_six,
    ten_minus_two_x,
    five_n,
    two_n_minus_two_x,
    one_minus_x,
    n_minus_two_x,
    three_n,
    two_x_minus_ten,
    two_x_plus_four,
    seven_n,
    four_x,
    ten,
    two_n_x,
    neg_three_n,
    neg_two_x,
    neg_five,
    two_x_plus_n,
    n_x,
    six_x,
    one_minus_n,
]

def hand_to_value(hand: list, x: int) -> int:
    n = len(hand)
    value = 0
    for card in hand:
        value += card(x, n)
    return value

def best_value(hand) -> int:
    possible_values = [hand_to_value(hand, x) for x in range(-10, 10) if hand_to_value(hand, x) <= 21]
    if len(possible_values) == 0:
        return 42
    return max(possible_values)

if __name__ == "__main__":

    VALUES: defaultdict[int, int] = defaultdict(int)
    HANDS = 0
    for HAND in combinations(LEVEL_ONE_DECK, 2):
        # print(best_value(hand), hand)
        VALUES[best_value(HAND)] += 1
        HANDS += 1

    # for each hand, we should compute the expected value of the hand,
    # assuming we draw whenever the expected value will increase

    ic(VALUES)
    ic(HANDS)
    ic(len(LEVEL_ONE_DECK))
