import sympy as sp
import random
import copy
from typing import Callable, Optional, Generator
from dataclasses import dataclass

from icecream import ic  # type: ignore

from util.debug import checkup

ic.disable()


@dataclass(frozen=True)
class GameMove:
    pass

@dataclass
class GameOutcome:
    """ Base class to track game outcomes (the payoffs and the moves) leading to those payoffs. """
    payoffs: tuple[sp.Rational, ...]
    """ the player scores at the end of the game """
    moves: Optional[tuple[GameMove, ...]]
    """ the moves leading to those scores """

    def __repr__(self) -> str:
        return f"Payoffs: {self.payoffs}\nMoves: {self.moves}"


class GameState:
    """ Abstract class representing the state of a game. """

    # region dunder methods

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
        self._stashed_hash: Optional[int] = None

    @checkup
    def __repr__(self) -> str:
        string = f"Player: {self.player} of {self.players}"
        if self._stashed_outcome is not None:
            string += f", {self._stashed_outcome}"
        return string

    def __hash__(self):
        raise NotImplementedError

    @checkup
    def hash(self) -> int:
        return hash((self._player, self._strategies, self._history))

    # endregion

    # region debugging

    def check(self):
        assert self.player < self.players

    # endregion

    # region properties

    @property
    def players(self) -> int:
        """ the number of players in the game """
        return len(self.strategies)

    @property
    def player(self) -> int:
        """ the current player in the game """
        return self._player

    @player.setter
    @checkup
    def player(self, player: int) -> None:
        """ the current player in the game is mutable """
        assert player < self.players
        self._player = player
        # invalidate the stashed_outcome
        self._stashed_outcome = None

    @property
    def strategies(self) -> tuple[Callable, ...]:
        """ the strategies for each player in the game """
        return self._strategies

    @property
    def history(self) -> Optional[tuple[GameMove, ...]]:
        """ the history of moves that lead to this state in the game """
        return self._history

    @property
    def outcome(self) -> GameOutcome:
        """
        This assumes that if hash(self) has not changed, then the outcome has not changed.
        To protect against hash collisions, users can call clear_stashed_outcome() before calling outcome()

        :return: the outcome of this game using the strategies
        """
        if self._stashed_outcome and self._stashed_hash == self.hash():
            return self._stashed_outcome
        elif self.game_over:
            self._stashed_outcome = self.compute_outcome()
        else:
            self._stashed_outcome = self.strategies[self.player](self)

        self._stashed_hash = self.hash()
        assert self._stashed_outcome is not None
        return self._stashed_outcome

    def clear_stashed_outcome(self) -> None:
        """ This can be called to clear out the stashed outcome before calling outcome
        to protect against hash collisions. """
        self._stashed_outcome = None

    # end region

    # region Abstract Methods

    @property
    def game_over(self) -> bool:
        """ Subclasses need to override this to return True when game is over

        :return: True if the game is over and False otherwise
        """
        raise NotImplementedError

    def compute_outcome(self) -> GameOutcome:
        """ Subclasses need to override this to return the game outcome when the game is over.

        :return: the GameOutcome that results from playing the state's strategies until the game ends.
        """
        raise NotImplementedError

    @property
    def branch_states(self) -> Generator:
        """ Subclasses need to override this to yeild the possible game states to which this state can transition.

        :return: the next possible game state to which this game state can transition
        """
        raise NotImplementedError

    # endregion

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


@dataclass(frozen=True)
class TreeMove(GameMove):
    branch: int

def tree_move_from_game_move(game_move: GameMove):
    """

    :param game_move: a generic GameMove
    :raise AssertionError: if game_move is not a TreeMove
    :return: returns a TreeMove object if game_move is a TreeMove
    """
    assert isinstance(game_move, TreeMove)
    return TreeMove(game_move.branch)

class BinTreeState(GameState):

    LEFT = TreeMove(branch=0)
    """ Left branch in a binary tree """
    RIGHT = TreeMove(branch=1)
    """ Right branch in a binary tree """

    def __init__(
        self,
        player,
        strategies,
        payoffs: dict[tuple[TreeMove, ...], tuple[sp.Rational, ...]],
        history=None,
    ):
        """

        :param player: the player number
        :param strategies: the strategies being used
        :param payoffs: the payoffs for each final state of the game
        :param history: the history of the game up to this state
        """
        super().__init__(player, strategies, history)
        self.payoffs = payoffs

    @property
    def game_over(self) -> bool:
        """
        A Binary Tree Game ends when it reaches an state with payoffs
        :return:
        """
        return self.history in self.payoffs

    def compute_outcome(self) -> GameOutcome:
        """

        :return: the payout determined by the previous moves and the state's payoffs
        """
        assert self.history is not None
        history = tuple(tree_move_from_game_move(move) for move in self.history)
        return GameOutcome(self.payoffs[history], self.history)

    @property
    def branch_states(self):
        """

        :return: the next state (from either choosing the LEFT or RIGHT branch
        """
        for move in (BinTreeState.LEFT, BinTreeState.RIGHT):
            new_player = (self.player + 1) % self.players
            new_strategies = copy.deepcopy(self.strategies)
            new_payoffs = copy.deepcopy(self.payoffs)
            new_history = self.history + (move,)
            new_state = BinTreeState(new_player, new_strategies, new_payoffs, new_history)
            yield new_state

    @staticmethod
    def rank(player: int, outcome: GameOutcome) -> sp.Rational:
        """

        :param player: the player to whom the payoff is being made
        :param outcome: the outcome to score
        :return: for Binary Tree Games, this is the appropriate value in the payoffs
        """
        return outcome.payoffs[player]


if __name__ == "__main__":
    pass
