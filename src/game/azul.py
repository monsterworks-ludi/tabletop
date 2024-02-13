import sympy as sp
import copy
import itertools

from icecream import ic  # type: ignore

from util.debug import checkup, icp

ic.disable()

# region SIMPLE TREES

# player_0_tiles -> player outcomes
RESULTS = {("b", "r"): (+3, -3), ("b", "t"): (-2, +2), ("r", "t"): (+4, -4)}

# player_1_tiles -> probability of choice
PROBS = {
    ("b", "r"): (sp.Rational(9, 10), sp.Rational(1, 10)),
    ("b", "t"): (sp.Rational(2, 10), sp.Rational(8, 10)),
    ("r", "t"): (sp.Rational(2, 10), sp.Rational(8, 10)),
}


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
                icp(f"{prefix}{player_moves} pays out {outcome}")
                return outcome, player_moves

    best: tuple[tuple[int, int], tuple[str, ...]] = (-sp.oo, -sp.oo), tuple("*")
    best_move: str = "*"
    for move in moves:
        icp(f"{prefix}Player {player} plays '{move}' from {player_moves}.")
        new_moves = moves.copy()
        new_moves.remove(move)
        new_player_moves = player_moves + (move,)
        result: tuple[tuple[int, int], tuple[str, ...]] = dfs(
            prefix, (player + 1) % 2, new_moves, new_player_moves
        )
        if result[0][player] > best[0][player]:
            icp(
                f"{prefix}Selecting '{move}' ({result[0]}) over '{best_move}' ({best[0]})"
            )
            best = result
            best_move = move
        else:
            icp(
                f"{prefix}Retaining '{best_move}' ({best[0]}) over '{move}' ({result[0]})"
            )
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
                icp(f"{prefix}{outcome} from {player_moves}.")
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
        icp(
            f"{prefix}Player {player} plays '{move}' from {player_moves} with probability {prob}."
        )
        new_moves = moves.copy()
        new_moves.remove(move)
        new_player_moves = player_moves + (move,)
        result: tuple[tuple[int, int], tuple[str, ...]] = dfs(
            prefix, (player + 1) % 2, new_moves, new_player_moves
        )
        expected_payoff[0] += prob * result[0][0]
        expected_payoff[1] += prob * result[0][1]
    icp(f"{prefix}Random moves lead to payoff of {tuple(expected_payoff)}.")
    return tuple(expected_payoff), player_moves + ("*",)


def rational_dfs(prefix, player, moves, player_moves=tuple()):
    return fixed_dfs(prefix, player, moves, player_moves)


def natural_dfs(prefix, player, moves, player_moves=tuple()):
    if player == 0:
        return fixed_dfs(prefix, player, moves, player_moves)
    else:
        return prob_dfs(prefix, player, moves, player_moves)


dfs = rational_dfs


def use_rational():
    global dfs
    dfs = rational_dfs
    return dfs


def use_natural():
    global dfs
    dfs = natural_dfs
    return dfs


# endregion


