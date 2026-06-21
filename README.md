# Fantasy Battle Master - Current Design (Alpha 9)

## Overview

Fantasy Battle Master is a turn-based fantasy skirmish simulator focused on:

- Fast combat resolution
- Simple range management
- Enemy AI targeting
- Morale-based behavior
- Tactical melee engagement

The project is currently transitioning from a single-file prototype into a modular repository structure.

---

# Combat Range System

Enemies exist in one of three range bands:

| Range | Meaning |
|---------|---------|
| MEL | In melee combat |
| OOM | Out of melee |
| OOB | Out of battle |

Examples:

```text
Orc Warrior #1 MEL
Orc Archer #1 OOM