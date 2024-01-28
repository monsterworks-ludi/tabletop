import random
import itertools as it
from typing import NamedTuple


class Card(NamedTuple):
    damage: int
    exploding: bool = False
    copy: int = 0


def copy_card(damage: int, exploding: bool = False, *, count: int = 1) -> set[Card]:
    """

    :param damage: the damage done by the card
    :param exploding: whether the card grants a bonus card draw
    :param count: the number of cards to be generated
    :return: a set consisting of count copies of a card with threats
    """
    return {Card(damage, exploding, i) for i in range(count)}


Deck = list[Card]


def shuffled(deck: Deck) -> Deck:
    """

    :param deck: the deck to be shuffled
    :return: a shuffled deck with the same cards as deck
    """
    deck = deck.copy()
    random.shuffle(deck)
    return deck


WHITE_DECK: Deck = [
    card
    for card in it.chain(
        copy_card(0, count=6),
        copy_card(1, count=6),
        copy_card(2, count=3),
        copy_card(2, True, count=3),
    )
]

YELLOW_DECK: Deck = [
    card
    for card in it.chain(
        copy_card(0, count=6),
        copy_card(2, count=6),
        copy_card(3, count=3),
        copy_card(4, True, count=3),
    )
]

RED_DECK: Deck = [
    card
    for card in it.chain(
        copy_card(0, count=6),
        copy_card(3, count=6),
        copy_card(4, count=3),
        copy_card(4, True, count=3),
    )
]

BLACK_DECK: Deck = [
    card
    for card in it.chain(
        copy_card(0, count=6),
        copy_card(4, count=6),
        copy_card(5, count=3),
        copy_card(5, True, count=3),
    )
]


def hit_drawing(number_of_cards: int, deck: Deck) -> bool:
    """

    :param number_of_cards: the number of cards drawn
    :param deck: the deck from which to draw
    :return: whether the hand scores a hit
    """
    blanks = 0
    for _ in range(number_of_cards):
        card = deck.pop()
        if card.damage == 0:
            blanks += 1
            if not blanks <= 1:
                break  # stop drawing cards, attack has missed
    return blanks <= 1


def damage_drawing(number_in_initial_draw: int, deck: Deck) -> int:
    """

    :param number_in_initial_draw: number of cards initially drawn
    :param deck: the deck from which the cards are to be drawn
    :return: the damage done by drawing the cards
    """
    blanks = 0
    damage = 0
    cards_drawn = 0
    draws_remaining = number_in_initial_draw
    while draws_remaining > 0:
        card = deck.pop()
        draws_remaining -= 1
        cards_drawn += 1
        if cards_drawn <= number_in_initial_draw and card.damage == 0:
            blanks += 1
            if not blanks <= 1:
                break  # stop drawing cards, attack has missed
        damage += card.damage
        if card.exploding:
            draws_remaining += 1
    return damage if blanks <= 1 else 0


class Face(NamedTuple):
    damage: int
    exploding: bool = False
    copy: int = 0


def copy_face(damage: int, exploding: bool = False, *, count: int = 1) -> set[Face]:
    """

    :param damage: the damage done by the card
    :param exploding: whether the card grants a bonus card draw
    :param count: the number of cards to be generated
    :return: a set consisting of count copies of a card with threats
    """
    return {Face(damage, exploding, i) for i in range(count)}


Die = tuple[Face, ...]


WHITE_DIE: Die = tuple(
    face
    for face in it.chain(
        copy_face(0, count=2),
        copy_face(1, count=2),
        copy_face(2),
        copy_face(2, exploding=True),
    )
)

YELLOW_DIE: Die = tuple(
    face
    for face in it.chain(
        copy_face(0, count=2),
        copy_face(2, count=2),
        copy_face(3),
        copy_face(3, exploding=True),
    )
)

RED_DIE: Die = tuple(
    face
    for face in it.chain(
        copy_face(0, count=2),
        copy_face(3, count=2),
        copy_face(4),
        copy_face(4, exploding=True),
    )
)

BLACK_DIE: Die = tuple(
    face
    for face in it.chain(
        copy_face(0, count=2),
        copy_face(4, count=2),
        copy_face(5),
        copy_face(5, exploding=True),
    )
)

# maybe we should specify the die as well
def hit_rolling(number_of_rolls: int, die: Die) -> bool:
    """

    :param number_of_rolls: the number of dice rolled
    :return: whether the hand scores a hit
    """
    blanks = 0
    for _ in range(number_of_rolls):
        face = random.choice(die)
        if face.damage == 0:
            blanks += 1
            if not blanks <= 1:
                break  # stop drawing cards, attack has missed
    return blanks <= 1

def damage_rolling(number_in_initial_roll: int, die: Die) -> int:
    """

    :param number_in_initial_roll: number of dice initially roll
    :param die: the dice which is rolled
    :return: the damage done by rolling the dice
    """
    blanks = 0
    damage = 0
    explosions = 0
    dice_rolled = 0
    rolls_remaining = number_in_initial_roll
    while rolls_remaining > 0:
        face: Face = random.choice(die)
        dice_rolled += 1
        rolls_remaining -= 1
        if dice_rolled <= number_in_initial_roll and face.damage == 0:
            blanks += 1
            if not blanks <= 1:
                break
        damage += face.damage
        if face.exploding:
            rolls_remaining += 1
            explosions += 1
            if explosions > 100_000:
                raise RuntimeError("YIKES! More than 100000 explosions!")
    return damage if blanks <= 1 else 0


if __name__ == "__main__":
    ...
