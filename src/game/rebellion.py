import random as rnd
from collections import defaultdict

import sympy as sp
from icecream import ic  # type: ignore

import mwmath.markov as mkv
from util.unique import unique

ic.disable()

# region Exciting Space Battle

# region Constants

Damage = tuple[int, int, int]

EXCITING_BATTLE_STATES: dict[int, set[Damage]] = {
    1: {(0, 0, 0)},
    2: {(0, 1, 0)},
    3: {(0, 2, 0)},
    4: {(0, 0, 1)},
    5: {(0, 1, 1)},
    6: {(0, 2, 1)},
    7: {(1, 0, 0)},
    8: {(1, 1, 0)},
    9: {(1, 0, 1)},
    10: {(1, 1, 1)},
    11: {  # Y-wing & corvette destroyed, destroyer not destroyed
        (1, 2, 0),
        (1, 2, 1),
        (1, 2, 2),
        (1, 2, 3),
    },
    12: {  # destroyer damaged at least twice, any rebel ship alive
        (0, 0, 2),  # both alive
        (0, 1, 2),  # both alive, corvette damaged
        (0, 2, 2),  # y_wing alive
        (1, 0, 2),  # corvette alive
        (1, 1, 2),  # corvette damaged
        (0, 0, 3),  # both alive
        (0, 1, 3),  # both alive, corvette damaged
        (0, 2, 3),  # y_wing alive
        (1, 0, 3),  # corvette alive
        (1, 1, 3),  # corvette damaged
    },
    13: {  # destroyer destroyed, any rebel ship alive
        (0, 0, 4),  # both alive
        (0, 1, 4),  # both alive, corvette damaged
        (0, 2, 4),  # y_wing alive
        (1, 0, 4),  # corvette alive
        (1, 1, 4),  # corvette damaged
    },
    14: {(1, 2, 4)},  # all destroyed
}
assert sum((len(value) for value in EXCITING_BATTLE_STATES.values())) == 2 * 3 * 5

StateDistribution = dict[int, sp.Rational]


def state_for_damage(damage: Damage) -> int:
    for key, value in EXCITING_BATTLE_STATES.items():
        if damage in value:
            return key
    assert False, f"could not find state for {damage=}"


ZERO = sp.Rational(0, 1)
ONE_SIXTH = sp.Rational(1, 6)
ONE_QUARTER = sp.Rational(1, 4)
ONE_THIRD = sp.Rational(1, 3)
ONE_HALF = sp.Rational(1, 2)
FIVE_SIXTH = sp.Rational(5, 6)
ONE = sp.Rational(1, 1)

DamageDistribution = dict[tuple[int, int, int], sp.Rational]

Y_WING_DAMAGE = 0
CORVETTE_DAMAGE = 1
DESTROYER_DAMAGE = 2

Hits = tuple[int, int, int, int]

BLACK_HIT = 0
RED_HIT = 1
CRITICAL_HIT = 2
MISS = 3

HitDistribution = dict[Hits, sp.Rational]

Y_WING_HIT_DISTRIBUTION: HitDistribution = {
    # Y-wing rolls red
    (0, 0, 0, 1): ONE_HALF,  # M
    (0, 1, 0, 0): ONE_THIRD,  # R
    (0, 0, 1, 0): ONE_SIXTH,  # C
}
assert mkv.is_distribution(Y_WING_HIT_DISTRIBUTION)
for KEY in Y_WING_HIT_DISTRIBUTION:
    assert sum(KEY) == 1

CORVETTE_HIT_DISTRIBUTION: HitDistribution = {
    # corvette rolls black, red
    (0, 0, 0, 2): ONE_HALF * ONE_HALF,  # MM
    (1, 0, 0, 1): ONE_THIRD * ONE_HALF,  # BM
    (0, 0, 1, 1): ONE_SIXTH * ONE_HALF + ONE_HALF * ONE_SIXTH,  # CM + MR
    (0, 1, 0, 1): ONE_HALF * ONE_THIRD,  # MR
    (1, 1, 0, 0): ONE_THIRD * ONE_THIRD,  # BR
    (0, 1, 1, 0): ONE_SIXTH * ONE_THIRD,  # CR
    (1, 0, 1, 0): ONE_THIRD * ONE_SIXTH,  # BC
    (0, 0, 2, 0): ONE_SIXTH * ONE_SIXTH,  # CC
}
assert mkv.is_distribution(CORVETTE_HIT_DISTRIBUTION)
for KEY in CORVETTE_HIT_DISTRIBUTION:
    assert sum(KEY) == 2

