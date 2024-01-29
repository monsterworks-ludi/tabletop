import sympy as sp
import time


def size(hand: list[int]) -> int:
    accumulator = 0
    for card_type in range(len(hand)):
        accumulator += hand[card_type]
    return accumulator


def white_damage(hand: list[int]) -> sp.Integer:
    return sp.Integer(1) * hand[1] + sp.Integer(2) * (hand[2] + hand[3])


# deck is a list of how many of each card remains
# hand_size is the original number of cards drawn
# hand is a list of how many of each card has been drawn
# probability is the probability that this hand was drawn
# construction tracks the order the cards appear


def card_damage(
    deck: list[int], hand_size: int, hand: list[int], probability: sp.Rational
) -> sp.Rational:
    if size(hand) == hand_size + hand[3]:
        damage = white_damage(hand) * probability
        return damage

    damage = sp.Integer(0)
    for card_type in range(4):
        if deck[card_type] > 0:
            prob = sp.Rational(deck[card_type], size(deck))
            deck[card_type] -= 1
            hand[card_type] += 1
            if (
                size(hand) > hand_size or hand[0] < 2
            ):  # bonus card or we haven't missed yet
                damage += card_damage(deck, hand_size, hand, probability * prob)
            hand[card_type] -= 1
            deck[card_type] += 1
    return damage


for n in range(11):
    ms1 = time.time() * 1000.0
    card = card_damage([6, 6, 3, 3], n, [0, 0, 0, 0], sp.Integer(1))
    ms2 = time.time() * 1000.0
    bigcard = card_damage([30, 30, 15, 15], n, [0, 0, 0, 0], sp.Integer(1))
    ms3 = time.time() * 1000.0
    print(
        f"{n=}\n\t{card=} approx {card.evalf(3)} @ {round(ms2-ms1,0)}ms"
        f"\n\t{bigcard=} approx {bigcard.evalf(3)} @ {round(ms3-ms2, 0)}ms"
    )
