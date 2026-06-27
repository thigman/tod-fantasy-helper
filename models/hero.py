from dataclasses import dataclass, field

from models.weapon import Weapon
from models.spell import Spell


@dataclass
class Hero:
    name: str

    hp: int
    max_hp: int

    arm: int

    str_: int
    dex: int

    ms: int
    rs: int
    spd: int

    intel: int

    weapon: Weapon
    secondary_weapon: Weapon | None = None

    spells: list[Spell] = field(default_factory=list)

    damage_done: int = 0