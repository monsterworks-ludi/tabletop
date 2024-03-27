import random  # type: ignore


class RaBidder:
    def __init__(self, valuation: float, shading: float, bidding_tiles: list[int]):
        self.valuation = valuation
        self.shading = shading
        self.bidding_tiles = bidding_tiles
        self.bidding_tiles.sort()

    def make_continuous_bid(self, current_bid: float, min_bid_increment: float):
        shaded_bid = self.valuation * self.shading

        if self.valuation < current_bid + min_bid_increment:
            return 0
        elif shaded_bid < current_bid + min_bid_increment <= self.valuation:
            return current_bid + min_bid_increment
        else:
            assert current_bid <= shaded_bid
            return shaded_bid

    def make_tile_bid(self, current_bid: float, min_bid_increment: float):
        continuous_bid = self.make_continuous_bid(current_bid, min_bid_increment)

        prev_tile = 0
        for bidding_tile in self.bidding_tiles:
            if self.valuation < bidding_tile:
                break
            else:
                prev_tile = bidding_tile
        return prev_tile


class RoseBidder(RaBidder):
    def __init__(self, valuation: float):
        super().__init__(valuation, 2 / 3, [5, 11])

class ColinBidder(RaBidder):
    def __init__(self, valuation: float):
        super().__init__(valuation, 1 / 2, [4, 9, 12])


class LarryBidder(RaBidder):
    def __init__(self, valuation: float):
        super().__init__(valuation, 0, [6, 13])


def run_continuous_auction(
    valuations: list[float],
    shadings: list[float],
    tiles: list[list[int]],
    min_bid_increment=10**-3,
):

    first_bidder = RaBidder(valuations[0], shadings[0], tiles[0])
    second_bidder = RaBidder(valuations[1], shadings[1], tiles[1])
    third_bidder = RaBidder(valuations[2], shadings[2], tiles[2])

    first_bid = first_bidder.make_continuous_bid(0, min_bid_increment)
    second_bid = second_bidder.make_continuous_bid(first_bid, min_bid_increment)
    third_bid = third_bidder.make_continuous_bid(
        max(first_bid, second_bid), min_bid_increment
    )

    winner = None
    revenue = max(first_bid, second_bid, third_bid)
    profit = 0
    if first_bid == revenue:
        winner = 1
        profit = first_bidder.valuation - first_bid
    elif second_bid == revenue:
        winner = 2
        profit = second_bidder.valuation - second_bid
    elif third_bid == revenue:
        winner = 3
        profit = third_bidder.valuation - third_bid

    assert profit >= 0
    assert winner is not None

    return winner, revenue, profit


def run_tile_auction(
    valuations: list[float],
    shadings: list[float],
    tiles: list[list[int]],
    min_bid_increment=10**-3,
):

    first_bidder = RaBidder(valuations[0], shadings[0], tiles[0])
    second_bidder = RaBidder(valuations[1], shadings[1], tiles[1])
    third_bidder = RaBidder(valuations[2], shadings[2], tiles[2])

    first_bid = first_bidder.make_tile_bid(0, min_bid_increment)
    second_bid = second_bidder.make_tile_bid(first_bid, min_bid_increment)
    third_bid = third_bidder.make_tile_bid(
        max(first_bid, second_bid), min_bid_increment
    )

    winner = None
    revenue = max(first_bid, second_bid, third_bid)
    profit = 0
    if first_bid == revenue:
        winner = 1
        profit = first_bidder.valuation - first_bid
    elif second_bid == revenue:
        winner = 2
        profit = second_bidder.valuation - second_bid
    elif third_bid == revenue:
        winner = 3
        profit = third_bidder.valuation - third_bid

    assert winner is not None
    assert profit >= 0
    return winner, revenue, profit