class AzulBoard:

    BROKEN_TILES_POINTS = [0, -1, -2, -4, -6, -8, -11, -14]

    @staticmethod
    def column(*, color, row):
        return (color + row) % 5

    @staticmethod
    def color(*, row, column):
        return (column - row) % 5

    def __init__(self, player, board=None, rows=None, score=0, broken_tiles=0):
        self.player = player
        if board is None:
            self.board = sp.zeros(5, 5)
        else:
            self.board = board
        if rows is None:
            # row number -> color, count
            self.rows = [[-1, 0], [-1, 0], [-1, 0], [-1, 0], [-1, 0]]
        else:
            self.rows = rows
        self.score = score
        self.broken_tiles = broken_tiles

    def check(self):
        assert self.board.shape == (5, 5)
        assert len(self.rows) == 5
        for row, (color, count) in enumerate(self.rows):
            assert count <= row + 1
            if color == TileFactories.EMPTY:
                assert count == 0
            else:
                assert count > 0
                column = AzulBoard.column(color=color, row=row)
                assert self.board[row, column] == 0

    @checkup
    def board_string(self):
        string = "["
        for row in range(5):
            for col in range(5):
                if self.board[row, col] == 1:
                    color_index = AzulBoard.color(row=row, column=col)
                    color_string = TileFactories.color_string(color_index)
                    string += color_string
                else:
                    string += "_"
            string += " | "
        string += "]"
        return string

    @checkup
    def row_string(self, index):
        color_index, count = self.rows[index]
        return count * TileFactories.color_string(color_index)

    @checkup
    def row_strings(self):
        strings = [self.row_string(index) for index in range(5)]
        return "[" + " | ".join(strings) + "]"

    @checkup
    def legal_placement(self, *, color, row):
        if self.board[row, self.column(color=color, row=row)] == 1:
            # cannot place in row if already played
            return False
        if not self.rows[row][0] in {0, color}:
            # cannot place in row of a different color
            return False
        if not self.rows[row][1] == row + 1:
            # cannot place in a full row
            return False
        return True

    @checkup
    def place_in_row(self, *, color, count, row):
        if not self.legal_placement(color=color, row=row):
            self.broken_tiles += count
        else:
            row_color, row_count = self.rows[row]
            assert row_color == 0 or row_color == color
            empty_spaces = (row + 1) - row_count
            unbroken_tiles = count - max(count, empty_spaces)
            broken_tiles = count - unbroken_tiles
            self.rows[row][1] += unbroken_tiles
            self.broken_tiles += broken_tiles

    @checkup
    def score_tile(self, row, col):
        old_score = self.score
        hor_score = False
        ver_score = False
        for delta in range(1, row + 1):
            if self.board[row - delta, col] == 1:
                hor_score = True
                self.score += 1
            else:
                break
        for delta in range(1, 5 - row):
            if self.board[row + delta, col] == 1:
                hor_score = True
                self.score += 1
            else:
                break
        for delta in range(1, col + 1):
            if self.board[row, col - delta] == 1:
                ver_score = True
                self.score += 1
            else:
                break
        for delta in range(1, 5 - col):
            if self.board[row, col + delta] == 1:
                ver_score = True
                self.score += 1
            else:
                break
        if ver_score:
            self.score += 1
        if hor_score:
            self.score += 1
        if not (ver_score or hor_score):
            self.score += 1
        icp(f"({row}, {col}) scores {self.score - old_score}.")

    @checkup
    def score_round(self):
        old_score = self.score
        for row, tiles in enumerate(self.rows):
            color, count = tiles
            if count == row + 1:
                # row is filled, place the tile
                col = AzulBoard.column(row=row, color=color)
                assert self.board[row, col] == 0
                self.board[row, col] = 1
                self.rows[row] = [TileFactories.EMPTY, 0]
                self.score_tile(row, col)

        if self.broken_tiles <= 7:
            self.score += AzulBoard.BROKEN_TILES_POINTS[self.broken_tiles]
        else:
            self.score += AzulBoard.BROKEN_TILES_POINTS[7] + 3 * (self.broken_tiles - 7)
        self.broken_tiles = 0

        self.score = max(self.score, 0)
        icp(
            f"EoR: Player {self.player} scores {self.score - old_score} for total of {self.score}"
        )

    @checkup
    def score_game(self):
        old_score = self.score
        for row in range(5):
            if all(self.board[row, col] == 1 for col in range(5)):
                self.score += 2
        for col in range(5):
            if all(self.board[row, col] == 1 for row in range(5)):
                self.score += 7
        for diag in range(5):
            if all(self.board[row, (row + diag) % 5] == 1 for row in range(5)):
                self.score += 10
        icp(
            f"EoG: Player {self.player} scores {self.score - old_score} for total of {self.score}"
        )


class TileFactories:

    EMPTY = -1

    BLUE = 0
    YELLOW = 1
    RED = 2
    BLACK = 3
    CYAN = 4

    FIRST_PLAYER = 5

    CENTER_PILE = 5

    @staticmethod
    def color_string(index):
        return ["*", "b", "y", "r", "k", "c", "1"][index + 1]

    # factory = [2, 1, 1, 0, 1, 0] = 2 blue, 1 yellow, 1 red, 0 black, 1 cyan
    # center = [1, 3, 2, 1, 3, 1] = 1 blue, 3 yellow, 2 red, 1 black, 3 cyan, 1 firstplayer

    def __init__(self, factories):
        self.factories = factories

    def check(self):
        assert len(self.factories) == TileFactories.CENTER_PILE + 1
        assert all(
            len(self.factories[index]) == 6
            for index in range(TileFactories.CENTER_PILE + 1)
        )

    @checkup
    def factory_string(self, factory_index):
        factory = self.factories[factory_index]
        string = ""
        for index in range(6):
            string += factory[index] * TileFactories.color_string(index)
        return string

    @checkup
    def factory_strings(self):
        strings = [self.factory_string(index) for index in range(6)]
        return "{" + " | ".join(strings) + "}"

    @checkup
    def take(self, *, factory, taken_color):
        if factory < TileFactories.CENTER_PILE:
            for color in range(5):
                if color != taken_color:
                    self.factories[TileFactories.CENTER_PILE][color] += self.factories[
                        factory
                    ][color]
            self.factories[factory] = [0, 0, 0, 0, 0, 0]
            return False
        else:
            self.factories[TileFactories.CENTER_PILE][taken_color] = 0
            if (
                self.factories[TileFactories.CENTER_PILE][TileFactories.FIRST_PLAYER]
                == 1
            ):
                self.factories[TileFactories.CENTER_PILE][
                    TileFactories.FIRST_PLAYER
                ] = 0
                return True

    @checkup
    def empty(self):
        empty = all(
            self.factories[factory][color] == 0
            for factory in range(TileFactories.CENTER_PILE + 1)
            for color in range(6)
        )
        return empty


