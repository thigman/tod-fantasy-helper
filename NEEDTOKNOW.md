# Fantasy Helper

This file is intended to help a future Copilot session quickly understand the project and continue development without requiring previous chat history.

---

# IMPORTANT WORKFLOW RULE

User preference:

- FULL FILES
- NOT PATCHES
- NOT SNIPPETS

When modifying a file:

- Return the entire file.
- Ensure imports are included.
- Ensure resulting file is internally consistent.
- Do not provide partial edits unless specifically requested.

---

# Project Summary

Fantasy Helper is a terminal-based fantasy combat assistant.

The tabletop is the source of truth.

The application acts as a combat assistant rather than a fully automated game.

Current focus:

- Combat simulation
- Enemy AI
- Engagement tracking
- Tactical display
- Morale system
- Regression testing

Correctness is more important than adding new features.

---

# Current Architecture

main.py

engine/
    ai.py
    combat.py
    dice.py
    morale.py
    movement.py
    ui.py

models/
    enemy.py
    enums.py
    hero.py
    weapon.py

data/
    monsters.json
    party.json
    weapons.json

tests/
    test_ai.py
    test_combat.py

encounters/
    builder.py

---

# Core Design Philosophy

The tabletop controls movement.

The application tracks:

- HP
- attacks
- combat state
- engagement
- enemy focus
- morale

The application does NOT automatically move models.

Enemy behavior is expressed as intent.

Examples:

    Orc Warrior #1:
    WANTS TO ENGAGE Fighter

    Orc Archer #1:
    WANTS TO WITHDRAW -> Wizard

Player moves minis physically and updates ranges manually.

---

# Heroes

The current hero roster is hardcoded in `main.py`.

Current heroes:

- Fighter
- Wizard

Heroes are represented by `models.hero.Hero`.

Each hero has:

- name
- hp / max_hp
- arm
- str_
- dex
- ms
- rs
- intel
- weapon

Wizard spellcasting is modeled through a standard weapon-like attack, but has special range restrictions.

---

# Enemies

Enemies are built in `encounters/builder.py`.

Current enemy types:

- Orc Warrior
- Orc Archer

Enemies are represented by `models.enemy.Enemy`.

Each enemy has:

- name
- hp / max_hp
- arm
- str_
- dex
- ms
- morale
- pack
- weapon
- rng
- focus_target
- focus_rounds
- engaged_target
- morale_state

---

# Range Bands

Range is represented by `models.enums.RangeBand`.

- `MEL` — melee
- `OOM` — out of melee
- `OOB` — out of battle

Rules enforced by `engine/combat.hero_attack()`:

- melee heroes require `MEL`
- Wizard spells require `OOM`
- Wizard cannot cast while engaged in melee

Range changes are assigned through `Set Enemy Range`.

---

# Engagement System

Enemy model contains:

    engaged_target

Purpose:

Tracks which hero an enemy is engaged with when in melee.

When an enemy is set to `MEL`, the user selects the engaged hero.

Example:

    enemy.engaged_target == "Fighter"

---

# Enemy AI

Enemy model contains:

    focus_target
    focus_rounds
    engaged_target

The AI uses `engine.ai.choose_focus()` to choose the most threatening living hero.

Threat is calculated from:

- hero weapon damage
- hero STR or INT bonus

Initial focus is assigned before the first enemy turn by `engine.ai.assign_initial_focus()`.

Enemies preserve focus for a small number of rounds before retargeting.

---

# Morale System

Implemented in `engine/morale.py`.

Morale states:

- `STEADY`
- `SHAKEN`
- `BROKEN`

Morale is updated each round by `engine.morale.update_morale()`.

Morale calculation considers:

- casualties vs starting enemy count
- remaining enemy HP ratio
- average enemy resolve (`morale + pack`)

Behavior:

- `STEADY` — normal combat
- `SHAKEN` — intent shown, still fights
- `BROKEN` — does not attack, displays fleeing intent

---

# Tactical Status

Displayed above the battlefield.

Status is derived from:

- enemy range band
- engaged target
- focus target
- morale state

Text is generated dynamically and not stored directly on the enemy.

Examples:

- `ENGAGING Fighter`
- `RANGED POSITION -> Wizard`
- `WANTS TO ENGAGE Fighter`
- `WANTS TO WITHDRAW -> Wizard`
- `SHAKEN -> <target>`
- `BROKEN - WANTS TO FLEE`

---

# Combat Log

Tracks:

- hits
- misses
- defeats
- advances
- withdrawals

The combat log is appended during hero and enemy actions.

---

# Enemy Turn Tracking

Enemy turns are handled in `engine.combat.enemy_turn()`.

Enemies act once per round via `enemy_acted`.

BROKEN enemies still consume their turn but do not attack.

---

# Dead Target Cleanup

Implemented in `engine.combat.validate_enemy_targets()`.

If a focused or engaged hero dies:

- `focus_target` is cleared
- `focus_rounds` is reset
- `engaged_target` is cleared

---

# Testing

Tests are in:

- `tests/test_ai.py`
- `tests/test_combat.py`

Run with:

    python -m pytest -v

Current status: `18 passed`.

---

# Future Work

The next extension should make heroes and enemies data-driven.

This means moving roster definitions into JSON files under `data/` and updating the builder/load path so new good guys and bad guys can be added without code changes.

Key future tasks:

1. Make `encounters.builder` and `main.py` load heroes/enemies from `data/*.json`.
2. Add JSON schemas for heroes, enemies, and weapons.
3. Add tests for data loading and model construction.
4. Keep engine combat logic unchanged while supporting new data.

---

# Recommended Prompt For New Session

Read NEEDTOKNOW.md first.

Current priorities:

1. Make hero/enemy definitions data-driven.
2. Keep all existing regression tests passing.
3. Preserve the current combat, AI, and morale behavior.

Remember:

FULL FILES.
NOT PATCHES.
NOT SNIPPETS.

    No ranged attacks
    No spells

If a combatant is engaged in melee:

    Cannot be targeted by
    ranged attacks or spells

Examples:

Allowed:

    Fighter -> Orc Warrior

    Orc Warrior -> Fighter

Disallowed:

    Wizard -> Orc Warrior
    (target engaged)

    Orc Archer -> Fighter
    (target engaged)

    Wizard casts while engaged

    Orc Archer shoots while engaged

Recommended helper functions:

    hero_is_engaged()

    enemy_is_engaged()

This is considered the next major combat rule update.

---

# Future Tasks

Priority:

1. Implement range lock rule.
2. Finish morale integration.
3. Add morale display to tactical status.
4. Prevent BROKEN enemies from attacking.
5. Add morale regression tests.

Later:

- Goblins
- Skeletons
- Zombies
- Ogres
- Trolls
- Bosses

---

# Recommended Prompt For New Session

Read NEEDTOKNOW.md first.

Current priorities:

1. Implement range lock.
2. Finish morale system.
3. Maintain all existing regression tests.

Remember:

FULL FILES.
NOT PATCHES.
NOT SNIPPETS.