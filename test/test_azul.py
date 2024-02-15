import sympy as sp

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
                [az.AzulTiles.EMPTY, 0],
                [az.AzulTiles.EMPTY, 0],
                [az.AzulTiles.BLUE, 2],
                [az.AzulTiles.EMPTY, 0],
                [az.AzulTiles.RED, 1],
            ],
            29,
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
                [az.AzulTiles.BLUE, 1],
                [az.AzulTiles.EMPTY, 0],
                [az.AzulTiles.EMPTY, 0],
                [az.AzulTiles.CYAN, 2],
                [az.AzulTiles.BLUE, 4],
            ],
            20,
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
    def test_rational() -> None:
        state = TestAzul.state(
            (az.AzulState.optimal_strategy, az.AzulState.optimal_strategy)
        )
        scores, history = state.label
        assert scores == (28, 25)
        assert history == ("r: 5 -> 0.3", "c: 5 -> 1.2", "b: 5 -> 0.0")

    @staticmethod
    def test_bayesian() -> None:

        def weights(tiles: az.AzulTiles, _: int, color: int) -> float:

            assert all(
                tiles.factories[factory][color] == 0
                for factory in range(az.AzulTiles.CENTER_PILE)
                for color in range(6)
            ), "Unexpected Tile Decision"
            assert all(
                tiles.factories[az.AzulTiles.CENTER_PILE][color] == 0
                for color in {az.AzulTiles.YELLOW, az.AzulTiles.BLACK}
            ), "Unexpected Tile Decision"
            assert color in {az.AzulTiles.BLUE, az.AzulTiles.RED, az.AzulTiles.CYAN}, "Unexpected Tile Decision"

            if tiles.factories[az.AzulTiles.CENTER_PILE][az.AzulTiles.RED] == 0:
                if color == az.AzulTiles.CYAN:
                    return 0.8
                else:
                    assert color == az.AzulTiles.BLUE, "Unexpected Tile Decision"
                    return 0.2

            elif tiles.factories[az.AzulTiles.CENTER_PILE][az.AzulTiles.BLUE] == 0:
                if color == az.AzulTiles.CYAN:
                    return 0.8
                else:
                    assert color == az.AzulTiles.RED, "Unexpected Tile Decision"
                    return 0.2
            elif tiles.factories[az.AzulTiles.CENTER_PILE][az.AzulTiles.CYAN] == 0:
                if color == az.AzulTiles.BLUE:
                    return 0.9
                else:
                    assert color == az.AzulTiles.RED, "Unexpected Tile Decision"
                    return 0.1
            else:
                assert False, "Unexpected Tile Decision"

        state = TestAzul.state(
            (
                az.AzulState.optimal_strategy,
                lambda s: az.AzulState.bayesian_strategy(s, weights),
            )
        )
        scores, history = state.label
        assert abs((scores[0] - scores[1]) - 3.4) < 10**-14
        assert history == ('c: 5 -> 0.1', '*')
