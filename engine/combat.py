from engine.ui import (
    menu,
    show_heroes,
    show_enemies,
    clear_screen,
)

from engine.dice import roll
from engine.ai import (
    choose_focus,
    assign_initial_focus,
)
from engine.morale import update_morale

from models.enemy import Enemy
from models.hero import Hero
from models.enums import RangeBand
from models.weapon import Weapon
from models.spell import Spell

import random

def hero_is_engaged(
    hero_name,
    enemies,
):

    return any(
        enemy.hp > 0
        and enemy.engaged_target == hero_name
        for enemy in enemies
    )


def enemy_is_engaged(
    enemy,
):

    return (
        enemy.hp > 0
        and enemy.engaged_target is not None
    )




def remove_dead(enemies):

    return [
        enemy
        for enemy in enemies
        if enemy.hp > 0
    ]


def validate_enemy_targets(
    enemies,
    heroes,
):

    living_names = {
        hero.name
        for hero in heroes
        if hero.hp > 0
    }

    for enemy in enemies:

        if (
            enemy.focus_target
            and enemy.focus_target
            not in living_names
        ):
            enemy.focus_target = None
            enemy.focus_rounds = 0

        if (
            enemy.engaged_target
            and enemy.engaged_target
            not in living_names
        ):
            enemy.engaged_target = None


def show_tactical_status(enemies):

    lines = []

    for enemy in enemies:

        if enemy.hp <= 0:
            continue

        if enemy.morale_state == "BROKEN":

            lines.append(
                f"{enemy.name}: "
                f"BROKEN - WANTS TO FLEE"
            )

            continue

        if enemy.morale_state == "SHAKEN":

            target = (
                enemy.focus_target
                or "No Target"
            )

            lines.append(
                f"{enemy.name}: "
                f"SHAKEN -> {target}"
            )

            continue

        if (
            enemy.rng == RangeBand.MEL
            and enemy.engaged_target
        ):

            lines.append(
                f"{enemy.name}: "
                f"ENGAGING "
                f"{enemy.engaged_target}"
            )

            continue

        if enemy.weapon.name == "BOW":

            target = (
                enemy.focus_target
                or "No Target"
            )

            if enemy.rng == RangeBand.OOM:

                lines.append(
                    f"{enemy.name}: "
                    f"RANGED POSITION "
                    f"-> {target}"
                )

            elif enemy.rng == RangeBand.MEL:

                lines.append(
                    f"{enemy.name}: "
                    f"WANTS TO WITHDRAW "
                    f"-> {target}"
                )

            continue

        if enemy.weapon.name == "AXE":

            target = (
                enemy.focus_target
                or "No Target"
            )

            if enemy.rng == RangeBand.OOM:

                lines.append(
                    f"{enemy.name}: "
                    f"WANTS TO ENGAGE "
                    f"{target}"
                )

    if not lines:
        return

    print("TACTICAL STATUS")
    print("----------------")

    for line in lines:
        print(line)

    print()


def show_battlefield(
    heroes,
    enemies,
    acted,
):

    show_tactical_status(
        enemies,
    )

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


def set_enemy_range(
    enemies,
    heroes,
):

    if not enemies:
        print("No enemies.")
        return

    enemy_index = menu(
        "Choose Enemy",
        [e.name for e in enemies],
    )

    enemy = enemies[enemy_index]

    range_index = menu(
        "Range",
        [
            "MEL - In Melee",
            "OOM - Out of Melee",
            "OOB - Out of Battle",
        ],
    )

    enemy.rng = list(
        RangeBand
    )[range_index]

    if enemy.rng == RangeBand.MEL:

        living_heroes = [
            hero
            for hero in heroes
            if hero.hp > 0
        ]

        if living_heroes:

            hero_index = menu(
                "Engaged Hero",
                [
                    hero.name
                    for hero in living_heroes
                ],
            )

            enemy.engaged_target = (
                living_heroes[
                    hero_index
                ].name
            )

            enemy.focus_target = (
                enemy.engaged_target
            )

        else:

            enemy.engaged_target = None

    else:

        enemy.engaged_target = None


