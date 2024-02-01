import random as rnd
from collections import defaultdict

import sympy as sp
from icecream import ic  # type: ignore

import mwmath.markov as mkv

ic.disable()

# region Exciting Space Battle

# todo: set up consistent ordering of y_wing, corvette, destroyer
# todo: doc strings
# states start at 1 to match book and give corvette, destroyer, y_wing damage
# it might have made more sense to do this as y_wing, corvette, destroyer
CORVETTE_DAMAGE = 0
DESTROYER_DAMAGE = 1
Y_WING_DAMAGE = 2

BATTLE_STATES = {
    1: {(0, 0, 0)},
    2: {(1, 0, 0)},
    3: {(2, 0, 0)},
    4: {(0, 1, 0)},
    5: {(1, 1, 0)},
    6: {(2, 1, 0)},
    7: {(0, 0, 1)},
    8: {(1, 0, 1)},
    11: {  # corvette & Y-wing destroyed, destroyer not destroyed
        (2, 0, 1),
        (2, 1, 1),
        (2, 2, 1),
        (2, 3, 1),
    },
    9: {(0, 1, 1)},
    10: {(1, 1, 1)},
    12: {  # destroyer damaged twice, any rebel ship alive
        (0, 2, 0),
        (1, 2, 0),
        (2, 2, 0),
        (0, 2, 1),
        (1, 2, 1),
        (0, 2, 0),
        (1, 2, 0),
        (2, 2, 0),
        (0, 2, 1),
        (1, 2, 1),
        (0, 3, 0),
        (1, 3, 0),
        (2, 3, 0),
        (0, 3, 1),
        (1, 3, 1),
        (0, 3, 0),
        (1, 3, 0),
        (2, 3, 0),
        (0, 3, 1),
        (1, 3, 1),
    },
    13: {  # destroyer destroyed, any rebel ship alive
        (0, 4, 0),
        (1, 4, 0),
        (2, 4, 0),
        (0, 4, 1),
        (1, 4, 1),
        (0, 4, 0),
        (1, 4, 0),
        (2, 4, 0),
        (0, 4, 1),
        (1, 4, 1),
    },
    14: {(2, 4, 1)},
}


def state_for_damage(damage):
    for key, value in BATTLE_STATES.items():
        if damage in value:
            return key
    assert False, f"could not find state for {damage=}"


ONE_SIXTH = sp.Rational(1, 6)
ONE_THIRD = sp.Rational(1, 3)
ONE_HALF = sp.Rational(1, 2)
FIVE_SIXTH = sp.Rational(5, 6)
ONE = sp.Rational(1, 1)

BLACK_HIT = 0
RED_HIT = 1
CRITICAL_HIT = 2
MISS = 3

# Y-wing rolls red (1/2)
# Perhaps we should use the BRCM encoding here
# (0, 0, 0, 0): ONE_HALF
# (1, 0, 0, 0): ONE_HALF
Y_WING_HIT_DISTRIBUTION = {
    0: ONE_HALF,  # M
    1: ONE_HALF,  # H
}
assert mkv.is_distribution(Y_WING_HIT_DISTRIBUTION)

# corvette rolls black (1/6) and red (1/2)
# Perhaps we should use the BRCM encoding here
CORVETTE_HIT_DISTRIBUTION = {
    0: FIVE_SIXTH * ONE_HALF,  # MM
    1: ONE_SIXTH * ONE_HALF + FIVE_SIXTH * ONE_HALF,  # HM, MH
    2: ONE_SIXTH * ONE_HALF,  # HH
}
assert mkv.is_distribution(CORVETTE_HIT_DISTRIBUTION)

