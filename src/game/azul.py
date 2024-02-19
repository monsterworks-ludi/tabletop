import sympy as sp
import copy
import itertools
import random
from typing import Callable, Optional
from dataclasses import dataclass

from icecream import ic  # type: ignore

from util.debug import checkup, icp, icprint

ic.disable()

# todo: docstrings and type information


class AzulTiles:

    EMPTY = -1

    BLUE = 0
    YELLOW = 1
    RED = 2
    BLACK = 3
    CYAN = 4
    FIRST_PLAYER = 5

    COLOR_COUNT = 6

    CENTER_PILE = 5
    FACTORY_COUNT = 6

    @staticmethod
    def color_string(index):
        return ["_", "b", "y", "r", "k", "c", "1"][index + 1]

    # pile = [2, 1, 1, 0, 1, 0] = 2 blue, 1 yellow, 1 red, 0 black, 1 cyan, 0 firstplayer
    # piles = [pile, pile, pile, ..., pile]

    def __init__(self, piles):
        self.piles = piles

    def check(self):
        assert len(self.piles) == AzulTiles.FACTORY_COUNT
        assert all(len(pile) == AzulTiles.COLOR_COUNT for pile in self.piles)

    @checkup
    def pile_string(self, pile):
        string = ""
        for color in range(self.COLOR_COUNT):
            string += pile[color] * AzulTiles.color_string(color)
        return string

    @checkup
    def __repr__(self):
        strings = (self.pile_string(pile) for pile in self.piles)
        return "{" + " | ".join(strings) + "}"

    @checkup
    def take(self, *, factory, taken_color):
        if factory < AzulTiles.CENTER_PILE:
            for color in range(AzulTiles.COLOR_COUNT):
                if color != taken_color:
                    self.piles[AzulTiles.CENTER_PILE][color] += self.piles[factory][
                        color
                    ]
            self.piles[factory] = [0, 0, 0, 0, 0, 0]
            return False
        else:
            self.piles[AzulTiles.CENTER_PILE][taken_color] = 0
            if self.piles[AzulTiles.CENTER_PILE][AzulTiles.FIRST_PLAYER] == 1:
                self.piles[AzulTiles.CENTER_PILE][AzulTiles.FIRST_PLAYER] = 0
                return True

    @checkup
    def has_tiles(self, index):
        return any(
            self.piles[index][color] > 0 for color in range(AzulTiles.COLOR_COUNT)
        )

    @checkup
    def __bool__(self):
        nonempty = any(
            self.piles[factory][color] > 0
            for factory in range(AzulTiles.FACTORY_COUNT)
            for color in range(AzulTiles.COLOR_COUNT)
        )
        return nonempty


