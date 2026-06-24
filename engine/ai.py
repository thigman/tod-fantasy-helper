def choose_focus(enemy, targets):
    """
    Pick a living target.

    Current simple threat model:
    choose the first living hero.
    """

    living_targets = [t for t in targets if t.hp > 0]

    if not living_targets:
        return None

    return living_targets[0]