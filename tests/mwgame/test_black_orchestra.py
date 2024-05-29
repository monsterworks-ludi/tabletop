import itertools as it
import random

from pytest import mark

from mwmath.monte_carlo import set_seed, bad_seed_message
from mwmath.combinations import mult, comb

# 1 -> Eagle
# 2, 3 -> Target
# 4, 5, 6 -> Other

def test_detection_formula() -> None:
    # Formula, p. 105
    assert (
        abs(
            (
                comb(7, 0) * (1 / 6) ** 0 * (5 / 6) ** 7
                + comb(7, 1) * (1 / 6) ** 1 * (5 / 6) ** 6
            )
            - 15625 / 23328
        )
        < 1e-15
    )
    assert abs(15625 / 23328 - 0.67) < 0.005

def test_detection_exhaustive() -> None:
    trials = 0
    successes = 0
    for rolls in it.product(range(1, 7), repeat=7):
        trials += 1
        if len([roll for roll in rolls if roll == 1]) <= 1:
            successes += 1
    # Formula, p. 105
    assert trials == 279_936
    assert successes == 187_500
    assert abs(successes / trials - 15625 / 23328) < 0.005

@mark.parametrize("trials", [100_000])
def test_detection_monte_carlo(trials: int) -> None:
    seed = set_seed()
    successes = 0
    for _ in range(trials):
        eagles = 0
        for die in range(7):
            roll = random.randrange(1, 7)
            if roll == 1:
                eagles += 1
        if eagles <= 1:
            successes += 1
    # Formula, p. 105
    assert (
        abs(successes / trials - 15625 / 23328) < 0.005
    ), bad_seed_message(seed, trials)

def test_plot_success_formula() -> None:
    total = 0.0
    for k in range(4, 8):
        total += comb(7, k) * (2 / 6) ** k * (4 / 6) ** (7 - k)
    # Formula, p. 105
    assert abs(total - 379 / 2187) < 1e-15
    assert abs(379 / 2187 - 0.17) < 0.005

def test_plot_success_exhaustive() -> None:
    trials = 0
    successes = 0
    for rolls in it.product(range(1, 7), repeat=7):
        trials += 1
        if len([roll for roll in rolls if roll in {2, 3}]) >= 4:
            successes += 1
    # Formula, p. 105
    assert trials == 279_936
    assert successes == 48_512
    assert abs(successes / trials - 379 / 2187) < 0.005

@mark.parametrize("trials", [100_000])
def test_plot_success_monte_carlo(trials) -> None:
    seed = set_seed()
    successes = 0
    for _ in range(trials):
        targets = 0
        for die in range(7):
            roll = random.randrange(1, 7)
            if roll in {2, 3}:
                targets += 1
        if targets >= 4:
            successes += 1
    # Formula, p. 105
    assert (
        abs(successes / trials - 379 / 2187) < 0.005
    ), bad_seed_message(seed, trials)

def test_one_eagle_five_targets_formula() -> None:
    # Formula, p. 105
    assert (
        abs(
            mult((1, 5, 1)) * (1 / 6) ** 1 * (2 / 6) ** 5 * (3 / 6) ** 1
            - 7 / 486
        )
        < 1e-15
    )

def test_one_eagle_five_targets_exhaustive() -> None:
    trials = 0
    successes = 0
    for rolls in it.product(range(1, 7), repeat=7):
        trials += 1
        if (
            len([roll for roll in rolls if roll == 1]) == 1
            and len([roll for roll in rolls if roll in {2, 3}]) == 5
        ):
            successes += 1
    # Formula, p. 105
    assert trials == 279_936
    assert successes == 4032
    assert abs(successes / trials - 7 / 486) < 0.005

@mark.parametrize("trials", [100_000])
def test_one_eagle_five_targets_monte_carlo(trials: int) -> None:
    seed = set_seed()
    successes = 0
    for _ in range(trials):
        targets = 0
        eagles = 0
        for die in range(7):
            roll = random.randrange(1, 7)
            if roll == 1:
                eagles += 1
            if roll in {2, 3}:
                targets += 1
        if eagles == 1 and targets == 5:
            successes += 1
    # Formula, p. 105
    assert (
        abs(successes / trials - 7 / 486) < 0.005
    ), bad_seed_message(seed, trials)

def test_success_formula() -> None:
    value = 0.0
    for i, j, k in it.product(range(2), range(4, 8), range(8)):
        if i + j + k == 7:
            value += (
                mult((i, j, k)) * (1 / 6) ** i * (2 / 6) ** j * (3 / 6) ** k
            )
    # Formula, p. 105
    assert abs(value - 110 / 729) < 1e-15
    assert abs(110 / 729 - 0.15) < 0.05

def test_success_exhaustive() -> None:
    trials = 0
    successes = 0
    for rolls in it.product(range(1, 7), repeat=7):
        trials += 1
        if (
            len([roll for roll in rolls if roll == 1]) <= 1
            and len([roll for roll in rolls if roll in {2, 3}]) >= 4
        ):
            successes += 1
    # Formula, p. 105
    assert abs(successes / trials - 110 / 729) < 1e-15

@mark.parametrize("trials", [100_000])
def test_success_monte_carlo(trials: int) -> None:
    seed = set_seed()
    successes = 0
    for _ in range(trials):
        eagles = 0
        targets = 0
        for die in range(7):
            roll = random.randrange(1, 7)
            if roll == 1:
                eagles += 1
            elif roll in {2, 3}:
                targets += 1
        if eagles <= 1 and targets >= 4:
            successes += 1
    # Formula, p. 105
    assert (
        abs(successes / trials - 110 / 729) < 0.005
    ), bad_seed_message(seed, trials)

if __name__ == "__main__":
    ...
