import sympy as sp

from icecream import ic  # type: ignore

ic.disable()

# player_0_tiles -> player outcomes
RESULTS = {("b", "r"): (+3, -3), ("b", "t"): (-2, +2), ("r", "t"): (+4, -4)}

# player_1_tiles -> probability of choice
PROBS = {("b", "r"): (sp.Rational(9, 10), sp.Rational(1, 10)),
         ("b", "t"): (sp.Rational(2, 10), sp.Rational(8, 10)),
         ("r", "t"): (sp.Rational(2, 10), sp.Rational(8, 10))}


def fixed_dfs(
    prefix: str,
    player: int,
    moves: list[str],
    player_moves: tuple[str, ...] = tuple(),
) -> tuple[tuple, tuple]:
    """

    :param prefix: a prefix for the ic statements so the tree structure is clearer
    :param player: the player to make the next move
    :param moves: the moves available to the player
    :param player_moves: the history of moves made in previous turns
    :return: the outcome and moves from an optimal play
    """

    prefix += "."

    if len(moves) == 0:
        for key, outcome in RESULTS.items():
            if set(player_moves[::2]) == set(key):
                output = f"{prefix}{player_moves} pays out {outcome}"
                ic(output)
                return outcome, player_moves

    best: tuple[tuple[int, int], tuple[str, ...]] = (-sp.oo, -sp.oo), tuple("*")
    best_move: str = "*"
    for move in moves:
        output = f"{prefix}Player {player} plays '{move}' from {player_moves}."
        ic(output)
        new_moves = moves.copy()
        new_moves.remove(move)
        new_player_moves = player_moves + (move,)
        result: tuple[tuple[int, int], tuple[str, ...]] = dfs(
            prefix, (player + 1) % 2, new_moves, new_player_moves
        )
        if result[0][player] > best[0][player]:
            output = f"{prefix}Selecting '{move}' ({result[0]}) over '{best_move}' ({best[0]})"
            best = result
            best_move = move
        else:
            output = f"{prefix}Retaining '{best_move}' ({best[0]}) over '{move}' ({result[0]})"
        ic(output)
    return best

def prob_dfs(
    prefix: str,
    player: int,
    moves: list[str],
    player_moves: tuple[str, ...] = tuple(),
) -> tuple[tuple, tuple]:
    """

    :param prefix: a prefix for the ic statements so the tree structure is clearer
    :param player: the player to make the next move
    :param moves: the moves available to the player
    :param player_moves: the history of moves made in previous turns
    :return: the outcome and moves from an optimal play
    """

    prefix += "."

    if len(moves) == 0:
        for key, outcome in RESULTS.items():
            if set(player_moves[::2]) == set(key):
                output = f"{prefix}{outcome} from {player_moves}."
                ic(output)
                return outcome, player_moves

    expected_payoff = [sp.Integer(0), sp.Integer(0)]
    for move in moves:
        prob = sp.Integer(1)
        for key, outcome in PROBS.items():
            if set(moves) == set(key):
                if key[0] == move:
                    prob = outcome[0]
                else:
                    assert key[1] == move
                    prob = outcome[1]
        output = f"{prefix}Player {player} plays '{move}' from {player_moves} with probability {prob}."
        ic(output)
        new_moves = moves.copy()
        new_moves.remove(move)
        new_player_moves = player_moves + (move,)
        result: tuple[tuple[int, int], tuple[str, ...]] = dfs(
            prefix, (player + 1) % 2, new_moves, new_player_moves
        )
        expected_payoff[0] += prob*result[0][0]
        expected_payoff[1] += prob*result[0][1]
    output = f"{prefix}Random moves lead to payoff of {tuple(expected_payoff)}."
    ic(output)
    return tuple(expected_payoff), player_moves + ("*",)

def rational_dfs(prefix, player, moves, player_moves=tuple()):
    return fixed_dfs(prefix, player, moves, player_moves)

def natural_dfs(prefix, player, moves, player_moves=tuple()):
    if player == 0:
        return fixed_dfs(prefix, player, moves, player_moves)
    else:
        return prob_dfs(prefix, player, moves, player_moves)

def use_rational():
    global dfs
    dfs = rational_dfs
    return dfs

def use_natural():
    global dfs
    dfs = natural_dfs
    return dfs

if __name__ == "__main__":

    dfs = rational_dfs
    ic(dfs("", 0, ["b", "r", "t"]))

    ic("")
    ic(50*"~")
    ic("")

    ic.enable()

    dfs = natural_dfs
    ic(dfs("", 0, ["b", "r", "t"]))

    ic.disable()
