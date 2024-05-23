import random  # type: ignore
import itertools
from collections import defaultdict
from typing import Optional

class RaBidder:
    """
    A bidder who uses a shading strategy based on upcoming bidders and a slightly overbids previous bids.
    """
    def __init__(self, index: int, valuation: float, shading: float, bidding_tiles: list[int]):
        self._index = index
        self._valuation = valuation
        self._shading = shading
        self._bidding_tiles = bidding_tiles
        self._bidding_tiles.sort()

    @property
    def index(self) -> int:
        return self._index

    @property
    def valuation(self) -> float:
        return self._valuation

    @property
    def bidding_tiles(self) -> list[int]:
        return self._bidding_tiles

    @property
    def shading(self) -> float:
        return self._shading

    def continuous_bid(self, current_bid: float, min_bid_increment: float) -> float:
        """
        Assumes that the bidder can bid any continuous value and is not restricted to their tiles

        :param current_bid: the current bid
        :param min_bid_increment: required minimum bid increment
        :return: the bid, a bid of 0 indicates no bid
        """

        shaded_bid = self.valuation * self.shading
        next_bid = current_bid + min_bid_increment

        if next_bid <= shaded_bid:
            #  try to win against future bidders with blind auction bid
            return shaded_bid
        elif shaded_bid < next_bid <= self.valuation:
            #  try to win against past bidders with English auction bid
            return next_bid
        else:
            assert self.valuation < next_bid
            #  too expensive, skip bid
            return 0

    def tile_bid(self) -> float:
        """

        :return: the highest bidding tile under the bidder's valuation, a bid of 0 indicates no bid
        """

        prev_tile = 0
        for bidding_tile in self.bidding_tiles:
            if self.valuation < bidding_tile:
                break
            else:
                prev_tile = bidding_tile
        return prev_tile

def run_continuous_ra_auction(bidders, min_bid_increment=1e-3) -> tuple[float, Optional[RaBidder]]:
    first_bid = bidders[0].continuous_bid(0, min_bid_increment)
    second_bid = bidders[1].continuous_bid(first_bid, min_bid_increment)
    third_bid = bidders[2].continuous_bid(
        max(first_bid, second_bid), min_bid_increment
    )

    winning_bidder = None
    winning_bid = max(first_bid, second_bid, third_bid)
    if winning_bid == 0:
        winning_bidder = None
    elif winning_bid == first_bid:
        winning_bidder = bidders[0]
    elif winning_bid == second_bid:
        winning_bidder = bidders[1]
    elif winning_bid == third_bid:
        winning_bidder = bidders[2]

    return winning_bid, winning_bidder


# these are the important checks, as they verify that we want shadings of 2/3 and 1/2

def make_continuous_auction(name, tiles, shadings, min_bid_increment):
    """

    :param name: used to identify which auction is being run
    :param tiles: the tiles of the bidders
    :param shadings: the shading strategies of the bidders
    :param min_bid_increment: the minimum bid increment in the auction
    :return: function which runs an auction
    """
    def auction(valuations: list[float]):
        """ In this auction, RaBidders can choose to bid any bid with increments of min_bid_increment.

        :param valuations: the valuations
        :return: the winning bidder, the winning bid, the profit
        """

        first_bidder = RaBidder(0, valuations[0], shadings[0], tiles[0])
        second_bidder = RaBidder(1, valuations[1], shadings[1], tiles[1])
        third_bidder = RaBidder(2, valuations[2], shadings[2], tiles[2])

        first_bid = first_bidder.continuous_bid(0, min_bid_increment)
        second_bid = second_bidder.continuous_bid(first_bid, min_bid_increment)
        third_bid = third_bidder.continuous_bid(
            max(first_bid, second_bid), min_bid_increment
        )

        winner = 0
        revenue = max(first_bid, second_bid, third_bid)
        profit = 0
        if revenue == 0:
            winner = 0
        elif first_bid == revenue:
            winner = 1
            profit = first_bidder.valuation - first_bid
        elif second_bid == revenue:
            winner = 2
            profit = second_bidder.valuation - second_bid
        elif third_bid == revenue:
            winner = 3
            profit = third_bidder.valuation - third_bid

        assert profit >= 0

        return winner, revenue, profit

    auction.__name__ = name
    return auction


