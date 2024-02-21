import sympy as sp
import copy

from pytest import mark
from pytest_check import check  # type: ignore

import mwmath.monte_carlo as mc
import game.azul as az


class TestAzul:

    @staticmethod
    def state(strategies) -> az.AzulState:
        board_zero = az.AzulBoard(
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
                az.AzulBoard.PatternLine(1),
                az.AzulBoard.PatternLine(2),
                az.AzulBoard.PatternLine(3, az.AzulTiles.BLUE, 2),
                az.AzulBoard.PatternLine(4),
                az.AzulBoard.PatternLine(5, az.AzulTiles.RED, 1),
            ],
            sp.Integer(29),
            1,
        )

        board_one = az.AzulBoard(
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
                az.AzulBoard.PatternLine(1, az.AzulTiles.BLUE, 1),
                az.AzulBoard.PatternLine(2),
                az.AzulBoard.PatternLine(3),
                az.AzulBoard.PatternLine(4, az.AzulTiles.CYAN, 2),
                az.AzulBoard.PatternLine(5, az.AzulTiles.BLUE, 4),
            ],
            sp.Integer(20),
            0,
        )

        tiles = az.AzulTiles(
            [  # b, y, r, k, c, 1 #
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [3, 0, 3, 0, 1, 0],
            ]
        )

        state = az.AzulState(
            0,
            tiles,
            (board_zero, board_one),
            strategies,
        )
        return state

    @staticmethod
    def weights(tiles: az.AzulTiles, _: int, color: int) -> float:

        assert all(
            tiles.piles[factory][color] == 0
            for factory in range(az.AzulTiles.CENTER_PILE)
            for color in range(az.AzulTiles.COLOR_COUNT)
        ), "Unexpected Tile Decision"
        assert all(
            tiles.piles[az.AzulTiles.CENTER_PILE][color] == 0
            for color in {az.AzulTiles.YELLOW, az.AzulTiles.BLACK}
        ), "Unexpected Tile Decision"
        assert color in {
            az.AzulTiles.BLUE,
            az.AzulTiles.RED,
            az.AzulTiles.CYAN,
        }, "Unexpected Tile Decision"

        if tiles.piles[az.AzulTiles.CENTER_PILE][az.AzulTiles.RED] == 0:
            if color == az.AzulTiles.CYAN:
                return sp.Rational(8, 10)
            else:
                assert color == az.AzulTiles.BLUE, "Unexpected Tile Decision"
                return sp.Rational(2, 10)

        elif tiles.piles[az.AzulTiles.CENTER_PILE][az.AzulTiles.BLUE] == 0:
            if color == az.AzulTiles.CYAN:
                return sp.Rational(8, 10)
            else:
                assert color == az.AzulTiles.RED, "Unexpected Tile Decision"
                return sp.Rational(2, 10)
        elif tiles.piles[az.AzulTiles.CENTER_PILE][az.AzulTiles.CYAN] == 0:
            if color == az.AzulTiles.BLUE:
                return sp.Rational(9, 10)
            else:
                assert color == az.AzulTiles.RED, "Unexpected Tile Decision"
                return sp.Rational(1, 10)
        else:
            assert False, "Unexpected Tile Decision"

    @staticmethod
    def test_rational() -> None:
        state = TestAzul.state(
            (az.AzulState.rational_strategy, az.AzulState.rational_strategy)
        )
        strategy = state.outcome
        with check:
            # Figure 6.8, p. 127
            assert strategy.scores == (28, 25)
        with check:
            # Figure 6.8, p. 127
            assert strategy.moves == (
                "r (3): 5 -> 0.3",
                "c (1): 5 -> 1.2",
                "b (3): 5 -> 0.0",
            )

    @staticmethod
    def test_bayesian() -> None:

        state = TestAzul.state(
            (
                az.AzulState.rational_strategy,
                lambda s: az.AzulState.bayesian_strategy(s, TestAzul.weights),
            )
        )
        strategy = state.outcome
        with check:
            # Figure 6.10, p. 128
            assert (strategy.scores[0] - strategy.scores[1]) == sp.Rational(34, 10)
        with check:
            # Figure 6.10, p.128
            assert strategy.moves == ("c (1): 5 -> 0.1", "*")

    @staticmethod
    @mark.parametrize("trials", [10_000])
    def test_monte_carlo(trials) -> None:
        seed = mc.set_seed()
        blue_cummulative = (0, 0)
        red_cummulative = (0, 0)
        cyan_cummulative = (0, 0)
        for _ in range(trials):

            state = TestAzul.state(
                (
                    az.AzulState.rational_strategy,
                    lambda s: az.AzulState.monte_carlo_strategy(s, TestAzul.weights),
                )
            )

            # try blue
            blue_state = copy.deepcopy(state)
            blue_state.tiles.piles[az.AzulTiles.CENTER_PILE][az.AzulTiles.BLUE] = 0
            blue_state.boards[0].patterns[0] = az.AzulBoard.PatternLine(
                1, az.AzulTiles.BLUE, 1
            )
            blue_state.boards[0].broken_tiles += 2
            blue_state.player = 1
            blue_strat = blue_state.compute_outcome()
            blue_cummulative = tuple(
                blue_cummulative[i] + blue_strat.scores[i] for i in range(2)
            )

            # try red
            red_state = copy.deepcopy(state)
            red_state.tiles.piles[az.AzulTiles.CENTER_PILE][az.AzulTiles.RED] = 0
            red_state.boards[0].patterns[4] = az.AzulBoard.PatternLine(
                5, az.AzulTiles.RED, 4
            )
            red_state.boards[0].broken_tiles += 0
            red_state.player = 1

            red_strat = red_state.compute_outcome()
            red_cummulative = tuple(
                red_cummulative[i] + red_strat.scores[i] for i in range(2)
            )

            # try cyan
            cyan_state = copy.deepcopy(state)
            cyan_state.tiles.piles[az.AzulTiles.CENTER_PILE][az.AzulTiles.CYAN] = 0
            cyan_state.boards[0].patterns[1] = az.AzulBoard.PatternLine(
                2, az.AzulTiles.CYAN, 1
            )
            cyan_state.boards[0].broken_tiles += 0
            cyan_state.player = 1

            cyan_strat = cyan_state.compute_outcome()
            cyan_cummulative = tuple(
                cyan_cummulative[i] + cyan_strat.scores[i] for i in range(2)
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
