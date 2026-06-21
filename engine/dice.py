import random


def roll(expr: str) -> int:
    n, s = map(int, expr.split("d"))

    return sum(
        random.randint(1, s)
        for _ in range(n)
    )