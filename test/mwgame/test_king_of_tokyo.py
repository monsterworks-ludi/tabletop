from pytest import mark

from mwmath.monte_carlo import set_seed, bad_seed_message
from mwgame.king_of_tokyo import compute_score, roll
from mwmath.combinations import mult


def test_score() -> None:
    assert compute_score([1, 1, 3, 0, 0, 0]) == 0
    assert compute_score([1, 1, 3, 1, 0, 0]) == 1
    assert compute_score([1, 1, 3, 1, 1, 0]) == 2
    assert compute_score([1, 1, 3, 1, 1, 1]) == 3
    assert compute_score([1, 1, 3, 3, 3, 0]) == 3
    assert compute_score([1, 1, 3, 3, 3, 3]) == 4
    assert compute_score([1, 1, 3, 1, 3, 3]) == 4
    assert compute_score([1, 1, 3, 2, 2, 2]) == 2

def test_formula() -> None:
    def scoreline(v, i, j, k):
        return v * mult((i, j, k)) * (1 / 6) ** i * (1 / 6) ** j * (4 / 6) ** k

    # Table 5.1, p. 104
    assert (
        scoreline(1, 1, 0, 2)
        + scoreline(1, 1, 1, 1)
        + scoreline(2, 2, 1, 0)
        + scoreline(2, 2, 0, 1)
        + scoreline(3, 3, 0, 0)
        + scoreline(3, 0, 2, 1)
        + scoreline(4, 0, 3, 0)
        + scoreline(4, 1, 2, 0)
        + 2 * (1 / 6) ** 3
    ) == 159 / 216
    # Example, p. 103
    assert abs(159 / 216 - 0.74) < 0.005

def test_scores_exhaustive() -> None:
    trials = 0
    scores = 0
    for roll1 in [0, 0, 0, 1, 2, 3]:
        for roll2 in [0, 0, 0, 1, 2, 3]:
            for roll3 in [0, 0, 0, 1, 2, 3]:
                scores += compute_score([1, 1, 3, roll1, roll2, roll3])
                trials += 1
    # Example, p. 103
    assert abs(scores / trials - 159 / 216) < 0.0005

@mark.parametrize("trials", [100_000])
def test_scores_monte_carlo(trials: int) -> None:
    seed = set_seed()
    scores = 0
    for _ in range(trials):
        dice = [1, 1, 3, roll(), roll(), roll()]
        score = compute_score(dice)
        scores += score
    # Example, p. 103
    assert (
        abs(scores / trials - 159 / 216) < 0.005
    ), bad_seed_message(seed, trials)

if __name__ == "__main__":
    ...
