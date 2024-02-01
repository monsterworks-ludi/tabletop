import itertools as it
# todo: shift random inside kt and zc
import random

from pytest import mark
from icecream import ic  # type: ignore

import mwmath.monte_carlo as mc
import game.king_of_tokyo as kt
import game.zombicide as zc
from mwmath.combinations import mult, comb


class TestZombicide:
    @staticmethod
    @mark.parametrize("trials", [100_000])
    def test_one_hit_with_shortbow_monte_carlo(trials: int) -> None:
        seed = mc.set_seed()
        successes = 0
        for _ in range(trials):
            hits = zc.hit_on_a(3)
            if hits == 1:
                successes += 1
        # Example, p. 93
        assert (
            abs(successes / trials - 2 / 3) < 0.005
        ), f"Bad Seed: {seed} and Trials: {trials}"

    @staticmethod
    @mark.parametrize("trials", [100_000])
    def test_two_hits_with_sword_monte_carlo(trials: int) -> None:
        seed = mc.set_seed()
        successes = 0
        for _ in range(trials):
            hits = zc.hit_on_a(4) + zc.hit_on_a(4)
            if hits == 2:
                successes += 1
        # Example, p. 93
        assert (
            abs(successes / trials - 1 / 4) < 0.005
        ), f"Bad Seed: {seed} and Trials: {trials}"

    @staticmethod
    @mark.parametrize("trials", [100_000])
    def test_hit_with_sword_monte_carlo(trials: int) -> None:
        seed = mc.set_seed()
        successes = 0
        for _ in range(trials):
            hits = zc.hit_on_a(4) + zc.hit_on_a(4)
            if hits >= 1:
                successes += 1
        # Example, p. 95
        assert (
            abs(successes / trials - 3 / 4) < 0.005
        ), f"Bad Seed: {seed} and Trials: {trials}"

    @staticmethod
    @mark.parametrize("trials", [100_000])
    def test_two_hit_with_repeating_crossbow_monte_carlo(trials: int) -> None:
        seed = mc.set_seed()
        successes = 0
        for _ in range(trials):
            hits = zc.hit_on_a(5) + zc.hit_on_a(5) + zc.hit_on_a(5)
            if hits == 2:
                successes += 1
        # Example, p. 95
        assert (
            abs(successes / trials - 48 / 216) < 0.005
        ), f"Bad Seed: {seed} and Trials: {trials}"

    @staticmethod
    @mark.parametrize("trials", [100_000])
    def test_mean_with_repeating_crossbow_monte_carlo(trials: int) -> None:
        seed = mc.set_seed()
        hits = 0
        for _ in range(trials):
            hits += zc.hit_on_a(5) + zc.hit_on_a(5) + zc.hit_on_a(5)
        # Example, p. 99
        assert abs(hits / trials - 1) < 0.005, f"Bad Seed: {seed} and Trials: {trials}"

    @staticmethod
    @mark.parametrize("trials", [100_000])
    def test_exploding_die_monte_carlo(trials: int) -> None:
        seed = mc.set_seed()
        hits = 0
        for _ in range(trials):
            hits += zc.hit_on_a(5, critical=6)
        # Example, p. 100
        assert (
            abs(hits / trials - 2 / 5) < 0.005
        ), f"Bad Seed: {seed} and Trials: {trials}"

    @staticmethod
    @mark.parametrize("trials", [100_000])
    def test_mean_with_great_sword_monte_carlo(trials: int) -> None:
        seed = mc.set_seed()
        hits = 0
        for _ in range(trials):
            hits += (
                zc.hit_on_a(5)
                + zc.hit_on_a(5)
                + zc.hit_on_a(5)
                + zc.hit_on_a(5)
                + zc.hit_on_a(5)
            )
        # Example, p. 102
        assert (
            abs(hits / trials - 10 / 6) < 0.005
        ), f"Bad Seed: {seed} and Trials: {trials}"

    @staticmethod
    @mark.parametrize("trials", [100_000])
    def test_mean_with_sword_monte_carlo(trials: int) -> None:
        seed = mc.set_seed()
        hits = 0
        for _ in range(trials):
            hits += zc.hit_on_a(3)
        # Example, p. 102
        assert (
            abs(hits / trials - 2 / 3) < 0.005
        ), f"Bad Seed: {seed} and Trials: {trials}"

    @staticmethod
    @mark.parametrize("trials", [100_000])
    def test_mean_with_hand_crossbow_monte_carlo(trials: int) -> None:
        seed = mc.set_seed()
        hits = 0
        for _ in range(trials):
            hits += zc.hit_on_a(3) + zc.hit_on_a(3)
        # Example, p. 102
        assert (
            abs(hits / trials - 4 / 3) < 0.005
        ), f"Bad Seed: {seed} and Trials: {trials}"


