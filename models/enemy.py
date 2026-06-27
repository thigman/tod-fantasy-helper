from dataclasses import dataclass, field

from models.enums import RangeBand
from models.weapon import Weapon
from models.spell import Spell


@dataclass
class Enemy:
    name: str
    hp: int
    max_hp: int
    arm: int
    str_: int
    dex: int
    ms: int
    spd: int
    morale: int
    pack: int
    weapon: Weapon
    secondary_weapon: Weapon | None = None
    spells: list[Spell] = field(default_factory=list)
    rng: RangeBand = RangeBand.OOM

    # AI state
    focus_target: str | None = None
    focus_rounds: int = 0

    # Melee engagement - MEL means in melee WITH these specific heroes
    melee_with: list[str] = field(default_factory=list)  # Heroes this enemy is in melee with
    engaged_target: str | None = None  # Preferred focus target (can be None for open melee)

    # Morale state
    morale_state: str = "STEADY"