EMPIRE_HIT_DISTRIBUTION: HitDistribution = {
    # destroyer rolls black, red, red
    # black, red, critical
    (0, 0, 0, 3): ONE_HALF * ONE_HALF * ONE_HALF,  # MMM
    (0, 0, 1, 2): ONE_SIXTH * ONE_HALF * ONE_HALF
    + ONE_HALF * ONE_SIXTH * ONE_HALF
    + ONE_HALF * ONE_HALF * ONE_SIXTH,  # CMM, MCM, MMC
    (0, 0, 2, 1): ONE_SIXTH * ONE_SIXTH * ONE_HALF
    + ONE_SIXTH * ONE_HALF * ONE_SIXTH
    + ONE_HALF * ONE_SIXTH * ONE_SIXTH,  # CCM, CMC, MCC
    (0, 0, 3, 0): ONE_SIXTH * ONE_SIXTH * ONE_SIXTH,  # CCC
    (0, 1, 0, 2): ONE_HALF * ONE_THIRD * ONE_HALF
    + ONE_HALF * ONE_HALF * ONE_THIRD,  # MRM, MMR
    (0, 1, 1, 1): ONE_SIXTH * ONE_THIRD * ONE_HALF
    + ONE_SIXTH * ONE_HALF * ONE_THIRD
    + ONE_HALF * ONE_SIXTH * ONE_THIRD
    + ONE_HALF * ONE_THIRD * ONE_SIXTH,  # CRM, CMR, MCR, MRC
    (0, 1, 2, 0): ONE_SIXTH * ONE_SIXTH * ONE_THIRD
    + ONE_SIXTH * ONE_THIRD * ONE_SIXTH,  # CCR CRC
    (0, 2, 0, 1): ONE_HALF * ONE_THIRD * ONE_THIRD,  # MRR
    (0, 2, 1, 0): ONE_SIXTH * ONE_THIRD * ONE_THIRD,  # CRR
    (1, 0, 0, 2): ONE_THIRD * ONE_HALF * ONE_HALF,  # BMM
    (1, 0, 1, 1): ONE_THIRD * ONE_SIXTH * ONE_HALF
    + ONE_THIRD * ONE_HALF * ONE_SIXTH,  # BCM, BMC
    (1, 0, 2, 0): ONE_THIRD * ONE_SIXTH * ONE_SIXTH,  # BCC
    (1, 1, 0, 1): ONE_THIRD * ONE_THIRD * ONE_HALF
    + ONE_THIRD * ONE_HALF * ONE_THIRD,  # BRM, BMR
    (1, 1, 1, 0): ONE_THIRD * ONE_SIXTH * ONE_THIRD
    + ONE_THIRD * ONE_THIRD * ONE_SIXTH,  # BCR, BRC
    (1, 2, 0, 0): ONE_THIRD * ONE_THIRD * ONE_THIRD,  # BRR
}
assert mkv.is_distribution(EMPIRE_HIT_DISTRIBUTION)
for KEY in EMPIRE_HIT_DISTRIBUTION:
    assert sum(KEY) == 3

def sum_hits(lhs: Hits, rhs: Hits) -> Hits:
    return lhs[0] + rhs[0], lhs[1] + rhs[1], lhs[2] + rhs[2], lhs[3] + rhs[3]

# endregion

def apply_hits_to_y_wing(y_wing_damage: int, hits: Hits) -> int:
    applied_hits = min(1 - y_wing_damage, hits[BLACK_HIT] + hits[CRITICAL_HIT])
    y_wing_damage_new = y_wing_damage + applied_hits
    assert y_wing_damage_new <= 1
    return y_wing_damage_new

def apply_hits_to_tie_fighter(tie_fighter_damage: int, hits: Hits) -> int:
    applied_hits = min(1 - tie_fighter_damage, hits[BLACK_HIT] + hits[CRITICAL_HIT])
    tie_fighter_damage_new = tie_fighter_damage + applied_hits
    assert tie_fighter_damage_new <= 1
    return tie_fighter_damage_new

def apply_hits_to_destroyer(destroyer_damage: int, hits: Hits) -> int:
    applied_hits = min(4 - destroyer_damage, hits[RED_HIT] + hits[CRITICAL_HIT])
    destroyer_damage_new = destroyer_damage + applied_hits
    assert destroyer_damage_new <= 4
    return destroyer_damage_new

