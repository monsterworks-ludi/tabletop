import random

def roll():
    result = random.randrange(1, 7)
    return result if result <= 3 else 0


def score(rolls):
    score = 0
    for number in range(1, 4):
        count = len([value for value in rolls if value == number])
        if count >= 3:
            score += number + (count - 3)
    return score

if __name__ == "__main__":
    ...