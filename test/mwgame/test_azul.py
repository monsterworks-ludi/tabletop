import sympy as sp
import copy

from pytest import mark
from pytest_check import check  # type: ignore

from mwmath.monte_carlo import set_seed
from mwmath.extensive_form import GameMove
from mwgame.azul import AzulTiles, AzulBoard, AzulState, AzulMove

class TestAzul:

    @staticmethod
    def state(strategies) -> AzulState:
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

        state = AzulState(
            0,
            tiles,
            (board_zero, board_one),
            strategies,
        )
        return state

    @staticmethod
    def weights(initial_state: AzulState, move: AzulMove) -> sp.Rational:
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

    @staticmethod
    def test_rational() -> None:
        state = TestAzul.state(
            (AzulState.rational_strategy(AzulState.rank), AzulState.rational_strategy(AzulState.rank))
        )
        outcome = state.outcome
        with check:
            # Figure 6.8, p. 127
            assert outcome.payoffs == (28, 25)
        with check:
            # Figure 6.8, p. 127
            assert outcome.moves == (
                AzulMove(AzulTiles.RED, 3, 5, 3),
                AzulMove(AzulTiles.CYAN, 1, 5, 2),
                AzulMove(AzulTiles.BLUE, 3, 5, 0)
            )

    @staticmethod
    def test_bayesian() -> None:

        state = TestAzul.state(
            (
                AzulState.rational_strategy(AzulState.rank),
                AzulState.bayesian_strategy(TestAzul.weights),
            )
        )
        outcome = state.outcome
        with check:
            # Figure 6.10, p. 128
            assert (outcome.payoffs[0] - outcome.payoffs[1]) == sp.Rational(34, 10)
        with check:
            # Figure 6.10, p.128
            assert outcome.moves == (
                AzulMove(AzulTiles.CYAN, 1, 5, 1),
                GameMove()
            )

    @staticmethod
    @mark.parametrize("trials", [10_000])
    def test_monte_carlo(trials) -> None:
        seed = set_seed()
        blue_cummulative = (0, 0)
        red_cummulative = (0, 0)
        cyan_cummulative = (0, 0)
        for _ in range(trials):

            state = TestAzul.state(
                (
                    AzulState.rational_strategy(AzulState.rank),
                    AzulState.monte_carlo_strategy(TestAzul.weights),
                )
            )

            # try blue
            blue_state = copy.deepcopy(state)
            blue_state.tiles.piles[AzulTiles.CENTER_PILE][AzulTiles.BLUE] = 0
            blue_state.boards[0].patterns[0] = AzulBoard.PatternLine(
                1, AzulTiles.BLUE, 1
            )
            blue_state.boards[0].broken_tiles += 2
            blue_state.player = 1
            blue_state.clear_stashed_outcome()
            blue_outcome = blue_state.outcome
            blue_cummulative = tuple(
                blue_cummulative[i] + blue_outcome.payoffs[i] for i in range(2)
            )

            # try red
            red_state = copy.deepcopy(state)
            red_state.tiles.piles[AzulTiles.CENTER_PILE][AzulTiles.RED] = 0
            red_state.boards[0].patterns[4] = AzulBoard.PatternLine(
                5, AzulTiles.RED, 4
            )
            red_state.boards[0].broken_tiles += 0
            red_state.player = 1
            red_state.clear_stashed_outcome()
            red_outcome = red_state.outcome
            red_cummulative = tuple(
                red_cummulative[i] + red_outcome.payoffs[i] for i in range(2)
            )

            # try cyan
            cyan_state = copy.deepcopy(state)
            cyan_state.tiles.piles[AzulTiles.CENTER_PILE][AzulTiles.CYAN] = 0
            cyan_state.boards[0].patterns[1] = AzulBoard.PatternLine(
                2, AzulTiles.CYAN, 1
            )
            cyan_state.boards[0].broken_tiles += 0
            cyan_state.player = 1
            cyan_state.clear_stashed_outcome()
            cyan_outcome = cyan_state.outcome
            cyan_cummulative = tuple(
                cyan_cummulative[i] + cyan_outcome.payoffs[i] for i in range(2)
            )

        blue_mean = tuple(blue_cummulative[i] / trials for i in range(2))
        red_mean = tuple(red_cummulative[i] / trials for i in range(2))
        cyan_mean = tuple(cyan_cummulative[i] / trials for i in range(2))

        with check:
            # Figure 6.10, p. 128
            assert (
                abs((blue_mean[0] - blue_mean[1]) - 2.0) < 10**-1
            ), f"Bad Seed: {seed} and Trials: {trials}"
        with check:
            # Figure 6.10, p. 128
            assert (
                abs((red_mean[0] - red_mean[1]) - 3.2) < 10**-1
            ), f"Bad Seed: {seed} and Trials: {trials}"
        with check:
            # Figure 6.10, p. 128
            assert (
                abs((cyan_mean[0] - cyan_mean[1]) - 3.4) < 10**-1
            ), f"Bad Seed: {seed} and Trials: {trials}"
