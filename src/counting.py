import sympy as sp
import itertools as it

a, g, s = sp.symbols("a, g, s")

GRIZZLED_CARDS = tuple(
    card
    for card in it.chain(
        (((a, g, s), i) for i in range(2)),
        (((a, g), i) for i in range(1)),
        (((a, s), i) for i in range(1)),
        (((g, s), i) for i in range(1)),
        (((a,), i) for i in range(10)),
        (((g,), i) for i in range(10)),
        (((s,), i) for i in range(10)),
    )
)


def contains_threats(card, threats):
    for threat in threats:
        if threat not in card[0]:
            return False
    return True


def count_threats(threats):
    return len(tuple(filter(lambda card: contains_threats(card, threats), GRIZZLED_CARDS)))


if __name__ == "__main__":
    ...
