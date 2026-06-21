from models.enemy import Enemy
from models.enums import RangeBand
from models.weapon import Weapon


axe = Weapon(
    "AXE",
    "1d8",
    2
)

bow = Weapon(
    "BOW",
    "1d6",
    1
)


def build_encounter():
    enemies = []

    orc_warrior_id = 1
    orc_archer_id = 1

    while True:

        print("\n=== ENCOUNTER BUILDER ===")

        if enemies:

            for enemy in enemies:
                print(enemy.name)

        else:

            print("No enemies yet.")

        print()
        print("1. Add Orc Warrior")
        print("2. Add Orc Archer")
        print("3. Start Encounter")

        choice = int(input("> "))

        if choice == 3:
            return enemies

        if choice == 1:

            enemies.append(
                Enemy(
                    name=f"Orc Warrior #{orc_warrior_id}",
                    hp=16,
                    max_hp=16,
                    arm=3,
                    spd=2,
                    str_=6,
                    dex=4,
                    ms=6,
                    morale=5,
                    pack=7,
                    weapon=axe,
                    rng=RangeBand.OOM,
                )
            )

            orc_warrior_id += 1

        elif choice == 2:

            enemies.append(
                Enemy(
                    name=f"Orc Archer #{orc_archer_id}",
                    hp=12,
                    max_hp=12,
                    arm=1,
                    spd=1,
                    str_=4,
                    dex=5,
                    ms=4,
                    morale=5,
                    pack=5,
                    weapon=bow,
                    rng=RangeBand.OOM,
                )
            )

            orc_archer_id += 1