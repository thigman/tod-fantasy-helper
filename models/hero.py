from dataclasses import dataclass

from models.weapon import Weapon


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

    intel: int

    weapon: Weapon

    damage_done: int = 0