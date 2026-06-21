from encounters.builder import build_encounter


def main():
    enemies = build_encounter()

    print()
    print("Encounter Created")
    print()

    for enemy in enemies:
        print(enemy.name)


if __name__ == "__main__":
    main()