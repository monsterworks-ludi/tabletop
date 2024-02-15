import sympy as sp
import copy
import itertools
from typing import Callable

from icecream import ic  # type: ignore

from util.debug import checkup

ic.disable()

# todo: docstrings and type information


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
        self.board = board if board else sp.zeros(5, 5)
        self.rows = rows if rows else [[-1, 0], [-1, 0], [-1, 0], [-1, 0], [-1, 0]]
        self.score = score
        self.broken_tiles = broken_tiles

    def check(self):
        assert self.board.shape == (5, 5)
        assert len(self.rows) == 5
        for row, (color, count) in enumerate(self.rows):
            assert count <= row + 1
            if color == AzulTiles.EMPTY:
                assert count == 0
            else:
                assert count > 0
                column = AzulBoard.column(color=color, row=row)
                assert self.board[row, column] == 0

    @checkup
    def board_string(self, row):
        string = "["
        for col in range(5):
            if self.board[row, col] == 1:
                color_index = AzulBoard.color(row=row, column=col)
                color_string = AzulTiles.color_string(color_index)
                string += color_string
            else:
                string += "_"
        string += "]"
        return string

    @checkup
    def row_string(self, index):
        color_index, count = self.rows[index]
        tiles = count * AzulTiles.color_string(color_index)
        string = (5 - len(tiles)) * " " + tiles
        return string

    @checkup
    def __repr__(self):
        string = (
            f"Player {self.player}, Score {self.score}, Broken {self.broken_tiles}\n"
        )
        for row in range(5):
            string += self.row_string(row) + " " + self.board_string(row) + "\n"
        return string

    @checkup
    def legal_placement(self, *, color, row):
        if self.board[row, self.column(color=color, row=row)] == 1:
            # cannot place in row if already played
            return False
        if not self.rows[row][0] in {AzulTiles.EMPTY, color}:
            # cannot place in row of a different color
            return False
        if not self.rows[row][1] < row + 1:
            # cannot place in a full row
            return False
        return True

    @checkup
    def place_in_row(self, *, color, count, row):
        if not self.legal_placement(color=color, row=row):
            self.broken_tiles += count
        else:
            self.check()
            row_color, row_count = self.rows[row]
            assert row_color == AzulTiles.EMPTY or row_color == color
            empty_spaces = (row + 1) - row_count
            unbroken_tiles = min(count, empty_spaces)
            broken_tiles = count - unbroken_tiles
            self.rows[row][0] = color
            self.rows[row][1] += unbroken_tiles
            self.broken_tiles += broken_tiles
            self.check()

    @checkup
    def score_tile(self, row, col):
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

    @checkup
    def score_round(self):
        for row, tiles in enumerate(self.rows):
            color, count = tiles
            if count == row + 1:
                # row is filled, place the tile
                col = AzulBoard.column(row=row, color=color)
                assert self.board[row, col] == 0
                self.board[row, col] = 1
                self.rows[row] = [AzulTiles.EMPTY, 0]
                self.score_tile(row, col)

        if self.broken_tiles <= 7:
            self.score += AzulBoard.BROKEN_TILES_POINTS[self.broken_tiles]
        else:
            self.score += AzulBoard.BROKEN_TILES_POINTS[7] + 3 * (self.broken_tiles - 7)
        self.broken_tiles = 0

        self.score = max(self.score, 0)

    @checkup
    def score_game(self):
        for row in range(5):
            if all(self.board[row, col] == 1 for col in range(5)):
                self.score += 2
        for col in range(5):
            if all(self.board[row, col] == 1 for row in range(5)):
                self.score += 7
        for diag in range(5):
            if all(self.board[row, (row + diag) % 5] == 1 for row in range(5)):
                self.score += 10


class AzulTiles:

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

    # factory = [2, 1, 1, 0, 1, 0] = 2 blue, 1 yellow, 1 red, 0 black, 1 cyan, 0 firstplayer

    def __init__(self, factories):
        self.factories = factories

    def check(self):
        assert len(self.factories) == AzulTiles.CENTER_PILE + 1
        assert all(
            len(self.factories[index]) == 6
            for index in range(AzulTiles.CENTER_PILE + 1)
        )

    @checkup
    def factory_string(self, factory_index):
        factory = self.factories[factory_index]
        string = ""
        for index in range(6):
            string += factory[index] * AzulTiles.color_string(index)
        return string

    @checkup
    def __repr__(self):
        strings = [self.factory_string(index) for index in range(6)]
        return "{" + " | ".join(strings) + "}"

    @checkup
    def take(self, *, factory, taken_color):
        if factory < AzulTiles.CENTER_PILE:
            for color in range(5):
                if color != taken_color:
                    self.factories[AzulTiles.CENTER_PILE][color] += self.factories[
                        factory
                    ][color]
            self.factories[factory] = [0, 0, 0, 0, 0, 0]
            return False
        else:
            self.factories[AzulTiles.CENTER_PILE][taken_color] = 0
            if self.factories[AzulTiles.CENTER_PILE][AzulTiles.FIRST_PLAYER] == 1:
                self.factories[AzulTiles.CENTER_PILE][AzulTiles.FIRST_PLAYER] = 0
                return True

    @checkup
    def __bool__(self):
        nonempty = any(
            self.factories[factory][color] > 0
            for factory in range(AzulTiles.CENTER_PILE + 1)
            for color in range(6)
        )
        return nonempty


