import sympy as sp
import random
from typing import Callable, Optional
from dataclasses import dataclass

from icecream import ic  # type: ignore

from util.debug import checkup

ic.disable()

class GameState:
    """As written, this assumes that players earn a score with the highest score winning the game."""

    @dataclass
    class Outcome:
        payoffs: tuple[sp.Rational, ...]
        """ the player scores at the end of the game """
        moves: tuple[str, ...]
        """ the moves leading to those scores """

    def __init__(
        self,
        player: int,
        players: int,
        strategies: tuple[Callable, ...],
        history: Optional[tuple[str, ...]] = None,
    ) -> None:
        """

        :param players: the number of players
        :param player: the player to make the next move
        :param strategies: the strategies for each player
        :param history: the sequence of moves leading to this point in the game
        """
        self._players = players
        self._player = player
        self._strategies = strategies
        self._history = history if history else ()
        self._stashed_outcome: Optional[GameState.Outcome] = None

    def check(self):
        assert self.player < self.players

    @property
    @checkup
    def players(self) -> int:
        return self._players

    @property
    @checkup
    def player(self) -> int:
        return self._player

    @property
    @checkup
    def strategies(self) -> tuple[Callable, ...]:
        return self._strategies

    @property
    @checkup
    def history(self) -> Optional[tuple[str, ...]]:
        return self._history

    @checkup
    def __repr__(self) -> str:
        string = f"Player: {self.player}"
        if self._stashed_outcome is not None:
            string += f", Scores: {self._stashed_outcome.payoffs}, Moves: {self._stashed_outcome.moves}"
        return string

    @property
    @checkup
    def outcome(self) -> Outcome:
        """

        :return: the current outcome resulting from the strategies in the game
        """
        return self._stashed_outcome if self._stashed_outcome else self.compute_outcome()

    @property
    def game_over(self) -> bool:
        return True

    def score_game(self) -> Outcome:
        return self.Outcome(
            tuple(sp.Integer(0) for _ in range(self.players)), tuple(self.history)
        )

    @checkup
    def compute_outcome(self) -> Outcome:
        """

        :return: the outcome resulting from the strategies in the game
        """
        if self.game_over:
            result = self.score_game()
            self._stashed_outcome = result
        else:
            self._stashed_outcome = self.strategies[self.player](self)
        assert self._stashed_outcome is not None
        return self._stashed_outcome

    @property
    @checkup
    def branch_states(self):
        return iter(())

    @checkup
    def rank(self, _: Outcome) -> sp.Rational:
        return sp.Integer(0)

    @checkup
    def rational_strategy(self) -> Outcome:
        """

        :return: the outcome resulting from taking the rational max-min strategy
        """
        optimal_outcome = max(
            (state.outcome for state in self.branch_states),
            key=lambda outcome: self.rank(outcome.payoffs),
        )
        return optimal_outcome

    def avg_payoff(self, weights):
        accumulation = tuple(sp.Integer(0) for _ in range(self.players))
        for state in self.branch_states:
            accumulation = (
                weights(state)[i] * state.outcome.payoffs[i] + accumulation[i]
                for i in range(self.players)
            )
        return accumulation

    @checkup
    def bayesian_strategy(self, weights: Callable) -> Outcome:
        """
        This computes the expected outcome based on the weights

        NOTE: bayesian is not completely random. Which tiles this strategy takes are random,
        but once the tiles are determined, they are played optimally.

        :param weights: the probability of choosing each move
        :return: the expected outcome resulting from the bayesian strategy
        """
        new_history = self.history + (f"*",)
        average_payoffs = tuple(sp.Integer(0) for _ in range(self.players))
        for state in self.branch_states:
            average_payoffs = tuple(
                weights(state) * state.outcome.payoffs[i] + average_payoffs[i]
                for i in range(self.players)
            )
        return self.Outcome(average_payoffs, new_history)

    @checkup
    def monte_carlo_strategy(self, weights: Callable) -> Outcome:
        """
        Decisions are made based on the weights function.

        NOTE: monte carlo is not completely random. Which tiles this strategy takes are random,
        but once the tiles are determined, they are played optimally.

        :param weights: the probability of choosing each move
        :return: the outcome resulting from the monte_carlo strategy
        """
        probability = random.random()
        cummulative_probability = 0
        outcome = None
        for state in self.branch_states:
            cummulative_probability += weights(state)
            if probability <= cummulative_probability:
                outcome = state.outcome
                break

        assert outcome is not None
        return outcome

if __name__ == "__main__":
    pass
