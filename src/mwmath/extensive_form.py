import sympy as sp
import random
import copy
from typing import Callable, Optional, Generator
from dataclasses import dataclass

from icecream import ic  # type: ignore

from util.debug import checkup, debug

ic.disable()


@dataclass(unsafe_hash=True)
class GameMove:
    pass


@dataclass
class GameOutcome:
    payoffs: tuple[sp.Rational, ...]
    """ the player scores at the end of the game """
    moves: Optional[tuple[GameMove, ...]]
    """ the moves leading to those scores """

    def __repr__(self) -> str:
        return f"Payoffs: {self.payoffs}\nMoves: {self.moves}"


class GameState:
    """As written, this assumes that players earn a score with the highest score winning the game."""

    # ABSTRACT METHODS

    @property
    def game_over(self) -> bool:
        # subclasses need to override this to return True when game is over
        raise NotImplementedError

    def compute_outcome(self) -> GameOutcome:
        # subclasses need to override this to return the payoffs and moves when the game is over
        raise NotImplementedError

    @property
    def branch_states(self) -> Generator:
        # subclasses need to override this to yeild the possible game states to which this state can transition
        raise NotImplementedError

    # END ABSTRACT METHODS

    def __init__(
        self,
        player: int,
        strategies: tuple[Callable, ...],
        history: Optional[tuple[GameMove, ...]] = None,
    ) -> None:
        """

        :param player: the player to make the next move
        :param strategies: the strategies for each player
        :param history: the sequence of moves leading to this point in the game
        """
        self._player = player
        self._strategies = strategies
        self._history = history if history else ()
        self._stashed_outcome: Optional[GameOutcome] = None

    @checkup
    def __repr__(self) -> str:
        string = f"Player: {self.player} of {self.players}"
        if self._stashed_outcome is not None:
            string += f", {self._stashed_outcome}"
        return string

    def check(self):
        assert self.player < self.players

    @property
    def players(self) -> int:
        return len(self.strategies)

    @property
    def player(self) -> int:
        return self._player

    @player.setter
    @checkup
    def player(self, player: int) -> None:
        assert player < self.players
        self._player = player

    @property
    def strategies(self) -> tuple[Callable, ...]:
        return self._strategies

    @property
    def history(self) -> Optional[tuple[GameMove, ...]]:
        return self._history

    @property
    def outcome(self) -> GameOutcome:
        """
        :return: the outcome of this game using the strategies
        """
        if self._stashed_outcome:
            return self._stashed_outcome
        elif self.game_over:
            self._stashed_outcome = self.compute_outcome()
        else:
            self._stashed_outcome = self.strategies[self.player](self)

        assert self._stashed_outcome is not None
        return self._stashed_outcome

    @staticmethod
    def rational_strategy(rank: Callable) -> Callable:

        def ranked_strategy(state: GameState) -> GameOutcome:
            """

            :return: the outcome resulting from taking the rational max-min strategy
            """
            optimal_outcome = max(
                (branch.outcome for branch in state.branch_states),
                key=lambda o: rank(state.player, o),
            )
            return optimal_outcome

        return ranked_strategy

    @staticmethod
    def bayesian_strategy(weights: Callable) -> Callable:

        def weighted_strategy(state: GameState) -> GameOutcome:
            """

            :param state: this is the state of the game before the move
            :return: the probability that the move would be taken
            """
            expected_payoffs = tuple(sp.Integer(0) for _ in range(state.players))
            for branch in state.branch_states:
                move = branch.history[-1]
                expected_payoffs = tuple(
                    weights(state, move) * branch.outcome.payoffs[p]
                    + expected_payoffs[p]
                    for p in range(state.players)
                )

            if state.history is None:
                new_history: tuple[GameMove, ...] = (GameMove(),)
            else:
                new_history = state.history + (GameMove(),)

            return GameOutcome(expected_payoffs, new_history)

        return weighted_strategy

    @staticmethod
    def monte_carlo_strategy(weights: Callable) -> Callable:
        """
        Decisions are made based on the weights function.

        NOTE: monte carlo is not completely random. Which tiles this strategy takes are random,
        but once the tiles are determined, they are played optimally.

        :param weights: the probability of choosing each move
        :return: the outcome resulting from the monte_carlo strategy
        """

        def weighted_strategy(state: GameState) -> GameOutcome:
            """

            :param state: this is the state of the game before the move
            :return: the probability that the move would be taken
            """
            probability = random.random()
            cummulative_probability = 0
            outcome = None
            for branch in state.branch_states:
                move = branch.history[-1]
                cummulative_probability += weights(state, move)
                if probability <= cummulative_probability:
                    outcome = branch.outcome
                    break
            assert outcome is not None
            return outcome

        return weighted_strategy


@dataclass(unsafe_hash=True)
class TreeMove(GameMove):
    branch: int

    def __init__(self, branch: int) -> None:
        self.branch = branch


def tree_move_from_game_move(game_move: GameMove):
    assert isinstance(game_move, TreeMove)
    return TreeMove(game_move.branch)

class BinTreeState(GameState):

    # todo: as written, this requires a binary tree, should extend to non-binary options
    LEFT = TreeMove(branch=0)
    RIGHT = TreeMove(branch=1)

    def __init__(
        self,
        player,
        strategies,
        payoffs: dict[tuple[TreeMove, ...], tuple[sp.Rational, ...]],
        history=None,
    ):
        super().__init__(player, strategies, history)
        self.payoffs = payoffs

    @property
    def game_over(self) -> bool:
        return self.history in self.payoffs

    def compute_outcome(self) -> GameOutcome:
        assert self.history is not None
        history = tuple(tree_move_from_game_move(move) for move in self.history)
        return GameOutcome(self.payoffs[history], self.history)

    @property
    def branch_states(self):
        for move in (BinTreeState.LEFT, BinTreeState.RIGHT):
            new_player = (self.player + 1) % self.players
            new_strategies = copy.deepcopy(self.strategies)
            new_payoffs = copy.deepcopy(self.payoffs)
            new_history = self.history + (move,)
            new_state = BinTreeState(new_player, new_strategies, new_payoffs, new_history)
            yield new_state

    @staticmethod
    def rank(player: int, outcome: GameOutcome) -> sp.Rational:
        return outcome.payoffs[player]


if __name__ == "__main__":
    pass
