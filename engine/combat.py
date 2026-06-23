from engine.ui import (
    menu,
    show_heroes,
    show_enemies,
)

from models.enums import RangeBand


def set_enemy_range(enemies):

    if not enemies:
        print("No enemies.")
        return

    enemy_index = menu(
        "Choose Enemy",
        [e.name for e in enemies],
    )

    range_index = menu(
        "Range",
        [
            "MEL - In Melee",
            "OOM - Out of Melee",
            "OOB - Out of Battle",
        ],
    )

    enemies[enemy_index].rng = list(RangeBand)[range_index]


def run_combat(heroes, enemies):

    acted = set()
    round_num = 1

    while True:

        print()
        print(f"=== COMBAT ROUND {round_num} ===")

        choice = menu(
            "Action",
            [
                "Status",
                "Set Enemy Range",
                "Next Round",
                "Quit",
            ],
        )

        if choice == 0:

            print()
            print("HEROES")

            show_heroes(
                heroes,
                acted,
            )

            print()
            print("ENEMIES")

            show_enemies(
                enemies,
            )

        elif choice == 1:

            set_enemy_range(
                enemies,
            )

        elif choice == 2:

            round_num += 1
            acted.clear()

        elif choice == 3:

            break