"""
Game session manager for Fantasy Helper.
Wraps combat logic into a stateful API.
"""

from models.hero import Hero
from models.enemy import Enemy
from models.weapon import Weapon
from models.spell import Spell
from models.enums import RangeBand
from engine.combat import (
    hero_is_engaged,
    enemy_is_engaged,
    remove_dead,
    validate_enemy_targets,
    show_tactical_status,
    build_hero_reinforcement,
    build_enemy_reinforcement,
)
from engine.ai import choose_focus, assign_initial_focus
from engine.morale import update_morale
from engine.dice import roll

import random


class GameSession:
    """Manages a single combat session."""

    def __init__(self, heroes, enemies):
        self.heroes = heroes
        self.enemies = enemies
        self.acted = set()
        self.enemy_acted = set()
        self.round_num = 1
        self.log = []
        self.battle_over = False
        self.battle_result = ""
        self.starting_enemy_count = sum(1 for enemy in enemies if enemy.hp > 0)

        assign_initial_focus(self.enemies, self.heroes)
        update_morale(self.enemies, self.starting_enemy_count)

    def get_state(self):
        """Get current game state as serializable dict."""
        update_morale(self.enemies, self.starting_enemy_count)

        return {
            "round": self.round_num,
            "battle_over": self.battle_over,
            "battle_result": self.battle_result,
            "heroes": [self._serialize_hero(h) for h in self.heroes],
            "enemies": [self._serialize_enemy(e) for e in self.enemies],
            "acted": list(self.acted),
            "enemy_acted": list(self.enemy_acted),
            "log": self.log[-50:],  # Last 50 entries
        }

    def _serialize_hero(self, hero):
        """Convert Hero to dict."""
        return {
            "name": hero.name,
            "hp": hero.hp,
            "max_hp": hero.max_hp,
            "arm": hero.arm,
            "str": hero.str_,
            "dex": hero.dex,
            "ms": hero.ms,
            "rs": hero.rs,
            "spd": hero.spd,
            "intel": hero.intel,
            "weapon": {
                "name": hero.weapon.name,
                "damage": hero.weapon.damage,
                "pen": hero.weapon.pen,
            },
            "secondary_weapon": {
                "name": hero.secondary_weapon.name,
                "damage": hero.secondary_weapon.damage,
                "pen": hero.secondary_weapon.pen,
            } if hero.secondary_weapon else None,
            "spells": [
                {
                    "name": spell.name,
                    "damage": spell.damage,
                    "pen": spell.pen,
                    "area": spell.area,
                }
                for spell in hero.spells
            ],
            "damage_done": hero.damage_done,
            "alive": hero.hp > 0,
        }

    def _serialize_enemy(self, enemy):
        """Convert Enemy to dict."""
        return {
            "name": enemy.name,
            "hp": enemy.hp,
            "max_hp": enemy.max_hp,
            "arm": enemy.arm,
            "str": enemy.str_,
            "dex": enemy.dex,
            "ms": enemy.ms,
            "spd": enemy.spd,
            "morale": enemy.morale,
            "pack": enemy.pack,
            "weapon": {
                "name": enemy.weapon.name,
                "damage": enemy.weapon.damage,
                "pen": enemy.weapon.pen,
            },
            "secondary_weapon": {
                "name": enemy.secondary_weapon.name,
                "damage": enemy.secondary_weapon.damage,
                "pen": enemy.secondary_weapon.pen,
            } if enemy.secondary_weapon else None,
            "spells": [
                {
                    "name": spell.name,
                    "damage": spell.damage,
                    "pen": spell.pen,
                    "area": spell.area,
                }
                for spell in enemy.spells
            ],
            "rng": enemy.rng.name,
            "focus_target": enemy.focus_target,
            "engaged_target": enemy.engaged_target,
            "morale_state": enemy.morale_state,
            "alive": enemy.hp > 0,
        }

    def get_available_heroes(self):
        """Get heroes that haven't acted this round."""
        return [
            h.name
            for h in self.heroes
            if h.hp > 0 and h.name not in self.acted
        ]

    def get_available_enemies(self):
        """Get living enemies."""
        return [e.name for e in self.enemies if e.hp > 0]

    def get_alive_heroes(self):
        """Get living heroes."""
        return [h.name for h in self.heroes if h.hp > 0]

    def hero_attack(self, hero_name, enemy_name=None, enemy_names=None, spell_index=None):
        """Process a hero attack (single or area spell)."""
        hero = next((h for h in self.heroes if h.name == hero_name), None)
        
        if not hero:
            return {"success": False, "error": "Hero not found"}

        # Check if hero already acted
        if hero_name in self.acted:
            return {"success": False, "error": f"{hero_name} already acted this round"}

        # Check if hero is alive
        if hero.hp <= 0:
            return {"success": False, "error": f"{hero_name} is dead"}

        # Determine targets
        targets = []
        if enemy_names:
            # Area spell - multiple targets
            for ename in enemy_names:
                e = next((en for en in self.enemies if en.name == ename and en.hp > 0), None)
                if e:
                    targets.append(e)
            if not targets:
                return {"success": False, "error": "No valid targets"}
            is_area_spell = True
        elif enemy_name:
            # Single target
            enemy = next((e for e in self.enemies if e.name == enemy_name), None)
            if not enemy or enemy.hp <= 0:
                return {"success": False, "error": f"{enemy_name} not found or dead"}
            targets = [enemy]
            is_area_spell = False
        else:
            return {"success": False, "error": "No target specified"}

        # Wizard spell attack
        if hero.weapon.name == "MM":
            if hero_is_engaged(hero.name, self.enemies):
                msg = f"{hero.name} cannot cast while engaged in melee."
                self.log.append(msg)
                return {"success": False, "error": msg}

            # Area spell check
            if is_area_spell:
                if spell_index == 1:
                    # Fireball - area spell, check all targets are OOM
                    for target in targets:
                        if target.rng != RangeBand.OOM:
                            msg = f"{hero.name} cannot cast Fireball on {target.name}. Target must be OOM."
                            self.log.append(msg)
                            return {"success": False, "error": msg}
                    damage_expr = "2d8"
                    pen = 0
                    spell_name = "Fireball"
                else:
                    return {"success": False, "error": "Invalid area spell"}
            else:
                # Single-target spell
                if targets[0].rng != RangeBand.OOM:
                    msg = f"{hero.name} cannot cast on {targets[0].name}. Target must be OOM."
                    self.log.append(msg)
                    return {"success": False, "error": msg}

                if spell_index == 0:
                    damage_expr = "1d8"
                    pen = 2
                    spell_name = "Magic Missile"
                elif spell_index == 1:
                    damage_expr = "2d8"
                    pen = 0
                    spell_name = "Fireball"
                else:
                    return {"success": False, "error": "Invalid spell"}

            hit = random.randint(1, 20) + hero.intel >= 10 + max(t.dex for t in targets)

        # Melee attack
        else:
            if targets[0].rng != RangeBand.MEL:
                msg = f"{hero.name} cannot attack {targets[0].name}. Target must be MEL."
                self.log.append(msg)
                return {"success": False, "error": msg}

            damage_expr = hero.weapon.damage
            pen = hero.weapon.pen
            spell_name = None

            hit = random.randint(1, 20) + hero.ms >= 10 + targets[0].ms

        # Mark hero as acted
        self.acted.add(hero.name)

        # Process damage to all targets
        if not hit:
            if is_area_spell:
                msg = f"{hero.name} casts {spell_name} but all targets evade!"
            else:
                msg = f"{hero.name} misses {targets[0].name}"
            self.log.append(msg)
            return {"success": True, "message": msg}

        # Calculate and apply damage
        for target in targets:
            damage = max(1, roll(damage_expr) - max(target.arm - pen, 0))
            target.hp -= damage
            hero.damage_done += damage

            if is_area_spell:
                msg = f"{hero.name} casts {spell_name} on {target.name} for {damage}"
            else:
                if spell_name:
                    msg = f"{hero.name} casts {spell_name} on {target.name} for {damage}"
                else:
                    msg = f"{hero.name} hits {target.name} for {damage}"

            self.log.append(msg)

            if target.hp <= 0:
                defeat_msg = f"{target.name} is defeated!"
                self.log.append(defeat_msg)

        # Remove dead enemies
        self.enemies[:] = remove_dead(self.enemies)

        # Check for victory
        if not self.enemies:
            self.battle_over = True
            self.battle_result = "HERO VICTORY"

        return {"success": True, "message": "Attack resolved"}

    def enemy_turn(self):
        """Process enemy turn."""
        if self.battle_over:
            return {"success": False, "error": "Battle is over"}

        if not self.enemies:
            self.battle_over = True
            self.battle_result = "HERO VICTORY"
            return {"success": True, "message": "No enemies remain"}

        validate_enemy_targets(self.enemies, self.heroes)

        heroes_alive = [h for h in self.heroes if h.hp > 0]
        if not heroes_alive:
            self.battle_over = True
            self.battle_result = "ENEMY VICTORY"
            return {"success": True, "message": "All heroes defeated"}

        for enemy in self.enemies:
            if enemy.hp <= 0 or enemy.name in self.enemy_acted:
                continue

            if enemy.morale_state == "BROKEN":
                msg = f"{enemy.name} is BROKEN - wants to flee."
                self.log.append(msg)
                self.enemy_acted.add(enemy.name)
                continue

            # Choose target
            current_target = None

            if enemy.engaged_target:
                current_target = next(
                    (h for h in heroes_alive if h.name == enemy.engaged_target), None
                )

            if current_target is None and enemy.focus_target:
                current_target = next(
                    (h for h in heroes_alive if h.name == enemy.focus_target), None
                )

            # Only re-choose focus if not locked in engagement
            if not enemy.engaged_target and (
                current_target is None
                or enemy.focus_rounds <= 0
            ):
                current_target = choose_focus(enemy, heroes_alive)
                if current_target:
                    enemy.focus_target = current_target.name
                    enemy.focus_rounds = 2

            if current_target is None:
                self.enemy_acted.add(enemy.name)
                continue

            # Check weapon/range constraints
            if enemy.weapon.name == "AXE" and enemy.rng == RangeBand.OOM:
                msg = f"{enemy.name} wants to engage {current_target.name} but remains OOM."
                self.log.append(msg)
                self.enemy_acted.add(enemy.name)
                continue

            if enemy.weapon.name == "BOW" and enemy.rng == RangeBand.MEL:
                msg = f"{enemy.name} wants to withdraw from melee but remains MEL."
                self.log.append(msg)
                self.enemy_acted.add(enemy.name)
                continue

            if enemy.rng == RangeBand.OOB:
                self.enemy_acted.add(enemy.name)
                continue

            # Attack
            hit = random.randint(1, 20) + enemy.ms >= 10 + current_target.ms

            if hit:
                damage = max(
                    1,
                    roll(enemy.weapon.damage)
                    - max(current_target.arm - enemy.weapon.pen, 0),
                )
                current_target.hp -= damage
                msg = f"{enemy.name} hits {current_target.name} for {damage}"
            else:
                msg = f"{enemy.name} misses {current_target.name}"

            self.log.append(msg)

            if current_target.hp <= 0:
                defeat_msg = f"{current_target.name} is defeated!"
                self.log.append(defeat_msg)

            if enemy.focus_rounds > 0:
                enemy.focus_rounds -= 1

            self.enemy_acted.add(enemy.name)

        # Remove dead heroes
        self.heroes[:] = [h for h in self.heroes if h.hp > 0 or h.hp <= 0]

        # Check for defeat
        if not any(h.hp > 0 for h in self.heroes):
            self.battle_over = True
            self.battle_result = "ENEMY VICTORY"

        return {"success": True, "message": "Enemy turn complete"}

    def set_enemy_range(self, enemy_name, range_band, engaged_hero=None):
        """Set enemy's range band."""
        enemy = next((e for e in self.enemies if e.name == enemy_name), None)
        if not enemy:
            return {"success": False, "error": "Enemy not found"}

        try:
            enemy.rng = RangeBand[range_band]
        except KeyError:
            return {"success": False, "error": f"Invalid range: {range_band}"}

        if enemy.rng == RangeBand.MEL:
            if engaged_hero:
                if engaged_hero not in [h.name for h in self.heroes if h.hp > 0]:
                    return {"success": False, "error": "Hero not alive"}
                enemy.engaged_target = engaged_hero
                enemy.focus_target = engaged_hero
            else:
                return {"success": False, "error": "Must specify engaged hero for MEL"}
        else:
            enemy.engaged_target = None

        msg = f"{enemy.name} range set to {range_band}"
        if engaged_hero:
            msg += f", engaged with {engaged_hero}"
        self.log.append(msg)

        return {"success": True, "message": msg}

    def add_reinforcement(self, unit_type, is_hero=True):
        """Add a reinforcement unit."""
        existing_names = {u.name for u in (self.heroes if is_hero else self.enemies)}

        if is_hero:
            unit = build_hero_reinforcement(unit_type, existing_names)
            if unit:
                self.heroes.append(unit)
                msg = f"{unit.name} joins the battle."
                self.log.append(msg)
                return {"success": True, "message": msg}
        else:
            unit = build_enemy_reinforcement(unit_type, existing_names)
            if unit:
                self.enemies.append(unit)
                msg = f"{unit.name} arrives as reinforcement."
                self.log.append(msg)
                return {"success": True, "message": msg}

        return {"success": False, "error": "Invalid unit type"}

    def next_round(self):
        """Advance to next round."""
        if self.battle_over:
            return {"success": False, "error": "Battle is over"}

        self.round_num += 1
        self.acted = set()
        self.enemy_acted = set()

        # Reset morale/focus as needed
        update_morale(self.enemies, self.starting_enemy_count)

        msg = f"--- Round {self.round_num} ---"
        self.log.append(msg)

        return {"success": True, "message": msg}

    def end_battle(self):
        """End battle and return final state."""
        self.battle_over = True
        if not self.battle_result:
            self.battle_result = "QUIT"

        return self.get_state()
