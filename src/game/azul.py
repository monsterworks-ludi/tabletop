import sympy as sp

from icecream import ic  # type: ignore

ic.disable()

# player_0_tiles -> player outcomes
RESULTS = {("b", "r"): (+3, -3), ("b", "t"): (-2, +2), ("r", "t"): (+4, -4)}


def dfs(
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


if __name__ == "__main__":

    ic(dfs("", 0, ["b", "r", "t"]))
