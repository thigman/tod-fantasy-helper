from encounters.builder import build_encounter
from engine.combat import run_combat

from models.hero import Hero
from models.weapon import Weapon


def main():

    fightersword = Weapon(
        "LSWD",
        "1d8",
        2,
    )

    heroes = [
        Hero(
            "Fighter",
            25,
            25,
            4,
            7,
            5,
            7,
            1,
            2,
            fightersword,
        )
    ]

    enemies = build_encounter()

    run_combat(
        heroes,
        enemies,
    )


if __name__ == "__main__":
    main()