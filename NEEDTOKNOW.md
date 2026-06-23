# NEEDTOKNOW.md

# Fantasy Helper

This file is intended to help a future Copilot/chat session quickly understand the project and continue development without requiring conversation history.

---

# Project Summary

Fantasy Helper is a terminal-based fantasy combat assistant.

Current focus is combat simulation, enemy AI, engagement, movement, and future morale systems.

The game is being built incrementally and correctness is more important than adding new features.

---

# Important Workflow Rule

The user prefers:

- FULL FILES
- NOT PATCHES
- NOT SNIPPETS

When updating a file:

- Return the entire file
- Ensure it is internally consistent
- Do not provide partial replacements unless specifically requested

---

# Current Architecture

```text
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
```

---

# Heroes

## Fighter

```text
HP 25
STR 7
DEX 5
MS 7
ARM 4
Weapon: Long Sword (1d8)
```

Role:

```text
Melee
```

---

## Wizard

```text
HP 12
STR 2
DEX 4
MS 2
ARM 1
```

Spells:

```text
Magic Missile (1d8 PEN 2)
Fireball (2d8)
```

Role:

```text
Ranged
```

---

# Enemies

## Orc Warrior

Weapon:

```text
AXE
```

Behavior:

```text
Advance from OOM to MEL
Engage target
Attack in MEL
```

---

## Orc Archer

Weapon:

```text
BOW
```

Behavior:

```text
Attack from OOM
Withdraw from MEL
```

---

# Range Bands

## MEL

In melee.

Allowed:

```text
Sword
Axe
```

---

## OOM

Out of melee.

Allowed:

```text
Bow
Magic Missile
Fireball
```

---

## OOB

Out of battle.

No attacks allowed.

---

# Engagement System

Enemy model currently contains:

```python
engaged_target
```

Purpose:

```text
Tracks which hero a melee enemy is currently engaged with.
```

Status display example:

```text
Orc Warrior #1 MEL(Fighter)
```

Manual range assignment:

When putting an enemy into MEL through:

```text
Set Enemy Range
```

the user chooses:

```text
Engaged Hero
```

and engagement is assigned.

---

# Tactical Status

Displayed at top of combat screen.

Examples:

```text
TACTICAL STATUS
---------------
Orc Warrior #1: ENGAGING Fighter
```

```text
TACTICAL STATUS
---------------
Orc Archer #1: RANGED POSITION -> Fighter
```

Current implementation derives tactical status from:

```text
range
focus target
engaged target
weapon type
```

rather than storing status text.

This is preferred because it cannot become stale.

---

# Combat Rules

## Melee

Allowed only in:

```text
MEL
```

Weapons:

```text
SWORD
AXE
```

---

## Ranged

Allowed only in:

```text
OOM
```

Weapons:

```text
BOW
MAGIC MISSILE
FIREBALL
```

---

# Current Combat Menu

```text
Attack
Set Enemy Range
Enemy Turn
Combat Log
Next Round
Quit
```

---

# Screen Handling

Current desired behavior:

```text
Status always visible at top.
```

Screen redraws frequently.

Combat Log is available separately.

---

# Combat Log

Tracks:

```text
Hits
Misses
Advances
Withdrawals
Defeats
```

Example:

```text
Wizard hits Orc Archer #1 for 7
Orc Warrior #1 advances toward Fighter
Orc Archer #1 withdraws from melee
```

---

# What Is Working

## Hero Combat

Working:

```text
Hero hit rolls
Hero damage
Hero acted tracking
Range restrictions
```

---

## Enemy Combat

Working:

```text
Advance
Withdraw
Damage
Hit rolls
Focus targeting
Engagement
```

---

## Tactical Status

Working.

Displayed continuously.

---

## Engagement

Working.

Displayed as:

```text
MEL(Fighter)
```

---

# Known Bugs

## Bug 1

Dead focus target may persist.

Example:

```text
Wizard dies.
Enemy still shows:

-> Wizard
```

Desired:

```text
Focus automatically cleared.
Enemy chooses a living target.
```

Priority:

```text
HIGH
```

---

## Bug 2

Enemy can currently act multiple times per round.

Example:

```text
Enemy Turn
Enemy Turn
Enemy Turn
```

results in multiple attacks.

Desired:

```text
One enemy action per round.
```

Implementation idea:

```python
enemy_acted = set()
```

Reset when:

```python
Next Round
```

is selected.

Priority:

```text
HIGH
```

---

# Next Development Tasks

## 1

Fix dead focus targets.

Priority:

```text
HIGH
```

---

## 2

Limit enemies to one action per round.

Priority:

```text
HIGH
```

---

## 3

Initial focus assignment.

Current tactical display may show:

```text
No Target
```

before first enemy turn.

Desired:

```text
Orc Warrior #1: ATTEMPTING ADVANCE -> Fighter
```

---

## 4

Morale System

Placeholder exists:

```text
engine/morale.py
```

Not implemented yet.

Ideas:

```text
Break
Retreat
Rally
Pack morale
Leader effects
```

---

## 5

Movement System

Placeholder exists:

```text
engine/movement.py
```

Not implemented yet.

Ideas:

```text
Advance
Withdraw
Charge
Retreat
```

---

## 6

Combat Balance

Future review:

```text
Hit chances
Armor values
Wizard balance
Enemy durability
```

---

## 7

Additional Enemies

Potential future additions:

```text
Goblin
Skeleton
Zombie
Ogre
Troll
Bosses
```

---

# Recommended Next Session Prompt

```text
I'm continuing work on Fantasy Helper.

Please read the attached repo dump and NEEDTOKNOW.md first.

Current priorities:

1. Fix dead focus targets.
2. Limit enemies to one action per round.

Please always return full file replacements.
```

---

# Repo Dump Format Recommendation

Use:

```text
===== FILE: README.md =====

(contents)

===== FILE: STATUS.md =====

(contents)

===== FILE: NEEDTOKNOW.md =====

(contents)

===== FILE: engine/combat.py =====

(contents)

===== FILE: engine/ui.py =====

(contents)

...
```

This provides enough context for a new session to resume work immediately.



I'm continuing work on Fantasy Helper.

Please read NEEDTOKNOW.md and the repo dump first.

Current priorities:

1. Fix dead focus targets.
2. Limit enemies to one action per round.

Please always return full file replacements.



OPEN BUGS

1. Dead focus targets are not cleared.
2. Enemies may act multiple times per round.
