import random

from typing import Callable, Optional


class Bidder:

    DELTA = 10**-4

    def __init__(self, number: int, valuation: float, strategy):
        self._number = number
        self._valuation = valuation
        self._active = True
        self._strategy = strategy

    def __repr__(self) -> str:
        return f"{self.valuation}"

    @property
    def number(self) -> int:
        return self._number

    @property
    def valuation(self):
        return self._valuation

    @property
    def active(self) -> bool:
        return self._active

    def bid(self, current_bid: float) -> float:
        bid = self._strategy(self.valuation, current_bid)
        if bid is None:
            self._active = False
        return bid

Auction = Callable[[list[Bidder]], tuple[float, Bidder, float]]
Strategy = Callable[[float, float], Optional[float]]

def run_english_auction(bidders: list[Bidder]) -> tuple[float, Bidder, float]:
    current_bid = 0.0
    highest_bidder = None
    active_bidders = tuple(bidder for bidder in bidders if bidder.active)
    while active_bidders:
        for bidder in active_bidders:
            bid = bidder.bid(current_bid)
            if bid is not None:
                current_bid = bid
                highest_bidder = bidder
        active_bidders = tuple(
            bidder
            for bidder in bidders
            if bidder.active and bidder is not highest_bidder
        )
    assert highest_bidder is not None
    return current_bid, highest_bidder, current_bid


def english_strategy(valuation: float, current_bid: float) -> Optional[float]:
    if valuation >= current_bid + Bidder.DELTA:
        return current_bid + Bidder.DELTA
    else:
        return None


def run_vickrey_auction(bidders: list[Bidder]) -> tuple[float, Bidder, float]:
    sorted_bidders = sorted(bidders, key=lambda bidder: bidder.valuation, reverse=True)
    highest_bidder = sorted_bidders[0]
    highest_bid = sorted_bidders[1].bid(0.0)
    return highest_bid, highest_bidder, highest_bid


def vickrey_strategy(valuation: float, _: float) -> Optional[float]:
    return valuation


def run_blind_auction(bidders: list[Bidder]) -> tuple[float, Bidder, float]:
    sorted_bidders = sorted(bidders, key=lambda bidder: bidder.valuation, reverse=True)
    highest_bidder = sorted_bidders[0]
    highest_bid = sorted_bidders[0].bid(0.0)
    return highest_bid, highest_bidder, highest_bid


def make_blind_strategy(bidder_count: int) -> Strategy:

    def blind_strategy(valuation: float, _: float) -> Optional[float]:
        return (bidder_count - 1) / bidder_count * valuation

    return blind_strategy


def run_dutch_auction(bidders: list[Bidder]) -> tuple[float, Bidder, float]:
    current_bid = 1.0 + Bidder.DELTA
    highest_bidder = None
    while highest_bidder is None:
        current_bid -= Bidder.DELTA
        for bidder in bidders:
            if bidder.bid(current_bid) >= current_bid:
                highest_bidder = bidder
                break
    return current_bid, highest_bidder, current_bid


def make_dutch_strategy(bidder_count: int) -> Strategy:

    def dutch_strategy(valuation: float, _: float) -> Optional[float]:
        return (bidder_count - 1) / bidder_count * valuation

    return dutch_strategy


def run_allpay_auction(bidders: list[Bidder]) -> tuple[float, Bidder, float]:
    sorted_bidders = sorted(bidders, key=lambda bidder: bidder.valuation, reverse=True)
    highest_bidder = sorted_bidders[0]
    highest_bid = sorted_bidders[0].bid(0.0)
    revenue = sum(bidder.bid(0.0) for bidder in sorted_bidders)
    return highest_bid, highest_bidder, revenue


def make_allpay_strategy(bidder_count: int) -> Strategy:

    def allpay_strategy(valuation: float, _: float) -> float:
        return (bidder_count - 1) / bidder_count * (valuation**bidder_count)

    return allpay_strategy


