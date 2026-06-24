from engine.combat import (
    remove_dead,
    validate_enemy_targets,
)

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