def apply_hits_to_rebels(
    y_wing_damage: int, corvette_damage: int, hits: Hits
) -> tuple[int, int]:
    mutable_hits = list(hits)

    # pile the black hits on the y-wing
    applied_damage = min(1 - y_wing_damage, mutable_hits[BLACK_HIT])
    y_wing_damage += applied_damage
    mutable_hits[BLACK_HIT] -= applied_damage

    # pile the red hits on the corvette
    applied_damage = min(2 - corvette_damage, mutable_hits[RED_HIT])
    corvette_damage += applied_damage
    mutable_hits[RED_HIT] -= applied_damage

    # decide where to place the critical hits
    if corvette_damage + mutable_hits[CRITICAL_HIT] >= 2:
        # we can destroy the corvette
        applied_damage = min(2 - corvette_damage, mutable_hits[CRITICAL_HIT])
        corvette_damage += applied_damage
        mutable_hits[CRITICAL_HIT] -= applied_damage
    if y_wing_damage + mutable_hits[CRITICAL_HIT] >= 1:
        # we can destroy the y_wing
        applied_damage = min(1 - y_wing_damage, mutable_hits[CRITICAL_HIT])
        y_wing_damage += applied_damage
        mutable_hits[CRITICAL_HIT] -= applied_damage
    if mutable_hits[CRITICAL_HIT] > 0:
        # we damage the corvette
        applied_damage = min(2 - corvette_damage, mutable_hits[CRITICAL_HIT])
        corvette_damage += applied_damage
        mutable_hits[CRITICAL_HIT] -= applied_damage

    # sanity checks
    if mutable_hits[BLACK_HIT] > 0:
        # we have left over black damage, so y_wing should be destroyed
        assert y_wing_damage == 1

    if mutable_hits[RED_HIT] > 0:
        # we have left over red damage, so corvette should be destroyed
        assert corvette_damage == 2

    if mutable_hits[CRITICAL_HIT] > 0:
        # we have left over critical damage, so both rebels should be destroyed
        assert y_wing_damage == 1
        assert corvette_damage == 2

    assert y_wing_damage <= 1
    assert corvette_damage <= 2
    return y_wing_damage, corvette_damage


def merge_rebel_hit_distributions(
    y_wing_distribution: HitDistribution, corvette_distribution: HitDistribution
) -> HitDistribution:
    """

    :param y_wing_distribution:
    :param corvette_distribution:
    :return:
    """
    assert mkv.is_distribution(y_wing_distribution)
    assert mkv.is_distribution(corvette_distribution)
    merged_distribution: HitDistribution = defaultdict(mkv.zero)
    for y_hits, y_prob in y_wing_distribution.items():
        for cor_hits, cor_prob in corvette_distribution.items():
            total_hits = sum_hits(y_hits, cor_hits)
            total_prob = y_prob * cor_prob
            merged_distribution[total_hits] += total_prob
    ic(merged_distribution)
    assert mkv.is_distribution(merged_distribution)
    return merged_distribution


def merge_damage_distributions(
    rebel_damage_distribution: dict[tuple[int, int], sp.Rational],
    empire_damage_distribution: dict[int, sp.Rational],
) -> StateDistribution:
    """

    :param rebel_damage_distribution:
    :param empire_damage_distribution:
    :return:
    """
    ic(rebel_damage_distribution)
    ic(empire_damage_distribution)
    merged_damage_distribution: dict[tuple[int, int, int], sp.Rational] = defaultdict(mkv.zero)
    for rebel_dam, rebel_prob in rebel_damage_distribution.items():
        for emp_dam, emp_prob in empire_damage_distribution.items():
            merged_damage_distribution[(rebel_dam[0], rebel_dam[1], emp_dam)] += (
                rebel_prob * emp_prob
            )
    assert mkv.is_distribution(merged_damage_distribution)
    ic(merged_damage_distribution)

    state_distribution: StateDistribution = defaultdict(mkv.zero)
    for damage, prob in merged_damage_distribution.items():
        state_distribution[state_for_damage(damage)] += prob

    assert mkv.is_distribution(state_distribution)
    return state_distribution