class AzulBoard:

    BROKEN_TILES_POINTS = [0, -1, -2, -4, -6, -8, -11, -14]

    ROW_COUNT = 5

    @dataclass
    class PatternLine:
        capacity: int
        color: int = AzulTiles.EMPTY
        count: int = 0

    @staticmethod
    def column(*, color, row) -> int:
        return (color + row) % AzulBoard.ROW_COUNT

    @staticmethod
    def color(*, row, column) -> int:
        return (column - row) % AzulBoard.ROW_COUNT

    def __init__(
        self, player, wall=None, patterns=None, score=0, broken_tiles=0
    ) -> None:
        self.player = player
        self.wall = wall if wall else sp.zeros(self.ROW_COUNT, self.ROW_COUNT)
        self.patterns = (
            patterns
            if patterns
            else [
                self.PatternLine(1),
                self.PatternLine(2),
                self.PatternLine(3),
                self.PatternLine(4),
                self.PatternLine(5),
            ]
        )
        self.score = score
        self.broken_tiles = broken_tiles

    def check(self) -> None:
        assert self.wall.shape == (self.ROW_COUNT, self.ROW_COUNT)
        assert len(self.patterns) == self.ROW_COUNT
        for row, pattern in enumerate(self.patterns):
            assert pattern.capacity == row + 1
            if pattern.color == AzulTiles.EMPTY:
                assert pattern.count == 0
            else:
                assert pattern.count <= pattern.capacity
                assert pattern.count > 0
                column = self.column(color=pattern.color, row=row)
                assert self.wall[row, column] == 0

    @checkup
    def wall_string(self, row) -> str:
        string = "["
        for col in range(self.ROW_COUNT):
            if self.wall[row, col] == 1:
                color = self.color(row=row, column=col)
                color_string = AzulTiles.color_string(color)
                string += color_string
            else:
                string += "_"
        string += "]"
        return string

    @checkup
    def pattern_string(self, pattern: PatternLine) -> str:
        string = f"{pattern.count * AzulTiles.color_string(pattern.color): >{self.ROW_COUNT}}"
        return string

    @checkup
    def __repr__(self) -> str:
        string = (
            f"Player {self.player}, Score {self.score}, Broken {self.broken_tiles}\n"
        )
        for row in range(self.ROW_COUNT):
            string += (
                self.pattern_string(self.patterns[row])
                + " "
                + self.wall_string(row)
                + "\n"
            )
        return string

    @checkup
    def legal_placement(self, *, color, row):
        if self.wall[row, self.column(color=color, row=row)] == 1:
            # cannot place in partial if already played to the wall
            return False
        if self.patterns[row].color not in {AzulTiles.EMPTY, color}:
            # cannot place in a partial of a different color
            return False
        if self.patterns[row].count == self.patterns[row].capacity:
            # cannot place in a full partial
            return False
        return True

    @checkup
    def place_in_partial(self, *, row, color, count):
        if not self.legal_placement(row=row, color=color):
            self.broken_tiles += count
        else:
            empty_spaces = self.patterns[row].capacity - self.patterns[row].count
            unbroken_tiles = min(count, empty_spaces)
            broken_tiles = count - unbroken_tiles
            self.patterns[row].color = color
            self.patterns[row].count += unbroken_tiles
            self.broken_tiles += broken_tiles

    @checkup
    def score_tile(self, row, col):
        points = 0
        hor_score = False
        ver_score = False
        for delta in range(1, row + 1):
            if self.wall[row - delta, col] == 1:
                hor_score = True
                points += 1
            else:
                break
        for delta in range(1, AzulBoard.ROW_COUNT - row):
            if self.wall[row + delta, col] == 1:
                hor_score = True
                points += 1
            else:
                break
        for delta in range(1, col + 1):
            if self.wall[row, col - delta] == 1:
                ver_score = True
                points += 1
            else:
                break
        for delta in range(1, AzulBoard.ROW_COUNT - col):
            if self.wall[row, col + delta] == 1:
                ver_score = True
                points += 1
            else:
                break
        if ver_score:
            points += 1
        if hor_score:
            points += 1
        if not (ver_score or hor_score):
            points += 1

        output = f"{self.player}: ({row}, {col}) gains {points} points"
        icp(output)
        self.score += points

    @checkup
    def score_round(self):
        for row, pattern in enumerate(self.patterns):
            if pattern.count == pattern.capacity:
                # row is filled, place the tile
                col = AzulBoard.column(row=row, color=pattern.color)
                assert self.wall[row, col] == 0
                self.wall[row, col] = 1
                self.patterns[row] = self.PatternLine(row + 1)
                self.score_tile(row, col)

        points = 0
        broken_tiles = self.broken_tiles
        if self.broken_tiles < len(AzulBoard.BROKEN_TILES_POINTS):
            points += AzulBoard.BROKEN_TILES_POINTS[self.broken_tiles]
        else:
            points += AzulBoard.BROKEN_TILES_POINTS[-1] + 3 * (
                self.broken_tiles - (len(AzulBoard.BROKEN_TILES_POINTS) - 1)
            )
        self.broken_tiles = 0

        output = f"{self.player}: {broken_tiles} broken tiles penalize {points} points"
        icp(output)
        self.score += points

        self.score = max(self.score, 0)

    @checkup
    def score_game(self):

        points = 0
        for row in range(AzulBoard.ROW_COUNT):
            if all(self.wall[row, col] == 1 for col in range(AzulBoard.ROW_COUNT)):
                points += 2
        output = f"{self.player}: rows score {points} points"
        icp(output)
        self.score += points

        points = 0
        for col in range(AzulBoard.ROW_COUNT):
            if all(self.wall[row, col] == 1 for row in range(AzulBoard.ROW_COUNT)):
                points += 7
        output = f"{self.player}: cols score {points} points"
        icp(output)
        self.score += points

        points = 0
        for diag in range(AzulBoard.ROW_COUNT):
            if all(
                self.wall[row, (row + diag) % AzulBoard.ROW_COUNT] == 1
                for row in range(AzulBoard.ROW_COUNT)
            ):
                points += 10
        output = f"{self.player}: diagonals score {points} points"
        icp(output)
        self.score += points


