def calculate_morale_state(
    starting_enemy_count,
    living_enemy_count,
):
    """
    Determine morale state based on
    percentage of casualties suffered.
    """

    if starting_enemy_count <= 0:
        return "STEADY"

    casualties = (
        starting_enemy_count
        - living_enemy_count
    )

    casualty_ratio = (
        casualties
        / starting_enemy_count
    )

    if casualty_ratio >= 0.50:
        return "BROKEN"

    if casualty_ratio >= 0.25:
        return "SHAKEN"

    return "STEADY"


def update_morale(
    enemies,
    starting_enemy_count,
):
    """
    Apply morale state to all
    living enemies.
    """

    living_enemy_count = sum(
        1
        for enemy in enemies
        if enemy.hp > 0
    )

    morale_state = calculate_morale_state(
        starting_enemy_count,
        living_enemy_count,
    )

    for enemy in enemies:

        if enemy.hp <= 0:
            continue

        enemy.morale_state = (
            morale_state
        )

    return morale_state