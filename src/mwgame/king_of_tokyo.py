import random as rnd

def roll() -> int:
    """

    :return: rolls a king of tokyo die, 0 represents a symbol
    """
    result = rnd.randrange(1, 7)
    return result if result <= 3 else 0


def compute_score(rolls: list[int]) -> int:
    """

    :param rolls: a list of dice values from King of Tokyo with 0 representing a symbol
    :return: the score for that combination of rolls
    """
    result = 0
    for number in range(1, 4):
        count = len([value for value in rolls if value == number])
        if count >= 3:
            result += number + (count - 3)
    return result

if __name__ == "__main__":
    ...