# destroyer rolls black, red, red
# Perhaps we should use the BRCM encoding here
EMPIRE_HIT_DISTRIBUTION = {
    # black, red, critical
    (0, 0, 0): ONE_HALF * ONE_HALF * ONE_HALF,  # MMM
    (0, 0, 1): ONE_SIXTH * ONE_HALF * ONE_HALF
    + ONE_HALF * ONE_SIXTH * ONE_HALF
    + ONE_HALF * ONE_HALF * ONE_SIXTH,  # CMM, MCM, MMC
    (0, 0, 2): ONE_SIXTH * ONE_SIXTH * ONE_HALF
    + ONE_SIXTH * ONE_HALF * ONE_SIXTH
    + ONE_HALF * ONE_SIXTH * ONE_SIXTH,  # CCM, CMC, MCC
    (0, 0, 3): ONE_SIXTH * ONE_SIXTH * ONE_SIXTH,  # CCC
    (0, 1, 0): ONE_HALF * ONE_THIRD * ONE_HALF
    + ONE_HALF * ONE_HALF * ONE_THIRD,  # MRM, MMR
    (0, 1, 1): ONE_SIXTH * ONE_THIRD * ONE_HALF
    + ONE_SIXTH * ONE_HALF * ONE_THIRD
    + ONE_HALF * ONE_SIXTH * ONE_THIRD
    + ONE_HALF * ONE_THIRD * ONE_SIXTH,  # CRM, CMR, MCR, MRC
    (0, 1, 2): ONE_SIXTH * ONE_SIXTH * ONE_THIRD
    + ONE_SIXTH * ONE_THIRD * ONE_SIXTH,  # CCR CRC
    (0, 2, 0): ONE_HALF * ONE_THIRD * ONE_THIRD,  # MRR
    (0, 2, 1): ONE_SIXTH * ONE_THIRD * ONE_THIRD,  # CRR
    (1, 0, 0): ONE_THIRD * ONE_HALF * ONE_HALF,  # BMM
    (1, 0, 1): ONE_THIRD * ONE_SIXTH * ONE_HALF
    + ONE_THIRD * ONE_HALF * ONE_SIXTH,  # BCM, BMC
    (1, 0, 2): ONE_THIRD * ONE_SIXTH * ONE_SIXTH,  # BCC
    (1, 1, 0): ONE_THIRD * ONE_THIRD * ONE_HALF
    + ONE_THIRD * ONE_HALF * ONE_THIRD,  # BRM, BMR
    (1, 1, 1): ONE_THIRD * ONE_SIXTH * ONE_THIRD
    + ONE_THIRD * ONE_THIRD * ONE_SIXTH,  # BCR, BRC
    (1, 2, 0): ONE_THIRD * ONE_THIRD * ONE_THIRD,  # BRR
}
assert mkv.is_distribution(EMPIRE_HIT_DISTRIBUTION)


# todo: hits should really be a hit vector BRCM
def apply_hits_to_destroyer(destroyer_damage, hits):
    destroyer_damage = min(destroyer_damage + hits, 4)
    return destroyer_damage


CORVETTE_HITS = 0
Y_WING_HITS = 1


def apply_hits_to_rebels(corvette_damage, y_wing_damage, hits):
    hits = list(hits)
    # pile the black hits on the y-wing
    applied_damage = min(1 - y_wing_damage, hits[BLACK_HIT])
    y_wing_damage += applied_damage
    hits[BLACK_HIT] -= applied_damage

    # pile the red hits on the corvette
    applied_damage = min(2 - corvette_damage, hits[RED_HIT])
    corvette_damage += applied_damage
    hits[RED_HIT] -= applied_damage

    # decide where to place the critical hits
    if corvette_damage + hits[CRITICAL_HIT] >= 2:
        # we can destroy the corvette
        applied_damage = min(2 - corvette_damage, hits[CRITICAL_HIT])
        corvette_damage += applied_damage
        hits[CRITICAL_HIT] -= applied_damage
    if y_wing_damage + hits[CRITICAL_HIT] >= 1:
        # we can destroy the y_wing
        applied_damage = min(1 - y_wing_damage, hits[CRITICAL_HIT])
        y_wing_damage += applied_damage
        hits[CRITICAL_HIT] -= applied_damage
    if hits[CRITICAL_HIT] > 0:
        # we damage the corvette
        applied_damage = min(2 - corvette_damage, hits[CRITICAL_HIT])
        corvette_damage += applied_damage
        hits[CRITICAL_HIT] -= applied_damage

    # sanity checks
    if hits[BLACK_HIT] > 0:
        # we have left over black damage, so y_wing should be destroyed
        assert y_wing_damage == 1

    if hits[RED_HIT] > 0:
        # we have left over red damage so corvette should be destroyed
        assert corvette_damage == 2

    if hits[CRITICAL_HIT] > 0:
        # we have left over critical damage, so both rebels should be destroyed
        assert y_wing_damage == 1
        assert corvette_damage == 2

    return corvette_damage, y_wing_damage


def merge_rebel_hits_distributions(corvette_distribution, y_wing_distribution):
    merged_distribution = defaultdict(int)
    for cor_hits, cor_prob in corvette_distribution.items():
        for y_hits, y_prob in y_wing_distribution.items():
            merged_distribution[cor_hits + y_hits] += cor_prob * y_prob
    assert mkv.is_distribution(merged_distribution)
    return merged_distribution


def merge_damage_distributions(rebel_damage_distribution, empire_damage_distribution):
    ic(rebel_damage_distribution)
    ic(empire_damage_distribution)
    merged_damage_distribution = defaultdict(int)
    for rebel_dam, rebel_prob in rebel_damage_distribution.items():
        for emp_dam, emp_prob in empire_damage_distribution.items():
            # book tracks them as "corvette, destroyer, y_wing"
            # it might make more sense as "y_wing, corvette, destroyer"
            merged_damage_distribution[(rebel_dam[0], emp_dam, rebel_dam[1])] += (
                rebel_prob * emp_prob
            )
    assert mkv.is_distribution(merged_damage_distribution)
    ic(merged_damage_distribution)

    state_distribution = defaultdict(int)
    for damage, prob in merged_damage_distribution.items():
        state_distribution[state_for_damage(damage)] += prob

    assert mkv.is_distribution(state_distribution)
    return state_distribution


