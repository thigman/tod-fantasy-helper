# Fantasy Battle Master

## Current State

Refactor 3 Baseline

Code has been split into modules.

## Working Structure

models/
    enemy.py
    hero.py
    weapon.py
    enums.py

engine/
    ai.py
    combat.py
    dice.py
    ui.py

encounters/
    builder.py

main.py

## Completed

- GitHub repository created
- Modular project structure created
- Hero model extracted
- Enemy model extracted
- Weapon model extracted
- RangeBand enum extracted
- Encounter builder extracted
- Dice module created
- UI module created
- Combat module created
- SPD attribute removed

## Current Combat Status

Combat shell exists.

run_combat()

supports:

- Status
- Quit

No actual attack logic migrated yet.

## Enemy Design

Enemy contains:

- hp
- max_hp
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

## AI Design

Focus targeting:

choose_focus(enemy, targets)

Current threat model:

damage_done + 5

## Future Work

Phase 1:
- Round tracking
- Combat status display

Phase 2:
- Set Enemy Range

Phase 3:
- Hero attacks

Phase 4:
- Enemy turns

Phase 5:
- Morale system

Phase 6:
- Engagement system

Phase 7:
- Automatic melee engagement

## Notes

SPD removed from Enemy model.