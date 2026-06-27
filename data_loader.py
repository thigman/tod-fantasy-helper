"""
Data loader for heroes and enemies from JSON files.
"""

import json
import os
from models.hero import Hero
from models.enemy import Enemy
from models.weapon import Weapon
from models.spell import Spell
from models.enums import RangeBand


def load_heroes_from_json():
    """Load hero templates from JSON."""
    json_path = os.path.join(os.path.dirname(__file__), "data", "heroes.json")
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
            heroes = []
            for hero_data in data:
                hero = _build_hero_from_data(hero_data)
                heroes.append(hero)
            return heroes
    except Exception as e:
        print(f"Error loading heroes: {e}")
        return []


def load_enemies_from_json():
    """Load enemy templates from JSON."""
    json_path = os.path.join(os.path.dirname(__file__), "data", "enemies.json")
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
            enemies = []
            for enemy_data in data:
                enemy = _build_enemy_from_data(enemy_data)
                enemies.append(enemy)
            return enemies
    except Exception as e:
        print(f"Error loading enemies: {e}")
        return []


def _build_hero_from_data(data):
    """Build a Hero object from JSON data."""
    weapon = Weapon(
        data["weapon"]["name"],
        data["weapon"]["damage"],
        data["weapon"]["pen"],
    ) if data.get("weapon") else None

    secondary_weapon = None
    if data.get("secondary_weapon"):
        secondary_weapon = Weapon(
            data["secondary_weapon"]["name"],
            data["secondary_weapon"]["damage"],
            data["secondary_weapon"]["pen"],
        )

    spells = []
    if data.get("spells"):
        for spell_data in data["spells"]:
            spell = Spell(
                spell_data["name"],
                spell_data["damage"],
                spell_data["pen"],
                spell_data.get("area", False),
            )
            spells.append(spell)

    return Hero(
        name=data["name"],
        hp=data["hp"],
        max_hp=data["hp"],
        arm=data["arm"],
        str_=data["str"],
        dex=data["dex"],
        ms=data["ms"],
        rs=data["rs"],
        spd=data["spd"],
        intel=data["intel"],
        weapon=weapon,
        secondary_weapon=secondary_weapon,
        spells=spells,
    )


def _build_enemy_from_data(data):
    """Build an Enemy object from JSON data."""
    weapon = Weapon(
        data["weapon"]["name"],
        data["weapon"]["damage"],
        data["weapon"]["pen"],
    ) if data.get("weapon") else None

    secondary_weapon = None
    if data.get("secondary_weapon"):
        secondary_weapon = Weapon(
            data["secondary_weapon"]["name"],
            data["secondary_weapon"]["damage"],
            data["secondary_weapon"]["pen"],
        )

    spells = []
    if data.get("spells"):
        for spell_data in data["spells"]:
            spell = Spell(
                spell_data["name"],
                spell_data["damage"],
                spell_data["pen"],
                spell_data.get("area", False),
            )
            spells.append(spell)

    return Enemy(
        name=data["name"],
        hp=data["hp"],
        max_hp=data["hp"],
        arm=data["arm"],
        str_=data["str"],
        dex=data["dex"],
        ms=data["ms"],
        spd=data["spd"],
        morale=data["morale"],
        pack=data["pack"],
        weapon=weapon,
        secondary_weapon=secondary_weapon,
        spells=spells,
        rng=RangeBand.OOM,
    )
