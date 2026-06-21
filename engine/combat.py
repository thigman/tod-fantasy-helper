from engine.ui import (
    menu,
    show_heroes,
    show_enemies,
)


def run_combat(heroes, enemies):

    acted = set()

    while True:

        print()
        print("=== COMBAT ===")

        choice = menu(
            "Action",
            [
                "Status",
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

            break