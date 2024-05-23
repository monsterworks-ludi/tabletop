import abc
import random


def uniform_distribution() -> float:
    """
    :return: a random number between 0 and 1 with uniform distribution.
    """
    return random.uniform(0, 1)


def triangular_distribution() -> float:
    """

    :return: a random number between 0 and 1 with triangular distribution.
    """
    return random.triangular()


def gaussian_distribution() -> float:
    """
    Mean is 0.5 and sigma is 0.1.
    Values outside the range [0,1] are clipped to 0 and 1.
    The probability that a value is clipped is roughly 5.7e-7

    :return: a random number between 0 and 1 with a clipped Gaussian distribution.
    """
    value = random.gauss(0.5, 0.1)
    return max(min(value, 1.0), 0.0)


def min_gap(valuations: tuple[float, ...]) -> float:
    """
    Determines the smallest distance between any two values in the valuations

    :param valuations: a list of floats
    :return: the smallest distance between any two values in the list
    """
    return min((abs(valuations[i] - valuations[j]) for i in range(len(valuations)) for j in range(i)))


def random_valuations(bidder_count, distribution=uniform_distribution, epsilon=1e-3) -> tuple[float, ...]:
    """

    :param bidder_count: number of valuations to compute
    :param distribution: the random distribution from which the valuations are taken
    :param epsilon: the minimum distance between any two values in the valuations
    :return: a list of random numbers from 0 to 1, each pair of which is no closer than epsilon
    """
    valuations = tuple(distribution() for _ in range(bidder_count))
    gap = min_gap(valuations)
    while gap <= epsilon:
        valuations = tuple(distribution() for _ in range(bidder_count))
        gap = min_gap(valuations)

    return valuations


class Bidder(metaclass=abc.ABCMeta):

    def __init__(self, index, valuation):
        self._valuation = valuation
        self._index = index

    def __repr__(self) -> str:
        return f"{self.index}: {self.valuation}"

    @property
    def index(self) -> int:
        return self._index

    @property
    def valuation(self) -> float:
        return self._valuation

    @property
    @abc.abstractmethod
    def max_bid(self) -> float:
        return 0


class ShadedBidder(Bidder):
    def __init__(self, index, valuation, shading):
        super().__init__(index, valuation)
        self._shading = shading

    @property
    def shading(self) -> float:
        return self._shading

    @property
    def max_bid(self) -> float:
        return self._shading * self._valuation


class EnglishBidder(ShadedBidder):

    def __init__(self, index: int, valuation: float) -> None:
        super().__init__(index, valuation, 1)


def run_english_auction(bidders: list[Bidder], min_bid_increment=1e-3) -> tuple[float, Bidder]:
    # should I handle the case where no one bids here?
    current_bid = 0.0
    active_bidders = tuple(bidder for bidder in bidders if bidder.max_bid >= current_bid)
    while len(active_bidders) > 1:
        current_bid += min_bid_increment
        active_bidders = tuple(
            bidder
            for bidder in bidders
            if bidder.max_bid >= current_bid
        )
    assert len(active_bidders) == 1, "Tied Bidders"
    return current_bid, active_bidders[0]


def run_vickrey_auction(bidders: list[Bidder]) -> tuple[float, Bidder]:
    sorted_bidders = sorted(bidders, key=lambda bidder: bidder.max_bid, reverse=True)
    highest_bidder = sorted_bidders[0]
    second_bid = sorted_bidders[1].max_bid

    return second_bid, highest_bidder


class BlindBidder(ShadedBidder):
    def __init__(self, index: int, valuation: float, bidder_count: int):
        super().__init__(index, valuation, (bidder_count - 1) / bidder_count)


def run_blind_auction(bidders: list[Bidder]) -> tuple[float, Bidder]:
    sorted_bidders = sorted(bidders, key=lambda bidder: bidder.max_bid, reverse=True)
    highest_bidder = sorted_bidders[0]
    highest_bid = highest_bidder.max_bid

    return highest_bid, highest_bidder


def run_dutch_auction(bidders: list[Bidder], min_bid_increment=1e-3, current_bid=1.0) -> tuple[float, Bidder]:
    while current_bid >= 0:
        for bidder in bidders:
            if bidder.max_bid > current_bid:
                return current_bid, bidder
        current_bid -= min_bid_increment
    assert False


class ShadedPowerBidder(Bidder):
    def __init__(self, index, valuation, shading, power):
        super().__init__(index, valuation)
        self._shading = shading
        self._power = power

    @property
    def shading(self):
        return self._shading

    @property
    def power(self):
        return self._power

    @property
    def max_bid(self) -> float:
        return self._shading * (self.valuation ** self._power)


class PartialPayBidder(Bidder):
    def __init__(self, index: int, valuation: float, bidder_count: int, loser_penalty):
        super().__init__(index, valuation)
        self._bidder_count = bidder_count
        self._loser_penalty = loser_penalty

    @property
    def bidder_count(self):
        return self._bidder_count

    @property
    def loser_penalty(self):
        return self._loser_penalty

    @property
    def max_bid(self):
        return (
                (self.bidder_count - 1) / self.bidder_count * self.valuation ** self.bidder_count
                * 1 / (self.loser_penalty + (1 - self.loser_penalty) * self.valuation ** (self.bidder_count - 1))
        )

if __name__ == "__main__":
    pass
