# Fantasy Helper

A terminal-based fantasy combat assistant for tabletop-style skirmish combat.

## Overview

Fantasy Helper is built as a combat assistant, not a fully automated game. The tabletop is the source of truth. The user tracks movement and range manually, while the application tracks state, intent, and combat outcomes.

## Current Design

### Heroes

The app currently includes a hardcoded hero roster in `main.py`:

- Fighter
- Wizard

Heroes are represented by `models.hero.Hero` and include HP, defenses, stats, movement, and a single weapon/spell profile.

### Enemies

Enemies are built through `encounters/builder.py` and currently support:

- Orc Warrior
- Orc Archer

Enemies are represented by `models.enemy.Enemy`. They include combat stats, morale attributes, weapon, and range state.

### Encounter Builder

The builder lets the user add enemies and start combat. It is currently a simple menu that creates hardcoded Orc types.

### Combat Flow

`engine/combat.py` handles the round loop and user choices:

- Attack
- Set Enemy Range
- Enemy Turn
- Combat Log
- Next Round
- Quit

Combat always shows the battlefield and tactical status before action selection.

### Tactical Status

`engine/combat.show_tactical_status()` calculates status from:

- enemy range band
- engaged hero
- focus target
- morale state

Current tactical displays include:

- `ENGAGING <hero>`
- `RANGED POSITION -> <hero>`
- `WANTS TO WITHDRAW -> <hero>`
- `WANTS TO ENGAGE <hero>`
- `SHAKEN -> <hero>`
- `BROKEN - WANTS TO FLEE`

### Morale

Morale is implemented in `engine/morale.py` and is now integrated into combat.

- `STEADY` – normal behavior
- `SHAKEN` – displays morale but still fights
- `BROKEN` – does not attack and displays fleeing intent

Morale state is updated each round based on:

- casualties against original enemy count
- remaining enemy HP ratio
- average enemy resolve (`morale + pack`)

### Range Lock and Engagement

The app enforces basic range rules:

- melee attacks require `MEL`
- wizard spells require `OOM`
- a wizard cannot cast while engaged in melee

`Set Enemy Range` allows the user to assign engagement manually when an enemy enters MEL.

## Testing

The repository includes regression tests for AI and combat logic:

- `tests/test_ai.py`
- `tests/test_combat.py`

Current status: `18 passed`.

Run the suite with:

```bash
.venv/bin/python -m pytest -q
```

## Project Structure

```text
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

encounters/
    builder.py

data/
    monsters.json
    party.json
    weapons.json

tests/
    test_ai.py
    test_combat.py

main.py
```

## Notes

- `data/*.json` files exist as placeholders for future roster loading.
- The current hero roster is hardcoded in `main.py`.
- The current encounter builder is hardcoded in `encounters/builder.py`.

## Next steps

The next extension is to make heroes and enemies data-driven, using JSON definitions for new good guys and bad guys without code changes.