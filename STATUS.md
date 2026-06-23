# Current Status

## Working

### Encounter Builder

- Add Orc Warrior
- Add Orc Archer
- Start Encounter

### Hero Combat

- Fighter melee attacks
- Wizard spell attacks
- Melee restricted to MEL
- Spells restricted to OOM

### Enemy Combat

- Warrior advance
- Archer withdraw
- Enemy hit rolls
- Enemy damage
- Enemy focus targeting

### Engagement

- engaged_target exists
- MEL enemies can be assigned to a hero
- Engagement displayed in status

### Tactical Display

- Battlefield displayed continuously
- Tactical status displayed above heroes/enemies

### Combat Log

- Stores and displays events

### Screen Handling

- Screen clears between actions
- Status redraws automatically

---

# Known Issues

## High Priority

### Dead Focus Targets

Current bug:

Enemy may continue displaying:

```text
-> Wizard
```

after Wizard is dead.

Desired:

- Clear focus automatically
- Select new target

---

### Enemy Multiple Turns

Current bug:

User can select:

```text
Enemy Turn
Enemy Turn
Enemy Turn
```

during the same round.

Desired:

- Enemy acts once per round
- Add:

```python
enemy_acted = set()
```

- Reset on:

```python
Next Round
```

---

# Next Development Tasks

## 1

Fix dead focus targets.

Priority: HIGH

---

## 2

Limit enemies to one action per round.

Priority: HIGH

---

## 3

Initial target assignment.

Currently tactical status may show:

```text
No Target
```

Desired:

```text
Orc Warrior #1: ATTEMPTING ADVANCE -> Fighter
```

before first enemy turn.

---

## 4

Morale System

Existing placeholder:

```text
engine/morale.py
```

Not yet implemented.

Ideas:

- Break
- Retreat
- Rally

---

## 5

Movement System

Existing placeholder:

```text
engine/movement.py
```

Not yet implemented.

Possible future features:

- Advance
- Withdraw
- Charge
- Retreat

---

## 6

Combat Balance

Future improvements:

- Hero hit rolls tuning
- Wizard balancing
- Armor tuning
- Damage balancing

---

## 7

Enemy Types

Potential additions:

- Goblin
- Skeleton
- Troll
- Ogre
- Bosses

---

# Immediate Goal

Fix:

- dead focus targets
- enemy acting multiple times per round

before implementing morale or additional enemy types.