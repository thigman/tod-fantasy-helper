def choose_focus(enemy, targets):
    """
    Current threat model.

    Focuses on the hero who has
    dealt the most damage.
    """

    return max(
        targets,
        key=lambda h: h.damage_done + 5
    )