def choose_focus(
    enemy,
    targets,
):
    """
    Pick a living target.

    Current threat model:
    choose the first living hero.
    """

    living_targets = [
        target
        for target in targets
        if target.hp > 0
    ]

    if not living_targets:
        return None

    return living_targets[0]


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