def get_unique_name(
    base,
    unit_counters,
):
    """Generate next unique name for a unit type.
    
    Args:
        base: The base unit name (e.g., "Fighter", "Orc Warrior")
        unit_counters: Dict tracking highest number used for each unit type
    
    Returns:
        Name with number: "Fighter #1", "Fighter #2", etc.
    """
    current_max = unit_counters.get(base, 0)
    next_number = current_max + 1
    unit_counters[base] = next_number
    return f"{base} #{next_number}"


def build_hero_reinforcement(
    hero_type,
    unit_counters,
):

    if hero_type == "Fighter":

        name = get_unique_name(
            "Fighter",
            unit_counters,
        )

        return Hero(
            name=name,
            hp=25,
            max_hp=25,
            arm=4,
            str_=7,
            dex=5,
            ms=7,
            rs=1,
            spd=6,
            intel=2,
            weapon=Weapon(
                "LSWD",
                "1d8",
                2,
            ),
            secondary_weapon=None,
            spells=[],
        )

    if hero_type == "Wizard":

        name = get_unique_name(
            "Wizard",
            unit_counters,
        )

        return Hero(
            name=name,
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
            spells=[
                Spell("Magic Missile", "1d8", 2, area=False),
                Spell("Fireball", "2d8", 0, area=True),
            ],
        )

    return None


def build_enemy_reinforcement(
    enemy_type,
    unit_counters,
):

    if enemy_type == "Orc Warrior":

        name = get_unique_name(
            "Orc Warrior",
            unit_counters,
        )

        return Enemy(
            name=name,
            hp=16,
            max_hp=16,
            arm=3,
            str_=6,
            dex=4,
            ms=6,
            spd=6,
            morale=5,
            pack=7,
            weapon=Weapon(
                "AXE",
                "1d8",
                2,
            ),
            secondary_weapon=Weapon(
                "CLAW",
                "1d4",
                0,
            ),
            rng=RangeBand.OOM,
        )

    if enemy_type == "Orc Archer":

        name = get_unique_name(
            "Orc Archer",
            unit_counters,
        )

        return Enemy(
            name=name,
            hp=12,
            max_hp=12,
            arm=1,
            str_=4,
            dex=5,
            ms=4,
            spd=6,
            morale=5,
            pack=5,
            weapon=Weapon(
                "BOW",
                "1d6",
                1,
            ),
            secondary_weapon=Weapon(
                "CLAW",
                "1d4",
                0,
            ),
            rng=RangeBand.OOM,
        )

    return None


