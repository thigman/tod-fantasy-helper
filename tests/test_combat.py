from engine.combat import (
    enemy_turn,
    hero_attack,
    remove_dead,
    show_battlefield,
    show_tactical_status,
    validate_enemy_targets,
)
from engine.morale import update_morale

from models.enemy import Enemy
from models.hero import Hero
from models.weapon import Weapon
from models.enums import RangeBand


def make_enemy():

    weapon = Weapon(
        "AXE",
        "1d8",
        2,
    )

    return Enemy(
        "Orc Warrior #1",
        16,
        16,
        3,
        6,
        4,
        6,
        5,
        7,
        weapon,
        RangeBand.OOM,
    )


def make_fighter():

    weapon = Weapon(
        "LSWD",
        "1d8",
        2,
    )

    return Hero(
        "Fighter",
        25,
        25,
        4,
        7,
        5,
        7,
        1,
        2,
        weapon,
    )


def make_wizard(hp=12):

    weapon = Weapon(
        "MM",
        "1d8",
        2,
    )

    return Hero(
        "Wizard",
        hp,
        12,
        1,
        2,
        4,
        2,
        2,
        8,
        weapon,
    )


def test_remove_dead_enemies():

    alive_enemy = make_enemy()

    dead_enemy = make_enemy()
    dead_enemy.name = "Dead Orc"
    dead_enemy.hp = 0

    result = remove_dead(
        [
            alive_enemy,
            dead_enemy,
        ]
    )

    assert len(result) == 1
    assert result[0].name == "Orc Warrior #1"


def test_dead_focus_target_is_cleared():

    enemy = make_enemy()

    enemy.focus_target = "Wizard"

    fighter = make_fighter()

    wizard = make_wizard(
        hp=0,
    )

    validate_enemy_targets(
        [enemy],
        [
            fighter,
            wizard,
        ],
    )

    assert enemy.focus_target is None


def test_dead_focus_resets_round_counter():

    enemy = make_enemy()

    enemy.focus_target = "Wizard"
    enemy.focus_rounds = 2

    fighter = make_fighter()

    wizard = make_wizard(
        hp=0,
    )

    validate_enemy_targets(
        [enemy],
        [
            fighter,
            wizard,
        ],
    )

    assert enemy.focus_rounds == 0


def test_dead_engaged_target_is_cleared():

    enemy = make_enemy()

    enemy.rng = RangeBand.MEL
    enemy.engaged_target = "Wizard"

    fighter = make_fighter()

    wizard = make_wizard(
        hp=0,
    )

    validate_enemy_targets(
        [enemy],
        [
            fighter,
            wizard,
        ],
    )

    assert enemy.engaged_target is None


def test_living_focus_target_is_preserved():

    enemy = make_enemy()

    enemy.focus_target = "Fighter"
    enemy.focus_rounds = 2

    fighter = make_fighter()

    wizard = make_wizard()

    validate_enemy_targets(
        [enemy],
        [
            fighter,
            wizard,
        ],
    )

    assert enemy.focus_target == "Fighter"
    assert enemy.focus_rounds == 2


def test_living_engaged_target_is_preserved():

    enemy = make_enemy()

    enemy.rng = RangeBand.MEL
    enemy.engaged_target = "Fighter"

    fighter = make_fighter()

    validate_enemy_targets(
        [enemy],
        [
            fighter,
        ],
    )

    assert enemy.engaged_target == "Fighter"


def test_update_morale_sets_broken_for_50_percent_casualties():

    alive_enemy = make_enemy()

    dead_enemy1 = make_enemy()
    dead_enemy1.hp = 0

    dead_enemy2 = make_enemy()
    dead_enemy2.hp = 0

    state = update_morale(
        [alive_enemy, dead_enemy1, dead_enemy2],
        3,
    )

    assert state == "BROKEN"
    assert alive_enemy.morale_state == "BROKEN"