def play_game(prefix, player, factories, player_boards, past_moves):

    icp(
        f"{prefix}Player 0: {player_boards[0].row_strings()} ({player_boards[0].broken_tiles} broken)"
    )
    icp(
        f"{prefix}Player 1: {player_boards[1].row_strings()} ({player_boards[1].broken_tiles} broken)"
    )
    icp(f"{prefix}Factory: {factories.factory_strings()}")

    if factories.empty():
        for player_board in player_boards:
            player_board.score_round()
            player_board.score_game()

        result = (
            player_boards[0].score,
            player_boards[1].score,
        ), player_boards

        ic.enable()
        ic(past_moves, result[0])
        ic.disable()

        return result

    optimal = (-1, -1), (None, None)
    for color, factory, row in itertools.product(range(5), range(6), range(5)):
        new_factories = copy.deepcopy(factories)
        new_player_boards = copy.deepcopy(player_boards)
        new_past_moves = copy.deepcopy(past_moves)
        count = new_factories.factories[factory][color]
        if count > 0:
            icp(
                f"{prefix}{TileFactories.color_string(color)} ({count}):{factory} -> {row}"
            )
            new_player_boards[player].place_in_row(color=color, count=count, row=row)
            if new_factories.take(taken_color=color, factory=factory):
                # we took the first player token
                icp(f"{prefix}First Player Tile Taken.")
                new_player_boards[player].broken_tiles += 1
            new_past_moves.append(
                f"{TileFactories.color_string(color)} {factory} -> {player}.{row}"
            )
            result = play_game(
                prefix + ".",
                (player + 1) % 2,
                new_factories,
                new_player_boards,
                new_past_moves,
            )

            new_player_0_score = result[0][0]
            new_player_1_score = result[0][1]
            old_player_0_score = optimal[0][0]
            old_player_1_score = optimal[0][1]

            if (
                player == 0
                and new_player_0_score - new_player_1_score
                > old_player_1_score - old_player_1_score
                or player == 1
                and new_player_1_score - new_player_0_score
                > old_player_1_score - old_player_0_score
            ):
                ic.enable()
                icp(f"{prefix}Player {player} prefers {result[0]} over {optimal[0]}.")
                optimal = result
                ic.disable()

    return optimal


if __name__ == "__main__":

    PLAYER_ONE_BOARD = AzulBoard(
        0,
        sp.Matrix(
            [
                [1, 0, 1, 1, 1],
                [1, 0, 1, 1, 1],
                [1, 1, 0, 1, 1],
                [1, 0, 1, 0, 0],
                [1, 0, 0, 1, 0],
            ]
        ),
        [
            [TileFactories.EMPTY, 0],
            [TileFactories.EMPTY, 0],
            [TileFactories.BLUE, 2],
            [TileFactories.EMPTY, 0],
            [TileFactories.EMPTY, 0],
        ],
        49,
        1,
    )
    PLAYER_ONE_BOARD.check()
    ic(PLAYER_ONE_BOARD.board_string())
    for i in range(5):
        ic(i, PLAYER_ONE_BOARD.row_string(i))

    PLAYER_TWO_BOARD = AzulBoard(
        1,
        sp.Matrix(
            [
                [0, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
                [0, 1, 1, 0, 1],
                [1, 0, 0, 1, 1],
                [0, 0, 1, 0, 0],
            ]
        ),
        [
            [TileFactories.BLUE, 1],
            [TileFactories.CYAN, 1],
            [TileFactories.EMPTY, 0],
            [TileFactories.EMPTY, 0],
            [TileFactories.YELLOW, 2],
        ],
        23,
        0,
    )
    PLAYER_TWO_BOARD.check()

    ic(PLAYER_TWO_BOARD.board_string())
    for i in range(5):
        ic(i, PLAYER_TWO_BOARD.row_string(i))

    FACTORIES = TileFactories(
        [
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [1, 0, 0, 3, 0, 0],
            [1, 0, 0, 0, 2, 0],
        ]
    )
    FACTORIES.check()

    res = play_game("", 0, FACTORIES, (PLAYER_ONE_BOARD, PLAYER_TWO_BOARD), [])

    ic.enable()

    ic(res[0])
    ic(res[1])
    ic(res[1][0].board_string())
    ic(res[1][1].board_string())

    ic.disable()

    # dfs = rational_dfs
    # ic(dfs("", 0, ["b", "r", "t"]))
    #
    # ic("")
    # ic(50 * "~")
    # ic("")
    #
    # dfs = natural_dfs
    # ic(dfs("", 0, ["b", "r", "t"]))


# todo: should really do a more extensive example here