def add_reinforcements(
    heroes,
    enemies,
):

    choice = menu(
        "Reinforcements",
        [
            "Add Hero Reinforcement",
            "Add Enemy Reinforcement",
            "Cancel",
        ],
    )

    if choice == 0:

        hero_names = {
            hero.name
            for hero in heroes
        }

        hero_type = [
            "Fighter",
            "Wizard",
        ][
            menu(
                "Hero Type",
                [
                    "Fighter",
                    "Wizard",
                ],
            )
        ]

        hero = build_hero_reinforcement(
            hero_type,
            hero_names,
        )

        if hero is not None:
            heroes.append(hero)
            print(
                f"{hero.name} joins the battle."
            )

    elif choice == 1:
        enemy_names = {
            enemy.name
            for enemy in enemies
        }

        enemy_type = [
            "Orc Warrior",
            "Orc Archer",
        ][
            menu(
                "Enemy Type",
                [
                    "Orc Warrior",
                    "Orc Archer",
                ],
            )
        ]

        enemy = build_enemy_reinforcement(
            enemy_type,
            enemy_names,
        )

        if enemy is not None:
            enemies.append(enemy)
            print(
                f"{enemy.name} arrives as reinforcement."
            )

    else:
        print("No reinforcements added.")


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

    if hero.name == "Wizard" and hero_is_engaged(
        hero.name,
        enemies,
    ):

        msg = (
            f"{hero.name} cannot cast while "
            f"engaged in melee."
        )

        print(msg)
        log.append(msg)

        return

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
    enemy_acted,
    log,
):

    print()
    print("=== ENEMY TURN ===")

    validate_enemy_targets(
        enemies,
        heroes,
    )

    for enemy in enemies:

        if enemy.hp <= 0:
            continue

        if enemy.name in enemy_acted:
            continue

        if enemy.morale_state == "BROKEN":

            msg = (
                f"{enemy.name} is BROKEN - "
                f"wants to flee."
            )

            print(msg)
            log.append(msg)

            enemy_acted.add(enemy.name)

            continue

        targets = [
            hero
            for hero in heroes
            if hero.hp > 0
        ]

        if not targets:
            break

        current_target = None

        if enemy.engaged_target:

            current_target = next(
                (
                    hero
                    for hero in targets
                    if hero.name
                    == enemy.engaged_target
                ),
                None,
            )

        if current_target is None:

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

            if current_target:

                enemy.focus_target = (
                    current_target.name
                )

                enemy.focus_rounds = 2

        if current_target is None:
            continue

        if (
            enemy.weapon.name == "AXE"
            and enemy.rng == RangeBand.OOM
        ):

            msg = (
                f"{enemy.name} wants to engage "
                f"{current_target.name} "
                f"but remains OOM."
            )

            print(msg)
            log.append(msg)

            enemy_acted.add(enemy.name)

            continue

        if (
            enemy.weapon.name == "BOW"
            and enemy.rng == RangeBand.MEL
        ):

            msg = (
                f"{enemy.name} wants to withdraw "
                f"from melee but remains MEL."
            )

            print(msg)
            log.append(msg)

            enemy_acted.add(enemy.name)

            continue

        if enemy.rng == RangeBand.OOB:

            enemy_acted.add(enemy.name)

            continue

        hit = (
            random.randint(1, 20)
            + enemy.ms
            >= 10 + current_target.ms
        )

        if hit:

            damage = max(
                1,
                roll(enemy.weapon.damage)
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

        enemy_acted.add(
            enemy.name
        )

    enemies[:] = remove_dead(
        enemies
    )


def show_combat_log(log):

    print()
    print("=== COMBAT LOG ===")

    if not log:
        print("No log entries.")
        return

    for entry in log[-20:]:
        print(entry)


def run_combat(
    heroes,
    enemies,
):

    acted = set()

    enemy_acted = set()

    round_num = 1

    log = []

    starting_enemy_count = sum(
        1
        for enemy in enemies
        if enemy.hp > 0
    )

    assign_initial_focus(
        enemies,
        heroes,
    )

    update_morale(
        enemies,
        starting_enemy_count,
    )

    battle_over = False

    battle_result = ""

    while True:

        if battle_over:

            clear_screen()

            print("=== BATTLE OVER ===")
            print()

            print(
                f"Result: {battle_result}"
            )

            print(
                f"Rounds: {round_num}"
            )

            print()

            print("HEROES")
            print("------")

            for hero in heroes:

                if hero.hp > 0:

                    print(
                        f"{hero.name}: "
                        f"HP {hero.hp}/{hero.max_hp}"
                    )

                else:

                    print(
                        f"{hero.name}: DEAD"
                    )

            print()

            choice = menu(
                "Post Battle",
                [
                    "Combat Log",
                    "Quit",
                ],
            )

            if choice == 0:

                show_combat_log(
                    log,
                )

                input("\nPress Enter...")

            else:

                break

            continue

        clear_screen()

        print(
            f"=== COMBAT ROUND "
            f"{round_num} ==="
        )

        print()

        update_morale(
            enemies,
            starting_enemy_count,
        )

        show_battlefield(
            heroes,
            enemies,
            acted,
        )

        choice = menu(
            "Action",
            [
                "Attack",
                "Set Enemy Range",
                "Enemy Turn",
                "Reinforcements",
                "Combat Log",
                "Next Round",
                "Quit",
            ],
        )

        if choice == 0:

            if enemies:

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

                battle_over = True
                battle_result = "HERO VICTORY"

            else:

                input("\nPress Enter...")

        elif choice == 1:

            set_enemy_range(
                enemies,
                heroes,
            )

            input("\nPress Enter...")

        elif choice == 2:

            enemy_turn(
                heroes,
                enemies,
                acted,
                enemy_acted,
                log,
            )

            living_heroes = [
                hero
                for hero in heroes
                if hero.hp > 0
            ]

            if not living_heroes:

                battle_over = True
                battle_result = "HERO DEFEAT"

            else:

                input("\nPress Enter...")

        elif choice == 3:

            add_reinforcements(
                heroes,
                enemies,
            )

            input("\nPress Enter...")

        elif choice == 4:

            show_combat_log(
                log,
            )

            input("\nPress Enter...")

        elif choice == 5:

            round_num += 1

            acted.clear()

            enemy_acted.clear()

        elif choice == 5:

            break