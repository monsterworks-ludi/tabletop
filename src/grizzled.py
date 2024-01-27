import sympy as sp
import itertools as it

assault, gas, shelling, snow, rain, night = sp.symbols("a, g, s, w, r, n")

Card = tuple[frozenset[sp.Symbol], int]
""" The threats are the first entry and the copy number is the second entry. """

def copy_card(threats: set[sp.Symbol], *, count: int = 1) -> set[Card]:
    """

    :param threats: the threats on the card
    :param count: the number of cards to be generated
    :return: a set consisting of count copies of a card with threats
    """
    return {(frozenset(threats), i) for i in range(count)}

DECK: tuple[Card, ...] = tuple(
    card
    for card in it.chain(
        copy_card({assault, gas, shelling, snow, rain, night}),
        copy_card({assault, gas, shelling}),
        copy_card({assault, gas}),
        copy_card({assault, shelling}),
        copy_card({assault, snow}, count=4),
        copy_card({assault, night}, count=3),
        copy_card({assault, rain}, count=3),
        copy_card({gas, shelling}),
        copy_card({gas, snow}, count=3),
        copy_card({gas, rain}, count=4),
        copy_card({gas, night}, count=3),
        copy_card({shelling, night}, count=4),
        copy_card({shelling, rain}, count=3),
        copy_card({shelling, snow}, count=3),
        copy_card({snow, rain, night}),
        copy_card({snow, rain}),
        copy_card({snow, night}),
        copy_card({rain, night}),
    )
)


def contains_all_threats(card: Card, threats: set[sp.Symbol]) -> bool:
    """

    :param card: the card to be checked
    :param threats: which threats to check for
    :return: True if the card contains all of the threats
    """
    for threat in threats:
        if threat not in card[0]:
            return False
    return True

def contains_no_threats(card: Card, threats: set[sp.Symbol]) -> bool:
    """

    :param card: the card to be checked
    :param threats: the threats to check for
    :return: False if the card contains any of those threats
    """
    for threat in threats:
        if threat in card[0]:
            return False
    return True

def count_threats(threats: set[sp.Symbol], cards: tuple[Card, ...]=DECK) -> int:
    """

    :param threats: the threats to check for
    :param cards: the cards to check for threats
    :return: the number of cards containing all threats
    """
    return len(tuple(filter(lambda card: contains_all_threats(card, threats), cards)))


def count_nonthreats(threats: set[sp.Symbol], cards: tuple[Card, ...] = DECK) -> int:
    """

    :param threats: the threats to cehck for
    :param cards: the cards to check for threats
    :return: the number of cards which do not have any of the threats
    """
    return len(tuple(filter(lambda card: contains_no_threats(card, threats), cards)))


if __name__ == "__main__":
    ...