class AzulState:

    def __init__(self, player, tiles, boards, strategies, history=None):
        self.player = player
        self.tiles = tiles
        self.boards = boards
        self.strategies = strategies
        self.history = history if history else ()

    def check(self):
        pass

    def optimal_strategy(
        self,
    ) -> tuple[tuple[float, ...], tuple[str, ...]]:
        optimal_result: tuple[tuple[float, ...], tuple[str, ...]] = (
            tuple(
                -sp.oo if p == self.player else sp.oo for p in range(len(self.boards))
            ),
            tuple(),
        )
        optimal_score = -sp.oo
        for color, factory, row in itertools.product(range(5), range(6), range(5)):
            count = self.tiles.factories[factory][color]
            if count > 0:
                new_player = (self.player + 1) % len(self.boards)
                new_tiles = copy.deepcopy(self.tiles)
                new_boards = copy.deepcopy(self.boards)
                new_strategies = self.strategies
                new_boards[self.player].place_in_row(color=color, count=count, row=row)
                if new_tiles.take(taken_color=color, factory=factory):
                    self.boards[self.player].broken_tiles += 1
                new_history = (
                    *self.history,
                    f"{AzulTiles.color_string(color)}: {factory} -> {self.player}.{row}",
                )
                state = AzulState(
                    new_player,
                    new_tiles,
                    new_boards,
                    new_strategies,
                    new_history,
                )
                result = state.label
                scores = result[0]
                result_score = min(
                    scores[self.player] - scores[p]
                    for p in range(len(self.boards))
                    if not p == self.player
                )
                if result_score > optimal_score:
                    optimal_result = result
                    optimal_score = result_score

        return optimal_result

    def bayesian_strategy(
        self, weights: Callable
    ) -> tuple[tuple[float, ...], tuple[str, ...]]:
        """
        NOTE: bayesian is not completely random. Which tiles this strategy takes are random,
        but once the tiles are determined, they are played optimally.

        :param weights:
        :return:
        """
        weighted_scores = tuple(0.0 for _ in range(len(self.boards)))
        new_history = (
            *self.history,
            f"*",
        )
        for color, factory in itertools.product(range(5), range(6)):
            optimal_scores = tuple(
                -sp.oo if p == self.player else sp.oo for p in range(len(self.boards))
            )
            optimal_score = -sp.oo
            for row in range(5):
                count = self.tiles.factories[factory][color]
                if count > 0:
                    new_player = (self.player + 1) % len(self.boards)
                    new_tiles = copy.deepcopy(self.tiles)
                    new_boards = copy.deepcopy(self.boards)
                    new_strategies = self.strategies
                    new_boards[self.player].place_in_row(
                        color=color, count=count, row=row
                    )
                    if new_tiles.take(taken_color=color, factory=factory):
                        self.boards[self.player].broken_tiles += 1
                    new_history = (
                        *self.history,
                        f"*",
                    )
                    state = AzulState(
                        new_player,
                        new_tiles,
                        new_boards,
                        new_strategies,
                        new_history,
                    )
                    row_result = state.label
                    row_scores = row_result[0]
                    # row_history = row_results[1] doesn't contain anything useful (we averaged over all possible moves)
                    row_score = min(
                        row_scores[self.player] - row_scores[p]
                        for p in range(len(self.boards))
                        if not p == self.player
                    )
                    if row_score > optimal_score:
                        optimal_score = row_score
                        optimal_scores = row_scores

            if not optimal_score == -sp.oo:
                # this color is available and I have an optimal scoring value for placing this color
                weighted_scores = tuple(
                    weighted_scores[i]
                    + weights(self.tiles, factory, color) * optimal_scores[i]
                    for i in range(len(weighted_scores))
                )

        return weighted_scores, new_history

    @property
    def label(self) -> tuple[tuple[float, ...], tuple[str, ...]]:
        if not self.tiles:
            for board in self.boards:
                board.score_round()
                board.score_game()
            result = (
                tuple(board.score for board in self.boards),
                self.history,
            )
            return result

        return self.strategies[self.player](self)


if __name__ == "__main__":
    ...