def exciting_transition_distribution(state):
    if state > 10:
        return {state: 1}

    assert len(BATTLE_STATES[state]) == 1
    damage = next(iter(BATTLE_STATES[state]))
    corvette_damage = damage[CORVETTE_DAMAGE]
    destroyer_damage = damage[DESTROYER_DAMAGE]
    y_wing_damage = damage[Y_WING_DAMAGE]

    if corvette_damage < 2:
        corvette_hit_distribution = CORVETTE_HIT_DISTRIBUTION
    else:
        corvette_hit_distribution = {0: ONE}
    if y_wing_damage < 1:
        y_wing_hit_distribution = Y_WING_HIT_DISTRIBUTION
    else:
        y_wing_hit_distribution = {0: ONE}
    ic(corvette_hit_distribution)
    ic(y_wing_hit_distribution)
    rebel_hit_distribution = merge_rebel_hits_distributions(
        corvette_hit_distribution, y_wing_hit_distribution
    )
    ic(rebel_hit_distribution)

    rebel_damage_distribution = defaultdict(int)
    empire_hit_distribution = EMPIRE_HIT_DISTRIBUTION
    ic(empire_hit_distribution)
    for hits, prob in empire_hit_distribution.items():
        new_corv_damage, new_y_wing_damage = apply_hits_to_rebels(
            corvette_damage, y_wing_damage, hits
        )
        rebel_damage_distribution[(new_corv_damage, new_y_wing_damage)] += prob
    assert mkv.is_distribution(rebel_damage_distribution)

    empire_damage_distribution = defaultdict(int)
    for hits, prob in rebel_hit_distribution.items():
        new_damage = apply_hits_to_destroyer(destroyer_damage, hits)
        empire_damage_distribution[new_damage] += prob
    assert mkv.is_distribution(empire_damage_distribution)

    state_distribution = merge_damage_distributions(
        rebel_damage_distribution, empire_damage_distribution
    )

    assert mkv.is_distribution(state_distribution)
    return state_distribution


# endregion

# region Probabalistic Battle


def black_die_result():
    roll = rnd.randint(1, 6)
    if roll == 1 or roll == 2 or roll == 3:
        return MISS
    elif roll == 4 or roll == 5:
        return BLACK_HIT
    else:
        assert roll == 6
        return CRITICAL_HIT


def red_die_result():
    roll = rnd.randint(1, 6)
    if roll == 1 or roll == 2 or roll == 3:
        return MISS
    elif roll == 4 or roll == 5:
        return RED_HIT
    else:
        assert roll == 6
        return CRITICAL_HIT


def roll_y_wing_attack():
    result = [0, 0, 0, 0]
    result[red_die_result()] += 1
    return result


def roll_corvette_attack():
    result = [0, 0, 0, 0]
    result[black_die_result()] += 1
    result[red_die_result()] += 1
    return result


def roll_destroyer_attack():
    result = [0, 0, 0, 0]
    result[black_die_result()] += 1
    result[red_die_result()] += 1
    result[red_die_result()] += 1

    return result


def combat_step(damages):
    corvette_damage = damages[CORVETTE_DAMAGE]
    destroyer_damage = damages[DESTROYER_DAMAGE]
    y_wing_damage = damages[Y_WING_DAMAGE]

    if y_wing_damage < 1:
        y_wing_hits = roll_y_wing_attack()
    else:
        y_wing_hits = [0, 0, 0, 0]

    if corvette_damage < 2:
        corvette_hits = roll_corvette_attack()
    else:
        corvette_hits = [0, 0, 0, 0]

    total_rebel_damage = (
        y_wing_hits[RED_HIT]
        + y_wing_hits[CRITICAL_HIT]
        + corvette_hits[RED_HIT]
        + corvette_hits[CRITICAL_HIT]
    )
    destroyer_damage_new = apply_hits_to_destroyer(destroyer_damage, total_rebel_damage)

    total_empire_damage = roll_destroyer_attack()
    corvette_damage_new, y_wing_damage_new = apply_hits_to_rebels(
        corvette_damage, y_wing_damage, total_empire_damage
    )

    return corvette_damage_new, destroyer_damage_new, y_wing_damage_new


def combat_transition(state):
    if state > 10:
        return state
    assert len(BATTLE_STATES[state]) == 1
    damage = next(iter(BATTLE_STATES[state]))
    damage_new = combat_step(damage)
    state_new = state_for_damage(damage_new)
    return state_new

def run_combat(state):
    rounds = 0
    while state <= 10:
        state = combat_transition(state)
        rounds += 1
    return state, rounds

# endregion

if __name__ == "__main__":
    ...
