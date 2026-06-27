from dataclasses import dataclass


@dataclass
class Spell:
    name: str
    damage: str
    pen: int
    area: bool = False
