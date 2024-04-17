import itertools as it

from pytest import mark

from mwmath.combinations import comb, mult
from mwmath.monte_carlo import set_seed, bad_seed_message
from mwgame.oathsworn import (
    WHITE_DIE, WHITE_DECK, BIG_WHITE_DECK,
    shuffled,
    hit_drawing, hit_rolling,
    damage_drawing, damage_rolling,
)

# setting this False will skip tests with runtimes over 15 seconds
run_long_tests: bool = False

class TestOathsworn:
    # region Constants

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

    Printed_Card_Hit_Probabilities = (
        1.00,
        1.00,
        0.90,
        0.75,
        0.59,
        0.44,
        0.31,
        0.20,
        0.12,
        0.07,
        0.03,
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

    Printed_Dice_Hit_Probabilities = (
        1.00,
        1.00,
        0.89,
        0.74,
        0.59,
        0.46,
        0.35,
        0.26,
        0.20,
        0.14,
        0.10,
    )

    Expected_White_Card_Damage = (
        0 / 1,
        47 / 40,
        47 / 20,
        193_527 / 61_880,
        157_627 / 46_410,
        656_611 / 204_204,
        463_753 / 170_170,
        912_919 / 437_580,
        842 / 585,
        85_919 / 97_240,
        96_011 / 204_204,
    )

    Printed_White_Card_Damage = (
        0.00,
        1.18,
        2.35,
        3.13,
        3.40,
        3.22,
        2.73,
        2.09,
        1.44,
        0.88,
        0.47,
    )

    Expected_Big_White_Card_Damage = (
        0,
        227 / 190,
        227 / 95,
        145_439_259 / 45_673_910,
        7_965_689_344 / 2_260_858_545,
        81_524_060_693 / 23_348_502_792,
        29_560_614_227_209 / 9_203_201_517_180,
        5_491_211_230_699_453 / 1_962_791_887_209_480,
        # C floats have 24 bits of precision,
        # so we cannot expect more than 7 digits out of these
        2.335312,
        1.883082,
        1.474792,
    )

    Printed_Big_White_Card_Damage = (
        0.00,
        1.19,
        2.39,
        3.18,
        3.52,
        3.49,
        3.21,
        2.80,
        2.34,
        1.88,
        1.47,
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

    Printed_White_Dice_Damage = (
        0.00,
        1.20,
        2.40,
        3.20,
        3.56,
        3.56,
        3.32,
        2.95,
        2.53,
        2.11,
        1.72,
    )

    # endregion

    # region Rounding

    @staticmethod
    @mark.parametrize("k", range(11))
    def test_dice_hit_rounding(k: int) -> None:
        expected = TestOathsworn.Expected_Dice_Hit_Probabilities
        printed = TestOathsworn.Printed_Dice_Hit_Probabilities
        assert abs(round(expected[k], 2) - printed[k]) < 0.005

    @staticmethod
    @mark.parametrize("k", range(11))
    def test_card_hit_rounding(k: int) -> None:
        expected = TestOathsworn.Expected_Card_Hit_Probabilities
        printed = TestOathsworn.Printed_Card_Hit_Probabilities
        assert abs(round(expected[k], 2) - printed[k]) < 0.005

    @staticmethod
    @mark.parametrize("k", range(11))
    def test_white_card_damage_rounding(k: int) -> None:
        expected = TestOathsworn.Expected_White_Card_Damage
        printed = TestOathsworn.Printed_White_Card_Damage
        assert abs(round(expected[k], 2) - printed[k]) < 0.005

    @staticmethod
    @mark.parametrize("k", range(11))
    def test_big_white_card_damage_rounding(k: int) -> None:
        expected = TestOathsworn.Expected_Big_White_Card_Damage
        printed = TestOathsworn.Printed_Big_White_Card_Damage
        assert abs(round(expected[k], 2) - printed[k]) < 0.005

    @staticmethod
    @mark.parametrize("k", range(11))
    def test_white_dice_damage_rounding(k: int) -> None:
        expected = TestOathsworn.Expected_White_Dice_Damage
        printed = TestOathsworn.Printed_White_Dice_Damage
        assert abs(round(expected[k], 2) - printed[k]) < 0.005

    # endregion

    # region Card Hit

    @staticmethod
    @mark.parametrize("k", range(11))
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
    @mark.parametrize("k", range(11 if run_long_tests else 7))
    def test_card_hit_exhaustive(k: int) -> None:
        """
        Runtimes over 5 min for k = 8, over 1 hour for k = 9, over 11 hours for k = 10.
        """
        trials = 0
        hits = 0
        for hand in it.permutations(WHITE_DECK, k):
            trials += 1
            if hit_drawing(k, hand):
                hits += 1
        # Table 5.3, p. 109
        assert (
            abs(hits / trials - TestOathsworn.Expected_Card_Hit_Probabilities[k])
            < 10**-15
        )

    @staticmethod
    @mark.parametrize("trials, k", [(100_000, k) for k in range(11)])
    def test_card_hit_monte_carlo(trials: int, k: int) -> None:
        seed = set_seed()
        hits = 0
        for _ in range(trials):
            deck = shuffled(WHITE_DECK)
            if hit_drawing(k, deck):
                hits += 1
        # Table 5.3, p. 109
        assert (
            abs(hits / trials - TestOathsworn.Expected_Card_Hit_Probabilities[k])
            < 0.005
        ), bad_seed_message(seed, trials)

    # endregion

    # region Dice Hit

    @staticmethod
    @mark.parametrize("n", range(11))
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
    @mark.parametrize("trials, n", [(100_000, n) for n in range(11)])
    def test_dice_hit_monte_carlo(trials, n) -> None:
        seed = set_seed()
        hits = 0
        for _ in range(trials):
            if hit_rolling(n, WHITE_DIE):
                hits += 1
        # Table 5.3, p. 109
        assert (
            abs(hits / trials - TestOathsworn.Expected_Dice_Hit_Probabilities[n])
            < 0.005
        ), bad_seed_message(seed, trials)

    # endregion

    # region White Deck Damage

    @staticmethod
    def test_white_deck_damage_formula() -> None:
        """I do not know of a way to compute this with a formula."""
        return

    @staticmethod
    @mark.parametrize("k", range(11 if run_long_tests else 6))
    def big_test_white_deck_damage_exhaustive(k: int):
        """
        Runtimes over 2 hours for k ≥ 6
        """
        trials = 0
        damage = 0
        max_exploding_cards = (
            3  # should get this number by counting the exploding cards
        )
        for shuffle in it.permutations(WHITE_DECK, k + max_exploding_cards):
            trials += 1
            damage += damage_drawing(k, shuffle)
        # Table 5.4, p. 110
        assert (
            abs(damage / trials - TestOathsworn.Expected_White_Card_Damage[k])
            < 10**-15
        )

    @staticmethod
    @mark.parametrize("trials, k", [(100_000, k) for k in range(11)])
    def test_white_deck_damage_monte_carlo(trials: int, k: int):
        seed = set_seed()
        damage = 0
        for _ in range(trials):
            deck = shuffled(WHITE_DECK)
            damage += damage_drawing(k, deck)
        # Table 5.4, p. 110
        assert (
            abs(damage / trials - TestOathsworn.Expected_White_Card_Damage[k]) < 0.1
        ), bad_seed_message(seed, trials)

    # endregion

    # region Big White Deck Damage

    @staticmethod
    def test_big_white_deck_damage_formula() -> None:
        """I do not know of a way to compute this with a formula."""
        return

    @staticmethod
    @mark.parametrize("k", range(11))
    def big_test_big_white_deck_damage_exhaustive(k: int):
        """
        Even if k = 0, there are roughly 6 * 10^28 shuffles to exam,
        so we won't even try to run this one
        """
        trials = 0
        damage = 0
        max_exploding_cards = sum([1 for card in BIG_WHITE_DECK if card.exploding])
        assert max_exploding_cards == 15
        for shuffle in it.permutations(BIG_WHITE_DECK, k + max_exploding_cards):
            trials += 1
            damage += damage_drawing(k, shuffle)
        # Table 5.4, p. 110
        assert (
            abs(damage / trials - TestOathsworn.Expected_Big_White_Card_Damage[k])
            < 10**-15
        )

    @staticmethod
    @mark.parametrize("trials, k", [(100_000, k) for k in range(11)])
    def test_big_white_deck_damage_monte_carlo(trials: int, k: int):
        seed = set_seed()
        damage = 0
        for _ in range(trials):
            deck = shuffled(BIG_WHITE_DECK)
            damage += damage_drawing(k, deck)
        # Table 5.4, p. 110
        assert (
            abs(damage / trials - TestOathsworn.Expected_Big_White_Card_Damage[k])
            < 0.02
        ), bad_seed_message(seed, trials)

    # endregion

    # region White Dice Damage

    @staticmethod
    @mark.parametrize("n", range(11))
    def test_white_dice_damage_formula(n: int) -> None:
        damage = 0.0
        for blanks, ones, twos in it.product(range(2), range(n + 1), range(n + 1)):
            explosions = n - (blanks + ones + twos)
            damage += (
                (0 * blanks + 1 * ones + 2 * twos + (2 + 6 / 5) * explosions)
                * mult(
                    (blanks, ones, twos, explosions)
                )  # maybe I should use packing to make this easier to read
                * (2 / 6) ** blanks
                * (2 / 6) ** ones
                * (1 / 6) ** twos
                * (1 / 6) ** explosions
            )
        # Table 5.4, p. 110
        assert (
            # should this be a relative error?
            abs(damage - TestOathsworn.Expected_White_Dice_Damage[n])
            < 10**-14
            # tolerance of 10**-15 doesn't work with n = 8
            # denominator is 405, maybe that just doesn't translate well to binary
        )

    @staticmethod
    @mark.parametrize("n", range(11))
    def test_white_dice_damage_exhaustive(n: int) -> None:
        """I'm not sure how to do this since it is possible that we roll an unending sequence of explosions."""
        return

    @staticmethod
    @mark.parametrize("trials, n", [(500_000, n) for n in range(11)])
    def test_white_dice_damage_monte_carlo(trials: int, n: int) -> None:
        seed = set_seed()
        damage = 0
        for _ in range(trials):
            damage += damage_rolling(n, WHITE_DIE)
        # Table 5.4, p. 110
        assert (
            abs(damage / trials - TestOathsworn.Expected_White_Dice_Damage[n]) < 0.01
        ), bad_seed_message(seed, trials)
        return

    # endregion

if __name__ == "__main__":
    ...
