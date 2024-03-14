from pytest import mark

from mwmath.monte_carlo import set_seed
from mwgame.zombicide import hit_on_a

@mark.parametrize("trials", [100_000])
def test_one_hit_with_shortbow_monte_carlo(trials: int) -> None:
    seed = set_seed()
    successes = 0
    for _ in range(trials):
        hits = hit_on_a(3)
        if hits == 1:
            successes += 1
    # Example, p. 93
    assert (
        abs(successes / trials - 2 / 3) < 0.005
    ), f"Bad Seed: {seed} and Trials: {trials}"

@mark.parametrize("trials", [100_000])
def test_two_hits_with_sword_monte_carlo(trials: int) -> None:
    seed = set_seed()
    successes = 0
    for _ in range(trials):
        hits = hit_on_a(4) + hit_on_a(4)
        if hits == 2:
            successes += 1
    # Example, p. 93
    assert (
        abs(successes / trials - 1 / 4) < 0.005
    ), f"Bad Seed: {seed} and Trials: {trials}"

@mark.parametrize("trials", [100_000])
def test_hit_with_sword_monte_carlo(trials: int) -> None:
    seed = set_seed()
    successes = 0
    for _ in range(trials):
        hits = hit_on_a(4) + hit_on_a(4)
        if hits >= 1:
            successes += 1
    # Example, p. 95
    assert (
        abs(successes / trials - 3 / 4) < 0.005
    ), f"Bad Seed: {seed} and Trials: {trials}"

@mark.parametrize("trials", [100_000])
def test_two_hit_with_repeating_crossbow_monte_carlo(trials: int) -> None:
    seed = set_seed()
    successes = 0
    for _ in range(trials):
        hits = hit_on_a(5) + hit_on_a(5) + hit_on_a(5)
        if hits == 2:
            successes += 1
    # Example, p. 95
    assert (
        abs(successes / trials - 48 / 216) < 0.005
    ), f"Bad Seed: {seed} and Trials: {trials}"

@mark.parametrize("trials", [100_000])
def test_mean_with_repeating_crossbow_monte_carlo(trials: int) -> None:
    seed = set_seed()
    hits = 0
    for _ in range(trials):
        hits += hit_on_a(5) + hit_on_a(5) + hit_on_a(5)
    # Example, p. 99
    assert abs(hits / trials - 1) < 0.005, f"Bad Seed: {seed} and Trials: {trials}"

@mark.parametrize("trials", [100_000])
def test_exploding_die_monte_carlo(trials: int) -> None:
    seed = set_seed()
    hits = 0
    for _ in range(trials):
        hits += hit_on_a(5, critical=6)
    # Example, p. 100
    assert (
        abs(hits / trials - 2 / 5) < 0.005
    ), f"Bad Seed: {seed} and Trials: {trials}"

@mark.parametrize("trials", [100_000])
def test_mean_with_great_sword_monte_carlo(trials: int) -> None:
    seed = set_seed()
    hits = 0
    for _ in range(trials):
        hits += (
            hit_on_a(5)
            + hit_on_a(5)
            + hit_on_a(5)
            + hit_on_a(5)
            + hit_on_a(5)
        )
    # Example, p. 102
    assert (
        abs(hits / trials - 10 / 6) < 0.005
    ), f"Bad Seed: {seed} and Trials: {trials}"

@mark.parametrize("trials", [100_000])
def test_mean_with_sword_monte_carlo(trials: int) -> None:
    seed = set_seed()
    hits = 0
    for _ in range(trials):
        hits += hit_on_a(3)
    # Example, p. 102
    assert (
        abs(hits / trials - 2 / 3) < 0.005
    ), f"Bad Seed: {seed} and Trials: {trials}"

@mark.parametrize("trials", [100_000])
def test_mean_with_hand_crossbow_monte_carlo(trials: int) -> None:
    seed = set_seed()
    hits = 0
    for _ in range(trials):
        hits += hit_on_a(3) + hit_on_a(3)
    # Example, p. 102
    assert (
        abs(hits / trials - 4 / 3) < 0.005
    ), f"Bad Seed: {seed} and Trials: {trials}"


if __name__ == "__main__":
    ...
