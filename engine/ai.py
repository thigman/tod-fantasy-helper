def calculate_threat_score(
    hero,
):
    """
    Rate how dangerous a hero is based
    on their potential damage output.
    """

    if hero.hp <= 0:
        return 0

    try:
        num, sides = map(
            int,
            hero.weapon.damage.split("d"),
        )
    except Exception:
        return 0

    max_damage = num * sides
    ability_bonus = max(
        getattr(hero, "str_", 0),
        getattr(hero, "intel", 0),
    )

    return max_damage + ability_bonus


def choose_focus(
    enemy,
    targets,
):
    """
    Pick the most threatening living target.

    Current threat model:
    choose the hero with the highest
    potential damage output.
    """

    living_targets = [
        target
        for target in targets
        if target.hp > 0
    ]

    if not living_targets:
        return None

    return max(
        living_targets,
        key=calculate_threat_score,
    )


def assign_initial_focus(
    enemies,
    heroes,
):
    """
    Assign initial targets before
    the first enemy turn so tactical
    status displays useful information.
    """

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

        if enemy.focus_target:
            continue

        target = choose_focus(
            enemy,
            living_heroes,
        )

        if target is None:
            continue

        enemy.focus_target = target.name
        enemy.focus_rounds = 2