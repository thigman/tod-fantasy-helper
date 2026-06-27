from models.hero import Hero
from models.weapon import Weapon

from encounters.builder import build_encounter
from engine.combat import run_combat


def main():

    fighter_sword = Weapon(
        "LSWD",
        "1d8",
        2,
    )

    heroes = [
        Hero(
            name="Fighter",
            hp=25,
            max_hp=25,
            arm=4,
            str_=7,
            dex=5,
            ms=7,
            rs=1,
            spd=6,
            intel=2,
            weapon=fighter_sword,
            secondary_weapon=Weapon(
                "BOW",
                "1d6",
                1,
            ),
        ),
        Hero(
            name="Wizard",
            hp=12,
            max_hp=12,
            arm=1,
            str_=2,
            dex=4,
            ms=2,
            rs=2,
            spd=6,
            intel=8,
            weapon=Weapon(
                "MM",
                "1d8",
                2,
            ),
            secondary_weapon=Weapon(
                "DAG",
                "1d4",
                0,
            ),
        ),
    ]

    enemies = build_encounter()

    run_combat(
        heroes,
        enemies,
    )


if __name__ == "__main__":
    main()