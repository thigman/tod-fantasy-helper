from engine.ui import (
    menu,
    show_heroes,
    show_enemies,
)


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

            round_num += 1
            acted.clear()

        elif choice == 2:

            break