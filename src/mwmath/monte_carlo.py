import sys
import random as rnd

def set_seed() -> int:
    seed = rnd.randrange(sys.maxsize)
    rnd.seed(seed)
    return seed