class AzulState:

    @dataclass
    class Strategy:
        scores: tuple[sp.Rational, ...]
        moves: tuple[str, ...]

    def __init__(self, player, tiles, boards, strategies, history=None) -> None:
        self.player = player
        self.tiles = tiles
        self.boards = boards
        self.strategies = strategies
        self.history = history if history else ()
        self.stashed_strategy: Optional[AzulState.Strategy] = None

    def check(self):
        pass

    @checkup
    def __repr__(self) -> str:
        string = f"Player: {self.player}\n {self.tiles}\n {self.boards[0]}\n {self.boards[1]}\n"
        if self.stashed_strategy is not None:
            string += ", Scores: {self.strategy.scores}, Moves: {self.strategy.moves}"
        return string

    @property
    @checkup
    def strategy(self) -> Strategy:
        return (
            self.stashed_strategy if self.stashed_strategy else self.compute_strategy()
        )

    @checkup
    def compute_strategy(self) -> Strategy:
        if not self.tiles:
            for board in self.boards:
                board.score_round()
                board.score_game()
            result = self.Strategy(
                tuple(board.score for board in self.boards),
                self.history,
            )
            self.stashed_strategy = result
        else:
            self.stashed_strategy = self.strategies[self.player](self)
        assert self.stashed_strategy is not None
        return self.stashed_strategy

    @checkup
    def branch_states_for(self, factory, color):
        count = self.tiles.piles[factory][color]
        if count > 0:
            for row in range(AzulBoard.ROW_COUNT):
                new_player = (self.player + 1) % len(self.boards)
                new_tiles = copy.deepcopy(self.tiles)
                new_boards = copy.deepcopy(self.boards)
                new_strategies = self.strategies
                new_boards[self.player].place_in_partial(
                    row=row, color=color, count=count
                )
                if new_tiles.take(taken_color=color, factory=factory):
                    # they took the first player marker
                    self.boards[self.player].broken_tiles += 1
                new_history = (
                    *self.history,
                    f"{AzulTiles.color_string(color)} ({count}): {factory} -> {self.player}.{row}",
                )
                state = AzulState(
                    new_player,
                    new_tiles,
                    new_boards,
                    new_strategies,
                    new_history,
                )
                yield state

    @property
    @checkup
    def branch_states(self):
        for factory in range(AzulTiles.COLOR_COUNT):
            if self.tiles.has_tiles(factory):
                for color in range(AzulTiles.COLOR_COUNT):
                    yield from self.branch_states_for(factory, color)

    @checkup
    def scores_to_score(self, scores):
        score = min(
            scores[self.player] - scores[p]
            for p in range(len(scores))
            if not p == self.player
        )
        return score

    @checkup
    def rational_strategy(
        self,
    ) -> Strategy:
        optimal_strategy = max(
            (state.strategy for state in self.branch_states),
            key=lambda strategy: self.scores_to_score(strategy.scores),
        )
        return optimal_strategy

    @checkup
    def bayesian_strategy(self, weights: Callable) -> Strategy:
        """
        NOTE: bayesian is not completely random. Which tiles this strategy takes are random,
        but once the tiles are determined, they are played optimally.

        :param weights:
        :return:
        """
        weighted_scores = tuple(sp.Integer(0) for _ in range(len(self.boards)))
        new_history = (
            *self.history,
            f"*",
        )
        for factory, color in itertools.product(
            range(AzulTiles.FACTORY_COUNT), range(AzulTiles.COLOR_COUNT)
        ):
            if self.tiles.piles[factory][color] > 0:
                optimal_strategy = max(
                    (
                        state.strategy
                        for state in self.branch_states_for(factory, color)
                    ),
                    key=lambda strategy: self.scores_to_score(strategy.scores),
                )
                weighted_scores = tuple(
                    weighted_scores[i]
                    + weights(self.tiles, factory, color) * optimal_strategy.scores[i]
                    for i in range(len(weighted_scores))
                )

        return self.Strategy(weighted_scores, new_history)

    @checkup
    def monte_carlo_strategy(self, weights: Callable, probability: float) -> Strategy:
        """
        NOTE: monte carlo is not completely random. Which tiles this strategy takes are random,
        but once the tiles are determined, they are played optimally.

        # todo:
        Passing in the random number seemed to make it work in early attempts.
        I think this was because in the original implementation,
        a different probability was computed with each row (and not each color seletion).
        In the current implemention, we are calling this function after fixing the row.
        I think the probability could be executed within this method instead of being passed in.

        :param weights:
        :param probability: this is the value used to determine which tile is chosen
        :return:
        """
        cummulative_probability = 0
        optimal_strategy = None
        for factory, color in itertools.product(
            range(AzulTiles.FACTORY_COUNT), range(AzulTiles.COLOR_COUNT)
        ):
            if self.tiles.piles[factory][color] > 0:
                cummulative_probability += weights(self.tiles, factory, color)
                ic(cummulative_probability)
                ic(probability)
                if probability < cummulative_probability:
                    ic(f"Trying {color}")
                    optimal_strategy = max(
                        (
                            state.strategy
                            for state in self.branch_states_for(factory, color)
                        ),
                        key=lambda strategy: self.scores_to_score(strategy.scores),
                    )
                    ic(optimal_strategy)
                    break
        ic(optimal_strategy)
        assert optimal_strategy is not None
        return optimal_strategy


