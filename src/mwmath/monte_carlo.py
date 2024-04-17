import sys
import random as rnd

def set_seed() -> int:
    seed = rnd.randrange(sys.maxsize)
    rnd.seed(seed)
    return seed


def bad_seed_message(seed, trials):
    return f"Failed Monte Carlo Experiment with {seed=} and {trials=}"
