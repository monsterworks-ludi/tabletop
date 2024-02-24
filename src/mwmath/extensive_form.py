import sympy as sp
import random
from typing import Callable, Optional, Generator
from dataclasses import dataclass

from icecream import ic  # type: ignore

from util.debug import checkup

ic.disable()


@dataclass
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
        self._player = player

    @property
    def strategies(self) -> tuple[Callable, ...]:
        return self._strategies

    @property
    def history(self) -> Optional[tuple[GameMove, ...]]:
        return self._history

    @checkup
    def __repr__(self) -> str:
        string = f"Player: {self.player}"
        if self._stashed_outcome is not None:
            string += f", Scores: {self._stashed_outcome.payoffs}, Moves: {self._stashed_outcome.moves}"
        return string

    @property
    def outcome(self) -> GameOutcome:
        """

        :return: the current outcome resulting from the strategies in the game
        """
        return self._stashed_outcome if self._stashed_outcome else self.compute_outcome()

    @property
    def game_over(self) -> bool:
        raise NotImplementedError

    def game_outcome(self) -> GameOutcome:
        raise NotImplementedError

    @checkup
    def compute_outcome(self) -> GameOutcome:
        """

        :return: the outcome resulting from the strategies in the game
        """
        if self.game_over:
            result = self.game_outcome()
            self._stashed_outcome = result
        else:
            self._stashed_outcome = self.strategies[self.player](self)
        assert self._stashed_outcome is not None
        return self._stashed_outcome

    @property
    def branch_states(self) -> Generator:
        # Should generate GameStates
        raise NotImplementedError

    @checkup
    def rank(self, _: GameOutcome) -> sp.Rational:
        raise NotImplementedError

    @checkup
    def rational_strategy(self) -> GameOutcome:
        """

        :return: the outcome resulting from taking the rational max-min strategy
        """
        optimal_outcome = max(
            (branch.outcome for branch in self.branch_states),
            key=lambda o: self.rank(o),
        )
        return optimal_outcome

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

            return outcome

        return weighted_strategy


if __name__ == "__main__":
    pass
