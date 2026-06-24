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

## Fighter

HP: 25

ARM: 4
STR: 7
DEX: 5
MS: 7

Weapon:

Long Sword
1d8
PEN 2

Role:

Melee

---

## Wizard

HP: 12

ARM: 1
STR: 2
DEX: 4
MS: 2
INT: 8

Spells:

Magic Missile
1d8
PEN 2

Fireball
2d8

Role:

Ranged

---

# Enemies

## Orc Warrior

HP: 16

Weapon:

AXE
1d8
PEN 2

Behavior:

- Prefer melee
- Advance from OOM
- Engage hero
- Attack in MEL

---

## Orc Archer

HP: 12

Weapon:

BOW
1d6
PEN 1

Behavior:

- Attack while OOM
- Withdraw if trapped in MEL

---

# Range Bands

## MEL

In melee

Allowed:

- Sword
- Axe

---

## OOM

Out of melee

Allowed:

- Bow
- Magic Missile
- Fireball

---

## OOB

Out of battle

Cannot attack

---

# Engagement System

Enemy model contains:

    engaged_target

Purpose:

Tracks which hero an enemy is engaged with.

Example:

    Orc Warrior #1
    HP 16/16
    MEL(Fighter)

---

# Manual Engagement Assignment

Menu:

    Set Enemy Range

If user selects:

    MEL

User is prompted:

    Engaged Hero

Engagement is assigned manually.

Example:

    Fighter

Result:

    enemy.engaged_target == "Fighter"

---

# Tactical Status

Displayed above battlefield view.

Examples:

    TACTICAL STATUS
    ----------------
    Orc Warrior #1:
    ENGAGING Fighter

    Orc Archer #1:
    RANGED POSITION -> Wizard

Status is derived from:

- range
- focus target
- engagement

Status text is NOT stored.

This is intentional.

---

# Enemy AI

Enemy model contains:

    focus_target
    focus_rounds
    engaged_target

Focus assignment:

Current AI selects first living hero.

Function:

    choose_focus()

Initial focus assignment implemented.

Combat now begins with immediate target selection.

Example:

    Orc Warrior #1:
    WANTS TO ENGAGE Fighter

instead of:

    No Target

---

# Combat Log

Tracks:

- hits
- misses
- defeats
- advances
- withdrawals

Example:

    Wizard hits Orc Archer #1 for 7

    Orc Warrior #1 misses Fighter

---

# Post Battle Screen

Implemented.

Features:

- Hero Victory
- Hero Defeat
- Round count
- Final hero status
- Combat log access

Combat does NOT automatically quit.

User must choose:

    Quit

from post-battle menu.

---

# Enemy Turn Tracking

Implemented.

Mechanism:

    enemy_acted = set()

Enemies may only act once per round.

Reset occurs when:

    Next Round

is selected.

---

# Dead Target Cleanup

Implemented.

If focused hero dies:

    focus_target = None

and

    focus_rounds = 0

If engaged hero dies:

    engaged_target = None

Enemy will select a new target.

---

# Regression Tests

Implemented.

Currently:

## tests/test_ai.py

5 passing tests

Verifies:

- living target selection
- dead target filtering
- no target behavior

---

## tests/test_combat.py

6 passing tests

Verifies:

- remove_dead()
- focus cleanup
- engagement cleanup
- focus round reset
- target preservation

---

Current test status:

    11 passed

Run with:

    python -m pytest -v

---

# Morale System

Partially implemented.

Current file:

    engine/morale.py

Contains:

    calculate_morale_state()

    update_morale()

Enemy model contains:

    morale_state

Default:

    STEADY

---

## Intended Morale Rules

Casualties based on original enemy count.

0-24%

    STEADY

25-49%

    SHAKEN

50%+

    BROKEN

---

## Intended Behavior

STEADY

Normal

---

SHAKEN

Displays morale state.

Still fights.

---

BROKEN

Will not attack.

Displays:

    BROKEN - WANTS TO FLEE

Movement remains player-controlled.

No automatic retreating.

---

# Range Lock Feature

NOT YET IMPLEMENTED

Desired rule:

If a combatant is engaged in melee:

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