def run_continuous_auctions(total, shadings, tiles, min_bid_increment=10**-3):
    total_revenue = 0
    bidder_profits = [0, 0, 0, 0]
    bidder_wins = [0, 0, 0, 0]
    for _ in range(total):
        winner, revenue, profit = run_continuous_auction(
            [random.uniform(0, 14), random.uniform(0, 14), random.uniform(0, 14)],
            shadings,
            tiles,
            min_bid_increment,
        )
        assert winner > 0
        assert profit >= 0
        total_revenue += revenue
        bidder_wins[winner] += 1
        bidder_profits[winner] += profit

    print(f"Average Revenue {total_revenue/total}")
    for i, (bidder_win, bidder_profit) in enumerate(zip(bidder_wins, bidder_profits)):
        print(
            f"Bidder {i} won {bidder_win/total} percentage of auctions with average profits {bidder_profit/total}"
        )


def run_tile_auctions(total, shadings, tiles, min_bid_increment=10**-3):
    total_revenue = 0
    bidder_profits = [0, 0, 0, 0]
    bidder_wins = [0, 0, 0, 0]
    for _ in range(total):
        winner, revenue, profit = run_tile_auction(
            [random.uniform(0, 14), random.uniform(0, 14), random.uniform(0, 14)],
            shadings,
            tiles,
            min_bid_increment,
        )
        assert winner > 0
        assert profit >= 0
        total_revenue += revenue
        bidder_wins[winner] += 1
        bidder_profits[winner] += profit

    print(f"Average Revenue {total_revenue/total}")
    for i, (bidder_win, bidder_profit) in enumerate(zip(bidder_wins, bidder_profits)):
        print(
            f"Bidder {i} won {bidder_win/total} percentage of auctions with average profits {bidder_profit/total}"
        )


def run_crafted_auction(valuations: list[float]):

    first_bid = 0.0
    if valuations[0] >= 5:
        first_bid = 5.0

    current_bid = first_bid

    second_bid = 0.0
    if current_bid == 0 and valuations[1] >= 4:
        second_bid = 4.0
    elif current_bid == 5 and valuations[1] >= 9:
        second_bid = 9.0

    current_bid = max(first_bid, second_bid)  # could be 0, 4, 5, 9

    third_bid = 0.0
    if current_bid < 6 <= valuations[2]:
        third_bid = 6.0
    elif current_bid < 13 <= valuations[2]:
        third_bid = 13.0

    winner = None
    revenue = max(first_bid, second_bid, third_bid)
    profit = 0.0
    if first_bid == revenue:
        winner = 1
        profit = valuations[0] - first_bid
    elif second_bid == revenue:
        winner = 2
        profit = valuations[1] - second_bid
    elif third_bid == revenue:
        winner = 3
        profit = valuations[2] - third_bid

    assert winner is not None
    assert profit >= 0
    return winner, revenue, profit


def run_crafted_auctions(total):
    total_revenue = 0
    bidder_profits = [0, 0, 0, 0]
    bidder_wins = [0, 0, 0, 0]
    for _ in range(total):
        winner, revenue, profit = run_crafted_auction(
            [random.uniform(0, 14), random.uniform(0, 14), random.uniform(0, 14)]
        )
        assert winner > 0
        assert profit >= 0
        total_revenue += revenue
        bidder_wins[winner] += 1
        bidder_profits[winner] += profit

    print(f"Average Revenue {total_revenue/total}")
    for i, (bidder_win, bidder_profit) in enumerate(zip(bidder_wins, bidder_profits)):
        print(
            f"Bidder {i} won {bidder_win/total} percentage of auctions with average profits {bidder_profit/total}"
        )

def expected_value(current_bid, remaining_bidders):
    pass

if __name__ == "__main__":

    random.seed(1)
    run_continuous_auctions(
        100_000,
        [2 / 3, 1 / 2, 0],
        [[5, 11], [4, 9, 12], [6, 13]],
    )

    random.seed(1)
    run_tile_auctions(
        100_000, [2/3, 1/2, 0], [[5, 11], [4, 9, 12], [6, 13]]
    )

    random.seed(1)
    run_crafted_auctions(100_00)