def make_naive_tile_auction(name, tiles):
    def auction(valuations: list[float]):
        """ In this auction, bidders are restricted to bidding based on their tiles.

        However, they do not factor in the tiles of later bidders."""
        first_bidder = RaBidder(valuations[0], tiles[0])
        second_bidder = RaBidder(valuations[1], tiles[1])
        third_bidder = RaBidder(valuations[2], tiles[2])

        first_bid = first_bidder.make_naive_tile_bid()
        second_bid = second_bidder.make_naive_tile_bid()
        third_bid = third_bidder.make_naive_tile_bid()

        winner = 0
        revenue = max(first_bid, second_bid, third_bid)
        profit = 0
        if revenue == 0:
            winner = 0
        elif first_bid == revenue:
            winner = 1
            profit = first_bidder.valuation - first_bid
        elif second_bid == revenue:
            winner = 2
            profit = second_bidder.valuation - second_bid
        elif third_bid == revenue:
            winner = 3
            profit = third_bidder.valuation - third_bid

        assert profit >= 0
        return winner, revenue, profit

    auction.__name__ = name

    return auction

def run_auctions(auction_list, total) -> tuple[dict[str, float], dict[str, dict[int, tuple[int, int]]]]:
    total_revenue = defaultdict(lambda: 0)
    bidder_profits = defaultdict(lambda: [0, 0, 0, 0])
    bidder_wins = defaultdict(lambda: [0, 0, 0, 0])
    for _ in range(total):
        valuation = [random.uniform(0, 14), random.uniform(0, 14), random.uniform(0, 14)]
        for auction in auction_list:
            winner, revenue, profit = auction(valuation)
            assert profit >= 0
            total_revenue[auction.__name__] += revenue
            bidder_wins[auction.__name__][winner] += 1
            bidder_profits[auction.__name__][winner] += profit

    avg_revenue: dict[str, float] = defaultdict(lambda: 0)
    avg_wins_gains: dict[str, dict[int, tuple[int, int]]] = defaultdict(dict)
    for auction in auction_list:
        avg_revenue[auction.__name__] = total_revenue[auction.__name__] / total
        for index, (bidder_win, bidder_gain) in enumerate(
                zip(bidder_wins[auction.__name__], bidder_profits[auction.__name__])):
            avg_wins_gains[auction.__name__][index] = (bidder_win / total, bidder_gain / total)

    return avg_revenue, avg_wins_gains


NOONE = 0
ROSE = 1
COLIN = 2
LARRY = 3

