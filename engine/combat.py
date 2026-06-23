from engine.ui import (
    menu,
    show_heroes,
    show_enemies,
)

from engine.dice import roll
from engine.ai import choose_focus

from models.enums import RangeBand


def remove_dead(enemies):

    return [
        enemy
        for enemy in enemies
        if enemy.hp > 0
    ]


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

    enemies[enemy_index].rng = list(
        RangeBand
    )[range_index]


def hero_attack(
    heroes,
    enemies,
    acted,
):

    available = [
        hero
        for hero in heroes
        if hero.hp > 0
        and hero.name not in acted
    ]

    if not available:
        print("No heroes available.")
        return

    hero = available[
        menu(
            "Hero",
            [h.name for h in available],
        )
    ]

    enemy = enemies[
        menu(
            "Enemy",
            [e.name for e in enemies],
        )
    ]

    if hero.name == "Wizard":

        spell = menu(
            "Spell",
            [
                "Magic Missile",
                "Fireball",
            ],
        )

        if spell == 0:
            damage_expr = "1d8"
            pen = 2
        else:
            damage_expr = "2d8"
            pen = 0

    else:

        if enemy.rng != RangeBand.MEL:
            print("Target not in melee.")
            return

        damage_expr = hero.weapon.damage
        pen = hero.weapon.pen

    damage = max(
        1,
        roll(damage_expr)
        - max(
            enemy.arm - pen,
            0,
        ),
    )

    enemy.hp -= damage
    hero.damage_done += damage

    acted.add(hero.name)

    print(
        f"{hero.name} hits "
        f"{enemy.name} "
        f"for {damage}"
    )

    if enemy.hp <= 0:

        print(
            f"{enemy.name} "
            f"is defeated!"
        )


def enemy_turn(
    heroes,
    enemies,
):

    print()
    print("=== ENEMY TURN ===")

    living_heroes = [
        hero
        for hero in heroes
        if hero.hp > 0
    ]

    if not living_heroes:
        return

    for enemy in enemies:

        if enemy.hp <= 0:
            continue

        targets = [
            hero
            for hero in heroes
            if hero.hp > 0
        ]

        if not targets:
            break

        current_target = None

        if enemy.focus_target:

            current_target = next(
                (
                    hero
                    for hero in targets
                    if hero.name
                    == enemy.focus_target
                ),
                None,
            )

        if (
            current_target is None
            or enemy.focus_rounds <= 0
        ):

            current_target = choose_focus(
                enemy,
                targets,
            )

            enemy.focus_target = (
                current_target.name
            )

            enemy.focus_rounds = 2

        damage = max(
            1,
            roll(
                enemy.weapon.damage
            )
            - max(
                current_target.arm
                - enemy.weapon.pen,
                0,
            ),
        )

        current_target.hp -= damage

        print(
            f"{enemy.name} "
            f"hits "
            f"{current_target.name} "
            f"for {damage}"
        )

        if current_target.hp <= 0:

            print(
                f"{current_target.name} "
                f"is defeated!"
            )

        if enemy.focus_rounds > 0:
            enemy.focus_rounds -= 1


def run_combat(
    heroes,
    enemies,
):

    acted = set()

    round_num = 1

    while True:

        print()
        print(
            f"=== COMBAT ROUND "
            f"{round_num} ==="
        )

        choice = menu(
            "Action",
            [
                "Status",
                "Attack",
                "Set Enemy Range",
                "Enemy Turn",
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

            if not enemies:
                print(
                    "No enemies remain."
                )
                continue

            hero_attack(
                heroes,
                enemies,
                acted,
            )

            enemies[:] = remove_dead(
                enemies
            )

            if not enemies:

                print()
                print(
                    "All enemies defeated!"
                )

                break

        elif choice == 2:

            set_enemy_range(
                enemies,
            )

        elif choice == 3:

            enemy_turn(
                heroes,
                enemies,
            )

            living_heroes = [
                hero
                for hero in heroes
                if hero.hp > 0
            ]

            if not living_heroes:

                print()
                print(
                    "The heroes have fallen!"
                )

                break

        elif choice == 4:

            round_num += 1

            acted.clear()

        elif choice == 5:

            break