import sympy as sp
import copy

from pytest_check import check  # type: ignore

from mwmath.extensive_form import BinTreeState


def chicken_payoffs():
    return copy.deepcopy(
        {
            (BinTreeState.LEFT, BinTreeState.LEFT): (sp.Integer(1), sp.Integer(1)),
            (BinTreeState.LEFT, BinTreeState.RIGHT): (sp.Integer(4), sp.Integer(2)),
            (BinTreeState.RIGHT, BinTreeState.LEFT): (sp.Integer(2), sp.Integer(4)),
            (BinTreeState.RIGHT, BinTreeState.RIGHT): (sp.Integer(3), sp.Integer(3)),
        }
    )


def prisoner_payoffs():
    return copy.deepcopy(
        {
            (BinTreeState.LEFT, BinTreeState.LEFT): (sp.Integer(2), sp.Integer(2)),
            (BinTreeState.LEFT, BinTreeState.RIGHT): (sp.Integer(4), sp.Integer(1)),
            (BinTreeState.RIGHT, BinTreeState.LEFT): (sp.Integer(1), sp.Integer(4)),
            (BinTreeState.RIGHT, BinTreeState.RIGHT): (sp.Integer(3), sp.Integer(3)),
        }
    )


def test_chicken_naive():
    strategies = (
        BinTreeState.rational_strategy(BinTreeState.rank),
        BinTreeState.rational_strategy(BinTreeState.rank),
    )
    payoffs = chicken_payoffs()
    state = BinTreeState(0, strategies, payoffs)
    with check:
        # Figure 6.20, p. 136
        assert state.outcome.moves == (BinTreeState.LEFT, BinTreeState.RIGHT)
    with check:
        # Figure 6.20, p. 136
        assert state.outcome.payoffs == (4, 2)


def test_chicken_threat():
    strategies = (
        BinTreeState.rational_strategy(BinTreeState.rank),
        BinTreeState.rational_strategy(BinTreeState.rank),
    )
    payoffs = chicken_payoffs()
    # make (Left, Left) look better than anything else
    payoffs[(BinTreeState.LEFT, BinTreeState.LEFT)] = (sp.Integer(1), sp.Integer(5))
    state = BinTreeState(0, strategies, payoffs)
    with check:
        # Figure 6.21, p. 136
        assert state.outcome.moves == (BinTreeState.RIGHT, BinTreeState.LEFT)
    with check:
        # Figure 6.21, p. 136
        assert state.outcome.payoffs == (2, 4)


def test_chicken_promise():
    strategies = (
        BinTreeState.rational_strategy(BinTreeState.rank),
        BinTreeState.rational_strategy(BinTreeState.rank),
    )
    payoffs = chicken_payoffs()
    # make (Right, Right) look better than anything else
    payoffs[(BinTreeState.RIGHT, BinTreeState.RIGHT)] = (sp.Integer(3), sp.Integer(5))
    print(payoffs)
    state = BinTreeState(0, strategies, payoffs)
    with check:
        # Figure 6.21, p. 136
        assert state.outcome.moves == (BinTreeState.LEFT, BinTreeState.RIGHT)
    with check:
        # Figure 6.21, p. 136
        assert state.outcome.payoffs == (4, 2)


def test_prisoner_naive():
    strategies = (
        BinTreeState.rational_strategy(BinTreeState.rank),
        BinTreeState.rational_strategy(BinTreeState.rank),
    )
    payoffs = prisoner_payoffs()
    state = BinTreeState(0, strategies, payoffs)
    with check:
        # Figure 6.20, p. 136
        assert state.outcome.moves == (BinTreeState.LEFT, BinTreeState.LEFT)
    with check:
        # Figure 6.20, p. 136
        assert state.outcome.payoffs == (2, 2)


def test_prisoner_threat():
    strategies = (
        BinTreeState.rational_strategy(BinTreeState.rank),
        BinTreeState.rational_strategy(BinTreeState.rank),
    )
    payoffs = prisoner_payoffs()
    # make (Right, Right) look better than anything else
    payoffs[(BinTreeState.LEFT, BinTreeState.RIGHT)] = (sp.Integer(4), sp.Integer(5))
    state = BinTreeState(0, strategies, payoffs)
    with check:
        # Figure 6.20, p. 136
        assert state.outcome.moves == (BinTreeState.LEFT, BinTreeState.RIGHT)
    with check:
        # Figure 6.20, p. 136
        assert state.outcome.payoffs == (4, 5)


def test_prisoner_promise():
    strategies = (
        BinTreeState.rational_strategy(BinTreeState.rank),
        BinTreeState.rational_strategy(BinTreeState.rank),
    )
    payoffs = prisoner_payoffs()
    # make (Right, Right) look better than anything else
    payoffs[(BinTreeState.RIGHT, BinTreeState.RIGHT)] = (sp.Integer(3), sp.Integer(5))
    state = BinTreeState(0, strategies, payoffs)
    with check:
        # Figure 6.20, p. 136
        assert state.outcome.moves == (BinTreeState.RIGHT, BinTreeState.RIGHT)
    with check:
        # Figure 6.20, p. 136
        assert state.outcome.payoffs == (3, 5)
