from encounters.builder import build_encounter
from engine.ui import menu


def main():

    menu(
        "Test Menu",
        [
            "Continue"
        ]
    )

    enemies = build_encounter()

    print()
    print("Encounter Created")
    print()

    for enemy in enemies:
        print(enemy.name)


if __name__ == "__main__":
    main()