NUM_TO_NAME = {NOONE: "No One", ROSE: "Rose", COLIN: "Colin", LARRY: "Larry"}
def rcl_auction(valuations: list[float]):
    # expect wins to be 4.3%, 17.7%, 33.2%, 44.8%

    val_rose = valuations[0]
    val_colin = valuations[1]
    val_larry = valuations[2]
    winner = NOONE

    # first bidder, Rose, has tiles 5, 11
    rbid0 = 0.0
    rbid5 = 9 / 14 * 6 / 14 * (val_rose - 5)  # Colin must not bid 9 or higher, Larry must not bid 6 or higher
    rbid11 = 12 / 14 * 13 / 14 * (val_rose - 11)  # Colin must not bid 12 or higher, Larry must not bid 13 or higher
    first_bid = 0
    if rbid11 >= max(rbid0, rbid5):
        assert False, "Rose should never bid 11 if valuations between 0 and 14"
        # first_bid = 11
        # winner = ROSE
    elif rbid5 >= max(rbid0, rbid11):
        first_bid = 5
        winner = ROSE

    current_bid = first_bid

    # second bidder, Colin, has tiles 4, 9, 12
    cbid0 = 0.0
    cbid4 = 6 / 14 * (val_colin - 4)  # Larry must not bid 6
    cbid9 = 13 / 14 * (val_colin - 9)  # Larry must not bid 13
    cbid12 = 13 / 14 * (val_colin - 12)  # Larry must not bid 13
    second_bid = 0
    if current_bid == 0:
        if cbid12 >= max(rbid0, cbid4, cbid9):
            assert False, "Colin should never bid 12"
            # second_bid = 12
            # winner = COLIN
        elif cbid9 >= max(rbid0, cbid4):
            second_bid = 9
            winner = COLIN
        elif cbid4 >= rbid0:
            second_bid = 4
            winner = COLIN
    elif current_bid == 5:
        if cbid12 >= max(cbid0, cbid9):
            second_bid = 12
            winner = COLIN
        elif cbid9 >= cbid0:
            second_bid = 9
            winner = COLIN
    elif current_bid == 11:
        if cbid12 >= cbid0:
            second_bid = 11
            winner = COLIN

    current_bid = max(first_bid, second_bid)  # could be 0, 4, 5, 9, 11

    # third bidder, Larry, has tiles 6, 13
    # just bids enough to win if they will have a non-negative gain
    third_bid = 0
    if current_bid < 6 <= val_larry:
        third_bid = 6
        winner = LARRY
    elif current_bid < 13 <= val_larry:
        third_bid = 13
        winner = LARRY

    revenue = max(first_bid, second_bid, third_bid)
    profit = 0.0
    if winner == ROSE:
        profit = valuations[0] - first_bid
    elif winner == COLIN:
        profit = valuations[1] - second_bid
    elif winner == LARRY:
        profit = valuations[2] - third_bid

    assert profit >= 0
    return winner, revenue, profit


def lrc_auction(valuations: list[float]):

    # No one: 4.4%
    # Larry: 28.9%
    # Rose: 28.2%
    # Colin: 38.3%

    val_rose = valuations[0]
    val_colin = valuations[1]
    val_larry = valuations[2]
    winner = NOONE

    # first bidder, Larry, has tiles 6, 13
    lbid0 = 0.0
    lbid6 = 11/14 * 9/14 * (val_larry - 6)  # Rose must not bid 11, Colin must not bid 9
    lbid13 = 14/14 * 14/14 * (val_larry - 13)  # Rose and Colin cannot overbid
    first_bid = 0
    if lbid13 >= max(lbid0, lbid6):
        first_bid = 13
        winner = LARRY
    elif lbid6 >= lbid0:
        first_bid = 6
        winner = LARRY

    current_bid = first_bid

    # second bidder, Rose, has tiles 5, 11
    rbid0 = 0.0
    rbid5 = 9/14 * (val_rose - 5)  # only wins if Colin won't bid 9
    rbid11 = 12/14 * (val_rose - 11)  # only wins if Colin won't bid 12
    second_bid = 0
    if current_bid == 0:
        if rbid11 >= max(rbid0, rbid5):
            second_bid = 11
            winner = ROSE
        elif rbid5 >= rbid0:
            second_bid = 5
            winner = ROSE
    elif current_bid == 6:
        if rbid11 >= rbid0:
            second_bid = 11
            winner = ROSE

    current_bid = max(first_bid, second_bid)  # could be 0, 5, 6, 11, 13

    # third bidder, Colin, has tiles 4, 9, 12
    # bids just enough to win if they will have a non-negative gain
    third_bid = 0
    if current_bid < 4 <= val_colin:
        third_bid = 4
        winner = COLIN
    elif current_bid < 9 <= val_colin:
        third_bid = 9
        winner = COLIN
    elif current_bid < 12 <= val_colin:
        third_bid = 12
        winner = COLIN

    revenue = max(first_bid, second_bid, third_bid)
    profit = 0.0
    if winner == LARRY:
        profit = val_larry - first_bid
    elif winner == ROSE:
        profit = val_rose - second_bid
    elif winner == COLIN:
        profit = val_colin - third_bid

    assert profit >= 0
    return winner, revenue, profit

