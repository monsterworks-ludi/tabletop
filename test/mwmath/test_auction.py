from pytest import mark
from pytest_check import check

from mwmath.monte_carlo import set_seed, bad_seed_message

from mwmath.auction import (
    random_valuations, uniform_distribution,
    EnglishBidder, BlindBidder, PartialPayBidder,
    run_english_auction, run_vickrey_auction, run_blind_auction, run_dutch_auction,
)


@mark.parametrize("bidder_count, trials", [(bidders, 100_000) for bidders in range(3, 7)])
def test_english_vickrey_equivalence(bidder_count: int, trials: int) -> None:
    seed = set_seed()
    tolerance = 1e-3

    english_profits = [0.0 for _ in range(bidder_count)]
    english_revenue = 0.0
    vickrey_profits = [0.0 for _ in range(bidder_count)]
    vickrey_revenue = 0.0

    for _ in range(trials):
        valuations = random_valuations(bidder_count, uniform_distribution, tolerance)

        bidders = [EnglishBidder(index, valuation) for index, valuation in enumerate(valuations)]

        english_winning_bid, english_winning_bidder = run_english_auction(bidders, tolerance)
        english_revenue += english_winning_bid / trials
        english_profits[english_winning_bidder.index] += (
                (english_winning_bidder.valuation - english_winning_bid) / trials)

        vickrey_winning_bid, vickrey_winning_bidder = run_vickrey_auction(bidders)
        vickrey_revenue += vickrey_winning_bid / trials
        vickrey_profits[vickrey_winning_bidder.index] += (
                (vickrey_winning_bidder.valuation - vickrey_winning_bid) / trials)

    with check:
        assert abs(english_revenue - vickrey_revenue) < tolerance, bad_seed_message(seed, trials)
    for index in range(bidder_count):
        with check:
            assert abs(english_profits[index] - vickrey_profits[index]) < tolerance, bad_seed_message(seed, trials)


@mark.parametrize("bidder_count, trials", [(bidders, 100_000) for bidders in range(3, 7)])
def test_blind_dutch_equivalence(bidder_count: int, trials: int) -> None:
    seed = set_seed()
    tolerance = 1e-3
    blind_profits = [0.0 for _ in range(bidder_count)]
    blind_revenue = 0.0
    dutch_profits = [0.0 for _ in range(bidder_count)]
    dutch_revenue = 0.0

    for _ in range(trials):
        valuations = random_valuations(bidder_count, uniform_distribution, tolerance)

        bidders = [BlindBidder(index, valuation, bidder_count) for index, valuation in enumerate(valuations)]

        blind_winning_bid, blind_winning_bidder = run_blind_auction(bidders)
        blind_revenue += blind_winning_bid / trials
        blind_profits[blind_winning_bidder.index] += (blind_winning_bidder.valuation - blind_winning_bid) / trials

        dutch_winning_bid, dutch_winning_bidder = run_dutch_auction(bidders, tolerance)
        dutch_revenue += dutch_winning_bid / trials
        dutch_profits[dutch_winning_bidder.index] += (dutch_winning_bidder.valuation - dutch_winning_bid) / trials

    with check:
        assert abs(blind_revenue - dutch_revenue) < tolerance, bad_seed_message(seed, trials)
    for index in range(bidder_count):
        with check:
            assert abs(blind_profits[index] - dutch_profits[index]) < tolerance, bad_seed_message(seed, trials)

@mark.parametrize("bidder_count, trials", [(bidders, 100_000) for bidders in range(3, 7)])
def test_revenue_equivalence(bidder_count: int, trials: int) -> None:
    seed = set_seed()
    tolerance = 1e-2
    epsilon = tolerance

    english_revenue = 0.0
    vickrey_revenue = 0.0
    blind_revenue = 0.0
    dutch_revenue = 0.0
    allpay_revenue = 0.0
    halfpay_revenue = 0.0
    doublepay_revenue = 0.0

    for _ in range(trials):
        valuations = random_valuations(bidder_count, uniform_distribution, epsilon)
        bidders = [EnglishBidder(index, valuation) for index, valuation in enumerate(valuations)]

        english_winning_bid, _ = run_english_auction(bidders, tolerance)
        english_revenue += english_winning_bid / trials

        vickrey_winning_bid, _ = run_vickrey_auction(bidders)
        vickrey_revenue += vickrey_winning_bid / trials

        bidders = [BlindBidder(index, valuation, bidder_count) for index, valuation in enumerate(valuations)]

        blind_winning_bid, _ = run_blind_auction(bidders)
        blind_revenue += blind_winning_bid / trials

        dutch_winning_bid, _ = run_dutch_auction(bidders, tolerance)
        dutch_revenue += dutch_winning_bid / trials

        loser_penalty = 1.0
        bidders = [PartialPayBidder(index, valuation, bidder_count, loser_penalty)
                   for index, valuation in enumerate(valuations)]
        winning_bid, winning_bidder = run_blind_auction(bidders)
        allpay_revenue += winning_bid / trials
        for bidder in (bidder for bidder in bidders if bidder is not winning_bidder):
            allpay_revenue += loser_penalty * bidder.max_bid / trials

        loser_penalty = 0.5
        bidders = [PartialPayBidder(index, valuation, bidder_count, loser_penalty)
                   for index, valuation in enumerate(valuations)]
        winning_bid, winning_bidder = run_blind_auction(bidders)
        halfpay_revenue += winning_bid / trials
        for bidder in (bidder for bidder in bidders if bidder is not winning_bidder):
            halfpay_revenue += loser_penalty * bidder.max_bid / trials

        loser_penalty = 2.0
        bidders = [PartialPayBidder(index, valuation, bidder_count, loser_penalty) for index, valuation in
                   enumerate(valuations)]
        winning_bid, winning_bidder = run_blind_auction(bidders)
        doublepay_revenue += winning_bid / trials
        for bidder in (bidder for bidder in bidders if bidder is not winning_bidder):
            doublepay_revenue += loser_penalty * bidder.max_bid / trials

    expected_revenue = (bidder_count - 1) / (bidder_count + 1)

    with check():
        assert abs(english_revenue - expected_revenue) < tolerance, bad_seed_message(seed, trials)
    with check():
        assert abs(vickrey_revenue - expected_revenue) < tolerance, bad_seed_message(seed, trials)
    with check():
        assert abs(blind_revenue - expected_revenue) < tolerance, bad_seed_message(seed, trials)
    with check():
        assert abs(dutch_revenue - expected_revenue) < tolerance, bad_seed_message(seed, trials)
    with check():
        assert abs(allpay_revenue - expected_revenue) < tolerance, bad_seed_message(seed, trials)
    with check():
        assert abs(halfpay_revenue - expected_revenue) < tolerance, bad_seed_message(seed, trials)
    with check():
        assert abs(doublepay_revenue - expected_revenue) < tolerance, bad_seed_message(seed, trials)
