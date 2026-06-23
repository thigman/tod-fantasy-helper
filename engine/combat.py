from engine.ui import (
    menu,
    show_heroes,
    show_enemies,
)

from engine.dice import roll
from engine.ai import choose_focus

from models.enums import RangeBand

import random


def remove_dead(enemies):

    return [
        enemy
        for enemy in enemies
        if enemy.hp > 0
    ]


def show_battlefield(
    heroes,
    enemies,
    acted,
):

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
    log,
):

    available = [
        hero
        for hero in heroes
        if hero.hp > 0
        and hero.name not in acted
    ]

    if not available:

        print(
            "No heroes available."
        )

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

    #
    # Wizard spells require OOM
    #

    if hero.name == "Wizard":

        if enemy.rng != RangeBand.OOM:

            msg = (
                f"{hero.name} cannot cast on "
                f"{enemy.name}. "
                f"Target must be OOM."
            )

            print(msg)
            log.append(msg)

            return

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

        hit = (
            random.randint(1, 20)
            + hero.intel
            >= 10 + enemy.dex
        )

    #
    # Melee heroes require MEL
    #

    else:

        if enemy.rng != RangeBand.MEL:

            msg = (
                f"{hero.name} cannot attack "
                f"{enemy.name}. "
                f"Target must be MEL."
            )

            print(msg)
            log.append(msg)

            return

        damage_expr = hero.weapon.damage
        pen = hero.weapon.pen

        hit = (
            random.randint(1, 20)
            + hero.ms
            >= 10 + enemy.ms
        )

    acted.add(
        hero.name
    )

    if not hit:

        msg = (
            f"{hero.name} misses "
            f"{enemy.name}"
        )

        print(msg)
        log.append(msg)

        return

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

    msg = (
        f"{hero.name} hits "
        f"{enemy.name} "
        f"for {damage}"
    )

    print(msg)
    log.append(msg)

    if enemy.hp <= 0:

        msg = (
            f"{enemy.name} "
            f"is defeated!"
        )

        print(msg)
        log.append(msg)


def enemy_turn(
    heroes,
    enemies,
    acted,
    log,
):

    print()
    print("=== ENEMY TURN ===")

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

        #
        # Archers withdraw from melee
        #

        if (
            enemy.weapon.name == "BOW"
            and enemy.rng == RangeBand.MEL
        ):

            enemy.rng = RangeBand.OOM

            msg = (
                f"{enemy.name} withdraws "
                f"from melee."
            )

            print(msg)
            log.append(msg)

            continue

        #
        # Warriors advance into melee
        #

        if (
            enemy.weapon.name == "AXE"
            and enemy.rng == RangeBand.OOM
        ):

            enemy.rng = RangeBand.MEL

            msg = (
                f"{enemy.name} advances "
                f"toward "
                f"{current_target.name}."
            )

            print(msg)
            log.append(msg)

            continue

        #
        # OOB enemies do nothing
        #

        if enemy.rng == RangeBand.OOB:
            continue

        #
        # Bow attacks require OOM
        #

        if (
            enemy.weapon.name == "BOW"
            and enemy.rng != RangeBand.OOM
        ):
            continue

        #
        # Axe attacks require MEL
        #

        if (
            enemy.weapon.name == "AXE"
            and enemy.rng != RangeBand.MEL
        ):
            continue

        hit = (
            random.randint(1, 20)
            + enemy.ms
            >= 10 + current_target.ms
        )

        if hit:

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

            msg = (
                f"{enemy.name} hits "
                f"{current_target.name} "
                f"for {damage}"
            )

        else:

            msg = (
                f"{enemy.name} misses "
                f"{current_target.name}"
            )

        print(msg)
        log.append(msg)

        if current_target.hp <= 0:

            msg = (
                f"{current_target.name} "
                f"is defeated!"
            )

            print(msg)
            log.append(msg)

        if enemy.focus_rounds > 0:

            enemy.focus_rounds -= 1

    enemies[:] = remove_dead(
        enemies
    )

    print()
    print("=== STATUS AFTER ENEMY TURN ===")

    show_battlefield(
        heroes,
        enemies,
        acted,
    )


def show_combat_log(log):

    print()
    print("=== COMBAT LOG ===")

    if not log:

        print(
            "No log entries."
        )

        return

    for entry in log[-20:]:

        print(entry)


def run_combat(
    heroes,
    enemies,
):

    acted = set()

    round_num = 1

    log = []

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
                "Combat Log",
                "Next Round",
                "Quit",
            ],
        )

        if choice == 0:

            show_battlefield(
                heroes,
                enemies,
                acted,
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
                log,
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
                acted,
                log,
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

            show_combat_log(
                log,
            )

        elif choice == 5:

            round_num += 1

            acted.clear()

            print(
                f"Starting Round "
                f"{round_num}"
            )

        elif choice == 6:

            break