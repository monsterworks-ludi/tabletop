import itertools as it
from collections import defaultdict

import sympy as sp

from mwmath.combinations import perm

Card = tuple[int, int]
""" A card is a tuple with two entries
  the first entry is the card type (zero-based),
  and the second entry is the copy of the card (zero-based).

For example, (4, 1) would indicate the second copy (1) of the fifth card (4)
"""

Deck = set[Card]
""" A Deck consists of a set of cards.
"""

DeckSpecification = dict[int, int]
""" A DecSpec is a dictionary
  the keys are the number of copies,
  and the values are the number of cards with that many copies.
  
  
  For a sprinter deck of flamme rouge, this would be {3: 5}.
  For a deck of brass, this would be {1: 2, 2: 12, 3: 7, 4: 1, 5: 1, 8: 1}.
"""

HashableDeckSpecification = tuple[int, ...]
"""
To make a deck specification hashable, we create a tuple with 0 in missing values
"""

def hashable(deck_spec: DeckSpecification) -> HashableDeckSpecification:
    """

    :param deck_spec: a Deck Specification as a dictionary
    :return: a Deck Specification as a tuple
    """
    max_key = max(deck_spec.keys())
    hash_deck_spec = (deck_spec[k] if k in deck_spec else 0 for k in range(max_key))
    return tuple(hash_deck_spec)

def build_decklist(deck: DeckSpecification) -> Deck:
    """

    :parameter deck: a deck specification
    :return: a set of cards in a deck specified by the deck specification
    """

    card_number = 0
    decklist = set()
    for copies, cards in deck.items():
        for card in range(cards):
            for copy in range(copies):
                new_card = (card_number, copy)
                decklist.add(new_card)
            card_number += 1
    return decklist


def collapse_hand(
    hand: Deck
) -> DeckSpecification:
    """

    :param hand: a tuple consisting of the cards in the hand
    :return: a dictionary indicating how many of each card type are in the hand
    """
    result: defaultdict[int, int] = defaultdict(lambda: 0)
    for card, copy in hand:
        result[card] += 1
    return result

def count_hands_permutation(deck: DeckSpecification, hand_size: int) -> int:
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
    last_report = 0.0
    permutation: tuple[tuple[int, int], ...]
    count: int
    for count, permutation in enumerate(it.permutations(deck_list, hand_size)):
        percentage = count / perm_count
        if percentage > last_report + 1e-8:
            last_report = percentage
        specification = hashable(collapse_hand(set(permutation)))
        hands.add(specification)
    return len(hands)


def count_hands_generating(deck: dict[int, int], hand_size: int) -> int:
    """
    This method uses generating functions to count the number of possible
    hands.

    :param deck: a deck specification
    :param hand_size: the number of cards in a hand
    :return: the number of possible hands
    """
    x = sp.symbols("x")
    product = sp.Poly.from_list([1], gens=x)
    for copies, cards in deck.items():
        for _ in range(cards):
            coeff = [1 for _ in range(copies + 1)]
            poly = sp.Poly.from_list(coeff, gens=x)
            product = product * poly

    return product.as_expr().coeff(x**hand_size)


if __name__ == "__main__":
    ...