def clr_auction(valuations: list[float]):

    val_rose = valuations[0]
    val_colin = valuations[1]
    val_larry = valuations[2]
    winner = NOONE

    # first bidder, Colin, has tiles 4, 9, 12
    lbid0 = 0.0
    lbid6 = 11/14 * 9/14 * (val_larry - 6)  # Rose must not bid 11, Colin must not bid 9
    lbid13 = 14/14 * 14/14 * (val_larry - 13)  # Rose and Colin cannot overbid
    first_bid = 0
    if lbid13 >= max(lbid0, lbid6):
        first_bid = 13
        winner = LARRY
    elif lbid6 >= lbid0:
        first_bid = 6
        winner = LARRY

    current_bid = first_bid

    # second bidder, Larry, has tiles 6, 13
    rbid0 = 0.0
    rbid5 = 9/14 * (val_rose - 5)  # only wins if Colin won't bid 9
    rbid11 = 12/14 * (val_rose - 11)  # only wins if Colin won't bid 12
    second_bid = 0
    if current_bid == 0:
        if rbid11 >= max(rbid0, rbid5):
            second_bid = 11
            winner = ROSE
        elif rbid5 >= rbid0:
            second_bid = 5
            winner = ROSE
    elif current_bid == 6:
        if rbid11 >= rbid0:
            second_bid = 11
            winner = ROSE

    current_bid = max(first_bid, second_bid)  # could be 0, 5, 6, 11, 13

    # third bidder, Rose, has tiles 5, 11
    # bids just enough to win if they will have a non-negative gain
    third_bid = 0
    if current_bid < 4 <= val_colin:
        third_bid = 4
        winner = COLIN
    elif current_bid < 9 <= val_colin:
        third_bid = 9
        winner = COLIN
    elif current_bid < 12 <= val_colin:
        third_bid = 12
        winner = COLIN

    revenue = max(first_bid, second_bid, third_bid)
    profit = 0.0
    if winner == LARRY:
        profit = val_larry - first_bid
    elif winner == ROSE:
        profit = val_rose - second_bid
    elif winner == COLIN:
        profit = val_colin - third_bid

    assert profit >= 0
    return winner, revenue, profit



def main():
    auction = make_continuous_auction("continuous auction", [[5, 11], [4, 9, 12], [6, 13]], [2 / 3, 1 / 2, 0], 1e-3)
    avg_revenue, avg_wins_gains = run_auctions([auction], 100_000)
    assert abs(avg_revenue[auction.__name__] - 5.5) < 1e-1
    assert abs(avg_wins_gains[auction.__name__][0][1] - 0.0) < 1e-1
    assert abs(avg_wins_gains[auction.__name__][1][1] - 0.5) < 1e-1
    assert abs(avg_wins_gains[auction.__name__][2][1] - 1.0) < 1e-1
    assert abs(avg_wins_gains[auction.__name__][3][1] - 2.7) < 1e-1


def table_7_1():
    auction_list = []
    for shading1, shading2 in itertools.product(range(1, 6), repeat=2):
        auction_name = f"{shading1}, {shading2}"
        auction_list.append(
            make_continuous_auction(auction_name,
                                    [[5, 11], [4, 9, 12], [6, 13]],
                                    [shading1 / 6, shading2 / 6, 0],
                                    1e-3))
    avg_revenue, avg_wins_gains = run_auctions(auction_list, 100_000)
    for auction in auction_list:
        # [x][1] is bidder x gains
        print(f"{auction.__name__}: {avg_wins_gains[auction.__name__][1][1]}, {avg_wins_gains[auction.__name__][2][1]}")

def clr_auctions():
    auction_list = [rcl_auction, lrc_auction]
    results = run_auctions(auction_list, 100_000)
    for name, result in results[1].items():
        print(f"{name}")
        for bidder, (win, profit) in result.items():
            print(f"\t{NUM_TO_NAME[bidder]}: wins {win}% and profits {profit}")


if __name__ == "__main__":
    pass
    # main()
    # table_7_1()
    # clr_auctions()
