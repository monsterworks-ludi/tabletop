import sympy as sp
import copy
from typing import Callable, Optional
from dataclasses import dataclass

from icecream import ic  # type: ignore

from util.debug import checkup, icp
from mwmath.extensive_form import GameMove, GameOutcome, GameState

ic.disable()


class AzulTiles:
    """ Reprents the five factory piles and the center pile of tiles in an Azul game. """

    EMPTY = -1
    """ Represents an empty space """

    BLUE = 0
    """ symbolic value for tile color """
    YELLOW = 1
    """ symbolic value for tile color """
    RED = 2
    """ symbolic value for tile color """
    BLACK = 3
    """ symbolic value for tile color """
    CYAN = 4
    """ symbolic value for tile color """
    FIRST_PLAYER = 5
    """ symbolic value for first player tile """

    COLOR_COUNT = 6
    """ number of tile colors that can be in a pile """

    CENTER_PILE = 5
    """ the index for the center pile of tiles """

    FACTORY_COUNT = 6
    """ the number of factories """

    @staticmethod
    def color_string(color: int) -> str:
        """

        :param color: the index of the color
        :return: a single character representation of that color
        """
        return ["_", "b", "y", "r", "k", "c", "1"][color + 1]

    # pile = [2, 1, 1, 0, 1, 0] = 2 blue, 1 yellow, 1 red, 0 black, 1 cyan, 0 firstplayer
    # piles = [pile, pile, pile, ..., pile]

    def __init__(self, piles) -> None:
        self._piles = piles

    @property
    def piles(self) -> list[list[int]]:
        return self._piles

    def __hash__(self) -> int:
        raise NotImplementedError

    def hash(self) -> int:
        piles = tuple(tuple(pile) for pile in self._piles)
        return hash(piles)

    def check(self) -> None:
        assert len(self.piles) == AzulTiles.FACTORY_COUNT
        assert all(len(pile) == AzulTiles.COLOR_COUNT for pile in self.piles)

    @checkup
    def pile_string(self, pile: list[int]) -> str:
        """

        :param pile: the pile whose string we want
        :return: the string representation of the pile
        """
        string = ""
        for color in range(self.COLOR_COUNT):
            string += pile[color] * AzulTiles.color_string(color)
        return string

    @checkup
    def __repr__(self) -> str:
        strings = (self.pile_string(pile) for pile in self.piles)
        return "{" + " | ".join(strings) + "}"

    @checkup
    def take(self, *, factory: int, taken_color: int) -> bool:
        """

        :param factory: the factory from which to take the tile
        :param taken_color: the color taken from that factory
        :return: True if the player took the first player tile, False otherwise
        """
        took_first_player_tile = False
        if factory < AzulTiles.CENTER_PILE:
            for color in range(AzulTiles.COLOR_COUNT):
                if color != taken_color:
                    self.piles[AzulTiles.CENTER_PILE][color] += self.piles[factory][
                        color
                    ]
            self.piles[factory] = [0, 0, 0, 0, 0, 0]
        else:
            self.piles[AzulTiles.CENTER_PILE][taken_color] = 0
            if self.piles[AzulTiles.CENTER_PILE][AzulTiles.FIRST_PLAYER] == 1:
                self.piles[AzulTiles.CENTER_PILE][AzulTiles.FIRST_PLAYER] = 0
                took_first_player_tile = True
        return took_first_player_tile

    @checkup
    def has_tiles(self, factory: int) -> bool:
        """

        :param factory: the factory we are checking
        :return: True if there are tiles remaining in that factory
        """
        return any(
            self.piles[factory][color] > 0 for color in range(AzulTiles.COLOR_COUNT)
        )

    @checkup
    def __bool__(self) -> bool:
        """

        :return: True if there are any tiles remaining in any factories
        """
        nonempty = any(
            self.piles[factory][color] > 0
            for factory in range(AzulTiles.FACTORY_COUNT)
            for color in range(AzulTiles.COLOR_COUNT)
        )
        return nonempty

