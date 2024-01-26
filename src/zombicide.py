import random

def hit_on_a(target, *, critical=None):
    hits = 0
    roll = random.randrange(1, 7)
    if roll >= target:
        hits += 1
    if critical and roll >= critical:
        hits += hit_on_a(target, critical=critical)
    return hits


