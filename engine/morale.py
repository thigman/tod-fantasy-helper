def calculate_morale_state(
    enemies,
    starting_enemy_count,
):
    """
    Determine morale state based on casualties,
    group health, and surviving enemy strength.
    """

    if starting_enemy_count <= 0:
        return "STEADY"

    living_enemies = [
        enemy
        for enemy in enemies
        if enemy.hp > 0
    ]

    living_enemy_count = len(living_enemies)

    casualties = (
        starting_enemy_count
        - living_enemy_count
    )

    casualty_ratio = (
        casualties
        / starting_enemy_count
    )

    total_hp = sum(
        max(0, enemy.hp)
        for enemy in enemies
    )

    total_max_hp = sum(
        enemy.max_hp
        for enemy in enemies
    )

    group_hp_ratio = (
        total_hp / total_max_hp
        if total_max_hp > 0
        else 1
    )

    average_resolve = 0
    if living_enemies:
        average_resolve = sum(
            enemy.morale + enemy.pack
            for enemy in living_enemies
        ) / len(living_enemies)

    if (
        casualty_ratio >= 0.50
        or group_hp_ratio <= 0.25
        or average_resolve < 6
    ):
        return "BROKEN"

    if (
        casualty_ratio >= 0.25
        or group_hp_ratio <= 0.50
        or average_resolve < 10
    ):
        return "SHAKEN"

    return "STEADY"


def update_morale(
    enemies,
    starting_enemy_count,
):
    """
    Apply morale state to all living enemies.
    Enemies with morale=0 (like skeletons) always stay STEADY.
    """

    morale_state = calculate_morale_state(
        enemies,
        starting_enemy_count,
    )

    for enemy in enemies:

        if enemy.hp <= 0:
            continue

        # Enemies with no morale (skeletons, etc.) are never affected
        if enemy.morale == 0:
            enemy.morale_state = "STEADY"
        else:
            enemy.morale_state = morale_state

    return morale_state