class AzulBoard:

    BROKEN_TILES_POINTS = [0, -1, -2, -4, -6, -8, -11, -14]
    """ Points deducted for broken tiles, beyond this, players lose 3 points per tile"""

    ROW_COUNT = 5
    """ Number of rows in the player's wall """

    @dataclass
    class PatternLine:
        """the pattern line on a player board"""

        capacity: int
        """ the number of tiles that fit in the pattern line (equal to row + 1) """
        color: int = AzulTiles.EMPTY
        """ the color of the tiles in the pattern line """
        count: int = 0
        """ the number of tiles in the pattern line """

        def __hash__(self) -> int:
            raise NotImplementedError

        def hash(self) -> int:
            return hash((self.capacity, self.color, self.count))

    @staticmethod
    def column(*, color, row) -> int:
        """

        :param color: the color of the tile
        :param row: the row of the tile's position on the wall
        :return: the column of the tile's position on the wall
        """
        return (color + row) % AzulBoard.ROW_COUNT

    @staticmethod
    def color(*, row, column) -> int:
        """

        :param row: the row of tile's position on the wall
        :param column: the column of the tile's position on the wall
        :return: the color of the tile at that position
        """
        return (column - row) % AzulBoard.ROW_COUNT

    def __init__(
        self,
        player: int,
        wall: Optional[sp.Matrix] = None,
        patterns: Optional[list[PatternLine]] = None,
        score: sp.Rational = sp.Integer(0),
        broken_tiles: int = 0,
    ) -> None:
        """

        :param player: the player number
        :param wall: the tiles in the player's walls (1 indicates a tile, 0 indicates no tile)
        :param patterns: the tiles in the player's patterns
        :param score: the player's current score
        :param broken_tiles: the number of broken tiles on the player's board
        """
        self._player = player
        self._wall = wall if wall else sp.zeros(self.ROW_COUNT, self.ROW_COUNT)
        self._patterns = (
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
        self._score = score
        self._broken_tiles: int = broken_tiles

    def __hash__(self) -> int:
        """ AzulBoard is mutable, so this is intentionally unimplemented. """
        raise NotImplementedError

    def hash(self) -> int:
        """ returns a hash used to quickly check if our values have changed. """
        wall = sp.ImmutableMatrix(self._wall)
        patterns = tuple(pattern.hash() for pattern in self._patterns)
        return hash((self._player, wall, patterns, self._score, self._broken_tiles))

    @property
    def player(self) -> int:
        return self._player

    @property
    def wall(self) -> sp.Matrix:
        assert self._wall is not None
        return self._wall

    @property
    def patterns(self) -> list[PatternLine]:
        assert self._patterns is not None
        return self._patterns

    @property
    def score(self) -> sp.Rational:
        return self._score

    @score.setter
    def score(self, score: sp.Rational) -> None:
        self._score = score

    @property
    def broken_tiles(self) -> int:
        return self._broken_tiles

    @broken_tiles.setter
    def broken_tiles(self, broken_tiles: int) -> None:
        self._broken_tiles = broken_tiles

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
        """

        :param row: the row whose string representation we want
        :return: the string representation of that row
        """
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
        """

        :param pattern: the row whose string representation of the pattern lines we want
        :return: the string representation of that pattern line
        """
        string = f"{pattern.count * AzulTiles.color_string(pattern.color): >{self.ROW_COUNT}}"
        return string

    @checkup
    def __repr__(self) -> str:
        """the string representation of the player's board"""
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
    def legal_placement(self, *, color: int, row: int) -> bool:
        """

        :param color: the color of the tile to be placed
        :param row: the row of the pattern line into which the tile will be placed
        :return: True if the tile may be placed on that pattern line
        """
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
    def place_in_partial(self, *, row: int, color: int, count: int) -> None:
        """
        Places as many tiles as possible into the partial and breaks the remaining tiles

        :param row: the row into which the tile is placed
        :param color: the color of the tile
        :param count: the number of tiles
        """
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
    def score_tile(self, row: int, col: int) -> None:
        """

        :param row: the row the tile is placed in
        :param col: the column the tile is placed in
        :return: the score obtained by placing this tile based on neighboring tiles in the wall
        """
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
    def score_round(self) -> None:
        """

        :return: the score of the player after moving all eligible tiles from the partials to the wall
        """
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

        self.score = max(self.score, sp.Integer(0))

    @checkup
    def score_game(self) -> None:
        """
        Adds points to the player's score based on end of game scoring (rows, columns, and diagonals)
        """
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


@dataclass(frozen=True)
class AzulMove(GameMove):
    """ A move in Azul takes (count) tiles with color (color) from factory (factory) and places them in pattern (row)"""
    color: int
    count: int
    factory: int
    row: int

    def __repr__(self):
        return f"{AzulTiles.color_string(self.color)} ({self.count}): Factory {self.factory} -> Row {self.row}"


class AzulState(GameState):

    def __init__(
        self,
        player: int,
        tiles: AzulTiles,
        boards: tuple[AzulBoard, ...],
        strategies: tuple[Callable, ...],
        history: Optional[tuple[GameMove, ...]] = None,
    ) -> None:
        """

        :param player: the player to make the next move
        :param tiles: the tiles available for that player
        :param boards: the player boards for each player
        :param strategies: the strategies for each player
        :param history: the sequence of moves leading to this point in the game
        """
        super().__init__(player, strategies, history)
        self._tiles = tiles
        self._boards = boards

    def __hash__(self) -> int:
        """ AzulState is mutable, so this is intentionally unimplemented """
        raise NotImplementedError

    def hash(self) -> int:
        """
        This is used to quickly check if the state has changed.

        :return: the hash of the current state
        """
        return hash((super().hash(), self._tiles.hash(), tuple(board.hash() for board in self._boards)))

    @checkup
    def __repr__(self) -> str:
        string = super().__repr__()
        string += f"\nTiles: {self.tiles}\n"
        for player, board in enumerate(self.boards):
            string += f"Player {player} Board: {self.boards[player]}\n"
        return string

    def check(self):
        super().check()
        assert self.players == len(self.boards)

    @property
    def tiles(self) -> AzulTiles:
        return self._tiles

    @property
    def boards(self) -> tuple[AzulBoard, ...]:
        return self._boards

    @property
    @checkup
    def game_over(self) -> bool:
        return not self.tiles

    @checkup
    def compute_outcome(self) -> GameOutcome:
        for board in self.boards:
            board.score_round()
            board.score_game()
        result = GameOutcome(tuple(board.score for board in self.boards), self.history)
        return result

    @checkup
    # maybe this should be optimal_branch_state_for() and just return one state
    def branch_states_for(self, factory: int, color: int):
        """

        :param factory: the factory from which the tiles are taken
        :param color: the color of tile taken
        :return: the states that result from trying the tile in different rows
        """
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
                if self.history is None:
                    new_history: tuple[GameMove, ...] = (
                        AzulMove(color, count, factory, row),
                    )
                else:
                    new_history = self.history + (AzulMove(color, count, factory, row),)
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
        """

        :return: the possible states that continue the game from this state assuming optimal row selected
        """
        for factory in range(AzulTiles.COLOR_COUNT):
            if self.tiles.has_tiles(factory):
                for color in range(AzulTiles.COLOR_COUNT):
                    if self.tiles.piles[factory][color] > 0:
                        optimal_state = max(
                            (
                                branch
                                for branch in self.branch_states_for(factory, color)
                            ),
                            key=lambda b: AzulState.rank(self.player, b.outcome),
                        )
                        yield optimal_state

    @staticmethod
    def rank(player: int, outcome: GameOutcome) -> sp.Rational:
        """

        :param player: the player from whose perspective the ranking occurs
        :param outcome: the outcome of this strategy
        :return: the worst relative score between this player and the other players
        """
        score = min(
            outcome.payoffs[player] - payoff
            for p, payoff in enumerate(outcome.payoffs)
            if not p == player
        )
        return score


def main():

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
            sp.Integer(29),
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
            sp.Integer(20),
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

        result = AzulState(
            0,
            tiles,
            (board_zero, board_one),
            strategies,
        )
        return result

    # RATIONAL ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    print("")
    print("~~ START OF RATIONAL GAME " + 10 * "~")
    state = make_state(
        (
            AzulState.rational_strategy(AzulState.rank),
            AzulState.rational_strategy(AzulState.rank),
        )
    )
    print(f"{state.boards[0]}")
    print(f"{state.boards[1]}")
    print(f"Tiles: {state.tiles}\n")
    print(f"{state.outcome}\n")

    # BAYESIAN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    print("~~ START OF BAYESIAN GAME " + 10 * "~")

    def sample_weights(initial_state: AzulState, move: AzulMove) -> sp.Rational:
        piles = initial_state.tiles.piles
        color = move.color
        factory = move.factory
        # all tiles are in the center pile
        assert all(sum(piles[f]) == 0 for f in range(AzulTiles.CENTER_PILE))
        # there are no yellow or black tiles
        assert all(
            piles[AzulTiles.CENTER_PILE][c] == 0
            for c in {AzulTiles.YELLOW, AzulTiles.BLACK}
        )
        assert color in {AzulTiles.BLUE, AzulTiles.RED, AzulTiles.CYAN}
        assert factory == AzulTiles.CENTER_PILE

        if piles[factory][AzulTiles.RED] == 0:
            if color == AzulTiles.CYAN:
                return sp.Rational(8, 10)
            else:
                assert color == AzulTiles.BLUE, "Unexpected Tile Decision"
                return sp.Rational(2, 10)

        elif piles[factory][AzulTiles.BLUE] == 0:
            if color == AzulTiles.CYAN:
                return sp.Rational(8, 10)
            else:
                assert color == AzulTiles.RED, "Unexpected Tile Decision"
                return sp.Rational(2, 10)
        elif piles[factory][AzulTiles.CYAN] == 0:
            if color == AzulTiles.BLUE:
                return sp.Rational(9, 10)
            else:
                assert color == AzulTiles.RED, "Unexpected Tile Decision"
                return sp.Rational(1, 10)
        else:
            assert False, "Unexpected Tile Decision"

    state = make_state(
        (
            AzulState.rational_strategy(AzulState.rank),
            AzulState.bayesian_strategy(sample_weights),
        )
    )
    print(f"{state.boards[0]}")
    print(f"{state.boards[1]}")
    print(f"Tiles: {state.tiles}\n")
    print(f"{state.outcome}\n")

    # MONTE CARLO ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    print("~~ START OF MONTE CARLO GAMES " + 10 * "~")
    print(f"{state.boards[0]}")
    print(f"{state.boards[1]}")
    print(f"Tiles: {state.tiles}\n")
    print("RUNNING MONTE CARLO GAMES")

    blue_sum = (0, 0)
    red_sum = (0, 0)
    cyan_sum = (0, 0)
    total_trials = 1_000
    for _ in range(total_trials):

        state = make_state(
            (
                AzulState.rational_strategy(AzulState.rank),
                AzulState.monte_carlo_strategy(sample_weights),
            )
        )

        # try blue
        blue_state = copy.deepcopy(state)
        blue_state.tiles.piles[AzulTiles.CENTER_PILE][AzulTiles.BLUE] = 0
        blue_state.boards[0].patterns[0] = AzulBoard.PatternLine(1, AzulTiles.BLUE, 1)
        blue_state.boards[0].broken_tiles += 2
        blue_state.player = 1
        blue_outcome = blue_state.outcome
        blue_sum = tuple(blue_sum[i] + blue_outcome.payoffs[i] for i in range(2))

        # try red
        red_state = copy.deepcopy(state)
        red_state.tiles.piles[AzulTiles.CENTER_PILE][AzulTiles.RED] = 0
        red_state.boards[0].patterns[4] = AzulBoard.PatternLine(5, AzulTiles.RED, 4)
        red_state.boards[0].broken_tiles += 0
        red_state.player = 1
        red_outcome = red_state.outcome
        red_sum = tuple(red_sum[i] + red_outcome.payoffs[i] for i in range(2))

        # try cyan
        cyan_state = copy.deepcopy(state)
        cyan_state.tiles.piles[AzulTiles.CENTER_PILE][AzulTiles.CYAN] = 0
        cyan_state.boards[0].patterns[1] = AzulBoard.PatternLine(2, AzulTiles.CYAN, 1)
        cyan_state.boards[0].broken_tiles += 0
        cyan_state.player = 1
        cyan_outcome = cyan_state.outcome
        cyan_sum = tuple(cyan_sum[i] + cyan_outcome.payoffs[i] for i in range(2))

    print("END OF MONTE CARLO GAMES")

    blue_average = tuple(blue_sum[i] / total_trials for i in range(2))
    red_average = tuple(red_sum[i] / total_trials for i in range(2))
    cyan_average = tuple(cyan_sum[i] / total_trials for i in range(2))

    print(f"Expected Blue Payoff: {1.0*blue_average[0] - blue_average[1]} ≈ 2")
    print(f"Expected Red Payoff: {1.0*red_average[0] - red_average[1]} ≈ 3.2")
    print(f"Expected Cyan Payoff: {1.0*cyan_average[0] - cyan_average[1]} ≈ 3.4")


if __name__ == "__main__":
    main()
