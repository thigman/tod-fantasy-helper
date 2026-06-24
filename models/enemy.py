from dataclasses import dataclass

from models.enums import RangeBand
from models.weapon import Weapon


@dataclass
class Enemy:
    name: str
    hp: int
    max_hp: int
    arm: int
    str_: int
    dex: int
    ms: int
    morale: int
    pack: int
    weapon: Weapon
    rng: RangeBand

    # AI state
    focus_target: str | None = None
    focus_rounds: int = 0

    # Melee engagement
    engaged_target: str | None = None

    # Morale state
    morale_state: str = "STEADY"