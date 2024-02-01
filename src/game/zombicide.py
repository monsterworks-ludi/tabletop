import random as rnd
from typing import Optional


def hit_on_a(target: int, *, critical: Optional[int] = None) -> int:
    """

    :param target: rolls at least target will hit
    :param critical: rolls at least critical will gain a bonus roll
    :return: the number of hits obtained from the roll
    """
    hits = 0
    roll = rnd.randrange(1, 7)
    if roll >= target:
        hits += 1
    if critical and roll >= critical:
        hits += hit_on_a(target, critical=critical)
    return hits
