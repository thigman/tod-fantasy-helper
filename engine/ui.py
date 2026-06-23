import os

from models.enums import RangeBand


def clear_screen():

    os.system(
        "cls"
        if os.name == "nt"
        else "clear"
    )


def menu(title, items):

    print(f"\n{title}")

    for i, item in enumerate(items, 1):
        print(f"{i}. {item}")

    while True:

        try:

            value = int(input("> "))

            if 1 <= value <= len(items):
                return value - 1

        except:
            pass

        print("Invalid selection")


def hero_state(hero, acted):

    if hero.hp <= 0:
        return "DEAD"

    if hero.name in acted:
        return "ACTED"

    return "READY"


def show_heroes(heroes, acted):

    for i, hero in enumerate(heroes, 1):

        print(
            f"{i}. "
            f"{hero.name} "
            f"HP{max(0, hero.hp)}/{hero.max_hp} "
            f"STR{hero.str_} "
            f"DEX{hero.dex} "
            f"MS{hero.ms} "
            f"ARM{hero.arm} "
            f"{hero.weapon.name}"
            f"({hero.weapon.damage}) "
            f"{hero_state(hero, acted)}"
        )


def show_enemies(enemies):

    for i, enemy in enumerate(enemies, 1):

        engaged = ""

        if (
            enemy.rng == RangeBand.MEL
            and enemy.engaged_target
        ):
            engaged = (
                f"({enemy.engaged_target})"
            )

        focus = ""

        if (
            enemy.focus_target
            and enemy.focus_target
            != enemy.engaged_target
        ):
            focus = (
                f" -> "
                f"{enemy.focus_target}"
            )

        print(
            f"{i}. "
            f"{enemy.name} "
            f"HP{max(0, enemy.hp)}/{enemy.max_hp} "
            f"STR{enemy.str_} "
            f"DEX{enemy.dex} "
            f"MS{enemy.ms} "
            f"ARM{enemy.arm} "
            f"{enemy.weapon.name}"
            f"({enemy.weapon.damage}) "
            f"{enemy.rng.value}"
            f"{engaged}"
            f"{focus}"
        )