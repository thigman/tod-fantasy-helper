# Fantasy Helper

A terminal-based fantasy combat assistant inspired by tabletop skirmish and RPG combat.

## Current Features

### Encounter Builder

Build encounters by adding enemies:

- Orc Warrior
- Orc Archer

Start combat when ready.

---

### Heroes

Current heroes:

#### Fighter

- HP: 25
- STR: 7
- DEX: 5
- MS: 7
- ARM: 4
- Weapon: Long Sword (1d8)

#### Wizard

- HP: 12
- STR: 2
- DEX: 4
- MS: 2
- ARM: 1
- Spells:
  - Magic Missile (1d8, PEN 2)
  - Fireball (2d8)

---

### Combat

Current combat menu:

- Attack
- Set Enemy Range
- Enemy Turn
- Combat Log
- Next Round
- Quit

Status is automatically displayed at the top of the screen.

---

### Range Bands

#### MEL

In melee.

Allowed attacks:

- Sword
- Axe

#### OOM

Out of melee.

Allowed attacks:

- Bow
- Magic Missile
- Fireball

#### OOB

Out of battle.

Cannot attack.

---

### Enemy AI

Enemies maintain:

- focus_target
- focus_rounds
- engaged_target

#### Warriors

Weapon: AXE

Behavior:

- Advance from OOM to MEL
- Engage a hero
- Attack only in MEL

#### Archers

Weapon: BOW

Behavior:

- Attack only while OOM
- Withdraw if trapped in MEL

---

### Engagement

Enemies in MEL may be engaged with a hero.

Example:

```text
Orc Warrior #1 HP16/16 AXE(1d8) MEL(Fighter)
```

When manually setting an enemy to MEL, the user chooses which hero the enemy is engaged with.

---

### Tactical Status

Displayed at the top of combat.

Example:

```text
TACTICAL STATUS
---------------
Orc Warrior #1: ENGAGING Fighter
Orc Archer #1: RANGED POSITION -> Wizard
```

---

### Combat Log

Stores recent combat events:

- Hits
- Misses
- Advances
- Withdrawals
- Defeats

---

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

main.py