def test_update_morale_sets_shaken_for_25_percent_casualties():

    alive_enemy1 = make_enemy()
    alive_enemy2 = make_enemy()

    dead_enemy = make_enemy()
    dead_enemy.hp = 0

    state = update_morale(
        [alive_enemy1, alive_enemy2, dead_enemy],
        3,
    )

    assert state == "SHAKEN"
    assert alive_enemy1.morale_state == "SHAKEN"
    assert alive_enemy2.morale_state == "SHAKEN"


def test_show_enemies_displays_morale_state(capsys):

    enemy = make_enemy()
    enemy.morale_state = "SHAKEN"

    from engine.ui import show_enemies

    show_enemies([enemy])

    captured = capsys.readouterr()

    assert "[SHAKEN]" in captured.out


def test_show_battlefield_displays_tactical_status(capsys):

    fighter = make_fighter()
    wizard = make_wizard()

    enemy = make_enemy()
    enemy.morale_state = "SHAKEN"
    enemy.focus_target = "Fighter"

    show_battlefield(
        [fighter, wizard],
        [enemy],
        set(),
    )

    captured = capsys.readouterr()

    assert "TACTICAL STATUS" in captured.out
    assert "SHAKEN -> Fighter" in captured.out


def test_update_morale_sets_broken_for_low_average_resolve():

    enemy = make_enemy()
    enemy.morale = 1
    enemy.pack = 2

    state = update_morale(
        [enemy],
        1,
    )

    assert state == "BROKEN"
    assert enemy.morale_state == "BROKEN"


def test_update_morale_sets_shaken_for_low_average_resolve():

    enemy = make_enemy()
    enemy.morale = 4
    enemy.pack = 4

    state = update_morale(
        [enemy],
        1,
    )

    assert state == "SHAKEN"
    assert enemy.morale_state == "SHAKEN"


def test_broken_enemy_does_not_act_during_enemy_turn():

    fighter = make_fighter()
    wizard = make_wizard()

    enemy = make_enemy()
    enemy.morale_state = "BROKEN"

    log = []
    enemy_acted = set()

    enemy_turn(
        [fighter, wizard],
        [enemy],
        set(),
        enemy_acted,
        log,
    )

    assert enemy.name in enemy_acted
    assert any(
        "BROKEN" in entry
        for entry in log
    )


def test_shaken_tactical_status_is_displayed(capsys):

    enemy = make_enemy()
    enemy.morale_state = "SHAKEN"
    enemy.focus_target = "Fighter"

    show_tactical_status([enemy])

    captured = capsys.readouterr()

    assert "TACTICAL STATUS" in captured.out
    assert "SHAKEN -> Fighter" in captured.out


def test_broken_tactical_status_is_displayed(capsys):

    enemy = make_enemy()
    enemy.morale_state = "BROKEN"

    show_tactical_status([enemy])

    captured = capsys.readouterr()

    assert "TACTICAL STATUS" in captured.out
    assert "BROKEN - WANTS TO FLEE" in captured.out


def test_broken_tactical_status_overrides_engaged_display(capsys):

    enemy = make_enemy()
    enemy.morale_state = "BROKEN"
    enemy.rng = RangeBand.MEL
    enemy.engaged_target = "Fighter"

    show_tactical_status([enemy])

    captured = capsys.readouterr()

    assert "BROKEN - WANTS TO FLEE" in captured.out
    assert "ENGAGING" not in captured.out


def test_wizard_cannot_cast_while_engaged(monkeypatch):

    fighter = make_fighter()
    wizard = make_wizard()

    enemy = make_enemy()
    enemy.rng = RangeBand.OOM
    enemy.engaged_target = "Wizard"

    choices = iter([
        1,  # choose Wizard
        0,  # choose enemy
    ])

    def fake_menu(title, items):
        return next(choices)

    monkeypatch.setattr(
        "engine.combat.menu",
        fake_menu,
    )

    log = []
    acted = set()

    hero_attack(
        [fighter, wizard],
        [enemy],
        acted,
        log,
    )

    assert any(
        "cannot cast while engaged in melee" in entry
        for entry in log
    )
    assert "Wizard" not in acted
