from engine.ai import choose_focus


class MockHero:

    def __init__(
        self,
        name,
        hp,
    ):
        self.name = name
        self.hp = hp


def test_choose_focus_returns_living_target():

    enemy = object()

    targets = [
        MockHero(
            "Wizard",
            0,
        ),
        MockHero(
            "Fighter",
            25,
        ),
    ]

    result = choose_focus(
        enemy,
        targets,
    )

    assert result is not None
    assert result.name == "Fighter"


def test_choose_focus_returns_first_living_target():

    enemy = object()

    targets = [
        MockHero(
            "Fighter",
            25,
        ),
        MockHero(
            "Wizard",
            12,
        ),
    ]

    result = choose_focus(
        enemy,
        targets,
    )

    assert result is not None
    assert result.name == "Fighter"


def test_choose_focus_ignores_dead_targets():

    enemy = object()

    targets = [
        MockHero(
            "Dead Hero",
            0,
        ),
        MockHero(
            "Fighter",
            25,
        ),
    ]

    result = choose_focus(
        enemy,
        targets,
    )

    assert result is not None
    assert result.name == "Fighter"


def test_choose_focus_returns_none_when_no_targets():

    enemy = object()

    result = choose_focus(
        enemy,
        [],
    )

    assert result is None


def test_choose_focus_returns_none_when_all_targets_dead():

    enemy = object()

    targets = [
        MockHero(
            "Wizard",
            0,
        ),
        MockHero(
            "Fighter",
            0,
        ),
    ]

    result = choose_focus(
        enemy,
        targets,
    )

    assert result is None


def test_choose_focus_prefers_highest_potential_damage():

    enemy = object()

    fighter = MockHero(
        "Fighter",
        25,
    )
    wizard = MockHero(
        "Wizard",
        12,
    )

    fighter.weapon = type(
        "W",
        (),
        {"damage": "1d8", "pen": 2},
    )()
    wizard.weapon = type(
        "W",
        (),
        {"damage": "2d8", "pen": 2},
    )()

    result = choose_focus(
        enemy,
        [fighter, wizard],
    )

    assert result is not None
    assert result.name == "Wizard"