class TestKingOfTokyo:
    @staticmethod
    def test_score() -> None:
        assert kt.score([1, 1, 3, 0, 0, 0]) == 0
        assert kt.score([1, 1, 3, 1, 0, 0]) == 1
        assert kt.score([1, 1, 3, 1, 1, 0]) == 2
        assert kt.score([1, 1, 3, 1, 1, 1]) == 3
        assert kt.score([1, 1, 3, 3, 3, 0]) == 3
        assert kt.score([1, 1, 3, 3, 3, 3]) == 4
        assert kt.score([1, 1, 3, 1, 3, 3]) == 4
        assert kt.score([1, 1, 3, 2, 2, 2]) == 2

    @staticmethod
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

    @staticmethod
    def test_scores_exhaustive() -> None:
        trials = 0
        scores = 0
        for roll1 in [0, 0, 0, 1, 2, 3]:
            for roll2 in [0, 0, 0, 1, 2, 3]:
                for roll3 in [0, 0, 0, 1, 2, 3]:
                    scores += kt.score([1, 1, 3, roll1, roll2, roll3])
                    trials += 1
        # Example, p. 103
        assert abs(scores / trials - 159 / 216) < 0.0005

    @staticmethod
    @mark.parametrize("trials", [100_000])
    def test_scores_monte_carlo(trials: int) -> None:
        seed = mc.set_seed()
        scores = 0
        for _ in range(trials):
            dice = [1, 1, 3, kt.roll(), kt.roll(), kt.roll()]
            score = kt.score(dice)
            scores += score
        # Example, p. 103
        assert (
            abs(scores / trials - 159 / 216) < 0.005
        ), f"Bad Seed: {seed} and Trials: {trials}"


class TestBlackOrchestra:
    # 1 -> Eagle
    # 2, 3 -> Target
    # 4, 5, 6 -> Other

    @staticmethod
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
            < 10**-15
        )
        assert abs(15625 / 23328 - 0.67) < 0.005

    @staticmethod
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

    @staticmethod
    @mark.parametrize("trials", [100_000])
    def test_detection_monte_carlo(trials: int) -> None:
        seed = mc.set_seed()
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
        ), f"Bad Seed: {seed} and Trials: {trials}"

    @staticmethod
    def test_plot_success_formula() -> None:
        total = 0.0
        for k in range(4, 8):
            total += comb(7, k) * (2 / 6) ** k * (4 / 6) ** (7 - k)
        # Formula, p. 105
        assert abs(total - 379 / 2187) < 10**-15
        assert abs(379 / 2187 - 0.17) < 0.005

    @staticmethod
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

    @staticmethod
    @mark.parametrize("trials", [100_000])
    def test_plot_success_monte_carlo(trials) -> None:
        seed = mc.set_seed()
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
        ), f"Bad Seed: {seed} and Trials: {trials}"

    @staticmethod
    def test_one_eagle_five_targets_formula() -> None:
        # Formula, p. 105
        assert (
            abs(
                mult((1, 5, 1)) * (1 / 6) ** 1 * (2 / 6) ** 5 * (3 / 6) ** 1
                - 7 / 486
            )
            < 10**-15
        )

    @staticmethod
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

    @staticmethod
    @mark.parametrize("trials", [100_000])
    def test_one_eagle_five_targets_monte_carlo(trials: int) -> None:
        seed = mc.set_seed()
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
        ), f"Bad Seed: {seed} and Trials: {trials}"

    @staticmethod
    def test_success_formula() -> None:
        value = 0.0
        for i, j, k in it.product(range(2), range(4, 8), range(8)):
            if i + j + k == 7:
                value += (
                    mult((i, j, k)) * (1 / 6) ** i * (2 / 6) ** j * (3 / 6) ** k
                )
        # Formula, p. 105
        assert abs(value - 110 / 729) < 10**-15
        assert abs(110 / 729 - 0.15) < 0.05

    @staticmethod
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
        assert abs(successes / trials - 110 / 729) < 10**-15

    @staticmethod
    @mark.parametrize("trials", [100_000])
    def test_success_monte_carlo(trials: int) -> None:
        seed = mc.set_seed()
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
        ), f"Bad Seed: {seed} and Trials: {trials}"


class TestFlammeRouge:
    @staticmethod
    def test_one_nine_formula() -> None:
        # Formula, p. 106
        assert abs(comb(2, 1) * comb(4, 2) / comb(6, 3) - 3 / 5) < 10**-15
        assert abs(3 / 5 - 0.60) < 0.005

    @staticmethod
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
        assert abs(successes / trials - 3 / 5) < 10**-15
        assert abs(3 / 5 - 0.60) < 0.05

    @staticmethod
    @mark.parametrize("trials", [100_000])
    def test_one_nine_monte_carlo(trials: int) -> None:
        seed = mc.set_seed()
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
        ), f"Bad Seed: {seed} and Trials: {trials}"


if __name__ == "__main__":
    ...
