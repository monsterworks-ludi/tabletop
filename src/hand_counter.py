import sympy as sp
from scipy.special import perm  # type: ignore
from collections import defaultdict
from itertools import permutations
from time import time

from icecream import ic  # type: ignore
ic.disable()

# the deck specification is a dictionary
#   the keys are the number of copies
#   the values are the number of cards with that many copies
#   for a sprinter deck of flamme rouge, this would be {3: 5}
#   for a deck of brass, this would be {1: 2, 2: 12, 3: 7, 4: 1, 5: 1, 8: 1}

# a card is a tuple with two entries
#   the first entry is the card type (zero-based)
#   the second entry is the copy of the card (zero-based)
#   for example, (4, 1) would indicate the second copy (1) of the fifth card (4)

def build_decklist(deck: dict[int, int]) -> list[tuple[int, int]]:
    """

    :parameter deck: a deck specification
    :return: a list of cards in a deck specified by the deck specification
    """

    card_number = 0
    decklist = []
    for copies, cards in deck.items():
        for card in range(cards):
            for copy in range(copies):
                new_card = (card_number, copy)
                decklist.append(new_card)
            card_number += 1
    return decklist

def collapse_hand(hand: tuple[tuple[int, int], ...], total_cards: int) -> tuple[int, ...]:
    """

    :param hand: a tuple consisting of the cards in the hand
    :param total_cards: the total number of card types
    :return: a tuple indicating how many of each card type are in the hand
    """
    card_dict: defaultdict[int, int] = defaultdict(lambda: 0)
    for card, copy in hand:
        card_dict[card] += 1
    card_list = []
    for i in range(total_cards):
        card_list.append(card_dict[i])
    collapsed_hand: tuple[int, ...] = tuple(card_list)
    return collapsed_hand

def count_hands_permutation(deck: dict[int, int], hand_size: int) -> int:
    """
    This method uses a brute force method to count the number of possible
    hands. It does this by running through all permutations and then coalescing
    equivalent hands.

    :param deck: a deck specification
    :param hand_size: the number of cards in a hand
    :return: the number of possible hands
    """
    hands = set()
    deck_list = build_decklist(deck)
    deck_size = len(deck_list)
    perm_count = perm(deck_size, hand_size)
    last_report = 0
    ic(time())
    # this line keeps mypy happy, otherwise it will not correctly type permutation
    permutation: tuple[tuple[int, int], ...]
    for count, permutation in enumerate(permutations(deck_list, hand_size)):
        percentage = count/perm_count
        if percentage > last_report + 10**-8:
            ic(f"Completed {percentage:0.8f}, {time()}")
            last_report = percentage
        hand_tuple = collapse_hand(permutation, deck_size)
        hands.add(hand_tuple)
    return len(hands)

def count_hands_generating(deck: dict[int, int], hand_size: int) -> int:
    """
    This method uses generating functions to count the number of possible
    hands.

    :param deck: a deck specification
    :param hand_size: the number of cards in a hand
    :return: the number of possible hands
    """
    x = sp.symbols('x')
    product = sp.Poly.from_list([1], gens=x)
    for copies, cards in deck.items():
        for _ in range(cards):
            coeff = [1 for _ in range(copies + 1)]
            poly = sp.Poly.from_list(coeff, gens=x)
            product = product*poly

    return product.as_expr().coeff(x**hand_size)

if __name__ == '__main__':
    ...