if __name__ == "__main__":

    # region Interactive Testing

    def make_state(strategies) -> AzulState:
        board_zero = AzulBoard(
            0,
            sp.Matrix(
                [
                    [0, 1, 1, 0, 1],
                    [0, 1, 0, 1, 1],
                    [1, 0, 0, 0, 1],
                    [0, 1, 0, 1, 0],
                    [0, 0, 0, 0, 1],
                ]
            ),
            [
                AzulBoard.PatternLine(1),
                AzulBoard.PatternLine(2),
                AzulBoard.PatternLine(3, AzulTiles.BLUE, 2),
                AzulBoard.PatternLine(4),
                AzulBoard.PatternLine(5, AzulTiles.RED, 1),
            ],
            29,
            1,
        )

        board_one = AzulBoard(
            1,
            sp.Matrix(
                [
                    [0, 1, 0, 0, 0],
                    [1, 1, 1, 0, 0],
                    [1, 0, 1, 1, 1],
                    [0, 1, 0, 0, 0],
                    [1, 1, 1, 0, 0],
                ]
            ),
            [
                AzulBoard.PatternLine(1, AzulTiles.BLUE, 1),
                AzulBoard.PatternLine(2),
                AzulBoard.PatternLine(3),
                AzulBoard.PatternLine(4, AzulTiles.CYAN, 2),
                AzulBoard.PatternLine(5, AzulTiles.BLUE, 4),
            ],
            20,
            0,
        )

        tiles = AzulTiles(
            [  # b, y, r, k, c, 1 #
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [3, 0, 3, 0, 1, 0],
            ]
        )

        state = AzulState(
            0,
            tiles,
            (board_zero, board_one),
            strategies,
        )
        return state

    STATE = make_state(
        (
            AzulState.rational_strategy,
            AzulState.rational_strategy,
        )
    )

    with icprint(False):
        icp("START OF RATIONAL GAME")
        ic(STATE.boards[0])
        ic(STATE.boards[1])
        ic(STATE.tiles)
        icp("RUNNING RATIONAL GAME")
        STATE.compute_strategy()
        icp("END OF RATIONAL GAME")
        ic(STATE.boards[0])
        ic(STATE.boards[1])
        ic(STATE.strategy)

    def sample_weights(tiles: AzulTiles, factory: int, color: int) -> float:

        assert all(
            tiles.piles[factory][color] == 0
            for factory in range(AzulTiles.CENTER_PILE)
            for color in range(6)
        ), "Unexpected Tile Decision"
        assert all(
            tiles.piles[AzulTiles.CENTER_PILE][color] == 0
            for color in {AzulTiles.YELLOW, AzulTiles.BLACK}
        ), "Unexpected Tile Decision"
        assert color in {
            AzulTiles.BLUE,
            AzulTiles.RED,
            AzulTiles.CYAN,
        }, "Unexpected Tile Decision"

        if tiles.piles[factory][AzulTiles.RED] == 0:
            if color == AzulTiles.CYAN:
                return 0.8
            else:
                assert color == AzulTiles.BLUE, "Unexpected Tile Decision"
                return 0.2

        elif tiles.piles[factory][AzulTiles.BLUE] == 0:
            if color == AzulTiles.CYAN:
                return 0.8
            else:
                assert color == AzulTiles.RED, "Unexpected Tile Decision"
                return 0.2
        elif tiles.piles[factory][AzulTiles.CYAN] == 0:
            if color == AzulTiles.BLUE:
                return 0.9
            else:
                assert color == AzulTiles.RED, "Unexpected Tile Decision"
                return 0.1
        else:
            assert False, "Unexpected Tile Decision"

    STATE = make_state(
        (
            AzulState.rational_strategy,
            lambda state: AzulState.bayesian_strategy(state, sample_weights),
        )
    )

    with icprint(False):
        icp("START OF BAYESIAN GAME")
        ic(STATE.boards[0])
        ic(STATE.boards[1])
        ic(STATE.tiles)
        icp("RUNNING BAYESIAN GAME")
        STATE.compute_strategy()
        icp("END OF BAYESIAN GAME")
        ic(STATE.boards[0])
        ic(STATE.boards[1])
        ic(STATE.strategy)

    BLUE_SUM = (0, 0)
    RED_SUM = (0, 0)
    CYAN_SUM = (0, 0)
    TOTAL_TRIALS = 100_000
    for _ in range(TOTAL_TRIALS):

        STATE = make_state(
            (
                AzulState.rational_strategy,
                lambda state: AzulState.monte_carlo_strategy(
                    state, sample_weights, random.random()
                ),
            )
        )

        # try blue
        BLUE_STATE = copy.deepcopy(STATE)
        BLUE_STATE.tiles.piles[AzulTiles.CENTER_PILE][AzulTiles.BLUE] = 0
        BLUE_STATE.boards[0].patterns[0] = AzulBoard.PatternLine(1, AzulTiles.BLUE, 1)
        BLUE_STATE.boards[0].broken_tiles += 2
        BLUE_STATE.player = 1
        with icprint():
            ic(BLUE_STATE)

        BLUE_STRAT = BLUE_STATE.compute_strategy()
        BLUE_SUM = tuple(BLUE_SUM[i] + BLUE_STRAT.scores[i] for i in range(2))

        # try red
        RED_STATE = copy.deepcopy(STATE)
        RED_STATE.tiles.piles[AzulTiles.CENTER_PILE][AzulTiles.RED] = 0
        RED_STATE.boards[0].patterns[4] = AzulBoard.PatternLine(5, AzulTiles.RED, 4)
        RED_STATE.boards[0].broken_tiles += 0
        RED_STATE.player = 1
        with icprint():
            ic(RED_STATE)

        RED_STRAT = RED_STATE.compute_strategy()
        RED_SUM = tuple(RED_SUM[i] + RED_STRAT.scores[i] for i in range(2))

        # try cyan
        CYAN_STATE = copy.deepcopy(STATE)
        CYAN_STATE.tiles.piles[AzulTiles.CENTER_PILE][AzulTiles.CYAN] = 0
        CYAN_STATE.boards[0].patterns[1] = AzulBoard.PatternLine(2, AzulTiles.CYAN, 1)
        CYAN_STATE.boards[0].broken_tiles += 0
        CYAN_STATE.player = 1
        with icprint():
            ic(CYAN_STATE)

        CYAN_STRAT = CYAN_STATE.compute_strategy()
        CYAN_SUM = tuple(CYAN_SUM[i] + CYAN_STRAT.scores[i] for i in range(2))

    BLUE_AVERAGE = tuple(BLUE_SUM[i] / TOTAL_TRIALS for i in range(2))
    RED_AVERAGE = tuple(RED_SUM[i] / TOTAL_TRIALS for i in range(2))
    CYAN_AVERAGE = tuple(CYAN_SUM[i] / TOTAL_TRIALS for i in range(2))

    print(
        BLUE_AVERAGE[0] - BLUE_AVERAGE[1],
        RED_AVERAGE[0] - RED_AVERAGE[1],
        CYAN_AVERAGE[0] - CYAN_AVERAGE[1],
    )

    # endregion