def exciting_transition_distribution(state: int) -> StateDistribution:
    if state > 10:
        return {state: ONE}

    damage = unique(EXCITING_BATTLE_STATES[state])
    y_wing_damage = damage[Y_WING_DAMAGE]
    corvette_damage = damage[CORVETTE_DAMAGE]
    destroyer_damage = damage[DESTROYER_DAMAGE]

    if y_wing_damage < 1:
        y_wing_hit_distribution = Y_WING_HIT_DISTRIBUTION
    else:
        y_wing_hit_distribution = {(0, 0, 0, 1): ONE}
    mkv.is_distribution(y_wing_hit_distribution)

    if corvette_damage < 2:
        corvette_hit_distribution = CORVETTE_HIT_DISTRIBUTION
    else:
        corvette_hit_distribution = {(0, 0, 0, 2): ONE}
    mkv.is_distribution(corvette_hit_distribution)

    rebel_hit_distribution = merge_rebel_hit_distributions(
        y_wing_hit_distribution, corvette_hit_distribution
    )
    ic(rebel_hit_distribution)

    empire_hit_distribution = EMPIRE_HIT_DISTRIBUTION
    ic(empire_hit_distribution)

    rebel_damage_distribution: dict[tuple[int, int], sp.Rational] = defaultdict(mkv.zero)
    for hits, prob in empire_hit_distribution.items():
        y_wing_damage_new, corv_damage_new = apply_hits_to_rebels(
            y_wing_damage, corvette_damage, hits
        )
        rebel_damage_distribution[(y_wing_damage_new, corv_damage_new)] += prob
    assert mkv.is_distribution(rebel_damage_distribution)

    empire_damage_distribution: dict[int, sp.Rational] = defaultdict(mkv.zero)
    for hits, prob in rebel_hit_distribution.items():
        destroyer_damage_new = apply_hits_to_destroyer(destroyer_damage, hits)
        empire_damage_distribution[destroyer_damage_new] += prob
    assert mkv.is_distribution(empire_damage_distribution)

    state_distribution = merge_damage_distributions(
        rebel_damage_distribution, empire_damage_distribution
    )
    assert mkv.is_distribution(state_distribution)

    return state_distribution


# endregion

# region Probabalistic Battle


def black_die_result(dice_count: int = 1) -> Hits:
    hit_list: list[int] = [0, 0, 0, 0]
    for _ in range(dice_count):
        roll = rnd.randint(1, 6)
        if roll in {1, 2, 3}:
            hit_list[MISS] += 1
        elif roll in {4, 5}:
            hit_list[BLACK_HIT] += 1
        else:
            assert roll == 6
            hit_list[CRITICAL_HIT] += 1
    hits = (hit_list[0], hit_list[1], hit_list[2], hit_list[3])
    return hits


def red_die_result(dice_count: int = 1) -> Hits:
    hit_list: list[int] = [0, 0, 0, 0]
    for _ in range(dice_count):
        roll = rnd.randint(1, 6)
        if roll in {1, 2, 3}:
            hit_list[MISS] += 1
        elif roll in {4, 5}:
            hit_list[RED_HIT] += 1
        else:
            assert roll == 6
            hit_list[CRITICAL_HIT] += 1
    hits = (hit_list[0], hit_list[1], hit_list[2], hit_list[3])
    return hits


def roll_tie_fighter_attack() -> Hits:
    return black_die_result()

def roll_y_wing_attack() -> Hits:
    return red_die_result()

def roll_corvette_attack() -> Hits:
    return sum_hits(black_die_result(), red_die_result())

def roll_destroyer_attack() -> Hits:
    return sum_hits(black_die_result(), red_die_result(2))


def combat_step(damage: Damage) -> Damage:
    y_wing_damage = damage[Y_WING_DAMAGE]
    corvette_damage = damage[CORVETTE_DAMAGE]
    destroyer_damage = damage[DESTROYER_DAMAGE]

    if y_wing_damage < 1:
        y_wing_hits = roll_y_wing_attack()
    else:
        y_wing_hits = (0, 0, 0, 1)

    if corvette_damage < 2:
        corvette_hits = roll_corvette_attack()
    else:
        corvette_hits = (0, 0, 0, 2)

    total_rebel_hits = sum_hits(y_wing_hits, corvette_hits)
    total_empire_hits = roll_destroyer_attack()

    destroyer_damage_new = apply_hits_to_destroyer(destroyer_damage, total_rebel_hits)

    y_wing_damage_new, corvette_damage_new = apply_hits_to_rebels(
        y_wing_damage, corvette_damage, total_empire_hits
    )

    return y_wing_damage_new, corvette_damage_new, destroyer_damage_new


def combat_transition(state: int) -> int:
    if state > 10:
        return state
    damage = unique(EXCITING_BATTLE_STATES[state])
    damage_new = combat_step(damage)
    state_new = state_for_damage(damage_new)
    return state_new


def run_combat(state: int) -> tuple[int, int]:
    rounds = 0
    while state <= 10:
        state = combat_transition(state)
        rounds += 1
    return state, rounds


# endregion

if __name__ == "__main__":
    ...