def make_partialpay_auction(partial: float) -> Auction:

    def run_partialpay_auction(bidders: list[Bidder]) -> tuple[float, Bidder, float]:
        sorted_bidders = sorted(
            bidders, key=lambda bidder: bidder.valuation, reverse=True
        )
        highest_bidder = sorted_bidders[0]
        highest_bid = sorted_bidders[0].bid(0.0)
        revenue = (sorted_bidders[0].bid(0.0)
                   + partial * sum(bidder.bid(0.0) for bidder in sorted_bidders[1:]))
        return highest_bid, highest_bidder, revenue

    return run_partialpay_auction


# def run_halfpay_auction(bidders: list[Bidder]) -> tuple[float, Bidder, float]:
#     sorted_bidders = sorted(bidders, key=lambda bidder: bidder.valuation, reverse=True)
#     highest_bidder = sorted_bidders[0]
#     highest_bid = sorted_bidders[0].bid(0.0)
#     revenue = sorted_bidders[0].bid(0.0) + 0.5 * sum(
#         bidder.bid(0.0) for bidder in sorted_bidders[1:]
#     )
#     return highest_bid, highest_bidder, revenue


def make_partialpay_strategy(bidder_count: int, partial: float) -> Strategy:

    def partialpay_strategy(valuation: float, _: float) -> Optional[float]:
        return (
            (bidder_count - 1) / bidder_count * (valuation**bidder_count)
            * 1 / (partial + (1 - partial) * valuation ** (bidder_count - 1))
        )

    return partialpay_strategy


def truncated_gauss(mu: float, sigma: float):
    value = random.gauss(mu, sigma)
    return max(min(value, 1.0), 0.0)


def random_valuation() -> float:
    return random.uniform(0, 1)
    # random.uniform(0, 1)
    # random.triangular(0, 1)
    # random.bivariate(alpha, beta)
    # random.gauss(0.5, 0.01) <- will need to truncate this


def main() -> None:
    bidder_count = 5
    trials = 10_000

    names = ("English", "Vickrey", "Blind", "Dutch", "All-Pay", "Half-Pay", "Double-Pay")
    auctions: tuple[Auction, ...] = (
        run_english_auction,
        run_vickrey_auction,
        run_blind_auction,
        run_dutch_auction,
        run_allpay_auction,
        make_partialpay_auction(0.5),
        make_partialpay_auction(2),
    )
    strategies: tuple[Strategy, ...] = (
        english_strategy,
        vickrey_strategy,
        make_blind_strategy(bidder_count),
        make_dutch_strategy(bidder_count),
        make_allpay_strategy(bidder_count),
        make_partialpay_strategy(bidder_count, 0.5),
        make_partialpay_strategy(bidder_count, 2),
    )
    profits: list[float] = [0.0 for _ in names]
    revenues: list[float] = [0.0 for _ in names]

    for _ in range(trials):
        valuations = tuple(random_valuation() for _ in range(bidder_count))
        assert len(set(valuations)) == len(valuations)

        for n, (run_auction, strategy) in enumerate(zip(auctions, strategies)):
            bidders = [
                Bidder(number, valuations[number], strategy)
                for number in range(bidder_count)
            ]
            highest_bid, highest_bidder, revenue = run_auction(bidders)
            profits[n] += highest_bidder.valuation - highest_bid
            revenues[n] += revenue

    print(f"If Uniformly Distributed Valuations, profit ≈ {1/(bidder_count + 1)}")
    for name, profit in zip(names, profits):
        print(f"{name} Profit {profit/trials}")
    print("")
    print(
        f"If Uniformly Distributed Valuations, revenue ≈ {(bidder_count - 1)/(bidder_count + 1)}"
    )
    for name, revenue in zip(names, revenues):
        print(f"{name} Revenue: {revenue/trials}")


if __name__ == "__main__":
    main()
