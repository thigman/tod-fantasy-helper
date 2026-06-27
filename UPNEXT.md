# Up Next

This file captures the next practical improvements for Fantasy Helper.

## Goal

Make the roster of heroes and enemies data-driven so new units can be added without editing application code.

## Why

Current hardcoded definitions live in `main.py` and `encounters/builder.py`.

Future content should be declared in JSON files under `data/`.

## Current Path

- `main.py` constructs heroes directly in code.
- `encounters/builder.py` creates enemies through menu choices.
- `data/` already has placeholder files:
  - `party.json`
  - `monsters.json`
  - `weapons.json`

## What to do

1. Define data schemas.

   - `data/party.json` for hero definitions.
   - `data/monsters.json` for enemy definitions.
   - `data/weapons.json` for weapon/spell definitions.

   Each definition should include:

   - `name`
   - `hp`
   - `max_hp`
   - `arm`
   - `str_`
   - `dex`
   - `ms`
   - `morale` and `pack` for enemies
   - `intel` for spellcasters
   - `weapon` reference
   - `rng` initial range value for enemies

2. Add loader utilities.

   - Create `data_loader.py` or extend `encounters/builder.py`.
   - Load JSON into model classes: `Hero`, `Enemy`, `Weapon`.
   - Keep model initialization separate from combat rules.

3. Update `main.py`.

   - Load heroes from `party.json`.
   - Load weapons from `weapons.json`.
   - Keep hero roster flexible.

4. Update `encounters/builder.py`.

   - Load enemy types from `monsters.json`.
   - Present dynamic menu items for available monsters.
   - Build enemies from JSON templates.

5. Add tests.

   - Validate JSON loading.
   - Ensure enemy and hero objects are built correctly.
   - Assert that new entries in data files can be instantiated without code changes.

## How to add more good guys and bad guys

- Good guys: add hero definitions to `data/party.json`.
- Bad guys: add monster definitions to `data/monsters.json`.
- Weapons: add entries to `data/weapons.json` and reference them by key.

Example hero entry:

```json
{
  "name": "Ranger",
  "hp": 18,
  "max_hp": 18,
  "arm": 3,
  "str_": 5,
  "dex": 6,
  "ms": 6,
  "rs": 1,
  "intel": 4,
  "weapon": "BOW"
}
```

Example enemy entry:

```json
{
  "name": "Skeleton Archer",
  "hp": 10,
  "max_hp": 10,
  "arm": 1,
  "str_": 3,
  "dex": 4,
  "ms": 5,
  "morale": 4,
  "pack": 5,
  "weapon": "BOW",
  "rng": "OOM"
}
```

Example weapon entry:

```json
{
  "name": "BOW",
  "damage": "1d6",
  "pen": 1
}
```

## Notes

- Keep the combat engine unchanged while enabling new data.
- Do not hardcode new unit names in the engine.
- Keep `RangeBand` values consistent with the enum.

## Recommended next development step

Start by creating a lightweight JSON loader module and converting one example hero and one example enemy to data-driven definitions.
