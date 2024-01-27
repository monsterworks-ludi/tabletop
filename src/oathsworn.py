from itertools import permutations
from math import factorial

# from pprint import pprint

# card: damage, explosions, number
deck = {
    (0, 0, 1),
    (0, 0, 2),
    (0, 0, 3),
    (0, 0, 4),
    (0, 0, 5),
    (0, 0, 6),
    (1, 0, 1),
    (1, 0, 2),
    (1, 0, 3),
    (1, 0, 4),
    (1, 0, 5),
    (1, 0, 6),
    (2, 0, 1),
    (2, 0, 2),
    (2, 0, 3),
    (2, 1, 1),
    (2, 1, 2),
    (2, 1, 3),
}


def card_to_key(card):
    if card[0] == 0:
        return "0"
    elif card[0] == 1:
        return "1"
    else:  # card[0] == 2
        if card[1] == 0:
            return "2"
        else:  # card[1] == 1
            return "e"


def hand_to_key(hand):
    key = hand["0"] * "0" + hand["1"] * "1" + hand["2"] * "2" + hand["e"] * "e"
    return key


# debugging information for hand_size = 3
# damage_by_hand = {
#     "000": 0,
#     "001": 0,
#     "002": 0,
#     "00e": 0,
#     "011": 0,
#     "012": 0,
#     "01e": 0,
#     "022": 0,
#     "02e": 0,
#     "0ee": 0,
#     "111": 0,
#     "112": 0,
#     "11e": 0,
#     "122": 0,
#     "12e": 0,
#     "1ee": 0,
#     "222": 0,
#     "22e": 0,
#     "2ee": 0,
#     "eee": 0,
# }
#
# count_by_hand = damage_by_hand.copy()


def calculate_card_damage(hand_size):
    shuffles = 0
    total_damage = 0
    for shuffle in permutations(deck, hand_size + 3):
        shuffle = list(shuffle)
        shuffles += 1
        draws = hand_size
        blanks = 0
        hand_damage = 0
        card_number = 1
        while draws > 0:
            card = shuffle.pop()
            draws = draws - 1
            if card_number <= hand_size:
                card_number += 1
                if card[0] == 0:
                    blanks += 1
                    if blanks >= 2:
                        break  # stop drawing cards, we have missed
            hand_damage += card[0]
            draws += card[1]
        if not blanks >= 2:
            total_damage += hand_damage

    return total_damage / shuffles


sides = {(0, 0, 1), (0, 0, 2), (1, 0, 1), (1, 0, 2), (2, 0, 1), (2, 1, 1)}


def quadnomial(blanks, ones, twos, explodes):
    return factorial(blanks + ones + twos + explodes) / (
        factorial(blanks) * factorial(ones) * factorial(twos) * factorial(explodes)
    )


def calculate_dice_damage(hand_size):
    total_damage = 0
    for blanks in range(2):
        for ones in range(hand_size - blanks + 1):
            for twos in range(hand_size - blanks - ones + 1):
                explodes = hand_size - blanks - ones - twos
                hand_damage = ones * 1 + twos * 2 + explodes * (2 + 6 / 5)
                # print(f"{blanks=}, {ones=}, {twos=}, {explodes=}, {hand_damage=}")
                total_damage += (
                    quadnomial(blanks, ones, twos, explodes)
                    * (2 / 6) ** blanks
                    * (2 / 6) ** ones
                    * (1 / 6) ** twos
                    * (1 / 6) ** explodes
                    * hand_damage
                )

    return total_damage


# for n in range(0, 7):
#     dice_damage = calculate_dice_damage(n)
#     card_damage = calculate_card_damage(n)
#     print(f"{n=}, {dice_damage=}, {card_damage=}")


def size(hand):
    accumulator = 0
    for card in range(len(hand)):
        accumulator += hand[card]
    return accumulator


def damage_function(low, hand):
    return low * hand[1] + (low + 1) * (hand[2] + hand[3])


def white_damage(hand):
    return 1 * hand[1] + 2 * (hand[2] + hand[3])


def yellow_damage(hand):
    return 2 * hand[1] + 3 * (hand[2] + hand[3])


def red_damage(hand):
    return 3 * hand[1] + 4 * (hand[2] + hand[3])


def black_damage(hand):
    return 4 * hand[1] + 5 * (hand[2] + hand[3])


# hand_size tracks the *initial* hand size
def card_damage(deck, hand_size, hand, probability, low, construction=None):
    if size(hand) == hand_size + hand[3]:
        probability = float(probability)
        damage = float(damage_function(low, hand) * probability)
        # print(f"{hand=}, {probability=:.2}, {damage=:.2}, {construction=}")
        return damage

    damage = 0
    for card in range(4):
        if deck[card] > 0:
            prob = deck[card] / size(deck)
            deck[card] -= 1
            hand[card] += 1
            if construction is not None:
                construction.append(card)
            if size(hand) > hand_size or hand[0] < 2:
                damage += card_damage(
                    deck, hand_size, hand, probability * prob, low, construction
                )
            else:
                ...
                # print(f"{hand=}, {probability=:.2}, damage=MISS, {construction=}")
            if construction is not None:
                construction.pop()
            hand[card] -= 1
            deck[card] += 1

    return damage


# print(card_damage([6, 6, 3, 3], 2, [0, 0, 0, 0], 1, []))

for n in range(2, 11):
    # dice = calculate_dice_damage(n)
    white = card_damage([6, 6, 3, 3], n, [0, 0, 0, 0], 1, 1)
    yellow = card_damage([6, 6, 3, 3], n, [0, 0, 0, 0], 1, 2)
    red = card_damage([6, 6, 3, 3], n, [0, 0, 0, 0], 1, 3)
    black = card_damage([6, 6, 3, 3], n, [0, 0, 0, 0], 1, 4)
    print(
        f"{n=}, {white=:.3} ({(yellow-white)/n=:.3}), {yellow=:.3} ({(red-yellow)/n=:.3}) {red=:.3} ({(black-red)/n=:.3}) {black=:.3}"
    )
    # print(f"{n=}, card damage = {card_damage([6, 6, 3, 3], n, [0, 0, 0, 0], 1)}")
    # print(f"{n=}, dice damage = {calculate_dice_damage(n)}")
