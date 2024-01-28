import sys
import random
import pytest
import itertools as it

from combinations import *

import oathsworn as os


def set_seed() -> int:
    seed = random.randrange(sys.maxsize)
    random.seed(seed)
    return seed


class TestOathsworn:
    Expected_Card_Hit_Probabilities = (
        1,
        1,
        46 / 51,
        77 / 102,
        121 / 204,
        209 / 476,
        473 / 1547,
        44 / 221,
        53 / 442,
        29 / 442,
        7 / 221,
    )

    Expected_Dice_Hit_Probabilities = (
        1,
        1,
        8 / 9,
        20 / 27,
        16 / 27,
        112 / 243,
        256 / 729,
        64 / 243,
        1280 / 6561,
        2816 / 19683,
        2048 / 19683,
    )

    @staticmethod
    @pytest.mark.parametrize("k", range(11))
    def test_card_hit_formula(k: int) -> None:
        hit_probability = (
            comb(6, 0) * comb(12, k) + comb(6, 1) * comb(12, k - 1)
        ) / comb(18, k)
        # Table 5.3, p. 109
        assert (
            abs(hit_probability - TestOathsworn.Expected_Card_Hit_Probabilities[k])
            < 10**-15
        )

    @staticmethod
    @pytest.mark.parametrize("k", range(11))
    def test_card_hit_exhaustive(k: int) -> None:
        """

        :param k:
        :return:

        Running times

        k = 0, 1, 2, 3:
            0 ms
        k = 4:
            14 ms
        k = 5:
            224 ms
        k = 6:
            3 sec 62 ms = 3062 ms
        k = 7:
            38 sec 177 ms = 38177 ms
        k = 8:
            7 min 11 sec = 431000 ms
        k = 9:
            1 hr 13 min = 4380000 ms
        k = 10:
            12 hr?
        """
        trials = 0
        hits = 0
        for hand in it.permutations(os.WHITE_DECK, k):
            trials += 1
            if os.hit_drawing(list(hand)):
                hits += 1
        # Table 5.3, p. 109
        assert (
            abs(hits / trials - TestOathsworn.Expected_Card_Hit_Probabilities[k])
            < 10**-15
        )

    @staticmethod
    @pytest.mark.parametrize("trials, k", [(100_000, k) for k in range(11)])
    def test_card_hit_monte_carlo(trials: int, k: int) -> None:
        seed = set_seed
        hits = 0
        for _ in range(trials):
            deck = os.shuffled(os.WHITE_DECK)
            if os.hit_drawing(k, deck):
                hits += 1
        # Table 5.3, p. 109
        assert (
            abs(hits / trials - TestOathsworn.Expected_Card_Hit_Probabilities[k])
            < 0.005
        ), f"Bad Seed: {seed} and Trials: {trials}"

    @staticmethod
    @pytest.mark.parametrize("n", range(11))
    def test_dice_hit_formula(n: int) -> None:
        hit_probability = comb(n, 0) * (2 / 6) ** 0 * (4 / 6) ** n + comb(n, 1) * (
            2 / 6
        ) ** 1 * (4 / 6) ** (n - 1)
        # Table 5.3, p. 109
        assert (
            abs(hit_probability - TestOathsworn.Expected_Dice_Hit_Probabilities[n])
            < 10**-15
        )

    @staticmethod
    def test_dice_hit_exhaustive() -> None:
        """I don't know a clean formula here since it is possible that there are an unending sequence of explosions."""
        return

    @staticmethod
    @pytest.mark.parametrize("trials, n", [(100_000, n) for n in range(11)])
    def test_dice_hit_monte_carlo(trials, n) -> None:
        seed = set_seed()
        hits = 0
        for _ in range(trials):
            if os.hit_rolling(n, os.WHITE_DIE):
                hits += 1
        # Table 5.3, p. 109
        assert (
            abs(hits / trials - TestOathsworn.Expected_Dice_Hit_Probabilities[n])
            < 0.005
        ), f"Bad Seed: {seed} and Trials: {trials}"

    Expected_White_Card_Damage = (
        0 / 4896,
        86292 / 73440,
        47 / 20,
        193_527 / 61_880,
        157_627 / 46_410,
        3.22,
        2.73,
        2.09,
        1.44,
        0.88,
        0.47,
    )

    Expected_White_Dice_Damage = (
        0,
        6 / 5,
        12 / 5,
        16 / 5,
        32 / 9,
        32 / 9,
        448 / 135,
        3584 / 1215,
        1024 / 405,
        512 / 243,
        11264 / 6561,
    )

    @staticmethod
    def test_white_deck_damage_formula() -> None:
        """I do not know of a way to compute this with a formula."""
        return

    @staticmethod
    @pytest.mark.parametrize("k", range(11))
    def test_white_deck_damage_exhaustive(k: int):
        """

        Running Times
        k = 0:
            0 ms
        k = 1:
            15 ms
        k = 2:
            318 ms
        k = 3:
            5313 ms
        k = 4:
            1 min 14 sec = 74000 ms
        k = 5:
            14 min 49 sec = 889000 ms
        k = 6:
            2 hr 35 min = 7235000 ms
        k = 7:
            ?
        k = 8:
            ?
        k = 9:
            ?
        k = 10:
            ?

        :param k:
        :return:
        """
        trials = 0
        damage = 0
        max_exploding_cards = 3
        for shuffle in it.permutations(os.WHITE_DECK, k + max_exploding_cards):
            trials += 1
            damage += os.damage_drawing(k, list(shuffle))
        print(f"{k}, {damage}, {trials}")
        # Table 5.4, p. 110
        assert abs(damage / trials - TestOathsworn.Expected_White_Card_Damage[k]) < 0.05

    @staticmethod
    @pytest.mark.parametrize("trials, k", [(10_000_000, k) for k in range(11)])
    def test_white_deck_damage_monte_carlo(trials: int, k: int):
        seed = set_seed
        damage = 0
        for _ in range(trials):
            deck = os.shuffled(os.WHITE_DECK)
            damage += os.damage_drawing(k, deck)
        # Table 5.4, p. 110
        assert (
            abs(damage / trials - TestOathsworn.Expected_White_Card_Damage[k]) < 0.005
        ), f"Bad Seed: {seed} and Trials: {trials}"

    @staticmethod
    @pytest.mark.parametrize("n", range(11))
    def test_white_dice_damage_formula(n: int) -> None:
        damage = 0.0
        for blanks, ones, twos in it.product(
            range(2), range(n + 1), range(n + 1)
        ):
            explosions = n - (blanks + ones + twos)
            damage += (
                (0 * blanks + 1 * ones + 2 * twos + (2 + 6 / 5) * explosions)
                * mult((blanks, ones, twos, explosions))  # maybe I should use packing to make this easier to read
                * (2/6)**blanks * (2/6)**ones * (1/6)**twos * (1/6)**explosions
            )
        # Table 5.4, p. 110
        assert (
            abs(damage - TestOathsworn.Expected_White_Dice_Damage[n])
            < 10**-14
            # tolerance of 10**-15 doesn't work with n = 8
            # denominator is 405, maybe that just doesn't translate well to binary
        )

    @staticmethod
    @pytest.mark.parametrize("n", range(11))
    def test_white_dice_damage_exhaustive(n: int) -> None:
        """I'm not sure how to do this since it is possible that we roll an unending sequence of explosions."""
        return

    @staticmethod
    @pytest.mark.parametrize("trials, n", [(10_000_000, n) for n in range(11)])
    def test_white_dice_damage_monte_carlo(trials: int, n: int) -> None:
        seed = set_seed()
        damage = 0
        for _ in range(trials):
            damage += os.damage_rolling(n, os.WHITE_DIE)
        # Table 5.4, p. 110
        assert (
            abs(damage / trials - TestOathsworn.Expected_White_Dice_Damage[n]) < 0.005
        ), f"Bad Seed: {seed} and Trials: {trials}"
        return

if __name__ == "__main__":
    ...
